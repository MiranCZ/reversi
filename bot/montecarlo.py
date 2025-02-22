import util
import math
import random
import time

random.seed(0)


class Node:
    constant = math.sqrt(2)

    def __init__(self, white, black, is_white, parent=None):
        self.white = white
        self.black = black
        self.is_white = is_white
        self.parent = parent
        self.children = []
        self.score = 0
        self.visited = 0
        self.is_terminal = False

    def calculate_value(self):
        if self.parent is None:
            return
        if self.visited == 0:
            return util.pos_infinity

        return self.score / self.visited + self.constant * math.sqrt(math.log(self.parent.visited) / self.visited)

    def add_child(self, child, move):
        self.children.append(child)


class RootNode(Node):
    def __init__(self, white, black, is_white, parent=None):
        super().__init__(white, black, is_white, parent)
        self.move_map = {}

    def add_child(self, child, move):
        super().add_child(child, move)

        self.move_map[child] = move


def add_moves(node: Node):
    white = node.white
    black = node.black
    is_white = not node.is_white

    moves = util.get_moves(white, black, is_white)

    # no moves, add single child representing move skip
    if moves == 0:
        child: Node = Node(node.white, node.black, is_white, node)
        node.add_child(child, None)

        # this means two node skips aka game end
        # FIXME still not entirely sure the logic here is correct
        if node.parent is not None and node.parent.white == node.white and node.parent.black == node.black:
            child.is_terminal = True
            child.visited = 1
            child.parent.visited += 1

            return get_game_outcome(black, white)
        return

    while moves != 0:
        lsb = moves & -moves
        moves &= moves - 1

        i = lsb.bit_length() - 1
        captured = util.get_captured(white, black, is_white, i)

        n_white = white ^ captured
        n_black = black ^ captured

        if is_white:
            n_white |= 1 << i
        else:
            n_black |= 1 << i

        child: Node = Node(n_white, n_black, is_white, parent=node)
        node.add_child(child, i)

        # hopefully this does not break anything
        if (n_white | n_black) == util.filled_board:
            child.is_terminal = True
            child.visited = 1
            child.parent.visited += 1

            return get_game_outcome(n_black, n_white)

    return


def select_leaf(node: Node):
    while len(node.children) > 0:
        best_child = None
        best_value = util.neg_infinity

        for child in node.children:
            value = child.calculate_value()
            if value > best_value:
                best_value = value
                best_child = child

        node = best_child

    return node


def simulate(node):
    white = node.white
    black = node.black
    is_white = node.is_white

    while True:
        # game ended
        if (white | black) == util.filled_board:
            return get_game_outcome(black, white)

        moves = util.get_moves(white, black, is_white)
        if moves == 0:
            is_white = not is_white
            moves = util.get_moves(white, black, is_white)

            # neither side can make a move, return result
            if moves == 0:
                return get_game_outcome(black, white)


        # selects a random move from the available ones, uses some bitwise operator magic to speed stuff up
        k = random.randrange(moves.bit_count())

        for _ in range(k):
            # Remove the lowest set bit
            moves &= moves - 1

        lsb = moves & -moves
        # move = lsb.bit_length() - 1

        captured = util.get_captured_shifted(white, black, is_white, lsb)

        white ^= captured
        black ^= captured

        if is_white:
            white |= lsb
        else:
            black |= lsb

        is_white = not is_white


def get_game_outcome(black, white):
    final_value = white.bit_count() - black.bit_count()
    if final_value > 0:
        return 1
    elif final_value < 0:
        return -1
    else:
        return 0.5


def back_propagate(node: Node, score):
    is_tie = (score == 0.5)

    winner_color = True if score > 0 else False


    while node is not None:
        node.visited += 1
        if is_tie:
            node.score += score
            node = node.parent
            continue

        if node.is_white == winner_color:
            node.score += 1
        node = node.parent


def best_move(white: int, black: int, is_white):
    root: RootNode = RootNode(white, black, not is_white)

    add_moves(root)

    # monte carlo tree search loop
    t = time.time()
    iters = 0
    while time.time() - t < 1 and iters < 50_000:
        for i in range(20):
            iters += 1
            selected = select_leaf(root)
            if selected.is_terminal:
                selected.visited += 1

                # TODO refactor this a bit
                score = selected.score

                if not selected.is_white and score == 1:
                    score = -1
                back_propagate(selected.parent, score)

                continue

            result = add_moves(selected)

            # non-None return means the child node is terminal, therefore we should just back-propagate
            if result is not None:
                # FIXME this is total spaghetti
                back_propagate(selected.children[0], result)
                continue

            selected = random.choice(selected.children)

            score = simulate(selected)
            back_propagate(selected, score)

    # iterations finished, select the most visited node
    best_node: Node | None = None
    most_visited = 0

    for node in root.children:
        score = node.visited

        if score > most_visited or best_node is None:
            best_node = node
            most_visited = score

    move = root.move_map.get(best_node)

    if move is None:
        return -1
    else:
        print("Selected:", move, best_node.is_white, best_node.score, best_node.visited,
              (best_node.score / best_node.visited) * 100, " iterations: ",iters)
    return move
