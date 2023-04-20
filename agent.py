import numpy as np


class agent:
    def __init__(self, pacmanz):
        self.pacmanz = pacmanz
        self.position_agent = self.pacmanz.board.find_empty_cell()
        self.pacmanz.board.board[
            self.position_agent[0], self.position_agent[1]
        ] = self.pacmanz.board.s_agent
        self.zombies_in_distance_2 = 0
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

    def get_distance(self, x, y, is_zombie):
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
                    # is_zombie or self.pacmanz.agent_has_vaccine,
                ):
                    queue.append([x1 + dir[0], y1 + dir[1], dis + 1])
                    visited.add((x1 + dir[0], y1 + dir[1]))

        # no path
        return self.pacmanz.Qotr

    def can_agent_shoot(self) -> list[bool, list]:
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
                        self.pacmanz.zombie[i].position_zombie[0] + dir[0],
                        self.pacmanz.zombie[i].position_zombie[1] + dir[1],
                    )
                    == self.position_agent
                ).all():
                    zombie_in_range.append(i)

        if len(zombie_in_range) > 0:
            return True, zombie_in_range
        else:
            return False, []

    def state_value(self):
        """
        return value of state based on weights and theire values
        """

        distance_to_nearest_zombie = self.pacmanz.Qotr
        sum_distance_to_all_zombie = 0
        zombies_in_distance_2 = 0
        for i in range(self.pacmanz.zombie_left):
            distance_to_zombie = self.get_distance(
                self.pacmanz.zombie[i].position_zombie[0],
                self.pacmanz.zombie[i].position_zombie[1],
                True,
            )
            if distance_to_zombie <= 2:
                zombies_in_distance_2 += 1
            if distance_to_zombie < distance_to_nearest_zombie:
                distance_to_nearest_zombie = distance_to_zombie
            sum_distance_to_all_zombie += distance_to_zombie
        self.zombies_in_distance_2 = zombies_in_distance_2

        distance_to_pit = self.get_distance(
            self.pacmanz.board.position_pit[0],
            self.pacmanz.board.position_pit[1],
            self.pacmanz.agent_has_vaccine,
        )

        distance_to_nearest_obstacle = np.inf
        sum_distance_to_all_obstacle_pit = distance_to_pit

        for i in range(self.pacmanz.board.n_obstcale):
            distance_to_obstacle = self.get_distance(
                self.pacmanz.board.position_obstacle[i][0],
                self.pacmanz.board.position_obstacle[i][1],
                self.pacmanz.agent_has_vaccine,
            )
            if distance_to_obstacle < distance_to_nearest_obstacle:
                distance_to_nearest_obstacle = distance_to_obstacle
            sum_distance_to_all_obstacle_pit += distance_to_obstacle

        distance_to_exit_port = self.get_distance(
            self.pacmanz.board.position_exit_port[0],
            self.pacmanz.board.position_exit_port[1],
            self.pacmanz.agent_has_vaccine,
        )

        can_agent_shoot = self.can_agent_shoot()

        distance_to_vaccine = self.get_distance(
            self.pacmanz.board.position_vaccine[0],
            self.pacmanz.board.position_vaccine[1],
            self.pacmanz.agent_has_vaccine,
        )

        values = np.array(
            [
                # 00. Distance to the nearest zombie with vaccine
                distance_to_nearest_zombie
                if self.pacmanz.agent_has_vaccine
                else 0,
                # 01. Distance to the nearest zombie without vaccine
                distance_to_nearest_zombie
                if not self.pacmanz.agent_has_vaccine
                else 0,
                # 02. Sum of distance to all zombies with vaccine
                sum_distance_to_all_zombie
                if self.pacmanz.agent_has_vaccine
                else 0,
                # 03. Sum of distance to all zombies without vaccine
                sum_distance_to_all_zombie
                if not self.pacmanz.agent_has_vaccine
                else 0,
                # 04. Distance to the nearest obstcale with vaccine
                distance_to_nearest_obstacle
                if self.pacmanz.agent_has_vaccine
                else 0,
                # 05. Distance to the nearest obstcale without vaccine
                distance_to_nearest_obstacle
                if not self.pacmanz.agent_has_vaccine
                else 0,
                # 06. sum of distance to all obstcales with vaccine
                sum_distance_to_all_obstacle_pit
                if self.pacmanz.agent_has_vaccine
                else 0,
                # 07. sum of distance to all obstcales without vaccine
                sum_distance_to_all_obstacle_pit
                if not self.pacmanz.agent_has_vaccine
                else 0,
                # 08. Distance to the exit port with vaccine
                distance_to_exit_port if self.pacmanz.agent_has_vaccine else 0,
                # 09. Distance to the exit port without vaccine
                distance_to_exit_port
                if not self.pacmanz.agent_has_vaccine
                else 0,
                # 10. Distance to the pit with vaccine
                distance_to_pit if self.pacmanz.agent_has_vaccine else 0,
                # 11. Distance to the pit without vaccine
                distance_to_pit if not self.pacmanz.agent_has_vaccine else 0,
                # 12. number of shot left with vaccine
                self.pacmanz.shot_left
                if self.pacmanz.agent_has_vaccine
                else 0,
                # 13. number of shot left without vaccine
                self.pacmanz.shot_left
                if not self.pacmanz.agent_has_vaccine
                else 0,
                # 14. number of zombies in distance 2 with vaccine
                zombies_in_distance_2 if self.pacmanz.agent_has_vaccine else 0,
                # 15. number of zombies in distance 2 without vaccine
                zombies_in_distance_2
                if not self.pacmanz.agent_has_vaccine
                else 0,
                # 16. number of shots left
                self.pacmanz.shot_left,
                # 17. can agent shoot with vaccine
                1 if can_agent_shoot and self.pacmanz.agent_has_vaccine else 0,
                # 18. can agent shoot without vaccine
                1
                if can_agent_shoot and not self.pacmanz.agent_has_vaccine
                else 0,
                # 19. distance to vaccine without vaccine
                distance_to_vaccine
                if not self.pacmanz.agent_has_vaccine
                else 0,
                # 20. Distance to exit port when no zombie left
                distance_to_exit_port if self.pacmanz.zombie_left == 0 else 0,
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
        state_value, values = self.state_value()
        if is_win:
            self.pacmanz.agent_weights += (
                self.pacmanz.learning_rate
                * (self.pacmanz.agent_win_reward - state_value)
                * values
            )
        else:
            self.pacmanz.agent_weights += (
                self.pacmanz.learning_rate
                * (self.pacmanz.agent_lose_reward - state_value)
                * values
            )

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

    def move(self):
        """
        move agent
        """
        # Choose action
        best_action, best_state_value = self.choose_action()

        # Check if current agent position was exit port
        if (
            self.pacmanz.board.position_exit_port == self.position_agent
        ).all():
            # Update current cell to exit port
            self.pacmanz.board.update_cell(
                self.position_agent[0],
                self.position_agent[1],
                self.pacmanz.board.s_exit_port,
                self.pacmanz.board.c_exit_port,
            )
        # Check if current agent position was vaccine
        elif (
            self.pacmanz.board.position_vaccine == self.position_agent
        ).all():
            # Update current cell to vaccine
            self.pacmanz.board.update_cell(
                self.position_agent[0],
                self.position_agent[1],
                self.pacmanz.board.s_vaccine,
                self.pacmanz.board.c_vaccine,
            )
        else:
            # Update current cell to empty
            self.pacmanz.board.update_cell(
                self.position_agent[0],
                self.position_agent[1],
                self.pacmanz.board.s_empty,
                self.pacmanz.board.c_empty,
            )

        if best_state_value == None:
            # There is no move so agent lost
            # Update weights and reset game
            self.update_weights_and_reset(is_win=False)
            return self.state_value()

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
                # Generate new vaccine
                self.pacmanz.board.generate_vaccine()
                # Update pygame
                self.pacmanz.board.create_rect(
                    self.pacmanz.board.c_vaccine,
                    self.pacmanz.board.position_vaccine[0],
                    self.pacmanz.board.position_vaccine[1],
                )

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

        # Check if agent must shoot zombie
        # If there is more than one zombie in distance 2
        # we must shoot otherwise we can run away
        if self.zombies_in_distance_2 > 1 and self.pacmanz.shot_left > 0:
            # Check if agent can shoot
            can_shoot, zombie_in_range = self.can_agent_shoot()
            if can_shoot:
                # Shoot all zombies in range except last one
                for i in range(len(zombie_in_range) - 1):
                    # Shoot zombie
                    self.shoot(i)

        # Check if can vaccinate zombie
        self.vaccinate_zombie()

        return best_state_value
