import numpy as np

from board import board
from agent import agent
from zombie import zombie


class PacManZ(board, agent, zombie):
    def __init__(self, height, width, n_zombie, n_obstcale, n_shot) -> None:
        self.board = board(self, height, width, n_obstcale, n_shot)
        self.agent = agent(self)
        self.n_zombie = n_zombie
        self.zombie = [zombie(self) for i in range(n_zombie)]

        self.board.generate_board()
        self.agent.generate_agent()
        for i in range(n_zombie):
            self.zombie[i].generate_zombie()

    def play(self):
        while True:
            print(self.agent.move_agent())
            self.board.print_board()
            # wait for key
            input()
