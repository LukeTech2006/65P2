class register:
    def __init__(self, size: int) -> None:
        self.register = str()
        self.size = size*8
        for i in range(size*8): self.register += '0'
        self.set(0)

    def set(self, value: int) -> None:
        if len(bin(value)[2:]) <= self.size:
            self.register = bin(value)[2:].ljust(self.size, '0')
        else:
            self.register = bin(value)[-self.size:]
    
    def get(self) -> int:
        return int(self.register, 2)

class statusRegister:
    def __init__(self) -> None:
        self.register = '00100000'
    
    def setNegative(self) -> None:
        newState = self.register.split()
        newState[0] = '1'
        self.register = ''.join(newState)

    def clearNegative(self) -> None:
        newState = self.register.split()
        newState[0] = '0'
        self.register = ''.join(newState)

    def setOverflow(self) -> None:
        newState = self.register.split()
        newState[1] = '1'
        self.register = ''.join(newState)

    def clearOverflow(self) -> None:
        newState = self.register.split()
        newState[1] = '0'
        self.register = ''.join(newState)

    def setBreak(self) -> None:
        newState = self.register.split()
        newState[3] = '1'
        self.register = ''.join(newState)

    def clearBreak(self) -> None:
        newState = self.register.split()
        newState[3] = '0'
        self.register = ''.join(newState)

    def setDecimal(self) -> None:
        newState = self.register.split()
        newState[4] = '1'
        self.register = ''.join(newState)

    def clearDecimal(self) -> None:
        newState = self.register.split()
        newState[4] = '0'
        self.register = ''.join(newState)

    def setInterrupt(self) -> None:
        newState = self.register.split()
        newState[5] = '1'
        self.register = ''.join(newState)

    def clearInterrupt(self) -> None:
        newState = self.register.split()
        newState[5] = '0'
        self.register = ''.join(newState)

    def setZero(self) -> None:
        newState = self.register.split()
        newState[6] = '1'
        self.register = ''.join(newState)

    def clearZero(self) -> None:
        newState = self.register.split()
        newState[6] = '0'
        self.register = ''.join(newState)

    def setCarry(self) -> None:
        newState = self.register.split()
        newState[7] = '1'
        self.register = ''.join(newState)

    def clearCarry(self) -> None:
        newState = self.register.split()
        newState[7] = '0'
        self.register = ''.join(newState)

class addressMode:
    implied = 0
    immediate = 1
    absolute = 2; absolute_x = 21; absolute_y = 22
    relative = 3
    indirect = 4; x_indirect = 41; indirect_y = 42
    zeropage = 5; zeropage_x = 51; zeropage_y = 52

class instruction:
    def __init__(self) -> None:
        pass

    instructions = {
        addressMode.implied: [],
        addressMode.immediate: [],
        addressMode.absolute: [],
        addressMode.absolute_x: [],
        addressMode.absolute_y: [],
        addressMode.relative: [],
        addressMode.indirect: [],
        addressMode.x_indirect: [],
        addressMode.indirect_y: [],
        addressMode.zeropage: [],
        addressMode.zeropage_x: [],
        addressMode.zeropage_y: [],
    }

class memoryRegion:
    def __init__(self, start: int, size: int, mode: str) -> None:
        if len(mode) <= 2: self.mode = mode.lower()
        else: raise ValueError
        self.start = start; self.size = size

class memory:
    def __init__(self, memoryMap: tuple[memoryRegion, ...]) -> None:
        self.memMap = memoryMap
        self.memory = list(list(int() for j in range(0xff)) for i in range(0xff))

        #initialize memory regions
        for region in memoryMap:
            hi_start, lo_start = self.load_address(region.start)
            hi_size, lo_size = self.load_address(region.size)
            for i in range(hi_start, hi_start + hi_size):
                for j in range(lo_start, lo_start + lo_size):
                    self.memory[i][j] = 0
        
        #with open('memdump.txt', 'w') as file:
        #    for page in self.memory: file.write(''.join(hex(val)[2:].ljust(2, '0') + ' ' for val in page) + '\n')
        #    file.close()
    
    def load_address(self, address: int) -> tuple[int, int]:
        full_address = hex(address)[2:].ljust(4, '0')
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
#   - PC: program Counter (2 byte)
#   - AC: accumulator (1 byte)
#   - XR, YR: X, Y index register (1 byte)
#   - SP: stack pointer (1 byte)
#   - P: processor status register (1 byte)

PC = register(0x02)
AC = register(0x01)
XR = register(0x01)
YR = register(0x01)
SP = register(0x01)
P  = statusRegister()

memoryMap = (
    memoryRegion(0x0000, 0x00FF, 'rw'),     #zeropage ram
    memoryRegion(0x0100, 0x00FF, 'rw'),     #stack
    memoryRegion(0x0200, 0x2DFF, 'r'),      #program rom
    memoryRegion(0x3000, 0xBFFF, 'rw'),     #main ram
    memoryRegion(0xFE00, 0x00FF, 'rw'),     #i/o 0
    memoryRegion(0xFF00, 0x00FF, 'rw')      #i/o 1
)

main_memory = memory(memoryMap)


AC.set(0xFF)
print(AC.register)
AC.set(AC.get() + 1)
print(AC.register)

from os import system; system('pause')