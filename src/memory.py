import os
import sys
from os.path import join
from program_counter import ProgramCounter

absolute_path = os.path.dirname(os.path.abspath(__file__))

class Memory(object):

    __DEFAULT_MEMORY = 4096
    __FONT_SET = [  0xF0, 0x90, 0x90, 0x90, 0xF0, #0
                    0x20, 0x60, 0x20, 0x20, 0x70, #1
                    0xF0, 0x10, 0xF0, 0x80, 0xF0, #2
                    0xF0, 0x10, 0xF0, 0x10, 0xF0, #3
                    0x90, 0x90, 0xF0, 0x10, 0x10, #4
                    0xF0, 0x80, 0xF0, 0x10, 0xF0, #5
                    0xF0, 0x80, 0xF0, 0x90, 0xF0, #6
                    0xF0, 0x10, 0x20, 0x40, 0x40, #7
                    0xF0, 0x90, 0xF0, 0x90, 0xF0, #8
                    0xF0, 0x90, 0xF0, 0x10, 0xF0, #9
                    0xF0, 0x90, 0xF0, 0x90, 0x90, #A
                    0xE0, 0x90, 0xE0, 0x90, 0xE0, #B
                    0xF0, 0x80, 0x80, 0x80, 0xF0, #C
                    0xE0, 0x90, 0x90, 0x90, 0xE0, #D
                    0xF0, 0x80, 0xF0, 0x80, 0xF0, #E
                    0xF0, 0x80, 0xF0, 0x80, 0x80  #F
                ]

    def __init__(self, counter: ProgramCounter):
        self.__memory = [0] * self.__DEFAULT_MEMORY
        self.__counter = counter
        self.__optcode = 0x0

        self.__load_fontset()

    def load_program(self, file_name):
        ''' load a binary file in the memory '''
        file_path = join(absolute_path, 'files', file_name)
        i = 0
        pc = self.__counter.get()
        with open(file_path, "rb") as file:
            byte = file.read(1)
            while byte != b"":
                converted = int.from_bytes(byte, byteorder=sys.byteorder)
                self.__memory[i + pc] = converted
                i += 1
                byte = file.read(1)

    def __load_fontset(self):
        for i, item in enumerate(self.__FONT_SET):
            self.__memory[i] = item

    def load_optcode(self):
        pc = self.__counter.get()
        mem_x = self.__memory[pc]
        mem_y = self.__memory[pc + 1]
        self.__optcode = mem_x << 8 | mem_y

        return self.__optcode

    def get_optcode(self):
        return self.__optcode
    
    def set_binary_code(self, index, register_x):
        self.__memory[index] = register_x / 100
        self.__memory[index+1] = (register_x / 10) % 10
        self.__memory[index+2] = (register_x % 100) % 10

    def set_registers_memory(self, index: int, register_x: int, registers):
        for i in range(0, register_x):
            self.__memory[index+i] = registers[i]

    def get_memory(self):
        return self.__memory