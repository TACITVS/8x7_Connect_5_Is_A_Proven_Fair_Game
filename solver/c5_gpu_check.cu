#include <cuda_runtime.h>
#include <stdio.h>
#include <stdint.h>

#define W 8
#define H 7
#define K 5
#define FULL_MASK 0x7F7F7F7F7F7F7F7FULL
#define BOTTOM_MASK 0x0101010101010101ULL

typedef unsigned long long u64;

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
    // Diagonal \ (shift 7)
    m = s & (s >> 7);
    if ((m & (m >> 14) & (s >> 28)) & FULL_MASK) return true;
    return false;
}

// 76 winning lines stored in GPU constant memory
__constant__ u64 d_LINES[76];

__global__ void test_kernel(int *out) {
    int tid = threadIdx.x;
    u64 s = 0;
    // Test 5 vertical pieces in col 0
    for (int r = 0; r < 5; r++) s |= (1ULL << r);
    bool won = has_won_5(s);
    if (tid == 0) out[0] = won ? 1 : 0;
}

int main() {
    int *d_out;
    cudaMalloc(&d_out, sizeof(int));
    test_kernel<<<1, 32>>>(d_out);
    cudaDeviceSynchronize();
    int h_out = 0;
    cudaMemcpy(&h_out, d_out, sizeof(int), cudaMemcpyDeviceToHost);
    printf("GPU Test Result: %d (expected 1)\n", h_out);
    cudaFree(d_out);
    return 0;
}
