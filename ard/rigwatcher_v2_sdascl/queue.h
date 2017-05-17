#ifndef QUEUE_H
#define QUEUE_H

template <typename T, size_t s>
class ringbuffer {
    private:
    T buffer[s];
    uint8_t front;
    uint8_t rear;
    const uint8_t size = s;
    Stream *ser;

    public:
    ringbuffer() : front(0), rear(0), ser(0) { };
    void set_debug(Stream *nser) { ser = nser; }
    bool insert(T item) {
        if (ser) {
            ser->print("RB insert "); 
            ser->println(item, HEX);
        }
        int fullness = front - rear;
        if (fullness < 0) { fullness += size; };
        if (fullness < size) {
            buffer[front++] = item;
            if (front == size) front = 0;
            return true;
        } 
        return false;
    }; 
    bool pop(T &item) {
        if (rear == front) {
            return false;
        }
        item = buffer[rear++];
        if (rear == size) rear = 0;
        return true;
    };
};


typedef ringbuffer<uint16_t,4> rb_u16_4_t;
typedef ringbuffer<uint32_t,6> rb_u32_4_t;
#endif

