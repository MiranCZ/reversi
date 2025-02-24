# distuils: language = c++
import math
import time
from libc.stdlib cimport rand
import random


cdef class Node:
    constant = math.sqrt(2)

    cdef unsigned long long white, black;
    cdef bint is_white, is_terminal;
    cdef float score;
    cdef int visited;
    cdef Node parent;
    cdef list children;

    def __init__(self, unsigned long long white, unsigned long long black, bint is_white, parent=None):
        self.white = white
        self.black = black
        self.is_white = is_white
        self.parent = parent
        self.children = []
        self.score = 0
        self.visited = 0
        self.is_terminal = False

    def calculate_value(self):
        assert self.parent is not None

        if self.visited == 0:
            return pos_infinity

        return self.score / self.visited + self.constant * math.sqrt(math.log(self.parent.visited) / self.visited)

    def add_child(self, child, move):
        self.children.append(child)

cdef class RootNode(Node):

    cdef dict[Node, int] move_map;

    def __init__(self, unsigned long long white, unsigned long long black, bint is_white, parent=None):
        super().__init__(white, black, is_white, parent)
        self.move_map = {}

    def add_child(self, child, move):
        super().add_child(child, move)

        self.move_map[child] = move

cdef float add_moves(Node node):
    cdef unsigned long long white = node.white
    cdef unsigned long long black = node.black
    cdef bint is_white = not node.is_white

    cdef unsigned long long moves = get_moves(white, black, is_white)
    cdef unsigned long long filled_board = 0xFFFFFFFFFFFFFFFFULL;

    # no moves, add single child representing move skip
    if moves == 0:
        child: Node = Node(node.white, node.black, is_white, node)
        node.add_child(child, None)

        # this means two node skips aka game end
        # FIXME still not entirely sure the logic here is correct
        if node.parent is not None and node.parent.white == node.white and node.parent.black == node.black:
            child.is_terminal = True
            child.visited = 1
            child.score = get_game_outcome(black, white)

            return get_game_outcome(black, white)

        return neg_infinity

    cdef unsigned long long n_white, n_black, captured, lsb;
    cdef int i;

    while moves != 0:
        lsb = moves & -moves
        moves &= moves - 1

        i = lsb.bit_length() - 1
        captured = get_captured(white, black, is_white, i)

        n_white = white ^ captured
        n_black = black ^ captured

        if is_white:
            n_white |= 1ULL << i
        else:
            n_black |= 1ULL << i

        child: Node = Node(n_white, n_black, is_white, parent=node)
        node.add_child(child, i)

        # hopefully this does not break anything
        if (n_white | n_black) == filled_board:
            child.is_terminal = True
            child.visited = 1
            child.score = get_game_outcome(n_black, n_white)

            return get_game_outcome(n_black, n_white)

    return neg_infinity

cdef Node select_leaf(Node node):
    cdef Node best_child;
    cdef float best_value;
    cdef float value;

    while len(node.children) > 0:
        best_child = None
        best_value = neg_infinity

        for child in node.children:
            value = child.calculate_value()
            if value > best_value:
                best_value = value
                best_child = child

        node = best_child

    return node

cdef int bit_count(unsigned long long n) nogil:
    """
    via https://en.wikipedia.org/wiki/Hamming_weight#Efficient_implementation
    """
    n -= (n >> 1) & 0x5555555555555555ULL  # put count of each 2 bits into those 2 bits
    n = (n & 0x3333333333333333ULL) + ((n >> 2) & 0x3333333333333333ULL)  # put count of each 4 bits into those 4 bits
    n = (n + (n >> 4)) & 0x0f0f0f0f0f0f0f0fULL  #put count of each 8 bits into those 8 bits
    n += n >> 8  # put count of each 16 bits into their lowest 8 bits
    n += n >> 16  # put count of each 32 bits into their lowest 8 bits
    n += n >> 32  # put count of each 64 bits into their lowest 8 bits
    return <int>(n & 0x7fULL)


cdef float simulate(Node node) nogil:
    cdef unsigned long long captured, moves, lsb;
    cdef int k, i;

    cdef unsigned long long white = node.white
    cdef unsigned long long black = node.black
    cdef bint is_white = not node.is_white
    cdef unsigned long long filled_board = 0xFFFFFFFFFFFFFFFFULL;


    while True:
        # game ended
        if (white | black) == filled_board:
            return get_game_outcome(black, white)

        moves = get_moves(white, black, is_white)
        if moves == 0:
            is_white = not is_white
            moves = get_moves(white, black, is_white)

            # neither side can make a move, return result
            if moves == 0:
                return get_game_outcome(black, white)

        # selects a random move from the available ones, uses some bitwise operator magic to speed stuff up
        k = (rand() % (bit_count(moves)))
        # k = random.randrange(bitcount(moves))
        # k = random.randrange(moves.bit_count())

        for i in range(k):
            # Remove the lowest set bit
            moves &= moves - 1

        lsb = moves & -moves
        # move = lsb.bit_length() - 1

        captured = get_captured_shifted(white, black, is_white, lsb)

        white ^= captured
        black ^= captured

        if is_white:
            white |= lsb
        else:
            black |= lsb

        is_white = not is_white

cdef float get_game_outcome(unsigned long long black,unsigned long long white) nogil:
    cdef int final_value = bit_count(white) - bit_count(black)
    # cdef int final_value = white.bit_count() - black.bit_count()

    if final_value > 0:
        return 1
    elif final_value < 0:
        return -1
    else:
        return 0.5

cdef void back_propagate(Node node, float score):
    cdef bint is_tie = (score == 0.5)
    cdef bint winner_color = True if score > 0 else False

    while node is not None:
        node.visited += 1
        if is_tie:
            node.score += score
            node = node.parent
            continue

        if node.is_white == winner_color:
            node.score += 1
        node = node.parent

def best_move(unsigned long long white, unsigned long long black, bint is_white):
    cdef float score;
    cdef RootNode root = RootNode(white, black, not is_white)
    cdef Node selected, node, child;

    result = add_moves(root)
    if result != neg_infinity:
        print("Only one move available!")
        return root.move_map.get(root.children[0])

    # monte carlo tree search loop
    cdef double t = time.time()
    iters = 0

    while time.time() - t < 1:
        for i in range(200):
            iters += 1
            selected = select_leaf(root)
            if selected.is_terminal:
                selected.visited += 1

                back_propagate(selected.parent, selected.score)

                continue

            result = add_moves(selected)

            # not -inf return means the child node is terminal, therefore we should just back-propagate
            if result != neg_infinity:
                # FIXME this is total spaghetti
                back_propagate(selected, result)
                continue

            # selected = selected.children[rand() % len(selected.children)]
            selected = random.choice(selected.children)

            score = simulate(selected)
            back_propagate(selected, score)

    # iterations finished, select the most visited node
    best_node: Node | None = None
    most_visited = 0

    print("Nodes: ")
    for node in root.children:
        score = node.visited
        print(root.move_map.get(node),  (node.score / node.visited) * 100, node.score, node.visited)

        if score > most_visited or best_node is None:
            best_node = node
            most_visited = score

    print()
    move = root.move_map.get(best_node)

    if move is None:
        print("NO MOVE")
        return -1
    else:
        print("Selected:", move, best_node.is_white, best_node.score, best_node.visited,
              (best_node.score / best_node.visited) * 100, " iterations: ", iters)
    return move

cdef unsigned long long __masks[8];
__masks[:] = [0x7F7F7F7F7F7F7F7FULL,
              0x007F7F7F7F7F7F7FULL,
              0xFFFFFFFFFFFFFFFFULL,
              0x00FEFEFEFEFEFEFEULL,
              0xFEFEFEFEFEFEFEFEULL,
              0xFEFEFEFEFEFEFE00ULL,
              0xFFFFFFFFFFFFFFFFULL,
              0x7F7F7F7F7F7F7F00ULL]

cdef unsigned long long __lshifts[8];
__lshifts[:] = [0, 0, 0, 0, 1, 9, 8, 7]

cdef unsigned long long  __rshifts[8];
__rshifts[:] = [1, 9, 8, 7, 0, 0, 0, 0]

cdef float pos_infinity = float('inf')
cdef float neg_infinity = float('-inf')

cdef unsigned long long shift(unsigned long long disks, int dir) nogil:
    """
    via: https://www.hanshq.net/othello.html#bitboards
    """
    if dir < 4:
        return (disks >> __rshifts[dir]) & __masks[dir]
    else:
        return (disks << __lshifts[dir]) & __masks[dir]

cdef unsigned long long get_moves(unsigned long long white, unsigned long long black, bint is_white) nogil:
    if is_white:
        return __get_moves(white, black)
    else:
        return __get_moves(black, white)

cdef unsigned long long __get_moves(unsigned long long player, unsigned long long opponent) nogil:
    """
    via: https://www.hanshq.net/othello.html#moves
    """
    cdef unsigned long long empty_cells, legal_moves, x;

    empty_cells = ~(player | opponent)
    legal_moves = 0

    cdef int dir;
    for dir in range(8):
        x = shift(player, dir) & opponent

        x |= shift(x, dir) & opponent
        x |= shift(x, dir) & opponent
        x |= shift(x, dir) & opponent
        x |= shift(x, dir) & opponent
        x |= shift(x, dir) & opponent

        legal_moves |= shift(x, dir) & empty_cells

    return legal_moves

cdef unsigned long long get_captured(unsigned long long white, unsigned long long black, bint is_white, int move) nogil:
    return get_captured_shifted(white, black, is_white, 1ULL << move)


cdef long long get_captured_shifted(unsigned long long white, unsigned long long black, bint is_white, unsigned long long move_shifted) nogil:
    if is_white:
        return __get_captured(white, black, move_shifted)
    else:
        return __get_captured(black, white, move_shifted)

cdef unsigned long long __get_captured(unsigned long long player, unsigned long long opponent, unsigned long long move) nogil:
    """
    via: https://www.hanshq.net/othello.html#moves
    """
    cdef unsigned long long captured, closing_disk, x;

    player |= move
    captured = 0

    cdef int dir;
    for dir in range(8):
        x = shift(move, dir) & opponent

        x |= shift(x, dir) & opponent
        x |= shift(x, dir) & opponent
        x |= shift(x, dir) & opponent
        x |= shift(x, dir) & opponent
        x |= shift(x, dir) & opponent

        closing_disk = shift(x, dir) & player
        captured |= (x if closing_disk != 0 else 0)

    return captured
