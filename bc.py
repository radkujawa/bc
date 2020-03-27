import copy
import math
import random
import sys
import threading
from queue import Queue

from asciimatics.screen import Screen

YEARS = 29
BOARD_HEIGHT = 60
BOARD_WIDTH = 128
CAKE_HEIGHT = 10
PLATE_R = 14
CAKE_R = int(PLATE_R * 8 / 10)


def get_board_str(board):
    ret = []
    for i in board:
        s = ""
        for j in board[i]:
            s += board[i][j]
        ret.append(s)

    return ret


def set_on_board(fun, char, board):
    on_board = set()
    for i in board:
        for j in board[i]:
            if fun(i, j):
                board[i][j] = char
                on_board.add((i, j))
    return on_board


def ellipse_disk(x, y, x0, y0, A, B, r):
    return (x - x0) ** 2 / A + (y - y0) ** 2 / B < r ** 2


def ellipse(x, y, x0, y0, A, B, r):
    return math.fabs((x - x0) ** 2 / A + (y - y0) ** 2 / B - r ** 2) < 3


def plat(x, y):
    return ellipse_disk(x, y, 0, 0, 1, 20, PLATE_R)


def set_plat(board):
    set_on_board(plat, "#", board)


def cake_layer(x, y, h):
    return ellipse_disk(x, y, -h, 0, 1, 20, CAKE_R)


def set_cake(board):
    for h in range(CAKE_HEIGHT):
        set_on_board(lambda x, y: cake_layer(x, y, h), ":", board)


def _coating(x, y, r):
    return ellipse_disk(x, y, -CAKE_HEIGHT, 0, 1, 20, r)


def coating(x, y):
    return _coating(x, y, CAKE_R)


def middle_coating(x, y):
    return _coating(x, y, CAKE_R - 1)


def down_len():
    n = 0
    while n < 6:
        if random.randint(0, 1):
            break
        n += 1
    return n


def set_coating(board):
    coating_fields = set_on_board(coating, "@", board)
    for x, y in coating_fields:
        for i in range(down_len()):
            board[x + i][y] = "@"


def middle(x, y):
    return ellipse(x, y, -CAKE_HEIGHT / 2, 0, 1, 20, CAKE_R) if x > -CAKE_HEIGHT / 2 else False


def set_middle(board):
    set_on_board(middle, "%", board)


def set_candle(board, x, y, fire, without_candles):
    for i in range(3):
        board[x - 2 * i][y] = "`"
        board[x - 2 * i - 1][y] = " "

    for i in range(6):
        if i % 2:
            left = "|"
            right = "\\"
        else:
            left = "\\"
            right = "|"
        board[x - i][y - 1] = left
        board[x - i][y + 1] = right

    board[x - 5][y] = "~"
    board[x - 6][y - 1] = "'"
    board[x - 6][y + 1] = "'"
    board[x - 6][y] = "|"

    if fire:
        board[x - 7][y - 1] = "("
        board[x - 7][y + 1] = ")"
        board[x - 7][y] = "o"
        board[x - 8][y] = "("
        board[x - 9][y] = ")"
    else:
        board[x - 7][y - 1] = without_candles[x - 7][y - 1]
        board[x - 7][y + 1] = without_candles[x - 7][y + 1]
        board[x - 7][y] = without_candles[x - 7][y]
        board[x - 8][y] = without_candles[x - 8][y]
        board[x - 9][y] = without_candles[x - 9][y]


class CakeTooSmall(Exception):
    pass


def set_candles(years, board):
    candles = set()

    num_tries = 1000

    while len(candles) < years and num_tries:
        num_tries -= 1

        candles = set()
        candidates = set()

        for i in board:
            for j in board[i]:
                if middle_coating(i, j):
                    candidates.add((i, j))

        while len(candidates) > 0 and len(candles) < years:

            x, y = random.choice(list(candidates))
            candidates.remove((x, y))

            fits = True
            for candle_x, candle_y, _ in candles:
                if math.fabs(candle_y - y) < 4 and math.fabs(candle_x - x) < 12:
                    fits = False
                    break

            if not fits:
                continue

            candles.add((x, y, True))

    if len(candles) == years:
        for x, y, fire in candles:
            assert fire
            set_candle(board, x, y, fire, None)
        return candles
    else:
        raise CakeTooSmall(f"not enough place to set {years} candles!")


def move_candles(candles, board):
    n = random.randint(0, int(len(candles) / 4))
    to_move = copy.deepcopy(candles)

    while n > 0:
        x, y, fire = random.choice(list(to_move))
        to_move.remove((x, y, fire))
        if fire:
            board[x - 8][y], board[x - 9][y] = board[x - 9][y], board[x - 8][y]
        n -= 1


def put_out_a_candle(candles, board, without_candles):
    firing = [(x, y, fire) for (x, y, fire) in candles if fire]
    if firing:
        x, y, fire = random.choice(firing)
        assert fire
        candles.remove((x, y, fire))
        candles.add((x, y, False))
        set_candle(board, x, y, False, without_candles)


def create_board():
    return {
        i: {j: " " for j in range(-int(BOARD_WIDTH / 2), int(BOARD_WIDTH / 2))}
        for i in range(-int(BOARD_HEIGHT / 2), int(BOARD_HEIGHT / 2))
    }


def fill_up_board(board):
    set_plat(board)
    set_cake(board)
    set_coating(board)
    set_middle(board)


def add_input(input_queue):
    while True:
        input_queue.put(sys.stdin.read(1))


def main(years):
    board = create_board()
    fill_up_board(board)
    without_candles = copy.deepcopy(board)
    candles = set_candles(years, board)

    input_queue = Queue()
    input_thread = threading.Thread(target=add_input, args=(input_queue,))
    input_thread.daemon = True
    input_thread.start()

    def print_board_ascii(screen):
        while True:
            if not input_queue.empty():
                char = input_queue.get()
                if char == "f":
                    put_out_a_candle(candles, board, without_candles)
            move_candles(candles, board)
            board_str = get_board_str(board)
            for i in range(len(board_str)):
                screen.print_at(board_str[i], 0, i)
            screen.refresh()

    Screen.wrapper(print_board_ascii)


if __name__ == "__main__":
    main(YEARS)
