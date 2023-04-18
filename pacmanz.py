import time
import numpy as np
from agent import agent
from board import board
from zombie import zombie


class pacmanz:
    def __init__(
        self, board_height, board_width, n_zombie, n_obstcale, n_shot
    ):
        self.D = np.array([[0, 1], [1, 0], [0, -1], [-1, 0]])
        self.n_shot = n_shot
        self.shot_left = n_shot
        self.n_zombie = n_zombie
        self.zombie_left = n_zombie
        self.agent_has_vaccine = False
        self.win_reward = 1000
        self.lose_reward = -1000
        self.score = 0
        self.vaccinate_score = 100
        self.learning_rate = 1e-2
        self.n_iteration = 0
        self.max_iteration = board_height * board_width * 2
        self.n_game = 0

        self.board = board(board_height, board_width, n_obstcale)
        self.agent = agent(self)
        self.zombie = []
        for _ in range(self.n_zombie):
            self.zombie.append(zombie(self))

        # Print board in start
        self.board.update_whole_board()

        self.create_agent_feature()

        pass

    def create_agent_feature(self):
        """
        00. Distance to the nearest zombie with vaccine
        01. Distance to the nearest zombie without vaccine
        02. Sum of distance to all zombies with vaccine
        03. Sum of distance to all zombies without vaccine
        04. Distance to the nearest obstcale with vaccine
        05. Distance to the nearest obstcale without vaccine
        06. sum of distance to all obstcales with vaccine
        07. sum of distance to all obstcales without vaccine
        08. Distance to the exit port with vaccine
        09. Distance to the exit port without vaccine
        10. Distance to the pit with vaccine
        11. Distance to the pit without vaccine
        12. number of shot left with vaccine
        13. number of shot left without vaccine
        14. number of zombies in distance 2 with vaccine
        15. number of zombies in distance 2 without vaccine
        16. agent has vaccine
        17. agent has no vaccine
        18. number of zombies left
        19. number of shots left
        20. can agent shoot with vaccine
        21. can agent shoot without vaccine
        22. Distance to vaccine with vaccine
        23. Distance to vaccine without vaccine
        24. Distance to exit port when no zombie left
        """
        self.agent_weights = np.random.rand(25)

        # 24. Distance to exit port when no zombie left
        self.agent_weights[24] = -1000

        # 10. Distance to the pit with vaccine
        self.agent_weights[10] = 500
        # 11. Distance to the pit without vaccine
        self.agent_weights[11] = 500

        # 23. Distance to vaccine without vaccine
        self.agent_weights[23] = -1000
        # 00. Distance to the nearest zombie with vaccine
        self.agent_weights[0] = -1000

        self.agent_weights
        self.Qotr = self.board.board_height + self.board.board_width
        self.agent_value_normalizer = np.array(
            [
                # 00. Distance to the nearest zombie with vaccine
                self.Qotr,
                # 01. Distance to the nearest zombie without vaccine
                self.Qotr,
                # 02. Sum of distance to all zombies with vaccine
                self.Qotr * self.n_zombie,
                # 03. Sum of distance to all zombies without vaccine
                self.Qotr * self.n_zombie,
                # 04. Distance to the nearest obstcale with vaccine
                self.Qotr,
                # 05. Distance to the nearest obstcale without vaccine
                self.Qotr,
                # 06. sum of distance to all obstcales with vaccine
                self.Qotr * self.board.n_obstcale,
                # 07. sum of distance to all obstcales without vaccine
                self.Qotr * self.board.n_obstcale,
                # 08. Distance to the exit port with vaccine
                self.Qotr,
                # 09. Distance to the exit port without vaccine
                self.Qotr,
                # 10. Distance to the pit with vaccine
                self.Qotr,
                # 11. Distance to the pit without vaccine
                self.Qotr,
                # 12. number of shot left with vaccine
                self.shot_left,
                # 13. number of shot left without vaccine
                self.shot_left,
                # 14. number of zombies in distance 2 with vaccine
                self.n_zombie,
                # 15. number of zombies in distance 2 without vaccine
                self.n_zombie,
                # 16. agent has vaccine
                1,
                # 17. agent has no vaccine
                1,
                # 18. number of zombies left
                self.n_zombie,
                # 19. number of shots left
                self.shot_left,
                # 20. can agent shoot with vaccine
                1,
                # 21. can agent shoot without vaccine
                1,
                # 22. Distance to vaccine with vaccine
                self.Qotr,
                # 23. Distance to vaccine without vaccine
                self.Qotr,
                # 24. Distance to exit port when no zombie left
                self.Qotr,
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
        # Reset game
        self.reset()

        # Play game
        while True:
            # wait 10ms
            time.sleep(0.01)



            self.n_iteration += 1
            # Move agent
            # self.agent.move()
            print(self.agent.move())

            if self.n_iteration > self.max_iteration:
                print("Game Over")
                # update agent
                self.agent.update_weights_and_reset(is_win=False)
                self.n_game += 1

        pass


game = pacmanz(10, 10, 4, 10, 3)
game.play()
