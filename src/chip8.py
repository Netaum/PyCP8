""" Classe para controle do emulador """

class Chip8(object):
    """ Classe para controle do emulador """
    # pylint: disable=too-many-instance-attributes
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
                print(byte)
                self.memory[i + self.PROGRAM_COUNTER_START] = byte
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
        return self.memory[self.program_counter] << 8 | self.memory[self.program_counter+1]

    def emulate_cycle(self):
        ''' emulates the cpu cycle '''
        opt_code = self.__fetch_code()

    def __switch(self, optcode):
        opt = optcode & 0xF000
        return {
            0x0000 : self.__opt_zero()
        }.get(opt, 0)

    def __opt_zero(self):
        print('test')

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

    def __unknow_code(self, optcode):
        print('Unknow code' + optcode)

    def __clear_screen(self):
        self.gfx = [0x0 for pixel in self.gfx]
        self.draw_flag = True
        self.__jump()

    def __return_subrotine(self):
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
