#importing required libraries for gym env
import gym
import numpy as np
from visgrid.taxi.taxi import VisTaxi5x5


#debugging
import pdb


'''Taxi Environment: inherits from gym.Env class'''
class TaxiEnv(gym.Env):

    metadata = {'render.modes': ['human', 'rgb_array']}


    def __init__(self, num_passengers=1, grayscale =False, have_goal = True, randomize_positions = True, ignore_rewards = False, max_steps_per_episode = None):
        '''creates taxi gym env: passed into GymWrapper for dreamerv2'''

        #base TaxiEnv environment: logistics
        self.taxi_env = VisTaxi5x5(n_passengers =  num_passengers, grayscale = grayscale)
        taxi_rendering = self.taxi_env.reset(goal = have_goal, explore = randomize_positions)
        taxi_rendering = self._convert_to_int(taxi_rendering)

        #stored for future resets
        self.have_goal = have_goal; self.randomize_positions = randomize_positions

        #observation space for TaxiEnv: RGB array
        #self.observation_space = gym.spaces.Box(low=0, high=255, shape = taxi_rendering.shape, dtype = np.uint8)
        self.observation_space = taxi_rendering

        #action space for TaxiEnv: discrete action space UP,DOWN,LEFT,RIGHT,PICKUP/DROP [added new in taxi.py]
        self.action_space = gym.spaces.Discrete(len(self.taxi_env.actions))

        #tracking steps + steps per episode + reward behaviour
        self.T = 0
        self.max_steps_per_episode = max_steps_per_episode
        self.ignore_rewards = ignore_rewards



    def step(self, action):
        '''
        step function
        converts an input from the self.action_space [Discrete space] into a Taxi gridworld move, takes the action on the Taxi gridworld

        input: action (sampled from self.action_space)
        returns: observation (after taking action), reward, done, info
        '''

        #increment step counter and take step in TaxiEnv
        taxi_rendering, reward, is_terminal = self.taxi_env.step(action)
        taxi_rendering = self._convert_to_int(taxi_rendering)

        self.T += 1

        if self.ignore_rewards:
            reward = 0
            done = False


        #tracking new info dict + adding terminal state info
        info = self._get_current_info()

        #consider terminal state v.s. timeout (reaching max steps)
        timeout = (self.T%self.max_steps_per_episode)==0 if self.max_steps_per_episode is not None else False

        info['timeout'] = timeout
        info['is_terminal'] = is_terminal
        #self.observation_space = taxi_rendering
        print('action: ', action, ' | reward: ', reward) 
        print('done step: ', is_terminal or timeout)
        print('timeout: ', timeout)
        return taxi_rendering, reward, is_terminal or timeout, info

    def reset(self):
        '''
        reset function
        resets the state to the starting point

        input: None
        output: state observation after resetting env
        '''

        #reset taxi environment: returns rendered RGB array
        rendered_taxi = self.taxi_env.reset(self.have_goal, self.randomize_positions)
        rendered_taxi = self._convert_to_int(rendered_taxi)

        #reset step count to 0
        self.T = 0
        
        #self.observation_space = rendered_taxi
        return rendered_taxi

    def render(self, mode='rgb_array'):
        '''
        render function
        generates RGB array of environment

        input: None
        output: RGB array of environment
        '''

        #render RGB array for environment
        if mode=='rgb_array':
            rendered_taxi = self.taxi_env.render()
            rendered_taxi = self._convert_to_int(rendered_taxi)
        else:
            raise NotImplementedError

        return rendered_taxi


    def _get_current_info(self):
        '''return info dictionary for env'''

        info = {}

        #extract state information for info dict
        state_info = self.taxi_env.get_state()

        taxi_position = state_info[0:2]
        info['taxi_col'] = taxi_position[1]
        info['taxi_row'] = taxi_position[0]

        #store position + in-taxi information for each passenger
        for i in range(0,len(state_info[2:]),3):

            p_row, p_col, p_in_taxi = state_info[i:i+3]

            info['p{}_row'.format(i)] = p_row
            info['p{}_col'.format(i)] = p_col
            info['p{}_in_taxi'.format(i)] = p_in_taxi

        return info

    def _convert_to_int(self, observation):
        '''casts a 0-1 image array (observation) into a 0-255 int array '''

        #scaling 0-1 to 0-255
        observation = observation*255

        #converting from float to int array
        observation = observation.astype(np.uint8)

        return observation
