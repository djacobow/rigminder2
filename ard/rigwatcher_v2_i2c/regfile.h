#ifndef REGFILE_H
#define REGFILE_H

#include <Arduino.h>
#include <Stream.h>

template<size_t REG_COUNT>
class regfile_c {
    private:
        uint16_t registers[REG_COUNT];
        Stream *ser;
    public:
        regfile_c() {
          ser = 0;
        }
        void set_debug(Stream *nser) {
          ser = nser;
        }
        void clear() {
          for (uint8_t i=0;i<REG_COUNT;i++) registers[i] = 0;
        };
        void dump() {
            for (uint8_t i=0; i< REG_COUNT; i++) {
                if (ser) {
                    ser->print("i (");
                    ser->print(i,HEX);
                    ser->print(") ");
                    ser->println(registers[i],HEX);
                }
            }
        };
        uint16_t get(uint8_t addr) { return registers[addr & (REG_COUNT-1)]; }
        void set(uint8_t addr, uint16_t val) {
            registers[addr & (REG_COUNT-1)] = val;
        }
        uint16_t *getptr(uint8_t addr) {
            addr = addr % REG_COUNT;
            return &(registers[addr]);
        };
        uint32_t update(uint32_t input) {
            ser->print("input "); ser->println(input,HEX);
            uint8_t cmd = input >> 16;
            uint16_t arg = input & 0xffff;
            uint8_t addr = cmd & (REG_COUNT-1);
            uint8_t act = (cmd /REG_COUNT) & (REG_COUNT-1);
            if (ser) {
                ser->print("RF cmd  "); ser->print(cmd,HEX);
                ser->print(" arg  "); ser->print(arg,HEX);
                ser->print(" addr "); ser->print(addr,HEX);
                ser->print(" act  "); ser->println(act,HEX);
            }
            switch (act) {
                case 0 : registers[addr]  = arg; break;
                case 1 : registers[addr] |= arg; break;
                case 2 : registers[addr] &= ~arg; break;
                case 3 : registers[addr] ^= arg; break;
                default: break;
            }
            uint32_t rv = ((uint32_t)cmd << 16) | registers[addr];
            if (ser) { ser->print("RF return: "); ser->println(rv,HEX); }
            return rv;
        }
};

#endif

