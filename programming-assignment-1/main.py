"""
@Author: Jack McGowan
@Date: 01/23/2023
"""
import unittest


class Instruction:
    opcode = int()
    Rd = int()
    Rs1 = int()
    Rs2 = int()
    immed = int()


class Cpu:
    MEM_SIZE = 65536
    NUM_REGISTERS = 16

    pc = int()
    next_pc = int()
    mem = [int()] * MEM_SIZE
    regs = [int()] * NUM_REGISTERS

    def fetch(self) -> int:
        instruction = self.mem[self.pc]
        self.next_pc = self.pc + 1
        return instruction

    def decode(self, instruction: int) -> Instruction:
        # We can assume the instruction to be 32bits long

        # No Magic Numbers
        MAX_4_BIT = 15         # 2 ** 4 - 1
        MAX_16_BIT = 65_535     # 2 ** 16 - 1

        # The decoded instruction object
        parsed = Instruction()

        parsed.opcode = (instruction >> 28) & MAX_4_BIT
        parsed.Rd = (instruction >> 24) & MAX_4_BIT
        parsed.Rs1 = (instruction >> 20) & MAX_4_BIT
        parsed.Rs2 = (instruction >> 16) & MAX_4_BIT
        parsed.immed = (instruction) & MAX_16_BIT

        return parsed

    def exec(self, i: Instruction) -> None:

        # if-elif was used in favor of match-case for python3 version compatibility
        op = i.opcode
        if op == 0:
            self.noop()
        elif op == 1:
            self.add(i.Rd, i.Rs1, i.Rs2)
        elif op == 2:
            self.addi(i.Rd, i.Rs1, i.immed)
        elif op == 3:
            self.beq(i.Rs1, i.Rs2, i.immed)
        elif op == 4:
            self.jal(i.Rd, i.immed)
        elif op == 5:
            self.lw(i.Rd, i.Rs1, i.immed)
        elif op == 6:
            self.sw(i.Rs1, i.Rs2, i.immed)
        elif op == 7:
            self.rtrn()
        else:
            self.noop()

        self.pc = self.next_pc

    def noop(self) -> None:
        return

    def add(self, rd, rs1, rs2) -> None:
        alu_result = self.regs[rs1] + self.regs[rs2]
        self.regs[rd] = alu_result
        return

    def addi(self, rd, rs1, immed) -> None:
        alu_result = self.regs[rs1] + immed
        self.regs[rd] = alu_result
        return

    def beq(self, rs1, rs2, immed) -> None:
        if (self.regs[rs1] == self.regs[rs2]):
            self.next_pc = self.pc + immed
        return

    def jal(self, rd, immed) -> None:
        alu_result = self.pc + 1
        self.regs[rd] = alu_result
        self.next_pc = self.pc + immed
        return

    def lw(self, rd, rs1, immed) -> None:
        eff_address = immed + self.regs[rs1]
        self.regs[rd] = self.mem[eff_address]
        return

    def sw(self, rs1, rs2, immed) -> None:
        eff_address = immed + self.regs[rs2]
        self.mem[eff_address] = self.regs[rs1]
        return

    # return function, named this way to avoid conflict with built-in return
    def rtrn(self) -> None:
        # Terminate
        pass


class TestCpuProgram(unittest.TestCase):
    MAX_16_BIT = 65536

    NOOP = 0
    ADD = 1
    ADDI = 2
    BEQ = 3
    JAL = 4
    LW = 5
    SW = 6
    RETURN = 7

    def get_instructions(self):
        instructions = []
        instructions.append((self.NOOP << 28))
        instructions.append((self.ADDI << 28) + (1 << 24) + (0 << 20) + 1)
        instructions.append((self.ADDI << 28) + (2 << 24) + (0 << 20) + 2)
        instructions.append((self.ADD << 28) + (3 << 24) +
                            (1 << 20) + (1 << 16))
        instructions.append((self.ADD << 28) + (4 << 24) +
                            (2 << 20) + (2 << 16))
        instructions.append((self.BEQ << 28) + (3 << 20) + (4 << 16) + 3)
        instructions.append((self.ADDI << 28) + (8 << 24) + (0 << 20) + 10)
        instructions.append((self.JAL << 28) + (0 << 24) + 2)
        instructions.append((self.ADDI << 28) + (8 << 24) + (0 << 20) + 1000)
        instructions.append((self.SW << 28) + (2 << 20) + (8 << 16) + 10)
        instructions.append((self.LW << 28) + (5 << 24) + (8 << 20) + 10)
        instructions.append((self.RETURN << 28))

        return instructions

    def load_validation_data(self):
        valid_regs = [108, 1, 2, 2, 4, 2, 0, 0, 10, 0, 0, 0, 0, 0, 0, 0]

        valid_memory = [int()] * self.MAX_16_BIT
        valid_memory[20] = 2

        instructions = self.get_instructions()
        for idx, elm in enumerate(range(100, 112)):
            valid_memory[elm] = instructions[idx]

        return valid_regs, valid_memory

    def test_correctness(self):
        VALID_REGS, VALID_MEMORY = self.load_validation_data()

        cpu = Cpu()

        instructions = self.get_instructions()
        for idx, elm in enumerate(range(100, 112)):
            cpu.mem[elm] = instructions[idx]

        cpu.pc = 100

        while True:
            instruction = cpu.fetch()
            instruction = cpu.decode(instruction)
            cpu.exec(instruction)
            if instruction.opcode == self.RETURN:
                break

        self.assertEqual(cpu.regs, VALID_REGS)
        self.assertEqual(cpu.mem, VALID_MEMORY)


if __name__ == '__main__':
    unittest.main()
