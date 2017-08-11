""" Classe para controle do emulador """
import random
import sys

class Chip8(object):
    """ Classe para controle do emulador """
    # pylint: disable=too-many-instance-attributes
    # pylint: disable=C0103
    DEFAULT_MEMORY = 4096
    DEFAULT_REGISTER = 16
    DEFAULT_GRAPHIC = 64 * 32
    DEFAULT_STACK = 16
    DEFAULT_KEYS = 16
    PROGRAM_COUNTER_START = 0x200

    def __init__(self):
        self.fontset = []
        self.memory = [0] * self.DEFAULT_MEMORY
        self.register = [0] * self.DEFAULT_REGISTER
        self.index = 0
        self.program_counter = self.PROGRAM_COUNTER_START
        self.gfx = [0] * self.DEFAULT_GRAPHIC
        self.delay_timer = 0
        self.sound_timer = 0
        self.stack = [0] * self.DEFAULT_STACK
        self.stack_pointer = 0
        self.keys = [0] * self.DEFAULT_KEYS
        self.draw_flag = False
        self.__fontset()

    def load_program(self, file_path):
        ''' load a binary file in the memory '''
        i = 0
        with open(file_path, "rb") as file:
            byte = file.read(1)
            while byte != b"":
                byteorder = sys.byteorder
                self.memory[i + self.PROGRAM_COUNTER_START] = int.from_bytes(byte, byteorder=byteorder)
                i += 1
                byte = file.read(1)


    def __fontset(self):
        ''' inits the cp8 font set '''
        self.fontset = [0xF0, 0x90, 0x90, 0x90, 0xF0]
        self.fontset.extend([0x20, 0x60, 0x20, 0x20, 0x70])
        self.fontset.extend([0xF0, 0x10, 0xF0, 0x80, 0xF0])
        self.fontset.extend([0xF0, 0x10, 0xF0, 0x10, 0xF0])
        self.fontset.extend([0x90, 0x90, 0xF0, 0x10, 0x10])
        self.fontset.extend([0xF0, 0x80, 0xF0, 0x10, 0xF0])
        self.fontset.extend([0xF0, 0x80, 0xF0, 0x90, 0xF0])
        self.fontset.extend([0xF0, 0x10, 0x20, 0x40, 0x40])
        self.fontset.extend([0xF0, 0x90, 0xF0, 0x90, 0xF0])
        self.fontset.extend([0xF0, 0x90, 0xF0, 0x10, 0xF0])
        self.fontset.extend([0xF0, 0x90, 0xF0, 0x90, 0x90])
        self.fontset.extend([0xE0, 0x90, 0xE0, 0x90, 0xE0])
        self.fontset.extend([0xF0, 0x80, 0x80, 0x80, 0xF0])
        self.fontset.extend([0xE0, 0x90, 0x90, 0x90, 0xE0])
        self.fontset.extend([0xF0, 0x80, 0xF0, 0x80, 0xF0])
        self.fontset.extend([0xF0, 0x80, 0xF0, 0x80, 0x80])

        for i, item in enumerate(self.fontset):
            self.memory[i] = item

    def __fetch_code(self):
        ''' fetchs the byte code from memory '''
        memx = self.memory[self.program_counter]
        memy = self.memory[self.program_counter+1]

        optcode = (memx << 8) | memy
        return optcode

    def emulate_cycle(self):
        ''' emulates the cpu cycle '''
        optcode = self.__fetch_code()
        self.__switch(optcode)

        if self.delay_timer > 0:
            self.delay_timer -= 1

        if self.sound_timer > 0:
            if self.sound_timer == 1:
                print("BEEP !!")
            self.sound_timer -= 1



    def __switch(self, optcode):
        opt = optcode & 0xF000
        return {
            0x0000 : self.__switch_0000,
            0x1000 : self.__jump_nnn,
            0x2000 : self.__call_subrotine,
            0x3000 : self.__skip_vx_eq_nn,
            0x4000 : self.__skip_vx_ne_nn,
            0x5000 : self.__skip_xv_eq_vy,
            0x6000 : self.__set_vx_nn,
            0x7000 : self.__add_nn_vx,
            0x8000 : self.__switch_8000,
            0x9000 : self.__skip_vx_ne_vy,
            0xA000 : self.__set_index_nnn,
            0xB000 : self.__jump_nnn,
            0xC000 : self.__set_vx_random,
            0xD000 : self.__draw_sprite,
            0xE000 : self.__switch_E000,
            0xF000 : self.__switch_F000,
        }.get(opt, self.__opt_not_found)(optcode)

    def __switch_F000(self, optcode):
        opt = optcode & 0x00FF
        return {
            0x0007: self.__set_vx_delay_timer,
            0x000A: self.__key_press_await,
            0x0015: self.__set_delay_timer_vx,
            0x0018: self.__set_sound_timer_vx,
            0x001E: self.__add_vx_index,
            0x0029: self.__set_sprite_vx,
            0x0033: self.__binary_decimal_format,
            0x0055: self.__fill_memory_vx_v0,
            0x0065: self.__fill_v0_vx_memory,
        }.get(opt, self.__opt_not_found)(optcode)

    def __switch_E000(self, optcode):
        opt = optcode & 0x00FF
        return {
            0x009E: self.__skip_key_pressed,
            0x00A1: self.__skip_key_not_pressed,
        }.get(opt, self.__opt_not_found)(optcode)

    def __switch_8000(self, optcode):
        opt = optcode & 0x000F
        return {
            0x0000: self.__set_vx_vy,
            0x0001: self.__set_vx_vx_or_vy,
            0x0002: self.__set_vx_vx_and_vy,
            0x0003: self.__set_vx_vx_xor_vy,
            0x0004: self.__add_vy_vx_carry,
            0x0005: self.__sub_vy_vx_carry,
            0x0006: self.__shift_right_vx_carry,
            0x0007: self.__sub_vx_vy_carry,
            0x000E: self.__shift_left_vx_carry,
        }.get(opt, self.__opt_not_found)(optcode)

    def __switch_0000(self, optcode):
        opt = optcode & 0x000F
        return {
            0x0000: self.__clear_screen,
            0x000E: self.__return_subrotine,
        }.get(opt, self.__opt_not_found)(optcode)

    def __opt_not_found(self, optcode):
        print('Unknown optcode: ' + hex(optcode))

    def __jump(self, step=2):
        self.program_counter += step

    def __stack(self):
        return self.stack[self.stack_pointer]

    def __push_stack(self, value):
        self.stack[self.stack_pointer] = value
        self.stack_pointer += 1

    def __get_vx(self, optcode):
        return self.register[(optcode & 0x0F00) >> 8]

    def __set_vx(self, optcode, value):
        self.register[(optcode & 0x0F00) >> 8] = value

    def __get_vy(self, optcode):
        return self.register[(optcode & 0x00F0) >> 4]

    def __set_vy(self, optcode, value):
        self.register[(optcode & 0x00F0) >> 4] = value

    def __get_vf(self):
        return self.register[0xF]

    def __set_vf(self, value):
        self.register[0xF] = value

    def __clear_screen(self, optcode):
        print(optcode)
        self.gfx = [0x0 for pixel in self.gfx]
        self.draw_flag = True
        self.__jump()

    def __return_subrotine(self, optcode):
        print(optcode)
        self.stack_pointer -= 1
        self.program_counter = self.__stack()
        self.__jump()

    def __jump_address(self, optcode):
        self.program_counter = optcode & 0x0FFF

    def __call_subrotine(self, optcode):
        self.__push_stack(self.program_counter)
        self.program_counter = optcode & 0x0FFF

    def __skip_vx_eq_nn(self, optcode):
        step = 4 if self.__get_vx(optcode) == (optcode & 0x00FF) else 2
        self.__jump(step)

    def __skip_vx_ne_nn(self, optcode):
        step = 4 if self.__get_vx(optcode) != (optcode & 0x00FF) else 2
        self.__jump(step)

    def __skip_xv_eq_vy(self, optcode):
        step = 4 if self.__get_vx(optcode) != self.__get_vy(optcode) else 2
        self.__jump(step)

    def __skip_vx_ne_vy(self, optcode):
        step = 4 if self.__get_vx(optcode) == self.__get_vy(optcode) else 2
        self.__jump(step)

    def __set_vx_nn(self, optcode):
        self.__set_vx(optcode, optcode & 0x00FF)
        self.__jump()

    def __add_nn_vx(self, optcode):
        register = self.__get_vx(optcode)
        register += optcode & 0x00FF
        self.__set_vx(optcode, register)
        self.__jump()

    def __set_vx_vy(self, optcode):
        self.__set_vx(optcode, self.__get_vy(optcode))
        self.__jump()

    def __set_vx_vx_or_vy(self, optcode):
        register = self.__get_vx(optcode) | self.__get_vy(optcode)
        self.__set_vx(optcode, register)
        self.__jump()

    def __set_vx_vx_and_vy(self, optcode):
        register = self.__get_vx(optcode) & self.__get_vy(optcode)
        self.__set_vx(optcode, register)
        self.__jump()

    def __set_vx_vx_xor_vy(self, optcode):
        register = self.__get_vx(optcode) ^ self.__get_vy(optcode)
        self.__set_vx(optcode, register)
        self.__jump()

    def __add_vy_vx_carry(self, optcode):
        if self.__get_vy(optcode) > (0x00FF - self.__get_vx(optcode)):
            self.__set_vf(1)
        else:
            self.__set_vf(0)

        register = self.__get_vx(optcode) + self.__get_vy(optcode)
        self.__set_vx(optcode, register)
        self.__jump()

    def __sub_vy_vx_carry(self, optcode):
        if self.__get_vy(optcode) > (self.__get_vx(optcode)):
            self.__set_vf(0)
        else:
            self.__set_vf(1)

        register = self.__get_vx(optcode) - self.__get_vy(optcode)
        self.__set_vx(optcode, register)
        self.__jump()

    def __shift_right_vx_carry(self, optcode):
        register = self.__get_vx(optcode)
        self.__set_vf(register & 0x1)
        register >>= 1
        self.__set_vx(optcode, register)
        self.__jump()

    def __sub_vx_vy_carry(self, optcode):
        if self.__get_vy(optcode) < (self.__get_vx(optcode)):
            self.__set_vf(0)
        else:
            self.__set_vf(1)

        register = self.__get_vy(optcode) - self.__get_vx(optcode)
        self.__set_vx(optcode, register)
        self.__jump()

    def __shift_left_vx_carry(self, optcode):
        register = self.__get_vx(optcode)
        self.__set_vf(register >> 7)
        register <<= 1
        self.__set_vx(optcode, register)
        self.__jump()

    def __set_index_nnn(self, optcode):
        self.index = optcode & 0x0FFF
        self.__jump()

    def __jump_nnn(self, optcode):
        step = (optcode & 0x0FFF) + self.register[0]
        self.__jump(step)

    def __set_vx_random(self, optcode):
        rand = (random.randint(0, 255) % 0xFF) & (optcode & 0x00FF)
        self.__set_vx(optcode, rand)
        self.__jump()

    def __set_vx_delay_timer(self, optcode):
        self.__set_vx(optcode, self.delay_timer)
        self.__jump()

    def __set_delay_timer_vx(self, optcode):
        self.delay_timer = self.__get_vx(optcode)
        self.__jump()

    def __set_sound_timer_vx(self, optcode):
        self.sound_timer = self.__get_vx(optcode)
        self.__jump()

    def __add_vx_index(self, optcode):
        indx = self.index + self.__get_vx(optcode)
        if indx > 0x0FFF:
            self.__set_vf(1)
        else:
            self.__set_vf(0)
        self.index = indx
        self.__jump()


    def __key_press_await(self, optcode):
        keypress = False
        for i, key in enumerate(self.keys):
            if key != 0:
                self.__set_vx(optcode, i)
                keypress = True

        if not keypress:
            return

        self.__jump()

    def __binary_decimal_format(self, optcode):
        self.memory[self.index] = self.__get_vx(optcode) / 100
        self.memory[self.index+1] = (self.__get_vx(optcode) / 10) % 10
        self.memory[self.index+2] = (self.__get_vx(optcode) % 100) % 10
        self.__jump()

    def __fill_memory_vx_v0(self, optcode):
        for i in range(0, self.__get_vx(optcode)):
            self.memory[self.index+i] = self.register[i]
        self.index += self.__get_vx(optcode) + 1
        self.__jump()

    def __fill_v0_vx_memory(self, optcode):
        for i in range(0, self.__get_vx(optcode)):
            self.register[i] = self.memory[self.index+i]
        self.index += self.__get_vx(optcode) + 1
        self.__jump()

    def __draw_sprite(self, optcode):
        print('not implemented')

    def __skip_key_pressed(self, optcode):
        print('not implemented')
    
    def __skip_key_not_pressed(self, optcode):
        print('not implemented')

    def __set_sprite_vx(self, optcode):
        print('not implemented')