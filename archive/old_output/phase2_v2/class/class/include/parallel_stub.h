/* Stub parallel.h for macOS compilation without C++ */
#ifndef PARALLEL_STUB_H
#define PARALLEL_STUB_H

/* Empty stub functions */
static inline void class_setup_parallel() {}
static inline void class_setup_parallel_optional(int x) {}
static inline void class_finish_parallel() {}

/* Simple macros that just execute the code block */
#define class_run_parallel(a,b) {b}
#define class_run_parallel_mutable(a,b) {b}

#endif

