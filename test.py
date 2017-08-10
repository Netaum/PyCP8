""" TEST CLASS """
from src.chip8 import Chip8
import os 

chip = Chip8()
dir_c = os.path.dirname(__file__)
rel_p = "bin\\pong2.c8"
abs_p = os.path.join(dir_c, rel_p)
chip.load_program(abs_p)

for i in range(0, 100):
    chip.emulate_cycle()
