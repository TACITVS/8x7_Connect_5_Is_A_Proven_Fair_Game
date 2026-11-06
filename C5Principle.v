(** * The invariant principle for follow-up strategies

    If a property [Inv] of positions (attacker to move) is such that every
    attacker move can be answered by a legal defender move that either
    wins at once or re-establishes [Inv] — and the attacker's move itself
    never completes a line — then the defender never loses from any
    position satisfying [Inv].  Proved by induction on the number of
    empty cells; no enumeration of positions is involved. *)
From Stdlib Require Import List Arith Bool Lia.
Import ListNotations.
From C5 Require Import C5Game C5Board.

Definition responds (d : player) (Inv : board -> Prop) : Prop :=
  forall b, wf b -> Inv b -> full b = false ->
  forall c, legal b c = true ->
    has_line (play b c (other d)) (other d) = false /\
    (full (play b c (other d)) = true \/
     exists c', legal (play b c (other d)) c' = true /\
       (has_line (play (play b c (other d)) c' d) d = true \/
        Inv (play (play b c (other d)) c' d))).

Theorem follow_up_principle : forall d Inv,
  responds d Inv -> forall b, wf b -> Inv b -> safe d b (other d).
Proof.
  intros d Inv R.
  assert (Main : forall n b, empties b <= n -> wf b -> Inv b -> safe d b (other d)).
  { induction n as [|n IH]; intros b Hn Hwf HI;
      destruct (full b) eqn:F; try (apply safe_full; exact F).
    - exfalso. apply full_false_iff in F as [c Hc].
      pose proof (empties_play b c White Hwf Hc). lia.
    - apply safe_att; [exact F|]. intros c Hc.
      destruct (R b Hwf HI F c Hc) as [Hno Hresp]. split; [exact Hno|].
      assert (Hwf1 : wf (play b c (other d))) by (apply wf_play; auto).
      destruct Hresp as [Hf | [c' [Hc' [Hwin | HI2]]]].
      + apply safe_full; exact Hf.
      + eapply safe_def; [exact Hc'|left; exact Hwin].
      + eapply safe_def; [exact Hc'|right].
        apply IH; auto.
        * pose proof (empties_play b c (other d) Hwf Hc).
          pose proof (empties_play _ c' d Hwf1 Hc'). lia.
        * apply wf_play; auto. }
  intros b Hwf HI. eapply Main; eauto.
Qed.

(** ** Utilities on cells, pairs and counting *)

Definition cell_eq_dec : forall x y : cell, {x = y} + {x <> y}.
Proof. decide equality; apply Nat.eq_dec. Defined.

Definition pair_cells (l : list (cell * cell)) : list cell :=
  flat_map (fun pr => [fst pr; snd pr]) l.

Lemma pair_cells_app : forall l1 l2,
  pair_cells (l1 ++ l2) = pair_cells l1 ++ pair_cells l2.
Proof. intros; unfold pair_cells; apply flat_map_app. Qed.

Lemma in_pair_cells : forall l z,
  In z (pair_cells l) <-> exists pr, In pr l /\ (z = fst pr \/ z = snd pr).
Proof.
  intros l z; unfold pair_cells; rewrite in_flat_map; split.
  - intros [pr [Hin Hz]]. exists pr; split; auto.
    simpl in Hz; destruct Hz as [H|[H|[]]]; auto.
  - intros [pr [Hin Hz]]. exists pr; split; auto.
    simpl; destruct Hz; auto.
Qed.

Lemma NoDup_app_disjoint : forall (A : Type) (l1 l2 : list A) z,
  NoDup (l1 ++ l2) -> In z l1 -> In z l2 -> False.
Proof.
  induction l1 as [|a l1 IH]; intros l2 z Hnd H1 H2; [destruct H1|].
  inversion Hnd as [|? ? Hnot Hnd']; subst.
  destruct H1 as [->|H1].
  - apply Hnot. apply in_app_iff; right; exact H2.
  - eapply IH; eauto.
Qed.

Lemma NoDup_app_l : forall (A : Type) (l1 l2 : list A), NoDup (l1 ++ l2) -> NoDup l1.
Proof.
  induction l1 as [|a l1 IH]; intros l2 H; [constructor|].
  inversion H as [|? ? Hnot Hnd']; subst. constructor; eauto.
  intros Hin; apply Hnot; apply in_app_iff; auto.
Qed.

Lemma NoDup_app_r : forall (A : Type) (l1 l2 : list A), NoDup (l1 ++ l2) -> NoDup l2.
Proof.
  induction l1 as [|a l1 IH]; intros l2 H; simpl in H; auto.
  inversion H; subst; eauto.
Qed.

Lemma NoDup_app : forall (A : Type) (l1 l2 : list A),
  NoDup l1 -> NoDup l2 -> (forall z, In z l1 -> In z l2 -> False) ->
  NoDup (l1 ++ l2).
Proof.
  induction l1 as [|a l1 IH]; intros l2 H1 H2 Hdisj; [exact H2|].
  inversion H1 as [|? ? Hnot H1']; subst.
  simpl. constructor.
  - intros Hin. apply in_app_iff in Hin as [Hin|Hin].
    + contradiction.
    + eapply Hdisj; [left; reflexivity|exact Hin].
  - apply IH; auto. intros z Hz1 Hz2. eapply Hdisj; [right; exact Hz1|exact Hz2].
Qed.

Lemma NoDup_map_inj : forall (A B : Type) (f : A -> B) (l : list A),
  (forall x y, In x l -> In y l -> f x = f y -> x = y) ->
  NoDup l -> NoDup (map f l).
Proof.
  induction l as [|a l IH]; intros Hinj Hnd; [constructor|].
  inversion Hnd as [|? ? Hnot Hnd']; subst.
  simpl. constructor.
  - intros Hin. apply in_map_iff in Hin as [x [E Hx]].
    assert (a = x) by (apply (Hinj a x); simpl; auto).
    subst. contradiction.
  - apply IH; auto. intros x y Hx Hy. apply Hinj; simpl; auto.
Qed.

(** In a list of pairs with pairwise distinct cells, a cell determines its pair. *)
Lemma pair_unique : forall l pr pr' z,
  NoDup (pair_cells l) -> In pr l -> In pr' l ->
  (z = fst pr \/ z = snd pr) -> (z = fst pr' \/ z = snd pr') -> pr = pr'.
Proof.
  induction l as [|p0 l IH]; intros pr pr' z Hnd Hin Hin' Hz Hz'; [destruct Hin|].
  simpl in Hnd. inversion Hnd as [|? ? Hn1 Hnd1]; subst.
  inversion Hnd1 as [|? ? Hn2 Hnd2]; subst.
  assert (Hcells : forall q, In q l -> z = fst q \/ z = snd q -> In z (pair_cells l)).
  { intros q Hq Hzq. apply in_pair_cells. eauto. }
  destruct Hin as [<-|Hin], Hin' as [<-|Hin']; auto.
  - exfalso. specialize (Hcells _ Hin' Hz').
    destruct Hz as [->| ->].
    + apply Hn1; right; auto.
    + apply Hn2; auto.
  - exfalso. specialize (Hcells _ Hin Hz).
    destruct Hz' as [->| ->].
    + apply Hn1; right; auto.
    + apply Hn2; auto.
  - eapply IH; eauto.
Qed.

Lemma pair_distinct : forall l pr,
  NoDup (pair_cells l) -> In pr l -> fst pr <> snd pr.
Proof.
  induction l as [|p0 l IH]; intros pr Hnd Hin; [destruct Hin|].
  simpl in Hnd. inversion Hnd as [|? ? Hn1 Hnd1]; subst.
  inversion Hnd1; subst.
  destruct Hin as [<-|Hin].
  - intros E; apply Hn1; left; auto.
  - eapply IH; eauto.
Qed.

Definition is_empty (b : board) (x : cell) : bool :=
  match owner b x with None => true | Some _ => false end.

Definition count_empty (b : board) (l : list cell) : nat :=
  length (filter (is_empty b) l).

(** Effect of filling one empty cell [z] on the number of empty cells of [l]. *)
Lemma count_fill : forall (b b2 : board) (z : cell) (l : list cell),
  NoDup l ->
  owner b z = None -> owner b2 z <> None ->
  (forall w, w <> z -> owner b2 w = owner b w) ->
  (In z l -> S (count_empty b2 l) = count_empty b l) /\
  (~ In z l -> count_empty b2 l = count_empty b l).
Proof.
  intros b b2 z l Hnd Hz Hz2 Hsame.
  induction l as [|w l IH]; [split; [intros []|reflexivity]|].
  inversion Hnd as [|? ? Hnot Hnd']; subst.
  destruct (IH Hnd') as [IH1 IH2].
  unfold count_empty in *. simpl.
  destruct (cell_eq_dec w z) as [->|Hne].
  - assert (E1 : is_empty b z = true) by (unfold is_empty; rewrite Hz; reflexivity).
    assert (E2 : is_empty b2 z = false)
      by (unfold is_empty; destruct (owner b2 z); congruence).
    rewrite E1, E2. simpl.
    split; [intros _; rewrite IH2 by auto; reflexivity
           |intros H; exfalso; apply H; left; reflexivity].
  - assert (E : is_empty b2 w = is_empty b w)
      by (unfold is_empty; rewrite (Hsame w Hne); reflexivity).
    rewrite E.
    split.
    + intros [E'|Hin]; [congruence|].
      destruct (is_empty b w); simpl; rewrite <- (IH1 Hin); reflexivity.
    + intros Hnin. assert (~ In z l) by (intros H; apply Hnin; right; auto).
      destruct (is_empty b w); simpl; rewrite IH2; auto.
Qed.

Lemma count_pos : forall b l,
  count_empty b l > 0 -> exists w, In w l /\ owner b w = None.
Proof.
  intros b l H. unfold count_empty in H.
  destruct (filter (is_empty b) l) as [|w r] eqn:E; simpl in H; [lia|].
  assert (Hw : In w (filter (is_empty b) l)) by (rewrite E; left; auto).
  apply filter_In in Hw as [Hin He]. exists w; split; auto.
  unfold is_empty in He. destruct (owner b w); congruence.
Qed.
