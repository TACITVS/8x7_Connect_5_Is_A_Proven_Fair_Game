/* Prototype proof search for gravity connect-K on a W x H board.
   Question answered: can defender D guarantee at least a draw?
   Leaves: (1) attacker has no live line, (2) "playable pairing":
   disjoint vertical dominoes + base pairs (two currently playable cells)
   such that every live attacker line contains a whole unit. */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <time.h>

#ifndef W
#define W 8
#endif
#ifndef H
#define H 7
#endif
#ifndef K
#define K 5
#endif
#define H1 (H + 1)
#define NCELL (W * H)
typedef uint64_t u64;
#define BIT(c, r) (1ULL << ((c) * H1 + (r)))

static u64 BOTTOM, FULL, COLMASK[W], TOPCELL[W];
static u64 LINES[256];
static int NL;

static void init(void) {
  for (int c = 0; c < W; c++) {
    COLMASK[c] = ((1ULL << H) - 1) << (c * H1);
    TOPCELL[c] = BIT(c, H - 1);
    BOTTOM |= BIT(c, 0);
    FULL |= COLMASK[c];
  }
  int D[4][2] = {{0, 1}, {1, 0}, {1, 1}, {1, -1}};
  for (int d = 0; d < 4; d++)
    for (int c = 0; c < W; c++)
      for (int r = 0; r < H; r++) {
        int ec = c + (K - 1) * D[d][0], er = r + (K - 1) * D[d][1];
        if (ec < 0 || ec >= W || er < 0 || er >= H) continue;
        u64 m = 0;
        for (int i = 0; i < K; i++) m |= BIT(c + i * D[d][0], r + i * D[d][1]);
        LINES[NL++] = m;
      }
}

typedef struct { u64 st[2]; u64 mask; int n; } Pos;

static inline u64 playable(const Pos *p) { return (p->mask + BOTTOM) & FULL; }

static inline int has_line(u64 s) {
  for (int l = 0; l < NL; l++) if ((LINES[l] & s) == LINES[l]) return 1;
  return 0;
}
/* playable cells that would complete a line for player P */
static inline u64 win_cells(const Pos *p, int P) {
  u64 s = p->st[P], o = p->st[1 - P], w = 0;
  for (int l = 0; l < NL; l++) {
    u64 L = LINES[l];
    if (L & o) continue;
    u64 e = L & ~s;
    if (e && !(e & (e - 1))) w |= e;
  }
  return w & playable(p);
}

/* ---------------- pairing leaf ---------------- */
static long long pair_nodes;
static int pl_nlive, pl_nu;
static u64 pl_unit[160];
static u64 pl_hit[160][2];   /* live lines hit by unit (bitset over live index) */
static int pl_cand[128][160], pl_ncand[128];
static u64 pl_need[2];

static int pl_rec(u64 used, u64 h0, u64 h1) {
  if (++pair_nodes > 2000000) return 0;
  if ((h0 & pl_need[0]) == pl_need[0] && (h1 & pl_need[1]) == pl_need[1]) return 1;
  int best = -1, bestn = 1 << 30;
  for (int i = 0; i < pl_nlive; i++) {
    int hit = i < 64 ? (h0 >> i) & 1 : (h1 >> (i - 64)) & 1;
    if (hit) continue;
    int n = 0;
    for (int j = 0; j < pl_ncand[i]; j++) if (!(pl_unit[pl_cand[i][j]] & used)) n++;
    if (n < bestn) { bestn = n; best = i; if (n == 0) return 0; }
  }
  for (int j = 0; j < pl_ncand[best]; j++) {
    int u = pl_cand[best][j];
    if (pl_unit[u] & used) continue;
    if (pl_rec(used | pl_unit[u], h0 | pl_hit[u][0], h1 | pl_hit[u][1])) return 1;
  }
  return 0;
}

static int pairing_leaf(const Pos *p, int D) {
  u64 dst = p->st[D];
  u64 empty = FULL & ~p->mask;
  int live[256];
  pl_nlive = 0;
  for (int l = 0; l < NL; l++) if (!(LINES[l] & dst)) live[pl_nlive++] = l;
  if (pl_nlive == 0) return 1;
  pl_nu = 0;
  for (int c = 0; c < W; c++)
    for (int r = 0; r + 1 < H; r++) {
      u64 u = BIT(c, r) | BIT(c, r + 1);
      if ((u & empty) == u) pl_unit[pl_nu++] = u;
    }
  u64 pb = playable(p);
  for (int a = 0; a < W; a++) {
    u64 ba = pb & COLMASK[a];
    if (!ba) continue;
    for (int b = a + 1; b < W; b++) {
      u64 bb = pb & COLMASK[b];
      if (bb) pl_unit[pl_nu++] = ba | bb;
    }
  }
  pl_need[0] = pl_need[1] = 0;
  for (int i = 0; i < pl_nlive; i++) {
    if (i < 64) pl_need[0] |= 1ULL << i; else pl_need[1] |= 1ULL << (i - 64);
    pl_ncand[i] = 0;
  }
  for (int u = 0; u < pl_nu; u++) {
    pl_hit[u][0] = pl_hit[u][1] = 0;
    for (int i = 0; i < pl_nlive; i++)
      if ((pl_unit[u] & LINES[live[i]]) == pl_unit[u]) {
        if (i < 64) pl_hit[u][0] |= 1ULL << i; else pl_hit[u][1] |= 1ULL << (i - 64);
        pl_cand[i][pl_ncand[i]++] = u;
      }
  }
  for (int i = 0; i < pl_nlive; i++) if (pl_ncand[i] == 0) return 0;
  return pl_rec(0, 0, 0);
}

/* ---------------- transposition table ---------------- */
typedef struct { u64 a, b; int8_t res; int8_t mv; } TTE;
#define TTBITS 25
static TTE *TT;
static inline u64 hkey(const Pos *p) {
  u64 h = p->st[0] * 0x9E3779B97F4A7C15ULL ^ (p->st[1] + 0x632BE59BD9B4E019ULL) * 0xC2B2AE3D27D4EB4FULL;
  return (h ^ (h >> 29)) & ((1ULL << TTBITS) - 1);
}

static long long nodes, leaves_dead, leaves_pair;
static int DEF;

static void play(Pos *q, const Pos *p, int c) {
  u64 mv = (p->mask + BIT(c, 0)) & COLMASK[c];
  *q = *p;
  q->st[p->n & 1] |= mv;
  q->mask |= mv;
  q->n = p->n + 1;
}

static int center_order[W];

static int prove(const Pos *p) {
  nodes++;
  if (p->n == NCELL) return 1;
  int side = p->n & 1, D = DEF, A = 1 - D;
  u64 h = hkey(p);
  TTE *e = &TT[h];
  if (e->a == p->st[0] && e->b == p->st[1] && e->res >= 0) return e->res;
  int res;
  if (side == D) {
    if (win_cells(p, D)) { res = 1; goto done; }
    u64 thr = win_cells(p, A);
    if (thr & (thr - 1)) { res = 0; goto done; }
    if (pairing_leaf(p, D)) { leaves_pair++; res = 1; goto done; }
    int cand[W], nc = 0;
    if (thr) {
      for (int c = 0; c < W; c++) if (thr & COLMASK[c]) cand[nc++] = c;
    } else {
      /* score moves */
      int sc[W];
      for (int i = 0; i < W; i++) {
        int c = center_order[i];
        if (p->mask & TOPCELL[c]) continue;
        Pos q; play(&q, p, c);
        /* never give the attacker an immediate win on top */
        int s = 0;
        u64 mv = q.mask ^ p->mask;
        for (int l = 0; l < NL; l++)
          if ((LINES[l] & mv) && !(LINES[l] & p->st[D])) {
            int k = __builtin_popcountll(LINES[l] & p->st[A]);
            s += 1 + k * k * 4;
          }
        if (pairing_leaf(&q, D)) s += 100000;
        cand[nc] = c; sc[nc] = s; nc++;
      }
      for (int i = 1; i < nc; i++)
        for (int j = i; j > 0 && sc[j] > sc[j - 1]; j--) {
          int t = sc[j]; sc[j] = sc[j - 1]; sc[j - 1] = t;
          t = cand[j]; cand[j] = cand[j - 1]; cand[j - 1] = t;
        }
    }
    res = 0;
    for (int i = 0; i < nc; i++) {
      Pos q; play(&q, p, cand[i]);
      if (has_line(q.st[D])) { res = 1; break; }
      if (prove(&q)) { res = 1; e = &TT[h]; e->mv = cand[i]; break; }
    }
  } else {
    if (win_cells(p, A)) { res = 0; goto done; }
    if (pairing_leaf(p, D)) { leaves_pair++; res = 1; goto done; }
    res = 1;
    for (int i = 0; i < W; i++) {
      int c = center_order[i];
      if (p->mask & TOPCELL[c]) continue;
      Pos q; play(&q, p, c);
      if (!prove(&q)) { res = 0; break; }
    }
  }
done:
  e = &TT[h];
  e->a = p->st[0]; e->b = p->st[1]; e->res = res;
  return res;
}

int main(int argc, char **argv) {
  init();
  DEF = argc > 1 ? atoi(argv[1]) : 1;
  for (int i = 0; i < W; i++) {
    /* center-first ordering */
    int c = W / 2 + ((i & 1) ? (i + 1) / 2 : -(i / 2));
    if (W % 2 == 0) c = (W / 2) + ((i & 1) ? -((i + 1) / 2) : (i / 2));
    center_order[i] = c;
  }
  TT = malloc(sizeof(TTE) << TTBITS);
  memset(TT, 0xff, sizeof(TTE) << TTBITS);
  for (u64 i = 0; i < (1ULL << TTBITS); i++) TT[i].res = -1, TT[i].a = TT[i].b = ~0ULL;
  printf("W=%d H=%d K=%d lines=%d defender=%s\n", W, H, K, NL, DEF ? "second" : "first");
  Pos p = {{0, 0}, 0, 0};
  clock_t t0 = clock();
  int r = prove(&p);
  printf("result: defender %s at least a draw\n", r ? "CAN force" : "CANNOT force");
  printf("nodes=%lld pairleaves=%lld pairnodes=%lld time=%.1fs\n", nodes, leaves_pair, pair_nodes,
         (double)(clock() - t0) / CLOCKS_PER_SEC);
  return 0;
}
