
class Stack(object):

    __DEFAULT_STACK = 16

    def __init__(self):
        self.__stack = [0] * self.__DEFAULT_STACK
        self.__pointer = 0

    def push(self, value):
        self.__stack[self.__pointer] = value
        self.__pointer += 1

    def pop(self):
        self.__pointer -= 1
        return self.__stack[self.__pointer]

    def peek(self):
        i = self.__pointer - 1
        return self.__stack[i]

    def __str__(self):
        prt = []
        for i in range(0, self.__pointer):
            prt.append(f' {self.__stack[i]} |')
        return 'STACK     ==> ' + ''.join(prt)