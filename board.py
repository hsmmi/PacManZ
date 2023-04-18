# from agent import agent
# from pacmanz import pacmanz
# from zombie import zombie
import numpy as np
import pygame


class board:
    def __init__(self, board_height, board_width, n_obstcale) -> None:
        # Store initial values
        self.board_height = board_height
        self.board_width = board_width
        self.n_obstcale = n_obstcale

        # Create character map
        self.s_zombie = "Z"
        self.c_zombie = (255, 0, 0)  # Red
        self.s_agent = "A"
        self.c_agent = (0, 0, 255)  # Blue
        self.s_obstacle = "O"
        self.c_obstacle = (128, 128, 128)  # Gray
        self.s_margin = "#"
        self.c_margin = (32, 32, 32)  # Dark gray
        self.s_empty = "_"
        self.c_empty = (255, 255, 255)  # White
        self.s_vaccine = "V"
        self.c_vaccine = (0, 255, 0)  # Green
        self.s_pit = "P"
        self.c_pit = (139, 69, 19)  # Brown
        self.s_exit_port = "E"
        self.c_exit_port = (128, 0, 128)
        # map character to color
        self.map_character_color = {
            self.s_zombie: self.c_zombie,
            self.s_agent: self.c_agent,
            self.s_obstacle: self.c_obstacle,
            self.s_margin: self.c_margin,
            self.s_empty: self.c_empty,
            self.s_vaccine: self.c_vaccine,
            self.s_pit: self.c_pit,
            self.s_exit_port: self.c_exit_port,
        }

        # Create position
        self.board = None
        self.position_obstacle = None
        self.position_pit = None
        self.position_exit_port = None
        self.position_vaccine = None

        # Create board
        self.create_board()
        self.init_pygame()
        self.update_whole_board()
        pass

    def is_cell_empty(self, x: int, y: int) -> bool:
        # Check if cell is empty
        if self.board[x, y] == self.s_empty:
            return True
        else:
            return False

    def find_empty_cell(self):
        x = np.random.randint(1, self.board_height + 1)
        y = np.random.randint(1, self.board_width + 1)
        while not self.is_cell_empty(x, y):
            x = np.random.randint(1, self.board_height + 1)
            y = np.random.randint(1, self.board_width + 1)
        return np.array([x, y])

    def generate_vaccine(self):
        x, y = self.find_empty_cell()
        self.board[x, y] = self.s_vaccine
        self.position_vaccine = np.array([x, y])
        pass

    def create_board(self):
        # Create board
        self.board = np.full(
            (self.board_height + 2, self.board_width + 2), self.s_empty
        )

        # Create margin
        self.board[0, :] = self.s_margin
        self.board[-1, :] = self.s_margin
        self.board[:, 0] = self.s_margin
        self.board[:, -1] = self.s_margin

        # Create obstacles
        self.position_obstacle = np.full((self.n_obstcale, 2), -1)
        for i in range(self.n_obstcale):
            x, y = self.find_empty_cell()
            self.board[x, y] = self.s_obstacle
            self.position_obstacle[i, :] = [x, y]

        # Create pit
        x, y = self.find_empty_cell()
        self.board[x, y] = self.s_pit
        self.position_pit = np.array([x, y])

        # Create exit port
        x, y = self.find_empty_cell()
        self.board[x, y] = self.s_exit_port
        self.position_exit_port = np.array([x, y])

        # Create vaccine
        self.generate_vaccine()
        pass

    def create_rect(self, color, x, y):
        pygame.draw.rect(
            self.screen,
            color,
            (
                y * self.zoom + self.line_width,
                x * self.zoom + self.line_width,
                self.zoom - 2 * +self.line_width,
                self.zoom - 2 * self.line_width,
            ),
        )
        # Update screen
        pygame.display.update()
        pass

    def init_pygame(self):
        # Initialize pygame
        pygame.init()

        # Set screen size
        self.zoom = 30
        self.line_width = 1
        self.screen = pygame.display.set_mode(
            (
                (self.board_width + 2) * self.zoom,
                (self.board_height + 2) * self.zoom,
            )
        )

        # Create Grid
        for i in range(self.board_height + 2):
            pygame.draw.line(
                self.screen,
                self.c_margin,
                (0, i * self.zoom),
                ((self.board_width + 2) * self.zoom, i * self.zoom),
                self.line_width,
            )
        for i in range(self.board_width + 2):
            pygame.draw.line(
                self.screen,
                self.c_margin,
                (i * self.zoom, 0),
                (i * self.zoom, (self.board_height + 2) * self.zoom),
                1,
            )

        # Update screen
        pygame.display.update()

    def update_whole_board(self):
        # Create board
        for i in range(self.board_height + 2):
            for j in range(self.board_width + 2):
                self.create_rect(
                    self.map_character_color[self.board[i, j]],
                    i,
                    j,
                )
