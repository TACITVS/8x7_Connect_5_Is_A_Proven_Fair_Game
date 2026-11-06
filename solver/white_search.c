#include "solver/rules.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define INF 0x3fffffffu
typedef uint32_t u32;
typedef struct { u64 a, b; u32 pn, dn; u32 work; int16_t busy; int8_t mv; int8_t lf; } TE;

static int TTB = 24;
static TE *TT;

static inline u64 mirror(u64 x) {
  u64 r = 0;
  for (int c = 0; c < W; c++) r |= ((x >> (c * H1)) & ((1ULL << H1) - 1)) << ((W - 1 - c) * H1);
  return r;
}
static inline void canon(const Pos *p, u64 *a, u64 *b, int *mir) {
  u64 a0 = p->st[0], b0 = p->st[1], a1 = mirror(a0), b1 = mirror(b0);
  if (a1 < a0 || (a1 == a0 && b1 < b0)) { *a = a1; *b = b1; *mir = 1; } else { *a = a0; *b = b0; *mir = 0; }
}
static inline u64 hsh(u64 a, u64 b) {
  u64 h = a * 0x9E3779B97F4A7C15ULL ^ (b + 0x632BE59BD9B4E019ULL) * 0xC2B2AE3D27D4EB4FULL;
  return h ^ (h >> 31);
}
static int tt_get(u64 a, u64 b, TE *out) {
  TE *bk = &TT[(hsh(a, b) & ((1ULL << TTB) - 1)) & ~3ULL];
  for (int i = 0; i < 4; i++) if (bk[i].a == a && bk[i].b == b && (bk[i].pn | bk[i].dn)) { *out = bk[i]; return 1; }
  return 0;
}
static void tt_put(u64 a, u64 b, u32 pn, u32 dn, u32 work, int mv, int lf) {
  TE *bk = &TT[(hsh(a, b) & ((1ULL << TTB) - 1)) & ~3ULL];
  TE *v = NULL;
  for (int i = 0; i < 4; i++) {
    if (bk[i].a == a && bk[i].b == b) { v = &bk[i]; break; }
    if (!v || (bk[i].pn == 0 && bk[i].dn == 0)) v = &bk[i];
  }
  v->a = a; v->b = b; v->pn = pn; v->dn = dn; v->work = work; v->mv = mv; v->lf = lf;
}

static void play(Pos *q, const Pos *p, int c) {
  u64 mv = (p->mask + BIT(c, 0)) & COLMASK[c];
  *q = *p; q->st[p->n & 1] |= mv; q->mask |= mv; q->n = p->n + 1;
}

static int quick_eval(const Pos *p, u32 *pn, u32 *dn, int *lf) {
  int D = DEF, A = 1 - D;
  *lf = 0;
  u64 wd = win_cells(p, D), wa = win_cells(p, A);
  if ((p->n & 1) == D) {
    if (wd) { *pn = 0; *dn = INF; *lf = 9; return 1; }
    if (wa & (wa - 1)) { *pn = INF; *dn = 0; return 1; }
  } else {
    if (wa) { *pn = INF; *dn = 0; return 1; }
    if (wd & (wd - 1)) { *pn = 0; *dn = INF; *lf = 8; return 1; }
  }
  return 0;
}

// Threat-biased move ordering for defender White
static int gen_moves_scored(const Pos *p, int *mv) {
  int D = DEF, A = 1 - D, n = 0;
  int is_def = (p->n & 1) == D;
  u64 must = is_def ? win_cells(p, A) : win_cells(p, D);

  int cand[W], scores[W];
  for (int c = 0; c < W; c++) {
    if (p->mask & TOPCELL[c]) continue;
    if (must && !(must & COLMASK[c])) continue;
    
    int score = 0;
    if (is_def) {
      Pos q; play(&q, p, c);
      // Blunder filter: don't give attacker immediate win
      if (win_cells(&q, A)) score -= 1000000;
      // Threat creation heuristic
      u64 played = q.mask ^ p->mask;
      for (int l = 0; l < NL; l++) {
        if (LINES[l] & p->st[A]) continue;
        if (LINES[l] & played) {
          int kd = popc(LINES[l] & q.st[D]);
          score += kd * kd * 10;
        }
      }
      // Center preference
      score += (c == 3 || c == 4) ? 5 : (c == 2 || c == 5) ? 3 : 1;
    } else {
      // Attacker prefers center
      score = (c == 3 || c == 4) ? 5 : (c == 2 || c == 5) ? 3 : 1;
    }
    cand[n] = c; scores[n] = score; n++;
  }
  // Sort descending
  for (int i = 1; i < n; i++)
    for (int j = i; j > 0 && scores[j] > scores[j - 1]; j--) {
      int t = scores[j]; scores[j] = scores[j - 1]; scores[j - 1] = t;
      t = cand[j]; cand[j] = cand[j - 1]; cand[j - 1] = t;
    }
  for (int i = 0; i < n; i++) mv[i] = cand[i];
  return n;
}

static long long nodes, leafcalls;
typedef struct { u32 pn, dn; } PD;
static inline u32 sat_add(u32 x, u32 y) { u64 s = (u64)x + y; return s >= INF ? INF : (u32)s; }

static PD child_value(R2Ctx *rx, const Pos *q, int mover) {
  PD r;
  int D = DEF;
  if (has_line(q->st[mover])) { r.pn = mover == D ? 0 : INF; r.dn = mover == D ? INF : 0; return r; }
  if (q->n == NCELL) { r.pn = 0; r.dn = INF; return r; }
  u64 a, b; int mir;
  canon(q, &a, &b, &mir);
  TE e;
  if (tt_get(a, b, &e)) { r.pn = e.pn; r.dn = e.dn; return r; }
  int lf;
  if (quick_eval(q, &r.pn, &r.dn, &lf)) { tt_put(a, b, r.pn, r.dn, 1, -1, lf); return r; }
  leafcalls++;
  lf = leaf_x(rx, q, NULL, NULL);
  if (lf) { r.pn = 0; r.dn = INF; tt_put(a, b, 0, INF, 1, -1, lf); return r; }
  int mv[W];
  int n = gen_moves_scored(q, mv);
  if ((q->n & 1) == D) { r.pn = 1; r.dn = n; } else { r.pn = n; r.dn = 1; }
  tt_put(a, b, r.pn, r.dn, 0, -1, 0);
  return r;
}

static u32 mid(R2Ctx *rx, const Pos *p, u32 thpn, u32 thdn, PD *out) {
  int D = DEF, side = p->n & 1, isor = side == D;
  u64 a, b; int mir;
  canon(p, &a, &b, &mir);
  int mv[W];
  int n = gen_moves_scored(p, mv);
  Pos ch[W]; PD cv[W];
  for (int i = 0; i < n; i++) { play(&ch[i], p, mv[i]); cv[i] = child_value(rx, &ch[i], side); }
  u32 work = 1;
  u32 pn, dn; int best = -1;
  for (;;) {
    nodes++;
    if (isor) {
      pn = INF; dn = 0;
      for (int i = 0; i < n; i++) { if (cv[i].pn < pn) { pn = cv[i].pn; best = i; } dn = sat_add(dn, cv[i].dn); }
    } else {
      pn = 0; dn = INF;
      for (int i = 0; i < n; i++) { pn = sat_add(pn, cv[i].pn); if (cv[i].dn < dn) { dn = cv[i].dn; best = i; } }
    }
    if (n == 0) { pn = 0; dn = INF; }
    if (pn >= thpn || dn >= thdn || pn == 0 || dn == 0) break;
    u32 cthpn, cthdn;
    if (isor) {
      u32 p2 = INF;
      for (int i = 0; i < n; i++) if (i != best && cv[i].pn < p2) p2 = cv[i].pn;
      u32 t = sat_add(thpn, cv[best].pn);
      cthpn = (t > pn) ? t - pn : 1;
      if (p2 < cthpn) cthpn = p2 + 1;
      cthdn = sat_add(thdn, cv[best].dn);
      if (cthdn > dn) cthdn -= dn; else cthdn = 1;
    } else {
      u32 d2 = INF;
      for (int i = 0; i < n; i++) if (i != best && cv[i].dn < d2) d2 = cv[i].dn;
      u32 t = sat_add(thdn, cv[best].dn);
      cthdn = (t > dn) ? t - dn : 1;
      if (d2 < cthdn) cthdn = d2 + 1;
      cthpn = sat_add(thpn, cv[best].pn);
      if (cthpn > pn) cthpn -= pn; else cthpn = 1;
    }
    PD r;
    work += mid(rx, &ch[best], cthpn, cthdn, &r);
    cv[best] = r;
  }
  tt_put(a, b, pn, dn, work, (best >= 0 && mir) ? (W - 1 - mv[best]) : (best >= 0 ? mv[best] : -1), 0);
  out->pn = pn; out->dn = dn;
  return work;
}

int main(void) {
  setvbuf(stdout, NULL, _IONBF, 0);
  init();
  DEF = 0; // White defender
  TT = calloc((size_t)1 << TTB, sizeof(TE));
  R2Ctx rx; memset(&rx, 0, sizeof(rx));

  // Root: White plays col 3
  Pos root = {{0, 0}, 0, 0};
  play(&root, &root, 3);
  printf("Starting White Defense Search from move 1 (White at col 3)...\n");

  clock_t t0 = clock();
  PD r;
  u32 th = 10000;
  for (int iter = 0; iter < 10; iter++) {
    mid(&rx, &root, th, th, &r);
    double el = (double)(clock() - t0) / CLOCKS_PER_SEC;
    printf("iter %2d: pn=%u dn=%u nodes=%lld leafcalls=%lld t=%.2fs\n", iter, r.pn, r.dn, nodes, leafcalls, el);
    if (r.pn == 0) { printf("WHITE DEFENSE PROVEN!\n"); break; }
    if (r.dn == 0) { printf("WHITE DEFENSE DISPROVEN!\n"); break; }
    th *= 2;
  }
  return 0;
}
