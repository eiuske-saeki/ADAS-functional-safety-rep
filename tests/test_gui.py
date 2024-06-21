import unittest
import tkinter as tk
from src.gui import gui

class TestGUI(unittest.TestCase):
    def setUp(self):
        # テストの前に実行されるセットアップメソッド
        self.root = tk.Tk()
        self.root.withdraw()  # GUIがポップアップしないようにする

    def tearDown(self):
        # テストの後に実行されるクリーンアップメソッド
        self.root.destroy()

    def test_run(self):
        # 実際にテストするメソッド
        self.assertIsNotNone(gui.run)

if __name__ == '__main__':
    unittest.main()
