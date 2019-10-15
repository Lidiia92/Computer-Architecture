"""CPU functionality."""

import sys

HLT =  0b00000001
LDI = 0b10000010
PRN = 0b01000111
MUL = 0b10100010

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.memory = [0] * 256
        self.registers = [0] * 8

        #Internal registers
        self.pc = 0


    def ram_read(self, address):
        return self.memory[address]

    def raw_write(self, address, value):
        self.memory[address] = value

    def load(self):
        """Load a program into memory."""

        try:
            address = 0
        
            with open(sys.argv[1]) as f:
                for line in f:

                    # Process comments:
                    # Ignore anything after a # symbol
                    comment_split = line.split("#")

                    # Convert any numbers from binary strings to integers
                    num = comment_split[0].strip()
                    try:
                        val = int(num)
                    except ValueError:
                        continue
                    print(num)

                    self.memory[address] = val
                    address += 1

        except FileNotFoundError:
            print(f"{sys.argv[0]}: {sys.argv[1]} not found")
            sys.exit(2)
    
    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.registers[reg_a] += self.registers[reg_b]
        #elif op == "SUB": etc
        elif op == "MUL":
            self.registers[reg_a] *= self.registers[reg_b]
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
            "MUL": MUL
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
                self.alu("MUL", operand_a, operand_b)
                self.pc += 3 

            else:
                print(f"Unknown instruction: {register}")
                sys.exit(1)
