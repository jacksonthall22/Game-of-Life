import re
import os
import time
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
        s += '\n\tstate:'
        for row in self.state:
            s += '\n\t\t{}'.format(row)

        return s

    def set_board_states(self):
        """Prompt user to set alive cells in board."""

        commands = {'live': 'turn on cells in the board',
                    'die': 'turn off cells in the board',
                    'show': 'show the state of the board',
                    'end': 'done setting up board',
                    'help': 'list available commands'}

        def valid_cell_format(s):
            """Determine if s follows the format "(a, b), (c, d), ... ".

            Credit to Patrick Artner:
                https://stackoverflow.com/questions/53419606/validating-user-input-with-regex

            """

            return re.match(r'^\s*([^,]+,[^,]\)\s*(?:,\s*\([^,]+,[^,]\))*)\s*$', s)

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
                # # Make each entered cell alive
                # for tuple_str in coords.split():
                #     [col, row] = [num for num in tuple_str[1:len(tuple_str)-1].split(',')]
                #     print('test col, row: {}, {}'.format(col, row))
                #     try:
                #         # Ensure col, row are integers
                #         col = int(col)
                #         row = int(row)
                #     except ValueError:
                #         # Cells are non-integers
                #         print('\tCell ({},{}) invalid: coordinates must be integers.'
                #               ''.format(col, row))
                #     else:
                #         if not 0 <= col < self.width and not 0 <= row < self.height:
                #             # Coords are integers but out of range
                #             print('\tCell ({},{}) invalid: coordinates are out of range.'
                #                   ''.format(col, row))
                #         else:
                #             # Cells are integers and in range
                #             if cmd == 'live':
                #                 self.cell_at(row, col).live()
                #                 print('\tRevived cell at ({}, {}).'.format(col, row))
                #             else:
                #                 self.cell_at(row, col).live()
                #                 print('\tKilled cell at ({}, {})'.format(col, row))
            elif cmd == 'show':
                self.render_board()
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

    def render_board(self, msg=''):
        """Render the current state of the board."""

        # Top of the board
        print('┌' + '─' * (self.width*2 + 2) + '┐')

        # Middle of the board
        for row in range(self.height-1, -1, -1):
            # Left edge of the board
            print('│ ', end='')
            for col in range(self.width):
                # Print the state of the cell
                print(self.cell_at(row, col), end='')

            # Right edge of the board
            print(' │', end='')

            # Print message on top row if it exists
            if row == self.width-1 and msg != '':
                print('    {}'.format(msg))
            else:
                print()

        # Bottom of the board
        print('└' + '─' * (self.width*2 + 2) + '┘')

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

        # Create a copy of the current Board object
        new_board = Board(self.tick, self.height, self.width, self.state.copy())

        for row in range(self.height-1, -1, -1):
            for col in range(self.width):
                # The cell object at this board position
                cell = self.cell_at(row, col)

                # Update the state of the cell in new_board
                if cell.should_live():
                    cell.live()
                else:
                    cell.die()

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

    def __init__(self, state: bool, row, col, board: Board):
        """Create a cell object."""

        self.state = state
        self.row = row
        self.col = col
        self.board = board

    def __str__(self) -> str:
        """Print character showing aliveness of the given cell."""

        if self.is_alive():
            return Cell.alive_char * 2
        else:
            return Cell.dead_char * 2

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

    def set_alive_neighbors(self, board: Board):
        """Return number of alive cells adjacent to the given cell."""

        # Shorten variables for reference
        state = board.state
        row = self.row
        col = self.col

        # State and values in state must have length
        assert len(state) > 0
        assert len(state[0]) > 0

        # Row and col are in bounds
        assert 0 <= row < len(state)
        assert 0 <= col < len(state[0])

        # Sets neighbors differently depending on whether the cell at state[row][col]
        # is on one of the 4 edges of the board or is a corner of the board
        # NOTE: The board is rendered bottom to top, so state[0] is the row that
        # will be printed on the bottom.
        if col == 0:
            # Cell is on left edge
            if row == 0:
                # Cell is in bottom left corner
                top = state[row + 1][col]
                top_right = state[row + 1][col + 1]
                right = state[row][col + 1]

                neighbors = Cell.num_alive([top, top_right, right])
            elif row == len(state)-1:
                # Cell is in top left corner
                right = state[row][col + 1]
                down_right = state[row - 1][col + 1]
                down = state[row - 1][col]

                neighbors = Cell.num_alive([right, down_right, down])
            else:
                # Cell is on left edge, but not a corner
                top = state[row + 1][col]
                top_right = state[row + 1][col + 1]
                right = state[row][col + 1]
                down_right = state[row - 1][col + 1]
                down = state[row - 1][col]

                neighbors = Cell.num_alive([top, top_right, right, down_right, down])
        elif col == len(state[0])-1:
            # Cell is on right edge
            if row == 0:
                # Cell is in bottom right corner
                left = state[row][col - 1]
                top_left = state[row + 1][col - 1]
                top = state[row + 1][col]

                neighbors = Cell.num_alive([left, top_left, top])
            elif row == len(state)-1:
                # Cell is in top right corner
                down = state[row - 1][col]
                down_left = state[row - 1][col - 1]
                left = state[row][col - 1]

                neighbors = Cell.num_alive([down, down_left, left])
            else:
                # Cell is on right edge, but not a corner
                down = state[row - 1][col]
                down_left = state[row - 1][col - 1]
                left = state[row][col - 1]
                top_left = state[row + 1][col - 1]
                top = state[row + 1][col]

                neighbors = Cell.num_alive([down, down_left, left, top_left, top])
        elif row == 0:
            # Cell is on bottom edge, but not a corner
            left = state[row][col - 1]
            top_left = state[row + 1][col - 1]
            top = state[row + 1][col]
            top_right = state[row + 1][col + 1]
            right = state[row][col + 1]

            neighbors = Cell.num_alive([left, top_left, top, top_right, right])
        elif row == len(state)-1:
            # Cell is on top edge, but nor a corner
            right = state[row][col + 1]
            down_right = state[row - 1][col + 1]
            down = state[row - 1][col]
            down_left = state[row - 1][col - 1]
            left = state[row][col - 1]

            neighbors = Cell.num_alive([right, down_right, down, down_left, left])
        else:
            # Cell is not on an edge of the board
            top_left = state[row + 1][col - 1]
            top = state[row + 1][col]
            top_right = state[row + 1][col + 1]
            right = state[row][col + 1]
            down_right = state[row - 1][col + 1]
            down = state[row - 1][col]
            down_left = state[row - 1][col - 1]
            left = state[row][col - 1]

            neighbors = Cell.num_alive(
                [top_left, top, top_right, right, down_right, down, down_left, left])

        # Add neighbors property
        setattr(self, 'neighbors', neighbors)

    def should_live(self) -> bool:
        """Determine if cell should be alive next game tick."""

        self.set_alive_neighbors(self.board)

        # Assume state doesn't change
        new_state = self.state

        # Check to see if it should
        if self.is_alive():
            # Cell is alive
            if self.neighbors < 2:
                # Die by underpopulation
                new_state = False
            elif self.neighbors > 3:
                # Die by overpopulation
                new_state = False
        else:
            # Cell is dead
            if self.neighbors == 3:
                # Live by reproduction
                new_state = True

        return new_state


def game_loop(board: Board):
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
        os.system('cls||clear')

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
    time.sleep(1)
    board.render_board()
    board.set_board_states()

    # Tick until user enters 'end'
    game_loop(board)


if __name__ == '__main__':
    main()
