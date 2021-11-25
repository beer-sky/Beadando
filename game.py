'''
    Slide Puzzle
'''

import pygame
import numpy as np
import sys
from PIL import Image
from sympy.combinatorics.permutations import Permutation
from itertools import product
from sys import argv
from getopt import getopt


# These may change during initialization
NUM_OF_COLS = 4
NUM_OF_ROWS = 4
BLANK = 15

# Create the constants
TILESIZE = 80
WINDOWWIDTH = 1280
WINDOWHEIGHT = 720
XMARGIN = (WINDOWWIDTH - (TILESIZE * NUM_OF_COLS + (NUM_OF_COLS + 1))) // 2
YMARGIN = (WINDOWHEIGHT - (TILESIZE * NUM_OF_ROWS + (NUM_OF_ROWS + 1))) // 2
FPS = 60
BASICFONTSIZE = 20

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
IVORY = (255, 255, 240)
SAND = (219, 213, 185)
DARK_SAND = (192, 186, 153)


BGCOLOR = IVORY
TILECOLOR = DARK_SAND
TEXTCOLOR = BLACK
BORDERCOLOR = BLACK
BUTTONCOLOR = SAND
BUTTONTEXTCOLOR = BLACK
MESSAGECOLOR = BLACK
DEFAULT_IMAGE = "dino.gif"


def main():
    '''
        Initialization based on the constants
    '''
    global msg, show_image, show_number, \
        FPSCLOCK, DISPLAYSURF, BASICFONT, IMAGES, NUM_OF_ROWS, NUM_OF_COLS, BLANK, \
        RESET_SURF, RESET_RECT, NEW_SURF, NEW_RECT, SOLVE_SURF, SOLVE_RECT

    # Initialization for the game
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption('Slide Puzzle')
    BASICFONT = pygame.font.Font('freesansbold.ttf', BASICFONTSIZE)
    show_image = False
    show_number = False

    # Buttons
    RESET_SURF, RESET_RECT = make_text(
        'Reset', TEXTCOLOR, BUTTONCOLOR, WINDOWWIDTH - 120, WINDOWHEIGHT - 90)
    NEW_SURF,   NEW_RECT = make_text(
        'New Game', TEXTCOLOR, BUTTONCOLOR, WINDOWWIDTH - 120, WINDOWHEIGHT - 60)
    SOLVE_SURF, SOLVE_RECT = make_text(
        'Solve',    TEXTCOLOR, BUTTONCOLOR, WINDOWWIDTH - 120, WINDOWHEIGHT - 30)

    board = None

    # check for command line arguments:
    arg = argv[1:]
    opts, _ = getopt(arg, "b:d:i:s:n:", [
                     "board=", "dimensions=", "image=", "source=", "shownumber="])
    for opt, val in opts:
        # Make the game board
        if opt in ("--board", "-s"):
            board = np.genfromtxt(val, delimiter=',', dtype=int)
            NUM_OF_ROWS, NUM_OF_COLS = np.shape(board)
        elif opt in ("--dimensions", "-d"):
            NUM_OF_ROWS, NUM_OF_COLS = tuple(map(int, val.split(',')))
        BLANK = NUM_OF_COLS * NUM_OF_ROWS - 1

        # Get the image
        if opt in ("--image", "-i"):
            show_image = True if val == 'True' else False

        if opt in ("--source", "-s"):
            IMAGES = process_image(val)
        elif show_image:
            IMAGES = process_image(DEFAULT_IMAGE)

        if opt in ("--shownumber", "-n"):
            show_number = True if val == 'True' else False

    if board is None:
        board = generate_new_puzzle()

    position = get_all_positions(board)
    moves = []
    msg = 'Click tile or press arrow keys to slide.'
    solvable = if_solvable(board, position)
    if not solvable:
        msg = 'This board is not solvable! Click tile or press arrow keys to slide.'

    SOLVEDBOARD = np.arange(
        NUM_OF_COLS * NUM_OF_ROWS).reshape(NUM_OF_ROWS, NUM_OF_COLS)
    run = True

    while run:    # Main game loop
        slide_to = None  # The direction a tile should slide

        if np.all(board == SOLVEDBOARD):
            msg = 'Congratulations!'

        draw_board(board)

        for event in pygame.event.get():  # Event loop
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                tile_x, tile_y = get_tile_clicked(
                    board, event.pos[0], event.pos[1])

                if (tile_x, tile_y) == (None, None):  # If the user clicked on a button

                    if RESET_RECT.collidepoint(event.pos):
                        moves = reverse_moves(moves)
                        for move in moves:
                            make_move(board, position, move,
                                      animation_speed=24)
                        moves.clear()

                    elif NEW_RECT.collidepoint(event.pos):
                        board = generate_new_puzzle()
                        position = get_all_positions(board)
                        msg = 'Click tile or press arrow keys to slide.'
                        solvable = True
                        moves.clear()

                    elif SOLVE_RECT.collidepoint(event.pos):
                        if solvable:
                            moves.extend(solve_board(board, position))

                else:  # If the clicked tile was next to the blank spot
                    blank_x, blank_y = position[BLANK]
                    if tile_x == blank_x + 1 and tile_y == blank_y:
                        slide_to = 'up'
                    elif tile_x == blank_x - 1 and tile_y == blank_y:
                        slide_to = 'down'
                    elif tile_x == blank_x and tile_y == blank_y + 1:
                        slide_to = 'left'
                    elif tile_x == blank_x and tile_y == blank_y - 1:
                        slide_to = 'right'

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and is_valid_move(position, 'left'):
                    slide_to = 'left'
                elif event.key == pygame.K_RIGHT and is_valid_move(position, 'right'):
                    slide_to = 'right'
                elif event.key == pygame.K_UP and is_valid_move(position, 'up'):
                    slide_to = 'up'
                elif event.key == pygame.K_DOWN and is_valid_move(position, 'down'):
                    slide_to = 'down'

        if slide_to:
            moves.append(slide_to)
            make_move(board, position, slide_to)

        pygame.display.update()
        FPSCLOCK.tick(FPS)


def process_image(image_source):
    img = Image.open(image_source)
    img = img.rotate(90)
    height = NUM_OF_COLS * TILESIZE
    width = NUM_OF_ROWS * TILESIZE
    img = img.resize((width, height), Image.ANTIALIAS)
    image_array = np.asarray(img)
    tiles = [image_array[x:x+TILESIZE, y:y+TILESIZE]
             for x in range(0, image_array.shape[0], TILESIZE) for y in range(0, image_array.shape[1], TILESIZE)]
    tiles = [pygame.surfarray.make_surface(x) for x in tiles]
    ordered_tiles = []
    for i, j in product(list(range(NUM_OF_ROWS)), list(range(NUM_OF_COLS))):
        ordered_tiles.append(tiles[i+j*NUM_OF_ROWS])
    return ordered_tiles


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

    global show_image, show_number

    top, left = get_topleft_of_tile(tile_x, tile_y)
    pygame.draw.rect(DISPLAYSURF, TILECOLOR,
                     (left + adj_x, top + adj_y, TILESIZE, TILESIZE))

    if show_image:
        DISPLAYSURF.blit(IMAGES[number], (left + adj_x, top+adj_y))
        if show_number:
            text_surf = BASICFONT.render(str(number), True, TEXTCOLOR)
            text_rect = text_surf.get_rect(
                center=(left + TILESIZE//2 + adj_x, top + TILESIZE//2 + adj_y))
            DISPLAYSURF.blit(text_surf, text_rect)

    else:
        text_surf = BASICFONT.render(str(number), True, TEXTCOLOR)
        text_rect = text_surf.get_rect(
            center=(left + TILESIZE//2 + adj_x, top + TILESIZE//2 + adj_y))
        DISPLAYSURF.blit(text_surf, text_rect)


def draw_board(board):
    DISPLAYSURF.fill(BGCOLOR)
    text_suft, text_rect = make_text(msg, MESSAGECOLOR, BGCOLOR, 10, 10)
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

    DISPLAYSURF.blit(RESET_SURF, RESET_RECT)
    DISPLAYSURF.blit(NEW_SURF, NEW_RECT)
    DISPLAYSURF.blit(SOLVE_SURF, SOLVE_RECT)


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


def get_all_positions(board):
    '''
        return a list. i_th element is the coordinates of number i in the board.
    '''
    positions = [0]*(NUM_OF_COLS * NUM_OF_ROWS)
    for index, x in np.ndenumerate(board):
        positions[x] = index
    return positions


def slide_animation(board, position, direction, speed):
    '''
        Animates a move.
        Does not check if the move is valid
    '''
    blank_x, blank_y = position[BLANK]

    if direction == 'left':
        move_x, move_y = blank_x, blank_y + 1
    elif direction == 'right':
        move_x, move_y = blank_x, blank_y - 1
    elif direction == 'up':
        move_x, move_y = blank_x + 1, blank_y
    elif direction == 'down':
        move_x, move_y = blank_x - 1, blank_y

    draw_board(board)
    base_surf = DISPLAYSURF.copy()
    move_top, move_left = get_topleft_of_tile(move_x, move_y)
    pygame.draw.rect(base_surf, BGCOLOR, (move_left,
                     move_top, TILESIZE, TILESIZE))

    for i in range(0, TILESIZE, speed):
        # animate the tile sliding over
        check_for_quit()
        DISPLAYSURF.blit(base_surf, (0, 0))

        if direction == 'up':
            draw_tile(move_x, move_y, board[move_x, move_y], 0, -i)
        elif direction == 'down':
            draw_tile(move_x, move_y, board[move_x, move_y], 0, i)
        elif direction == 'left':
            draw_tile(move_x, move_y, board[move_x, move_y], -i, 0)
        elif direction == 'right':
            draw_tile(move_x, move_y, board[move_x, move_y], i, 0)

        pygame.display.update()
        FPSCLOCK.tick(FPS)


def check_for_quit():
    for event in pygame.event.get(pygame.QUIT):  # get all the QUIT events
        pygame.quit()
        sys.exit()
    for event in pygame.event.get(pygame.KEYDOWN):  # get all the KEYUP events
        if event.key == pygame.K_ESCAPE:
            pygame.quit()
            sys.exit()
        pygame.event.post(event)  # put the other KEYUP event objects back


def is_valid_move(position, move):
    '''
        return if a move is valid
    '''
    blank_x, blank_y = position[BLANK]

    return (move == 'up' and blank_x != NUM_OF_ROWS-1) or \
        (move == 'down' and blank_x != 0) or \
        (move == 'left' and blank_y != NUM_OF_COLS-1) or \
        (move == 'right' and blank_y != 0) \



def make_move(board, position, move, animation=True, animation_speed=8):
    '''
        Does not check if a move is valid
        changes board and position
        returns the move
    '''
    if animation:
        slide_animation(board, position, move, animation_speed)

    blank_x, blank_y = position[BLANK]

    if move == 'left':
        new_x, new_y = blank_x, blank_y + 1
    elif move == 'right':
        new_x, new_y = blank_x, blank_y - 1
    elif move == 'up':
        new_x, new_y = blank_x + 1, blank_y
    elif move == 'down':
        new_x, new_y = blank_x - 1, blank_y

    swapped_num = board[new_x, new_y]
    position[BLANK], position[swapped_num] = position[swapped_num], position[BLANK]
    board[blank_x, blank_y], board[new_x,
                                   new_y] = board[new_x, new_y], board[blank_x, blank_y]

    return move


def reverse_moves(moves):
    opposite_moves = {'left': 'right',
                      'right': 'left',
                      'up': 'down',
                      'down': 'up'}

    reversed = [opposite_moves[move] for move in moves]
    reversed.reverse()
    return reversed


def order_board(original_board, original_position):
    '''
        Given a board, make a copy of is.
        Moves the blank tile to the bottom right corner with legal moves
        return ordered board
    '''
    board = np.copy(original_board)
    position = list.copy(original_position)
    while position[BLANK][0] != NUM_OF_ROWS-1:
        make_move(board, position, 'up', animation=False)
    while position[BLANK][1] != NUM_OF_COLS-1:
        make_move(board, position, 'left', animation=False)
    return board


def if_solvable(board, position):
    '''
        Determines whether a given board is solvable or not
    '''
    ordered_board = order_board(board, position)
    permutations = Permutation(ordered_board.flatten())

    return (Permutation.parity(permutations) == 0)


def move_blank_to(board, position, x, y):
    '''
        Moves BLANK to the given coordinate: x,y
    '''
    moves = []
    # Moves in lines
    while position[BLANK][1] != y:
        if position[BLANK][1] < y:
            moves.append(make_move(board, position, 'left'))
        else:
            moves.append(make_move(board, position, 'right'))

    # Moves in columns
    while position[BLANK][0] != x:
        if position[BLANK][0] < x:
            moves.append(make_move(board, position, 'up'))
        else:
            moves.append(make_move(board, position, 'down'))
    return moves


def move_tile_to(board, position, tile, x, y):
    '''
        Moves tile to the given coordinate: x,y
        tile: number of the tile
        we don't touch tiles on the left and top of x, y
            if not necessary.
    '''
    moves = []

    # Moves in lines
    if position[tile][0] == NUM_OF_ROWS-1:  # If in the last row, take it out
        moves.extend(move_blank_to(board, position, NUM_OF_ROWS -
                                   2, position[BLANK][1]))
        moves.extend(move_blank_to(board, position,
                                   position[tile][0]-1, position[tile][1]))
        moves.append(make_move(board, position, 'up'))

    while position[tile][1] != y:
        moves.extend(move_blank_to(board, position,
                                   position[tile][0]+1, position[BLANK][1]))
        if position[tile][1] < y:
            moves.extend(move_blank_to(
                board, position, position[tile][0], position[tile][1]+1))
            moves.append(make_move(board, position, 'right'))
        else:
            moves.extend(move_blank_to(
                board, position, position[tile][0], position[tile][1]-1))
            moves.append(make_move(board, position, 'left'))

    # If the BLANK and tile would be in the same row, it would get wrong
    if position[tile][0] == position[BLANK][0] and position[tile][1] > position[BLANK][1]:
        moves.extend(move_blank_to(board, position,
                                   position[tile][0]+1, position[BLANK][1]))

    # Moves in Column
    if position[tile][1] == NUM_OF_COLS-1:  # If in the last co, take it out
        moves.extend(move_blank_to(board, position,
                                   position[BLANK][0], NUM_OF_COLS-2))
        moves.extend(move_blank_to(board, position,
                                   position[tile][0], position[tile][1]-1))
        moves.append(make_move(board, position, 'left'))

    while position[tile][0] != x:
        moves.extend(move_blank_to(board, position,
                                   position[BLANK][0], position[tile][1]+1))
        moves.extend(move_blank_to(board, position,
                                   position[tile][0]-1, position[BLANK][1]))
        moves.extend(move_blank_to(board, position,
                                   position[BLANK][0], position[tile][1]))
        moves.append(make_move(board, position, 'up'))

    return moves


def first_rows(board, position):
    '''
        Solves the first NUM_OF_ROWS-2 rows
    '''
    moves = []

    for i, j in product(list(range(NUM_OF_ROWS-2)), list(range(NUM_OF_COLS))):
        # Tries to move the correct tile into (i,j)

        if j < NUM_OF_COLS-2:  # if not the last 2 columns
            tile = i*NUM_OF_COLS+j
            moves.extend(move_tile_to(board, position, tile, i, j))

        # If the col before the last: we take here the last element
        elif j == NUM_OF_COLS-2:
            tile = i*NUM_OF_COLS+j+1

            # If the last would be next to it, we woult get stucked
            if board[i][j] == i*NUM_OF_COLS+j:
                moves.extend(move_blank_to(board, position, i, j))
                moves.append(make_move(board, position, 'left'))
            moves.extend(move_tile_to(board, position, tile, i, j))

        else:  # Last column
            # We take the elements before the last to their place,
            # The last element will go to its place automatically
            tile = i*NUM_OF_COLS+j-1
            if position[BLANK] == (i, j):  # Solves: 0 1 3 15
                #  * * * 2
                moves.append(make_move(board, position, 'up'))
            if position[tile] == (i, j):  # Solves if the order: 0 1 3 2
                moves.extend(move_blank_to(board, position, i, j-1))

                moves_to_do = ['left', 'up', 'up',
                               'right', 'down', 'down', 'left']
                for move in moves_to_do:
                    moves.append(make_move(board, position, move))

                moves.extend(move_tile_to(board, position, tile+1, i, j-1))
            moves.extend(move_tile_to(board, position, tile, i+1, j-1))
            moves.extend(move_tile_to(board, position,
                         tile, i, position[tile][1]))

    return moves


def solve_board(board, position):  # TODO
    '''
        Solve the puzzle
    '''

    moves = (first_rows(board, position))

    return moves


if __name__ == '__main__':
    main()
