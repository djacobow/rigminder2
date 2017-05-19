  
#include <Arduino.h>
#include <Wire.h>
#include "regfile.h"
#include "ema.h"


const uint8_t MY_I2C_ADDR = 42;
const uint8_t REG_TIMER = 7;
const uint8_t REG_OUTPUT = 6;
const uint8_t REG_WDOG_MASK = 5;
const uint8_t REG_V_IN = 0;
const uint8_t REG_V_OUT = 1;


const uint8_t dc_ctrl = 7;
const uint8_t ac_ctrl = 6;
const uint8_t led_ctrl = 9;
const uint8_t oc_ctrl = 8;

const uint16_t OUTPUT_MASK_DC  = 0x1;
const uint16_t OUTPUT_MASK_AC  = 0x2;
const uint16_t OUTPUT_MASK_OC  = 0x4;
const uint16_t OUTPUT_MASK_LED = 0x8;

const size_t rf_size = 16;
regfile_c<rf_size> rf;

uint16_t last_opattern;

ema_c<int16_t, int32_t, 1, 32> v_in;
ema_c<int16_t, int32_t, 1, 32> v_out;

// there is only one request type, and it is very simple:
// dump the entire register file. We don't even need to
// examine the "command"
void requestEvent() {
  Serial.println("requestEvent");
  void *rf0 = rf.getptr(0);
  Wire.write((uint8_t *)rf0,rf_size * sizeof(uint16_t));
}

void receiveEvent(int count) {
  Serial.println("receiveEvent");
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
      count--;
    }
  }
}



void setup() {

  Wire.begin(MY_I2C_ADDR);
  Wire.onReceive(receiveEvent);
  Wire.onRequest(requestEvent);

  // our output wires
  pinMode(dc_ctrl, OUTPUT);
  pinMode(ac_ctrl, OUTPUT);
  pinMode(led_ctrl, OUTPUT);
  pinMode(oc_ctrl, OUTPUT);

  // initialize the register file, start
  // in shutdon mode
  rf.clear();
  rf.set(REG_OUTPUT,0);
  rf.set(REG_WDOG_MASK, 0xffff);
  rf.set(REG_TIMER,0);
  rf.set_debug(&Serial);
  last_opattern = 0;

  v_in.init(analogRead(A1));
  v_out.init(analogRead(A0));
  interrupts();
  Serial.begin(57600);
  Serial.println("Heyyo!");

}


uint8_t x = 1;
uint32_t loop_count = 0;
void loop() {

  uint32_t rx_data;
  uint16_t opattern = rf.get(REG_OUTPUT);
  if (opattern != last_opattern) {
      Serial.print("New pat: ");
      Serial.println(opattern,HEX);
      digitalWrite(dc_ctrl, (opattern & OUTPUT_MASK_DC)  ? HIGH : LOW);
      digitalWrite(ac_ctrl, (opattern & OUTPUT_MASK_AC)  ? HIGH : LOW);
      digitalWrite(led_ctrl,(opattern & OUTPUT_MASK_LED) ? HIGH : LOW);
      digitalWrite(oc_ctrl, (opattern & OUTPUT_MASK_OC)  ? HIGH : LOW);
      last_opattern = opattern;
  }

  uint16_t vin   = v_in.update(analogRead(A1));
  uint16_t vout = v_out.update(analogRead(A0));

  rf.set(REG_V_IN, vin);
  rf.set(REG_V_OUT,vout);

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
      if (0) {
        Serial.print("Timer: "); Serial.print(tval);
        Serial.print(" vin: "); Serial.print(vin);
        Serial.print(" vout: "); Serial.println(vout);
      }
  }
  
 
  loop_count += 1;
  delay(100);
};

