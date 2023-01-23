"""
@Author: Jack McGowan
@Date: 01/23/2023
"""


class Instruction:
    opcode = int()
    Rd = int()
    Rs1 = int()
    Rs2 = int()
    immed = int()


class CPU:
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
        MAX_1_BYTE = 15
        MAX_4_BYTE = 65_535

        # The decoded instruction object
        parsed = Instruction()

        parsed.opcode = (instruction >> 28) & MAX_1_BYTE
        parsed.Rd = (instruction >> 24) & MAX_1_BYTE
        parsed.Rs1 = (instruction >> 20) & MAX_1_BYTE
        parsed.Rs2 = (instruction >> 16) & MAX_1_BYTE
        parsed.immed = (instruction) & MAX_4_BYTE

        return parsed

    def exec(self, i: Instruction) -> None:
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


def validate_run(memory, regs):
    for idx, elm in enumerate(regs):
        print(f"R{idx}={elm}", end=", ")
    print("")

    ADDRESS_TO_CHECK = 20
    print(f"value at address {ADDRESS_TO_CHECK}: {memory[ADDRESS_TO_CHECK]}")


def main():
    NOOP = 0
    ADD = 1
    ADDI = 2
    BEQ = 3
    JAL = 4
    LW = 5
    SW = 6
    RETURN = 7

    cpu = CPU()

    i0 = (NOOP << 28)
    i1 = (ADDI << 28) + (1 << 24) + (0 << 20) + 1
    i2 = (ADDI << 28) + (2 << 24) + (0 << 20) + 2
    i3 = (ADD << 28) + (3 << 24) + (1 << 20) + (1 << 16)
    i4 = (ADD << 28) + (4 << 24) + (2 << 20) + (2 << 16)
    i5 = (BEQ << 28) + (3 << 20) + (4 << 16) + 3
    i6 = (ADDI << 28) + (8 << 24) + (0 << 20) + 10
    i7 = (JAL << 28) + (0 << 24) + 2
    i8 = (ADDI << 28) + (8 << 24) + (0 << 20) + 1000
    i9 = (SW << 28) + (2 << 20) + (8 << 16) + 10
    i10 = (LW << 28) + (5 << 24) + (8 << 20) + 10
    i11 = (RETURN << 28)

    cpu.mem[100] = i0
    cpu.mem[101] = i1
    cpu.mem[102] = i2
    cpu.mem[103] = i3
    cpu.mem[104] = i4
    cpu.mem[105] = i5
    cpu.mem[106] = i6
    cpu.mem[107] = i7
    cpu.mem[108] = i8
    cpu.mem[109] = i9
    cpu.mem[110] = i10
    cpu.mem[111] = i11

    cpu.pc = 100

    while True:
        instruction = cpu.fetch()
        instruction = cpu.decode(instruction)
        cpu.exec(instruction)
        if instruction.opcode == RETURN:
            break

    validate_run(cpu.mem, cpu.regs)


main()
