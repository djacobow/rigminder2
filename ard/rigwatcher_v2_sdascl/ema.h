#ifndef __EMA_H
#define __EMA_H

template <typename SAMP_TYPE, typename STORE_TYPE,
      uint32_t ALPHA, uint32_t DENOM>
class ema_c {
 public:
  ema_c() { };

  // not strictly necessary, but you can 'prime' the
  // filter with the first sample
  void init(SAMP_TYPE sample) {
    state = sample * DENOM;
  }

  // call every time you have a new sample, returns the
  // current average
  SAMP_TYPE update(SAMP_TYPE sample) {
    state = (
              (ALPHA * sample) +

              state -

              ((ALPHA * state) / DENOM)
            );

    return (state / DENOM);
  }

 private:
  STORE_TYPE state;
};

#endif

