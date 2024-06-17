class register:
    def __init__(self, size: int, preLoad = 0) -> None:
        self.register = preLoad
        self.size = size*8

    def set(self, value: int) -> None:
        self.register = value
    
    def get(self) -> int:
        return self.register

class statusRegister(register):
    def __init__(self) -> None:
        super().__init__(1, 0b00100000)
    
    def setNegative(self) -> None:
        self.register |= 0x80

    def clearNegative(self) -> None:
        self.register &= 0x7F
    
    def getNegative(self) -> int:
        return 1 if self.register & 0x80 > 0 else 0

    def setOverflow(self) -> None:
        self.register |= 0x40

    def clearOverflow(self) -> None:
        self.register &= 0xBF

    def getOverflow(self) -> int:
        return 1 if self.register & 0x40 > 0 else 0

    def setBreak(self) -> None:
        self.register |= 0x10

    def clearBreak(self) -> None:
        self.register &= 0xEF

    def getBreak(self) -> int:
        return 1 if self.register & 0x10 > 0 else 0

    def setDecimal(self) -> None:
        self.register |= 0x08

    def clearDecimal(self) -> None:
        self.register &= 0xF7

    def getDecimal(self) -> int:
        return 1 if self.register & 0x08 > 0 else 0

    def setInterrupt(self) -> None:
        self.register |= 0x04

    def clearInterrupt(self) -> None:
        self.register &= 0xFB

    def getInterrupt(self) -> int:
        return 1 if self.register & 0x04 > 0 else 0

    def setZero(self) -> None:
        self.register |= 0x02

    def clearZero(self) -> None:
        self.register &= 0xFD

    def getZero(self) -> int:
        return 1 if self.register & 0x02 > 0 else 0

    def setCarry(self) -> None:
        self.register |= 0x01

    def clearCarry(self) -> None:
        self.register &= 0xFE

    def getCarry(self) -> int:
        return 1 if self.register & 0x01 > 0 else 0

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

class prgmCounterHandler(register):
    def __init__(self) -> None:
        super().__init__(0x02)

    def increment(self) -> None:
        accumulator = self.get()
        self.set(accumulator + 1)

    def jmpRelative(self, oper: int) -> None:
        accumulator = [self.get(), oper]
        if accumulator[1] < 128: self.set(accumulator[0] + accumulator[1])
        else:
            accumulator[1] = 128 - (accumulator[1] - 128)
            self.set(accumulator[0] - accumulator[1])
            
    def jmpAbsolute(self, oper: int) -> None:
        accumulator = oper
        self.set(accumulator)

class aMode:
    implied = 0
    immediate = 1
    absolute = 2; absolute_x = 21; absolute_y = 22
    relative = 3
    indirect = 4; x_indirect = 41; indirect_y = 42
    zeropage = 5; zeropage_x = 51; zeropage_y = 52

class modeHandler:
    stopped = 0
    running = 1
    interrupt = 2
    mode = 0
    
    def __init__(self) -> None:
        pass
    
    def setMode(self, mode: int) -> None:
        self.mode = mode
    
    def getMode(self) -> int:
        return self.mode
        
class instructionHandler:
    def __init__(self) -> None:
        pass
    
    def check_oper(self, oper: int, size: int) -> bool:
        return True if oper < pow(2, size*8) else False

    def _adc(self, addressing: int, oper: int) -> None:
        if addressing == aMode.immediate:
            if self.check_oper(oper, 1):
                accumulator = AC.get()
                accumulator += oper
            else: raise ValueError(f'Operand {hex(oper)} invalid for addressing mode!')
        elif addressing == aMode.zeropage:
            if self.check_oper(oper, 1):
                accumulator = AC.get()
                accumulator += main_memory.read(0x00 + oper)
            else: raise ValueError(f'Operand {hex(oper)} invalid for addressing mode!')
        elif addressing == aMode.zeropage_x:
            if self.check_oper(oper, 1):
                accumulator = AC.get()
                accumulator += main_memory.read(0x00 + oper + XR.get())
            else: raise ValueError(f'Operand {hex(oper)} invalid for addressing mode!')
        elif addressing == aMode.absolute:
            if self.check_oper(oper, 2):
                accumulator = AC.get()
                accumulator += main_memory.read(oper)
            else: raise ValueError(f'Operand {hex(oper)} invalid for addressing mode!')
        elif addressing == aMode.absolute_x:
            if self.check_oper(oper, 2):
                accumulator = AC.get()
                accumulator += main_memory.read(oper + XR.get())
            else: raise ValueError(f'Operand {hex(oper)} invalid for addressing mode!')
        elif addressing == aMode.absolute_y:
            if self.check_oper(oper, 2):
                accumulator = AC.get()
                accumulator += main_memory.read(oper + YR.get())
            else: raise ValueError(f'Operand {hex(oper)} invalid for addressing mode!')
        elif addressing == aMode.x_indirect:
            if self.check_oper(oper, 2):
                accumulator = AC.get()
                lo_byte, hi_byte = main_memory.read(oper + XR.get()), main_memory.read(oper + XR.get() + 1)
                lo_byte, hi_byte = hex(lo_byte)[2:].rjust(2, '0'), hex(hi_byte)[2:].rjust(2, '0')
                accumulator += main_memory.read(int(hi_byte + lo_byte, 16))
            else: raise ValueError(f'Operand {hex(oper)} invalid for addressing mode!')
        elif addressing == aMode.indirect_y:
            if self.check_oper(oper, 2):
                accumulator = AC.get()
                lo_byte, hi_byte = main_memory.read(oper), main_memory.read(oper + 1)
                lo_byte, hi_byte = hex(lo_byte)[2:].rjust(2, '0'), hex(hi_byte)[2:].rjust(2, '0')
                accumulator += main_memory.read(int(hi_byte + lo_byte, 16) + YR.get())
            else: raise ValueError(f'Operand {hex(oper)} invalid for addressing mode!')
        else: raise TypeError('Invalid addressing mode!')

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
        if addressing == aMode.immediate:
            if self.check_oper(oper, 1):
                accumulator = AC.get()
                accumulator &= oper
            else: raise ValueError(f'Operand {hex(oper)} invalid for addressing mode!')
        elif addressing == aMode.zeropage:
            if self.check_oper(oper, 1):
                accumulator = AC.get()
                accumulator &= main_memory.read(0x00 + oper)
            else: raise ValueError(f'Operand {hex(oper)} invalid for addressing mode!')
        elif addressing == aMode.zeropage_x:
            if self.check_oper(oper, 1):
                accumulator = AC.get()
                accumulator &= main_memory.read(0x00 + oper + XR.get())
            else: raise ValueError(f'Operand {hex(oper)} invalid for addressing mode!')
        elif addressing == aMode.absolute:
            if self.check_oper(oper, 2):
                accumulator = AC.get()
                accumulator &= main_memory.read(oper)
            else: raise ValueError(f'Operand {hex(oper)} invalid for addressing mode!')
        elif addressing == aMode.absolute_x:
            if self.check_oper(oper, 2):
                accumulator = AC.get()
                accumulator &= main_memory.read(oper + XR.get())
            else: raise ValueError(f'Operand {hex(oper)} invalid for addressing mode!')
        elif addressing == aMode.absolute_y:
            if self.check_oper(oper, 2):
                accumulator = AC.get()
                accumulator &= main_memory.read(oper + YR.get())
            else: raise ValueError(f'Operand {hex(oper)} invalid for addressing mode!')
        elif addressing == aMode.x_indirect:
            if self.check_oper(oper, 2):
                accumulator = AC.get()
                lo_byte, hi_byte = main_memory.read(oper + XR.get()), main_memory.read(oper + XR.get() + 1)
                lo_byte, hi_byte = hex(lo_byte)[2:].rjust(2, '0'), hex(hi_byte)[2:].rjust(2, '0')
                accumulator &= main_memory.read(int(hi_byte + lo_byte, 16))
            else: raise ValueError(f'Operand {hex(oper)} invalid for addressing mode!')
        elif addressing == aMode.indirect_y:
            if self.check_oper(oper, 2):
                accumulator = AC.get()
                lo_byte, hi_byte = main_memory.read(oper), main_memory.read(oper + 1)
                lo_byte, hi_byte = hex(lo_byte)[2:].rjust(2, '0'), hex(hi_byte)[2:].rjust(2, '0')
                accumulator &= main_memory.read(int(hi_byte + lo_byte, 16) + YR.get())
            else: raise ValueError(f'Operand {hex(oper)} invalid for addressing mode!')
        else: raise TypeError('Invalid addressing mode!')

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
            
            if addressing == aMode.implied: accumulator = AC.get()
            elif addressing == aMode.zeropage: accumulator = main_memory.read(oper) if self.check_oper(oper, 1) else ...
            elif addressing == aMode.zeropage_x: accumulator = main_memory.read(oper + XR.get()) if self.check_oper(oper, 1) else ...
            elif addressing == aMode.absolute: accumulator = main_memory.read(oper) if self.check_oper(oper, 2) else ...
            elif addressing == aMode.absolute_x: accumulator = main_memory.read(oper + XR.get()) if self.check_oper(oper, 2) else ...
            else: raise TypeError('Invalid addressing mode!')
            if accumulator == ...: raise ValueError(f'Operand {hex(oper)} invalid for addressing mode!')

            if bin(accumulator)[2:].rjust(8, '0')[0] == '1': P.setCarry()
            else: P.clearCarry()

            accumulator <<= 1
            
            if addressing == aMode.implied: AC.set(accumulator)
            elif addressing == aMode.zeropage: main_memory.write(oper, accumulator) if self.check_oper(oper, 1) else ...
            elif addressing == aMode.zeropage_x: main_memory.write(oper + XR.get(), accumulator) if self.check_oper(oper, 1) else ...
            elif addressing == aMode.absolute: main_memory.write(oper, accumulator) if self.check_oper(oper, 2) else ...
            elif addressing == aMode.absolute_x: main_memory.write(oper + XR.get(), accumulator) if self.check_oper(oper, 2) else ...

    def _bcc(self, addressing: int, oper: int) -> None:
        if addressing == aMode.relative:
            if self.check_oper(oper, 1):
                if P.getCarry() == 0: PC.jmpRelative(oper)
            else: raise ValueError(f'Operand {hex(oper)} invalid for addressing mode!')
        else: raise TypeError('Invalid adressing mode!')
        return
    
    def _bcs(self, addressing: int, oper: int) -> None:
        if addressing == aMode.relative:
            if self.check_oper(oper, 1):
                if P.getCarry() == 1: PC.jmpRelative(oper)
            else: raise ValueError(f'Operand {hex(oper)} invalid for addressing mode!')
        else: raise TypeError('Invalid adressing mode!')
        return
    
    def _beq(self, addressing: int, oper: int) -> None:
        if addressing == aMode.relative:
            if self.check_oper(oper, 1):
                if P.getZero() == 1: PC.jmpRelative(oper)
            else: raise ValueError(f'Operand {hex(oper)} invalid for addressing mode!')
        else: raise TypeError('Invalid adressing mode!')
        return
    
    def _bit(self, addressing: int, oper: int) -> None:
        if addressing == aMode.zeropage:
            if self.check_oper(oper, 1):
                accumulator = [AC.get(), main_memory.read(oper)]
                byte_operand = bin(accumulator[1])[2:].rjust(8, '0')
                
                P.setOverflow() if byte_operand[6] == '1' else P.clearOverflow()
                P.setNegative() if byte_operand[7] == '1' else P.clearNegative()
                P.setZero()     if accumulator[0] & accumulator[1] == 0 else ...
            else: raise ValueError(f'Operand {hex(oper)} invalid for addressing mode!')
        elif addressing == aMode.absolute:
            if self.check_oper(oper, 2):
                accumulator = [AC.get(), main_memory.read(oper)]
                byte_operand = bin(accumulator[1])[2:].rjust(8, '0')
                
                P.setOverflow() if byte_operand[6] == '1' else P.clearOverflow()
                P.setNegative() if byte_operand[7] == '1' else P.clearNegative()
                P.setZero()     if accumulator[0] & accumulator[1] == 0 else ...
            else: raise ValueError(f'Operand {hex(oper)} invalid for addressing mode!')
        else: raise TypeError('Invalid addressing mode!')

    def _bmi(self, addressing: int, oper: int) -> None:
        if addressing == aMode.relative:
            if self.check_oper(oper, 1):
                if P.getNegative() == 1: PC.jmpRelative(oper)
            else: raise ValueError(f'Operand {hex(oper)} invalid for addressing mode!')
        else: raise TypeError('Invalid adressing mode!')
        return

    def _bne(self, addressing: int, oper: int) -> None:
        if addressing == aMode.relative:
            if self.check_oper(oper, 1):
                if P.getZero() == 0: PC.jmpRelative(oper)
            else: raise ValueError(f'Operand {hex(oper)} invalid for addressing mode!')
        else: raise TypeError('Invalid adressing mode!')
        return

    def _bpl(self, addressing: int, oper: int) -> None:
        if addressing == aMode.relative:
            if self.check_oper(oper, 1):
                if P.getNegative() == 0: PC.jmpRelative(oper)
            else: raise ValueError(f'Operand {hex(oper)} invalid for addressing mode!')
        else: raise TypeError('Invalid adressing mode!')
        return

    def _brk(self, addressing: int, oper: int) -> None:
        if addressing == aMode.implied:
            lo_byte, hi_byte = PC.get() & 0x00ff, PC.get() & 0xff00
            stack.push(lo_byte); stack.push(hi_byte)

            statusbits = str()
            for x in [P.getNegative(), P.getOverflow(), 1, 1, P.getDecimal(), P.getInterrupt(), P.getZero(), P.getCarry()]:
                statusbits += str(x)
            stack.push(int(statusbits, 2))
            
            processor.setMode(modeHandler.interrupt)
                
        else: raise TypeError('Invalid addressing mode!')

    def _bvc(self, addressing: int, oper: int) -> None:
        if addressing == aMode.relative:
            if self.check_oper(oper, 1):
                if P.getOverflow() == 0: PC.jmpRelative(oper)
            else: raise ValueError(f'Operand {hex(oper)} invalid for addressing mode!')
        else: raise TypeError('Invalid adressing mode!')
        return

    def _bvs(self, addressing: int, oper: int) -> None:
        if addressing == aMode.relative:
            if self.check_oper(oper, 1):
                if P.getOverflow() == 1: PC.jmpRelative(oper)
            else: raise ValueError(f'Operand {hex(oper)} invalid for addressing mode!')
        else: raise TypeError('Invalid adressing mode!')
        return

    def _clc(self, addressing: int, oper: int) -> None:
        if addressing == aMode.implied: P.clearCarry()
        else: raise TypeError('Invalid addressing mode!')
            
    def _cld(self, addressing: int, oper: int) -> None:
        if addressing == aMode.implied: P.clearDecimal()
        else: raise TypeError('Invalid addressing mode!')
            
    def _cli(self, addressing: int, oper: int) -> None:
        if addressing == aMode.implied: P.clearInterrupt()
        else: raise TypeError('Invalid addressing mode!')
            
    def _clv(self, addressing: int, oper: int) -> None:
        if addressing == aMode.implied: P.clearOverflow()
        else: raise TypeError('Invalid addressing mode!')
            
    def _cmp(self, addressing: int, oper: int) -> None:
        if addressing == aMode.immediate:
            if self.check_oper(oper, 1):
                accumulator = oper
            else: raise ValueError(f'Operand {hex(oper)} invalid for addressing mode!')
        elif addressing == aMode.zeropage:
            if self.check_oper(oper, 1):
                accumulator = main_memory.read(0x00 + oper)
            else: raise ValueError(f'Operand {hex(oper)} invalid for addressing mode!')
        elif addressing == aMode.zeropage_x:
            if self.check_oper(oper, 1):
                accumulator = main_memory.read(oper + XR.get())
            else: raise ValueError(f'Operand {hex(oper)} invalid for addressing mode!')
        elif addressing == aMode.absolute:
            if self.check_oper(oper, 2):
                accumulator = main_memory.read(oper)
            else: raise ValueError(f'Operand {hex(oper)} invalid for addressing mode!')
        elif addressing == aMode.absolute_x:
            if self.check_oper(oper, 2):
                accumulator = main_memory.read(oper + XR.get())
            else: raise ValueError(f'Operand {hex(oper)} invalid for addressing mode!')
        elif addressing == aMode.absolute_y:
            if self.check_oper(oper, 2):
                accumulator = main_memory.read(oper + YR.get())
            else: raise ValueError(f'Operand {hex(oper)} invalid for addressing mode!')
        elif addressing == aMode.x_indirect:
            if self.check_oper(oper, 2):
                lo_byte, hi_byte = main_memory.read(oper + XR.get()), main_memory.read(oper + XR.get() + 1)
                lo_byte, hi_byte = hex(lo_byte)[2:].rjust(2, '0'), hex(hi_byte)[2:].rjust(2, '0')
                accumulator = main_memory.read(int(hi_byte + lo_byte, 16))
            else: raise ValueError(f'Operand {hex(oper)} invalid for addressing mode!')
        elif addressing == aMode.indirect_y:
            if self.check_oper(oper, 2):
                lo_byte, hi_byte = main_memory.read(oper), main_memory.read(oper + 1)
                lo_byte, hi_byte = hex(lo_byte)[2:].rjust(2, '0'), hex(hi_byte)[2:].rjust(2, '0')
                accumulator = main_memory.read(int(hi_byte + lo_byte, 16) + YR.get())
            else: raise ValueError(f'Operand {hex(oper)} invalid for addressing mode!')
        else: raise TypeError('Invalid addressing Mode!')
        
        accumulator = AC.get() - accumulator
        if accumulator == 0:
            P.clearNegative(); P.setZero(); P.setCarry()
        elif accumulator > 0:
            P.clearNegative() if oper & 0x80 == 0 else P.setNegative(); P.clearZero(); P.clearCarry()
        elif accumulator < 0:
            P.clearNegative() if oper & 0x80 == 0 else P.setNegative(); P.clearZero(); P.setCarry()

    def _cpx(self, addressing: int, oper: int) -> None:
        if addressing == aMode.immediate:
            if self.check_oper(oper, 1):
                accumulator = oper
            else: raise ValueError(f'Operand {hex(oper)} invalid for addressing mode!')
        elif addressing == aMode.zeropage:
            if self.check_oper(oper, 1):
                accumulator = main_memory.read(0x00 + oper)
            else: raise ValueError(f'Operand {hex(oper)} invalid for addressing mode!')
        elif addressing == aMode.absolute:
            if self.check_oper(oper, 2):
                accumulator = main_memory.read(oper)
            else: raise ValueError(f'Operand {hex(oper)} invalid for addressing mode!')
        else: raise TypeError('Invalid addressing Mode!')
        
        accumulator = XR.get() - accumulator
        if accumulator == 0:
            P.clearNegative(); P.setZero(); P.setCarry()
        elif accumulator > 0:
            P.clearNegative() if oper & 0x80 == 0 else P.setNegative(); P.clearZero(); P.clearCarry()
        elif accumulator < 0:
            P.clearNegative() if oper & 0x80 == 0 else P.setNegative(); P.clearZero(); P.setCarry()

    def _cpy(self, addressing: int, oper: int) -> None:
        if addressing == aMode.immediate:
            if self.check_oper(oper, 1):
                accumulator = oper
            else: raise ValueError(f'Operand {hex(oper)} invalid for addressing mode!')
        elif addressing == aMode.zeropage:
            if self.check_oper(oper, 1):
                accumulator = main_memory.read(oper % 256)
            else: raise ValueError(f'Operand {hex(oper)} invalid for addressing mode!')
        elif addressing == aMode.absolute:
            if self.check_oper(oper, 2):
                accumulator = main_memory.read(oper)
            else: raise ValueError(f'Operand {hex(oper)} invalid for addressing mode!')
        else: raise TypeError('Invalid addressing Mode!')
        
        accumulator = YR.get() - accumulator
        if accumulator == 0:
            P.clearNegative(); P.setZero(); P.setCarry()
        elif accumulator > 0:
            P.clearNegative() if oper & 0x80 == 0 else P.setNegative(); P.clearZero(); P.clearCarry()
        elif accumulator < 0:
            P.clearNegative() if oper & 0x80 == 0 else P.setNegative(); P.clearZero(); P.setCarry()

    #def _dec(self, addressing: int, oper: int) -> None:
        #if addressing == aMode.zeropage:
        #    if self.check_oper(oper, 2):
        #        accumulator = main_memory.read(oper % 256)
        #    else: raise ValueError(f'Operand {hex(oper)} invalid for addressing mode!')
        #elif addressing == aMode.zeropage_x:
        #    if self.check_oper(oper, 2):
        #        accumulator = main_memory.read((oper + XR.get()) % 256)
        #    else: raise ValueError(f'Operand {hex(oper)} invalid for addressing mode!')
        #elif addressing == aMode.absolute:
        #    if self.check_oper(oper, 3):
        #        accumulator = main_memory.read(oper)
        #    else: raise ValueError(f'Operand {hex(oper)} invalid for addressing mode!')
        #elif addressing == aMode.absolute_x:
        #    if self.check_oper(oper, 3):
        #        accumulator = main_memory.read(oper + XR.get())
        #    else: raise ValueError(f'Operand {hex(oper)} invalid for addressing mode!')
        #else: raise TypeError('Invalid addressing Mode!')
        
        #if accumulator == 0:
        #    P.clearNegative(); P.setZero(); P.setCarry()
        #elif accumulator > 0:
        #    P.clearNegative() if oper & 0x80 == 0 else P.setNegative(); P.clearZero(); P.clearCarry()
        #elif accumulator < 0:
        #    P.clearNegative() if oper & 0x80 == 0 else P.setNegative(); P.clearZero(); P.setCarry()

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
processor = modeHandler()                   #initialize mode handler methods

print(AC.get(), P.register)
instr._adc(aMode.immediate, 0x08)
print(AC.get(), P.register)
instr._asl(aMode.implied, 0)
print(AC.get(), P.register)

#from os import system; system('pause')