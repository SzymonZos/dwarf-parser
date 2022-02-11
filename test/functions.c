const char* foo(const char* const array[21]) { return ""; }

void baz(volatile const char* ptr) {}

struct Foo {};
struct Foo* brr(const struct Foo* f) { return f; }

void frr(volatile unsigned char * const restrict p) {}
void fft(const unsigned char * volatile p) {}

void* alloc(void) {}

int main(void) {
    return 0;
}
