#ifndef RPI_COMM_H
#define RPI_COMM_H

#include <Arduino.h>
#include <stdint.h>
#include <Stream.h>

#include "queue.h"
const uint8_t p_clk = A5;
const uint8_t p_dat = A4;

class rpi_communicator_c {
    private:
    Stream *ser;
    volatile uint32_t rxword;
    volatile uint32_t tx_data;
    void txBit(bool b);
    rb_u32_4_t *rb;


    // try 2
    bool d_p, d_p_p;
    uint8_t cs;
    bool do_send;
    bool odd;
    
    public:
    
    rpi_communicator_c();
    void set_rb(rb_u32_4_t *nrb) { rb = nrb; };
    void set_debug(Stream *nser) { 
      ser = nser;
      if (ser) ser->println("Debug initialized");
    };
    void init();
    void on_clock_edge();
    void set_tx_data(uint32_t t) { tx_data = t; };
};


#endif

