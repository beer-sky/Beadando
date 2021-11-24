'''
    Slide Puzzle
'''

import pygame
import numpy as np
from PIL import Image
from sympy.combinatorics.permutations import Permutation
from itertools import product


# Create the constants
NUM_OF_COLS = 4
NUM_OF_ROWS = 4
BLANK = NUM_OF_COLS * NUM_OF_ROWS - 1
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


def main():
    '''
        Initialization based on the constants
    '''
    global msg, if_image, FPSCLOCK, DISPLAYSURF, BASICFONT, RESET_SURF, RESET_RECT, NEW_SURF, NEW_RECT, SOLVE_SURF, SOLVE_RECT, IMAGES

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption('Slide Puzzle')
    BASICFONT = pygame.font.Font('freesansbold.ttf', BASICFONTSIZE)

    # Image TODO
    IMAGES = process_image()
    if_image = True

    # Board TODO

    # Buttons
    RESET_SURF, RESET_RECT = make_text(
        'Reset', TEXTCOLOR, BUTTONCOLOR, WINDOWWIDTH - 120, WINDOWHEIGHT - 90)
    NEW_SURF,   NEW_RECT = make_text(
        'New Game', TEXTCOLOR, BUTTONCOLOR, WINDOWWIDTH - 120, WINDOWHEIGHT - 60)
    SOLVE_SURF, SOLVE_RECT = make_text(
        'Solve',    TEXTCOLOR, BUTTONCOLOR, WINDOWWIDTH - 120, WINDOWHEIGHT - 30)

    # exit
    board = generate_new_puzzle()
    position = get_all_positions(board)
    moves = []
    SOLVEDBOARD = np.arange(
        NUM_OF_COLS * NUM_OF_ROWS).reshape(NUM_OF_ROWS, NUM_OF_COLS)
    msg = 'Click tile or press arrow keys to slide.'
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
                exit()

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
                        moves.clear()

                    elif SOLVE_RECT.collidepoint(event.pos):
                        moves.extend(solve_board(board, position))

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
                if event.key == pygame.K_LEFT and is_valid_move(board, 'left'):
                    slide_to = 'left'
                elif event.key == pygame.K_RIGHT and is_valid_move(board, 'right'):
                    slide_to = 'right'
                elif event.key == pygame.K_UP and is_valid_move(board, 'up'):
                    slide_to = 'up'
                elif event.key == pygame.K_DOWN and is_valid_move(board, 'down'):
                    slide_to = 'down'

        if slide_to:
            moves.append(slide_to)
            make_move(board, position, slide_to)

        pygame.display.update()
        FPSCLOCK.tick(FPS)


def process_image(image_source='dino.gif'):
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
    global if_image
    top, left = get_topleft_of_tile(tile_x, tile_y)
    pygame.draw.rect(DISPLAYSURF, TILECOLOR,
                     (left + adj_x, top + adj_y, TILESIZE, TILESIZE))
    if if_image:
        DISPLAYSURF.blit(IMAGES[number], (left + adj_x, top+adj_y))
        if False:  # Kirakást segítő, ráírjuk a számokat a képre
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


def slide_animation(board, direction, speed):
    '''
        Animates a move.
        Does not check if the move is valid
    '''
    blank_x, blank_y = get_position(board, BLANK)

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
        # check_for_quit() TODO
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


def is_valid_move(board, move):
    '''
        return if a move is valid
    '''
    blank_x, blank_y = get_position(board, BLANK)

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
        slide_animation(board, move, animation_speed)

    blank_x, blank_y = get_position(board, BLANK)

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
    ordered_board = [order_board(board)]

   # Make a permutation out of the board
    permutations = Permutation(
        list(ordered_board.reshape(1, NUM_OF_COLS*NUM_OF_ROWS))[0])

    # The general rule for both EVEN number of columns and ODD number of column is,
    # if the blank is in the bottom right corner, the number of inversions must be EVEN

    return (Permutation.parity(permutations) == 0)


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
    moves = []

    moves.extend(first_rows(board, position))

    return moves


if __name__ == '__main__':
    main()
