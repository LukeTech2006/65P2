class register:
    def __init__(self, size: int, preLoad = 0) -> None:
        self.register = str()
        self.size = size*8
        for i in range(self.size): self.register += '0'
        self.set(preLoad)

    def set(self, value: int) -> None:
        if len(bin(value)[2:]) <= self.size:
            self.register = bin(value)[2:].rjust(self.size, '0')
        else:
            self.register = bin(value)[-self.size:]
    
    def get(self) -> int:
        return int(self.register, 2)

class statusRegister:
    def __init__(self) -> None:
        self.register = '00100000'
    
    def setNegative(self) -> None:
        newState = [x for x in self.register]
        newState[0] = '1'
        self.register = ''.join(newState)

    def clearNegative(self) -> None:
        newState = [x for x in self.register]
        newState[0] = '0'
        self.register = ''.join(newState)
    
    def getNegative(self) -> int:
        return int(self.register[0])

    def setOverflow(self) -> None:
        newState = [x for x in self.register]
        newState[1] = '1'
        self.register = ''.join(newState)

    def clearOverflow(self) -> None:
        newState = [x for x in self.register]
        newState[1] = '0'
        self.register = ''.join(newState)

    def getOverflow(self) -> int:
        return int(self.register[1])

    def setBreak(self) -> None:
        newState = [x for x in self.register]
        newState[3] = '1'
        self.register = ''.join(newState)

    def clearBreak(self) -> None:
        newState = [x for x in self.register]
        newState[3] = '0'
        self.register = ''.join(newState)

    def getBreak(self) -> int:
        return int(self.register[3])

    def setDecimal(self) -> None:
        newState = [x for x in self.register]
        newState[4] = '1'
        self.register = ''.join(newState)

    def clearDecimal(self) -> None:
        newState = [x for x in self.register]
        newState[4] = '0'
        self.register = ''.join(newState)

    def getDecimal(self) -> int:
        return int(self.register[4])

    def setInterrupt(self) -> None:
        newState = [x for x in self.register]
        newState[5] = '1'
        self.register = ''.join(newState)

    def clearInterrupt(self) -> None:
        newState = [x for x in self.register]
        newState[5] = '0'
        self.register = ''.join(newState)

    def getInterrupt(self) -> int:
        return int(self.register[5])

    def setZero(self) -> None:
        newState = [x for x in self.register]
        newState[6] = '1'
        self.register = ''.join(newState)

    def clearZero(self) -> None:
        newState = [x for x in self.register]
        newState[6] = '0'
        self.register = ''.join(newState)

    def getZero(self) -> int:
        return int(self.register[6])

    def setCarry(self) -> None:
        newState = [x for x in self.register]
        newState[7] = '1'
        self.register = ''.join(newState)

    def clearCarry(self) -> None:
        newState = [x for x in self.register]
        newState[7] = '0'
        self.register = ''.join(newState)

    def getCarry(self) -> int:
        return int(self.register[7])

class stackHandler:
    def __init__(self) -> None:
        pass

    def push(self, value: int) -> None: # type: ignore
        stackpointer = SP.get()
        SP.set(0x01FF) if stackpointer - 1 < 0x100 else SP.set(stackpointer - 1)

        stackpointer = SP.get()
        main_memory.write(stackpointer, value if instr.check_oper(value, 1) else 0xFF)
        
    def pop(self) -> int:
        stackpointer = SP.get()
        stack_element = main_memory.read(stackpointer)
        SP.set(0x0100) if stackpointer + 1 > 0x01FF else SP.set(stackpointer + 1)
        return stack_element

class prgmCounterHandler:
    def __init__(self) -> None:
        raise NotImplementedError

    def increment(self) -> None:
        ...

    def jmpRelative(self, oper: int) -> None:
        ...
    
    def jmpAbsolute(self, oper: int) -> None:
        ...

class aMode:
    implied = 0
    immediate = 1
    absolute = 2; absolute_x = 21; absolute_y = 22
    relative = 3
    indirect = 4; x_indirect = 41; indirect_y = 42
    zeropage = 5; zeropage_x = 51; zeropage_y = 52

class instructionHandler:
    def __init__(self) -> None:
        pass
    
    def check_oper(self, oper: int, size: int) -> bool:
        oper_hex = hex(oper)[2:].rjust(size*2, '0')
        if len(oper_hex) == size*2: return True
        else: return False

    def _adc(self, addressing: int, oper: int) -> None:
        match addressing:
            case aMode.immediate:
                if self.check_oper(oper, 1):
                    accumulator = AC.get()
                    accumulator += oper
                else: raise ValueError(f'Operand {hex(oper)} invalid for addressing mode!')
            case aMode.zeropage:
                if self.check_oper(oper, 1):
                    accumulator = AC.get()
                    accumulator += main_memory.read(0x00 + oper)
                else: raise ValueError(f'Operand {hex(oper)} invalid for addressing mode!')
            case aMode.zeropage_x:
                if self.check_oper(oper, 1):
                    accumulator = AC.get()
                    accumulator += main_memory.read(0x00 + oper + XR.get())
                else: raise ValueError(f'Operand {hex(oper)} invalid for addressing mode!')
            case aMode.absolute:
                if self.check_oper(oper, 2):
                    accumulator = AC.get()
                    accumulator += main_memory.read(oper)
                else: raise ValueError(f'Operand {hex(oper)} invalid for addressing mode!')
            case aMode.absolute_x:
                if self.check_oper(oper, 2):
                    accumulator = AC.get()
                    accumulator += main_memory.read(oper + XR.get())
                else: raise ValueError(f'Operand {hex(oper)} invalid for addressing mode!')
            case aMode.absolute_y:
                if self.check_oper(oper, 2):
                    accumulator = AC.get()
                    accumulator += main_memory.read(oper + YR.get())
                else: raise ValueError(f'Operand {hex(oper)} invalid for addressing mode!')
            case aMode.x_indirect:
                if self.check_oper(oper, 2):
                    accumulator = AC.get()
                    lo_byte, hi_byte = main_memory.read(oper + XR.get()), main_memory.read(oper + XR.get() + 1)
                    lo_byte, hi_byte = hex(lo_byte)[2:].rjust(2, '0'), hex(hi_byte)[2:].rjust(2, '0')
                    accumulator += main_memory.read(int(hi_byte + lo_byte, 16))
                else: raise ValueError(f'Operand {hex(oper)} invalid for addressing mode!')
            case aMode.indirect_y:
                if self.check_oper(oper, 2):
                    accumulator = AC.get()
                    lo_byte, hi_byte = main_memory.read(oper), main_memory.read(oper + 1)
                    lo_byte, hi_byte = hex(lo_byte)[2:].rjust(2, '0'), hex(hi_byte)[2:].rjust(2, '0')
                    accumulator += main_memory.read(int(hi_byte + lo_byte, 16) + YR.get())
                else: raise ValueError(f'Operand {hex(oper)} invalid for addressing mode!')
            case _: raise TypeError('Invalid addressing mode!')

        #if carry set, add 1
        if P.getCarry() == 1: accumulator += 1
        
        #drop upper bit(s) and set carry, if necessary
        if accumulator <= 0xff:
            AC.set(accumulator)
        else:
            P.setCarry()
            while accumulator > 0xff: accumulator -= 0x100
            AC.set(accumulator)

        #check zero
        if AC.get() == 0: P.setZero()
        else: P.clearZero()

        #check negative
        if AC.get() >= 0x80: P.setNegative()
        else: P.clearNegative()

        return

    def _and(self, addressing: int, oper: int) -> None:
        match addressing:
            case aMode.immediate:
                if self.check_oper(oper, 1):
                    accumulator = AC.get()
                    accumulator &= oper
                else: raise ValueError(f'Operand {hex(oper)} invalid for addressing mode!')
            case aMode.zeropage:
                if self.check_oper(oper, 1):
                    accumulator = AC.get()
                    accumulator &= main_memory.read(0x00 + oper)
                else: raise ValueError(f'Operand {hex(oper)} invalid for addressing mode!')
            case aMode.zeropage_x:
                if self.check_oper(oper, 1):
                    accumulator = AC.get()
                    accumulator &= main_memory.read(0x00 + oper + XR.get())
                else: raise ValueError(f'Operand {hex(oper)} invalid for addressing mode!')
            case aMode.absolute:
                if self.check_oper(oper, 2):
                    accumulator = AC.get()
                    accumulator &= main_memory.read(oper)
                else: raise ValueError(f'Operand {hex(oper)} invalid for addressing mode!')
            case aMode.absolute_x:
                if self.check_oper(oper, 2):
                    accumulator = AC.get()
                    accumulator &= main_memory.read(oper + XR.get())
                else: raise ValueError(f'Operand {hex(oper)} invalid for addressing mode!')
            case aMode.absolute_y:
                if self.check_oper(oper, 2):
                    accumulator = AC.get()
                    accumulator &= main_memory.read(oper + YR.get())
                else: raise ValueError(f'Operand {hex(oper)} invalid for addressing mode!')
            case aMode.x_indirect:
                if self.check_oper(oper, 2):
                    accumulator = AC.get()
                    lo_byte, hi_byte = main_memory.read(oper + XR.get()), main_memory.read(oper + XR.get() + 1)
                    lo_byte, hi_byte = hex(lo_byte)[2:].rjust(2, '0'), hex(hi_byte)[2:].rjust(2, '0')
                    accumulator &= main_memory.read(int(hi_byte + lo_byte, 16))
                else: raise ValueError(f'Operand {hex(oper)} invalid for addressing mode!')
            case aMode.indirect_y:
                if self.check_oper(oper, 2):
                    accumulator = AC.get()
                    lo_byte, hi_byte = main_memory.read(oper), main_memory.read(oper + 1)
                    lo_byte, hi_byte = hex(lo_byte)[2:].rjust(2, '0'), hex(hi_byte)[2:].rjust(2, '0')
                    accumulator &= main_memory.read(int(hi_byte + lo_byte, 16) + YR.get())
                else: raise ValueError(f'Operand {hex(oper)} invalid for addressing mode!')
            case _: raise TypeError('Invalid addressing mode!')

        #check zero
        if AC.get() == 0: P.setZero()
        else: P.clearZero()

        #check negative
        if AC.get() >= 0x80: P.setNegative()
        else: P.clearNegative()

        #update accumulator register
        AC.set(accumulator)
        return

    def _asl(self, addressing: int, oper: int) -> None:
            match addressing:
                case aMode.implied: accumulator = AC.get()
                case aMode.zeropage: accumulator = main_memory.read(oper) if self.check_oper(oper, 1) else ...
                case aMode.zeropage_x: accumulator = main_memory.read(oper + XR.get()) if self.check_oper(oper, 1) else ...
                case aMode.absolute: accumulator = main_memory.read(oper) if self.check_oper(oper, 2) else ...
                case aMode.absolute_x: accumulator = main_memory.read(oper + XR.get()) if self.check_oper(oper, 2) else ...
                case _: raise TypeError('Invalid addressing mode!')
            if accumulator == ...: raise ValueError(f'Operand {hex(oper)} invalid for addressing mode!')

            if bin(accumulator)[2:].rjust(8, '0')[0] == '1': P.setCarry()
            else: P.clearCarry()

            accumulator <<= 1
            match addressing:
                case aMode.implied: AC.set(accumulator)
                case aMode.zeropage: main_memory.write(oper, accumulator) if self.check_oper(oper, 1) else ...
                case aMode.zeropage_x: main_memory.write(oper + XR.get(), accumulator) if self.check_oper(oper, 1) else ...
                case aMode.absolute: main_memory.write(oper, accumulator) if self.check_oper(oper, 2) else ...
                case aMode.absolute_x: main_memory.write(oper + XR.get(), accumulator) if self.check_oper(oper, 2) else ...

    def _bcc(self, addressing: int, oper: int) -> None:
        match addressing:
            case aMode.relative:
                if self.check_oper(oper, 1):
                    if P.getCarry() == 0:
                        accumulator = PC.get()
                        if oper > 0x80: PC.set(accumulator - (oper - 0x80) - 1)
                        else: PC.set(accumulator + oper - 1)
                else: raise ValueError(f'Operand {hex(oper)} invalid for addressing mode!')
            case _: raise TypeError('Invalid adressing mode!')
        return
    
    def _bcs(self, addressing: int, oper: int) -> None:
        match addressing:
            case aMode.relative:
                if self.check_oper(oper, 1):
                    if P.getCarry() == 1:
                        accumulator = PC.get()
                        if oper > 0x80: PC.set(accumulator - (oper - 0x80) - 1)
                        else: PC.set(accumulator + oper - 1)
                else: raise ValueError(f'Operand {hex(oper)} invalid for addressing mode!')
            case _: raise TypeError('Invalid adressing mode!')
        return
    
    def _beq(self, addressing: int, oper: int) -> None:
        match addressing:
            case aMode.relative:
                if self.check_oper(oper, 1):
                    if P.getZero() == 1:
                        accumulator = PC.get()
                        if oper > 0x80: PC.set(accumulator - (oper - 0x80) - 1)
                        else: PC.set(accumulator + oper - 1)
                else: raise ValueError(f'Operand {hex(oper)} invalid for addressing mode!')
            case _: raise TypeError('Invalid adressing mode!')
        return
    
    def _bit(self, addressing: int, oper: int) -> None:
        match addressing:
            case aMode.zeropage:
                if self.check_oper(oper, 1):
                    accumulator = [AC.get(), main_memory.read(oper)]
                    byte_operand = bin(accumulator[1])[2:].rjust(8, '0')
                    
                    P.setOverflow() if byte_operand[6] == '1' else P.clearOverflow()
                    P.setNegative() if byte_operand[7] == '1' else P.clearNegative()
                    P.setZero()     if accumulator[0] & accumulator[1] == 0 else ...
                else: raise ValueError(f'Operand {hex(oper)} invalid for addressing mode!')
            case aMode.absolute:
                if self.check_oper(oper, 2):
                    accumulator = [AC.get(), main_memory.read(oper)]
                    byte_operand = bin(accumulator[1])[2:].rjust(8, '0')
                    
                    P.setOverflow() if byte_operand[6] == '1' else P.clearOverflow()
                    P.setNegative() if byte_operand[7] == '1' else P.clearNegative()
                    P.setZero()     if accumulator[0] & accumulator[1] == 0 else ...
                else: raise ValueError(f'Operand {hex(oper)} invalid for addressing mode!')
            case _: raise TypeError('Invalid addressing mode!')

    def _bmi(self, addressing: int, oper: int) -> None:
        match addressing:
            case aMode.relative:
                if self.check_oper(oper, 1):
                    if P.getNegative() == 1:
                        accumulator = PC.get()
                        if oper > 0x80: PC.set(accumulator - (oper - 0x80) - 1)
                        else: PC.set(accumulator + oper - 1)
                else: raise ValueError(f'Operand {hex(oper)} invalid for addressing mode!')
            case _: raise TypeError('Invalid adressing mode!')
        return

    def _bne(self, addressing: int, oper: int) -> None:
        match addressing:
            case aMode.relative:
                if self.check_oper(oper, 1):
                    if P.getZero() == 0:
                        accumulator = PC.get()
                        if oper > 0x80: PC.set(accumulator - (oper - 0x80) - 1)
                        else: PC.set(accumulator + oper - 1)
                else: raise ValueError(f'Operand {hex(oper)} invalid for addressing mode!')
            case _: raise TypeError('Invalid adressing mode!')
        return

    def _bpl(self, addressing: int, oper: int) -> None:
        match addressing:
            case aMode.relative:
                if self.check_oper(oper, 1):
                    if P.getNegative() == 0:
                        accumulator = PC.get()
                        if oper > 0x80: PC.set(accumulator - (oper - 0x80) - 1)
                        else: PC.set(accumulator + oper - 1)
                else: raise ValueError(f'Operand {hex(oper)} invalid for addressing mode!')
            case _: raise TypeError('Invalid adressing mode!')
        return

    def _brk(self, addressing: int, oper: int) -> None:
        match addressing:
            case aMode.implied:
                lo_byte, hi_byte = hex(PC.get())[2:].rjust(2, '0')[2:4], hex(PC.get())[2:].rjust(2, '0')[-2:]

            case _: raise TypeError('Invalid addressing mode!')

class memoryRegion:
    def __init__(self, start: int, size: int, mode: str) -> None:
        if len(mode) <= 2: self.mode = mode.lower()
        else: raise ValueError
        self.start = start; self.size = size + 1

class memoryHandler:
    def __init__(self, memoryMap: tuple[memoryRegion, ...]) -> None:
        self.memMap = memoryMap
        self.memory = list(list(int(0) for j in range(0x100)) for i in range(0x100))
        
        #with open('memdump.txt', 'w') as file:
        #    for page in self.memory: file.write(''.join(hex(val)[2:].rjust(2, '0') + ' ' for val in page) + '\n')
        #    file.close()
    
    def load_address(self, address: int) -> tuple[int, int]:
        full_address = hex(address)[2:].rjust(4, '0')
        hi_addr = full_address[:2]
        lo_addr = full_address[2:]
        return (int(hi_addr, 16), int(lo_addr, 16))

    def check_address(self, address: int, check_for: str) -> bool:
        for region in self.memMap:
            if address in range(region.start, region.start + region.size) and region.mode.find(check_for) == -1: return False
            elif address in range(region.start, region.start + region.size): return True
        return False

    def read(self, address: int) -> int:
        if self.check_address(address, 'r'):
            hi_byte, lo_byte = self.load_address(address)
            return self.memory[hi_byte][lo_byte]
        else: raise MemoryError(f'Memory at {hex(address)} not readable!')
    
    def write(self, address: int, value: int) -> None:
        #check if memory location is writable
        if self.check_address(address, 'w'):
            hi_byte, lo_byte = self.load_address(address)
            if value <= 0xff: self.memory[hi_byte][lo_byte] = value
            else: self.memory[hi_byte][lo_byte] = int(bin(value)[-8:], 2)
        else: raise MemoryError(f'Memory at {hex(address)} not writable!')

#define registers:
#   - PC:       program Counter (2 byte)
#   - AC:       accumulator (1 byte)
#   - XR, YR:   X, Y index register (1 byte)
#   - SP:       stack pointer (1 byte)
#   - P:        processor status register (1 byte)

PC = prgmCounterHandler()
AC = register(0x01)
XR = register(0x01)
YR = register(0x01)
SP = register(0x01, 0x01ff)
P  = statusRegister()

#define memory map for this 6502
#   - zeropage ram: $0000 - $00FF
#   - stack:        $0100 - $01FF
#   - program rom:  $0200 - $2FFF
#   - main ram:     $3000 - $EFFF
#   - i/o 0:        $FD00 - $FDFF
#   - i/o 1:        $FE00 - $FEFF
#   - vectors:      $FFFA - $FFFF
#       -> NMI:     $FFFA (LSB), $FFFB (MSB)
#       -> RESET:   $FFFC (LSB), $FFFD (MSB)
#       -> IRQ/BRK: $FFFE (LSB), $FFFF (MSB)

memoryMap = (
    memoryRegion(0x0000, 0x00FF, 'rw'),     #zeropage ram
    memoryRegion(0x0100, 0x00FF, 'rw'),     #stack
    memoryRegion(0x0200, 0x2DFF, 'r'),      #program rom
    memoryRegion(0x3000, 0xBFFF, 'rw'),     #main ram
    memoryRegion(0xFD00, 0x00FF, 'rw'),     #i/o 0
    memoryRegion(0xFE00, 0x00FF, 'rw'),     #i/o 1
    memoryRegion(0xFFFA, 0x0005, 'rw'),     #vectors
)

main_memory = memoryHandler(memoryMap)      #initialize memory handler w/ memory map
instr = instructionHandler()                #initialize instruction handler methods
stack = stackHandler()                      #initialize stack handler methods

print(AC.get(), P.register)
instr._adc(aMode.immediate, 0x08)
print(AC.get(), P.register)
instr._asl(aMode.implied, 0)
print(AC.get(), P.register)

#from os import system; system('pause')