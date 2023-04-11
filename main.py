import board
import numpy as np

game = board.PacManZ(10, 10, 4, 10, 3)
game.generate_board()
game.print_board()
game.agent_state_value()
while True:
    move, state_value = game.choose_agent_action()
    game.board[game.pos_agent[0], game.pos_agent[1]] = "B"
    game.pos_agent[0] += move[0]
    game.pos_agent[1] += move[1]
    game.board[game.pos_agent[0], game.pos_agent[1]] = "A"
    game.print_board()
    print(state_value)
    # wait for key
    input()
