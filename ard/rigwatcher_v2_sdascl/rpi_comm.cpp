#include "rpi_comm.h"

const bool rpi_debug = false;

rpi_communicator_c::rpi_communicator_c() {
};

void rpi_communicator_c::init() {
    ser = 0;
    rb = 0;
    pinMode(p_clk, INPUT);
    pinMode(p_dat, INPUT);
};

void rpi_communicator_c::txBit(bool b) {
   if (b) {
     pinMode(p_dat,INPUT);
     digitalWrite(p_dat,HIGH);
     if (ser) ser->print("txBit HiZ ");
   } else { 
     digitalWrite(p_dat,LOW);
     pinMode(p_dat,OUTPUT);
     if (ser) ser->print("txBit LOW ");
   }
}

void rpi_communicator_c::on_clock_edge() {
  noInterrupts();
  bool d = digitalRead(p_dat);

  bool reset = !d && !d_p && !d_p_p;
  bool one   = d && !d_p;
  bool zero  = !d && d_p;
  bool err   = false; d & d_p;
  bool ob = 0x1 & (tx_data >> (cs - 0x30));
  bool in_rx = (cs >= 0x10) && (cs <= 0x2f);
  bool in_tx = (cs >= 0x30) && (cs <= 0x4f);
      
  if (reset || err) {
    if (ser && reset) ser->println("reset");
    if (ser &&  err) ser->println("err");

    cs = 0;
    odd = false;
    pinMode(p_dat, INPUT);
  } if (odd) {
    if (ser) { ser->print("odd cs="); ser->println(cs, HEX); }
    if (cs == 0) {
     if (one) {
        cs = 1;
        if (ser) ser->println("proceeding to rw bit");      
      } else {
        cs = 0;
        if (ser) ser->println("back to reset no positive sync");
      }
    } else if (cs == 1) {
      if (one) rxword = 0;
      cs = one ? 0x10 :
            zero ? 0x30 :
            0x0;
    } else if (in_rx) {
      rxword <<= 1;
      rxword |= one;
      if (ser) { ser->print("rxword: "); ser->println(rxword,HEX); }

      if (cs == 0x2f) {
        rb->insert(rxword);
        cs = 0;
      } else {
        cs += 1;
      }
    } else if (in_tx) {
      if (ser) { ser->print("word "); ser->print(tx_data,HEX); ser->print(" idx "); ser->println(cs,HEX); }
      txBit(ob);
      if (cs == 0x4f) {
        cs = 0;
      } else {
        cs += 1;
      }
    }
    odd = false;
  } else {
    if (ser) { ser->print("even cs="); ser->println(cs, HEX); }
    if (in_tx) {
      txBit(!ob);
    }
    odd = true;
  }
  
  d_p_p = d_p;
  d_p = d;
  interrupts();
}



