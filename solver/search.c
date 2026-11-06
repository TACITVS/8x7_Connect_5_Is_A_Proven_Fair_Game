#include "rules.h"
/* ---------------- TT ---------------- */
typedef struct { u64 a, b; int8_t res; int8_t depth; int8_t mv; int8_t leaf; } TTE;
static int TTBITS = 26;
static TTE *TT;
static inline u64 mirror(u64 x) {
#if W * H1 == 64
  return __builtin_bswap64(x);
#else
  u64 r = 0;
  for (int c = 0; c < W; c++) r |= ((x >> (c * H1)) & ((1ULL << H1) - 1)) << ((W - 1 - c) * H1);
  return r;
#endif
}
static inline void canon(const Pos *p, u64 *a, u64 *b, int *mir) {
  u64 a0 = p->st[0], b0 = p->st[1], a1 = mirror(a0), b1 = mirror(b0);
  if (a1 < a0 || (a1 == a0 && b1 < b0)) { *a = a1; *b = b1; *mir = 1; } else { *a = a0; *b = b0; *mir = 0; }
}
static inline TTE *tt_slot(u64 a, u64 b) {
  u64 h = a * 0x9E3779B97F4A7C15ULL ^ (b + 0x632BE59BD9B4E019ULL) * 0xC2B2AE3D27D4EB4FULL;
  h ^= h >> 31;
  return &TT[h & ((1ULL << TTBITS) - 1)];
}

static long long nodes;
static int center_order[W];
static void play(Pos *q, const Pos *p, int c) {
  u64 mv = (p->mask + BIT(c, 0)) & COLMASK[c];
  *q = *p; q->st[p->n & 1] |= mv; q->mask |= mv; q->n = p->n + 1;
}

/* returns 1 if proven within depth */
static int prove(const Pos *p, int depth) {
  nodes++;
  if (p->n == NCELL) return 1;
  int side = p->n & 1, D = DEF, A = 1 - D;
  u64 ka, kb; int mir;
  canon(p, &ka, &kb, &mir);
  TTE *e = tt_slot(ka, kb);
  if (e->a == ka && e->b == kb) {
    if (e->res == 1) return 1;
    if (e->res == 0 && e->depth >= depth) return 0;
  }
  int res = 0, lf = 0, bestmv = -1;
  if (side == D) {
    u64 wc = win_cells(p, D);
    if (wc) { res = 1; lf = 3; bestmv = ctz(wc) / H1; goto done; }
    u64 thr = win_cells(p, A);
    if (thr & (thr - 1)) { res = 0; depth = 127; goto done; } /* absolute loss */
    if ((lf = leaf(p))) { res = 1; goto done; }
    if (depth <= 0) { res = 0; goto done; }
    int cand[W], sc[W], nc = 0;
    for (int i = 0; i < W; i++) {
      int c = center_order[i];
      if (p->mask & TOPCELL[c]) continue;
      if (thr && !(thr & COLMASK[c])) continue;
      Pos q; play(&q, p, c);
      int s = 0;
      if (win_cells(&q, A)) s -= 1000000; /* gives attacker immediate win */
      u64 mv = q.mask ^ p->mask;
      for (int l = 0; l < NL; l++)
        if ((LINES[l] & mv) && !(LINES[l] & p->st[D])) {
          int k = popc(LINES[l] & p->st[A]);
          s += 1 + k * k * 4;
        }
      if (leaf(&q)) s += 100000;
      cand[nc] = c; sc[nc] = s; nc++;
    }
    for (int i = 1; i < nc; i++)
      for (int j = i; j > 0 && sc[j] > sc[j - 1]; j--) {
        int t = sc[j]; sc[j] = sc[j - 1]; sc[j - 1] = t;
        t = cand[j]; cand[j] = cand[j - 1]; cand[j - 1] = t;
      }
    for (int i = 0; i < nc; i++) {
      Pos q; play(&q, p, cand[i]);
      if (prove(&q, depth - 1)) { res = 1; bestmv = cand[i]; break; }
    }
  } else {
    if (win_cells(p, A)) { res = 0; depth = 127; goto done; }
    if ((lf = leaf(p))) { res = 1; goto done; }
    if (depth <= 0) { res = 0; goto done; }
    res = 1;
    for (int i = 0; i < W; i++) {
      int c = center_order[i];
      if (p->mask & TOPCELL[c]) continue;
      Pos q; play(&q, p, c);
      if (!prove(&q, depth - 1)) { res = 0; break; }
    }
  }
done:
  e = tt_slot(ka, kb);
  if (!(e->a == ka && e->b == kb && e->res == 1)) {
    e->a = ka; e->b = kb; e->res = res; e->depth = depth;
    e->mv = (bestmv >= 0 && mir) ? (W - 1 - bestmv) : bestmv;
    e->leaf = lf;
  }
  return res;
}

/* count proof DAG size (distinct canonical positions) */
static long long pnodes, pleaf[5];
typedef struct { u64 a, b; } Key;
static Key *SEEN; static u64 SEENMASK;
static int seen_insert(u64 a, u64 b) {
  u64 h = (a * 0x9E3779B97F4A7C15ULL ^ b * 0xC2B2AE3D27D4EB4FULL);
  h ^= h >> 29;
  for (u64 i = h & SEENMASK;; i = (i + 1) & SEENMASK) {
    if (SEEN[i].a == 0 && SEEN[i].b == 0) { SEEN[i].a = a; SEEN[i].b = b; return 1; }
    if (SEEN[i].a == a && SEEN[i].b == b) return 0;
  }
}
static int extract(const Pos *p, int depth) {
  if (p->n == NCELL) { pleaf[0]++; return 1; }
  u64 ka, kb; int mir;
  canon(p, &ka, &kb, &mir);
  if (!seen_insert(ka ^ 1ULL << 63, kb)) return 1;
  pnodes++;
  int side = p->n & 1;
  if (side == DEF) {
    u64 wc = win_cells(p, DEF);
    if (wc) { pleaf[4]++; return 1; }
  } else if (win_cells(p, 1 - DEF)) return 0;
  int lf = leaf(p);
  if (lf) { pleaf[lf]++; return 1; }
  TTE *e = tt_slot(ka, kb);
  if (!(e->a == ka && e->b == kb && e->res == 1)) {
    if (!prove(p, depth)) { printf("extract: reprove failed\n"); return 0; }
    e = tt_slot(ka, kb);
  }
  if (side == DEF) {
    int mv = e->mv;
    if (mir) mv = W - 1 - mv;
    if (mv < 0 || mv >= W) { printf("bad mv\n"); return 0; }
    Pos q; play(&q, p, mv);
    return extract(&q, depth - 1);
  }
  for (int c = 0; c < W; c++) {
    if (p->mask & TOPCELL[c]) continue;
    Pos q; play(&q, p, c);
    if (!extract(&q, depth - 1)) return 0;
  }
  return 1;
}

int main(int argc, char **argv) {
  init();
  DEF = argc > 1 ? atoi(argv[1]) : 1;
  int maxdepth = argc > 2 ? atoi(argv[2]) : 40;
  USE_R2 = argc > 3 ? atoi(argv[3]) : 1;
  if (argc > 4) TTBITS = atoi(argv[4]);
  for (int i = 0; i < W; i++) {
    int c = (W % 2 == 0) ? (W / 2) + ((i & 1) ? -((i + 1) / 2) : (i / 2))
                         : W / 2 + ((i & 1) ? (i + 1) / 2 : -(i / 2));
    center_order[i] = c;
  }
  TT = calloc((size_t)1 << TTBITS, sizeof(TTE));
  for (u64 i = 0; i < (1ULL << TTBITS); i++) TT[i].res = -1;
  printf("W=%d H=%d K=%d lines=%d defender=%s R2=%d\n", W, H, K, NL, DEF ? "second" : "first", USE_R2);
  fflush(stdout);
  Pos p = {{0, 0}, 0, 0};
  clock_t t0 = clock();
  for (int d = 0; d <= maxdepth; d++) {
    int r = prove(&p, d);
    printf("depth %2d: %s  nodes=%lld r1=%lld r2=%lld  t=%.1fs\n", d, r ? "PROVEN" : "-", nodes, r1calls, r2calls,
           (double)(clock() - t0) / CLOCKS_PER_SEC);
    fflush(stdout);
    if (r) {
      SEENMASK = (1ULL << 26) - 1;
      SEEN = calloc(SEENMASK + 1, sizeof(Key));
      int ok = extract(&p, d);
      printf("proof DAG: ok=%d internal+leaf positions=%lld leaves: full=%lld R1=%lld R2=%lld R3=%lld win=%lld\n", ok, pnodes,
             pleaf[0], pleaf[1], pleaf[2], pleaf[3], pleaf[4]);
      return 0;
    }
  }
  return 0;
}
