/* Strategy DISCOVERY tool: depth-first proof-number search for a defender
   strategy whose leaves satisfy the follow-up rules in rules.h. */
#include "rules.h"

#define INF 0x3fffffffu
typedef uint32_t u32;
typedef struct { u64 a, b; u32 pn, dn; u32 work; int8_t mv; int8_t lf; int8_t pad[2]; } TE;
static int TTB = 26;
static TE *TT;
static long long nodes, mids, leafcalls;
static int center_order[W];
static double EPS = 0.25;

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
static inline u64 hsh(u64 a, u64 b) {
  u64 h = a * 0x9E3779B97F4A7C15ULL ^ (b + 0x632BE59BD9B4E019ULL) * 0xC2B2AE3D27D4EB4FULL;
  return h ^ (h >> 31);
}
static TE *tt_find(u64 a, u64 b) {
  TE *bk = &TT[(hsh(a, b) & ((1ULL << TTB) - 1)) & ~3ULL];
  for (int i = 0; i < 4; i++) if (bk[i].a == a && bk[i].b == b && (bk[i].pn | bk[i].dn)) return &bk[i];
  return NULL;
}
static void tt_store(u64 a, u64 b, u32 pn, u32 dn, u32 work, int mv, int lf) {
  TE *bk = &TT[(hsh(a, b) & ((1ULL << TTB) - 1)) & ~3ULL];
  TE *v = NULL;
  for (int i = 0; i < 4; i++) if (bk[i].a == a && bk[i].b == b) { v = &bk[i]; break; }
  if (!v) {
    /* replace: empty first, then lowest-work unsolved, then lowest work */
    u32 best = 0xffffffffu;
    for (int i = 0; i < 4; i++) {
      if (!(bk[i].pn | bk[i].dn)) { v = &bk[i]; break; }
      int solved = bk[i].pn == 0 || bk[i].dn == 0;
      u32 score = bk[i].work + (solved ? 0x40000000u : 0);
      if (score < best) { best = score; v = &bk[i]; }
    }
  }
  v->a = a; v->b = b; v->pn = pn; v->dn = dn; v->work = work; v->mv = mv; v->lf = lf;
}

static void play(Pos *q, const Pos *p, int c) {
  u64 mv = (p->mask + BIT(c, 0)) & COLMASK[c];
  *q = *p; q->st[p->n & 1] |= mv; q->mask |= mv; q->n = p->n + 1;
}

/* Static evaluation of a nonterminal node. Returns 1 if solved (pn/dn set). */
static int static_eval(const Pos *p, u32 *pn, u32 *dn, int *lf) {
  int side = p->n & 1, D = DEF, A = 1 - D;
  *lf = 0;
  if (side == D) {
    if (win_cells(p, D)) { *pn = 0; *dn = INF; *lf = 9; return 1; }
    u64 thr = win_cells(p, A);
    if (thr & (thr - 1)) { *pn = INF; *dn = 0; return 1; }
  } else {
    if (win_cells(p, A)) { *pn = INF; *dn = 0; return 1; }
    u64 dw = win_cells(p, D);
    if (dw & (dw - 1)) { *pn = 0; *dn = INF; *lf = 8; return 1; }
  }
  leafcalls++;
  int l = leaf(p);
  if (l) { *pn = 0; *dn = INF; *lf = l; return 1; }
  return 0;
}

/* legal (non-losing-pruned) moves */
static int gen_moves(const Pos *p, int *mv) {
  int side = p->n & 1, D = DEF, A = 1 - D, n = 0;
  u64 must = 0;
  if (side == D) must = win_cells(p, A);   /* defender must block */
  else must = win_cells(p, D);             /* attacker must block */
  for (int i = 0; i < W; i++) {
    int c = center_order[i];
    if (p->mask & TOPCELL[c]) continue;
    if (must && !(must & COLMASK[c])) continue;
    mv[n++] = c;
  }
  return n;
}

typedef struct { u32 pn, dn; } PD;

/* child value: terminal / TT / static */
static PD child_value(const Pos *q, int mover) {
  PD r;
  int D = DEF;
  if (has_line(q->st[mover])) { r.pn = mover == D ? 0 : INF; r.dn = mover == D ? INF : 0; return r; }
  if (q->n == NCELL) { r.pn = 0; r.dn = INF; return r; }
  u64 a, b; int mir;
  canon(q, &a, &b, &mir);
  TE *e = tt_find(a, b);
  if (e) { r.pn = e->pn; r.dn = e->dn; return r; }
  int lf;
  if (static_eval(q, &r.pn, &r.dn, &lf)) { tt_store(a, b, r.pn, r.dn, 1, -1, lf); return r; }
  int mv[W];
  int n = gen_moves(q, mv);
  if ((q->n & 1) == D) { r.pn = 1; r.dn = n; } else { r.pn = n; r.dn = 1; }
  return r;
}

static inline u32 sat_add(u32 x, u32 y) { u64 s = (u64)x + y; return s >= INF ? INF : (u32)s; }

static u32 mid(const Pos *p, u32 thpn, u32 thdn, PD *out) {
  mids++;
  int D = DEF, side = p->n & 1, isor = side == D;
  u64 a, b; int mir;
  canon(p, &a, &b, &mir);
  {
    /* cheap terminal checks (gen_moves pruning relies on them) */
    u64 wd = win_cells(p, D), wa = win_cells(p, 1 - D);
    int solved = 0; u32 spn = 0, sdn = 0;
    if (isor) {
      if (wd) { solved = 1; spn = 0; sdn = INF; }
      else if (wa & (wa - 1)) { solved = 1; spn = INF; sdn = 0; }
    } else {
      if (wa) { solved = 1; spn = INF; sdn = 0; }
      else if (wd & (wd - 1)) { solved = 1; spn = 0; sdn = INF; }
    }
    if (solved) { tt_store(a, b, spn, sdn, 1, -1, 0); out->pn = spn; out->dn = sdn; return 1; }
  }
  int mv[W];
  int n = gen_moves(p, mv);
  Pos ch[W];
  PD cv[W];
  for (int i = 0; i < n; i++) { play(&ch[i], p, mv[i]); cv[i] = child_value(&ch[i], side); }
  u32 work = 1;
  u32 pn, dn;
  int best = -1;
  for (;;) {
    nodes++;
    if (isor) {
      pn = INF; dn = 0;
      for (int i = 0; i < n; i++) { if (cv[i].pn < pn) pn = cv[i].pn; dn = sat_add(dn, cv[i].dn); }
    } else {
      pn = 0; dn = INF;
      for (int i = 0; i < n; i++) { pn = sat_add(pn, cv[i].pn); if (cv[i].dn < dn) dn = cv[i].dn; }
    }
    if (n == 0) { /* cannot happen: board not full */ pn = 0; dn = INF; }
    if (pn >= thpn || dn >= thdn || pn == 0 || dn == 0) break;
    /* select */
    int b1 = -1; u32 v1 = INF + 1, v2 = INF;
    for (int i = 0; i < n; i++) {
      u32 v = isor ? cv[i].pn : cv[i].dn;
      if (v < v1) { v2 = v1; v1 = v; b1 = i; } else if (v < v2) v2 = v;
    }
    if (v2 > INF) v2 = INF;
    u32 cthpn, cthdn;
    u32 lim = (u32)((double)v2 * (1.0 + EPS)) + 1;
    if (lim > INF) lim = INF;
    if (isor) {
      cthpn = thpn < lim ? thpn : lim;
      cthdn = (thdn >= INF) ? INF : sat_add(thdn - dn, cv[b1].dn);
      if (cthdn > INF) cthdn = INF;
    } else {
      cthdn = thdn < lim ? thdn : lim;
      cthpn = (thpn >= INF) ? INF : sat_add(thpn - pn, cv[b1].pn);
    }
    PD r;
    work += mid(&ch[b1], cthpn, cthdn, &r);
    cv[b1] = r;
    best = b1;
  }
  int bm = -1;
  if (isor && pn == 0) for (int i = 0; i < n; i++) if (cv[i].pn == 0) { bm = mv[i]; break; }
  if (bm >= 0 && mir) bm = W - 1 - bm;
  (void)best;
  tt_store(a, b, pn, dn, work, bm, 0);
  out->pn = pn; out->dn = dn;
  return work;
}

/* ---- proof extraction / size ---- */
typedef struct { u64 a, b; } Key;
static Key *SEEN; static u64 SEENMASK;
static int seen_insert(u64 a, u64 b) {
  u64 h = hsh(a, b);
  for (u64 i = h & SEENMASK;; i = (i + 1) & SEENMASK) {
    if (SEEN[i].a == 0 && SEEN[i].b == 0) { SEEN[i].a = a; SEEN[i].b = b; return 1; }
    if (SEEN[i].a == a && SEEN[i].b == b) return 0;
  }
}
static long long px_internal, px_leaf[10], px_maxply;
static int extract(const Pos *p) {
  int D = DEF, side = p->n & 1;
  u64 a, b; int mir;
  canon(p, &a, &b, &mir);
  if (!seen_insert(a | (1ULL << 63), b)) return 1;
  if (p->n > px_maxply) px_maxply = p->n;
  u32 pn, dn; int lf;
  if (static_eval(p, &pn, &dn, &lf)) {
    if (pn != 0) { printf("extract: static says not proven\n"); return 0; }
    px_leaf[lf]++;
    return 1;
  }
  px_internal++;
  int mv[W];
  int n = gen_moves(p, mv);
  if (side == D) {
    for (int i = 0; i < n; i++) {
      Pos q; play(&q, p, mv[i]);
      if (has_line(q.st[D]) || q.n == NCELL) { px_leaf[7]++; return 1; }
    }
    for (int i = 0; i < n; i++) {
      Pos q; play(&q, p, mv[i]);
      if (has_line(q.st[1 - D])) continue;
      PD v = child_value(&q, side);
      if (v.dn == 0) continue;
      if (v.pn != 0) {
        PD r; mid(&q, INF, INF, &r);
        if (r.pn != 0) continue;
      }
      return extract(&q);
    }
    printf("extract: no proven child\n");
    return 0;
  }
  for (int i = 0; i < n; i++) {
    Pos q; play(&q, p, mv[i]);
    if (has_line(q.st[1 - D])) { printf("extract: attacker wins\n"); return 0; }
    if (q.n == NCELL) { px_leaf[7]++; continue; }
    PD v = child_value(&q, side);
    if (v.dn == 0) { printf("extract: child disproven\n"); return 0; }
    if (v.pn != 0) { PD r; mid(&q, INF, INF, &r); if (r.pn != 0) { printf("extract: child not proven\n"); return 0; } }
    if (!extract(&q)) return 0;
  }
  return 1;
}

int main(int argc, char **argv) {
  init();
  DEF = argc > 1 ? atoi(argv[1]) : 1;
  if (argc > 2) TTB = atoi(argv[2]);
  USE_R2 = argc > 3 ? atoi(argv[3]) : 1;
  for (int i = 0; i < W; i++) {
    int c = (W % 2 == 0) ? (W / 2) + ((i & 1) ? -((i + 1) / 2) : (i / 2))
                         : W / 2 + ((i & 1) ? (i + 1) / 2 : -(i / 2));
    center_order[i] = c;
  }
  TT = calloc((size_t)1 << TTB, sizeof(TE));
  printf("dfpn W=%d H=%d K=%d lines=%d defender=%s TT=2^%d\n", W, H, K, NL, DEF ? "second" : "first", TTB);
  fflush(stdout);
  Pos p = {{0, 0}, 0, 0};
  clock_t t0 = clock();
  PD r = {1, 1};
  u32 th = 2;
  while (r.pn != 0 && r.dn != 0) {
    mid(&p, th, INF, &r);
    printf("th=%u root pn=%u dn=%u nodes=%lld leafcalls=%lld r1=%lld r2=%lld t=%.1fs\n", th, r.pn, r.dn, nodes, leafcalls,
           r1calls, r2calls, (double)(clock() - t0) / CLOCKS_PER_SEC);
    fflush(stdout);
    if (r.pn == 0 || r.dn == 0) break;
    th = r.pn + 1 > th * 2 ? r.pn + 1 : th * 2;
    if (th >= INF) th = INF;
  }
  printf("RESULT: defender %s\n", r.pn == 0 ? "CAN force at least a draw" : "CANNOT (attacker wins)");
  if (r.pn == 0) {
    SEENMASK = (1ULL << 27) - 1;
    SEEN = calloc(SEENMASK + 1, sizeof(Key));
    int ok = extract(&p);
    printf("proof: ok=%d internal=%lld leaves: R1=%lld R2=%lld R3=%lld defwin=%lld dbl=%lld term=%lld maxply=%lld t=%.1fs\n", ok,
           px_internal, px_leaf[1], px_leaf[2], px_leaf[3], px_leaf[9], px_leaf[8], px_leaf[7], px_maxply,
           (double)(clock() - t0) / CLOCKS_PER_SEC);
  }
  return 0;
}
