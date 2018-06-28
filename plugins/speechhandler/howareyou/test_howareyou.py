# -*- coding: utf-8 -*-
import unittest
from jasper import testutils
from .howareyou import HowAreYouPlugin


class TestHowAreYouPlugin(unittest.TestCase):
    def setUp(self):
        self.plugin = testutils.get_plugin_instance(MeaningOfLifePlugin)

    def test_is_valid_method(self):
        self.assertTrue(self.plugin.is_valid("How are you?"))

    def test_handle_method(self):
        mic = testutils.TestMic()
        self.plugin.handle("How are you?", mic)
        self.assertEqual(len(mic.outputs), 1)
