// I don't have any ideas how to test for inline functions
// gcc 9 produces no DW_AT_inline entry in this case
// https://github.com/SzymonZos/dwarf-parser/issues/2
// static inline int tiny(const unsigned char * volatile restrict p) { return 0; }

// It is expected to fail as for now support of properly parsing arrays is not done
// https://github.com/SzymonZos/dwarf-parser/issues/1
// const char* foo(const char* const array[21]) { return ""; }

void baz(const volatile char* ptr) {}

struct Foo {}; struct Foo* brr(const struct Foo* f) { return f; }

void frr(volatile unsigned char * const restrict p) {}
void fft(const unsigned char * volatile p) {}

void* alloc(void) {}

const unsigned char* ptr = "ptr";
int main(void) { return 0; }
