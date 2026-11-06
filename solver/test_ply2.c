#include "rules.h"
#include <stdio.h>

int main() {
    init();
    DEF = 0; // White defender
    R2Ctx rx; memset(&rx, 0, sizeof(rx));

    Pos p0 = {{0, 0}, 0, 0};
    // Move 0: White plays col 3
    Pos p1;
    u64 mv = (p0.mask + BIT(3, 0)) & COLMASK[3];
    p1 = p0; p1.st[0] |= mv; p1.mask |= mv; p1.n = 1;

    int reply[8] = {7, 6, 5, 3, 4, 2, 1, 0};

    printf("Testing White Defense at Ply 2 after pairing response:\n");
    for (int c1 = 0; c1 < 8; c1++) {
        Pos p2;
        u64 mv1 = (p1.mask + BIT(c1, 0)) & COLMASK[c1];
        p2 = p1; p2.st[1] |= mv1; p2.mask |= mv1; p2.n = 2;

        int c2 = reply[c1];
        Pos p3;
        u64 mv2 = (p2.mask + BIT(c2, 0)) & COLMASK[c2];
        p3 = p2; p3.st[0] |= mv2; p3.mask |= mv2; p3.n = 3;

        // At p3: ply = 3, Black to move (n=3 is odd, E=53 odd).
        // Wait, at p2 (n=2, Black to move, White defender, E=54):
        // At p2, Black is about to move. Can White's pairing structure solve p2?
        // Let's test leaf_x at p2!
        int fc = -1, ft = -1;
        int lf2 = leaf_x(&rx, &p2, &fc, &ft);
        printf("  c1=%d (c2=%d): leaf_x at p2 (n=2, E=54) = %d (fc=%d, ft=%d)\n", c1, c2, lf2, fc, ft);
        
        // Also test with fc=4, ft=6 (excluding cell (4, 6)) at p2:
        int r2_ex = r2_solve(&rx, &p2, 0, 4, 6);
        printf("    with fc=4, ft=6: r2_solve = %d\n", r2_ex);

        // Also test at p3 with White reply:
        int r2_p3 = r2_solve(&rx, &p3, 0, 4, 6);
        printf("    at p3 (after White reply %d): r2_solve = %d\n", c2, r2_p3);
    }
    return 0;
}
