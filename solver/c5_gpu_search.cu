#include <cuda_runtime.h>
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <vector>
#include <iostream>
#include <chrono>

#define W 8
#define H 7
#define K 5
#define FULL_MASK 0x7F7F7F7F7F7F7F7FULL
#define BOTTOM_MASK 0x0101010101010101ULL

typedef unsigned long long u64;
typedef uint32_t u32;
typedef int8_t i8;

// Bit operations
#define BIT(c, r) (1ULL << ((c) * 8 + (r)))
#define COLMASK(c) (0x7FULL << ((c) * 8))

// Constant memory for winning lines
__constant__ u64 c_LINES[76];
static u64 h_LINES[76];

// Initialize the 76 winning lines
void init_lines() {
    int nl = 0;
    // Horizontal lines (28)
    for (int r = 0; r < H; r++) {
        for (int c = 0; c <= W - K; c++) {
            u64 m = 0;
            for (int i = 0; i < K; i++) m |= BIT(c + i, r);
            h_LINES[nl++] = m;
        }
    }
    // Vertical lines (24)
    for (int c = 0; c < W; c++) {
        for (int r = 0; r <= H - K; r++) {
            u64 m = 0;
            for (int i = 0; i < K; i++) m |= BIT(c, r + i);
            h_LINES[nl++] = m;
        }
    }
    // Diagonal / lines (12)
    for (int c = 0; c <= W - K; c++) {
        for (int r = 0; r <= H - K; r++) {
            u64 m = 0;
            for (int i = 0; i < K; i++) m |= BIT(c + i, r + i);
            h_LINES[nl++] = m;
        }
    }
    // Diagonal \ lines (12)
    for (int c = 0; c <= W - K; c++) {
        for (int r = K - 1; r < H; r++) {
            u64 m = 0;
            for (int i = 0; i < K; i++) m |= BIT(c + i, r - i);
            h_LINES[nl++] = m;
        }
    }
    cudaMemcpyToSymbol(c_LINES, h_LINES, sizeof(h_LINES));
}

// 5-in-a-row detector (both host and device)
__host__ __device__ inline bool has_won_5(u64 s) {
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

// GPU Evaluation Result Structure
struct EvalResult {
    i8 score;       // 1 = Win, -1 = Loss (opponent wins/has double win), 0 = Inconclusive
    i8 best_col;    // Best recommended move
    i8 num_moves;   // Number of valid moves
    i8 pad;
    i8 col_scores[8]; // Relative scores of moves 0..7 (-128 if illegal/blunder)
};

// Massively parallel evaluation kernel for N positions
__global__ void eval_batch_kernel(
    const u64 *d_white,
    const u64 *d_black,
    int mover, // 0 = White, 1 = Black
    EvalResult *d_results,
    int n
) {
    int idx = blockDim.x * blockIdx.x + threadIdx.x;
    if (idx >= n) return;

    u64 w = d_white[idx];
    u64 b = d_black[idx];
    u64 mask = w | b;

    u64 my_stones = (mover == 0) ? w : b;
    u64 opp_stones = (mover == 0) ? b : w;

    EvalResult res;
    res.score = 0;
    res.best_col = -1;
    res.num_moves = 0;
    for (int c = 0; c < 8; c++) res.col_scores[c] = -128;

    // Check if opponent already won
    if (has_won_5(opp_stones)) {
        res.score = -1;
        d_results[idx] = res;
        return;
    }

    // Check if mover already won
    if (has_won_5(my_stones)) {
        res.score = 1;
        d_results[idx] = res;
        return;
    }

    // Find playable cells
    int my_win_col = -1;
    int opp_win_count = 0;
    int opp_must_block_col = -1;

    u64 landings[8];
    for (int c = 0; c < 8; c++) {
        u64 col_bit = 1ULL << (c * 8);
        u64 col_mask = 0x7FULL << (c * 8);
        u64 land = (mask + col_bit) & col_mask & ~mask;
        landings[c] = land;
        if (land) {
            res.num_moves++;
            // Check if mover wins immediately
            if (has_won_5(my_stones | land)) {
                my_win_col = c;
            }
            // Check if opponent would win immediately by playing here
            if (has_won_5(opp_stones | land)) {
                opp_win_count++;
                opp_must_block_col = c;
            }
        }
    }

    // If mover can win in 1 move -> WIN
    if (my_win_col >= 0) {
        res.score = 1;
        res.best_col = my_win_col;
        res.col_scores[my_win_col] = 100;
        d_results[idx] = res;
        return;
    }

    // If opponent has 2 or more winning moves -> LOSS (mover cannot block both)
    if (opp_win_count >= 2) {
        res.score = -1;
        d_results[idx] = res;
        return;
    }

    // Score all legal moves
    int best_score = -999;
    int best_c = -1;

    for (int c = 0; c < 8; c++) {
        u64 land = landings[c];
        if (!land) continue;

        // If opponent has 1 winning move, mover MUST block it
        if (opp_win_count == 1 && c != opp_must_block_col) {
            res.col_scores[c] = -100;
            continue;
        }

        // Blunder filter: check if playing here allows opponent to win on top
        u64 next_land = (land << 1) & COLMASK(c);
        if (next_land && has_won_5(opp_stones | next_land)) {
            res.col_scores[c] = -50; // Major blunder: gives opponent instant win!
            continue;
        }

        int score = 0;
        // Center column preference (columns 3 and 4 are center)
        if (c == 3 || c == 4) score += 6;
        else if (c == 2 || c == 5) score += 4;
        else if (c == 1 || c == 6) score += 2;

        res.col_scores[c] = (i8)score;
        if (score > best_score) {
            best_score = score;
            best_c = c;
        }
    }

    res.best_col = best_c;
    d_results[idx] = res;
}

// Host benchmark function
int main() {
    printf("Initializing Connect-5 GPU Engine on RTX 4060...\n");
    init_lines();

    int dev = 0;
    cudaGetDevice(&dev);
    cudaDeviceProp prop;
    cudaGetDeviceProperties(&prop, dev);
    printf("Device: %s (%d SMs, Compute %d.%d, VRAM: %.1f GB)\n",
           prop.name, prop.multiProcessorCount, prop.major, prop.minor,
           (double)prop.totalGlobalMem / (1024*1024*1024));

    // Allocate batch memory
    const int N = 262144; // 256K positions
    u64 *h_white = (u64*)malloc(N * sizeof(u64));
    u64 *h_black = (u64*)malloc(N * sizeof(u64));
    EvalResult *h_results = (EvalResult*)malloc(N * sizeof(EvalResult));

    // Generate random positions
    for (int i = 0; i < N; i++) {
        h_white[i] = 0;
        h_black[i] = 0;
        int moves = 2 + (i % 20);
        int heights[8] = {0};
        for (int m = 0; m < moves; m++) {
            int c = (i * 7 + m * 11) % 8;
            if (heights[c] < 7) {
                u64 bit = 1ULL << (c * 8 + heights[c]++);
                if (m % 2 == 0) h_white[i] |= bit;
                else h_black[i] |= bit;
            }
        }
    }

    u64 *d_white, *d_black;
    EvalResult *d_results;
    cudaMalloc(&d_white, N * sizeof(u64));
    cudaMalloc(&d_black, N * sizeof(u64));
    cudaMalloc(&d_results, N * sizeof(EvalResult));

    cudaMemcpy(d_white, h_white, N * sizeof(u64), cudaMemcpyHostToDevice);
    cudaMemcpy(d_black, h_black, N * sizeof(u64), cudaMemcpyHostToDevice);

    printf("Benchmarking GPU Batch Evaluator on %d positions...\n", N);
    auto t0 = std::chrono::high_resolution_clock::now();

    int threads = 256;
    int blocks = (N + threads - 1) / threads;
    eval_batch_kernel<<<blocks, threads>>>(d_white, d_black, 0, d_results, N);
    cudaDeviceSynchronize();

    auto t1 = std::chrono::high_resolution_clock::now();
    double el = std::chrono::duration<double>(t1 - t0).count();

    cudaMemcpy(h_results, d_results, N * sizeof(EvalResult), cudaMemcpyDeviceToHost);

    int wins = 0, losses = 0, inconc = 0;
    for (int i = 0; i < N; i++) {
        if (h_results[i].score == 1) wins++;
        else if (h_results[i].score == -1) losses++;
        else inconc++;
    }

    printf("Evaluation complete in %.3f ms!\n", el * 1000.0);
    printf("Throughput: %.2f MILLION positions/second!\n", (N / el) / 1e6);
    printf("Wins: %d, Losses: %d, Inconclusive: %d\n", wins, losses, inconc);

    cudaFree(d_white);
    cudaFree(d_black);
    cudaFree(d_results);
    free(h_white);
    free(h_black);
    free(h_results);

    return 0;
}
