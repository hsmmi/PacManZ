import numpy as np


class board:
    def __init__(self, PacManZ, height, width, n_obstcale, n_shot) -> None:
        self.packmanz = PacManZ
        self.height = height
        self.width = width
        self.board = np.full((height + 2, width + 2), "B")

        self.pit = np.zeros((1, 2))
        self.vaccine = np.zeros((1, 2))
        self.exit_port = np.zeros((1, 2))
        self.n_obstcale = n_obstcale
        self.obstcales = np.zeros((n_obstcale, 2))
        self.n_shot = n_shot
        self.has_vaccine = False
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

    def generate_vaccine(self) -> None:
        x, y = self.random_blank_cell()
        self.board[x, y] = "V"
        self.vaccine = np.array([x, y])

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

        self.generate_vaccine()

        pass

    def man_distance(self, x1, y1, x2, y2) -> float:
        return abs(x1 - x2) + abs(y1 - y2)

    def euc_distance(self, x1, y1, x2, y2) -> float:
        return np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

    def BFS_distance(self, x1, y1, x2, y2) -> float:
        # BFS on the board from (x1, y1) to (x2, y2)
        # valid move: "B", "V", "E" and should not be neighbour of "Z"
        queue = [(x1, y1)]
        visited = set()
        visited.add((x1, y1))
        distance = 0
        while queue:
            distance += 1
            for _ in range(len(queue)):
                x, y = queue.pop(0)
                if x == x2 and y == y2:
                    return distance
                for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                    # new_cell = (x + dx, y + dy)
                    if (
                        self.board[x + dx, y + dy] == "B"
                        or self.board[x + dx, y + dy] == "V"
                        or self.board[x + dx, y + dy] == "E"
                    ):
                        is_safe = True
                        for dx2, dy2 in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                            if self.board[x + dx + dx2, y + dy + dy2] == "Z":
                                is_safe = False
                                break
                        if is_safe and (x + dx, y + dy) not in visited:
                            queue.append((x + dx, y + dy))
                            visited.add((x + dx, y + dy))

        return distance

    def print_board(self) -> None:
        print(self.board)
        pass
