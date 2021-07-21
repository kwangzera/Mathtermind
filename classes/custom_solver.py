from classes.classic_solver import ClassicSolver


class CustomSolver(ClassicSolver):
    def __init__(self, rounds, matches, verified, answer):
        super().__init__(rounds, matches, verified)
        self.ans_str = ", ".join(map(str, answer))

    def solve(self):
        # Custom games won't to be solved
        self.sol_panel.title = f"Valid Solutions Unavailable"
        self.sol_panel.description = f"Solutions will not be listed since you are in a custom game. The winning combination is ||`{self.ans_str}`||."
        return
