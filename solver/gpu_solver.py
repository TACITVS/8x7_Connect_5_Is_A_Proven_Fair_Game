import os
import sys
import time
import ctypes
import numpy as np

# Load CUDA and NVRTC DLLs
for d in [
    r"C:\Users\baian\AppData\Local\Programs\Python\Python312\Lib\site-packages\nvidia\cuda_nvrtc\bin",
    r"C:\Users\baian\AppData\Local\Programs\Python\Python312\Lib\site-packages\nvidia\cuda_runtime\bin"
]:
    if os.path.exists(d): os.add_dll_directory(d)

hCuda = ctypes.WinDLL("nvcuda.dll")
hNvrtc = ctypes.WinDLL(r"C:\Users\baian\AppData\Local\Programs\Python\Python312\Lib\site-packages\nvidia\cuda_nvrtc\bin\nvrtc64_120_0.dll")

assert hCuda.cuInit(0) == 0
dev = ctypes.c_int()
assert hCuda.cuDeviceGet(ctypes.byref(dev), 0) == 0
ctx = ctypes.c_void_p()
assert hCuda.cuCtxCreate(ctypes.byref(ctx), 0, dev) == 0

# CUDA C Kernel for Connect-5 (8x7) Massively Parallel Evaluator
CUDA_SRC = b"""
#define W 8
#define H 7
#define K 5
#define FULL_MASK 0x7F7F7F7F7F7F7F7FULL
#define BOTTOM_MASK 0x0101010101010101ULL

typedef unsigned long long u64;
typedef signed char i8;

__device__ inline bool has_won_5(u64 s) {
    u64 m;
    // Vertical (shift 1)
    m = s & (s >> 1);
    if ((m & (m >> 2) & (s >> 4)) & FULL_MASK) return true;
    // Horizontal (shift 8)
    m = s & (s >> 8);
    if ((m & (m >> 16) & (s >> 32)) & FULL_MASK) return true;
    // Diagonal / (shift 9)
    m = s & (s >> 9);
    if ((m & (m >> 18) & (s >> 36)) & FULL_MASK) return true;
    // Diagonal \\ (shift 7)
    m = s & (s >> 7);
    if ((m & (m >> 14) & (s >> 28)) & FULL_MASK) return true;
    return false;
}

// Parallel Board Evaluator Kernel
// Evaluates N board states in parallel across all GPU threads
extern "C" __global__ void eval_boards(
    const u64 *white_boards,
    const u64 *black_boards,
    i8 *results,
    int n,
    int mover // 0 = White, 1 = Black
) {
    int idx = blockDim.x * blockIdx.x + threadIdx.x;
    if (idx >= n) return;

    u64 w = white_boards[idx];
    u64 b = black_boards[idx];
    u64 mask = w | b;

    // Check if previous move already won
    if (mover == 0 && has_won_5(b)) { results[idx] = -1; return; }
    if (mover == 1 && has_won_5(w)) { results[idx] = -1; return; }

    // Check if mover can win in 1 move
    u64 my_stones = (mover == 0) ? w : b;
    u64 opp_stones = (mover == 0) ? b : w;
    u64 playable = (mask + BOTTOM_MASK) & FULL_MASK & ~mask;

    int win_moves = 0;
    int opp_win_moves = 0;

    for (int c = 0; c < 8; c++) {
        u64 col_bit = 1ULL << (c * 8);
        u64 col_mask = 0x7FULL << (c * 8);
        u64 landing = (mask + col_bit) & col_mask & ~mask;
        if (landing) {
            if (has_won_5(my_stones | landing)) win_moves++;
            if (has_won_5(opp_stones | landing)) opp_win_moves++;
        }
    }

    if (win_moves > 0) {
        results[idx] = 1; // Mover wins immediately
        return;
    }

    if (opp_win_moves >= 2) {
        results[idx] = -2; // Opponent has double win, mover loses
        return;
    }

    results[idx] = 0; // Inconclusive / needs deeper search
}
"""

prog = ctypes.c_void_p()
hNvrtc.nvrtcCreateProgram(ctypes.byref(prog), CUDA_SRC, b"c5_eval.cu", 0, None, None)
opts = (ctypes.c_char_p * 1)(b"--gpu-architecture=compute_89")
res = hNvrtc.nvrtcCompileProgram(prog, 1, opts)
if res != 0:
    log_sz = ctypes.c_size_t()
    hNvrtc.nvrtcGetProgramLogSize(prog, ctypes.byref(log_sz))
    log = ctypes.create_string_buffer(log_sz.value)
    hNvrtc.nvrtcGetProgramLog(prog, log)
    print("Compilation Log:\n", log.value.decode())
    sys.exit(1)

ptx_sz = ctypes.c_size_t()
hNvrtc.nvrtcGetPTXSize(prog, ctypes.byref(ptx_sz))
ptx = ctypes.create_string_buffer(ptx_sz.value)
hNvrtc.nvrtcGetPTX(prog, ptx)

mod = ctypes.c_void_p()
assert hCuda.cuModuleLoadData(ctypes.byref(mod), ptx) == 0
k_eval = ctypes.c_void_p()
assert hCuda.cuModuleGetFunction(ctypes.byref(k_eval), mod, b"eval_boards") == 0

print("CUDA Connect-5 Evaluator loaded onto RTX 4060!", flush=True)

# Test performance: evaluate 100,000 board positions on GPU
N = 100_000
h_white = np.zeros(N, dtype=np.uint64)
h_black = np.zeros(N, dtype=np.uint64)
h_res = np.zeros(N, dtype=np.int8)

print(f"Generating {N:,} random board test states...", flush=True)
rng = np.random.default_rng(42)
for i in range(N):
    # Some random stones
    num_moves = rng.integers(2, 20)
    w_mask = 0
    b_mask = 0
    col_heights = [0]*8
    for m in range(num_moves):
        c = rng.integers(0, 8)
        if col_heights[c] < 7:
            bit = 1 << (c * 8 + col_heights[c])
            col_heights[c] += 1
            if m % 2 == 0:
                w_mask |= bit
            else:
                b_mask |= bit
    h_white[i] = w_mask
    h_black[i] = b_mask

d_white = ctypes.c_uint64()
d_black = ctypes.c_uint64()
d_res = ctypes.c_uint64()

assert hCuda.cuMemAlloc(ctypes.byref(d_white), N * 8) == 0
assert hCuda.cuMemAlloc(ctypes.byref(d_black), N * 8) == 0
assert hCuda.cuMemAlloc(ctypes.byref(d_res), N) == 0

hCuda.cuMemcpyHtoD.argtypes = [ctypes.c_uint64, ctypes.c_void_p, ctypes.c_size_t]
hCuda.cuMemcpyDtoH.argtypes = [ctypes.c_void_p, ctypes.c_uint64, ctypes.c_size_t]

assert hCuda.cuMemcpyHtoD(d_white, h_white.ctypes.data, N * 8) == 0
assert hCuda.cuMemcpyHtoD(d_black, h_black.ctypes.data, N * 8) == 0

c_n = ctypes.c_int(N)
c_mover = ctypes.c_int(0)

params = (ctypes.c_void_p * 5)(
    ctypes.cast(ctypes.byref(d_white), ctypes.c_void_p),
    ctypes.cast(ctypes.byref(d_black), ctypes.c_void_p),
    ctypes.cast(ctypes.byref(d_res), ctypes.c_void_p),
    ctypes.cast(ctypes.byref(c_n), ctypes.c_void_p),
    ctypes.cast(ctypes.byref(c_mover), ctypes.c_void_p)
)

print(f"Launching evaluation of {N:,} board positions on RTX 4060 GPU...", flush=True)
t0 = time.perf_counter()
threads_per_block = 256
blocks = (N + threads_per_block - 1) // threads_per_block

res = hCuda.cuLaunchKernel(k_eval, blocks, 1, 1, threads_per_block, 1, 1, 0, None, params, None)
assert res == 0
hCuda.cuCtxSynchronize()
t1 = time.perf_counter()

assert hCuda.cuMemcpyDtoH(h_res.ctypes.data, d_res, N) == 0

eval_time = t1 - t0
rate = N / eval_time

print(f"Time: {eval_time*1000:.2f} ms", flush=True)
print(f"Throughput: {rate / 1e6:.2f} MILLION positions/second on RTX 4060!", flush=True)
print(f"Wins found: {np.count_nonzero(h_res == 1):,}, Losses: {np.count_nonzero(h_res == -1):,}, Inconclusive: {np.count_nonzero(h_res == 0):,}", flush=True)
