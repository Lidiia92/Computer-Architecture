"""CPU functionality."""

import sys

HLT =  0b00000001
LDI = 0b10000010
PRN = 0b01000111
MUL = 0b10100010
POP = 0b01000110
PUSH = 0b01000101
CALL = 0b01010000
RET = 0b00010001
ADD = 0b10100000
CMP = 0b10100111
JMP = 0b01010100
JEQ = 0b01010101
JNE = 0b01010110

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.memory = [0] * 256
        self.registers = [0] * 8

        #Internal registers
        self.pc = 0

        self.sp = 7
        self.flags = 0


    def ram_read(self, address):
        return self.memory[address]

    def raw_write(self, address, value):
        self.memory[address] = value

    # def load(self):
    #     """Load a program into memory."""
        
    #     address = 0

    #     # For now, we've just hardcoded a program:

    #     program = [
    #         # From print8.ls8
    #         0b10000010, # LDI R0,8
    #         0b00000000,
    #         0b00001000,
    #         0b10000010, # LDI R1,9
    #         0b00000001,
    #         0b00001001,
    #         0b10100010, # MUL R0,R1
    #         0b00000000,
    #         0b00000001,
    #         0b01000111, # PRN R0
    #         0b00000000,
    #         0b00000001, # HLT
    #     ]

    #     for instruction in program:
    #         self.memory[address] = instruction
    #         address += 1

    def load(self):
        address = 0
        
        with open(sys.argv[1]) as f:
            for line in f:
                # Process comments:
                # Ignore anything after a # symbol
                # 
                comment_split = line.split("#")
                
                # Convert any numbers from binary strings to integers
                # 
                num = comment_split[0].strip()
                try:
                    val = int(num, 2)
                except ValueError:
                    continue
                self.memory[address] = val
                address += 1
                # print(f"{val:08b}: {val:d}")
    
    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.registers[reg_a] += self.registers[reg_b]
        #elif op == "SUB": etc
        elif op == "MUL":
            self.registers[reg_a] *= self.registers[reg_b]

        elif op == "CMP":
            #Flags # 0b00000LGE
            if self.registers[reg_a] == self.registers[reg_b]:
                self.flags = 0b00000001
            elif self.registers[reg_a] < self.registers[reg_b]:
                self.flags = 0b0000100
            elif self.registers[reg_a] > self.registers[reg_b]:
                self.flags = 0b0000010

        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.registers[i], end='')

        print()


    def run(self):
        """Run the CPU."""

        operations = {
            "HLT":  HLT,
            "LDI": LDI,
            "PRN": PRN,
            "MUL": MUL,
            "POP": POP,
            "PUSH": PUSH,
            "CALL": CALL,
            "RET": RET,
            "ADD": ADD,
            "CMP": CMP,
            "JMP": JMP,
            "JEQ": JEQ,
            "JNE": JNE,
        }

        running = True

        while running:
            register = self.memory[self.pc]
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            #LDI: load "immediate", store a value in a register, or "set this register to this value".
            if register == operations["LDI"]:
                self.registers[operand_a] = operand_b 
                self.pc += 3

            #HLT: halt the CPU and exit the emulator.
            elif register == operations["HLT"]:
                running = False

            #PRN: a pseudo-instruction that prints the numeric value stored in a register.
            elif register == operations["PRN"]:
                print("PRN", self.registers[operand_a]) # Print contents of the memory
                self.pc += 2

            elif register == operations["MUL"]:
                result = self.alu("MUL", operand_a, operand_b)
                print("MUL", result)
                self.pc += 3 
                
            elif register == operations["PUSH"]:
                value = self.registers[operand_a]
                # Decrement the SP.
                self.registers[self.sp] -= 1
                # Copy the value in the given register to the address pointed to by SP.
                self.memory[self.registers[self.sp]] = value
                self.pc += 2
                
            elif register == operations["POP"]:

                value = self.memory[self.registers[self.sp]]
                # Copy the value from the address pointed to by SP to the given register.
                self.registers[operand_a] = value
                # Increment SP.
                self.registers[self.sp] += 1
                self.pc += 2

            elif register == operations["CALL"]:
                self.registers[self.sp] -= 1
                self.memory[self.registers[self.sp]] = self.pc + 2
                self.pc = self.registers[operand_a]

            elif register == operations["RET"]:
                self.pc = self.memory[self.registers[self.sp]]
                self.registers[self.sp] += 1

            elif register == operations["ADD"]:
                self.registers[operand_a] += self.registers[operand_b] 
                self.pc += 3




            else:
                print(f"Unknown instruction: {register}")
                sys.exit(1)
