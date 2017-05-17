  
#include <Arduino.h>

#ifdef ATTINY84
  #include "SoftTX.h"
  #include "shiftout.h"
#endif

#include "rpi_comm.h"
#include "queue.h"
#include "regfile.h"

const uint8_t REG_TIMER = 7;
const uint8_t REG_OUTPUT = 6;
const uint8_t REG_WDOG_MASK = 5;
const uint8_t REG_V_IN = 0;
const uint8_t REG_V_OUT = 1;


const bool main_debug = false;

#include "ema.h"



rpi_communicator_c rpic;
#ifdef ATTINY84
  const uint16_t shiftdata = 0;
  const uint16_t shiftclock = 1;
  const uint16_t latchclock = 2;
  shifter8_c<shiftclock, shiftdata, latchclock> shifter;
#else
  const uint8_t dc_ctrl = 7;
  const uint8_t ac_ctrl = 8;
  const uint8_t led_ctrl = 9;
  const uint8_t oc_ctrl = 6;
  const uint16_t OUTPUT_MASK_DC = 0x1;
  const uint16_t OUTPUT_MASK_AC = 0x8;
  const uint16_t OUTPUT_MASK_LED = 0x2;
  const uint16_t OUTPUT_MASK_OC = 0x4;
  
#endif

regfile_c<16> rf;
rb_u32_4_t rb;

uint16_t last_opattern;

ema_c<int16_t, int32_t, 1, 32> v_in;
ema_c<int16_t, int32_t, 1, 32> v_out;

#ifdef ATTINY84
ISR(PCINT0_vect) {
  rpic.on_clock_edge();
  return;
}
#else
ISR(PCINT1_vect) {
  rpic.on_clock_edge();
  return;
}
#endif

void setup() {

#ifdef ATTINY84
  PCMSK0 = (1<<PCINT4);
  GIMSK |= (1<<PCIE0);
  shifter.init();
#else
  // TODO set up 328 to respond to pin change on SCL
  PCMSK1 = (1<<PCINT13); // SCL
  PCICR  = (1<<PCIE1);
  pinMode(dc_ctrl, OUTPUT);
  pinMode(ac_ctrl, OUTPUT);
  pinMode(led_ctrl, OUTPUT);
  pinMode(oc_ctrl, OUTPUT);

#endif

  rf.clear();
  rf.set(REG_OUTPUT,0);
  rf.set(REG_WDOG_MASK, 0xffff);
  rf.set(REG_TIMER,0);
  rf.set_debug(&Serial);
  rb.set_debug(&Serial);
  last_opattern = 0;

  rpic.init();
  rpic.set_rb(&rb);
  rpic.set_debug(&Serial);

  v_in.init(analogRead(A1));
  v_out.init(analogRead(A0));
  pinMode(10,OUTPUT);
  interrupts();
  Serial.begin(57600);

}


uint8_t x = 1;
uint32_t loop_count = 0;
void loop() {

  uint32_t rx_data;
  if (rb.pop(rx_data)) {
    Serial.print("RB popped: ");
    Serial.println(rx_data,HEX);
    uint32_t value = rf.update(rx_data);
    rpic.set_tx_data(value);
  }
  uint16_t opattern = rf.get(REG_OUTPUT);
  if (opattern != last_opattern) {
      Serial.print("New pat: ");
      Serial.println(opattern,HEX);
#ifdef ATTINY84
      shifter.shift(opattern);
#else
      digitalWrite(dc_ctrl, (opattern & OUTPUT_MASK_DC)  ? HIGH : LOW);
      digitalWrite(ac_ctrl, (opattern & OUTPUT_MASK_AC)  ? HIGH : LOW);
      digitalWrite(led_ctrl,(opattern & OUTPUT_MASK_LED) ? HIGH : LOW);
      digitalWrite(oc_ctrl, (opattern & OUTPUT_MASK_OC)  ? HIGH : LOW);
#endif

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
      Serial.print("Timer: "); Serial.print(tval);
      Serial.print(" vin: "); Serial.print(vin);
      Serial.print(" vout: "); Serial.println(vout);
  }
  
 
  loop_count += 1;
  delay(100);
};

