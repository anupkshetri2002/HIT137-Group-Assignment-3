class GameState:
    max_mistakes = 3

    def __init__(self) -> None:
        self.reset_round()

    def reset_round(self) -> None:
        self.mistakes = 0
        self.found_count = 0
        self.round_won = False
        self.game_over = False
        self.revealed = False

    def record_correct(self, total_differences: int) -> None:
        self.found_count += 1
        if self.found_count >= total_differences:
            self.round_won = True

    def record_mistake(self) -> None:
        self.mistakes += 1
        if self.mistakes >= self.max_mistakes:
            self.game_over = True

    def set_revealed(self) -> None:
        self.revealed = True
        self.game_over = True

    @property
    def remaining(self) -> int:
        return max(0, self.total_differences - self.found_count)

    @property
    def total_differences(self) -> int:
        return 5
