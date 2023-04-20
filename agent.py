import numpy as np


class agent:
    def __init__(self, pacmanz):
        self.pacmanz = pacmanz
        self.position_agent = self.pacmanz.board.find_empty_cell()
        self.pre_position_agent = self.position_agent
        self.pacmanz.board.board[
            self.position_agent[0], self.position_agent[1]
        ] = self.pacmanz.board.s_agent
        self.zombies_in_close_range = 0
        self.close_range = 4
        self.mid_range = 8
        pass

    def reset(self):
        self.position_agent = self.pacmanz.board.find_empty_cell()
        self.pacmanz.board.board[
            self.position_agent[0], self.position_agent[1]
        ] = self.pacmanz.board.s_agent

    # def can_agent_go(self, x, y, agent_has_vaccine):
    def can_agent_go(self, x, y):
        """
        check if agent can go to the cell
        """
        # Check if it is margin or obstacle or zombie
        if (
            self.pacmanz.board.board[x, y] == self.pacmanz.board.s_margin
            or self.pacmanz.board.board[x, y] == self.pacmanz.board.s_obstacle
            or self.pacmanz.board.board[x, y] == self.pacmanz.board.s_zombie
        ):
            return False
        # if agent_has_vaccine:
        #     return True
        # else:
        #     for d in self.pacmanz.dir_8:
        #         if (
        #             self.pacmanz.board.board[x + d[0], y + d[1]]
        #             == self.pacmanz.board.s_zombie
        #         ):
        #             return False
        # It's not margin or obstacle
        # Agent don't have vaccine
        # There is no zombie around
        return True

    def get_distance(self, x, y, max_dis):
        """
        Distance agent to x, y using BFS
        """
        # Check if it is the target
        if self.position_agent[0] == x and self.position_agent[1] == y:
            return 0
        # Create queue
        queue = []
        queue.append([self.position_agent[0], self.position_agent[1], 0])
        # Create visited as set
        visited = set()
        visited.add((self.position_agent[0], self.position_agent[1]))
        while len(queue) > 0:
            # Pop from queue
            x1, y1, dis = queue.pop(0)

            # If distance is bigger than max_dis then return 0
            if dis > max_dis:
                return 0

            # Add children to queue
            for dir in self.pacmanz.dir_4:
                # Check if it is the target
                if x1 + dir[0] == x and y1 + dir[1] == y:
                    return dis + 1

                if (
                    x1 + dir[0],
                    y1 + dir[1],
                ) not in visited and self.can_agent_go(
                    x1 + dir[0],
                    y1 + dir[1],
                ):
                    queue.append([x1 + dir[0], y1 + dir[1], dis + 1])
                    visited.add((x1 + dir[0], y1 + dir[1]))

        # no path
        return self.pacmanz.Qotr

    def euclidean_distance(self, x, y):
        return np.sqrt(
            (x - self.position_agent[0]) ** 2
            + (y - self.position_agent[1]) ** 2
        )

    def can_agent_shoot(self) -> list[int, list]:
        """
        check if agent can shoot and return which zombie
        """
        if self.pacmanz.shot_left <= 0:
            return False, []
        zombie_in_range = []
        for i in range(self.pacmanz.zombie_left):
            for dir in self.pacmanz.dir_4x2:
                if (
                    (
                        self.pacmanz.zombie[i].position_zombie[0] - dir[0],
                        self.pacmanz.zombie[i].position_zombie[1] - dir[1],
                    )
                    == self.position_agent
                ).all():
                    zombie_in_range.append(i)

        if len(zombie_in_range) > 0:
            return len(zombie_in_range), zombie_in_range
        else:
            return False, []

    def state_value(self):
        """
        return value of state based on weights and theire values
        """

        distance_to_nearest_zombie_in_mid_range = self.pacmanz.Qotr
        distance_to_nearest_zombie_in_close_range = 0
        sum_distance_to_all_zombie_in_mid_range = 0
        zombies_in_close_range = 0
        euclidean_distance_to_nearest_zombie = self.pacmanz.Qotr
        for i in range(self.pacmanz.zombie_left):
            distance_to_zombie = self.get_distance(
                self.pacmanz.zombie[i].position_zombie[0],
                self.pacmanz.zombie[i].position_zombie[1],
                self.mid_range
                if not self.pacmanz.agent_has_vaccine
                else self.pacmanz.Qotr,
            )
            if distance_to_zombie <= self.close_range:
                zombies_in_close_range += 1
            if distance_to_zombie < distance_to_nearest_zombie_in_mid_range:
                if distance_to_zombie <= self.close_range:
                    distance_to_nearest_zombie_in_close_range = (
                        distance_to_zombie
                    )
                distance_to_nearest_zombie_in_mid_range = distance_to_zombie
                euclidean_distance_to_nearest_zombie = self.euclidean_distance(
                    self.pacmanz.zombie[i].position_zombie[0],
                    self.pacmanz.zombie[i].position_zombie[1],
                )
            sum_distance_to_all_zombie_in_mid_range += distance_to_zombie

        self.zombies_in_close_range = zombies_in_close_range

        distance_to_pit_in_mid_range = self.get_distance(
            self.pacmanz.board.position_pit[0],
            self.pacmanz.board.position_pit[1],
            self.mid_range,
        )

        distance_to_nearest_obstacle_in_mid_range = np.inf
        sum_distance_to_all_obstacle_pit_in_mid_range = (
            distance_to_pit_in_mid_range
        )

        for i in range(self.pacmanz.board.n_obstcale):
            distance_to_obstacle = self.get_distance(
                self.pacmanz.board.position_obstacle[i][0],
                self.pacmanz.board.position_obstacle[i][1],
                self.mid_range,
            )
            if (
                distance_to_obstacle
                < distance_to_nearest_obstacle_in_mid_range
            ):
                distance_to_nearest_obstacle_in_mid_range = (
                    distance_to_obstacle
                )
            sum_distance_to_all_obstacle_pit_in_mid_range += (
                distance_to_obstacle
            )

        distance_to_exit_port = self.get_distance(
            self.pacmanz.board.position_exit_port[0],
            self.pacmanz.board.position_exit_port[1],
            self.pacmanz.agent_has_vaccine,
        )

        can_agent_shoot = self.can_agent_shoot()

        distance_to_vaccine = self.get_distance(
            self.pacmanz.board.position_vaccine[0],
            self.pacmanz.board.position_vaccine[1],
            self.pacmanz.Qotr,
        )

        number_of_possible_move = len(self.possible_moves())

        values = np.array(
            [
                # 00. Distance to the nearest zombie in mid range with vaccine
                distance_to_nearest_zombie_in_mid_range
                if self.pacmanz.agent_has_vaccine
                else 0,
                # 01. Distance to the nearest zombie in mid range without vaccine
                distance_to_nearest_zombie_in_mid_range
                if not self.pacmanz.agent_has_vaccine
                else 0,
                # 02. Sum of distance to all zombies in mid range with vaccine
                sum_distance_to_all_zombie_in_mid_range
                if self.pacmanz.agent_has_vaccine
                else 0,
                # 03. Sum of distance to all zombies in mid range without vaccine
                sum_distance_to_all_zombie_in_mid_range
                if not self.pacmanz.agent_has_vaccine
                else 0,
                # 04. Distance to the nearest obstcale in mid range without vaccine
                distance_to_nearest_obstacle_in_mid_range
                if not self.pacmanz.agent_has_vaccine
                else 0,
                # 05. sum of distance to all obstcales in mid range without vaccine
                sum_distance_to_all_obstacle_pit_in_mid_range
                if not self.pacmanz.agent_has_vaccine
                else 0,
                # 06. Distance to the pit in mid range with vaccine
                distance_to_pit_in_mid_range
                if self.pacmanz.agent_has_vaccine
                else 0,
                # 07. Distance to the pit in mid range without vaccine
                distance_to_pit_in_mid_range
                if not self.pacmanz.agent_has_vaccine
                else 0,
                # 08. number of shot left with vaccine
                self.pacmanz.shot_left
                if self.pacmanz.agent_has_vaccine
                else 0,
                # 09. number of shot left without vaccine
                self.pacmanz.shot_left
                if not self.pacmanz.agent_has_vaccine
                else 0,
                # 10. number of zombies in close range with vaccine
                zombies_in_close_range
                if self.pacmanz.agent_has_vaccine
                else 0,
                # 11. number of zombies in close range without vaccine
                zombies_in_close_range
                if not self.pacmanz.agent_has_vaccine
                else 0,
                # 12. number of shots left
                self.pacmanz.shot_left,
                # 13. can agent shoot with vaccine
                1 if can_agent_shoot and self.pacmanz.agent_has_vaccine else 0,
                # 14. can agent shoot without vaccine
                1
                if can_agent_shoot and not self.pacmanz.agent_has_vaccine
                else 0,
                # 15. distance to vaccine without vaccine
                distance_to_vaccine
                if not self.pacmanz.agent_has_vaccine
                else 0,
                # 16. Distance to exit port when no zombie left
                distance_to_exit_port if self.pacmanz.zombie_left == 0 else 0,
                # 17. Number of possible moves with vaccine
                number_of_possible_move
                if not self.pacmanz.agent_has_vaccine
                else 0,
                # 18. Number of possible moves without vaccine
                number_of_possible_move
                if self.pacmanz.agent_has_vaccine
                else 0,
                # 19. Euclidean distance to the nearest zombie with vaccine
                euclidean_distance_to_nearest_zombie
                if self.pacmanz.agent_has_vaccine
                else 0,
                # 20. Euclidean distance to the nearest zombie without vaccine
                euclidean_distance_to_nearest_zombie
                if not self.pacmanz.agent_has_vaccine
                else 0,
                # 21. Distance to the nearest zombie in close range with vaccine
                distance_to_nearest_zombie_in_close_range
                if self.pacmanz.agent_has_vaccine
                else 0,
                # 22. Distance to the nearest zombie in close range without vaccine
                distance_to_nearest_zombie_in_close_range
                if not self.pacmanz.agent_has_vaccine
                else 0,
            ]
        )

        # Add sqrt to all values after normalizing [0, 1] to emphasize the on near distances(around 0)
        return (
            np.sum(
                self.pacmanz.agent_weights
                * (values / self.pacmanz.agent_value_normalizer) ** 0.25
            ),
            (values / self.pacmanz.agent_value_normalizer) ** 0.25,
        )

    def possible_moves(self):
        """
        return possible moves of agent
        """
        possible_moves = []
        for dir in self.pacmanz.dir_4:
            if self.can_agent_go(
                self.position_agent[0] + dir[0],
                self.position_agent[1] + dir[1],
                # self.pacmanz.agent_has_vaccine,
            ):
                possible_moves.append(dir)

        return np.array(possible_moves)

    def update_weights_and_reset(self, is_win):
        """
        update weights
        """
        self.position_agent = self.pre_position_agent
        pre_state_value, pre_values = self.state_value()

        if is_win:
            self.pacmanz.agent_weights += (
                self.pacmanz.learning_rate
                * (self.pacmanz.agent_win_reward - pre_state_value)
                * pre_values
            )
            print("Agent Win")
            print(f"Score: {self.pacmanz.score}\n{'-' * 20}")
        else:
            self.pacmanz.agent_weights += (
                self.pacmanz.learning_rate
                * (self.pacmanz.agent_lose_reward - pre_state_value)
                * pre_values
            )
            print("Agent Lose")
            print(f"Score: {self.pacmanz.score}\n{'-' * 20}")

        # reset game
        self.pacmanz.reset()

    def choose_action(self) -> list[int, int]:
        """
        choose action based on state value of possible actions
        return best action, state value
        """
        possible_moves = self.possible_moves()
        if len(possible_moves) == 0:
            return None, None

        best_action = None
        best_state_value = -np.inf

        for move in possible_moves:
            # Do move
            self.pacmanz.board.board[
                self.position_agent[0], self.position_agent[1]
            ] = self.pacmanz.board.s_empty
            self.position_agent[0] += move[0]
            self.position_agent[1] += move[1]
            s_cell = self.pacmanz.board.board[
                self.position_agent[0], self.position_agent[1]
            ]
            self.pacmanz.board.board[
                self.position_agent[0], self.position_agent[1]
            ] = self.pacmanz.board.s_agent

            # Get state value
            state_value, _ = self.state_value()

            if state_value > best_state_value:
                best_state_value = state_value
                best_action = move

            # Back to original state
            self.pacmanz.board.board[
                self.position_agent[0], self.position_agent[1]
            ] = s_cell
            self.position_agent[0] -= move[0]
            self.position_agent[1] -= move[1]
            self.pacmanz.board.board[
                self.position_agent[0], self.position_agent[1]
            ] = self.pacmanz.board.s_agent

        return best_action, best_state_value

    def shoot(self, zombie_id):
        if self.pacmanz.shot_left == 0:
            return
        self.pacmanz.shot_left -= 1
        self.pacmanz.score += self.pacmanz.score_shoot_zombie
        self.pacmanz.zombie[zombie_id].update_weights_and_reset(
            is_win=False, is_in_pit=False
        )
        # Update board
        self.pacmanz.board.update_cell(
            self.pacmanz.zombie[zombie_id].position_zombie[0],
            self.pacmanz.zombie[zombie_id].position_zombie[1],
            self.pacmanz.board.s_empty,
            self.pacmanz.board.c_empty,
        )
        # Remove zombie from list
        self.pacmanz.zombie.pop(zombie_id)
        self.pacmanz.zombie_left -= 1

    def vaccinate_zombie(self):
        if not self.pacmanz.agent_has_vaccine:
            return False

        # Check if there is zombie in distance 1
        for zombie_id in range(self.pacmanz.zombie_left):
            for dir in self.pacmanz.dir_8:
                if (
                    self.pacmanz.zombie[zombie_id].position_zombie[0]
                    == self.position_agent[0] + dir[0]
                    and self.pacmanz.zombie[zombie_id].position_zombie[1]
                    == self.position_agent[1] + dir[1]
                ):
                    # Vaccinate zombie
                    self.pacmanz.score += self.pacmanz.score_vaccinate_zombie
                    self.pacmanz.agent_has_vaccine = False
                    self.pacmanz.zombie[zombie_id].update_weights_and_reset(
                        is_win=False, is_in_pit=False
                    )
                    # Update board
                    self.pacmanz.board.update_cell(
                        self.pacmanz.zombie[zombie_id].position_zombie[0],
                        self.pacmanz.zombie[zombie_id].position_zombie[1],
                        self.pacmanz.board.s_empty,
                        self.pacmanz.board.c_empty,
                    )
                    # Remove zombie from list
                    self.pacmanz.zombie.pop(zombie_id)
                    self.pacmanz.zombie_left -= 1
                    return True

        return False

    def check_for_shooting(self):
        # Check if agent must shoot zombie
        # If there is more than one zombie in distance 2
        # we must shoot otherwise we can run away
        if self.zombies_in_close_range > 1 and self.pacmanz.shot_left > 0:
            # Check if agent can shoot
            can_shoot, zombie_in_range = self.can_agent_shoot()
            if can_shoot:
                # Shoot all zombies in range except last one if agent has vaccine
                for i in range(
                    len(zombie_in_range) - 1,
                    self.pacmanz.agent_has_vaccine - 1,
                    -1,
                ):
                    # Shoot zombie
                    self.shoot(zombie_in_range[i])

    def move(self):
        """
        move agent
        """
        self.check_for_shooting()
        # Choose action
        best_action, best_state_value = self.choose_action()

        # Update current cell to pre state
        self.pacmanz.board.update_cell_before_move(
            self.position_agent[0], self.position_agent[1]
        )

        if best_state_value == None:
            # There is no move so agent lost
            # Update weights and reset game
            self.update_weights_and_reset(is_win=False)
            return self.state_value()

        self.pre_position_agent = self.position_agent
        # Do move
        self.position_agent[0] += best_action[0]
        self.position_agent[1] += best_action[1]
        # type of cell that agent is moving to
        s_cell = self.pacmanz.board.board[
            self.position_agent[0], self.position_agent[1]
        ]
        # change current cell to agent
        self.pacmanz.board.update_cell(
            self.position_agent[0],
            self.position_agent[1],
            self.pacmanz.board.s_agent,
            self.pacmanz.board.c_agent,
        )

        # Check if cell was vaccine
        if s_cell == self.pacmanz.board.s_vaccine:
            # Check if agent hasn't vaccine
            if not self.pacmanz.agent_has_vaccine:
                self.pacmanz.agent_has_vaccine = True
                self.pacmanz.score += self.pacmanz.score_get_vaccine
                # Generate new vaccine
                self.pacmanz.board.generate_vaccine()

        # Check if cell was pit
        elif s_cell == self.pacmanz.board.s_pit:
            # Update weights and reset game
            self.update_weights_and_reset(is_win=False)
        # Check if cell is exit port and all zombies gone = win
        elif (
            s_cell == self.pacmanz.board.s_exit_port
            and self.pacmanz.zombie_left == 0
        ):
            # Update weights and reset game
            self.update_weights_and_reset(is_win=True)

        self.check_for_shooting()

        # Check if can vaccinate zombie
        self.vaccinate_zombie()

        return best_state_value
