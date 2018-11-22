import re
import os
import time
import copy
from typing import List
# import pygame


class Board:
    def __init__(self, tick: int, height, width, state=None):
        """Initialize board object."""

        if state is None:
            state = [[Cell(False, row, col, self) for col in range(width)] for row in range(height)]

        self.tick = tick
        self.height = height
        self.width = width
        self.state = state

    def __str__(self):
        """Display relevant metadata for Board objects."""

        s = '<__main__.Board object at {}>:'.format(hex(id(self)))
        s += '\n\ttick: {}'.format(self.tick)
        s += '\n\theight: {}'.format(self.height)
        s += '\n\twidth: {}'.format(self.width)
        s += '\n\tstate: <{}>'.format(hex(id(self.state)))
        for row in self.state:
            s += '\n\t\t<{} : {}>'.format(hex(id(row)), )
            s += ','.join(['<{}>'.format(self.state[row][col]) for col in row])
            s += '>'
        for row in self.state:
            s += '\n\t\t{}'.format(row)

        return s

    def set_board_states(self):
        """Prompt user to set alive cells in board."""

        commands = {'live': 'turn on cells in the board',
                    'die': 'turn off cells in the board',
                    'clear': 'clear the board',
                    'show': 'show the state of the board',
                    'end': 'done setting up board',
                    'help': 'list available commands'}

        def valid_cell_format(s):
            """Determine if string follows the format "(a, b), (c, d), ... ".

            Credit to Patrick Artner:
                https://stackoverflow.com/questions/53419606/validating-user-input-with-regex

            """

            return re.match(r'^\s*([^,]+,[^,]+\)\s*(?:,\s*\([^,]+,[^,]+\))*)\s*$', s)

        def separate_valids(s):
            """Return 2 sets of valid and invalid coordinates in s respectively.

            Credit to Patrick Artner:
                https://stackoverflow.com/questions/53419606/validating-user-input-with-regex

            """

            # Remove all spaces from user input
            s = s.replace(" ", "")

            # Check if input is a proper list of tuples
            if not valid_cell_format(s):
                raise ValueError('Could not parse input.')

            # Convert string input like "(1, 4), (a, 7), (-3, 3), (3, 3)"
            # to a list like ['1,4', 'a,7', '-3,3', '3,3']
            stripped_coord = [j.lstrip("(") for j in s.replace(" ", "").rstrip(")").split("),")]

            # Convert ['1,4', 'a,7', '-3,3', '3,3']
            # to [(1, 4), ('a', 7), ('-3', 3), (3, 3)]
            all_tuples = [tuple(map(try_int, nums.split(","))) for nums in stripped_coord]

            # Create sets that hold valid and invalid tuples
            valid_tuples = []
            invalid_tuples = []
            for j in all_tuples:
                # Adds tuples only if not duplicates
                if self.coord_in_range(j):
                    if j not in valid_tuples:
                        valid_tuples.append(j)
                else:
                    if j not in invalid_tuples:
                        invalid_tuples.append(j)

            return valid_tuples, invalid_tuples

        cont = True
        while cont:
            cmd = input('Enter a command or type help for more info:\n>>> ').lower()

            if cmd in ['live', 'die']:
                print()

                cont_ = True
                while cont_:
                    coords = input('Enter cells to {} as (x,y) coordinates separated by spaces:'
                                   '\n>>> '.format(cmd))

                    try:
                        valid_coords, invalid_coords = separate_valids(coords)
                    except ValueError as e:
                        # Coords was not entered in a valid format
                        print('\n{} '.format(e), end='')
                    else:
                        # Entered coords are of integers and are in range
                        # Print the valid coords
                        for tup in valid_coords:
                            col, row = tup[0], tup[1]
                            if cmd == 'live':
                                if self.cell_at(row, col).is_alive():
                                    print('\tCell at ({}, {}) was already alive.'.format(col, row))
                                else:
                                    self.cell_at(row, col).live()
                                    print('\tRevived cell at ({}, {}).'.format(col, row))
                            else:
                                if self.cell_at(row, col).is_dead():
                                    print('\tCell at ({}, {}) was already dead.'.format(col, row))
                                else:
                                    self.cell_at(row, col).live()
                                    print('\tKilled cell at ({}, {}).'.format(col, row))
                        if len(invalid_coords) != 0:
                            # Print the invalid coords
                            print('\tThe following coordinates were invalid '
                                  'and were left unchanged:')
                            for tup in invalid_coords:
                                col, row = tup[0], tup[1]
                                print('\t\t({}, {})'.format(col, row))

                        cont_ = False
                print()
            elif cmd == 'clear':
                self.clear_board()
            elif cmd == 'show':
                self.render_board('[Board Editing Mode]', True)
                print()
            elif cmd == 'end':
                cont = False
                print()
            elif cmd == 'help':
                print('\tCommands:')
                for i in commands:
                    print('\t\t{} - {}'.format(i, commands[i]))
                print()
            else:
                print('\nInvalid command. ', end='')

    def clear_board(self):
        """Kill all cell objects in self."""

        for row in range(self.height):
            for col in range(self.width):
                self.cell_at(row, col).die()

    def render_board(self, msg='', show_coords=False):
        """Render the current state of the board."""

        # Extra left padding if showing coordinates
        if show_coords:
            print(' ', end='')

        # Top of the board
        print('  ' + '┌' + '─' * (self.width*2 + 2) + '┐')

        # Print middle of the board
        for row in range(self.height-1, -1, -1):
            # Print row coordinates if applicable
            if show_coords:
                if row % 5 == 0:
                    print('{} '.format(str(row).rjust(2)), end='')
                else:
                    print('   ', end='')
            else:
                print('  ', end='')

            # Print left edge of the board
            print('│ ', end='')

            # Print the cell
            for col in range(self.width):
                # Creates checkerboard effect
                dark = (row + col) % 2 == 1

                # Print the state of the cell
                self.cell_at(row, col).render_cell(dark, end='')

            # Print right edge of the board
            print(' │', end='')

            # Print message on top row if it exists
            if row == self.width-1 and msg != '':
                print('    {}'.format(msg))
            else:
                print()

        # Print extra left padding if showing coordinates
        if show_coords:
            print(' ', end='')

        # Print bottom of the board
        print('  ' + '└' + '─' * (self.width*2 + 2) + '┘')

        # Print column coords if applicable
        if show_coords:
            if self.width > 99:
                # Rewrite this part if this becomes a problem
                raise ValueError('render_board() cannot currently handle board widths of 3 digits'
                                 'when printing col coordinates')

            if self.width > 9:
                # Print 2-digit coordinate numbers vertically

                # First and second digits of numbers
                top_line = ''
                bottom_line = ''
                for i in range(0, self.width, 5):
                    top_line += '{0:<10}'.format(str(i).ljust(2)[0])
                    bottom_line += '{0:<10}'.format(str(i).ljust(2)[1])
                print('     ' + top_line)
                print('      ' + bottom_line)
            else:
                # Print padding
                print('     ', end='')

                # Print numbers normally (horizontally)
                for i in range(0, self.width, 5):
                    print('{0:<10}'.format(i))

            print()

    def tick_board(self, tick=1):
        """Advance the board by given number of game ticks."""

        for i in range(tick):
            self.state = self.advance_all()

        self.tick += tick

    def cell_at(self, row, col):
        """Return Cell object at specified row and col."""

        return self.state[row][col]

    def advance_all(self):
        """Advance every cell on the board by one game tick."""

        # Create a deep copy of the current Board object
        new_board = copy.deepcopy(self)

        for row in range(self.height-1, -1, -1):
            for col in range(self.width):
                # The cell object at the current board position
                cell = self.cell_at(row, col)

                # Update the state of the cell in the new board
                if cell.should_live():
                    new_board.cell_at(row, col).live()
                else:
                    new_board.cell_at(row, col).die()

        return new_board.state

    def row_in_range(self, row: int) -> bool:
        """True if row is in range of the board height."""

        return 0 <= row < self.height

    def col_in_range(self, col: int) -> bool:
        """True if col is in range of the board width."""

        return 0 <= col < self.width

    def coord_in_range(self, coord: tuple) -> bool:
        """True if items in given (col, row) coordinate contains valid indices of the board.

        Credit to Patrick Artner:
            https://stackoverflow.com/questions/53419606/validating-user-input-with-regex

        """

        return all(isinstance(num, int) for num in coord) \
            and self.row_in_range(coord[0]) \
            and self.col_in_range(coord[1])


class Cell:

    # Characters used to print alive and dead cell states
    alive_char = '█'
    dead_char = '░'
    dead_char_dark = '▒'

    def __init__(self, state: bool, row, col, board: Board, neighbors=None):
        """Create a cell object."""

        self.state = state
        self.row = row
        self.col = col
        self.board = board
        self.neighbors = neighbors

    def render_cell(self, dark=False, end=''):
        """Print character showing aliveness of the given cell.

        Optional arg dark returns darker character for dead cells.

        """

        if self.is_alive():
            print(Cell.alive_char*2, end=end)
        elif dark:
            print(Cell.dead_char_dark*2, end=end)
        else:
            print(Cell.dead_char*2, end=end)

    def is_alive(self) -> bool:
        """Return True if cell is alive."""

        return self.state

    def is_dead(self) -> bool:
        """Return True if cell is dead."""

        return not self.state

    @staticmethod
    def num_alive(cells):
        """Return number of alive cell objects in given iterable."""

        total = 0
        for cell in cells:
            total += cell.is_alive()

        return total

    def live(self):
        """Make the given cell alive."""

        self.state = True

    def die(self):
        """Make the given cell dead."""

        self.state = False

    def set_alive_neighbors(self):
        """Set the number of alive cells adjacent to self."""

        # State and values in state must have length
        assert self.board.width > 0
        assert self.board.height > 0

        # Row and col are in bounds
        assert self.board.row_in_range(self.row)
        assert self.board.col_in_range(self.col)

        # Sets the neighbors to sum depending on whether the cell at state[row][col]
        # is on one of the 4 edges of the board or is a corner of the board.
        # NOTE: The board is rendered bottom to top, so state[0] is the row that
        # will be printed on the bottom.
        if self.col == 0:
            # Cell is on left edge
            if self.row == len(self.board.state)-1:
                # Cell rendered in top left corner
                check_cells = ((+1, +0),  # right
                               (+1, -1),  # down right
                               (+0, -1))  # down
            elif self.row == 0:
                # Cell rendered in bottom left corner
                check_cells = ((+0, +1),  # top
                               (+1, +1),  # top right
                               (+1, +0))  # right
            else:
                # Cell is on left edge
                check_cells = ((+0, +1),  # top
                               (+1, +1),  # top right
                               (+1, +0),  # right
                               (+1, -1),  # down right
                               (+0, -1))  # down
        elif self.col == len(self.board.state[0])-1:
            # Cell is on right edge
            if self.row == len(self.board.state)-1:
                # Cell rendered in top right corner
                check_cells = ((+0, -1),  # down
                               (-1, -1),  # down left
                               (-1, +0))  # left
            elif self.row == 0:
                # Cell rendered in bottom right corner
                check_cells = ((-1, +1),  # top left
                               (+0, +1),  # top
                               (-1, +0))  # left
            else:
                # Cell is on right edge
                check_cells = ((-1, +1),  # top left
                               (+0, +1),  # top
                               (+0, -1),  # down
                               (-1, -1),  # down left
                               (-1, +0))  # left
        elif self.row == len(self.board.state)-1:
            # Cell rendered in top edge, but is not a corner
            check_cells = ((+1, +0),  # right
                           (+1, -1),  # down right
                           (+0, -1),  # down
                           (-1, -1),  # down left
                           (-1, +0))  # left
        elif self.row == 0:
            # Cell rendered in bottom edge, but is not a corner
            check_cells = ((-1, +1),  # top left
                           (+0, +1),  # top
                           (+1, +1),  # top right
                           (+1, +0),  # right
                           (-1, +0))  # left
        else:
            # Cell is not on an edge of the board
            check_cells = ((-1, +1),  # top left
                           (+0, +1),  # top
                           (+1, +1),  # top right
                           (+1, +0),  # right
                           (+1, -1),  # down right
                           (+0, -1),  # down
                           (-1, -1),  # down left
                           (-1, +0))  # left

        # Make list of neighboring cell objects
        neighbors = []
        for t in check_cells:
            neighbors.append(self.board.cell_at(self.row+t[1], self.col+t[0]))

        self.neighbors = neighbors

    def should_live(self) -> bool:
        """Determine if cell should be alive next game tick."""

        self.set_alive_neighbors()
        alive_neighbors = self.num_alive(self.neighbors)

        # Assume state doesn't change
        new_state = self.state

        # Check to see if it should
        if self.is_alive():
            # Cell is alive
            if alive_neighbors < 2:
                # Die by underpopulation
                new_state = False
            elif alive_neighbors > 3:
                # Die by overpopulation
                new_state = False
        else:
            # Cell is dead
            if alive_neighbors == 3:
                # Live by reproduction
                new_state = True

        return new_state


def game_loop(board: Board):
    """Tick the board until user enters "end" sentinel."""

    # # Set up window data
    # pygame.init()
    # win = pygame.display.set_mode((500, 500))
    # pygame.display.set_caption('Game of Life')
    # millis_per_tick = 100
    #
    # # Main game loop
    # run = True
    # while run:
    #     pygame.time.delay(millis_per_tick)
    #
    #     for event in pygame.event.get():
    #         if event.type == pygame.QUIT:
    #             run = False
    #
    #     pygame.draw.rect(win, (50, 60, 60), )
    # pygame.quit()

    cont = True
    while cont:
        # Flush the terminal
        # os.system('cls||clear')

        # Render the board and wait
        board.render_board('Tick: {}'.format(board.tick))
        prompt = input('Press enter to continue or type end to end:\n>>> ').lower()

        # Tick board unless user types end
        if prompt != 'end':
            board.tick_board()
        else:
            cont = False


def try_int(s: str):
    """Return an int if possible, else the original value."""

    if s.isdigit():
        return int(s)
    else:
        return s


def prompt_board_size() -> (int, int):
    """Prompt for and return height, width ints for a Board object."""

    # Get board height
    height = input('Enter board height:\n>>> ')
    while not height.isdigit():
        height = input('Invalid input. Enter board height:\n>>> ')

        try:
            if int(height) > 48:
                reset_height = input('Boards greater than 48 squares might not fit on your'
                                     'screen. Would you like to set the board height to 48'
                                     'squares? (y/n)\n>>> ').lower()
                while reset_height in ['y', 'n']:
                    reset_height = input('Enter "y" or "n":\n>>> ')

                if reset_height == 'y':
                    height = 48
        except ValueError:
            pass

    print('\tHeight set at {}.\n'.format(height))

    # Get board width
    width = input('Enter board width:\n>>> ')
    while not width.isdigit():
        width = input('Invalid input. Enter board height:\n>>> ')

        try:
            if int(width) > 48:
                reset_width = input('Boards greater than 48 squares might not fit on your'
                                    'screen. Would you like to set the board height to 48'
                                    'squares? (y/n)\n>>> ').lower()
                while reset_width in ['y', 'n']:
                    reset_width = input('Enter "y" or "n":\n>>> ')

                if reset_width == 'y':
                    width = 48
        except ValueError:
            pass

    print('\tWidth set at {}.\n'.format(width))

    return int(height), int(width)


def main():
    # Get board size
    height, width = prompt_board_size()

    # Make the board
    board = Board(0, height, width)

    # Set up the board
    print('Setting up board...')
    # time.sleep(1)
    board.render_board('[Board Editing Mode]', True)
    board.set_board_states()

    # Tick until user enters 'end'
    game_loop(board)


if __name__ == '__main__':
    main()
