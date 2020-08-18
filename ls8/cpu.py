"""CPU functionality."""

import sys
from ipdb import set_trace as st

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.PC = 0
        self.IR = []

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
        program = []
        with open(file_dir) as file_obj:
            program = file_obj.readlines()

        for instruction in program:
            self.ram[address] = instruction
            # st()
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

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        # elif op == "SUB": etc
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
            # st()
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
