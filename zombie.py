import numpy as np

from board import board


class zombie:
    def __init__(self, PacManZ) -> None:
        self.packmanz = PacManZ
        self.pos_zombie = np.zeros((1, 2))
        """
            Feature of zombie:
            0. Distace to the agent(low if agent don't have vaccine)
            1. Distance to the nearest obstcale(high)
            2. Distance to the pit(high)
            3. has vaccine(-1 if agent has vaccine)(low)
            4. possible move(high)
            5. can killed by shot(false)
            6. Number of shot(low)
        """
        self.feature_zombie = np.random.rand(7)
        pass

    def generate_zombie(self) -> None:
        x, y = self.packmanz.board.random_blank_cell()
        self.packmanz.board.board[x, y] = "Z"
        self.pos_zombie = x, y

    def can_zombie_go(self, x, y) -> bool:
        if (
            self.packmanz.board.board[x, y] == "B"
            or (self.packmanz.board.has_vaccine == False and self.packmanz.board.board[x, y] == "A")
        ):
            return True
        else:
            return False

    def possible_zombie_move(self) -> list:
        possible_move = []
        D = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        X = [-1, 1, 0, 0]
        Y = [0, 0, -1, 1]

        for i in range(4):
            if self.can_zombie_go(
                self.pos_zombie[0] + D[i][0], self.pos_zombie[1] + D[i][1]
            ):
                possible_move.append(D[i])

        return possible_move

    def zombie_state_value(self) -> float:
        distance_to_agent = self.packmanz.board.man_distance(
            self.pos_zombie[0],
            self.pos_zombie[1],
            self.packmanz.board.pos_agent[0],
            self.packmanz.board.pos_agent[1],
        )
        sum_distance_to_zombies = 0

        distance_to_nearest_obstcale = 1000
        sum_distance_to_obstcales = 0
        for i in range(self.n_obstcale):
            dis = self.man_distance(
                self.pos_zombie[0],
                self.pos_zombie[1],
                self.obstcales[i, 0],
                self.obstcales[i, 1],
            )
            sum_distance_to_obstcales += dis
            if dis < distance_to_nearest_obstcale:
                distance_to_nearest_obstcale = dis

        distance_to_pit = self.man_distance(
            self.pos_zombie[0],
            self.pos_zombie[1],
            self.pit[0],
            self.pit[1],
        )

        distance_to_exit_port = self.man_distance(
            self.pos_zombie[0],
            self.pos_zombie[1],
            self.exit_port[0],
            self.exit_port[1],
        )

        distance_to_vaccine = self.man_distance(
            self.pos_zombie[0],
            self.pos_zombie[1],
            self.vaccine[0],
            self.vaccine[1],
        )

        possible_move = self.possible_zombie_move()

        can_shot = False
        if (
            self.pos_zombie[0] + 2 <= self.width
            and self.packmanz.board.board[self.pos_zombie[0] + 2, self.pos_zombie[1]]
            == "Z"
        ):
            can_shot = True
        elif (
            self.pos_zombie[0] - 2 >= 1
            and self.packmanz.board.board[self.pos_zombie[0] - 2, self.pos_zombie[1]]
            == "Z"
        ):
            can_shot = True
        elif (
            self.pos_zombie[1] + 2 <= self.height
            and self.packmanz.board.board[self.pos_zombie[0], self.pos_zombie[1] + 2]
            == "Z"
        ):
            can_shot = True
        elif (
            self.pos_zombie[1] - 2 >= 1
            and self.packmanz.board.board[self.pos_zombie[0], self.pos_zombie[1] - 2]
            == "Z"
        ):
            can_shot = True

        state_value = (
            distance_to_agent * self.feature_zombie[0]
            + distance_to_pit * self.feature_zombie[1]
            + distance_to_nearest_obstcale * self.feature_zombie[2]
            + distance_to_exit_port * self.feature_zombie[3]
            + distance_to_vaccine * self.feature_zombie[4]
            + self.n_shot * self.feature_zombie[5]
            + self.n_zombie * self.feature_zombie[6]
            + sum_distance_to_zombies * self.feature_zombie[7]
            + sum_distance_to_obstcales * self.feature_zombie[8]
            + self.has_vaccine * self.feature_zombie[9]
            + len(possible_move) * self.feature_zombie[10]
        )

        return state_value

    def choose_zombie_action(self) -> tuple:
        possible_move = self.possible_zombie_move()
        if len(possible_move) == 0:
            return (0, 0)

        max_state_value = -1000000
        max_move = (0, 0)
        for move in possible_move:
            self.packmanz.board.board[self.pos_zombie[0], self.pos_zombie[1]] = "B"
            self.pos_zombie[0] += move[0]
            self.pos_zombie[1] += move[1]
            self.packmanz.board.board[self.pos_zombie[0], self.pos_zombie[1]] = "A"
            state_value = self.zombie_state_value()
            if state_value > max_state_value:
                max_state_value = state_value
                max_move = move
            self.packmanz.board.board[self.pos_zombie[0], self.pos_zombie[1]] = "B"
            self.pos_zombie[0] -= move[0]
            self.pos_zombie[1] -= move[1]
            self.packmanz.board.board[self.pos_zombie[0], self.pos_zombie[1]] = "A"

        return max_move, max_state_value
