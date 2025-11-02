class TicTacToe:
    def __init__(self, n=3):
        self.size = n
        self.matrix = [["" for _ in range(n)] for _ in range(n)]

    def insert(self, i: int, j: int, val: str):
        self.matrix[i][j] = val

    def display(self):
        for row in self.matrix:
            print([" " if cell == "" else cell for cell in row])
        print()

    def game_over(self):
        n = self.size
        m = self.matrix

        # Check rows and columns
        for i in range(n):
            if m[i][0] != "" and all(m[i][j] == m[i][0] for j in range(n)):
                return True
            if m[0][i] != "" and all(m[j][i] == m[0][i] for j in range(n)):
                return True

        # Check diagonals
        if m[0][0] != "" and all(m[i][i] == m[0][0] for i in range(n)):
            return True
        if m[0][n - 1] != "" and all(m[i][n - 1 - i] == m[0][n - 1] for i in range(n)):
            return True

        return False


class Player:
    def __init__(self, name: str, player_id: int):
        self.name = name
        self.symbol = 'X' if player_id == 1 else 'O'

    def play(self, i: int, j: int, game: TicTacToe):
        game.insert(i, j, self.symbol)
        game.display()


def main():
    game = TicTacToe()
    players = [Player("Rahul", 1), Player("Chinnulu", 2)]
    count = 0

    while True:
        current = players[count % 2]
        try:
            i, j = map(int, input(f"{current.name} ({current.symbol}) enter i,j: ").split(","))
            if not (0 <= i < game.size and 0 <= j < game.size):
                print("Invalid cell coordinates.")
                continue
        except ValueError:
            print("Invalid input format. Use i,j (e.g., 1,2)")
            continue

        if game.matrix[i][j] == "":
            current.play(i, j, game)
            count += 1
        else:
            print("Cell already filled! Try again.")
            continue

        if game.game_over():
            print(f"{current.name} wins!")
            break
        if count == game.size * game.size:
            print("It's a draw!")
            break


if __name__ == "__main__":
    main()
