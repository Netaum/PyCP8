
class Register(object):

    __DEFAULT_REGISTER_NUMBER = 16

    def __init__(self):
        self.__registers = [0] * self.__DEFAULT_REGISTER_NUMBER

    def set_vx(self, optcode, value):
        x = (optcode & 0x0F00) >> 8
        self.__registers[x] = value & 0xFF

    def get_vx(self, optcode):
        x = (optcode & 0x0F00) >> 8 
        return self.__registers[x]

    def set_vy(self, optcode, value):
        y = (optcode & 0x00F0) >> 4 
        self.__registers[y] = value & 0xFF

    def get_vy(self, optcode):
        y = (optcode & 0x00F0) >> 4 
        return self.__registers[y]

    def set_v0(self, value):
        self.__registers[0] = value

    def get_v0(self):
        return self.__registers[0]

    def set_vF(self, value):
        self.__registers[0xF] = value

    def get_vF(self):
        return self.__registers[0xF]

    def get_registers(self):
        return self.__registers

    def set_memory_registry(self, index:int, registry_x:int, memory):
        for i in range(0, registry_x):
            self.__registers[i] = memory[index + i]
    
    def __str__(self):
        prt = [ ' {}x{:03x} |'.format(i,f) for i, f in enumerate(self.__registers)]
        return 'REGISTERS ==> ' + ''.join(prt)