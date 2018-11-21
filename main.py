import pygame


class Board:
    def __init__(self, tick, state, height=None, width=None):
        """Initialize game object."""

        if height is None:
            height = len(state)
        if width is None:
            width = len(state[0])

        self.tick = tick
        self.state = state
        self.height = height
        self.width = width

    def render_board(self):
        """Render the current state of the board."""

        # Top of the board
        print('┌' + '─'*self.width + '┐')

        # Middle of the board
        for row in range(len(self.state), -1, -1):
            # Left edge of the board
            print('│', end='')
            for col in self.state[row]:
                # Print the state of the cell
                print(self.state[row][col])

            # Right edge of the board
            print('│')

        # Bottom of the board
        print('└' + '─'*self.width + '┘')

    def tick(self, tick):
        """Advance the board by given number of game ticks."""

        for i in range(tick):
            self.advance_all()

    def advance_all(self):
        """Advance every cell on the board by one game tick."""

        # Create a copy of the current Board object
        new_state = Board(self.tick, self.state.copy(), self.height, self.width)

        for row in self.state:
            for col in self.state[row]:
                # The cell object at this board position
                cell = self.state[row][col]

                # Update the state of the cell in new_board
                if cell.should_live():
                    new_state.state[row][col].live()
                else:
                    new_state.state[row][col].die()


class Cell:
    alive_char = 'O'
    dead_char = ' '

    def __init__(self, state, row, col):
        """Create a cell object."""

        self.state = state
        self.row = row
        self.col = col
        self.neighbors = self.num_alive_neighbors()

    def __str__(self):
        """Print character showing aliveness of the given cell."""

        if self.is_alive():
            return Cell.alive_char
        else:
            return Cell.dead_char

    def is_alive(self):
        """Return True iff cell is alive."""

        return self.state

    def live(self):
        """Make the given cell alive."""

        self.state = True

    def die(self):
        """Make the given cell dead."""

        self.state = False

    def num_alive_neighbors(self):
        """Return number of alive neighbors of the given cell."""

        # Shorten variables for reference
        state = self.state
        row = self.row
        col = self.col

        # State and values in state must have length
        assert len(state) > 0
        assert len(state[0]) > 0

        # Row and col are in bounds
        assert 0 <= row < len(state)
        assert 0 <= col < len(state[0])

        # Sets neighbors differently depending on whether state[row][col]
        # is on one of the 4 edges of the board or is on a corner of the board
        if col == 0:
            if row == 0:
                # Cell is in top left corner
                right = state[row][col + 1]
                down_right = state[row - 1][col + 1]
                down = state[row - 1][col]

                neighbors = sum([right, down_right, down])
            elif row == len(state):
                # Cell is in bottom left corner
                top = state[row + 1][col]
                top_right = state[row + 1][col + 1]
                right = state[row][col + 1]

                neighbors = sum([top, top_right, right])
            else:
                # Cell is on left edge, but not a corner
                top = state[row + 1][col]
                top_right = state[row + 1][col + 1]
                right = state[row][col + 1]
                down_right = state[row - 1][col + 1]
                down = state[row - 1][col]

                neighbors = sum([top, top_right, right, down_right, down])
        elif col == len(state[0])-1:
            # Cell is on right edge
            if row == 0:
                # Cell is in top right corner
                down = state[row - 1][col]
                down_left = state[row - 1][col - 1]
                left = state[row][col - 1]

                neighbors = sum([down, down_left, left])
            elif row == len(state)-1:
                # Cell is in bottom right corner
                left = state[row][col - 1]
                top_left = state[row + 1][col - 1]
                top = state[row + 1][col]

                neighbors = sum([left, top_left, top])
            else:
                # Cell is on right edge, but not a corner
                down = state[row - 1][col]
                down_left = state[row - 1][col - 1]
                left = state[row][col - 1]
                top_left = state[row + 1][col - 1]
                top = state[row + 1][col]

                neighbors = sum([down, down_left, left, top_left, top])
        elif row == 0:
            # Cell is on top edge
            right = state[row][col + 1]
            down_right = state[row - 1][col + 1]
            down = state[row - 1][col]
            down_left = state[row - 1][col - 1]
            left = state[row][col - 1]

            neighbors = sum([right, down_right, down, down_left, left])
        elif row == len(state)-1:
            # Cell is on bottom edge
            left = state[row][col - 1]
            top_left = state[row + 1][col - 1]
            top = state[row + 1][col]
            top_right = state[row + 1][col + 1]
            right = state[row][col + 1]

            neighbors = sum([left, top_left, top, top_right, right])
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

            neighbors = sum(
                [top_left, top, top_right, right, down_right, down, down_left, left])

        return neighbors

    def should_live(self) -> bool:
        """Determine if cell should be alive next game tick."""

        # Get number of adjacent living cells
        num_neighbors = self.num_alive_neighbors()

        # Assume state doesn't change
        new_state = self.state

        # Check to see if it should
        if self.state:
            # Cell is alive
            if num_neighbors < 2:
                # Die by underpopulation
                new_state = False
            elif num_neighbors > 3:
                # Die by overpopulation
                new_state = False
        else:
            # Cell is dead
            if num_neighbors == 3:
                # Live by reproduction
                new_state = True

        return new_state


def game_loop():
    # Set up window data
    pygame.init()
    win = pygame.display.set_mode((500, 500))
    pygame.display.set_caption('Game of Life')
    millis_per_tick = 100

    # Main game loop
    run = True
    while run:
        pygame.time.delay(millis_per_tick)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        pygame.draw.rect(win, (50, 60, 60), )
    pygame.quit()


def main():
    board = Board()


if __name__ == '__main__':
    main()
