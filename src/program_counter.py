class ProgramCounter(object):

    __PROGRAM_COUNTER_START = 0x200
    
    def __init__(self):
        self.__counter = self.__PROGRAM_COUNTER_START

    def jump(self):
        self.__counter += 2

    def double_jump(self):
        self.__counter += 4

    def jump_to(self, value):
        self.__counter = value

    def get(self):
        return self.__counter

    def __str__(self):
        return 'PROGRAM CT==>  0x{:03x}'.format((self.__counter))