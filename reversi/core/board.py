class Board:
    def __init__(self, x=8, y=8):
        self.x = x
        self.y = y
        self.board = [['.' for i in range(y)] for i in range(x)]
        self.directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        self.initial_stones()


    def initial_stones(self):
        mid_x, mid_y = self.x // 2, self.y // 2
        self.board[mid_x - 1][mid_y - 1] = 'W'
        self.board[mid_x][mid_y] = 'W'
        self.board[mid_x - 1][mid_y] = 'B'
        self.board[mid_x][mid_y - 1] = 'B'

    def print_board(self):
        for row in self.board:
            print(" ".join(row))
        print()

    def get_moves(self, player):
        opp = 'B' if player == 'W' else 'W'
        valid_moves = []

        for row in range(self.x):
            for col in range(self.y):
                if self.board[row][col] == '.':
                    for direction in self.directions:
                        if self.valid_dir(row, col, direction[0], direction[1], player, opp):
                            valid_moves.append((row, col))
                            break
        return valid_moves

    def valid_dir(self, x, y, move_row, move_col, player, opp):
        x = x + move_row
        y = y + move_col
        found_opp = False

        while x >= 0 and x < self.x and y >= 0 and y < self.y:
            if self.board[x][y] == opp:
                found_opp = True
            elif self.board[x][y] == player:
                return found_opp
            else:
                return False
            x = x + move_row
            y = y + move_col

        return False

    def play_move(self, row, col, player):
        if (row, col) not in self.get_moves(player):
            return False

        opp = 'B' if player == 'W' else 'W'
        flipped_any = False

        for direction in self.directions:
            if self.flip_stones(row, col, direction[0], direction[1], player, opp):
                flipped_any = True

        if flipped_any:
            self.board[row][col] = player

        return flipped_any

    def flip_stones(self, row, col, dx, dy, player, opp):
        x, y = row + dx, col + dy
        pieces_to_flip = []

        while 0 <= x < self.x and 0 <= y < self.y and self.board[x][y] == opp:
            pieces_to_flip.append((x, y))
            x += dx
            y += dy

        if 0 <= x < self.x and 0 <= y < self.y and self.board[x][y] == player:
            for flip_x, flip_y in pieces_to_flip:
                self.board[flip_x][flip_y] = player
            return True

        return False

    def get_b_stones(self):
        return sum(row.count('B') for row in self.board)

    def get_w_stones(self):
        return sum(row.count('W') for row in self.board)
