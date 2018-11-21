class Board:
    def __init__(self, state, height, width, tick):
        """Initialize game object."""
        self.state = state
        self.height = height
        self.width = width
        self.tick = tick

    def render_board(self):
        """Render the current state of the board."""
        pass

    def tick(self, state, tick):
        """Advance the board by given number of ticks."""
        pass

    def check_all(self):
        """Advance every cell on the board by one game tick."""
        pass

    @staticmethod
    def num_alive_neighbors(state, x, y):
        """Return number of alive neighbors of the given cell."""

        assert len(state) > 0
        assert len(state[0]) > 0
        assert y < len(state)
        assert x < len(state[0])

        if not any([x == 0, y == 0, x == len(state[0])-1, y == len(state)-1]):
            # Cell is not on an edge of the board
            top_left = state[y + 1][x - 1]
            top = state[y + 1][x]
            top_right = state[y + 1][x + 1]
            right = state[y][x + 1]
            down_right = state[y - 1][x + 1]
            down = state[y - 1][x]
            down_left = state[y - 1][x - 1]
            left = state[y][x - 1]

            num_neighbors = sum([top_left, top, top_right, right, down_right, down, down_left, left])
        elif x == 0:
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
            raise ValueError('num_alive_neighbors() called with invalid x and y\n\tx: {}, y: {}'
                             ''.format(x, y))

        return num_neighbors

    @staticmethod
    def should_live(state):
        """Determine if cell should live on next game tick."""
        pass

    @staticmethod
    def should_die(state):
        """Determine if cell should die on next game tick."""
        pass


def main():
    pass


if __name__ == '__main__':
    main()
