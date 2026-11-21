import random


class BattleshipGame:
    """Консольна гра «Морський бій» на динамічних матрицях із процедурним ШІ бота."""

    def __init__(self, size: int = 10):
        self.size = size
        self.ship_sizes = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]
        self.row_letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']

        # Динамічні матриці ігрових полів
        self.player_board = [[' ' for _ in range(size)] for _ in range(size)]
        self.bot_board = [[' ' for _ in range(size)] for _ in range(size)]
        self.player_view = [[' ' for _ in range(size)] for _ in range(size)]

        # Стан процедурного ШІ бота (скінченний автомат HUNT / TARGET)
        self.bot_mode = "HUNT"
        self.bot_hits = []
        self.bot_potential_targets = []

    def parse_row(self, row_input) -> int | None:
        """Конвертує введену літеру (A–J) або цифру (0–9) в індекс рядка (0–9)."""
        row_input = str(row_input).strip().upper()
        if row_input in self.row_letters:
            return self.row_letters.index(row_input)
        try:
            val = int(row_input)
            if 0 <= val < self.size:
                return val
        except ValueError:
            pass
        return None

    def print_board_single(self, board: list[list[str]], title: str = "ПОЛЕ") -> None:
        print(f"\n{title:^27}")
        print("  " + " ".join([str(i) for i in range(self.size)]))
        for r in range(self.size):
            print(f"{self.row_letters[r]} " + " ".join(board[r]))

    def print_boards(self) -> None:
        print("\n" + "=" * 57)
        print(f"{' ТВОЄ ПОЛЕ ':^27} | {' ПОЛЕ БОТА ':^27}")
        print(
            "  " + " ".join([str(i) for i in range(self.size)])
            + " |   " + " ".join([str(i) for i in range(self.size)])
        )
        for r in range(self.size):
            p_row = f"{self.row_letters[r]} " + " ".join(self.player_board[r])
            b_row = f"{self.row_letters[r]} " + " ".join(self.player_view[r])
            print(p_row + f" | {b_row}")
        print("=" * 57)

    def can_place_ship(self, board: list[list[str]], r: int, c: int, size: int, horizontal: bool) -> bool:
        """Перевіряє можливість розміщення корабля з урахуванням буферної зони 3x3."""
        for i in range(size):
            nr = r if horizontal else r + i
            nc = c + i if horizontal else c

            if nr < 0 or nr >= self.size or nc < 0 or nc >= self.size:
                return False

            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    tr, tc = nr + dr, nc + dc
                    if 0 <= tr < self.size and 0 <= tc < self.size:
                        if board[tr][tc] == 'S':
                            return False
        return True

    def place_ships_manually(self) -> None:
        print("\n--- РУЧНА РОЗСТАНОВКА КОРАБЛІВ ---")
        print("Формат вводу: [Рядок-літера] [Стовпчик-цифра] [Орієнтація H/V]")
        print("Приклад: `A 0 H` (де A — рядок, 0 — стовпчик, H — горизонтально).")

        for size in self.ship_sizes:
            while True:
                self.print_board_single(self.player_board, f"Твоє поле (розміщуємо корабель довжиною: {size})")
                try:
                    user_input = input(f"Введи дані для {size}-палубного корабля: ").split()
                    if len(user_input) != 3:
                        print("Помилка! Потрібно ввести рівно 3 значення (наприклад: `A 2 H`).")
                        continue

                    r = self.parse_row(user_input[0])
                    c = int(user_input[1])
                    orientation = user_input[2].upper()

                    if r is None or not (0 <= c < self.size):
                        print(f"Помилка координат! Рядок має бути від A до J, а стовпчик від 0 до {self.size - 1}.")
                        continue

                    if orientation not in ['H', 'V']:
                        print("Помилка орієнтації! Використовуй 'H' (горизонтально) або 'V' (вертикально).")
                        continue

                    horizontal = (orientation == 'H')

                    if not self.can_place_ship(self.player_board, r, c, size, horizontal):
                        print("Сюди не можна поставити корабель! Він виходить за межі або торкається іншого.")
                        continue

                    for i in range(size):
                        nr = r if horizontal else r + i
                        nc = c + i if horizontal else c
                        self.player_board[nr][nc] = 'S'
                    break
                except ValueError:
                    print("Помилка вводу! Стовпчик має бути цілим числом.")

        self.print_board_single(self.player_board, "Твій флот успішно сформовано!")

    def place_ships_randomly(self, board: list[list[str]]) -> None:
        for size in self.ship_sizes:
            placed = False
            while not placed:
                horizontal = random.choice([True, False])
                r = random.randint(0, self.size - 1)
                c = random.randint(0, self.size - 1)

                if self.can_place_ship(board, r, c, size, horizontal):
                    for i in range(size):
                        nr = r if horizontal else r + i
                        nc = c + i if horizontal else c
                        board[nr][nc] = 'S'
                    placed = True

    def get_ship_coordinates(self, board: list[list[str]], start_r: int, start_c: int) -> list[tuple[int, int]]:
        """Пошук усіх координат зв'язного корабля методом пошуку в ширину (BFS)."""
        visited = set()
        queue = [(start_r, start_c)]
        ship_cells = []

        while queue:
            r, c = queue.pop(0)
            if (r, c) in visited:
                continue
            visited.add((r, c))

            if board[r][c] in ['X', 'S']:
                ship_cells.append((r, c))
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < self.size and 0 <= nc < self.size:
                        if board[nr][nc] in ['X', 'S'] and (nr, nc) not in visited:
                            queue.append((nr, nc))
        return ship_cells

    def is_ship_sunk(self, board: list[list[str]], ship_cells: list[tuple[int, int]]) -> bool:
        for r, c in ship_cells:
            if board[r][c] == 'S':
                return False
        return True

    def mark_sunk_ship_contours(
        self,
        board: list[list[str]],
        view_board: list[list[str]],
        ship_cells: list[tuple[int, int]],
    ) -> None:
        for r, c in ship_cells:
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    tr, tc = r + dr, c + dc
                    if 0 <= tr < self.size and 0 <= tc < self.size:
                        if board[tr][tc] == ' ':
                            board[tr][tc] = '*'
                            view_board[tr][tc] = '*'

    def player_turn(self) -> bool:
        while True:
            try:
                print("\nТвій хід! Введи координати пострілу (рядок-літеру та стовпчик через пробіл, наприклад: `B 5`):")
                parts = input().split()
                if len(parts) != 2:
                    print("Помилка! Введи рівно два значення (наприклад: `B 5`).")
                    continue

                r = self.parse_row(parts[0])
                c = int(parts[1])

                if r is None or not (0 <= c < self.size):
                    print(f"Координати поза межами поля (Рядок: A-J, Стовпчик: 0-{self.size - 1}).")
                    continue

                if self.player_view[r][c] in ['X', '*']:
                    print("Ти вже стріляв сюди! Вибери іншу клітинку.")
                    continue

                if self.bot_board[r][c] == 'S':
                    print("==> ВЛУЧИВ! Можеш стріляти знову.")
                    self.bot_board[r][c] = 'X'
                    self.player_view[r][c] = 'X'

                    ship_cells = self.get_ship_coordinates(self.bot_board, r, c)
                    if self.is_ship_sunk(self.bot_board, ship_cells):
                        print("Ти потопив ворожий корабель!")
                        self.mark_sunk_ship_contours(self.bot_board, self.player_view, ship_cells)
                    return True
                else:
                    print("==> ПРОМАХ.")
                    self.bot_board[r][c] = '*'
                    self.player_view[r][c] = '*'
                    return False
            except ValueError:
                print("Помилка вводу! Стовпчик має бути цілим числом.")

    def bot_turn(self) -> bool:
        print("\nХід бота...")
        while True:
            if not self.bot_potential_targets:
                self.bot_mode = "HUNT"

            if self.bot_mode == "HUNT":
                available = [
                    (r, c)
                    for r in range(self.size)
                    for c in range(self.size)
                    if self.player_board[r][c] in [' ', 'S'] and (r + c) % 2 == 0
                ]
                if not available:
                    available = [
                        (r, c)
                        for r in range(self.size)
                        for c in range(self.size)
                        if self.player_board[r][c] in [' ', 'S']
                    ]
                if not available:
                    return False
                r, c = random.choice(available)

            elif self.bot_mode == "TARGET":
                if not self.bot_potential_targets:
                    self.bot_mode = "HUNT"
                    continue
                r, c = self.bot_potential_targets.pop(0)
                if self.player_board[r][c] in ['X', '*']:
                    continue

            if self.player_board[r][c] == 'S':
                print(f"Бот влучив у твою клітинку [{self.row_letters[r]}, {c}]!")
                self.player_board[r][c] = 'X'
                self.bot_hits.append((r, c))

                ship_cells = self.get_ship_coordinates(self.player_board, r, c)
                if self.is_ship_sunk(self.player_board, ship_cells):
                    print("Бот потопив твій корабель!")
                    self.mark_sunk_ship_contours(self.player_board, self.player_board, ship_cells)
                    self.bot_mode = "HUNT"
                    self.bot_hits = []
                    self.bot_potential_targets = []
                else:
                    self.bot_mode = "TARGET"
                    self.bot_potential_targets = []
                    if len(self.bot_hits) >= 2:
                        rs = [h[0] for h in self.bot_hits]
                        cs = [h[1] for h in self.bot_hits]
                        if len(set(rs)) == 1:
                            row = rs[0]
                            candidates = [(row, min(cs) - 1), (row, max(cs) + 1)]
                        else:
                            col = cs[0]
                            candidates = [(min(rs) - 1, col), (max(rs) + 1, col)]
                    else:
                        candidates = [(r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)]

                    for tr, tc in candidates:
                        if 0 <= tr < self.size and 0 <= tc < self.size:
                            if self.player_board[tr][tc] in [' ', 'S']:
                                self.bot_potential_targets.append((tr, tc))
                return True
            else:
                print(f"Бот стріляв у [{self.row_letters[r]}, {c}] — промах.")
                self.player_board[r][c] = '*'
                return False

    def check_victory(self) -> bool:
        player_has_ships = any('S' in row for row in self.player_board)
        bot_has_ships = any('S' in row for row in self.bot_board)

        if not bot_has_ships:
            self.print_boards()
            print("\nВІТАЮ! Ти переміг у морському бою!")
            return True
        if not player_has_ships:
            self.print_boards()
            print("\nГра закінчена. Бот переміг!")
            return True
        return False

    def play(self) -> None:
        self.place_ships_manually()

        print("\nКораблі бота генеруються випадковим чином...")
        self.place_ships_randomly(self.bot_board)

        while True:
            self.print_boards()

            while True:
                extra_turn = self.player_turn()
                if self.check_victory():
                    return
                if not extra_turn:
                    break
                self.print_boards()

            while True:
                bot_extra = self.bot_turn()
                if self.check_victory():
                    return
                if not bot_extra:
                    break


if __name__ == "__main__":
    game = BattleshipGame()
    game.play()
