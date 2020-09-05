# -*- coding: utf-8 -*-

import os
from src.const.color import *


BASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../")
DEFAULT_MARKER = itertools.cycle(('o', '*', 's', 'v', '^', '<', '>', '1', '2', '3', '4', 'p', 'P', 'x', 'D', ))
DEFAULT_LINESTYLE = itertools.cycle(('solid', 'dashed', 'dotted', 'dashdot',  (0, (1, 10)), (0, (5, 10)), (0, (5, 1)), ':'))
# DEAFULT_HATCH = itertools.cycle(('///', '\\\\\\', '|||', '---', '+++', 'xxx', 'ooo', 'O', '.', '*'))
DEFAULT_HATCH = itertools.cycle(('/', '\\', '|', '-', '+', 'x', 'o', 'O', '.', '*'))


