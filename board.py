import numpy as np


class PacManZ:
    def __init__(self, height, width, n_zombie, n_obstcale, n_shot) -> None:
        self.height = height
        self.width = width
        self.board = np.full((height + 2, width + 2), "B")
        self.n_zombie = n_zombie
        self.pos_zombie = np.zeros((n_zombie, 2))
        self.pos_agent = np.zeros((1, 2))
        self.pit = np.zeros((1, 2))
        self.vaccine = np.zeros((1, 2))
        self.exit_port = np.zeros((1, 2))
        self.n_obstcale = n_obstcale
        self.obstcales = np.zeros((n_obstcale, 2))
        self.n_shot = n_shot
        self.has_vaccine = False
        """
            Feature of agent:
        ok    1. Distance to the nearest zombie(high)
        ok    2. Distance to the pit(high)
        ok    3. Distance to the nearest obstcale(high)
        ok    4. Distance to the exit port(low)
        ok    5. Distance to the vaccine(low)
        ok    6. Number of shot(low)
        ok    7. Number of zombie(low)
        ok    8. Sum of distance to all zombies(low)
        ok    9. Sum of distance to all obstcales(low)
        ok    10. has vaccine(true)
        ok    11. possible move(high)
        ok    12. can_shot(low)
        """
        self.feature_agent = np.random.rand(13)
        self.feature_agent[0] = -100
        pass

    def is_cell_blank(self, x, y) -> bool:
        if self.board[x, y] == "B":
            return True
        else:
            return False

    def random_blank_cell(self) -> tuple:
        x = np.random.randint(1, self.height + 1)
        y = np.random.randint(1, self.width + 1)
        while self.is_cell_blank(x, y) == False:
            x = np.random.randint(1, self.height + 1)
            y = np.random.randint(1, self.width + 1)
        return x, y

    def generate_board(self) -> None:
        # Create a border
        self.board[0, :] = "M"
        self.board[-1, :] = "M"
        self.board[:, 0] = "M"
        self.board[:, -1] = "M"

        # Create a pit
        # choose x, y randomly from 1 to height, 1 to width
        x, y = self.random_blank_cell()
        self.board[x, y] = "P"
        self.pit = np.array([x, y])

        # Create a exit port
        # choose x, y randomly from 1 to height, 1 to width
        x, y = self.random_blank_cell()
        self.board[x, y] = "E"
        self.exit_port = np.array([x, y])

        # Create obstcales
        for i in range(self.n_obstcale):
            x, y = self.random_blank_cell()
            self.board[x, y] = "O"
            self.obstcales[i, :] = x, y

        # Create agent
        x, y = self.random_blank_cell()
        self.board[x, y] = "A"
        self.pos_agent = np.array([x, y])

        # Create zombies
        for i in range(self.n_zombie):
            x, y = self.random_blank_cell()
            self.board[x, y] = "Z"
            self.pos_zombie[i, :] = x, y

        # Create vaccine
        x, y = self.random_blank_cell()
        self.board[x, y] = "V"
        self.vaccine = np.array([x, y])

        pass

    def man_distance(self, x1, y1, x2, y2) -> float:
        return abs(x1 - x2) + abs(y1 - y2)

    def can_agent_go(self, x, y) -> bool:
        if self.board[x, y] == "B" or self.board[x, y] == "V":
            return True
        else:
            return False

    def possible_agent_move(self) -> list:
        possible_move = []
        D = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        X = [-1, 1, 0, 0]
        Y = [0, 0, -1, 1]

        for i in range(4):
            if (
                self.board[
                    self.pos_agent[0] + D[i][0], self.pos_agent[1] + D[i][1]
                ]
                == "B"
            ):
                is_safe = True
                for j in range(self.n_zombie):
                    if (
                        self.man_distance(
                            self.pos_agent[0] + D[i][0],
                            self.pos_agent[1] + D[i][1],
                            self.pos_zombie[j, 0],
                            self.pos_zombie[j, 1],
                        )
                        < 2
                    ):
                        is_safe = False
                        break
                if is_safe:
                    possible_move.append(D[i])

        return possible_move

    def agent_state_value(self) -> float:
        distance_to_nearest_zombie = 1000
        sum_distance_to_zombies = 0
        for i in range(self.n_zombie):
            dis = self.man_distance(
                self.pos_agent[0],
                self.pos_agent[1],
                self.pos_zombie[i, 0],
                self.pos_zombie[i, 1],
            )
            sum_distance_to_zombies += dis
            if dis < distance_to_nearest_zombie:
                distance_to_nearest_zombie = dis

        distance_to_nearest_obstcale = 1000
        sum_distance_to_obstcales = 0
        for i in range(self.n_obstcale):
            dis = self.man_distance(
                self.pos_agent[0],
                self.pos_agent[1],
                self.obstcales[i, 0],
                self.obstcales[i, 1],
            )
            sum_distance_to_obstcales += dis
            if dis < distance_to_nearest_obstcale:
                distance_to_nearest_obstcale = dis

        distance_to_pit = self.man_distance(
            self.pos_agent[0],
            self.pos_agent[1],
            self.pit[0],
            self.pit[1],
        )

        distance_to_exit_port = self.man_distance(
            self.pos_agent[0],
            self.pos_agent[1],
            self.exit_port[0],
            self.exit_port[1],
        )

        distance_to_vaccine = self.man_distance(
            self.pos_agent[0],
            self.pos_agent[1],
            self.vaccine[0],
            self.vaccine[1],
        )

        possible_move = self.possible_agent_move()

        can_shot = False
        if (
            self.pos_agent[0] + 2 <= self.width
            and self.board[self.pos_agent[0] + 2, self.pos_agent[1]] == "Z"
        ):
            can_shot = True
        elif (
            self.pos_agent[0] - 2 >= 1
            and self.board[self.pos_agent[0] - 2, self.pos_agent[1]] == "Z"
        ):
            can_shot = True
        elif (
            self.pos_agent[1] + 2 <= self.height
            and self.board[self.pos_agent[0], self.pos_agent[1] + 2] == "Z"
        ):
            can_shot = True
        elif (
            self.pos_agent[1] - 2 >= 1
            and self.board[self.pos_agent[0], self.pos_agent[1] - 2] == "Z"
        ):
            can_shot = True

        state_value = (
            distance_to_nearest_zombie * self.feature_agent[0]
            + distance_to_pit * self.feature_agent[1]
            + distance_to_nearest_obstcale * self.feature_agent[2]
            + distance_to_exit_port * self.feature_agent[3]
            + distance_to_vaccine * self.feature_agent[4]
            + self.n_shot * self.feature_agent[5]
            + self.n_zombie * self.feature_agent[6]
            + sum_distance_to_zombies * self.feature_agent[7]
            + sum_distance_to_obstcales * self.feature_agent[8]
            + self.has_vaccine * self.feature_agent[9]
            + len(possible_move) * self.feature_agent[10]
        )

        return state_value

    def choose_agent_action(self) -> tuple:
        possible_move = self.possible_agent_move()
        if len(possible_move) == 0:
            return (0, 0)

        max_state_value = -1000000
        max_move = (0, 0)
        for move in possible_move:
            self.board[self.pos_agent[0], self.pos_agent[1]] = "B"
            self.pos_agent[0] += move[0]
            self.pos_agent[1] += move[1]
            self.board[self.pos_agent[0], self.pos_agent[1]] = "A"
            state_value = self.agent_state_value()
            if state_value > max_state_value:
                max_state_value = state_value
                max_move = move
            self.board[self.pos_agent[0], self.pos_agent[1]] = "B"
            self.pos_agent[0] -= move[0]
            self.pos_agent[1] -= move[1]
            self.board[self.pos_agent[0], self.pos_agent[1]] = "A"

        return max_move, max_state_value

    def print_board(self) -> None:
        print(self.board)
        pass
