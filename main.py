import re
import os
import time
import copy
from typing import List
# import pygame


class Board:
    def __init__(self, tick: int, height, width, state: List[List] = None):
        """Initialize board object."""

        if state is None:
            state = [[Cell(False, row, col, self) for col in range(width)] for row in range(height)]
        else:
            assert len(state) == height
            assert len(state[0]) == width

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
        s += '\n\tstate: <state:List {} :\n\t\t'.format(hex(id(self.state)))
        # Print ids of all cell objects
        for row in range(self.height):
            s += '\n\t\t<row:List {} : '.format(hex(id(self.state[row])))
            s += ', '.join(['\n\t\t\t<cell:Cell {}>'.format(hex(id(self.cell_at(row, col))))
                            for col in range(self.width)])
            s += '\n\t\t>'
            if row != self.height-1:
                s += ','

        s += '>'

        return s

    def set_board_states(self, flush=False, msg=''):
        """Prompt user to set alive cells in board."""

        commands = {'live': 'turn on cells in the board',
                    'die': 'turn off cells in the board',
                    'clear': 'clear the board',
                    'done': 'exit board setup mode',
                    'help': 'list available commands'}

        def valid_cell_format(s):
            """Determine if string follows the format "(a, b), (c, d), ... ".

            Credit to Patrick Artner:
                https://stackoverflow.com/questions/53419606/validating-user-input-with-regex

            """

            return re.match(r'^\s*([^,]+,[^,]+\)\s*(?:,\s*\([^,]+,[^,]+\))*)\s*$', s)

        def separate_valids(s):
            """Return 2 lists of tuples containing the valid/invalid coordinates in s respectively.

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

        # Show the board
        self.render_board('[Board Editing Mode]', '', True, True)

        # Show message if it exists
        if msg != '':
            print(msg)

        # Change the board while the user wants to
        cont = True
        while cont:
            # Get user command
            cmd = input('Enter a command or type help for more info:\n>>> ').lower()

            # Execute commands
            if cmd in ['live', 'die']:
                print()

                cont_ = True
                while cont_:
                    coords = input('Enter cells to {} as (x,y) coordinates separated by commas:'
                                   '\n>>> '.format(cmd))

                    try:
                        # Get list of coordinates as tuples, like [(1,3),(2,3), ...]
                        valid_coords, invalid_coords = separate_valids(coords)
                    except ValueError as e:
                        # Coords were not entered in a valid format
                        print('\n{} '.format(e), end='')

                    else:
                        # Entered coords are of integers and are in range
                        # Print the valid coords
                        msg_below = ''
                        for tup in valid_coords:
                            col, row = tup[0], tup[1]
                            if cmd == 'live':
                                if self.cell_at(row, col).is_alive():
                                    msg_below += '\tCell at ({}, {}) was already ' \
                                                'alive.\n'.format(col, row)
                                else:
                                    self.cell_at(row, col).live()
                                    msg_below += '\tRevived cell at ({}, {}).\n'.format(col, row)
                            else:
                                if self.cell_at(row, col).is_dead():
                                    msg_below += '\tCell at ({}, {}) was already ' \
                                                'dead.\n'.format(col, row)
                                else:
                                    self.cell_at(row, col).die()
                                    msg_below += '\tKilled cell at ({}, {}).\n'.format(col, row)
                        if len(invalid_coords) != 0:
                            # Print the invalid coords
                            msg_below += '\n\tThe following coordinates were invalid:'
                            for tup in invalid_coords:
                                col, row = tup[0], tup[1]
                                msg_below += '\n\t\t({}, {})'.format(col, row)
                            msg_below += '\n'

                        # Clear the terminal if applicable
                        if flush:
                            flush_terminal()

                        # Show the board
                        self.render_board('[Board Editing Mode]', msg_below, True, True)

                        # Break from the loop
                        cont_ = False

                print()
            elif cmd == 'clear':
                self.clear_board()

                # Clear the terminal if applicable
                if flush:
                    flush_terminal()

                # Show the board
                self.render_board('[Board Editing Mode]', 'Board cleared.\n\n', True, True)
            elif cmd == 'done':
                cont = False
                print()
            elif cmd == 'help':
                print('\tCommands:')
                for i in commands:
                    print('\t\t"{}" - {}'.format(i, commands[i]))
                print()
            else:
                print('\nInvalid command. ', end='')

    def clear_board(self):
        """Kill all cell objects in self."""

        for row in range(self.height):
            for col in range(self.width):
                self.cell_at(row, col).die()

    def render_board(self, msg_side='', msg_below='', show_coords=False, checker=False):
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
                # Creates checkerboard effect if applicable
                dark = (row + col) % 2 == 1 and checker

                # Print the state of the cell
                self.cell_at(row, col).render_cell(dark, end='')

            # Print right edge of the board
            print(' │', end='')

            # Print message on top row if it exists
            if row == self.height-1 and msg_side != '':
                print('    {}'.format(msg_side))
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
                raise ValueError('render_board() cannot currently handle board widths of 3 digits '
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
                    print('{0:<10}'.format(i), end='')

            print()
        if msg_below != '':
            print(msg_below, end='')

    def tick_board(self, num_ticks=1, flush=True, delay=0, show_ticks=True):
        """Advance the board by given number of game ticks."""

        # Convert milliseconds to seconds
        delay /= 1000

        for i in range(num_ticks):
            # Update board
            self.advance_all()

            # Clear terminal if applicable
            if flush:
                flush_terminal()

            # Render board
            self.tick += 1
            msg = ''
            if show_ticks:
                msg = 'Tick: {}'.format(self.tick)
            self.render_board(msg)

            # Wait
            time.sleep(delay)

        if show_ticks:
            print('Advanced the board by {} ticks.\n'.format(num_ticks))
        else:
            print()

    def cell_at(self, row, col):
        """Return Cell object at specified row and col."""

        return self.state[row][col]

    def advance_all(self):
        """Advance every cell on the board by one game tick."""

        # Create a deep copy of the current Board object
        new_board = copy.deepcopy(self)

        # Update states in the new board where applicable
        for row in range(self.height-1, -1, -1):
            for col in range(self.width):
                # The cell object at the current board position
                cell = self.cell_at(row, col)

                # Update the state of the cell in the new board
                if cell.should_live():
                    new_board.cell_at(row, col).live()
                else:
                    new_board.cell_at(row, col).die()

        self.state = copy.deepcopy(new_board.state)

        # Get rid of the temporary board
        del new_board

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

        # Create the list of neighboring cell objects, top-to-bottom and left-to-right
        neighbors = []
        for try_row in [-1, +0, +1]:
            for try_col in [-1, +0, +1]:
                # Skip the cell itself, (+0, +0)
                if not try_row == try_col == 0:
                    # Add the neighboring cell
                    # When self.row + try_row == self.board.height,
                    # (self.row+try_row) % self.board.height == 0.
                    # This creates the toroidal board wrapping effect.
                    neighbors += self.board.cell_at((self.row+try_row) % self.board.height,
                                                    (self.col+try_col) & self.board.height)

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


def game_loop(board: Board, flush=False):
    """Tick the board until user enters "end" sentinel."""

    commands = {'': 'update board to the next tick',
                'tick': 'update the board by some number of ticks',
                'edit': 'edit current state of the board',
                'end': 'quit the program',
                'help': 'list available commands'}

    cont = True
    refresh_board = True
    while cont:
        if refresh_board:
            # Clear the terminal if applicable
            if flush:
                flush_terminal()

            # Render the board and wait
            board.render_board('[GAME OF LIFE]  Tick: {}'.format(board.tick))

        prompt = input('\nPress enter to tick the board or type help for more info:\n'
                       '>>> ').lower().strip()

        # Validate command
        while prompt not in commands:
            prompt = input('\nUnknown command. Press enter to continue or type help for '
                           'more info:\n>>> ').lower().strip()

        # Execute command
        if prompt == '':
            # Tick board by 1
            board.tick_board()

            refresh_board = True
        elif prompt == 'edit':
            # Edit state of the board
            board.set_board_states()
            print()

            refresh_board = True
        elif prompt == 'tick':
            # Tick the board given number of times
            num_ticks = input('Enter number of ticks:\n>>> ')

            # Validate number of ticks
            while not num_ticks.isdigit():
                num_ticks = input('Invalid number. Enter number of ticks:\n>>> ')
            num_ticks = int(num_ticks)

            sleep_time = input('Enter milliseconds to pause between each tick (default 100):\n>>> ')

            while not sleep_time.isdigit():
                sleep_time = input('Invalid number. Enter milliseconds to pause between each tick '
                                   '(default 100):\n>>> ')

            sleep_time = int(sleep_time)

            # Tick the board
            board.tick_board(num_ticks, True, sleep_time, True)

            refresh_board = True
        elif prompt == 'end':
            # Break out of game loop
            cont = False
            print()
        elif prompt == 'help':
            # Show available commands
            print('\tCommands:')
            for i in commands:
                if i == '':
                    print('\t\tpress enter - {}'.format(commands[i]))
                else:
                    print('\t\t{} - {}'.format(i, commands[i]))
            print()

            refresh_board = False


def try_int(s: str):
    """Return an int if possible, else the original value."""

    if s.isdigit():
        return int(s)
    else:
        return s


def flush_terminal():
    """Clear output on the terminal."""

    os.system('cls||clear')


def prompt_for_board_size() -> (int, int):
    """Prompt for and return height, width ints for a Board object."""

    # Get board height
    height = input('Enter board height:\n>>> ')
    while not height.isdigit():
        height = input('Invalid input. Enter board height:\n>>> ')

        try:
            if int(height) > 40:
                reset_height = input('Boards greater than 40 squares high might not fit on your'
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
                                    'screen. Would you like to set the board width to 48'
                                    'squares? (y/n)\n>>> ').lower()
                while reset_width in ['y', 'n']:
                    reset_width = input('Enter "y" or "n":\n>>> ')

                if reset_width == 'y':
                    width = 48
        except ValueError:
            pass

    print('\tWidth set at {}.\n'.format(width))

    return int(height), int(width)


def welcome():
    """Show welcome message."""

    # Os will be living cells, spaces to dead cells
    welcome_art = [
        '                                                                      ',
        '                                                                      ',
        '   OOOOO OOOOO O   O OOOOO    OOOOO OOOOO   O     OOOOO OOOOO OOOOO   ',
        '   O     O   O OO OO O        O   O O       O       O   O     O       ',
        '   O  OO OOOOO O O O OOOO     O   O OOOO    O       O   OOOO  OOOO    ',
        '   O   O O   O O   O O        O   O O       O       O   O     O       ',
        '   OOOOO O   O O   O OOOOO    OOOOO O       OOOOO OOOOO O     OOOOO   ',
        '                                                                      ',
        '                                                                      '
    ][::-1]

    # Create the board the state from welcome_art
    welcome_board = Board(0, len(welcome_art), len(welcome_art[0]))
    for row in range(len(welcome_art)-1, -1, -1):
        for col in range(len(welcome_art[0])):
            if welcome_art[row][col] == 'O':
                welcome_board.cell_at(row, col).live()

    # Clear terminal before printing board
    flush_terminal()

    welcome_board.render_board()
    time.sleep(2)
    welcome_board.tick_board(110, True, 50, False)

    time.sleep(0.5)
    print('Welcome to the Game of Life! Let\'s set up your board.\n')


def main():
    welcome()

    cont = True
    while cont:
        # Get board size
        height, width = prompt_for_board_size()

        # Make the board
        print('Creating your board...')
        board = Board(0, height, width)

        time.sleep(1)

        # User can set up the board
        flush_terminal()
        board.set_board_states(True, 'Board created!\n')

        # Ticks until user enters 'end'
        game_loop(board, True)


if __name__ == '__main__':
    main()
