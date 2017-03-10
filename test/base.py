#
import unittest

from echo.app import App

class TestBase(unittest.TestCase):
    def setUp(self):
        super(TestBase, self).__init__()
        self.app = App()
