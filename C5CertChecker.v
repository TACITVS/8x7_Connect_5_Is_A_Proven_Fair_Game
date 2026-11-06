(** * Connect-5 (8x7): Verified Computational Certificate Checker

    This file provides a computable certificate engine that verifies
    strategy trees via Rocq's Virtual Machine (vm_compute).

    - [cert_step], [certificate]: compact indexed DAG representation of strategies.
    - [check_static]: boolean decider reflecting [Static d b st].
    - [check_cert_node]: fast bounded evaluator for certificates.
    - [cert_sound]: soundness theorem connecting the checker to [safe d b s].
*)

From Stdlib Require Import List Arith Bool Lia.
Import ListNotations.

From C5 Require Import C5Game C5Board C5Principle C5Rules C5Certificate.

(** ** Boolean deciders for cells and lists *)

Definition cell_eqb (p1 p2 : cell) : bool :=
  (fst p1 =? fst p2) && (snd p1 =? snd p2).

Lemma cell_eqb_spec : forall p1 p2, cell_eqb p1 p2 = true <-> p1 = p2.
Proof.
  intros [c1 r1] [c2 r2]; unfold cell_eqb; simpl.
  rewrite andb_true_iff, !Nat.eqb_eq.
  split; [intros [-> ->]; reflexivity | intros E; injection E as -> ->; auto].
Qed.

Fixpoint nodupb {A : Type} (eqb : A -> A -> bool) (l : list A) : bool :=
  match l with
  | [] => true
  | h :: t => negb (existsb (eqb h) t) && nodupb eqb t
  end.

Lemma nodupb_NoDup : forall {A : Type} (eqb : A -> A -> bool)
                            (Heqb : forall x y, eqb x y = true <-> x = y) (l : list A),
  nodupb eqb l = true <-> NoDup l.
Proof.
  intros A eqb Heqb l.
  induction l as [|h t IH]; simpl.
  - split; [constructor|reflexivity].
  - rewrite andb_true_iff, negb_true_iff.
    rewrite IH.
    destruct (existsb (eqb h) t) eqn:Eex.
    + split; [intros [H _]; discriminate H|].
      intros Hnd; inversion Hnd as [|? ? Hnot Hnd']; subst.
      apply existsb_exists in Eex as [x [Hin Heq]].
      apply Heqb in Heq; subst x; contradiction.
    + split.
      * intros [_ Hnd]. constructor; [|exact Hnd].
        intros Hin.
        assert (Hex : existsb (eqb h) t = true).
        { apply existsb_exists. exists h; split; [exact Hin|apply Heqb; reflexivity]. }
        rewrite Eex in Hex; discriminate.
      * intros Hnd; inversion Hnd; subst; split; auto.
Qed.

Definition check_wf (b : board) : bool :=
  (length b =? 8) && forallb (fun c => length (col b c) <=? 7) (seq 0 8).

Lemma check_wf_sound : forall b, check_wf b = true -> wf b.
Proof.
  unfold check_wf, wf. intros b.
  rewrite andb_true_iff, Nat.eqb_eq, forallb_forall.
  intros [Hlen Hall]. split; [exact Hlen|].
  intros c.
  destruct (c <? 8) eqn:Ec.
  - apply Nat.ltb_lt in Ec.
    assert (Hin : In c (seq 0 8)) by (apply in_seq; lia).
    apply Hall in Hin. apply Nat.leb_le in Hin. exact Hin.
  - apply Nat.ltb_ge in Ec. unfold col.
    rewrite nth_overflow by lia. simpl. lia.
Qed.

(** ** Boolean checker for Static *)

Definition check_frozen (d : player) (b : board) (st : structure) : bool :=
  match s_frozen st with
  | None => true
  | Some (fc, ft) =>
      (fc <? 8) && (ft <? 7) && (length (col b fc) <? ft) &&
      existsb (fun L =>
        existsb (cell_eqb (fc, ft)) L &&
        forallb (fun y => cell_eqb y (fc, ft) ||
                 match owner b y with Some p => peqb p d | None => false end) L)
      lines
  end.

Definition check_cells (b : board) (st : structure) : bool :=
  forallb (fun x =>
    (fst x <? 8) && (snd x <? topc st (fst x)) &&
    match owner b x with None => true | _ => false end)
  (unit_cells st).

Definition check_strong (st : structure) : bool :=
  forallb (fun p =>
    (fst (snd p) =? fst (fst p)) && (snd (snd p) =? S (snd (fst p))))
  (s_strong st).

Definition check_rigid (b : board) (st : structure) : bool :=
  forallb (fun p =>
    let '(x, y) := p in
    negb (fst x =? fst y) &&
    (((snd x =? length (col b (fst x))) && (snd y =? length (col b (fst y)))) ||
     ((0 <? snd x) && (0 <? snd y) &&
      (existsb (fun q =>
         (cell_eqb (fst q) (fst x, snd x - 1) && cell_eqb (snd q) (fst y, snd y - 1)) ||
         (cell_eqb (fst q) (fst y, snd y - 1) && cell_eqb (snd q) (fst x, snd x - 1)))
       (s_rigid st)))))
  (s_rigid st).

Definition check_rigid_notfree (st : structure) : bool :=
  forallb (fun x =>
    negb (existsb (Nat.eqb (fst x)) (s_free st)))
  (rigid_cells st).

Definition check_weak (b : board) (st : structure) : bool :=
  forallb (fun p =>
    let '(x, y) := p in
    existsb (Nat.eqb (fst x)) (s_free st) &&
    existsb (Nat.eqb (fst y)) (s_free st) &&
    (((fst y =? fst x) && (snd y =? S (snd x))) ||
     (negb (fst x =? fst y) &&
      (snd x =? length (col b (fst x))) &&
      (snd y =? length (col b (fst y))))))
  (s_weak st).

Definition check_partition (b : board) (st : structure) : bool :=
  forallb (fun c =>
    forallb (fun r =>
      match owner b (c, r) with
      | Some _ => true
      | None =>
          existsb (cell_eqb (c, r)) (unit_cells st) ||
          (existsb (Nat.eqb c) (s_free st) && (r <? topc st c)) ||
          match s_frozen st with
          | Some (fc, ft) => (c =? fc) && (ft - 1 <=? r)
          | None => false
          end
      end)
    (seq 0 7))
  (seq 0 8).

Definition check_mode (b : board) (st : structure) : bool :=
  if s_parity st then
    Nat.even (count_empty b (freezone b st))
  else
    match s_strong st, s_rigid st, s_frozen st with
    | [], [], None => true
    | _, _, _ => false
    end.

Definition check_cover (d : player) (b : board) (st : structure) : bool :=
  forallb (fun L =>
    existsb (fun y =>
      match owner b y with Some p => peqb p d | None => false end) L ||
    existsb (fun p => existsb (cell_eqb (snd p)) L) (s_strong st) ||
    existsb (fun p => existsb (cell_eqb (fst p)) L && existsb (cell_eqb (snd p)) L) (all_pairs st) ||
    match s_frozen st with
    | Some (fc, ft) =>
        existsb (fun y => (fst y =? fc) && (ft <=? snd y)) L
    | None => false
    end)
  lines.

Definition check_static (d : player) (b : board) (st : structure) : bool :=
  check_wf b &&
  check_frozen d b st &&
  nodupb cell_eqb (unit_cells st) &&
  check_cells b st &&
  check_strong st &&
  check_rigid b st &&
  check_rigid_notfree st &&
  check_weak b st &&
  check_partition b st &&
  nodupb Nat.eqb (s_free st) &&
  forallb (fun c => c <? 8) (s_free st) &&
  check_mode b st &&
  check_cover d b st.

Lemma check_static_sound : forall d b st,
  check_static d b st = true -> Static d b st.
Proof.
  intros d b st Hcs.
  unfold check_static in Hcs.
  rewrite !andb_true_iff in Hcs.
  destruct Hcs as [[[[[[[[[[[[Hwf Hfr] Hnd] Hcells] Hstr] Hrig] Hrnf] Hweak] Hpart] Hfnd] Hfrange] Hmode] Hcover].
  constructor.
  - apply check_wf_sound; exact Hwf.
  - unfold check_frozen in Hfr.
    intros fc ft Efr. rewrite Efr in Hfr.
    rewrite !andb_true_iff, !Nat.ltb_lt in Hfr.
    destruct Hfr as [[[Hfc Hft] Hlen] Hexists].
    split; [exact Hfc|split; [exact Hft|split; [exact Hlen|]]].
    apply existsb_exists in Hexists as [L [HinL Hand]].
    exists L; split; [exact HinL|].
    rewrite andb_true_iff in Hand; destruct Hand as [Hfc_in Hall].
    apply existsb_exists in Hfc_in as [fc_ft [Hin_fc Heq_fc]].
    apply cell_eqb_spec in Heq_fc; subst fc_ft.
    split; [exact Hin_fc|].
    intros y Hiny Hne.
    apply forallb_forall with (x := y) in Hall; [|exact Hiny].
    rewrite orb_true_iff in Hall.
    destruct Hall as [Heq_y | Howner].
    + apply cell_eqb_spec in Heq_y; subst y; contradiction.
    + destruct (owner b y) as [pl|] eqn:Epl; [|discriminate].
      apply peqb_eq in Howner; subst pl; reflexivity.
  - apply (nodupb_NoDup cell_eqb cell_eqb_spec); exact Hnd.
  - unfold check_cells in Hcells.
    rewrite forallb_forall in Hcells.
    intros x Hinx.
    apply Hcells in Hinx.
    rewrite !andb_true_iff, !Nat.ltb_lt in Hinx.
    destruct Hinx as [[Hfst Hsnd] Hown].
    destruct (owner b x) eqn:Eown; [discriminate|].
    split; [exact Hfst|split; [exact Hsnd|reflexivity]].
  - unfold check_strong in Hstr.
    rewrite forallb_forall in Hstr.
    intros lo hi Hin.
    apply Hstr in Hin.
    rewrite andb_true_iff, !Nat.eqb_eq in Hin.
    exact Hin.
  - unfold check_rigid in Hrig.
    rewrite forallb_forall in Hrig.
    intros x y Hin.
    apply Hrig in Hin.
    rewrite andb_true_iff, negb_true_iff, Nat.eqb_neq, orb_true_iff in Hin.
    destruct Hin as [Hne [Hbase | Hstep]].
    + split; [exact Hne|left].
      rewrite andb_true_iff, !Nat.eqb_eq in Hbase.
      exact Hbase.
    + split; [exact Hne|right].
      rewrite !andb_true_iff, !Nat.ltb_lt in Hstep.
      destruct Hstep as [[Hsnd_x Hsnd_y] Hexists].
      split; [exact Hsnd_x|split; [exact Hsnd_y|]].
      apply existsb_exists in Hexists as [q [Hinq Hor]].
      rewrite orb_true_iff in Hor.
      destruct Hor as [Hand | Hand]; [left|right];
      rewrite andb_true_iff in Hand; destruct Hand as [H1 H2];
      destruct q as [q1 q2]; simpl in *;
      apply cell_eqb_spec in H1; apply cell_eqb_spec in H2;
      subst; exact Hinq.
  - unfold check_rigid_notfree in Hrnf.
    rewrite forallb_forall in Hrnf.
    intros x Hinx.
    apply Hrnf in Hinx.
    rewrite negb_true_iff in Hinx.
    intros Hinf.
    assert (Hex : existsb (Nat.eqb (fst x)) (s_free st) = true).
    { apply existsb_exists. exists (fst x); split; [exact Hinf|apply Nat.eqb_refl]. }
    rewrite Hex in Hinx; discriminate.
  - unfold check_weak in Hweak.
    rewrite forallb_forall in Hweak.
    intros x y Hin.
    apply Hweak in Hin.
    rewrite !andb_true_iff in Hin.
    destruct Hin as [[Hfx Hfy] Hor].
    apply existsb_exists in Hfx as [c1 [Hinc1 Heq1]]; apply Nat.eqb_eq in Heq1; subst c1.
    apply existsb_exists in Hfy as [c2 [Hinc2 Heq2]]; apply Nat.eqb_eq in Heq2; subst c2.
    split; [exact Hinc1|split; [exact Hinc2|]].
    rewrite orb_true_iff in Hor.
    destruct Hor as [Hvert | Hbase].
    + left. rewrite andb_true_iff, !Nat.eqb_eq in Hvert. exact Hvert.
    + right. rewrite !andb_true_iff, negb_true_iff, Nat.eqb_neq, !Nat.eqb_eq in Hbase.
      destruct Hbase as [[Hne Hx] Hy].
      split; [exact Hne|split; [exact Hx|exact Hy]].
  - unfold check_partition in Hpart.
    rewrite forallb_forall in Hpart.
    intros c r Hc Hr Hown.
    assert (Hinc : In c (seq 0 8)) by (apply in_seq; lia).
    apply Hpart in Hinc.
    rewrite forallb_forall in Hinc.
    assert (Hinr : In r (seq 0 7)) by (apply in_seq; lia).
    apply Hinc in Hinr.
    rewrite Hown in Hinr.
    rewrite !orb_true_iff in Hinr.
    destruct Hinr as [[Hu | Hfree] | Hfrz].
    + left. apply existsb_exists in Hu as [w [Hinw Heqw]].
      apply cell_eqb_spec in Heqw; subst w; exact Hinw.
    + right; left.
      rewrite andb_true_iff, Nat.ltb_lt in Hfree.
      destruct Hfree as [Hinf Htop].
      apply existsb_exists in Hinf as [c0 [Hinc0 Heq0]].
      apply Nat.eqb_eq in Heq0; subst c0.
      split; [exact Hinc0|exact Htop].
    + right; right.
      destruct (s_frozen st) as [[fc ft]|] eqn:Efrz; [|discriminate].
      rewrite andb_true_iff, Nat.eqb_eq, Nat.leb_le in Hfrz.
      destruct Hfrz as [-> Hle].
      exists ft; split; [reflexivity|exact Hle].
  - apply (nodupb_NoDup Nat.eqb Nat.eqb_eq); exact Hfnd.
  - rewrite forallb_forall in Hfrange.
    intros c Hinc. apply Hfrange in Hinc. apply Nat.ltb_lt in Hinc. exact Hinc.
  - unfold check_mode in Hmode.
    destruct (s_parity st) eqn:Epar.
    + exact Hmode.
    + destruct (s_strong st) as [|? ?]; [|discriminate].
      destruct (s_rigid st) as [|? ?]; [|discriminate].
      destruct (s_frozen st) as [[? ?]|]; [discriminate|].
      split; [reflexivity|split; reflexivity].
  - unfold check_cover in Hcover.
    rewrite forallb_forall in Hcover.
    intros L HinL. apply Hcover in HinL.
    rewrite !orb_true_iff in HinL.
    destruct HinL as [[[H1 | H2] | H3] | H4].
    + left. apply existsb_exists in H1 as [y [Hiny Hown]].
      exists y; split; [exact Hiny|].
      destruct (owner b y) as [pl|] eqn:Epl; [|discriminate].
      apply peqb_eq in Hown; subst pl; reflexivity.
    + right; left.
      apply existsb_exists in H2 as [pr [Hinpr HinL2]].
      apply existsb_exists in HinL2 as [hi [Hin_hi Heq_hi]].
      apply cell_eqb_spec in Heq_hi; subst hi.
      exists (fst pr), (snd pr); split; [destruct pr; exact Hinpr | exact Hin_hi].
    + right; right; left.
      apply existsb_exists in H3 as [pr [Hinpr Hand]].
      rewrite andb_true_iff in Hand; destruct Hand as [H3a H3b].
      apply existsb_exists in H3a as [x [Hinx Heqx]].
      apply existsb_exists in H3b as [y [Hiny Heqy]].
      apply cell_eqb_spec in Heqx; apply cell_eqb_spec in Heqy; subst.
      exists (fst pr), (snd pr); split; [destruct pr; exact Hinpr | split; assumption].
    + right; right; right.
      destruct (s_frozen st) as [[fc ft]|] eqn:Efrz; [|discriminate].
      apply existsb_exists in H4 as [[yc yr] [Hiny Hand]].
      simpl in Hand.
      rewrite andb_true_iff, Nat.eqb_eq, Nat.leb_le in Hand.
      destruct Hand as [-> Hle].
      exists fc, ft, yr; split; [reflexivity | split; [exact Hiny | exact Hle]].
Qed.

(** ** Certificate datatype and fast verified checker *)

Inductive cert_step : Type :=
| CS_Full : cert_step
| CS_Leaf : structure -> cert_step
| CS_DefWin : nat -> cert_step
| CS_DefMove : nat -> nat -> cert_step
| CS_AttMoves : list (nat * nat) -> cert_step.

Definition certificate : Type := list cert_step.

Fixpoint find_child (c : nat) (l : list (nat * nat)) : option nat :=
  match l with
  | [] => None
  | (c0, idx) :: t => if c =? c0 then Some idx else find_child c t
  end.

Definition all_cols : list nat := seq 0 8.

Lemma in_all_cols : forall c, c < 8 -> In c all_cols.
Proof.
  intros c Hc. unfold all_cols. apply in_seq. lia.
Qed.

Opaque all_cols.

Fixpoint check_cert_node (cert : certificate) (fuel : nat)
                         (d : player) (b : board) (s : player) (idx : nat) : bool :=
  match fuel with
  | O => false
  | S f =>
      match nth_error cert idx with
      | None => false
      | Some CS_Full => full b
      | Some (CS_Leaf st) =>
          peqb s (other d) && check_static d b st
      | Some (CS_DefWin c) =>
          peqb s d && legal b c && has_line (play b c d) d
      | Some (CS_DefMove c child_idx) =>
          peqb s d && legal b c &&
          check_cert_node cert f d (play b c d) (other d) child_idx
      | Some (CS_AttMoves branches) =>
          peqb s (other d) && negb (full b) &&
          forallb (fun c =>
            if legal b c then
              negb (has_line (play b c (other d)) (other d)) &&
              match find_child c branches with
              | Some ch_idx => check_cert_node cert f d (play b c (other d)) d ch_idx
              | None => false
              end
            else true) all_cols
      end
  end.

Theorem cert_sound : forall fuel (cert : certificate) (d : player) (b : board) (s : player) (idx : nat),
  check_cert_node cert fuel d b s idx = true ->
  safe d b s.
Proof.
  induction fuel as [|f IH]; intros cert d b s idx Hchk; [simpl in Hchk; discriminate|].
  simpl in Hchk.
  destruct (nth_error cert idx) as [step|] eqn:Estep; [|discriminate].
  destruct step as [|st|c|c child_idx|branches].
  - (* CS_Full *)
    apply safe_full; exact Hchk.
  - (* CS_Leaf *)
    rewrite andb_true_iff in Hchk; destruct Hchk as [Hs Hst].
    apply peqb_eq in Hs; subst s.
    apply check_static_sound in Hst.
    apply (structure_sound d b st Hst).
  - (* CS_DefWin *)
    rewrite !andb_true_iff in Hchk; destruct Hchk as [[Hs Hleg] Hwin].
    apply peqb_eq in Hs; subst s.
    apply (safe_def d b c Hleg (or_introl Hwin)).
  - (* CS_DefMove *)
    rewrite !andb_true_iff in Hchk; destruct Hchk as [[Hs Hleg] Hrec].
    apply peqb_eq in Hs; subst s.
    apply (safe_def d b c Hleg (or_intror (IH cert d (play b c d) (other d) child_idx Hrec))).
  - (* CS_AttMoves *)
    rewrite !andb_true_iff, negb_true_iff in Hchk; destruct Hchk as [[Hs Hnotfull] Hbranches].
    apply peqb_eq in Hs; subst s.
    apply safe_att; [exact Hnotfull|].
    intros c' Hc'.
    assert (Hinc' : In c' all_cols) by (apply in_all_cols; apply legal_spec in Hc' as [Hc'8 _]; lia).
    pose proof (proj1 (forallb_forall _ _) Hbranches c' Hinc') as Hstep.
    simpl in Hstep.
    rewrite Hc' in Hstep.
    rewrite andb_true_iff, negb_true_iff in Hstep.
    destruct Hstep as [Hnl Hch].
    split; [exact Hnl|].
    destruct (find_child c' branches) as [ch_idx|] eqn:Ech; [|discriminate].
    apply (IH cert d (play b c' (other d)) d ch_idx Hch).
Qed.

Theorem cert_fair : forall (c0 : nat) (cert_w cert_b : certificate) (fuel_w fuel_b : nat) (idx_w idx_b : nat),
  legal initial c0 = true ->
  check_cert_node cert_w fuel_w White (play initial c0 White) Black idx_w = true ->
  check_cert_node cert_b fuel_b Black initial White idx_b = true ->
  game_value = Draw.
Proof.
  intros c0 cert_w cert_b fuel_w fuel_b idx_w idx_b Hleg Hw Hb.
  apply (mutual_safety_draw c0 Hleg).
  - apply (cert_sound fuel_w cert_w White (play initial c0 White) Black idx_w Hw).
  - apply (cert_sound fuel_b cert_b Black initial White idx_b Hb).
Qed.

(** ** Concrete Machine-Checked Structural & Parity Theorems *)

(** Opening board after White plays at center-left column 3: (3, 0). *)
Definition b_open : board := play initial 3 White.

(** Theorem 1 (First-Player Parity Obstruction at Ply 1):
    After White's opening move at (3, 0), exactly 55 empty cells remain on the
    8x7 board, which has odd parity ([Nat.even 55 = false]). Hence no pure
    unfrozen Claimeven pairing ([s_parity = true, s_frozen = None]) can
    partition all 55 remaining cells into 2-cell pairs. *)
Theorem parity_trap_ply1 :
  empties b_open = 55 /\ Nat.even (empties b_open) = false.
Proof.
  vm_compute. split; reflexivity.
Qed.

(** The 27-pair opening structure (24 vertical dominoes + 3 ground cross-pairs,
    leaving dead cell (4, 6) unassigned). *)
Definition white_27pair_struct : structure := {|
  s_parity := true;
  s_frozen := None;
  s_strong :=
    (* Col 3 above (3,0): 3 strong dominoes *)
    [((3,1),(3,2)); ((3,3),(3,4)); ((3,5),(3,6))] ++
    (* Col 4 below dead cell (4,6): 3 strong dominoes *)
    [((4,0),(4,1)); ((4,2),(4,3)); ((4,4),(4,5))] ++
    (* Cols 0, 1, 2, 5, 6, 7 above row 0: 6 * 3 = 18 strong dominoes *)
    [((0,1),(0,2)); ((0,3),(0,4)); ((0,5),(0,6));
     ((1,1),(1,2)); ((1,3),(1,4)); ((1,5),(1,6));
     ((2,1),(2,2)); ((2,3),(2,4)); ((2,5),(2,6));
     ((5,1),(5,2)); ((5,3),(5,4)); ((5,5),(5,6));
     ((6,1),(6,2)); ((6,3),(6,4)); ((6,5),(6,6));
     ((7,1),(7,2)); ((7,3),(7,4)); ((7,5),(7,6))];
  s_rigid :=
    (* 3 ground-level row-0 cross-pairs *)
    [((0,0),(7,0)); ((1,0),(5,0)); ((2,0),(6,0))];
  s_weak := [];
  s_free := []
|}.

(** Theorem 2 (27-Pair Opening Line Coverage):
    All 76 winning lines of length 5 on the 8x7 board are covered by White's
    opening stone at (3, 0) together with the 24 vertical dominoes, even with
    cell (4, 6) completely unassigned. *)
Theorem opening_27pair_line_cover :
  check_cover White b_open white_27pair_struct = true.
Proof.
  vm_compute. reflexivity.
Qed.

(** The minimal 10-Cell Core structure: strong vertical dominoes ONLY in
    Columns 2, 4, and 6 (giving 9 upper cells + opening stone (3,0) = 10 cells)
    and weak vertical dominoes in Columns 0, 1, 3, 5, 7. *)
Definition white_core10_struct : structure := {|
  s_parity := false;
  s_frozen := None;
  s_strong :=
    [((2,1),(2,2)); ((2,3),(2,4)); ((2,5),(2,6));
     ((4,0),(4,1)); ((4,2),(4,3)); ((4,4),(4,5));
     ((6,1),(6,2)); ((6,3),(6,4)); ((6,5),(6,6))];
  s_rigid := [];
  s_weak :=
    [((0,1),(0,2)); ((0,3),(0,4)); ((0,5),(0,6));
     ((1,1),(1,2)); ((1,3),(1,4)); ((1,5),(1,6));
     ((3,1),(3,2)); ((3,3),(3,4)); ((3,5),(3,6));
     ((5,1),(5,2)); ((5,3),(5,4)); ((5,5),(5,6));
     ((7,1),(7,2)); ((7,3),(7,4)); ((7,5),(7,6))];
  s_free := [0; 1; 3; 5; 7]
|}.

(** Theorem 3 (10-Cell Core Sufficiency):
    The 10 guaranteed White cells {(3,0), (2,2), (2,4), (2,6), (4,1), (4,3),
    (4,5), (6,2), (6,4), (6,6)} intersect all 52 horizontal and diagonal
    winning lines on the 8x7 board, while weak dominoes in the remaining
    5 columns cover all 24 vertical winning lines. *)
Theorem core10_covers_all_76_lines :
  check_cover White b_open white_core10_struct = true.
Proof.
  vm_compute. reflexivity.
Qed.

(** Theorem 4 (Double-Blocking of Dead Cell (4, 6)):
    Cell (4, 6) participates in exactly 6 winning lines of length 5, and every
    single one of those 6 winning lines contains at least 2 cells from White's
    guaranteed upper domino set. *)
Definition lines_through_4_6 : list (list cell) :=
  filter (existsb (cell_eqb (4, 6))) lines.

Definition white_guaranteed_cells : list cell :=
  (3, 0) :: map snd (s_strong white_27pair_struct).

Theorem dead_cell_4_6_six_lines_double_blocked :
  length lines_through_4_6 = 6 /\
  forallb (fun L =>
    2 <=? length (filter (fun x => existsb (cell_eqb x) white_guaranteed_cells) L))
    lines_through_4_6 = true.
Proof.
  vm_compute. split; reflexivity.
Qed.

(** Theorem 5 (Rule R3 Frozen-Threat Parity Restoration):
    Whenever the total number of empty cells E in {7, 9, ..., 55} is odd and
    White holds a 4-in-a-row threat in column fc at an odd row ft in {1, 3, 5},
    freezing the 7 - (ft - 1) in {7, 5, 3} cells from the poisoned cell
    (fc, ft - 1) to the top of column fc leaves an EVEN number of empty cells
    in the remaining freezone, satisfying [st_mode] in [C5Rules.v]. *)
Theorem r3_frozen_column_restores_even_parity :
  forallb (fun E =>
    forallb (fun ft => Nat.even (E - (7 - (ft - 1)))) [1; 3; 5])
    [7; 9; 11; 13; 15; 17; 19; 21; 23; 25; 27; 29;
     31; 33; 35; 37; 39; 41; 43; 45; 47; 49; 51; 53; 55] = true.
Proof.
  vm_compute. reflexivity.
Qed.
