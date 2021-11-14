'''
    Slide Puzzle
'''

from numpy.lib.shape_base import tile
import pygame
import numpy as np
from pygame.constants import KEYDOWN, MOUSEBUTTONDOWN
from sympy.combinatorics.permutations import Permutation
from itertools import product

from sympy.core.numbers import E


# Create the constants
NUM_OF_COLS = 4
NUM_OF_ROWS = 4
BLANK = NUM_OF_COLS * NUM_OF_ROWS - 1
TILESIZE = 80
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
XMARGIN = (WINDOWWIDTH - (TILESIZE * NUM_OF_COLS + (NUM_OF_COLS + 1))) // 2
YMARGIN = (WINDOWHEIGHT - (TILESIZE * NUM_OF_ROWS + (NUM_OF_ROWS + 1))) // 2
FPS = 60
BASICFONTSIZE = 20

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BRIGHTBLUE = (0, 50, 255)
DARKTURQUOISE = (3, 54, 73)
GREEN = (0, 204, 0)

BGCOLOR = DARKTURQUOISE
TILECOLOR = GREEN
TEXTCOLOR = WHITE
BORDERCOLOR = BRIGHTBLUE
BUTTONCOLOR = WHITE
BUTTONTEXTCOLOR = BLACK
MESSAGECOLOR = WHITE


def main():
    '''
        Initialization based on the constants
    '''
    global FPSCLOCK, DISPLAYSURF, BASICFONT

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption('Slide Puzzle')
    BASICFONT = pygame.font.Font('freesansbold.ttf', BASICFONTSIZE)

    # Buttons
    # new
    # solve
    # reset
    # exit

    board = generate_new_puzzle()
    SOLVEDBOARD = np.arange(
        NUM_OF_COLS * NUM_OF_ROWS).reshape(NUM_OF_ROWS, NUM_OF_COLS)
    msg = 'Click tile or press arrow keys to slide.'
    run = True

    while run:    # Main game loop
        slide_to = None  # The direction a tile should slide

        if np.all(board == SOLVEDBOARD):
            msg = 'Congratulations!'

        draw_board(board, msg)

        for event in pygame.event.get():  # Event loop
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                exit()

            if event.type == MOUSEBUTTONDOWN:
                tile_x, tile_y = get_tile_clicked(
                    board, event.pos[0], event.pos[1])

                if (tile_x, tile_y) == (None, None):  # If the user clicked on a button
                    # TODO
                    pass

                else:  # If the clicked tile was next to the blank spot
                    blank_x, blank_y = get_blank_position(board)
                    print(blank_x, blank_y)
                    if tile_x == blank_x + 1 and tile_y == blank_y:
                        slide_to = 'up'
                    elif tile_x == blank_x - 1 and tile_y == blank_y:
                        slide_to = 'down'
                    elif tile_x == blank_x and tile_y == blank_y + 1:
                        slide_to = 'left'
                    elif tile_x == blank_x and tile_y == blank_y - 1:
                        slide_to = 'right'
                    print(slide_to)

            elif event.type == KEYDOWN:
                # TODO
                pass

        if slide_to:
            slide_animation(board, slide_to, msg)
            make_move(board, slide_to)

        pygame.display.update()
        FPSCLOCK.tick(FPS)


def generate_new_puzzle():
    '''
        Return a 2D numpy array, Which is solvable.
        For example a 3x4 board is:
        [
            [ 3,  0,  2,  5]
            [10,  7,  4,  8]
            [ 1,  6,  9, 11]
        ]
        where the last element is always the BLANK
    '''
    perm = Permutation.random(NUM_OF_ROWS * NUM_OF_COLS - 1)
    while Permutation.parity(perm):
        perm = Permutation.random(NUM_OF_ROWS * NUM_OF_COLS - 1)
    perm_list = list(perm)
    perm_list.append(BLANK)
    return np.array(perm_list, dtype='int32').reshape(NUM_OF_ROWS, NUM_OF_COLS)


def make_text(text, color, bgcolor, top, left):
    '''
        Create the Surface and Rect objects for some text.
    '''
    text_surf = BASICFONT.render(text, True, color, bgcolor)
    text_rect = text_surf.get_rect(topleft=(top, left))
    return (text_surf, text_rect)


def get_topleft_of_tile(tile_x, tile_y):
    '''
        return the topleft coordinates of a tile
    '''
    top = YMARGIN + (tile_x * TILESIZE) + (tile_x - 1)
    left = XMARGIN + (tile_y * TILESIZE) + (tile_y - 1)
    return (top, left)


def draw_tile(tile_x, tile_y, number, adj_x=0, adj_y=0):
    '''
        draw a tile
        tile_x and tile_y is the tile's x and y position in the board array
        adj_x and adj_y is for animating
        they are small distances in the direction of the corresponding axles
    '''
    top, left = get_topleft_of_tile(tile_x, tile_y)
    pygame.draw.rect(DISPLAYSURF, TILECOLOR,
                     (left + adj_x, top + adj_y, TILESIZE, TILESIZE))

    text_surf = BASICFONT.render(str(number), True, TEXTCOLOR)
    text_rect = text_surf.get_rect(
        center=(left + TILESIZE//2 + adj_x, top + TILESIZE//2 + adj_y))
    DISPLAYSURF.blit(text_surf, text_rect)


def draw_board(board, msg):
    DISPLAYSURF.fill(BGCOLOR)
    text_suft, text_rect = make_text(msg, MESSAGECOLOR, BGCOLOR, 5, 5)
    DISPLAYSURF.blit(text_suft, text_rect)

    for coordinates in product(list(range(NUM_OF_ROWS)), list(range(NUM_OF_COLS))):
        if board[coordinates] != BLANK:
            draw_tile(*coordinates, board[coordinates])

    top, left = get_topleft_of_tile(0, 0)
    width = NUM_OF_COLS * TILESIZE + NUM_OF_COLS + 1
    height = NUM_OF_ROWS * TILESIZE + NUM_OF_ROWS + 1

    PADDING = 5
    RADIUS = 4
    pygame.draw.rect(DISPLAYSURF, BORDERCOLOR,
                     (left-PADDING, top-PADDING, width + PADDING + RADIUS//2, height + PADDING + RADIUS//2), RADIUS)

    # gombok kirajzolása TODO


def get_tile_clicked(board, x, y):
    '''
        From he x and y pixel coordinates, get the x and y board coordinates
    '''
    for coordinates in product(list(range(NUM_OF_ROWS)), list(range(NUM_OF_COLS))):
        top, left = get_topleft_of_tile(*coordinates)
        tile_rect = pygame.Rect(left, top, TILESIZE, TILESIZE)
        if tile_rect.collidepoint(x, y):
            return coordinates

    return (None, None)


def get_blank_position(board):
    '''
        Return the x and y board coordinates of the blank space
    '''
    for cooridnates in product(list(range(NUM_OF_ROWS)), list(range(NUM_OF_COLS))):
        if board[cooridnates] == BLANK:
            return cooridnates


def slide_animation(board, direction, msg):
    '''
        Animates a move.
        Does not check if the move is valid
    '''
    ANIMATION_SPEED = 8
    blank_x, blank_y = get_blank_position(board)

    if direction == 'left':
        move_x, move_y = blank_x, blank_y + 1
    elif direction == 'right':
        move_x, move_y = blank_x, blank_y - 1
    elif direction == 'up':
        move_x, move_y = blank_x + 1, blank_y
    elif direction == 'down':
        move_x, move_y = blank_x - 1, blank_y

    draw_board(board, msg)
    base_surf = DISPLAYSURF.copy()
    move_top, move_left = get_topleft_of_tile(move_x, move_y)
    pygame.draw.rect(base_surf, BGCOLOR, (move_left,
                     move_top, TILESIZE, TILESIZE))

    for i in range(0, TILESIZE, ANIMATION_SPEED):
        # animate the tile sliding over
        # checkForQuit() TODO
        DISPLAYSURF.blit(base_surf, (0, 0))
        if direction == 'up':
            draw_tile(move_x, move_y, board[move_x, move_y], 0, -i)
        if direction == 'down':
            draw_tile(move_x, move_y, board[move_x, move_y], 0, i)
        if direction == 'left':
            draw_tile(move_x, move_y, board[move_x, move_y], -i, 0)
        if direction == 'right':
            draw_tile(move_x, move_y, board[move_x, move_y], i, 0)

        pygame.display.update()
        FPSCLOCK.tick(FPS)


def make_move(board, move):
    '''
        Does not check if a move is valid
    '''
    blank_x, blank_y = get_blank_position(board)

    if move == 'left':
        board[blank_x, blank_y], board[blank_x, blank_y +
                                       1] = board[blank_x, blank_y + 1], board[blank_x, blank_y]
    elif move == 'right':
        board[blank_x, blank_y], board[blank_x, blank_y -
                                       1] = board[blank_x, blank_y - 1], board[blank_x, blank_y]
    elif move == 'up':
        board[blank_x, blank_y], board[blank_x + 1,
                                       blank_y] = board[blank_x + 1, blank_y], board[blank_x, blank_y]
    elif move == 'down':
        board[blank_x, blank_y], board[blank_x - 1,
                                       blank_y] = board[blank_x - 1, blank_y], board[blank_x, blank_y]


if __name__ == '__main__':
    main()
