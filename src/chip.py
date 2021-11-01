from program_counter import ProgramCounter
from memory import Memory
from register import Register
from stack import Stack
import time
import os
import random

clear = lambda: os.system('clear')

class Chip(object):

    __DEFAULT_GRAPHIC = 64 * 32
    __DEFAULT_KEYS = 16

    def __init__(self):
        
        self.__pc = ProgramCounter()
        self.__memory = Memory(self.__pc)
        self.__register = Register()
        self.__stack = Stack()

        self.__index = 0
        self.__delay_timer = 0
        self.__sound_timer = 0
        self.__draw_flag = False

        self.gfx = [0] * self.__DEFAULT_GRAPHIC
        self.keys = [0] * self.__DEFAULT_KEYS

        self.__init_optcodes()
        self.__load__()

    def __load__(self):
        file_path = 'invaders.c8'
        self.__memory.load_program(file_path)
    
    def __init_optcodes(self):
        self.__optcode_0000 = {
            0x0000: self.__clear_screen,
            0x000E: self.__return_subrotine,
            0xFFFFF : 0x000F
        }

        self.__optcode_8000 = {
            0x0000: self.__set_vx_vy,
            0x0001: self.__set_vx_vx_or_vy,
            0x0002: self.__set_vx_vx_and_vy,
            0x0003: self.__set_vx_vx_xor_vy,
            0x0004: self.__add_vy_vx_carry,
            0x0005: self.__sub_vy_vx_carry,
            0x0006: self.__shift_right_vx_carry,
            0x0007: self.__sub_vx_vy_carry,
            0x000E: self.__shift_left_vx_carry,
            0xFFFFF : 0x000F
        }

        self.__optcode_E000 = {
            0x009E: self.__skip_key_pressed,
            0x00A1: self.__skip_key_not_pressed,
            0xFFFFF : 0x00FF
        }

        self.__optcode_F000 = {
            0x0007: self.__set_vx_delay_timer,
            0x000A: self.__key_press_await,
            0x0015: self.__set_delay_timer_vx,
            0x0018: self.__set_sound_timer_vx,
            0x001E: self.__add_vx_index,
            0x0029: self.__set_sprite_vx,
            0x0033: self.__binary_decimal_format,
            0x0055: self.__fill_memory_vx_v0,
            0x0065: self.__fill_v0_vx_memory,
            0xFFFFF : 0x00FF
        }

        self.__optcodes = {
            0x0000 : self.__optcode_0000,
            0x1000 : self.__jump_nnn,
            0x2000 : self.__call_subrotine,
            0x3000 : self.__skip_vx_eq_nn,
            0x4000 : self.__skip_vx_ne_nn,
            0x5000 : self.__skip_xv_eq_vy,
            0x6000 : self.__set_vx_nn,
            0x7000 : self.__add_nn_vx,
            0x8000 : self.__optcode_8000,
            0x9000 : self.__skip_vx_ne_vy,
            0xA000 : self.__set_index_nnn,
            0xB000 : self.__jump_nnn_v0,
            0xC000 : self.__set_vx_random,
            0xD000 : self.__draw_sprite,
            0xE000 : self.__optcode_E000,
            0xF000 : self.__optcode_F000,
            0xFFFFF : 0xF000
        }

    def emulate_cycle(self):
        optcode = self.__memory.load_optcode()
        self.__execute_optcode(optcode, self.__optcodes)

    def __execute_optcode(self, optcode, optcode_list):
        mask = optcode_list[0xFFFFF]
        index = optcode & mask
        if index not in optcode_list:
            print('Optcode not found')
            return

        exe_optcode = optcode_list[index]
        if not callable(exe_optcode):
            self.__execute_optcode(optcode, exe_optcode)

        else:
            exe_optcode(optcode)
            pc = hex(self.__pc.get())
            vx = f'({(optcode & 0x0F00) >> 8}:{hex(self.__register.get_vx(optcode))})' 
            vy = f'({(optcode & 0x00F0) >> 4}:{hex(self.__register.get_vy(optcode))})' 
            i = hex(self.__index)
            name = exe_optcode.__name__
            message = f'{name}: {hex(optcode)} [pc:{pc} | I:{i} | vx: {vx} | vy: {vy}]'
            #clear()
            #self.__print_registers(optcode, name)
            #print(message)

    def __opt_not_found(self, optcode):
        print('Unknown optcode: ' + hex(optcode))

    def __clear_screen(self, optcode):
        self.gfx = [0x0 for pixel in self.gfx]
        self.__draw_flag = True
        self.__pc.jump()
    
    def __key_press_await(self, optcode):
        keypress = False
        for i, key in enumerate(self.keys):
            if key != 0:
                self.__register.set_vx(optcode, i)
                keypress = True

        if not keypress:
            return

        self.__pc.jump()

    def __return_subrotine(self, optcode):
        subrotine = self.__stack.pop()
        self.__pc.jump_to(subrotine)
        self.__pc.jump()

    def __call_subrotine(self, optcode):
        self.__stack.push(self.__pc.get())
        value = optcode & 0x0FFF
        self.__pc.jump_to(value)

    def __skip_vx_eq_nn(self, optcode):
        vx = self.__register.get_vx(optcode)
        if vx == (optcode & 0x00FF):
            self.__pc.double_jump()
        else:
            self.__pc.jump()

    def __skip_vx_ne_nn(self, optcode):
        vx = self.__register.get_vx(optcode)
        if vx != (optcode & 0x00FF):
            self.__pc.double_jump()
        else:
            self.__pc.jump()

    def __skip_xv_eq_vy(self, optcode):
        vx = self.__register.get_vx(optcode)
        vy = self.__register.get_vy(optcode)
        if vx == vy:
            self.__pc.double_jump()
        else:
            self.__pc.jump()

    def __skip_vx_ne_vy(self, optcode):
        vx = self.__register.get_vx(optcode)
        vy = self.__register.get_vy(optcode)
        if vx != vy:
            self.__pc.double_jump()
        else:
            self.__pc.jump()

    def __set_vx_nn(self, optcode):
        value = optcode & 0x00FF
        self.__register.set_vx(optcode, value)
        self.__pc.jump()

    def __add_nn_vx(self, optcode):
        value = self.__register.get_vx(optcode)
        value += optcode & 0x00FF
        self.__register.set_vx(optcode, value)
        self.__pc.jump()

    def __set_vx_vy(self, optcode):
        value = self.__register.get_vx(optcode)
        self.__register.set_vy(optcode, value)
        self.__pc.jump()

    def __set_vx_vx_or_vy(self, optcode):
        vx = self.__register.get_vx(optcode)
        vy = self.__register.get_vy(optcode)
        value = vx | vy
        self.__register.set_vx(optcode, value)
        self.__pc.jump()

    def __set_vx_vx_and_vy(self, optcode):
        vx = self.__register.get_vx(optcode)
        vy = self.__register.get_vy(optcode)
        value = vx & vy
        self.__register.set_vx(optcode, value)
        self.__pc.jump()

    def __set_vx_vx_xor_vy(self, optcode):
        vx = self.__register.get_vx(optcode)
        vy = self.__register.get_vy(optcode)
        value = vx ^ vy
        self.__register.set_vx(optcode, value)
        self.__pc.jump()

    def __add_vy_vx_carry(self, optcode):
        vx = self.__register.get_vx(optcode)
        vy = self.__register.get_vy(optcode)

        if vy > (0xFF - vx):
            self.__register.set_vF(1)
        else:
            self.__register.set_vF(0)

        value = vx + vy
        self.__register.set_vx(optcode, value)
        self.__pc.jump()

    def __sub_vy_vx_carry(self, optcode):
        vx = self.__register.get_vx(optcode)
        vy = self.__register.get_vy(optcode)

        if vy > vx:
            self.__register.set_vF(0)
        else:
            self.__register.set_vF(1)

        value = vx - vy
        self.__register.set_vx(optcode, value)
        self.__pc.jump()

    def __shift_right_vx_carry(self, optcode):
        value = self.__register.get_vx(optcode)
        self.__register.set_vF(value & 0x1)
        value >>= 1
        self.__register.set_vx(optcode, value)
        self.__pc.jump()

    def __sub_vx_vy_carry(self, optcode):
        vx = self.__register.get_vx(optcode)
        vy = self.__register.get_vy(optcode)

        if vy < vx:
            self.__register.set_vF(0)
        else:
            self.__register.set_vF(1)

        value = vy - vx
        self.__register.set_vx(optcode, value)
        self.__pc.jump()

    def __shift_left_vx_carry(self, optcode):
        value = self.__register.get_vx(optcode)
        self.__register.set_vF(value >> 7)
        value <<= 1
        self.__register.set_vx(optcode, value)
        self.__pc.jump()

    def __set_index_nnn(self, optcode):
        self.__index = optcode & 0x0FFF
        self.__pc.jump()

    def __jump_nnn(self, optcode):
        value = (optcode & 0x0FFF)
        self.__pc.jump_to(value)
    
    def __jump_nnn_v0(self, optcode):
        value = (optcode & 0x0FFF) + self.__register.get_v0()
        self.__pc.jump_to(value)

    def __set_vx_random(self, optcode):
        rand = random.randint(0, 255) & (optcode & 0x00FF)
        self.__register.set_vx(optcode, rand)
        self.__pc.jump()

    def __set_vx_delay_timer(self, optcode):
        self.__register.set_vx(optcode, self.__delay_timer)
        self.__pc.jump()

    def __set_delay_timer_vx(self, optcode):
        self.__delay_timer = self.__register.get_vx(optcode)
        self.__pc.jump()

    def __set_sound_timer_vx(self, optcode):
        self.__sound_timer = self.__register.get_vx(optcode)
        self.__pc.jump()

    def __add_vx_index(self, optcode):
        idx = self.__index + self.__register.get_vx(optcode)
        if idx > 0x0FFF:
            self.__register.set_vF(1)
        else:
            self.__register.set_vF(0)

        self.__index = idx
        self.__pc.jump()

    def __binary_decimal_format(self, optcode):
        vx = self.__register.get_vx(optcode)
        self.__memory.set_binary_code(self.__index, vx)
        self.__pc.jump()

    def __fill_memory_vx_v0(self, optcode):
        vx = self.__register.get_vx(optcode)
        registers = self.__register.get_registers()
        self.__memory.set_registers_memory(self.__index, vx, registers)
        self.__index += vx + 1
        self.__pc.jump()

    def __fill_v0_vx_memory(self, optcode):
        memory = self.__memory.get_memory()
        vx = self.__register.get_vx(optcode)
        self.__register.set_memory_registry(self.__index, vx, memory)
        
        self.__index += vx + 1
        self.__pc.jump()

    def __draw_sprite(self, optcode):
        vx = self.__register.get_vx(optcode)
        vy = self.__register.get_vy(optcode)
        memory = self.__memory.get_memory()

        height = optcode & 0x000F

        self.__register.set_vF(0)
        for yline in range(0, height):
            pixel = memory[self.__index + yline]
            for xline in range(0, 8):
                if (pixel & (0x80 >> xline)) != 0:
                    if self.gfx[vx + xline + ((vy + yline) * 64)] == 1:
                        self.__register.set_v0(1)
                    self.gfx[vx + xline + ((vy + yline) * 64)] ^= 1
        self.__draw_flag = True
        self.__pc.jump()
        
    def __skip_key_pressed(self, optcode):
        vx = self.__register.get_vx(optcode)
        if self.keys[vx] != 0:
            self.__pc.double_jump()
        else:
            self.__pc.jump()
    
    def __skip_key_not_pressed(self, optcode):
        vx = self.__register.get_vx(optcode)
        if self.keys[vx] == 0:
            self.__pc.double_jump()
        else:
            self.__pc.jump()

    def __set_sprite_vx(self, optcode):
        vx = self.__register.get_vx(optcode)
        self.__index = vx * 0x5
        self.__pc.jump()

    def __print_registers(self, optcode, method):
        clear()
        print(self.__register)
        print(self.__stack)
        print(self.__pc)
        print('INDEX     ==>  0x{:03x}'.format((self.__index)))
        print('OPTCODE   ==>  0x{:04x}'.format(optcode))
        print('METHOD    ==>  {}'.format(method))

if __name__ == '__main__':
    c = Chip()
    while True:
        c.emulate_cycle()
        time.sleep(0.25)
