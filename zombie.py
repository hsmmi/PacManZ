import numpy as np


class zombie:
    def __init__(self, pacmanz):
        self.pacmanz = pacmanz
        self.position_zombie = self.pacmanz.board.find_empty_cell()
        self.pre_position_zombie = self.position_zombie
        self.pacmanz.board.board[
            self.position_zombie[0], self.position_zombie[1]
        ] = self.pacmanz.board.s_zombie
        pass

    def can_zombie_go(self, x, y):
        """
        Check if zombie can go to (x, y)
        """
        # Can't go to margin or obstacle or on another zombie or agent
        if (
            self.pacmanz.board.board[x, y] == self.pacmanz.board.s_margin
            or self.pacmanz.board.board[x, y] == self.pacmanz.board.s_obstacle
            or self.pacmanz.board.board[x, y] == self.pacmanz.board.s_zombie
            or self.pacmanz.board.board[x, y] == self.pacmanz.board.s_agent
        ):
            return False

        # # Can't go near agent when agent has vaccine
        # if self.pacmanz.agent_has_vaccine:
        #     position_agent = self.pacmanz.agent.position_agent
        #     for dir in self.pacmanz.dir_8:
        #         x1 = position_agent[0] + dir[0]
        #         y1 = position_agent[1] + dir[1]

        #         if x1 == x and y1 == y:
        #             return False

        # # Can't go where agent can shoot if agent has any shot left
        # if self.pacmanz.shot_left > 0:
        #     for dir in self.pacmanz.dir_4x2:
        #         x1 = self.pacmanz.agent.position_agent[0] + dir[0]
        #         y1 = self.pacmanz.agent.position_agent[1] + dir[1]

        #         if x1 == x and y1 == y:
        #             return False

        return True

    def get_distance(self, x, y):
        """
        Get distance from position zombie to (x,y)
        with BFS algorithm
        """

        if x == self.position_zombie[0] and y == self.position_zombie[1]:
            return 0

        # Create queue
        queue = []
        queue.append([self.position_zombie[0], self.position_zombie[1], 0])

        # Create visited as a set
        visited = set()
        visited.add((self.position_zombie[0], self.position_zombie[1]))

        # BFS
        while len(queue) > 0:
            # Get first element
            x1, y1, dis = queue.pop(0)

            # Add children to queue
            for dir in self.pacmanz.dir_4:
                x2 = x1 + dir[0]
                y2 = y1 + dir[1]

                # Check if (x2, y2) is the target
                if x2 == x and y2 == y:
                    return dis + 1

                if (x2, y2) not in visited and self.can_zombie_go(x2, y2):
                    queue.append([x2, y2, dis + 1])
                    visited.add((x2, y2))

        # no path
        return self.pacmanz.Qotr

    def can_kill_agent(self):
        """
        Check if zombie can kill agent
        """
        # If agent has vaccine then zombie can't kill agent
        if self.pacmanz.agent_has_vaccine:
            return False

        position_agent = self.pacmanz.agent.position_agent

        for dir in self.pacmanz.dir_8:
            x = self.position_zombie[0] + dir[0]
            y = self.position_zombie[1] + dir[1]

            if x == position_agent[0] and y == position_agent[1]:
                return True

        return False

    def state_value(self):
        """
        Calculate state value
        """

        distance_to_pit = self.get_distance(
            self.pacmanz.board.position_pit[0],
            self.pacmanz.board.position_pit[1],
        )
        distance_nearest_obstacle = self.pacmanz.Qotr
        sum_distance_obstacle_pit = distance_to_pit

        # Find nearest obstacle
        for obstacle in self.pacmanz.board.position_obstacle:
            distance = self.get_distance(obstacle[0], obstacle[1])
            if distance < distance_nearest_obstacle:
                distance_nearest_obstacle = distance

            sum_distance_obstacle_pit += distance

        distance_to_agent = self.get_distance(
            self.pacmanz.agent.position_agent[0],
            self.pacmanz.agent.position_agent[1],
        )

        distance_to_all_zombie = 0
        for i in range(self.pacmanz.zombie_left):
            distance_to_all_zombie += self.get_distance(
                self.pacmanz.zombie[i].position_zombie[0],
                self.pacmanz.zombie[i].position_zombie[1],
            )

        # Calculate state value
        values = [
            # 00. Distance to the pit with vaccine
            distance_to_pit if self.pacmanz.agent_has_vaccine else 0,
            # 01. Distance to the pit without vaccine
            distance_to_pit if not self.pacmanz.agent_has_vaccine else 0,
            # 02. Sum distance to all obstcales + distance to pit with vaccine
            sum_distance_obstacle_pit if self.pacmanz.agent_has_vaccine else 0,
            # 03. Sum distance to all obstcales + distance to pit without vaccine
            sum_distance_obstacle_pit
            if not self.pacmanz.agent_has_vaccine
            else 0,
            # 04. Distance to the nearest obstacle with vaccine
            distance_nearest_obstacle if self.pacmanz.agent_has_vaccine else 0,
            # 05. Distance to the nearest obstcale without vaccine
            distance_nearest_obstacle
            if not self.pacmanz.agent_has_vaccine
            else 0,
            # 06. Distance to the agent with vaccine
            distance_to_agent if self.pacmanz.agent_has_vaccine else 0,
            # 07. Distance to the agent without vaccine
            distance_to_agent if not self.pacmanz.agent_has_vaccine else 0,
            # 08. Sum distance to all zombies when agent has vaccine
            distance_to_all_zombie if self.pacmanz.agent_has_vaccine else 0,
            # 09. Sum distance to all zombies when agent has no vaccine
            distance_to_all_zombie
            if not self.pacmanz.agent_has_vaccine
            else 0,
        ]

        return (
            np.sum(
                self.pacmanz.zombie_weights
                * values
                / self.pacmanz.zombie_value_normalizer
            ),
            values / self.pacmanz.zombie_value_normalizer,
        )

    def possible_moves(self):
        """
        Get possible moves of zombie
        """
        possible_moves = []
        for dir in self.pacmanz.dir_4:
            if self.can_zombie_go(
                self.position_zombie[0] + dir[0],
                self.position_zombie[1] + dir[1],
            ):
                possible_moves.append(dir)

        return np.array(possible_moves)

    def regenerate_zombie(self):
        """
        Regenerate zombie
        """
        self.position_zombie = self.pacmanz.board.find_empty_cell()

    def update_weights_and_reset(self, is_win, is_in_pit) -> None:
        """
        Update weights of zombie and reset board or
        regenerate zombie if zombie is in pit
        """
        # Back the zombie to pre position
        self.position_zombie = self.pre_position_zombie
        pre_state_value, pre_values = self.state_value()

        if is_in_pit:
            # Update weights
            self.pacmanz.zombie_weights += (
                self.pacmanz.learning_rate
                * (self.pacmanz.zombie_regenerate_reward - pre_state_value)
                * pre_values
            )

            # Regenerate zombie
            self.regenerate_zombie()
            return

        if is_win:
            # Update weights
            self.pacmanz.zombie_weights += (
                self.pacmanz.learning_rate
                * (self.pacmanz.zombie_win_reward - pre_state_value)
                * pre_values
            )
            # Reset game
            self.pacmanz.reset()

        else:
            # Update weights
            self.pacmanz.zombie_weights += (
                self.pacmanz.learning_rate
                * (self.pacmanz.zombie_lose_reward - pre_state_value)
                * pre_values
            )

        return

    def choose_action(self) -> list[int, int]:
        """
        choose action based on state value of possible actions
        return best action and state value
        """

        possible_moves = self.possible_moves()
        if len(possible_moves) == 0:
            return None, None

        best_action = None
        best_state_value = -np.inf

        for move in possible_moves:
            # Do move
            self.pacmanz.board.board[
                self.position_zombie[0], self.position_zombie[1]
            ] = self.pacmanz.board.s_empty
            self.position_zombie[0] += move[0]
            self.position_zombie[1] += move[1]
            s_cell = self.pacmanz.board.board[
                self.position_zombie[0], self.position_zombie[1]
            ]
            self.pacmanz.board.board[
                self.position_zombie[0], self.position_zombie[1]
            ] = self.pacmanz.board.s_zombie

            # Get state value
            state_value, _ = self.state_value()

            if state_value > best_state_value:
                best_state_value = state_value
                best_action = move

            # Back to original state
            self.pacmanz.board.board[
                self.position_zombie[0], self.position_zombie[1]
            ] = s_cell
            self.position_zombie[0] -= move[0]
            self.position_zombie[1] -= move[1]
            self.pacmanz.board.board[
                self.position_zombie[0], self.position_zombie[1]
            ] = self.pacmanz.board.s_zombie

        return best_action, best_state_value

    def move(self):
        # Choose action (find the best move)
        best_action, best_state_value = self.choose_action()

        # Check if current zombie position was exit port
        if (
            self.pacmanz.board.position_exit_port == self.position_zombie
        ).all():
            # change current cell to exit port
            self.pacmanz.board.update_cell(
                self.position_zombie[0],
                self.position_zombie[1],
                self.pacmanz.board.s_exit_port,
                self.pacmanz.board.c_exit_port,
            )

        # Check if current zombie position was vaccine
        elif (
            self.pacmanz.board.position_vaccine == self.position_zombie
        ).all():
            # change current cell to vaccine
            self.pacmanz.board.update_cell(
                self.position_zombie[0],
                self.position_zombie[1],
                self.pacmanz.board.s_vaccine,
                self.pacmanz.board.c_vaccine,
            )

        else:
            # change current cell to empty
            self.pacmanz.board.update_cell(
                self.position_zombie[0],
                self.position_zombie[1],
                self.pacmanz.board.s_empty,
                self.pacmanz.board.c_empty,
            )

        # Check if there is no move for zombie
        if best_state_value is None:
            # Update weights
            self.update_weights_and_reset(is_win=False, is_in_pit=True)
            # Game reseted so go out
            return None, None

        # Do move
        self.position_zombie[0] += best_action[0]
        self.position_zombie[1] += best_action[1]
        # type of cell that zombie is moving to
        s_cell = self.pacmanz.board.board[
            self.position_zombie[0], self.position_zombie[1]
        ]
        # change current cell to zombie
        self.pacmanz.board.update_cell(
            self.position_zombie[0],
            self.position_zombie[1],
            self.pacmanz.board.s_zombie,
            self.pacmanz.board.c_zombie,
        )

        # Check if zombie is in pit
        if s_cell == self.pacmanz.board.s_pit:
            self.pacmanz.board.update_cell(
                self.position_zombie[0],
                self.position_zombie[1],
                self.pacmanz.board.s_pit,
                self.pacmanz.board.c_pit,
            )
            # Update weights
            self.update_weights_and_reset(is_win=False, is_in_pit=True)
            # Zombie reseted so go out
            return None, None
        
        # Check if can kill agent
        if self.can_kill_agent():
            self.update_weights_and_reset(is_win=True, is_in_pit=False)
            self.pacmanz.agent.update_weights_and_reset(is_win=False)
            # Game reseted so go out
            return None, None
        
        return best_state_value
