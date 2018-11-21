import re
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
                    'end': 'done setting up board',
                    'help': 'list available commands'}

        cont = True
        while cont:
            cmd = input('\nEnter a command or type help for help:\n>>> ').lower()

            if cmd in ['live', 'die']:
                coords = input('Enter cells to {} as (x,y) coordinates separated by spaces:'
                               '\n>>> '.format(cmd))

                # Make each entered cell alive
                for tuple_str in coords.split():
                    [col, row] = [num for num in tuple_str[1:len(tuple_str)-1].split(',')]
                    print('test col, row: {}, {}'.format(col, row))
                    try:
                        # Ensure col, row are integers
                        col = int(col)
                        row = int(row)
                    except ValueError:
                        # Cells are non-integers
                        print('\tCell ({},{}) invalid: coordinates must be integers.'
                              ''.format(col, row))
                    else:
                        if not 0 <= col < self.width and not 0 <= row < self.height:
                            # Coords are integers but out of range
                            print('\tCell ({},{}) invalid: coordinates are out of range.'
                                  ''.format(col, row))
                        else:
                            # Cells are integers and in range
                            if cmd == 'live':
                                self.cell_at(row, col).live()
                                print('\tRevived cell at ({}, {}).'.format(col, row))
                            else:
                                self.cell_at(row, col).live()
                                print('\tKilled cell at ({}, {})'.format(col, row))
            elif cmd == 'end':
                cont = False
            elif cmd == 'help':
                print('\tCommands:')
                for i in commands:
                    print('\t\t{} - {}'.format(i, commands[i]))
            else:
                print('Invalid command. ', end='')

            print()

    def render_board(self):
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
            print(' │')

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

    @staticmethod
    def row_in_range(board: Board, row: int) -> bool:
        """True if row is in range of the board height."""

        return 0 <= row < board.height

    @staticmethod
    def col_in_range(board: Board, col: int) -> bool:
        """True if col is in range of the board width."""

        return 0 <= col < board.width

    @staticmethod
    def coord_in_range(board: Board, coord: tuple) -> bool:
        """True if items in given (col, row) coordinate contains valid indices of the board."""

        return all(isinstance(num, int) for num in coord) \
               and board.row_in_range(board, coord[0]) \
               and board.col_in_range(board, coord[1])

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
        """Return True iff cell is alive."""

        return self.state

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


def game_loop():
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
    pass


def try_int(s: str):
    """Return an int if possible, else the original value."""

    if s.isdigit():
        return int(s)
    else:
        return s


def main():
    board = Board(0, 15, 15)
    board.render_board()
    board.set_board_states()
    board.render_board()
    input('Press enter to continue.')
    board.tick_board()
    board.render_board()
    input('Press enter to continue.')
    board.tick_board()
    board.render_board()


if __name__ == '__main__':
    main()
