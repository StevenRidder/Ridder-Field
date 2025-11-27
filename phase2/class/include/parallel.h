/* Stub parallel.h for macOS compilation without full C++11 threading */
/* This stub provides serial-only execution */
#ifndef PARALLEL_STUB_H
#define PARALLEL_STUB_H

#ifdef __cplusplus

/* C++ version: Use lambdas to properly contain return statements */
/* Track if any parallel block failed */
static int _stub_parallel_failure = 0;

/* Execute code block in a lambda to contain return statements */
#define class_run_parallel(a,b) do { \
  auto _parallel_task = [a]() -> int { b }; \
  int _result = _parallel_task(); \
  if (_result != 0) _stub_parallel_failure = _result; \
} while(0)

#define class_run_parallel_mutable(a,b) do { \
  auto _parallel_task = [a]() mutable -> int { b }; \
  int _result = _parallel_task(); \
  if (_result != 0) _stub_parallel_failure = _result; \
} while(0)

/* Stub setup and finish */
#define class_setup_parallel() _stub_parallel_failure = 0
#define class_setup_parallel_optional(x) _stub_parallel_failure = 0
#define class_finish_parallel() do { \
  if (_stub_parallel_failure != 0) return _stub_parallel_failure; \
} while(0)

/* C++ stub for task_system used in hmcode.c */
namespace Tools {
  struct TaskSystem {
    static int GetNumThreads() { return 1; }
  };
}
static Tools::TaskSystem task_system;

#else

/* Pure C version: Simple serial execution (no lambda support) */
/* WARNING: This won't work with code that uses return inside class_run_parallel */
#define class_run_parallel(a,b) {b}
#define class_run_parallel_mutable(a,b) {b}
#define class_setup_parallel()
#define class_setup_parallel_optional(x)
#define class_finish_parallel()

#endif /* __cplusplus */

/* Argument wrappers - pass through */
#define with_arguments(...) __VA_ARGS__
#define declare_list_of_variables_inside_parallel_region(...) __VA_ARGS__

#endif /* PARALLEL_STUB_H */
