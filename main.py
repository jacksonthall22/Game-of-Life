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

    def tick(self, state, tick):
        """Advance the board by given number of ticks."""
        pass

    def check_all(self):
        """Advance every cell on the board by one game tick."""
        pass


class Cell:
    alive_char = 'O'
    dead_char = ' '

    def __init__(self, state, row, col):
        """Create a cell object."""

        self.state = state
        self.row = row
        self.col = col

    def __str__(self):
        """Print character showing aliveness of the given cell."""

        if self.is_alive():
            return Cell.alive_char
        else:
            return Cell.dead_char

    def is_alive(self):
        """Return True iff cell is alive."""

        return self.state

    def toggle_state(self):
        """Toggle the aliveness of the given cell."""

        self.state = not self.state

    def num_alive_neighbors(self, x, y):
        """Return number of alive neighbors of the given cell."""

        state = self.state

        # State and values in state have length
        assert len(state) > 0
        assert len(state[0]) > 0

        # x and y are in bounds
        assert 0 <= y < len(state)
        assert 0 <= x < len(state[0])

        # Sets num_neighbors differently depending on whether state[y][x]
        # is on one of the 4 edges of the board or is on a corner of the board
        if x == 0:
            if y == 0:
                # Cell is in top left corner
                right = state[y][x + 1]
                down_right = state[y - 1][x + 1]
                down = state[y - 1][x]

                num_neighbors = sum([right, down_right, down])
            elif y == len(state):
                # Cell is in bottom left corner
                top = state[y + 1][x]
                top_right = state[y + 1][x + 1]
                right = state[y][x + 1]

                num_neighbors = sum([top, top_right, right])
            else:
                # Cell is on left edge, but not a corner
                top = state[y + 1][x]
                top_right = state[y + 1][x + 1]
                right = state[y][x + 1]
                down_right = state[y - 1][x + 1]
                down = state[y - 1][x]

                num_neighbors = sum([top, top_right, right, down_right, down])
        elif x == len(state[0])-1:
            # Cell is on right edge
            if y == 0:
                # Cell is in top right corner
                down = state[y - 1][x]
                down_left = state[y - 1][x - 1]
                left = state[y][x - 1]

                num_neighbors = sum([down, down_left, left])
            elif y == len(state)-1:
                # Cell is in bottom right corner
                left = state[y][x - 1]
                top_left = state[y + 1][x - 1]
                top = state[y + 1][x]

                num_neighbors = sum([left, top_left, top])
            else:
                # Cell is on right edge, but not a corner
                down = state[y - 1][x]
                down_left = state[y - 1][x - 1]
                left = state[y][x - 1]
                top_left = state[y + 1][x - 1]
                top = state[y + 1][x]

                num_neighbors = sum([down, down_left, left, top_left, top])
        elif y == 0:
            # Cell is on top edge
            right = state[y][x + 1]
            down_right = state[y - 1][x + 1]
            down = state[y - 1][x]
            down_left = state[y - 1][x - 1]
            left = state[y][x - 1]

            num_neighbors = sum([right, down_right, down, down_left, left])
        elif y == len(state)-1:
            # Cell is on bottom edge
            left = state[y][x - 1]
            top_left = state[y + 1][x - 1]
            top = state[y + 1][x]
            top_right = state[y + 1][x + 1]
            right = state[y][x + 1]

            num_neighbors = sum([left, top_left, top, top_right, right])
        else:
            # Cell is not on an edge of the board
            top_left = state[y + 1][x - 1]
            top = state[y + 1][x]
            top_right = state[y + 1][x + 1]
            right = state[y][x + 1]
            down_right = state[y - 1][x + 1]
            down = state[y - 1][x]
            down_left = state[y - 1][x - 1]
            left = state[y][x - 1]

            num_neighbors = sum(
                [top_left, top, top_right, right, down_right, down, down_left, left])

        return num_neighbors

    def next_state(self, num_neighbors) -> bool:
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
