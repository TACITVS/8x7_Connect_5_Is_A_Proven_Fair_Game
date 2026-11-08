"use strict";
// Independent reconstructions for the audited snapshot.
// Run: node audit/reproduce_findings.cjs
// This does not execute Rocq, Lean, C, or CUDA.
function assert(condition, message) {
  if (!condition) throw new Error(message);
}
const key = cell => cell.join(",");
const directions = [[1, 0], [0, 1], [1, 1], [1, -1]];
const lines = [];
for (let c = 0; c < 8; c++) {
  for (let r = 0; r < 7; r++) {
    for (const [dc, dr] of directions) {
      const ec = c + 4 * dc, er = r + 4 * dr;
      if (ec < 8 && er >= 0 && er < 7) {
        lines.push(Array.from({length: 5}, (_, i) => [c + i * dc, r + i * dr]));
      }
    }
  }
}
const nonvertical = lines.filter(l => l[0][0] !== l[1][0]);
const core = new Set([
  [3, 0],
  ...[2, 6].flatMap(c => [2, 4, 6].map(r => [c, r])),
  ...[1, 3, 5].map(r => [4, r])
].map(key));
const wall = new Set([
  ...[0, 2, 4, 6].map(r => [3, r]),
  ...[1, 3, 5].map(r => [4, r])
].map(key));
const uppers = new Set(Array.from({length: 8}, (_, c) =>
  (c === 4 ? [1, 3, 5] : [2, 4, 6]).map(r => [c, r])
).flat().map(key));
const throughDead = lines.filter(l => l.some(x => key(x) === "4,6"));
const geometry = {
  total: lines.length,
  horizontal: lines.filter(l => l[0][1] === l[1][1]).length,
  vertical: lines.length - nonvertical.length,
  diagonal: nonvertical.filter(l => l[0][1] !== l[1][1]).length,
  coreHits: nonvertical.filter(l => l.some(x => core.has(key(x)))).length,
  wallHits: nonvertical.filter(l => l.some(x => wall.has(key(x)))).length,
  deadLines: throughDead.length,
  deadUpperCounts: throughDead.map(l => l.filter(x => uppers.has(key(x))).length)
};
assert(geometry.total === 76 && geometry.horizontal === 28 &&
       geometry.vertical === 24 && geometry.diagonal === 24, "line counts");
assert(geometry.coreHits === 52 && geometry.wallHits === 40, "transversals");
assert(geometry.deadLines === 6 &&
       geometry.deadUpperCounts.every(n => n >= 2), "dead-cell coverage");

// Reconstruct white_27pair_struct's cells and partition obligation.
const strong = [];
for (let c = 0; c < 8; c++) {
  for (let r = c === 4 ? 0 : 1; r + 1 < 7; r += 2) {
    strong.push([[c, r], [c, r + 1]]);
  }
}
const rigid = [[[0, 0], [7, 0]], [[1, 0], [5, 0]], [[2, 0], [6, 0]]];
const assigned = new Set([...strong, ...rigid].flat().map(key));
const unassigned = [];
for (let c = 0; c < 8; c++) {
  for (let r = 0; r < 7; r++) {
    if (!(c === 3 && r === 0) && !assigned.has(key([c, r]))) {
      unassigned.push([c, r]);
    }
  }
}
assert(strong.length === 24 && assigned.size === 54, "27-pair reconstruction");
assert(JSON.stringify(unassigned) === "[[4,6]]", "unassigned cell");
// In check_mode's false branch, a nonempty strong list is rejected.
const coreMode = {parity: false, strongCount: 9, rigidCount: 0, frozen: null};
const coreModePass = coreMode.parity ||
  (coreMode.strongCount === 0 && coreMode.rigidCount === 0 &&
   coreMode.frozen === null);
assert(!coreModePass, "core structure mode must fail");

const FULL = 0x7f7f7f7f7f7f7f7fn;
const masks = lines.map(l => l.reduce(
  (m, [c, r]) => m | (1n << BigInt(8 * c + r)), 0n));
// Literal structure of has_won_5, expressed using BigInt.
function shiftDetector(s) {
  for (const d of [1n, 8n, 9n, 7n]) {
    const m = s & (s >> d);
    if ((m & (m >> (2n * d)) & (s >> (4n * d))) & FULL) return true;
  }
  return false;
}
assert(masks.every(shiftDetector), "all winning masks must be detected");
for (const mask of masks) {
  for (let i = 0n; i < 64n; i++) {
    const bit = 1n << i;
    if (mask & bit) assert(!shiftDetector(mask ^ bit), "four-stone near miss");
  }
}
let seed = 123456789;
function random32() {
  seed = (Math.imul(seed, 1664525) + 1013904223) >>> 0;
  return seed;
}
let discrepancies = 0;
for (let i = 0; i < 100000; i++) {
  const s = ((BigInt(random32()) << 32n) | BigInt(random32())) & FULL;
  const enumerated = masks.some(m => (s & m) === m);
  if (shiftDetector(s) !== enumerated) discrepancies++;
}
assert(discrepancies === 0, "win-detector discrepancy");

// Reconstruct the CUDA benchmark's inputs, without executing CUDA.
const distinct = new Set();
let wrongMover = 0;
for (let i = 0; i < 262144; i++) {
  let w = 0n, b = 0n;
  const heights = Array(8).fill(0), moves = 2 + i % 20;
  for (let m = 0; m < moves; m++) {
    const c = (i * 7 + m * 11) % 8;
    if (heights[c] < 7) {
      const bit = 1n << BigInt(c * 8 + heights[c]++);
      if (m % 2 === 0) w |= bit;
      else b |= bit;
    }
  }
  distinct.add(w.toString() + "," + b.toString());
  if (moves % 2 === 1) wrongMover++;
}
assert(distinct.size === 38 && wrongMover === 131072, "benchmark reconstruction");
console.log(JSON.stringify({
  geometry,
  white27Unassigned: unassigned,
  whiteCoreModePass: coreModePass,
  detector: {boards: 100000, discrepancies},
  benchmark: {boards: 262144, distinct: distinct.size, wrongMover}
}, null, 2));
