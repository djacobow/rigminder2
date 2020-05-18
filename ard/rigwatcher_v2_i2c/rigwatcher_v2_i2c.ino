  
#include <Arduino.h>
#include <Wire.h>
#include "regfile.h"
#include "ema.h"


const uint8_t MY_I2C_ADDR = 42;
const uint8_t REG_V_IN      = 0;
const uint8_t REG_V_OUT0    = 1;
const uint8_t REG_V_OUT1    = 2;
const uint8_t REG_I_OUT0    = 3;
const uint8_t REG_I_OUT1    = 4;
const uint8_t REG_WDOG_MASK = 5;
const uint8_t REG_OUTPUT    = 6;
const uint8_t REG_TIMER     = 7;


const uint8_t pin_dc0_ctrl = 4;
const uint8_t pin_dc1_ctrl = 5;
const uint8_t pin_oc0_ctrl = 6;
const uint8_t pin_oc1_ctrl = 7;
const uint8_t pin_vin      = A0;
const uint8_t pin_vout0    = A1;
const uint8_t pin_vout1    = A2;
const uint8_t pin_iout0    = A7;
const uint8_t pin_iout1    = A6;

const uint16_t OUTPUT_MASK_DC0  = 0x1;
const uint16_t OUTPUT_MASK_DC1  = 0x2;
const uint16_t OUTPUT_MASK_OC0  = 0x4;
const uint16_t OUTPUT_MASK_OC1  = 0x8;

const size_t rf_size = 16;
regfile_c<rf_size> rf;

uint16_t last_opattern;

ema_c<int16_t, int32_t, 1, 32> v_in;
ema_c<int16_t, int32_t, 1, 32> v_out0;
ema_c<int16_t, int32_t, 1, 32> v_out1;
ema_c<int16_t, int32_t, 1, 32> i_out0;
ema_c<int16_t, int32_t, 1, 32> i_out1;

// there is only one request type, and it is very simple:
// dump the entire register file. We don't even need to
// examine the "command"
void requestEvent() {
  Serial.println("reqEv");
  void *rf0 = rf.getptr(0);
  Wire.write((uint8_t *)rf0,rf_size * sizeof(uint16_t));
}

void receiveEvent(int count) {
  Serial.println("recEv");
  if (count == 3) {
    uint8_t cmd = Wire.read();
    uint8_t valh = Wire.read();
    uint8_t vall = Wire.read();
    uint32_t blob = 0;
    blob |= (uint32_t)cmd << 16;
    blob |= (uint32_t)valh << 8;
    blob |= (uint32_t)vall;
    rf.update(blob);
  } else {
    while (count) {
      uint8_t x = Wire.read();
      (void)x;
      count--;
    }
  }
}



void setup() {

  pinMode(A4, INPUT_PULLUP);
  pinMode(A5, INPUT_PULLUP);
  Wire.begin(MY_I2C_ADDR);
  Wire.onReceive(receiveEvent);
  Wire.onRequest(requestEvent);

  // our output wires
  pinMode(pin_dc0_ctrl, OUTPUT);
  pinMode(pin_dc1_ctrl, OUTPUT);
  pinMode(pin_oc1_ctrl, OUTPUT);
  pinMode(pin_oc0_ctrl, OUTPUT);

  // initialize the register file, start
  // in shutdon mode
  rf.clear();
  rf.set(REG_OUTPUT,0);
  rf.set(REG_WDOG_MASK, 0xffff);
  rf.set(REG_TIMER,0);
  rf.set_debug(&Serial);
  last_opattern = 0;

  v_in.init(analogRead(pin_vin));
  v_out0.init(analogRead(pin_vout0));
  v_out1.init(analogRead(pin_vout1));
  i_out0.init(analogRead(pin_iout0));
  i_out1.init(analogRead(pin_iout1));
  interrupts();
  Serial.begin(57600);
  Serial.println("Heyyo!");

}


uint8_t x = 1;
uint32_t loop_count = 0;
uint32_t last_run = 0;

void loop() {

  uint16_t vin   = v_in.update(analogRead(pin_vin));
  uint16_t vout0 = v_out0.update(analogRead(pin_vout0));
  uint16_t vout1 = v_out1.update(analogRead(pin_vout1));
  uint16_t iout0 = i_out0.update(analogRead(pin_iout0));
  uint16_t iout1 = i_out1.update(analogRead(pin_iout1));

  auto now = millis();
  if (now < (last_run + 50)) {
      delay(10);
      return;
  }
  last_run = now;

  uint32_t rx_data;
  uint16_t opattern = rf.get(REG_OUTPUT);
  if (opattern != last_opattern) {
      Serial.print("New pat: ");
      Serial.println(opattern,HEX);
      digitalWrite(pin_dc0_ctrl, (opattern & OUTPUT_MASK_DC0)  ? HIGH : LOW);
      digitalWrite(pin_dc1_ctrl, (opattern & OUTPUT_MASK_DC1)  ? HIGH : LOW);
      digitalWrite(pin_oc0_ctrl, (opattern & OUTPUT_MASK_OC0)  ? HIGH : LOW);
      digitalWrite(pin_oc1_ctrl, (opattern & OUTPUT_MASK_OC1)  ? HIGH : LOW);
      last_opattern = opattern;
  }


  rf.set(REG_V_IN, vin);
  rf.set(REG_V_OUT0,vout0);
  rf.set(REG_V_OUT1,vout1);
  rf.set(REG_I_OUT0,iout0);
  rf.set(REG_I_OUT1,iout1);

  if (!(loop_count % 20)) {
      uint16_t tval = rf.get(REG_TIMER);
      if (tval) {
          tval -= 1;
          rf.set(REG_TIMER,tval);
      } else {
          opattern = rf.get(REG_OUTPUT);
          opattern &= ~rf.get(REG_WDOG_MASK);
          rf.set(REG_OUTPUT, opattern);
      }
      if (1) {
        Serial.print("Timer: "); Serial.print(tval);
        Serial.print(" vin: "); Serial.print(vin);
        Serial.print(" vout0: "); Serial.print(vout0);
        Serial.print(" vout1: "); Serial.println(vout1);
      }
  }
  
  loop_count += 1;
};

