import unittest
from battleship import BattleshipGame


class TestBattleshipGame(unittest.TestCase):
    def setUp(self):
        self.game = BattleshipGame(size=10)

    def test_parse_row(self):
        self.assertEqual(self.game.parse_row("A"), 0)
        self.assertEqual(self.game.parse_row("b"), 1)
        self.assertEqual(self.game.parse_row("9"), 9)
        self.assertIsNone(self.game.parse_row("Z"))

    def test_can_place_ship_boundaries_and_buffer(self):
        self.assertFalse(self.game.can_place_ship(self.game.player_board, 0, 8, 4, True))
        self.assertFalse(self.game.can_place_ship(self.game.player_board, 8, 4, 3, False))

        # Place 4-deck ship at A0..A3
        for c in range(4):
            self.game.player_board[0][c] = 'S'

        # Diagonal touch at B4 should be forbidden
        self.assertFalse(self.game.can_place_ship(self.game.player_board, 1, 4, 2, True))
        # Valid placement at C0
        self.assertTrue(self.game.can_place_ship(self.game.player_board, 2, 0, 3, True))

    def test_bfs_ship_sinking(self):
        self.game.bot_board[2][2] = 'X'
        self.game.bot_board[2][3] = 'X'
        cells = self.game.get_ship_coordinates(self.game.bot_board, 2, 2)
        self.assertEqual(set(cells), {(2, 2), (2, 3)})
        self.assertTrue(self.game.is_ship_sunk(self.game.bot_board, cells))


if __name__ == "__main__":
    unittest.main()
