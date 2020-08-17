"""CPU functionality."""

import sys

LDI = 0b10000010
PRN = 0b01000111
HLT = 0b00000001
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b01000110
ADD = 0b10100000
CALL = 0b01010000
RET = 0b00010001
CMP = 0b10100111
JEQ = 0b01010101
JNE = 0b01010110
JMP = 0b01010100


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.pc = 0
        self.flag = 0x00000000
        self.ram = [None] * 256
        self.reg = [None] * 8
        self.reg[7] = 0xF4
        self.running = False
        self.branchtable = {}
        self.branchtable[LDI] = self.handle_ldi
        self.branchtable[PRN] = self.handle_prn
        self.branchtable[HLT] = self.handle_hlt
        self.branchtable[PUSH] = self.handle_push
        self.branchtable[POP] = self.handle_pop
        self.branchtable[CALL] = self.handle_call
        self.branchtable[RET] = self.handle_ret
        self.branchtable[JEQ] = self.handle_jeq
        self.branchtable[JNE] = self.handle_jne
        self.branchtable[JMP] = self.handle_jmp

    def load(self):
        """Load a program into memory."""

        address = 0
        try:
            with open(sys.argv[1]) as file:
                for line in file:
                    if len(line) > 1 and line.split()[0] != '#':

                        self.ram[address] = int('0b' + line.split()[0], 2)

                        address += 1
        except FileNotFoundError:
            print(f'{sys.argv[0]}: {sys.argv[1]} not found')

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == ADD:
            self.reg[reg_a] += self.reg[reg_b]
        elif op == MUL:
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == CMP:
            if self.reg[reg_a] > self.reg[reg_b]:
                self.flag = 0b010
            elif self.reg[reg_a] == self.reg[reg_b]:
                self.flag = 0b001
            elif self.reg[reg_a] < self.reg[reg_b]:
                self.flag = 0b100
            else:
                print(f"flag not set {self.flag}")
        # elif op == "SUB": etc
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def ram_read(self, mar):

        return self.ram[mar]

    def ram_write(self, mar, mdr):
        self.ram[mar] = mdr

    def handle_ldi(self, reg_idx, value):
        # reg_idx = self.ram_read(pc + 1)
        # value = self.ram_read(pc + 2)
        self.reg[reg_idx] = value

    def handle_hlt(self, _, __):
        self.running = False

    def handle_prn(self, reg_idx, __):
        # reg_idx = self.ram_read(pc+1)
        num = self.reg[reg_idx]
        print(num)

    def handle_push(self, reg_to_push, __):
        # reg_to_push = self.ram_read(pc + 1)
        self.reg[7] -= 1

        value = self.reg[reg_to_push]
        self.ram_write(self.reg[7], value)

    def handle_pop(self, reg_to_write, __):
        # reg_to_write = self.ram_read(pc + 1)
        sp = self.reg[7]
        value = self.ram_read(sp)
        self.reg[reg_to_write] = value

        self.reg[7] += 1

    def handle_call(self, reg_idx, _):
        return_address = self.pc + 2

        self.reg[7] -= 1
        self.ram_write(self.reg[7], return_address)
        self.pc = self.reg[reg_idx]

    def handle_ret(self, _, __):
        ret_idx = self.ram_read(self.reg[7])
        self.pc = ret_idx

        self.reg[7] += 1

    def handle_jeq(self, reg_idx, __):
        if self.flag & 0b001 == 1:
            new_pc = self.reg[reg_idx]
            self.pc = new_pc

    def handle_jne(self, reg_idx, _):
        if self.flag & 0b001 == 0:
            new_pc = self.reg[reg_idx]
            self.pc = new_pc

    def handle_jmp(self, op_a, _):
        pass

    def run(self):
        """Run the CPU."""
        self.running = True
        while self.running:
            try:

                IR = self.ram_read(self.pc)
                op_a = self.ram_read(self.pc + 1)
                op_b = self.ram_read(self.pc + 2)

                sets_pc_directly = (IR >> 4) & 0b0001
                is_alu_command = ((IR >> 5) & 0b001) == 1

                if is_alu_command:

                    self.alu(IR, op_a, op_b)

                else:
                    self.branchtable[IR](op_a, op_b)

                if not sets_pc_directly:
                    self.pc += 1 + (IR >> 6)

            except:
                print('unknown error')
