import time
import numpy as np
from agent import agent
from board import board
from zombie import zombie


class pacmanz:
    def __init__(
        self, board_height, board_width, n_zombie, n_obstcale, n_shot
    ):
        self.dir_4 = np.array([[0, 1], [1, 0], [0, -1], [-1, 0]])
        self.dir_4x2 = np.array([[0, 2], [2, 0], [0, -2], [-2, 0]])
        self.dir_8 = np.array(
            [
                [0, 1],
                [1, 1],
                [1, 0],
                [1, -1],
                [0, -1],
                [-1, -1],
                [-1, 0],
                [-1, 1],
            ]
        )
        self.n_shot = n_shot
        self.shot_left = n_shot
        self.n_zombie = n_zombie
        self.zombie_left = n_zombie
        self.agent_has_vaccine = False

        self.score = 0
        self.agent_win_reward = 1000
        self.agent_lose_reward = -1000
        self.zombie_win_reward = 1000
        self.zombie_lose_reward = -1000
        self.zombie_regenerate_reward = -100

        self.vaccinate_score = 100
        self.learning_rate = 1e-2
        self.n_iteration = 0
        self.max_iteration = board_height * board_width / 2
        self.n_game = 0
        self.delay = 200
        self.board = board(board_height, board_width, n_obstcale)
        self.agent = agent(self)
        self.zombie = []
        for _ in range(self.n_zombie):
            self.zombie.append(zombie(self))

        # Print board in start
        self.board.update_whole_board()

        self.create_agent_feature()
        self.create_zombie_feature()

        pass

    def create_agent_feature(self):
        """
        00. Distance to the nearest zombie in mid range with vaccine
        01. Distance to the nearest zombie in mid range without vaccine
        02. Sum of distance to all zombies in mid range with vaccine
        03. Sum of distance to all zombies in mid range without vaccine
        04. Distance to the nearest obstcale in mid range without vaccine
        05. sum of distance to all obstcales in mid range without vaccine + pit
        06. Distance to the pit in mid range with vaccine
        07. Distance to the pit in mid range without vaccine
        08. number of shot left with vaccine
        09. number of shot left without vaccine
        10. number of zombies in close range with vaccine
        11. number of zombies in close range without vaccine
        12. number of shots left
        13. can agent shoot with vaccine
        14. can agent shoot without vaccine
        15. Distance to vaccine without vaccine
        16. Distance to exit port when no zombie left
        17. Number of possible move with vaccine
        18. Number of possible move without vaccine
        19. Euclidean distance to the nearest zombie with vaccine
        20. Euclidean distance to the nearest zombie without vaccine
        21. Distance to the nearest zombie in close range with vaccine
        22. Distance to the nearest zombie in close range without vaccine
        """
        self.agent_weights = np.random.rand(23)

        # 13. can agent shoot with vaccine
        self.agent_weights[13] = 10
        # 14. can agent shoot without vaccine
        self.agent_weights[14] = 20

        # 16. Distance to exit port when no zombie left
        self.agent_weights[16] = -100

        # 06. Distance to the pit in mid range with vaccine
        self.agent_weights[6] = 30
        # 07. Distance to the pit in mid range without vaccine
        self.agent_weights[7] = 30

        # 15. Distance to vaccine without vaccine
        self.agent_weights[15] = -300
        # 00. Distance to the nearest zombie in mid range with vaccine
        self.agent_weights[0] = -30
        # 01. Distance to the nearest zombie in mid range without vaccine
        self.agent_weights[1] = 12
        # 03. Sum of distance to all zombies in mid range without vaccine
        self.agent_weights[3] = 8
        # 18. Number of possible move without vaccine
        self.agent_weights[18] = 40  # Go where there is more moves
        # 19. Euclidean distance to the nearest zombie with vaccine
        self.agent_weights[19] = -800
        # 20. Euclidean distance to the nearest zombie without vaccine
        self.agent_weights[20] = 20
        # 21. Distance to the nearest zombie in close range with vaccine
        self.agent_weights[21] = -20
        # 22. Distance to the nearest zombie in close range without vaccine
        self.agent_weights[22] = 70

        self.agent_weights
        self.Qotr = self.board.board_height + self.board.board_width
        self.agent_value_normalizer = np.array(
            [
                # 00. Distance to the nearest zombie in mid range with vaccine
                self.agent.mid_range,
                # 01. Distance to the nearest zombie in mid range without vaccine
                self.agent.mid_range,
                # 02. Sum of distance to all zombies in mid range with vaccine
                self.agent.mid_range * self.n_zombie,
                # 03. Sum of distance to all zombies in mid range without vaccine
                self.agent.mid_range * self.n_zombie,
                # 04. Distance to the nearest obstcale in mid range without vaccine
                self.agent.mid_range,
                # 05. sum of distance to all obstcales in mid range without vaccine + pit
                self.agent.mid_range * self.board.n_obstcale,
                # 06. Distance to the pit in mid range with vaccine
                self.agent.mid_range,
                # 07. Distance to the pit in mid range without vaccine
                self.agent.mid_range,
                # 08. number of shot left with vaccine
                self.shot_left,
                # 09. number of shot left without vaccine
                self.shot_left,
                # 10. number of zombies in close range with vaccine
                self.n_zombie,
                # 11. number of zombies in close range without vaccine
                self.n_zombie,
                # 12. number of shots left
                self.shot_left,
                # 13. can agent shoot with vaccine
                self.n_shot,
                # 14. can agent shoot without vaccine
                self.n_shot,
                # 15. Distance to vaccine without vaccine
                self.Qotr,
                # 16. Distance to exit port when no zombie left
                self.Qotr,
                # 17. Number of possible move with vaccine
                4,
                # 18. Number of possible move without vaccine
                4,
                # 19. Euclidean distance to the nearest zombie with vaccine
                self.Qotr,
                # 20. Euclidean distance to the nearest zombie without vaccine
                self.Qotr,
                # 21. Distance to the nearest zombie in close range with vaccine
                self.agent.close_range,
                # 22. Distance to the nearest zombie in close range without vaccine
                self.agent.close_range,
            ]
        )

    def create_zombie_feature(self):
        """
        00. Distance to the pit with vaccine
        01. Distance to the pit without vaccine
        02. Sum distance to all obstcales + distance to pit with vaccine
        03. Sum distance to all obstcales + distance to pit without vaccine
        04. Distance to the nearest obstcale with vaccine
        05. Distance to the nearest obstcale without vaccine
        06. Distance to the agent with vaccine
        07. Distance to the agent without vaccine
        08. Sum distance to all zombies when agent has vaccine
        09. Sum distance to all zombies when agent has no vaccine
        """
        self.zombie_weights = np.random.rand(10)

        # 07. Distance to the agent without vaccine
        self.zombie_weights[7] = -1000
        # 06. Distance to the agent with vaccine
        self.zombie_weights[6] = 1000

        self.zombie_value_normalizer = np.array(
            [
                # 00. Distance to the pit with vaccine
                self.Qotr,
                # 01. Distance to the pit without vaccine
                self.Qotr,
                # 02. Sum distance to all obstcales + distance to pit with vaccine
                self.Qotr * (self.board.n_obstcale + 1),
                # 03. Sum distance to all obstcales + distance to pit without vaccine
                self.Qotr * (self.board.n_obstcale + 1),
                # 04. Distance to the nearest obstcale with vaccine
                self.Qotr,
                # 05. Distance to the nearest obstcale without vaccine
                self.Qotr,
                # 06. Distance to the agent without vaccine
                self.Qotr,
                # 07. Distance to the agent with vaccine
                self.Qotr,
                # 08. Sum distance to all zombies when agent has vaccine
                self.Qotr * (self.n_zombie - 1),
                # 09. Sum distance to all zombies when agent has no vaccine
                self.Qotr * (self.n_zombie - 1),
            ]
        )

    def reset(self):
        # Reset pacmanz
        self.n_iteration = 0
        self.score = 0
        self.agent_has_vaccine = False
        self.shot_left = self.n_shot

        # Reset board
        self.board.create_board()

        # Reset agent
        self.agent = agent(self)

        # Reset zombie
        self.zombie = []
        self.zombie_left = self.n_zombie
        for _ in range(self.n_zombie):
            self.zombie.append(zombie(self))

        self.board.update_whole_board()

        pass

    def vaccinate_zombie(self, position):
        for i in range(self.n_zombie):
            if (self.zombie[i].position_zombie == position).all():
                self.zombie[i] = self.zombie[-1]
                self.zombie_left -= 1
                self.zombie.pop()
                break
        self.agent_has_vaccine = False
        self.score += self.vaccinate_score
        pass

    def play(self):
        # self.load_weights()
        # Reset game
        self.reset()

        self.pre_agent_score = 0
        self.pre_pre_agent_score = 0

        # Play gamex
        while True:
            self.n_iteration += 1
            if self.n_iteration == 1:
                self.n_game += 1
            # Move Zombie
            for i in range(self.zombie_left):
                zombie_score = self.zombie[i].move()
                if self.board.show_time:
                    # wait self.delay ms
                    time.sleep(self.delay * 1e-3)
                    print(f"Value Zombie {i}: ", zombie_score)

            for i in range(4):
                agent_score = self.agent.move()
                if self.board.show_time:
                    # wait self.delay ms
                    time.sleep(self.delay * 3 * 1e-3)
                    print("Value Agent: ", agent_score)
            # if self.n_iteration > self.max_iteration:
            if agent_score == self.pre_pre_agent_score:
                print("Game Over With Loop")
                # update agent
                self.agent.update_weights_and_reset(is_win=False)
                # Store weights
                self.save_weights()
            else:
                self.pre_pre_agent_score = self.pre_agent_score
                self.pre_agent_score = agent_score

        pass

    def save_weights(self):
        """
        Save zombie weights in zombie.csv and agent weights in agent.csv
        """
        np.savetxt("weights/zombie.csv", self.zombie_weights, delimiter=",")
        np.savetxt("weights/agent.csv", self.agent_weights, delimiter=",")
        pass

    def load_weights(self):
        """
        Load zombie weights from zombie.csv and agent weights from agent.csv
        """
        self.zombie_weights = np.loadtxt("weights/zombie.csv", delimiter=",")
        self.agent_weights = np.loadtxt("weights/agent.csv", delimiter=",")
        pass


game = pacmanz(10, 15, 4, 10, 3)
game.play()
