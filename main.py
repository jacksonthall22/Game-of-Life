import re
import os
import time
import random
import copy
from typing import List
from bitstring import BitArray, CreationError


class Board:

    alive_char = '█'
    dead_char = '░'
    dead_char_dark = '▒'

    def __init__(self, tick, height, width, state: List[List[BitArray]] = None):
        """Initialize Board object."""

        if state is None:
            state = copy.deepcopy(self.get_blank_board(height, width))
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

    def set_board_states(self, flush=True, msg=''):
        """Prompt user to set alive cells in the board."""

        commands = {'live': 'turn on cells in the board',
                    'die': 'turn off cells in the board',
                    'presets': 'show a list of preset patterns',
                    'randomize': 'randomize the cells in the board from a given density',
                    'clear': 'clear the board',
                    'cls': 're-render the board, removing command interactions',
                    'done': 'exit board setup mode',
                    'help': 'list available commands'}

        # Credit for preset patterns:
        # http://www.radicaleye.com/lifepage/#browse
        # and
        # https://bitstorm.org/gameoflife/
        presets = {
            'c/2 glider':
                {
                    'size': (3, 3),
                    'pattern': (
                        (1, 3), (2, 3), (3, 3), (3, 2), (2, 1)
                    )
                },
            'c/5 glider':
                {
                    'size': (26, 7),
                    'pattern': (
                        (12, 2), (20, 2), (6, 3), (7, 3), (9, 3), (11, 3),
                        (13, 3), (14, 3), (18, 3), (19, 3), (21, 3), (23, 3),
                        (25, 3), (26, 3), (3, 4), (4, 4), (5, 4), (7, 4), (9, 4),
                        (10, 4), (11, 4), (21, 4), (22, 4), (23, 4), (25, 4),
                        (27, 4), (28, 4), (29, 4), (3, 5), (7, 5), (9, 5),
                        (15, 5), (17, 5), (23, 5), (25, 5), (29, 5), (7, 6),
                        (8, 6), (15, 6), (17, 6), (24, 6), (25, 6), (4, 7),
                        (5, 7), (15, 7), (17, 7), (27, 7), (28, 7), (4, 8),
                        (5, 8), (7, 8), (8, 8), (24, 8), (25, 8), (27, 8),
                        (28, 8), (8, 9), (24, 9)
                    )
                },
            'c/3 puffer':
                {
                    'size': (47, 16),
                    'pattern': (
                        (25, 2), (29, 2), (42, 2), (24, 3), (26, 3), (28, 3), (30, 3),
                        (32, 3), (33, 3), (34, 3), (36, 3), (37, 3), (39, 3), (40, 3),
                        (41, 3), (42, 3), (44, 3), (45, 3), (46, 3), (48, 3), (49, 3),
                        (12, 4), (13, 4), (14, 4), (17, 4), (19, 4), (20, 4), (21, 4),
                        (23, 4), (28, 4), (30, 4), (36, 4), (37, 4), (39, 4), (40, 4),
                        (43, 4), (48, 4), (49, 4), (11, 5), (16, 5), (17, 5), (19, 5),
                        (20, 5), (26, 5), (28, 5), (29, 5), (32, 5), (34, 5), (36, 5),
                        (44, 5), (45, 5), (47, 5), (50, 5), (8, 6), (9, 6), (11, 6),
                        (18, 6), (22, 6), (27, 6), (31, 6), (32, 6), (34, 6), (35, 6),
                        (8, 7), (9, 7), (11, 7), (13, 7), (15, 7), (16, 7), (19, 7),
                        (21, 7), (22, 7), (24, 7), (25, 7), (27, 7), (28, 7), (29, 7),
                        (37, 7), (38, 7), (10, 8), (12, 8), (14, 8), (19, 8), (27, 8),
                        (28, 8), (29, 8), (37, 8), (5, 9), (6, 9), (7, 9), (11, 9),
                        (15, 9), (16, 9), (22, 9), (29, 9), (37, 9), (4, 10), (5, 10),
                        (6, 10), (7, 10), (11, 10), (22, 10), (3, 11), (7, 11), (8, 11),
                        (15, 11), (8, 12), (11, 12), (12, 12), (14, 12), (15, 12),
                        (17, 12), (18, 12), (3, 13), (5, 13), (8, 13), (11, 13),
                        (12, 13), (14, 13), (15, 13), (16, 13), (17, 13), (19, 13),
                        (21, 13), (22, 13), (23, 13), (25, 13), (26, 13), (28, 13),
                        (16, 14), (17, 14), (19, 14), (25, 14), (26, 14), (28, 14),
                        (29, 14), (12, 15), (21, 15), (23, 15), (25, 15), (27, 15),
                        (30, 15), (12, 16), (20, 16), (21, 16), (23, 16), (29, 16),
                        (20, 17), (21, 18)
                    )
                },
            'exploder':
                {
                    'size': (5, 5),
                    'pattern': (
                        (1, 1), (3, 1), (5, 1), (1, 2), (5, 2), (1, 3), (5, 3), (1, 4),
                        (5, 4), (1, 5), (3, 5), (5, 5)
                    )
                },
            'small exploder':
                {
                    'size': (3, 4),
                    'pattern': (
                        (1, 2), (2, 1), (2, 3), (3, 1), (3, 2), (3, 3), (4, 2)
                    )
                },
            'glider gun':
                {
                    'size': (35, 8),
                    'pattern': (
                        (25, 1), (23, 2), (25, 2), (13, 3), (14, 3), (21, 3), (22, 3),
                        (35, 3), (36, 3), (12, 4), (16, 4), (21, 4), (22, 4), (35, 4),
                        (36, 4), (1, 5), (2, 5), (11, 5), (17, 5), (21, 5), (22, 5),
                        (1, 6), (2, 6), (11, 6), (15, 6), (17, 6), (18, 6), (23, 6),
                        (25, 6), (11, 7), (17, 7), (25, 7), (12, 8), (16, 8), (13, 9),
                        (14, 9)
                    )
                }
        }

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
            for t in all_tuples:
                # User-entered coords are 1-indexed, must convert
                # to 0-indexed tuples

                if isinstance(t[0], int) and isinstance(t[1], int):
                    t = (t[0]-1, t[1]-1)

                    # Adds tuple only if not duplicates
                    if self.coord_in_range(t):
                        if t not in valid_tuples:
                            valid_tuples.append(t)
                    else:
                        if t not in invalid_tuples:
                            invalid_tuples.append(t)
                else:
                    invalid_tuples.append(t)

            return valid_tuples, invalid_tuples

        # Show the board
        self.render_board('[BOARD EDITING MODE]', '', True, True)

        # Show message if it exists
        if msg != '':
            print(msg)

        # Edit the board while the user wants to
        cont = True
        while cont:
            # Get user command
            cmd = input('Enter a command or type \"help\" for more info:\n>>> ').lower()

            # Execute commands
            if cmd in ['live', 'die']:
                print()

                _cont = True
                while _cont:
                    coords = input('Enter cells to {} as (x,y) coordinates separated by commas '
                                   'or type "cancel":'
                                   '\n>>> '.format(cmd))

                    if coords.lower() == 'cancel':
                        print()
                        _cont = False
                    else:
                        try:
                            # Get list of coordinates as tuples, like [(1,3),(2,3), ...]
                            valid_coords, invalid_coords = separate_valids(coords)
                        except ValueError as e:
                            # Coords were not entered in a valid format
                            # Print the error message raised in separate_valids()
                            print('\n{} '.format(e), end='')
                        else:
                            # Entered coords are of integers and are in range
                            # Update board and print the valid coords
                            msg_below = self.set_board_states_from_coords(valid_coords, cmd)

                            # Print the invalid coords if there are any
                            if len(invalid_coords) != 0:
                                msg_below += '\n\tThe following coordinates were invalid:'
                                for tup in invalid_coords:
                                    col, row = tup[0], tup[1]
                                    msg_below += '\n\t\t({}, {})'.format(col, row)
                                msg_below += '\n'

                            # Clear the terminal if applicable
                            if flush:
                                flush_terminal()

                            # Show the board
                            self.render_board('[BOARD EDITING MODE]', msg_below, True, True)

                            # Break from the loop
                            _cont = False

                print()
            elif cmd == 'presets':
                print()

                # Print the names of available presets
                print('\tPresets:')
                for preset in presets:
                    print('\t\t' + preset)
                    print('\t\t\tWidth required: {} cells'.format(presets[preset]['size'][0]), end='')
                    # Warn user if width too small (must be >= because of toroidal board)
                    if presets[preset]['size'][0] >= self.width:
                        print(' (board too small)')
                    else:
                        print()
                    print('\t\t\tHeight required: {} cells'.format(presets[preset]['size'][1]), end='')
                    # Warn user if height too small (must be >= because of toroidal board)
                    if presets[preset]['size'][1] >= self.height:
                        print(' (board too small)', end='')
                    else:
                        print()
                print()

                # Loop while user enters invalid presets
                _cont = True
                while _cont:
                    preset = input('Enter a preset name from list above or type "cancel":'
                                   '\n>>> ').lower()

                    if preset == 'cancel':
                        _cont = False
                    else:
                        # Validate input
                        if preset not in presets:
                            # Input not a preset
                            print('Invalid entry. ', end='')
                        else:
                            if not self.coord_in_range(presets[preset]['size']):
                                # Size of the preset is out of range of the board
                                print('That preset can\'t fit in your board. ', end='')
                            else:
                                print()

                                # Loop while user enters invalid starting square
                                # (where to place the preset)
                                __cont = True
                                while __cont:
                                    # Is a valid preset. Get coordinate to place it
                                    start_square = input('Enter bottom-left coordinate of the '
                                                         '{}x{} region you want to put the preset '
                                                         'or type "cancel":\n>>> '
                                                         ''.format(presets[preset]['size'][0],
                                                                   presets[preset]['size'][1]))

                                    if start_square.lower() == 'cancel':
                                        print()
                                        __cont = False
                                    else:
                                        # Validate input
                                        try:
                                            # Get coordinates as a list of tuples,
                                            # like [(1,3),(2,3), ...]
                                            valid_coords, invalid_coords = \
                                                separate_valids(start_square)
                                        except ValueError as e:
                                            # Coords were not entered in a valid format
                                            # Print the error message raised in
                                            # separate_valids()
                                            print('\n{} '.format(e), end='')
                                        else:
                                            if len(valid_coords) + len(invalid_coords) > 1:
                                                # User entered more than 1 cell
                                                print('Please only enter one coordinate. ',
                                                      end='')
                                            elif len(invalid_coords) == 1:
                                                if not isinstance(invalid_coords[0][0], int) \
                                                        and isinstance(invalid_coords[0][1], int):
                                                    # Cell is valid format, but out of range
                                                    print('\n\tYour coordinate "{}" was out of '
                                                          'range.'.format(start_square))
                                                else:
                                                    # Entered cell is not in valid format
                                                    print('\n\tYour coordinate "{}" was invalid. '
                                                          ''.format(start_square))
                                            elif not self.coord_in_range((valid_coords[0][0],
                                                                         valid_coords[0][1])):
                                                # Entered cell is a valid format,
                                                # but not on the board
                                                # (elif above makes 1-indexed user entry 0-indexed)
                                                print('\n\tThe cell {} is out of range.'
                                                      ''.format(start_square))
                                            else:
                                                # Change cell from 1-indexed to 0-indexed
                                                start_square = (valid_coords[0][0]-1,
                                                                valid_coords[0][1]-1)

                                                # Entered cell is in a valid format
                                                # and on the board.
                                                # Clear board and update it with the preset
                                                msg_below = self.set_board_states_from_coords(
                                                    presets[preset]['pattern'], 'live', True,
                                                    start_square) + '\n'

                                                # Clear the terminal if applicable
                                                if flush:
                                                    flush_terminal()

                                                # Show the board
                                                self.render_board('[BOARD EDITING MODE]', msg_below,
                                                                  True, True)

                                                # Break from the loop
                                                __cont = False
                                                _cont = False
            elif cmd == 'randomize':
                print()

                _cont = True
                while _cont:
                    density = input('Enter density (percentage of living cells):\n>>> ')

                    try:
                        density = float(density)
                    except ValueError:
                        print('Invalid input. ', end='')
                    else:
                        # Input was a float, check if it's in range
                        if not 0 < density <= 100:
                            print('Invalid input. Density must be between 0 and 100. '
                                  '', end='')
                        else:
                            print('\tDensity set at {}.'.format(density))
                            _cont = False

                # Randomize the board
                print('\nRandomizing board...')
                self.state = Board.get_random_board(self.height, self.width, density)
                time.sleep(1)

                if flush:
                    flush_terminal()

                self.render_board('[BOARD EDITING MODE]  Board randomized with density {}%. '
                                  ''.format(density), '', True, True)

            elif cmd == 'clear':
                self.clear_board()

                # Clear the terminal if applicable
                if flush:
                    flush_terminal()

                # Show the board
                self.render_board('[BOARD EDITING MODE]  Board cleared.', '', True, True)
            elif cmd == 'cls':
                if flush:
                    flush_terminal()

                # Re-render the same state of the board
                self.render_board('[BOARD EDITING MODE]  Terminal cleared.', '', True, True)
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

    def set_board_states_from_coords(self, cell_list, cmd, clear=False, start_square=(0, 0)):
        """Make the cells in cell_list alive or dead, depending on cmd, return success message."""

        msg_below = ''

        # Clear the board when using a preset
        if clear:
            self.clear_board()

        # Update the board with all the tuples
        for tup in cell_list:
            col, row = (tup[0] + start_square[0]) % self.width, \
                       (tup[1] + start_square[1]) % self.height
            if cmd == 'live':
                if self.is_alive(row, col):
                    msg_below += '\tCell at ({}, {}) was already ' \
                                 'alive.\n'.format(col + 1, row + 1)
                else:
                    self.live(row, col)
                    msg_below += '\tRevived cell at ({}, {}).\n' \
                                 ''.format(col + 1, row + 1)
            else:
                if self.is_dead(row, col):
                    msg_below += '\tCell at ({}, {}) was already ' \
                                 'dead.\n'.format(col + 1, row + 1)
                else:
                    self.die(row, col)
                    msg_below += '\tKilled cell at ({}, {}).\n' \
                                 ''.format(col + 1, row + 1)

        return msg_below

    def clear_board(self):
        """Kill all cell objects in self."""

        for row in range(self.height):
            for col in range(self.width):
                self.die(row, col)

    @staticmethod
    def get_blank_board(height, width) -> List[BitArray]:
        """Return a list of BitArrays initialized to 0.

        Arguments:
            height: Int height of the board to generate
            width: Int width of the board to generate

        This method is static so a blank board can be
        generated at instance creation.

        """

        # Create the list
        return [BitArray('0b' + '0' * width) for _ in range(height)]

    @staticmethod
    def get_random_board(height, width, density) -> List[BitArray]:
        """Randomize alive and dead cells in the board.

        Arguments:
            height: Int height of the board to generate
            width: Int width of the board to generate
            density: Percent of cells that should be alive (0 < density <= 100)

        This method is static so boards can be instantiated without
        looping through board twice (once to instantiate to BitArrays
        of 0s, again to randomize board).

        Credit for random bit generation strategy:
            https://stackoverflow.com/questions/14324472/random-boolean-by-percentage

        """

        new_state = []

        for row in range(height):
            # Create BitArray to hold the row
            new_state.append(BitArray())

            for col in range(width):
                # Generate random bit
                bit = random.uniform(0, 1) < density / 100

                # Add to the BitArray
                new_state[row].append('0b' + str(int(bit)))

        # Prevent low percentages returning a blank board
        if new_state == Board.get_blank_board(height, width):
           return Board.get_random_board(height, width, density)

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
            self.render_board('[GAME OF LIFE]  ' + msg)

            # Wait
            time.sleep(delay)

        if show_ticks:
            print('\tAdvanced the board by {} ticks.\n'.format(num_ticks))
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
        """Return true if cell at given coordinates is true.

        This is equivalent to is_alive(); included for semantic clarity.

        """

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
                    # Add the neighboring cell to the total (False is 0, True is 1).
                    # The modulo creates a toroidal wrapping effect.
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


def game_loop(board: Board, flush=True):
    """Tick Board until user enters "end" sentinel."""

    commands = {'': 'update board to the next tick',
                'tick': 'update the board by some number of ticks',
                'edit': 'edit current state of the board',
                'resize': 'resize the board and start from scratch',
                'end': 'end the program',
                'help': 'list available commands'}

    # Will determine if program starts new game once returning from game_loop()
    new_game = False
    # Re-renders board each loop if true
    refresh_board = True

    # Tick board or execute commands while user says so
    cont = True
    while cont:
        if refresh_board:
            # Clear the terminal if applicable
            if flush:
                flush_terminal()

            # Render the board and wait
            board.render_board('[GAME OF LIFE]  Tick: {}'.format(board.tick))

        prompt = input('\nPress enter to tick the board or type \"help\" for more info:\n'
                       '>>> ').lower().strip()

        # Validate prompt
        while prompt not in commands:
            prompt = input('\nUnknown command. Press enter to continue or type \"help\" for '
                           'more info:\n>>> ').lower().strip()

        # Execute command
        if prompt == '':
            # Tick board by 1
            board.tick_board()

            refresh_board = True
        elif prompt == 'edit':
            # Edit state of the board
            if flush:
                flush_terminal()

            board.set_board_states()
            print()

            refresh_board = True
        elif prompt == 'tick':
            # Tick the board given number of times
            num_ticks = input('\nEnter number of ticks or type "cancel":\n>>> ').lower()

            if num_ticks != 'cancel':
                # Validate number of ticks
                while not num_ticks.isdigit():
                    num_ticks = input('Invalid number. Enter number of ticks:\n>>> ')
                num_ticks = int(num_ticks)

                sleep_time = input('\nEnter milliseconds to pause between each tick '
                                   '(default 0):\n>>> ')

                if sleep_time == '':
                    sleep_time = 0
                else:
                    while not sleep_time.isdigit():
                        sleep_time = input('Invalid number. Enter milliseconds to pause '
                                           'between each tick (default 0):\n>>> ')
                    sleep_time = int(sleep_time)

                # Tick the board
                board.tick_board(num_ticks, True, sleep_time, True)

                refresh_board = True
        elif prompt == 'resize':
            print()

            # Break out of game loop
            cont = False
            new_game = True
        elif prompt == 'end':
            cont = False
            new_game = False
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

    return new_game


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
    welcome_state = [
        BitArray('0b' + '0000000000000000000000000000000000000000000000000000000000000000000000'),
        BitArray('0b' + '0000000000000000000000000000000000000000000000000000000000000000000000'),
        BitArray('0b' + '0001111101111101000101111100001111101111100010000011111011111011111000'),
        BitArray('0b' + '0001000001000101101101000000001000101000000010000000100010000010000000'),
        BitArray('0b' + '0001001101111101010101111000001000101111000010000000100011110011110000'),
        BitArray('0b' + '0001000101000101000101000000001000101000000010000000100010000010000000'),
        BitArray('0b' + '0001111101000101000101111100001111101000000011111011111010000011111000'),
        BitArray('0b' + '0000000000000000000000000000000000000000000000000000000000000000000000'),
        BitArray('0b' + '0000000000000000000000000000000000000000000000000000000000000000000000')
    ][::-1]

    time.sleep(0.5)
    print('Welcome to the Game of Life! Let\'s set up your board.\n')

    # Render and animate the board
    welcome_board = Board(0, len(welcome_state), len(welcome_state[0]), welcome_state)
    flush_terminal()
    welcome_board.render_board()
    time.sleep(2)
    welcome_board.tick_board(110, True, 50, False)

    time.sleep(0.5)
    print('Welcome to the Game of Life! Let\'s set up your board.\n')


def main():
    # welcome()

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
        cont = game_loop(board)


if __name__ == '__main__':
    main()
