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
