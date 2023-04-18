from agent import agent
# from board import board
# from pacmanz import pacmanz
# from zombie import zombie


class zombie:
    def __init__(self, pacmanz):
        self.pacmanz = pacmanz
        self.position_zombie = self.pacmanz.board.find_empty_cell()
        self.pacmanz.board.board[self.position_zombie[0], self.position_zombie[1]] = self.pacmanz.board.s_zombie
        pass
