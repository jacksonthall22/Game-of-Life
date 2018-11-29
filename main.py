import re
import os
import time
import copy
from typing import List
from bitstring import BitArray, CreationError
# import pygame


class Board:

    alive_char = '█'
    dead_char = '░'
    dead_char_dark = '▒'

    def __init__(self, tick, height, width, state: List[List[BitArray]] = None):
        """Initialize Board object."""

        if state is None:
            state = [BitArray('0b' + '0' * width) for _ in range(height)]
        else:
            # Confirm height and width are correct if state is defined
            assert len(state) == height
            assert all([len(row) == len(state[0]) == width for row in state])

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
        s += '\n\tstate:'
        s += '\n\t\t<'
        for row in self.state:
            # Print binary representation of BitArray object
            s += '\n\t\t\t{}'.format(row.bin)
        s += '\n\t\t>'

        return s

    def set_board_states(self, flush=False, msg=''):
        """Prompt user to set alive cells in parent_board."""

        commands = {'live': 'turn on cells in the parent_board',
                    'die': 'turn off cells in the parent_board',
                    'clear': 'clear the parent_board',
                    'done': 'exit parent_board setup mode',
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

        # Show the parent_board
        self.render_board('[Board Editing Mode]', '', True, True)

        # Show message if it exists
        if msg != '':
            print(msg)

        # Edit the parent_board while the user wants to
        cont = True
        while cont:
            # Get user command
            cmd = input('Enter a command or type help for more info:\n>>> ').lower()

            # Execute commands
            if cmd in ['live', 'die']:
                print()

                _cont = True
                while _cont:
                    coords = input('Enter cells to {} as (x,y) coordinates separated by commas'
                                   'or type "cancel":'
                                   '\n>>> '.format(cmd))

                    if coords.lower() != 'cancel':
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
                                    if self.is_alive(row, col):
                                        msg_below += '\tCell at ({}, {}) was already ' \
                                                    'alive.\n'.format(col, row)
                                    else:
                                        self.live(row, col)
                                        msg_below += '\tRevived cell at ({}, {}).\n'.format(col, row)
                                else:
                                    if self.is_dead(row, col):
                                        msg_below += '\tCell at ({}, {}) was already ' \
                                                    'dead.\n'.format(col, row)
                                    else:
                                        self.die(row, col)
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
                            _cont = False

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
                self.die(row, col)

    @staticmethod
    def get_board_from_state(state_list: List[str]):
        """Return a list of BitArrays from list of strings of 1s and 0s."""

        # Create the list
        new_state = []
        for row in range(len(state_list)):
            # Will raise CreationError if row is empty or contains
            # anything except 0s and 1s
            new_state.append(BitArray('0b' + state_list[row]))

        return new_state

    @staticmethod
    def get_blank_board(height, width):
        """Return a list of BitArrays initialized to 0."""

        # Create the list
        new_state = []
        for row in range(height):
            new_state.append(BitArray('0b' + '0'*width))

        return new_state

    def render_cell(self, row, col, dark, end=''):
        """Print the current state of the cell."""

        # Prints characters twice in a row so they appear as squares in the terminal
        if self.is_alive(row, col):
            print(Board.alive_char*2, end=end)
        elif dark:
            print(Board.dead_char_dark*2, end=end)
        else:
            print(Board.dead_char*2, end=end)

    def render_board(self, msg_side='', msg_below='', show_coords=False, checker=False):
        """Render the current state of the board.

        Arguments:
            msg_side: String printed to the right of board at the top row.
            msg_below: String printed below board (with end='').
            show_coords: Bool indicating whether board should display
                coordinates at left and bottom of board.
            checker: Bool indicating whether board should be rendered
                with a checkerboard background.

        """

        # Extra left padding if showing coordinates
        if show_coords:
            print(' ', end='')

        # Top of the board
        print('  ' + '┌' + '─' * (self.width*2 + 2) + '┐')

        # Print middle of the board
        for row in range(self.height-1, -1, -1):
            # Print row coordinates if applicable
            if show_coords:
                if (row+1) % 5 == 0:
                    print('{} '.format(str(row+1).rjust(2)), end='')
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
                self.render_cell(row, col, dark)

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
                # First and second digits of col coords should be printed vertically
                top_line = ''
                bottom_line = ''
                for i in range(5, self.width+1, 5):
                    top_line += '{0:<10}'.format(str(i).ljust(2)[0])
                    bottom_line += '{0:<10}'.format(str(i).ljust(2)[1])

                # Print the two lines with leading 0 coordinate
                print(' 0           ' + top_line)
                print('              ' + bottom_line)
            else:
                # Col numbers can be printed normally (horizontally)
                top_line = ''
                for i in range(5, self.width+1, 5):
                    top_line += '{0:<10}'.format(str(i).ljust(2)[0])

                # Print the line with leading 0 coordinate
                print(' 0           ' + top_line)

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
        """Return state of the cell at given coordinates.

        This is equivalent to is_alive(); included for semantic clarity.

        """

        return self.state[row][col]

    def next_state(self, row, col) -> bool:
        """Return the correct state of given cell at the next game tick."""

        # Set next state depending on number of living neighbors
        neighbors = self.num_alive_neighbors(row, col)
        if self.is_alive(row, col):
            # Cell is alive
            if neighbors < 2:
                # Die by underpopulation
                should_live = False
            elif neighbors > 3:
                # Die by overpopulation
                should_live = False
            else:
                # Stay alive with 2 or 3 neighbors
                should_live = True
        else:
            # Cell is dead
            if neighbors == 3:
                # Live by reproduction
                should_live = True
            else:
                # Stay dead
                should_live = False

        return should_live

    def is_alive(self, row, col):
        """Return true if cell at given coordinates is true."""

        return self.state[row][col]

    def is_dead(self, row, col):
        """Return true if cell at given coordinates is false."""

        return not self.state[row][col]

    def live(self, row, col):
        """Make the cell at the given coordinates alive."""

        self.state[row][col] = True

    def die(self, row, col):
        """Make the cell at the given coordinates dead."""

        self.state[row][col] = False

    def advance_all(self):
        """Advance every cell on the board by one game tick."""

        # Create lists of cells to change after all cells are evaluated
        # If cells were changed immediately, number of neighbors would be
        # measured inaccurately
        should_live = []
        should_die = []

        # Update states in the new board where applicable
        for row in range(self.height):
            for col in range(self.width):
                # Update the state of the cell at these coordinates
                if self.next_state(row, col):
                    should_live.append((row, col))
                else:
                    should_die.append((row, col))

        # Update the cells
        for coord in should_live:
            self.live(coord[0], coord[1])

        for coord in should_die:
            self.die(coord[0], coord[1])

    def num_alive_neighbors(self, row, col) -> int:
        """Return number of alive cells adjacent to cell on given board at given coordinates."""

        # Assumes state has width and length
        state_height = len(self.state)
        state_width = len(self.state[0])

        # Sum the neighboring cells, top-to-bottom and left-to-right
        num_neighbors = 0
        for try_row in [-1, +0, +1]:
            for try_col in [-1, +0, +1]:
                # Skip the cell itself, (+0, +0)
                if not try_row == try_col == 0:
                    # Add the neighboring cell to the total (False is 0, True is 1)
                    # NOTE: (self.row+try_row) % self.parent_board.height == 0.
                    # creates a toroidal wrapping effect.
                    num_neighbors += self.cell_at(
                        (row + try_row) % state_height,
                        (col + try_col) % state_width
                    )

        return num_neighbors

    def row_in_range(self, row) -> bool:
        """Return true if row is in range of the board height."""

        return 0 <= row < self.height

    def col_in_range(self, col) -> bool:
        """Return true if col is in range of the board width."""

        return 0 <= col < self.width

    def coord_in_range(self, coord: tuple) -> bool:
        """Return true if items in given (col, row) coordinate contains valid indices of the board.

        Credit to Patrick Artner:
            https://stackoverflow.com/questions/53419606/validating-user-input-with-regex

        """

        return all(isinstance(num, int) for num in coord) \
            and self.row_in_range(coord[0]) \
            and self.col_in_range(coord[1])


def game_loop(board: Board, flush=False):
    """Tick Board until user enters "end" sentinel."""

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
    """Show Game of Life welcome message and animation."""

    # Spells 'GAME OF LIFE'
    welcome_art = [
        '0000000000000000000000000000000000000000000000000000000000000000000000',
        '0000000000000000000000000000000000000000000000000000000000000000000000',
        '0001111101111101000101111100001111101111100010000011111011111011111000',
        '0001000001000101101101000000001000101000000010000000100010000010000000',
        '0001001101111101010101111000001000101111000010000000100011110011110000',
        '0001000101000101000101000000001000101000000010000000100010000010000000',
        '0001111101000101000101111100001111101000000011111011111010000011111000',
        '0000000000000000000000000000000000000000000000000000000000000000000000',
        '0000000000000000000000000000000000000000000000000000000000000000000000'
    ][::-1]

    # Convert welcome_art to a list of BitArray objects
    welcome_state = Board.get_board_from_state(welcome_art)

    time.sleep(0.5)
    print('Welcome to the Game of Life! Let\'s set up your board.\n')

    # Show and animate the board
    welcome_board = Board(0, len(welcome_state), len(welcome_state[0]), welcome_state)
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

        # Prompt user to set up the board
        flush_terminal()
        board.set_board_states(True, 'Board created!\n')

        # Ticks until user enters 'end'
        game_loop(board, True)


if __name__ == '__main__':
    main()
