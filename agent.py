import numpy as np


class agent:
    def __init__(self, PacManZ) -> None:
        self.packmanz = PacManZ
        self.pos_agent = np.zeros((1, 2))
        self.n_shot = 0
        """
            Feature of agent:
        ok    00. Distance to the nearest zombie(high if agent don't have vaccine)
        ok    01. Distance to the pit(high)
        ok    02. Distance to the nearest obstcale(high)
        ok    03. Distance to the exit port(low)
        ok    04. Distance to the vaccine(low)
        ok    05. Number of shot(high)
        ok    06. Number of zombie(low)
        ok    07. Sum of distance to all zombies(low)
        ok    08. Sum of distance to all obstcales(low)
        ok    09. has vaccine(true)
        ok    10. possible move(high)
        ok    11. can_shot(low)
        """
        self.feature_agent = np.random.rand(13)
        self.feature_agent[0] = 100  # Get far from zombie
        self.feature_agent[1] = -100  # Prefer to get away from pit
        self.feature_agent[3] = -100  # Get near to exit port
        self.feature_agent[4] = -10000  # Get near to vaccine
        # self.feature_agent[7] = 20  # Get far from all zombies
        self.feature_agent[8] = 5  # Get far from all obstcales

    def generate_agent(self) -> None:
        x, y = self.packmanz.board.random_blank_cell()
        self.packmanz.board.board[x, y] = "A"
        self.pos_agent = np.array([x, y])

    def can_agent_go(self, x, y) -> bool:
        if (
            self.packmanz.board.board[x, y] == "B"
            or self.packmanz.board.board[x, y] == "V"
            or self.packmanz.board.board[x, y] == "E"
            or (
                self.packmanz.board.has_vaccine
                and self.packmanz.board.board[x, y] == "Z"
            )
        ):
            return True
        else:
            return False

    def possible_agent_move(self) -> list:
        possible_move = []
        D = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for i in range(4):
            new_pos = self.pos_agent[0] + D[i][0], self.pos_agent[1] + D[i][1]
            if self.can_agent_go(new_pos[0], new_pos[1]):
                is_safe = True
                for j in range(self.packmanz.n_zombie):
                    if (
                        self.packmanz.board.man_distance(
                            new_pos[0],
                            new_pos[1],
                            self.packmanz.zombie[j].pos_zombie[0],
                            self.packmanz.zombie[j].pos_zombie[1],
                        )
                        < 2
                        and self.packmanz.board.has_vaccine == False
                    ):
                        is_safe = False
                        break
                if is_safe:
                    possible_move.append(D[i])

        return possible_move

    def agent_state_value(self) -> float:
        distance_to_nearest_zombie = 1000
        sum_distance_to_zombies = 0
        for i in range(self.packmanz.n_zombie):
            dis = self.packmanz.board.man_distance(
                self.pos_agent[0],
                self.pos_agent[1],
                self.packmanz.zombie[i].pos_zombie[0],
                self.packmanz.zombie[i].pos_zombie[1],
            )
            sum_distance_to_zombies += dis
            if dis < distance_to_nearest_zombie:
                distance_to_nearest_zombie = dis

        distance_to_nearest_obstcale = 1000
        sum_distance_to_obstcales = 0
        for i in range(self.packmanz.board.n_obstcale):
            dis = self.packmanz.board.man_distance(
                self.pos_agent[0],
                self.pos_agent[1],
                self.packmanz.board.obstcales[i, 0],
                self.packmanz.board.obstcales[i, 1],
            )
            sum_distance_to_obstcales += dis
            if dis < distance_to_nearest_obstcale:
                distance_to_nearest_obstcale = dis

        distance_to_pit = self.packmanz.board.man_distance(
            self.pos_agent[0],
            self.pos_agent[1],
            self.packmanz.board.pit[0],
            self.packmanz.board.pit[1],
        )

        distance_to_exit_port = self.packmanz.board.man_distance(
            self.pos_agent[0],
            self.pos_agent[1],
            self.packmanz.board.exit_port[0],
            self.packmanz.board.exit_port[1],
        )

        distance_to_vaccine = self.packmanz.board.man_distance(
            self.pos_agent[0],
            self.pos_agent[1],
            self.packmanz.board.vaccine[0],
            self.packmanz.board.vaccine[1],
        )

        possible_move = self.possible_agent_move()

        can_shot = False
        D_shot = [(-2, 0), (2, 0), (0, -2), (0, 2)]
        for i in range(4):
            if (
                self.pos_agent[0] + D_shot[i][0] > 0
                and self.pos_agent[0] + D_shot[i][0]
                <= self.packmanz.board.height
                and self.pos_agent[1] + D_shot[i][1] > 0
                and self.pos_agent[1] + D_shot[i][1]
                <= self.packmanz.board.width
                and self.packmanz.board.board[
                    self.pos_agent[0] + D_shot[i][0],
                    self.pos_agent[1] + D_shot[i][1],
                ]
                == "Z"
            ):
                can_shot = True

        state_value = (
            distance_to_nearest_zombie
            * self.feature_agent[0]
            * (self.packmanz.board.has_vaccine * -1)
            + distance_to_pit * self.feature_agent[1]
            + distance_to_nearest_obstcale * self.feature_agent[2]
            + distance_to_exit_port
            * self.feature_agent[3]
            * (self.packmanz.n_zombie == 0)
            + distance_to_vaccine
            * self.feature_agent[4]
            * (self.packmanz.board.has_vaccine == 0)
            * (self.packmanz.board.has_vaccine == 0)
            + self.n_shot * self.feature_agent[5]
            + self.packmanz.n_zombie * self.feature_agent[6]
            + sum_distance_to_zombies
            * self.feature_agent[7]
            * (self.packmanz.board.has_vaccine * -1)
            + sum_distance_to_obstcales * self.feature_agent[8]
            + self.packmanz.board.has_vaccine * self.feature_agent[9]
            + len(possible_move) * self.feature_agent[10]
            + can_shot * self.feature_agent[11]
        )

        return state_value

    def choose_agent_action(self) -> tuple:
        possible_move = self.possible_agent_move()
        if len(possible_move) == 0:
            return (0, 0)

        max_state_value = -1000000
        max_move = (0, 0)
        for move in possible_move:
            ch = self.packmanz.board.board[
                self.pos_agent[0] + move[0], self.pos_agent[1] + move[1]
            ]
            self.packmanz.board.board[
                self.pos_agent[0], self.pos_agent[1]
            ] = "B"
            self.pos_agent[0] += move[0]
            self.pos_agent[1] += move[1]
            self.packmanz.board.board[
                self.pos_agent[0], self.pos_agent[1]
            ] = "A"
            state_value = self.agent_state_value()

            if state_value > max_state_value:
                max_state_value = state_value
                max_move = move
            self.packmanz.board.board[
                self.pos_agent[0], self.pos_agent[1]
            ] = ch
            self.pos_agent[0] -= move[0]
            self.pos_agent[1] -= move[1]
            self.packmanz.board.board[
                self.pos_agent[0], self.pos_agent[1]
            ] = "A"

        return max_move, max_state_value

    def move_agent(self) -> float:
        move_agent, state_value_agent = self.choose_agent_action()
        if move_agent == 0:
            print("Agent can't move")
            exit()  # Update weight
        self.packmanz.board.board[self.pos_agent[0], self.pos_agent[1]] = "B"
        self.pos_agent[0] += move_agent[0]
        self.pos_agent[1] += move_agent[1]
        if (
            self.packmanz.board.board[self.pos_agent[0], self.pos_agent[1]]
            == "V"
        ):
            self.packmanz.board.has_vaccine = True
            self.packmanz.board.generate_vaccine()
        if (
            self.packmanz.board.board[self.pos_agent[0], self.pos_agent[1]]
            == "Z"
        ):
            self.packmanz.board.has_vaccine = False
            for i in range(self.packmanz.n_zombie):
                if (
                    self.packmanz.zombie[i].pos_zombie == self.pos_agent
                ).all():
                    self.packmanz.zombie[i] = self.packmanz.zombie[-1]
                    self.packmanz.zombie.pop()
                    self.packmanz.n_zombie -= 1
                    break

        self.packmanz.board.board[self.pos_agent[0], self.pos_agent[1]] = "A"

        return state_value_agent
