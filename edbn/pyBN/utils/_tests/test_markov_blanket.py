"""
**************
Markov Blanket
Unit Test
**************
"""

__author__ = """Nicholas Cullen <ncullen.th@dartmouth.edu>"""

import os
import unittest
from os.path import dirname

from pyBN.independence.markov_blanket import markov_blanket
from pyBN.readwrite.read import read_bn


class ConstraintTestsTestCase(unittest.TestCase):

	def setUp(self):
		self.dpath = os.path.join(dirname(dirname(dirname(dirname(__file__)))),'data')	
		self.bn = read_bn(os.path.join(self.dpath,'cmu.bn'))

	def tearDown(self):
		pass

	def test_markov_blanket(self):
		self.assertDictEqual(markov_blanket(self.bn),
			{'Alarm': ['Earthquake', 'Burglary', 'JohnCalls', 'MaryCalls'],
			 'Burglary': ['Alarm', 'Earthquake'],
			 'Earthquake': ['Alarm', 'Burglary'],
			 'JohnCalls': ['Alarm'],
			 'MaryCalls': ['Alarm']})