"""CPU functionality."""

import sys
import re
from pudb import set_trace as st

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.PC = 0
        self.IR = 0
        self.SP = 0xff # next empty slot (top of stack)
        self.flags = {
            "E": 0,
            "L": 0,
            "G": 0
        }

    def ram_read(self, address: int):
        return self.ram[address]

    def ram_write(value, address: int):
        self.ram[address] = value

    def load(self, file_dir):
        """Load a program into memory."""

        address = 0

        # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010,  # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111,  # PRN R0
        #     0b00000000,
        #     0b00000001,  # HLT
        # ]
        # program = []
        with open(file_dir) as file_obj:
            program_txt = "".join(file_obj.readlines())

        program = re.findall("[0,1]{8}", program_txt)

        for instruction in program:
            # self.ram[address] = '0b' + instruction
            self.ram[address] = int(instruction, 2)
            address += 1

    def LDI(self):
        self.PC += 1
        reg_num = self.ram_read(self.PC)
        self.PC += 1
        value = self.ram_read(self.PC)
        self.reg[reg_num] = value

    def PRN(self):
        self.PC += 1
        reg_num = self.ram_read(self.PC)
        print(self.reg[reg_num])

    def HLT(self):
        exit()

    def PUSH(self):
        self.PC += 1

        reg_num = self.ram[self.PC]
        value = self.reg[reg_num]
        top_of_stack_addr = self.SP
        self.ram[top_of_stack_addr] = value
        
        self.SP -= 1

    def POP(self):
        # st()
        self.PC += 1
        self.SP += 1

        reg_num = self.ram[self.PC]
        top_of_stack_addr = self.SP
        value = self.ram[top_of_stack_addr]
        self.reg[reg_num] = value

    def CALL(self):
        self.PC += 1

        reg_num = self.ram[self.PC]
        subroutine_addr = self.reg[reg_num]
        
        # push return addr
        # ret_addr = self.PC + 1
        ret_addr = self.PC
        self.ram[self.SP] = ret_addr
        self.SP -= 1

        # go to subroutine
        self.PC = subroutine_addr

    def RET(self):
        self.SP += 1
        ret_addr = self.ram[self.SP]
        self.PC = ret_addr

    def MUL(self):
        self.PC += 1
        reg_num_1 = self.ram_read(self.PC)
        self.PC += 1
        reg_num_2 = self.ram_read(self.PC)
        self.alu("MUL", reg_num_1, reg_num_2)

    def ADD(self):
        self.PC += 1
        reg_num_1 = self.ram_read(self.PC)
        self.PC += 1
        reg_num_2 = self.ram_read(self.PC)
        self.alu("ADD", reg_num_1, reg_num_2)

    def CMP(self):
        # st()
        self.PC += 1
        reg_num_1 = self.ram_read(self.PC)
        self.PC += 1
        reg_num_2 = self.ram_read(self.PC)
        self.alu("CMP", reg_num_1, reg_num_2)

    def JMP(self):
        # st()
        self.PC += 1
        reg_num = self.ram_read(self.PC)
        self.PC = self.reg[reg_num]

    def JEQ(self):
        # st()
        self.PC += 1
        if self.flags["E"]:
            reg_num = self.ram_read(self.PC)
            self.PC = self.reg[reg_num]
        else:
            self.PC += 1

    def JNE(self):  # jmp reg
        # st()
        self.PC += 1
        if not self.flags["E"]:
            reg_num = self.ram_read(self.PC)
            self.PC = self.reg[reg_num]
        else:
            self.PC += 1

    # def ADDI(self):
    #     self.PC += 1
    #     reg_num = self.ram_read(self.PC)
    #     self.PC += 1
    #     value = self.ram_read(self.PC)
    #     # self.alu("CMP", reg_num_1, reg_num_2)
    #     # reg_num += value

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]

        elif op == "SUB":
            self.reg[reg_a] -= self.reg[reg_b]

        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]

        elif op == "CMP":
            self.flags["E"] = int(self.reg[reg_a] == self.reg[reg_b])
            self.flags["L"] = int(self.reg[reg_a] < self.reg[reg_b])
            self.flags["G"] = int(self.reg[reg_a] > self.reg[reg_b])

        elif op == "AND":
            self.reg[reg_a] &= self.reg[reg_b]

        elif op == "OR":
            self.reg[reg_a] |= self.reg[reg_b]

        elif op == "XOR":
            self.reg[reg_a] ^= self.reg[reg_b]

        elif op == "NOT":
            self.reg[reg_a] = ~self.reg[reg_b]

        elif op == "SHL":
            self.reg[reg_a] = self.reg[reg_b] << 1

        elif op == "SHR":
            self.reg[reg_a] = self.reg[reg_b] >> 1

        elif op == "MOD":
            self.reg[reg_a] %= self.reg[reg_b]

        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.PC,
            # self.fl,
            # self.ie,
            self.ram_read(self.PC),
            self.ram_read(self.PC + 1),
            self.ram_read(self.PC + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        running = True
        while running:
            # self.trace()
            ir = self.ram_read(self.PC)

            if ir == 0b10000010:
                self.LDI()

                self.PC += 1

            if ir == 0b01000111:
                self.PRN()

                self.PC += 1

            if ir == 0b00000001:
                self.HLT()

                self.PC += 1

            if ir == 0b10100010:
                self.MUL()

                self.PC += 1

            if ir == 0b10100000:
                self.ADD()

                self.PC += 1

            if ir == 0b01000101:
                self.PUSH()

                self.PC += 1

            if ir == 0b01000110:
                self.POP()

                self.PC += 1

            if ir == 0b01010000:
                # st()
                self.CALL()

            if ir == 0b00010001:
                # st()
                self.RET()

                self.PC += 1

            if ir == 0b10100111:
                self.CMP()

                self.PC += 1

            if ir == 0b01010100:
                self.JMP()

                # self.PC += 1

            if ir == 0b01010101:
                self.JEQ()

                # self.PC += 1

            if ir == 0b01010110:
                self.JNE()

                # self.PC += 1
