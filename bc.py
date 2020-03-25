import math
import random
from copy import copy

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
        if not {c for k, c in board[i].items() if c != " "}:
            continue
        for j in board[i]:
            s += board[i][j]
        ret.append(s)
        s = ""

    return ret


def set_on_board(fun, char, board):
    for i in board:
        for j in board[i]:
            if fun(i, j):
                board[i][j] = char


def ellipse_disk(x, y, x0, y0, A, B, r):
    return (x - x0) ** 2 / A + (y - y0) ** 2 / B < r ** 2


def ellipse(x, y, x0, y0, A, B, r):
    return math.fabs((x - x0) ** 2 / A + (y - y0) ** 2 / B - r ** 2) < 1


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


def set_coating(board):
    set_on_board(coating, "@", board)


def middle(x, y):
    return ellipse(x, y, -CAKE_HEIGHT / 2, 0, 1, 20, CAKE_R) if x > -CAKE_HEIGHT / 2 else False


def set_middle(board):
    set_on_board(middle, "%", board)


def set_candle(board, x, y):
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
    board[x - 7][y - 1] = "("
    board[x - 7][y + 1] = ")"
    board[x - 7][y] = "o"
    board[x - 8][y] = "("
    board[x - 10][y] = ")"


def set_candles(years, board):
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
        for candle_x, candle_y in candles:
            if math.fabs(candle_y - y) < 4 and math.fabs(candle_x - x) < 12:
                fits = False
                break

        if not fits:
            continue

        candles.add((x, y))
        set_candle(board, x, y)

    return candles


def move_candles(candles, board):
    n = random.randint(0, int(len(candles) / 4))
    to_move = copy(candles)

    while n > 0:
        x, y = random.choice(list(to_move))
        to_move.remove((x, y))
        board[x - 8][y], board[x - 10][y] = board[x - 10][y], board[x - 8][y]
        n -= 1


def create_board():
    return {
        i: {j: " " for j in range(-int(BOARD_WIDTH / 2), int(BOARD_WIDTH / 2))}
        for i in range(-int(BOARD_HEIGHT / 2), int(BOARD_HEIGHT / 2))
    }


def fill_up_board(board, candles_number):
    set_plat(board)
    set_cake(board)
    set_coating(board)
    set_middle(board)
    return set_candles(candles_number, board), board


def main(years):
    candles, board = fill_up_board(create_board(), years)

    def print_board_ascii(screen):
        while True:
            move_candles(candles, board)
            board_str = get_board_str(board)
            for i in range(len(board_str)):
                screen.print_at(board_str[i], 0, i)
            screen.refresh()

    Screen.wrapper(print_board_ascii)


if __name__ == "__main__":
    main(YEARS)
