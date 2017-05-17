#ifndef SHIFTOUT_H
#define SHIFTOUT_H

#include <stdint.h>

template<uint8_t shclk, uint8_t dout, uint8_t latchclk>
class shifter8_c {
    public:
    void init() {
        pinMode(shclk,    OUTPUT);
        pinMode(dout,     OUTPUT);
        pinMode(latchclk, OUTPUT);
        digitalWrite(shclk, LOW);
        digitalWrite(dout, LOW);
        digitalWrite(latchclk, LOW);
    }

    void shift(uint8_t data) {
        digitalWrite(shclk, LOW);
        delay(1);
        for (uint8_t i=0; i<8; i++) {
            bool bit = (data >> i) & 0x1;
            digitalWrite(dout, bit);
            delay(1);
            digitalWrite(shclk, HIGH);
            delay(1);
            digitalWrite(shclk, LOW);
            delay(1);
        }
        digitalWrite(latchclk, HIGH);
        delay(1);
        digitalWrite(latchclk, LOW);
        delay(1);
    }
};

#endif
