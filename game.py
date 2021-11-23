'''
    Slide Puzzle
'''

import pygame
import numpy as np
from sympy.combinatorics.permutations import Permutation
from itertools import product


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

    # Buttons TODO
    # new
    # solve
    # reset
    # exit

    board = generate_new_puzzle()
    position = get_all_positions(board)
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

            if event.type == pygame.MOUSEBUTTONDOWN:
                tile_x, tile_y = get_tile_clicked(
                    board, event.pos[0], event.pos[1])

                if (tile_x, tile_y) == (None, None):  # If the user clicked on a button
                    # TODO
                    pass

                else:  # If the clicked tile was next to the blank spot
                    blank_x, blank_y = get_position(board, BLANK)
                    if tile_x == blank_x + 1 and tile_y == blank_y:
                        slide_to = 'up'
                    elif tile_x == blank_x - 1 and tile_y == blank_y:
                        slide_to = 'down'
                    elif tile_x == blank_x and tile_y == blank_y + 1:
                        slide_to = 'left'
                    elif tile_x == blank_x and tile_y == blank_y - 1:
                        slide_to = 'right'

            elif event.type == pygame.KEYDOWN:
                # TODO
                pass

        if slide_to:
            make_move(board, position, slide_to)

        first_rows(board, position)

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


def get_position(board, number):
    '''
        Return the x and y board coordinates of the blank space
    '''

    for index, x in np.ndenumerate(board):
        if x == number:
            return index


def get_all_positions(board):
    '''
        return a list. i_th element is the coordinates of number i in the board.
    '''
    positions = [0]*(NUM_OF_COLS * NUM_OF_ROWS)
    for index, x in np.ndenumerate(board):
        positions[x] = index
    return positions


def slide_animation(board, direction, msg):
    '''
        Animates a move.
        Does not check if the move is valid
    '''
    ANIMATION_SPEED = 8
    blank_x, blank_y = get_position(board, BLANK)

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


def make_move(board, position, move, anim=True):
    '''
        Does not check if a move is valid
        changes board and position
        returns the move
    '''
    blank_x, blank_y = get_position(board, BLANK)

    match move:
        case 'left':
            new_x, new_y = blank_x, blank_y + 1
        case 'right':
            new_x, new_y = blank_x, blank_y - 1
        case 'up':
            new_x, new_y = blank_x + 1, blank_y
        case 'down':
            new_x, new_y = blank_x - 1, blank_y

    if anim:
        slide_animation(board, move, "asd")

    swapped_num = board[new_x, new_y]
    position[BLANK], position[swapped_num] = position[swapped_num], position[BLANK]
    board[blank_x, blank_y], board[new_x,
                                   new_y] = board[new_x, new_y], board[blank_x, blank_y]

    # print("move: ", move, " swapped: ", swapped_num)
    # print("blank pos: ", position[BLANK])
    # print("new_pos: ", position[swapped_num])
    return move


def order_board(original_board, original_position):
    '''
        Given a board, transports the blank tile to the bottom right corner, with legal moves
    '''
    board = np.copy(original_board)
    position = list.copy(original_position)

    blank_x, blank_y = get_position(board, BLANK)
    # How many tiles we have to move the blank to the right
    distance_from_right = NUM_OF_COLS - int(blank_x/NUM_OF_COLS) - 1
    # How many tiles we have to move the blank to down
    distance_from_bottom = NUM_OF_ROWS - int(blank_y/NUM_OF_ROWS) - 1
    for i in range(distance_from_right):
        make_move(board, position, 'right')
    for j in range(distance_from_bottom):
        make_move(board, position, 'down')
    return board


def solvable(board):
    '''
        Determines whether a given board is solvable or not
    '''
    # ordered_board = [order_board(board)]

    # # Make a permutation out of the board
    # permutations = Permutation(
    #     list(ordered_board.reshape(1, NUM_OF_COLS*NUM_OF_ROWS))[0])

    # # The general rule for both EVEN number of columns and ODD number of column is,
    # # if the blank is in the bottom right corner, the number of inversions must be EVEN

    # return (Permutation.parity(permutations) == 0)


def move_blank_to(board, position, x, y):
    '''
        Moves BLANK to the given coordinate: x,y
    '''
    moves = []
    # sorban mozgat
    while position[BLANK][1] != y:
        if position[BLANK][1] < y:
            moves.append(make_move(board, position, 'left'))
        else:
            moves.append(make_move(board, position, 'right'))

    # oszlopban mozgat
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
    # sorban mozgat
    if position[tile][0] == NUM_OF_ROWS-1:  # Ha utolsó sorban van, kihozzuk
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

    # ha ugyanabban a sorban van a BLANK mint a tile akkor elromolna
    if position[tile][0] == position[BLANK][0] and position[tile][1] > position[BLANK][1]:
        moves.extend(move_blank_to(board, position,
                                   position[tile][0]+1, position[BLANK][1]))

    # oszlopban mozgat
    if position[tile][1] == NUM_OF_COLS-1:  # kihozzuk az utolsó oszlopból, ha ott van
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
        print(i, j)
        # az (i,j) helyre próbáljuk a megfelelő tile-t vinni

        if j < NUM_OF_COLS-2:  # ha nem az utolsó két oszlop
            tile = i*NUM_OF_COLS+j
            moves.extend(move_tile_to(board, position, tile, i, j))

        elif j == NUM_OF_COLS-2:  # ha az utolsó előtti oszlop: oda visszük az utolsó oszlop elemét
            tile = i*NUM_OF_COLS+j+1
            # ha mellette van a utolsó előtti elem beragadnánk
            if board[i][j] == i*NUM_OF_COLS+j:
                moves.extend(move_blank_to(board, position, i, j))
                moves.append(make_move(board, position, 'left'))
            moves.extend(move_tile_to(board, position, tile, i, j))

        else:  # utolsó oszlop
            # utolsó előtti elemet elvisszük a helyére, közben utolsó elem is jó helyére kerül
            tile = i*NUM_OF_COLS+j-1
            if position[BLANK] == (i, j):  # ezt oldja meg: 0 1 3 15
                #  * * * 2
                moves.append(make_move(board, position, 'up'))
            if position[tile] == (i, j):  # megoldja ha a sorrend 0 1 3 2
                moves.extend(move_blank_to(board, position, i, j-1))
                moves.append(make_move(board, position, 'left'))
                moves.append(make_move(board, position, 'up'))
                moves.append(make_move(board, position, 'up'))
                moves.append(make_move(board, position, 'right'))
                moves.append(make_move(board, position, 'down'))
                moves.append(make_move(board, position, 'down'))
                moves.append(make_move(board, position, 'left'))
                moves.extend(move_tile_to(board, position, tile+1, i, j-1))
            moves.extend(move_tile_to(board, position, tile, i+1, j-1))
            moves.extend(move_tile_to(board, position,
                         tile, i, position[tile][1]))

    return moves


if __name__ == '__main__':
    main()
