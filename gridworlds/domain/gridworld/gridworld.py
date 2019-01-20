import numpy as np
import matplotlib.pyplot as plt

from . import grid
from .objects.agent import Agent

class GridWorld(grid.BaseGrid):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.agent = Agent()
        self.actions = [i for i in range(4)]
        self.action_map = {
            0: grid.LEFT,
            1: grid.RIGHT,
            2: grid.UP,
            3: grid.DOWN
        }
        self.agent.position = np.asarray((0,0), dtype=int)

    def step(self, action):
        assert(action in range(4))
        direction = self.action_map[action]
        if not self.has_wall(self.agent.position, direction):
            self.agent.position += direction
        s = self.get_state()
        r = 0
        done = False
        return s, r, done

    def can_run(self, action):
        assert(action in range(4))
        direction = self.action_map[action]
        return False if self.has_wall(self.agent.position, direction) else True

    def get_state(self):
        return np.copy(self.agent.position)

    def plot(self):
        ax = super().plot()
        if self.agent:
            self.agent.plot(ax)
        return ax

class TestWorld(GridWorld):
    def __init__(self):
        super().__init__(rows=3, cols=4)
        self._grid[1,4] = 1
        self._grid[2,3] = 1
        self._grid[3,2] = 1
        self._grid[5,4] = 1
        # self._grid[4,7] = 1

        # Should look roughly like this:
        # _______
        #|  _|   |
        #| |    _|
        #|___|___|

    def plot(self):
        super().plot()
