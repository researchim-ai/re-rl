"""Масштабируемые задачи: число звеньев и длина решения растут вместе с уровнем."""

import math
import random
import re

import pytest

from re_rl.tasks.generators import ALL_TASK_GENERATORS
from re_rl.tasks.math.discrete.greedy_coins.task import greedy_picks, optimal_count
from re_rl.tasks.math.logic.line_infection.task import spread_once
from re_rl.tasks.math.logic.next_greater.task import next_greater
from re_rl.tasks.math.probability.polya_urn.task import sequence_probability
from re_rl.tasks.ml.kmeans_rounds.task import cluster_rounds
from re_rl.tasks.math.analysis.difference_table.task import extend_table, polynomial_value
from re_rl.tasks.math.discrete.cf_expand.task import convergents
from re_rl.tasks.physics.networks.network_reduce.task import equivalent, leaf_sum
from re_rl.tasks.physics.quantum.decay_generations.task import decay_tick
from re_rl.tasks.physics.electricity.charge_redistribute.task import share_sequence
from re_rl.tasks.math.discrete.sandpile_path.task import stabilize
from re_rl.tasks.physics.relativity.boost_chain.task import add_boosts
from re_rl.tasks.math.probability.markov_steps.task import markov_weights
from re_rl.tasks.math.probability.sir_ticks.task import sir_run
from re_rl.tasks.math.algebra.poly_div.task import poly_divmod, poly_mul
from re_rl.tasks.math.logic.johnson_span.task import completion, johnson_order
from re_rl.tasks.math.logic.lights_path.task import apply_presses, chase_presses
from re_rl.tasks.physics.mechanics.weighing_trace.task import follow_weighings
from re_rl.tasks.physics.electricity.switch_net.task import evaluate, flip_leaf
from re_rl.tasks.math.logic.domino_chain.task import first_break
from re_rl.tasks.math.logic.bound_scan.task import scan_bounds
from re_rl.tasks.physics.mechanics.billiard_box.task import billiard_trace
from re_rl.tasks.physics.mechanics.mobile_torque.task import rod_balanced
from re_rl.tasks.physics.mechanics.traffic_light.task import departure_times
from re_rl.tasks.physics.measurements.drop_cross.task import first_cross, running_sums
from re_rl.tasks.math.logic.claim_count.task import consistent_counts
from re_rl.tasks.math.logic.quorum_rise.task import play_votes
from re_rl.tasks.physics.mechanics.ternary_balance.task import place_weights
from re_rl.tasks.physics.mechanics.siding_counter.task import run_sidings
from re_rl.tasks.physics.mechanics.motion_segments.task import integrate_motion
from re_rl.tasks.physics.mechanics.slope_run.task import run_slopes
from re_rl.tasks.physics.mechanics.echo_bounce.task import echo_hits
from re_rl.tasks.physics.mechanics.fall_ticks.task import fall_trace
from re_rl.tasks.physics.mechanics.friction_slide.task import slide_trace
from re_rl.tasks.physics.thermodynamics.heat_mix.task import mix_temperature
from re_rl.tasks.physics.thermodynamics.heat_rod.task import heat_ticks
from re_rl.tasks.physics.waves.wave_row.task import wave_ticks
from re_rl.tasks.physics.electricity.leak_charge.task import leak_trace
from re_rl.tasks.physics.electricity.resistor_ladder.task import ladder_trace
from re_rl.tasks.physics.waves.doppler_chain.task import doppler_trace
from re_rl.tasks.physics.fluids.float_load.task import load_trace
from re_rl.tasks.physics.thermodynamics.melt_heat.task import melt_trace
from re_rl.tasks.physics.mechanics.throw_ticks.task import throw_trace
from re_rl.tasks.physics.mechanics.impulse_run.task import impulse_trace
from re_rl.tasks.physics.mechanics.beam_load.task import beam_trace
from re_rl.tasks.physics.mechanics.mass_shift.task import shift_trace
from re_rl.tasks.physics.mechanics.spring_join.task import join_trace
from re_rl.tasks.physics.waves.optic_path.task import optic_trace
from re_rl.tasks.physics.waves.pulse_meet.task import pulse_trace
from re_rl.tasks.physics.thermodynamics.cool_ticks.task import cool_trace
from re_rl.tasks.physics.electricity.series_cap.task import cap_trace
from re_rl.tasks.physics.fluids.column_pressure.task import column_trace
from re_rl.tasks.physics.mechanics.cradle_hit.task import cradle_trace
from re_rl.tasks.physics.quantum.photon_eject.task import photon_trace
from re_rl.tasks.physics.astrophysics.orbit_years.task import orbit_trace
from re_rl.tasks.physics.waves.grating_order.task import grating_trace
from re_rl.tasks.physics.magnetism.wire_force.task import wire_trace
from re_rl.tasks.physics.astrophysics.escape_speed.task import escape_trace
from re_rl.tasks.physics.waves.harmonic_nodes.task import node_trace
from re_rl.tasks.physics.waves.snell_shift.task import snell_trace
from re_rl.tasks.physics.thermodynamics.heat_steps.task import heat_trace
from re_rl.tasks.physics.fluids.hydraulic_lift.task import hydraulic_trace
from re_rl.tasks.math.logic.hat_line.task import rear_parity, saved_count
from re_rl.tasks.math.logic.reagent_chain.task import react
from re_rl.tasks.math.logic.tax_brackets.task import apply_tax
from re_rl.tasks.math.logic.codon_scan.task import STOPS, scan_codons
from re_rl.tasks.math.logic.dose_schedule.task import concentration_trace
from re_rl.tasks.math.logic.melody_walk.task import walk_melody
from re_rl.tasks.math.logic.fifo_cost.task import fifo_account
from re_rl.tasks.math.logic.borda_count.task import borda_scores, borda_winner
from re_rl.tasks.math.logic.shift_add.task import shift_add
from re_rl.tasks.math.logic.rally_lead.task import rally_trace
from re_rl.tasks.math.discrete.pascal_row.task import pascal_rows
from re_rl.tasks.math.algebra.fraction_ops.task import apply_fraction_ops
from re_rl.tasks.math.discrete.stern_path.task import stern_walk
from re_rl.tasks.math.discrete.partition_count.task import distinct_ways, partition_ways
from re_rl.tasks.math.discrete.derange_count.task import binom, derange_table
from re_rl.tasks.math.algebra.gauss_mul.task import multiply_gauss
from re_rl.tasks.math.discrete.perm_compose.task import compose_perms, inversion_count
from re_rl.tasks.math.geometry.cover_span.task import cover_trace, sweep_cover
from re_rl.tasks.math.discrete.reverse_add.task import is_palindrome, reverse_add_trace
from re_rl.tasks.math.probability.stream_median.task import median_trace
from re_rl.tasks.math.discrete.totient_row.task import totient_values
from re_rl.tasks.math.discrete.coprime_count.task import inclusion_rows
from re_rl.tasks.math.algebra.digit_div.task import divide_digits
from re_rl.tasks.math.discrete.tree_depth.task import tree_depths
from re_rl.tasks.math.discrete.sign_walk.task import walk_signs
from re_rl.tasks.math.discrete.perm_rank.task import factorial_rank
from re_rl.tasks.math.discrete.lcm_rise.task import lcm_trace
from re_rl.tasks.math.discrete.zigzag_row.task import entringer_rows
from re_rl.tasks.math.discrete.record_highs.task import record_trace
from re_rl.tasks.math.discrete.sum_kinds.task import subset_growth
from re_rl.tasks.math.discrete.fib_word.task import fib_word_stats
from re_rl.tasks.math.probability.mode_track.task import mode_trace
from re_rl.tasks.math.discrete.look_say.task import look_say_once, look_say_trace
from re_rl.tasks.math.discrete.zeckendorf.task import fibonacci_list, zeckendorf_trace
from re_rl.tasks.math.discrete.roman_value.task import roman_trace
from re_rl.tasks.math.discrete.digit_stream.task import digit_stream
from re_rl.tasks.math.logic.deque_trace.task import deque_trace
from re_rl.tasks.math.discrete.dragon_fold.task import dragon_folds
from re_rl.tasks.math.discrete.permanent.task import permanent_trace
from re_rl.tasks.math.discrete.bead_count.task import bead_trace
from re_rl.tasks.math.discrete.negabase.task import negabase_trace
from re_rl.tasks.math.geometry.ulam_walk.task import ulam_trace
from re_rl.tasks.math.discrete.luhn_sum.task import luhn_trace
from re_rl.tasks.math.discrete.kaprekar_step.task import kaprekar_once, kaprekar_trace
from re_rl.tasks.math.discrete.morton_code.task import morton_trace
from re_rl.tasks.math.logic.stock_span.task import stock_spans
from re_rl.tasks.math.logic.candy_row.task import candy_passes
from re_rl.tasks.math.discrete.digit_fact.task import digit_fact_trace
from re_rl.tasks.math.discrete.recaman.task import recaman_trace
from re_rl.tasks.math.discrete.xor_basis.task import xor_basis_trace
from re_rl.tasks.math.discrete.palindrome_radius.task import palindrome_radii
from re_rl.tasks.math.discrete.squarefree_row.task import squarefree_flags
from re_rl.tasks.math.logic.fenwick_sum.task import fenwick_build, fenwick_prefix
from re_rl.tasks.math.logic.sparse_min.task import build_sparse, sparse_min
from re_rl.tasks.math.logic.z_array.task import z_values
from re_rl.tasks.math.logic.selection_swaps.task import selection_trace
from re_rl.tasks.math.logic.rho_cycle.task import rho_cycle
from re_rl.tasks.math.logic.tree_times.task import tree_times
from re_rl.tasks.math.logic.dutch_flag.task import dutch_trace
from re_rl.tasks.math.logic.window_distinct.task import distinct_windows
from re_rl.tasks.math.logic.stable_place.task import stable_order
from re_rl.tasks.math.logic.naive_find.task import naive_scan
from re_rl.tasks.math.logic.budget_take.task import budget_take
from re_rl.tasks.math.logic.skip_op.task import apply_ops
from re_rl.tasks.math.logic.retry_goal.task import retry_until
from re_rl.tasks.math.logic.signal_edges.task import signal_trace
from re_rl.tasks.math.logic.plan_gate.task import plan_trace
from re_rl.tasks.math.logic.tool_pick.task import tool_assign
from re_rl.tasks.math.logic.diff_count.task import diff_trace
from re_rl.tasks.math.logic.cell_patch.task import patch_trace
from re_rl.tasks.math.logic.pred_scan.task import pred_trace
from re_rl.tasks.math.logic.rate_limit.task import rate_flags
from re_rl.tasks.math.logic.lateness.task import lateness_trace
from re_rl.tasks.math.logic.switch_flip.task import flip_trace
from re_rl.tasks.math.geometry.turn_signs.task import turn_trace
from re_rl.tasks.math.logic.first_fit.task import first_fit
from re_rl.tasks.math.logic.plurality.task import plurality_trace
from re_rl.tasks.math.logic.floor_run.task import floor_trace
from re_rl.tasks.math.logic.saturate_count.task import saturate_trace
from re_rl.tasks.math.logic.undo_reg.task import undo_trace
from re_rl.tasks.math.logic.cover_point.task import cover_trace as cover_point_trace
from re_rl.tasks.math.logic.next_fit.task import next_fit
from re_rl.tasks.ml.sgd_online.task import sgd_trace
from re_rl.tasks.rl.actor_critic.task import critic_trace, preferred_action
from re_rl.tasks.rl.ucb_bandit.task import ucb_trace
from re_rl.tasks.ml.grad_clip.task import clip_trace
from re_rl.tasks.ml.weight_decay.task import decay_trace
from re_rl.tasks.ml.early_stop.task import stop_trace
from re_rl.tasks.ml.prototype_mean.task import nearer_class, prototype_trace
from re_rl.tasks.rl.target_sync.task import sync_trace
from re_rl.tasks.rl.replay_fifo.task import fifo_trace
from re_rl.tasks.rl.shape_reward.task import shape_trace
from re_rl.tasks.rl.eps_schedule.task import eps_trace
from re_rl.tasks.math.logic.scope_lookup.task import scope_lookup, scope_trace
from re_rl.tasks.math.logic.lock_log.task import lock_trace
from re_rl.tasks.math.logic.path_toll.task import toll_trace
from re_rl.tasks.math.logic.backoff_wait.task import backoff_trace
from re_rl.tasks.math.logic.priority_run.task import priority_order
from re_rl.tasks.math.logic.inbox_take.task import inbox_trace
from re_rl.tasks.math.logic.goal_match.task import goal_trace
from re_rl.tasks.math.logic.craft_need.task import craft_trace
from re_rl.tasks.math.logic.checkpoint_roll.task import checkpoint_trace
from re_rl.tasks.math.logic.schema_check.task import schema_trace
from re_rl.tasks.math.algebra.infix_value.task import eval_infix
from re_rl.tasks.math.discrete.ballot_walk.task import ballot_trace
from re_rl.tasks.math.discrete.digit_root.task import digit_trace
from re_rl.tasks.math.discrete.crt_lift.task import crt_search
from re_rl.tasks.math.discrete.mod_order.task import order_trace
from re_rl.tasks.math.logic.first_repeat.task import repeat_trace
from re_rl.tasks.math.logic.coupon_cover.task import coupon_trace
from re_rl.tasks.math.logic.coin_weigh.task import weigh_trace
from re_rl.tasks.math.logic.two_color.task import color_trace
from re_rl.tasks.math.discrete.lattice_sum.task import lattice_trace
from re_rl.tasks.ml.roc_walk.task import roc_trace
from re_rl.tasks.ml.ema_loss.task import ema_trace
from re_rl.tasks.ml.lr_decay.task import lr_trace
from re_rl.tasks.ml.batch_grad.task import batch_trace
from re_rl.tasks.ml.best_margin.task import margin_trace
from re_rl.tasks.rl.online_base.task import base_trace
from re_rl.tasks.rl.td_clip.task import td_clip_trace
from re_rl.tasks.rl.count_bonus.task import bonus_trace
from re_rl.tasks.rl.option_hold.task import hold_trace
from re_rl.tasks.rl.policy_eval.task import eval_sweeps
from re_rl.tasks.math.algebra.horner_mod.task import horner_plain, horner_trace
from re_rl.tasks.math.algebra.rational_root.task import horner_value, root_trace
from re_rl.tasks.math.analysis.geom_sum.task import geom_closed, geom_trace
from re_rl.tasks.math.discrete.cyclo_eval.task import cyclo_coeffs, cyclo_trace
from re_rl.tasks.math.discrete.chebyshev_row.task import chebyshev_trace
from re_rl.tasks.math.discrete.hermite_row.task import hermite_trace
from re_rl.tasks.math.discrete.series_conv.task import conv_full
from re_rl.tasks.math.probability.transport_cost.task import transport_trace
from re_rl.tasks.math.discrete.pochhammer.task import poch_trace
from re_rl.tasks.math.discrete.binom_build.task import binom_trace
from re_rl.tasks.math.discrete.farey_next.task import farey_trace
from re_rl.tasks.math.discrete.mobius_sum.task import mobius, mobius_trace
from re_rl.tasks.math.discrete.involution_count.task import involution_trace
from re_rl.tasks.math.discrete.jacobi_row.task import jacobi, jacobi_trace
from re_rl.tasks.math.discrete.ruler_sum.task import ruler_trace, valuation
from re_rl.tasks.math.discrete.thue_count.task import thue_trace
from re_rl.tasks.math.discrete.aliquot_walk.task import aliquot_trace, divisor_sum
from re_rl.tasks.math.discrete.carmichael_row.task import carmichael, carmichael_trace
from re_rl.tasks.math.discrete.cayley_trees.task import cayley_trace
from re_rl.tasks.math.discrete.factoradic.task import factoradic_trace
from re_rl.tasks.math.discrete.stirling_first.task import stirling_rows
from re_rl.tasks.math.discrete.bell_row.task import bell_trace
from re_rl.tasks.math.discrete.andre_row.task import andre_rows
from re_rl.tasks.math.discrete.bernoulli_den.task import bernoulli_den_trace
from re_rl.tasks.math.discrete.chebyshev_u.task import chebyshev_u_trace
from re_rl.tasks.math.discrete.sigma_row.task import sigma, sigma_trace
from re_rl.tasks.math.discrete.prime_omega.task import omega_trace, prime_omega
from re_rl.tasks.math.discrete.motzkin_row.task import motzkin_trace
from re_rl.tasks.math.discrete.primorial.task import primorial_trace
from re_rl.tasks.math.discrete.rgs_rank.task import growth_table, rank_parts
from re_rl.tasks.math.discrete.bernoulli_numer.task import bernoulli_trace
from re_rl.tasks.math.discrete.genocchi_row.task import genocchi_value
from re_rl.tasks.math.discrete.kronecker_row.task import kronecker, kronecker_trace
from re_rl.tasks.math.discrete.hook_length.task import hook_trace
from re_rl.tasks.math.discrete.legendre_frac.task import legendre_trace
from re_rl.tasks.math.discrete.laguerre_frac.task import laguerre_trace
from re_rl.tasks.math.discrete.harmonic_frac.task import harmonic_trace
from re_rl.tasks.math.discrete.eulerian_row.task import eulerian_rows
from re_rl.tasks.math.discrete.fubini_row.task import fubini_trace
from re_rl.tasks.math.discrete.delannoy_row.task import delannoy_recur, delannoy_trace
from re_rl.tasks.math.discrete.tau_row.task import tau, tau_trace
from re_rl.tasks.math.discrete.prime_nu.task import nu_trace, prime_nu
from re_rl.tasks.math.discrete.sopfr_row.task import sopfr, sopfr_trace
from re_rl.tasks.math.discrete.pell_row.task import pell_trace
from re_rl.tasks.math.discrete.tribonacci_row.task import tribonacci_trace
from re_rl.tasks.math.discrete.narayana_row.task import narayana_trace
from re_rl.tasks.math.discrete.schroder_row.task import schroder_trace
from re_rl.tasks.math.discrete.gaussian_bin.task import gauss_product, gauss_rows
from re_rl.tasks.math.discrete.kolakoski.task import kolakoski_full, run_lengths
from re_rl.tasks.math.discrete.cantor_pair.task import cantor_fold, cantor_pair, cantor_unpair
from re_rl.tasks.math.logic.horn_fire.task import horn_trace
from re_rl.tasks.math.logic.carry_row.task import carry_trace
from re_rl.tasks.math.logic.lamp_trio.task import lamp_trace
from re_rl.tasks.math.logic.parity_sheet.task import parity_trace
from re_rl.tasks.math.logic.mux_index.task import mux_trace
from re_rl.tasks.math.logic.jury_veto.task import jury_trace
from re_rl.tasks.math.logic.gate_fold.task import gate_trace
from re_rl.tasks.math.logic.exactly_one.task import exact_trace
from re_rl.tasks.math.logic.knave_next.task import knave_trace
from re_rl.tasks.math.logic.priority_bit.task import priority_trace
from re_rl.tasks.math.logic.interval_merge.task import merge_trace as interval_trace
from re_rl.tasks.math.logic.cycle_count.task import cycle_trace
from re_rl.tasks.math.logic.stack_perm.task import stack_trace
from re_rl.tasks.math.logic.inversion_row.task import inversion_trace
from re_rl.tasks.math.logic.run_length.task import run_trace
from re_rl.tasks.math.logic.median_merge.task import merge_trace as list_merge
from re_rl.tasks.math.geometry.diag_cross.task import diag_quads
from re_rl.tasks.math.geometry.billiard_cross.task import billiard_trace as cross_trace
from re_rl.tasks.math.discrete.popcount_sum.task import pop_trace
from re_rl.tasks.math.discrete.rencontres_row.task import rencontres_row
from re_rl.tasks.math.discrete.ballot_tri.task import ballot_rows
from re_rl.tasks.math.discrete.dedekind_psi.task import dedekind_psi, psi_trace
from re_rl.tasks.math.discrete.jordan_tot.task import jordan_two
from re_rl.tasks.math.discrete.sylvester_row.task import sylvester_trace
from re_rl.tasks.math.discrete.lucas_row.task import lucas_trace
from re_rl.tasks.math.discrete.liouville_row.task import liouville, liouville_trace
from re_rl.tasks.math.discrete.necklace_count.task import necklace_trace
from re_rl.tasks.math.discrete.hamming_smooth.task import hamming_trace
from re_rl.tasks.math.discrete.menage_count.task import menage_trace
from re_rl.tasks.math.logic.bracket_final.task import bracket_trace
from re_rl.tasks.math.logic.unit_prop.task import unit_trace
from re_rl.tasks.math.logic.gf2_solve.task import gf2_trace
from re_rl.tasks.math.logic.resolve_proof.task import resolution_trace, resolve
from re_rl.tasks.math.logic.bool_eq.task import eq_trace
from re_rl.tasks.math.logic.assign_check.task import check_trace
from re_rl.tasks.math.logic.pigeon_place.task import pigeon_trace
from re_rl.tasks.math.logic.kripke_box.task import box_trace
from re_rl.tasks.math.logic.all_are.task import all_trace
from re_rl.tasks.math.logic.literal_clash.task import clash_trace
from re_rl.tasks.math.logic.until_line.task import until_trace
from re_rl.tasks.math.logic.dung_ground.task import ground_trace, grounded_labels
from re_rl.tasks.math.logic.causal_do.task import causal_pair, causal_values
from re_rl.tasks.math.logic.lukas_fold.task import lukas_apply, lukas_trace
from re_rl.tasks.math.logic.doctrinal.task import doctrine_result
from re_rl.tasks.math.logic.knows_line.task import knows_trace
from re_rl.tasks.math.logic.rough_set.task import rough_trace
from re_rl.tasks.math.logic.naf_fire.task import naf_trace, reduct_matches
from re_rl.tasks.math.logic.agenda_vote.task import agenda_trace
from re_rl.tasks.ml.ctc_collapse.task import ctc_trace
from re_rl.tasks.ml.relu_chain.task import relu_trace
from re_rl.tasks.ml.causal_pick.task import prefix_choice
from re_rl.tasks.ml.triplet_gap.task import triplet_trace
from re_rl.tasks.ml.beam_keep.task import beam_trace as keep_trace
from re_rl.tasks.rl.hindsight_hit.task import hindsight_trace
from re_rl.tasks.rl.legal_greedy.task import legal_trace
from re_rl.tasks.rl.reward_machine.task import machine_trace
from re_rl.tasks.rl.episode_cut.task import cut_trace
from re_rl.tasks.rl.best_reply.task import reply_trace
from re_rl.tasks.ml.draft_accept.task import draft_trace
from re_rl.tasks.ml.class_margin.task import score_gap
from re_rl.tasks.ml.bin_tally.task import bin_trace
from re_rl.tasks.ml.grad_accum.task import accum_trace
from re_rl.tasks.ml.skip_add.task import skip_trace
from re_rl.tasks.rl.arm_rate.task import arm_trace
from re_rl.tasks.rl.budget_step.task import budget_trace
from re_rl.tasks.rl.done_boot.task import boot_trace
from re_rl.tasks.rl.greedy_gap.task import gap_trace
from re_rl.tasks.rl.switch_cost.task import switch_trace
from re_rl.tasks.math.logic.short_circuit.task import short_trace
from re_rl.tasks.math.logic.ref_count.task import ref_trace
from re_rl.tasks.math.logic.wrap_index.task import wrap_trace
from re_rl.tasks.math.logic.bit_prog.task import bit_trace
from re_rl.tasks.math.logic.break_sum.task import break_trace
from re_rl.tasks.math.logic.bounds_step.task import bounds_trace
from re_rl.tasks.math.logic.reg_swap.task import reg_trace
from re_rl.tasks.math.logic.elif_pick.task import elif_trace
from re_rl.tasks.math.logic.post_inc.task import post_trace
from re_rl.tasks.math.logic.min_hold.task import stack_min
from re_rl.tasks.math.logic.jump_add.task import jump_trace
from re_rl.tasks.math.logic.div_chain.task import div_trace
from re_rl.tasks.math.logic.clamp_add.task import clamp_trace
from re_rl.tasks.math.logic.ptr_walk.task import ptr_trace
from re_rl.tasks.math.logic.continue_sum.task import cont_trace
from re_rl.tasks.math.logic.delay_line.task import delay_trace
from re_rl.tasks.math.logic.switch_case.task import case_trace
from re_rl.tasks.math.logic.digit_scan.task import scan_trace
from re_rl.tasks.math.logic.rot_nibble.task import rot_trace
from re_rl.tasks.math.logic.buf_len.task import buf_trace
from re_rl.tasks.math.logic.cmp_branch.task import cmp_trace
from re_rl.tasks.math.logic.bit_set.task import bitset_trace
from re_rl.tasks.math.logic.cell_write.task import write_trace
from re_rl.tasks.math.logic.lcg_step.task import lcg_trace
from re_rl.tasks.math.logic.two_stack.task import queue_trace
from re_rl.tasks.math.logic.sorted_insert.task import rank_trace
from re_rl.tasks.math.logic.brace_pair.task import brace_trace
from re_rl.tasks.math.logic.hash_probe.task import probe_trace
from re_rl.tasks.math.logic.part_count.task import part_trace
from re_rl.tasks.math.logic.fill_forward.task import fill_trace
from re_rl.tasks.math.logic.xor_fold.task import xor_trace
from re_rl.tasks.math.logic.bubble_pass.task import bubble_trace
from re_rl.tasks.math.logic.mtf_list.task import mtf_trace
from re_rl.tasks.math.logic.turnstile.task import stile_trace
from re_rl.tasks.math.logic.hamming_step.task import ham_trace
from re_rl.tasks.math.logic.row_major.task import index_trace
from re_rl.tasks.math.logic.union_count.task import link_trace
from re_rl.tasks.math.logic.trie_node.task import trie_trace
from re_rl.tasks.math.logic.minute_add.task import minute_trace
from re_rl.tasks.math.logic.mod_accum.task import mod_ops
from re_rl.tasks.math.logic.nfa_run.task import nfa_trace
from re_rl.tasks.math.logic.moore_run.task import moore_trace
from re_rl.tasks.math.logic.sync_run.task import image_trace
from re_rl.tasks.math.logic.meet_run.task import meet_trace
from re_rl.tasks.math.logic.lfsr_run.task import lfsr_trace
from re_rl.tasks.math.logic.crc_rem.task import crc_trace
from re_rl.tasks.math.logic.feistel_run.task import feistel_trace
from re_rl.tasks.math.logic.elgamal_enc.task import elgamal_trace
from re_rl.tasks.ml.neighbor_vote.task import nearest_votes
from re_rl.tasks.rl.trace_decay.task import decay_visits
from re_rl.tasks.ml.boost_weights.task import double_weights
from re_rl.tasks.ml.momentum_sgd.task import momentum_steps
from re_rl.tasks.ml.decision_list.task import first_match
from re_rl.tasks.rl.td_table.task import td_updates
from re_rl.tasks.registry import registry

CYRILLIC = re.compile(r"[А-Яа-яЁё]")

POOL = [
    "gear_train",
    "relay_time",
    "voltage_divider",
    "crew_work",
    "mix_chain",
    "mod_chain",
    "spring_series",
    "lens_stack",
    "block_stack",
    "sticking_chain",
    "gcd_chain",
    "recurrence_walk",
    "turtle_walk",
    "horner_eval",
    "ledger_guard",
    "door_toggles",
    "truck_trips",
    "portal_walk",
    "cascade_tanks",
    "greedy_coins",
    "walk_range",
    "line_infection",
    "corridor_keys",
    "carry_add",
    "next_greater",
    "window_max",
    "two_pointer_merge",
    "cooldown_schedule",
    "pancake_trace",
    "bracket_scan",
    "kmeans_rounds",
    "bayes_updates",
    "polya_urn",
    "policy_rollout",
    "extended_euclid",
    "crt_chain",
    "cf_expand",
    "nim_sum",
    "difference_table",
    "network_reduce",
    "decay_generations",
    "bounce_heights",
    "charge_redistribute",
    "sandpile_path",
    "boost_chain",
    "markov_steps",
    "sir_ticks",
    "poly_div",
    "johnson_span",
    "lights_path",
    "weighing_trace",
    "switch_net",
    "domino_chain",
    "bound_scan",
    "billiard_box",
    "mobile_torque",
    "traffic_light",
    "drop_cross",
    "claim_count",
    "quorum_rise",
    "ternary_balance",
    "siding_counter",
    "hat_line",
    "reagent_chain",
    "tax_brackets",
    "codon_scan",
    "dose_schedule",
    "melody_walk",
    "boost_weights",
    "momentum_sgd",
    "decision_list",
    "td_table",
    "fifo_cost",
    "borda_count",
    "shift_add",
    "rally_lead",
    "pascal_row",
    "fraction_ops",
    "neighbor_vote",
    "trace_decay",
    "motion_segments",
    "slope_run",
    "echo_bounce",
    "stern_path",
    "partition_count",
    "derange_count",
    "gauss_mul",
    "perm_compose",
    "cover_span",
    "reverse_add",
    "stream_median",
    "totient_row",
    "coprime_count",
    "digit_div",
    "tree_depth",
    "sign_walk",
    "perm_rank",
    "lcm_rise",
    "zigzag_row",
    "record_highs",
    "sum_kinds",
    "fib_word",
    "mode_track",
    "fall_ticks",
    "friction_slide",
    "heat_mix",
    "heat_rod",
    "wave_row",
    "leak_charge",
    "resistor_ladder",
    "doppler_chain",
    "float_load",
    "melt_heat",
    "throw_ticks",
    "impulse_run",
    "beam_load",
    "mass_shift",
    "spring_join",
    "optic_path",
    "pulse_meet",
    "cool_ticks",
    "series_cap",
    "column_pressure",
    "cradle_hit",
    "photon_eject",
    "orbit_years",
    "grating_order",
    "wire_force",
    "escape_speed",
    "harmonic_nodes",
    "snell_shift",
    "heat_steps",
    "hydraulic_lift",
    "look_say",
    "zeckendorf",
    "roman_value",
    "digit_stream",
    "deque_trace",
    "dragon_fold",
    "permanent",
    "bead_count",
    "negabase",
    "ulam_walk",
    "luhn_sum",
    "kaprekar_step",
    "morton_code",
    "stock_span",
    "candy_row",
    "digit_fact",
    "recaman",
    "xor_basis",
    "palindrome_radius",
    "squarefree_row",
    "fenwick_sum",
    "sparse_min",
    "z_array",
    "selection_swaps",
    "rho_cycle",
    "tree_times",
    "dutch_flag",
    "window_distinct",
    "stable_place",
    "naive_find",
    "budget_take",
    "skip_op",
    "retry_goal",
    "signal_edges",
    "plan_gate",
    "tool_pick",
    "diff_count",
    "cell_patch",
    "pred_scan",
    "rate_limit",
    "lateness",
    "switch_flip",
    "turn_signs",
    "first_fit",
    "plurality",
    "floor_run",
    "saturate_count",
    "undo_reg",
    "cover_point",
    "next_fit",
    "sgd_online",
    "actor_critic",
    "ucb_bandit",
    "grad_clip",
    "weight_decay",
    "early_stop",
    "prototype_mean",
    "target_sync",
    "replay_fifo",
    "shape_reward",
    "eps_schedule",
    "scope_lookup",
    "lock_log",
    "path_toll",
    "backoff_wait",
    "priority_run",
    "inbox_take",
    "goal_match",
    "craft_need",
    "checkpoint_roll",
    "schema_check",
    "infix_value",
    "ballot_walk",
    "digit_root",
    "crt_lift",
    "mod_order",
    "first_repeat",
    "coupon_cover",
    "coin_weigh",
    "two_color",
    "lattice_sum",
    "roc_walk",
    "ema_loss",
    "lr_decay",
    "batch_grad",
    "best_margin",
    "online_base",
    "td_clip",
    "count_bonus",
    "option_hold",
    "policy_eval",
    "horner_mod",
    "rational_root",
    "geom_sum",
    "cyclo_eval",
    "chebyshev_row",
    "hermite_row",
    "series_conv",
    "transport_cost",
    "pochhammer",
    "binom_build",
    "farey_next",
    "mobius_sum",
    "involution_count",
    "jacobi_row",
    "ruler_sum",
    "thue_count",
    "aliquot_walk",
    "carmichael_row",
    "cayley_trees",
    "factoradic",
    "stirling_first",
    "bell_row",
    "andre_row",
    "bernoulli_den",
    "chebyshev_u",
    "sigma_row",
    "prime_omega",
    "motzkin_row",
    "primorial",
    "rgs_rank",
    "bernoulli_numer",
    "genocchi_row",
    "kronecker_row",
    "hook_length",
    "legendre_frac",
    "laguerre_frac",
    "harmonic_frac",
    "eulerian_row",
    "fubini_row",
    "delannoy_row",
    "tau_row",
    "prime_nu",
    "sopfr_row",
    "pell_row",
    "tribonacci_row",
    "narayana_row",
    "schroder_row",
    "gaussian_bin",
    "kolakoski",
    "cantor_pair",
    "horn_fire",
    "carry_row",
    "lamp_trio",
    "parity_sheet",
    "mux_index",
    "jury_veto",
    "gate_fold",
    "exactly_one",
    "knave_next",
    "priority_bit",
    "interval_merge",
    "cycle_count",
    "stack_perm",
    "inversion_row",
    "run_length",
    "median_merge",
    "diag_cross",
    "billiard_cross",
    "popcount_sum",
    "rencontres_row",
    "ballot_tri",
    "dedekind_psi",
    "jordan_tot",
    "sylvester_row",
    "lucas_row",
    "liouville_row",
    "necklace_count",
    "hamming_smooth",
    "menage_count",
    "bracket_final",
    "unit_prop",
    "gf2_solve",
    "resolve_proof",
    "bool_eq",
    "assign_check",
    "pigeon_place",
    "kripke_box",
    "all_are",
    "literal_clash",
    "until_line",
    "dung_ground",
    "causal_do",
    "lukas_fold",
    "doctrinal",
    "knows_line",
    "rough_set",
    "naf_fire",
    "agenda_vote",
    "ctc_collapse",
    "relu_chain",
    "causal_pick",
    "triplet_gap",
    "beam_keep",
    "hindsight_hit",
    "legal_greedy",
    "reward_machine",
    "episode_cut",
    "best_reply",
    "draft_accept",
    "class_margin",
    "bin_tally",
    "grad_accum",
    "skip_add",
    "arm_rate",
    "budget_step",
    "done_boot",
    "greedy_gap",
    "switch_cost",
    "short_circuit",
    "ref_count",
    "wrap_index",
    "bit_prog",
    "break_sum",
    "bounds_step",
    "reg_swap",
    "elif_pick",
    "post_inc",
    "min_hold",
    "jump_add",
    "div_chain",
    "clamp_add",
    "ptr_walk",
    "continue_sum",
    "delay_line",
    "switch_case",
    "digit_scan",
    "rot_nibble",
    "buf_len",
    "cmp_branch",
    "bit_set",
    "cell_write",
    "lcg_step",
    "two_stack",
    "sorted_insert",
    "brace_pair",
    "hash_probe",
    "part_count",
    "fill_forward",
    "xor_fold",
    "bubble_pass",
    "mtf_list",
    "turnstile",
    "hamming_step",
    "row_major",
    "union_count",
    "trie_node",
    "minute_add",
    "mod_accum",
    "nfa_run",
    "moore_run",
    "sync_run",
    "meet_run",
    "lfsr_run",
    "crc_rem",
    "feistel_run",
    "elgamal_enc",
]


def _one(task_type, language, difficulty, subtype=None, seed=0):
    random.seed(seed)
    kwargs = {"language": language, "difficulty": difficulty}
    if subtype is not None:
        kwargs["task_type"] = subtype
    return ALL_TASK_GENERATORS[task_type](**kwargs)


@pytest.mark.parametrize("task_type", POOL)
def test_registered(task_type):
    assert task_type in registry
    assert task_type in ALL_TASK_GENERATORS


@pytest.mark.parametrize("task_type", POOL)
@pytest.mark.parametrize("language", ["ru", "en"])
@pytest.mark.parametrize("difficulty", [1, 5, 10])
def test_self_consistent(task_type, language, difficulty):
    for subtype in registry[task_type].TASK_TYPES:
        for seed in range(3):
            task = _one(task_type, language, difficulty, subtype, seed + difficulty)
            blob = task.description + "\n" + "\n".join(task.solution_steps)
            assert task.final_answer is not None
            assert "{" not in blob
            assert len(task.solution_steps) >= task.n
            assert task.verify(f"<answer>{task.final_answer}</answer>") == pytest.approx(1.0)
            if language == "en":
                assert not CYRILLIC.search(blob)
            else:
                assert CYRILLIC.search(task.description)


@pytest.mark.parametrize("task_type", POOL)
def test_size_grows_with_difficulty(task_type):
    low = _one(task_type, "ru", 1, seed=1)
    high = _one(task_type, "ru", 10, seed=1)
    assert high.n > low.n
    assert len(high.solution_steps) > len(low.solution_steps)


def test_chain_values():
    random.seed(4)
    gear = _one("gear_train", "en", 6, seed=4)
    product = gear.teeth[0] * gear.speeds[0]
    assert all(teeth * speed == product for teeth, speed in zip(gear.teeth, gear.speeds))
    assert gear.answer == gear.speeds[-1]

    relay = _one("relay_time", "en", 7, seed=4)
    assert relay.total == sum(leg["distance"] // leg["speed"] for leg in relay.legs)

    divider = _one("voltage_divider", "en", 8, "part", seed=4)
    assert divider.total_v == divider.current * sum(divider.resistors)
    assert divider.part == divider.current * divider.resistors[divider.k - 1]

    crew = _one("crew_work", "en", 5, seed=4)
    assert crew.job == crew.days * sum(crew.rates)

    mix = _one("mix_chain", "en", 9, seed=4)
    current = mix.start
    for step in mix.steps:
        solute = (mix.volume - step["out"]) * step["before"] + step["out"] * step["added"]
        assert solute % mix.volume == 0
        assert step["after"] == solute // mix.volume
        current = step["after"]
    assert mix.answer == current

    chain = _one("mod_chain", "en", 10, seed=4)
    value = chain.start
    for factor, shift, stored in chain.ops:
        value = (value * factor + shift) % chain.mod
        assert stored == value
    assert chain.answer == value

    springs = _one("spring_series", "en", 6, seed=4)
    assert springs.total == sum(springs.force // item for item in springs.stiffness)
    assert all(springs.force % item == 0 for item in springs.stiffness)

    lenses = _one("lens_stack", "en", 5, seed=4)
    assert lenses.total == sum(lenses.powers)
    assert all(item != 0 for item in lenses.powers)

    blocks = _one("block_stack", "en", 7, "moment", seed=4)
    assert blocks.moment == sum(mass * center for mass, center in zip(blocks.masses, blocks.centers))
    assert all(item % 2 == 0 for item in blocks.thickness)

    carts = _one("sticking_chain", "en", 8, "speed", seed=4)
    assert sum(carts.velocities) == carts.n * carts.speed
    assert carts.momentum == carts.mass * sum(carts.velocities)

    gcd_task = _one("gcd_chain", "en", 9, seed=4)
    assert gcd_task.answer == math.gcd(*gcd_task.numbers)

    walk = _one("recurrence_walk", "en", 10, seed=4)
    for index in range(2, len(walk.terms)):
        assert walk.terms[index] == walk.terms[index - 1] + walk.terms[index - 2]
    assert walk.answer == walk.terms[-1]
    assert len(walk.solution_steps) >= walk.n

    turtle = _one("turtle_walk", "en", 6, "manhattan", seed=4)
    assert turtle.manhattan == abs(turtle.x) + abs(turtle.y)
    assert turtle.trace[-1] == (turtle.x, turtle.y)

    horner = _one("horner_eval", "en", 8, seed=4)
    acc = 0
    for coeff in horner.coeffs:
        acc = acc * horner.x + coeff
    assert horner.answer == acc

    ledger = _one("ledger_guard", "en", 7, "rejected", seed=4)
    balance = ledger.start
    rejected = 0
    for op in ledger.ops:
        if op["sign"] > 0:
            balance += op["amount"]
        elif op["amount"] > balance:
            rejected += 1
        else:
            balance -= op["amount"]
        assert op["balance"] == balance
    assert (ledger.balance, ledger.rejected) == (balance, rejected)

    doors = _one("door_toggles", "en", 10, "count", seed=4)
    assert doors.count == math.isqrt(doors.n)
    assert doors.largest == math.isqrt(doors.n) ** 2

    truck = _one("truck_trips", "en", 9, "trips", seed=4)
    trips = 1
    load = 0
    for size in truck.sizes:
        if load + size > truck.capacity:
            trips += 1
            load = 0
        load += size
    assert (truck.trips, truck.leftover) == (trips, load)
    assert load <= truck.capacity

    portal = _one("portal_walk", "en", 10, seed=4)
    room = 0
    for _ in range(portal.n):
        room = portal.nxt[room]
    assert portal.answer == room

    tanks = _one("cascade_tanks", "en", 8, "tank", seed=4)
    left = tanks.pour
    held = []
    for cap in tanks.caps:
        take = min(cap, left)
        held.append(take)
        left -= take
    assert tanks.held == held
    assert tanks.spilled == left
    assert sum(held) + left == tanks.pour

    coins = _one("greedy_coins", "en", 10, "extra", seed=4)
    assert coins.picks == greedy_picks(coins.amount)
    assert coins.optimal == optimal_count(coins.amount)
    assert coins.extra == len(coins.picks) - coins.optimal
    assert coins.extra > 0
    assert coins.n > _one("greedy_coins", "en", 1, seed=4).n

    walk = _one("walk_range", "en", 9, "lowest", seed=4)
    assert walk.final == sum(walk.deltas)
    assert walk.lowest == min([0] + walk.heights)

    infected = _one("line_infection", "en", 7, seed=4)
    state = infected.infected[:]
    for _ in range(infected.n):
        state = spread_once(state)
    assert infected.answer == sum(state)

    keys = _one("corridor_keys", "en", 8, "farthest", seed=4)
    held = set()
    farthest = 0
    for room in range(keys.n):
        if room and keys.need[room] is not None and keys.need[room] not in held:
            break
        held.update(keys.keys_here[room])
        farthest = room
    assert keys.farthest == farthest
    assert keys.keys == len(held)

    addition = _one("carry_add", "en", 10, "carries", seed=4)
    assert addition.sum == addition.a + addition.b
    assert addition.carries == sum(1 for column in addition.columns if column["carry_out"])

    greater = _one("next_greater", "en", 8, "distance_sum", seed=4)
    assert greater.nxt == next_greater(greater.values)
    assert greater.missing == sum(1 for index in greater.nxt if index < 0)

    window = _one("window_max", "en", 10, "total", seed=4)
    maxima = [
        max(window.values[start:start + window.k])
        for start in range(window.length - window.k + 1)
    ]
    assert window.maxima == maxima
    assert window.n == window.length - window.k + 1
    assert window.n > _one("window_max", "en", 1, seed=4).n

    merged = _one("two_pointer_merge", "en", 9, "wins", seed=4)
    assert merged.merged == sorted(merged.left + merged.right)
    assert len(merged.merged) == merged.n

    schedule = _one("cooldown_schedule", "en", 7, "idles", seed=4)
    assert schedule.time == schedule.n + schedule.idles

    pancakes = _one("pancake_trace", "en", 6, "place", seed=4)
    perm = pancakes.start[:]
    for width in pancakes.flips:
        perm[:width] = list(reversed(perm[:width]))
    assert perm == pancakes.perm
    assert pancakes.place == perm.index(1) + 1

    brackets = _one("bracket_scan", "en", 8, "error", seed=4)
    assert len(brackets.expr) == brackets.n
    assert brackets.max_depth >= 0
    assert brackets.error == 0 or 1 <= brackets.error <= brackets.n + 1

    rounds = _one("kmeans_rounds", "en", 6, "center", seed=4)
    assert rounds.rounds == cluster_rounds(rounds.points, rounds.n)
    assert rounds.center == rounds.rounds[-1][0]

    bayes = _one("bayes_updates", "en", 7, "percent", seed=4)
    favor, against = bayes.start, 100 - bayes.start
    for item in bayes.updates:
        num = favor * item["yes"]
        den = against * item["no"]
        assert item["new"] == (100 * num) // (num + den)
        divisor = math.gcd(num, den)
        favor, against = num // divisor, den // divisor
    assert bayes.percent == (100 * favor) // (favor + against)

    urn = _one("polya_urn", "en", 8, "denom", seed=4)
    probability = sequence_probability(urn.red, urn.blue, urn.sequence)
    assert (urn.numer, urn.denom) == (probability.numerator, probability.denominator)

    rollout = _one("policy_rollout", "en", 9, "reward", seed=4)
    position = rollout.start
    total = 0
    for action_state in rollout.trace:
        pos, action, nxt, running = action_state
        assert pos == position
        landed = min(rollout.length - 1, max(0, position + rollout.policy[position]))
        assert nxt == landed
        total += rollout.rewards[nxt]
        assert running == total
        position = nxt
    assert rollout.total == total
    assert rollout.end == position

    bezout = _one("extended_euclid", "en", 8, "x", seed=4)
    assert len(bezout.trace) == bezout.n
    assert bezout.a * bezout.x + bezout.b * bezout.y == bezout.gcd

    system = _one("crt_chain", "en", 7, "value", seed=4)
    assert all(system.value % mod == rem for mod, rem in zip(system.moduli, system.remainders))
    assert 0 <= system.value < system.modulus

    fraction = _one("cf_expand", "en", 6, "numer", seed=4)
    assert fraction.pairs == convergents(fraction.quotients)
    assert math.gcd(fraction.numer, fraction.denom) == 1

    nim = _one("nim_sum", "en", 9, "winning", seed=4)
    total_xor = 0
    for size in nim.heaps:
        total_xor ^= size
    assert nim.nim == total_xor
    assert nim.winning == (1 if total_xor else 0)

    table = _one("difference_table", "en", 10, "next", seed=4)
    assert table.nxt == polynomial_value(table.coeffs, table.n)
    assert table.nxt == extend_table(table.values)
    assert table.delta == table.coeffs[-1]

    network = _one("network_reduce", "en", 8, "equivalent", seed=4)
    assert network.equivalent == equivalent(network.tree)
    assert network.total_leaves == leaf_sum(network.tree)
    assert network.equivalent <= network.total_leaves

    decay = _one("decay_generations", "en", 6, "stable", seed=4)
    counts = [decay.seed_count * 2 ** decay.n] + [0] * (decay.species - 1)
    for _ in range(decay.n):
        counts = decay_tick(counts)
    assert decay.counts == counts
    assert sum(counts) == decay.seed_count * 2 ** decay.n
    assert counts[0] == decay.seed_count

    bounce = _one("bounce_heights", "en", 10, "at_k", seed=4)
    assert bounce.heights[0] == bounce.start // 2
    assert bounce.final == bounce.unit
    assert bounce.at_k == bounce.start // 2 ** bounce.k

    charge = _one("charge_redistribute", "en", 8, "numer", seed=4)
    shared = share_sequence(charge.charges, charge.links)
    assert shared[charge.k - 1] == charge.chosen
    assert charge.numer == charge.chosen.numerator

    pile = _one("sandpile_path", "en", 7, "remaining", seed=4)
    heights, topples, lost, _trace = stabilize(pile.n, pile.chips, pile.cell)
    assert pile.topples == topples
    assert pile.remaining == sum(heights)
    assert pile.remaining + lost == pile.chips

    boost = _one("boost_chain", "en", 6, "denom", seed=4)
    speeds = add_boosts(boost.boosts)
    assert speeds[-1] == boost.final_speed
    assert boost.denom == boost.final_speed.denominator

    chain = _one("markov_steps", "en", 8, "state2", seed=4)
    weights = markov_weights(chain.rows, chain.n)
    assert weights[-1][chain.target] == chain.answer
    assert sum(weights[-1]) == 2 ** chain.n

    epidemic = _one("sir_ticks", "en", 6, "recovered", seed=4)
    states = sir_run(epidemic.healthy, epidemic.sick, epidemic.n)
    assert states[-1][2] == epidemic.final_recovered
    assert sum(states[-1]) == epidemic.healthy + epidemic.sick

    division = _one("poly_div", "en", 6, "remainder", seed=4)
    quotient, remainder = poly_divmod(division.dividend, division.divisor)
    assert quotient == division.quotient
    rebuilt = poly_mul(quotient, division.divisor)
    rebuilt[-2] += remainder[0]
    rebuilt[-1] += remainder[1]
    assert rebuilt == division.dividend

    schedule = _one("johnson_span", "en", 8, "idle", seed=4)
    order = johnson_order(schedule.machine_a, schedule.machine_b)
    span, _slots = completion(order, schedule.machine_a, schedule.machine_b)
    assert span == schedule.makespan
    assert schedule.idle == span - sum(schedule.machine_b)
    assert schedule.idle > 0

    lamps = _one("lights_path", "en", 10, "presses", seed=4)
    assert apply_presses(lamps.presses) == lamps.lights
    recovered, _states = chase_presses(lamps.lights)
    assert recovered == lamps.presses
    assert sum(recovered) == lamps.press_count

    scale = _one("weighing_trace", "en", 8, "heavy", seed=4)
    weighed = [coin for coin, _outcome in scale.records]
    downs = [coin for coin, outcome in scale.records if outcome == "down"]
    assert len(weighed) == scale.n
    assert len(set(scale.coins) - set(weighed)) == 1
    if downs:
        assert downs == [scale.heavy]
        assert scale.tipped == weighed.index(scale.heavy) + 1
    else:
        assert scale.heavy not in weighed
        assert scale.tipped == 0
    found, tipped, _sets = follow_weighings(scale.coins, scale.records)
    assert found == scale.heavy and tipped == scale.tipped and len(_sets[-1]) == 1

    switches = _one("switch_net", "en", 8, "flip", seed=4)
    assert evaluate(switches.tree) == switches.conducts
    assert evaluate(flip_leaf(switches.tree, switches.k)) == switches.flipped_value
    assert switches.changes == int(switches.flipped_value != switches.conducts)

    dominoes = _one("domino_chain", "en", 10, "break", seed=4)
    break_at, matched = first_break(dominoes.dominoes)
    assert break_at == dominoes.break_at
    assert matched == dominoes.matched

    bounds = _one("bound_scan", "en", 8, "tight", seed=4)
    end_lo, end_hi, tight, _history = scan_bounds(bounds.lo, bounds.hi, bounds.constraints)
    assert end_lo == end_hi == bounds.value
    assert tight == bounds.tight

    table = _one("billiard_box", "en", 8, "height", seed=4)
    trace, corner = billiard_trace(table.width, table.height)
    assert trace == table.trace
    assert len(trace) == table.n
    assert corner[0] in (0, table.width) and corner[1] in (0, table.height)
    assert table.mark == trace[table.k - 1][2]

    mobile = _one("mobile_torque", "en", 7, "hidden", seed=4)
    assert rod_balanced(mobile.root)
    assert mobile.load == sum(leaf["mass"] for leaf in mobile.leaves)
    parent = next(
        rod for rod in mobile.rods
        if (rod["left"]["kind"] == "leaf" and rod["left"]["id"] == mobile.k)
        or (rod["right"]["kind"] == "leaf" and rod["right"]["id"] == mobile.k)
    )
    if parent["left"]["kind"] == "leaf" and parent["left"]["id"] == mobile.k:
        expect = parent["arm_r"] * parent["right"]["mass"] // parent["arm_l"]
    else:
        expect = parent["arm_l"] * parent["left"]["mass"] // parent["arm_r"]
    assert expect == mobile.hidden_mass

    light = _one("traffic_light", "en", 8, "at_k", seed=4)
    times = departure_times(light.n, light.green, light.red)
    assert times == light.times
    cycle = light.green + light.red
    assert all((tick - 1) % cycle < light.green for tick in times)
    assert light.at_k == times[light.k - 1]

    drops = _one("drop_cross", "en", 9, "cross", seed=4)
    sums = running_sums(drops.sizes)
    assert first_cross(sums, drops.threshold) == drops.cross
    assert sums[drops.cross - 1] >= drops.threshold
    if drops.cross > 1:
        assert sums[drops.cross - 2] < drops.threshold
    assert drops.excess == sums[-1] - drops.threshold

    claims = _one("claim_count", "en", 8, "knight", seed=4)
    assert consistent_counts(claims.claims) == [claims.count]
    assert claims.is_knight == (1 if claims.claims[claims.k - 1] == claims.count else 0)

    meeting = _one("quorum_rise", "en", 8, "before", seed=4)
    passed, quorum, trace = play_votes(meeting.votes, meeting.start)
    assert passed == meeting.passed
    assert quorum == meeting.start + meeting.passed
    assert trace[meeting.k - 1][0] == meeting.before

    scale = _one("ternary_balance", "en", 8, "right", seed=4)
    digits = place_weights(scale.target, scale.n)
    assert digits == scale.digits
    assert sum(digit * weight for digit, weight in zip(digits, scale.weights)) == scale.target
    assert scale.right == sum(weight for digit, weight in zip(digits, scale.weights) if digit == 1)
    assert scale.used == sum(1 for digit in digits if digit)

    yard = _one("siding_counter", "en", 10, "bit", seed=4)
    state, _flips, exits = run_sidings(yard.n)
    assert state == yard.state
    assert state == [((yard.n >> index) & 1) for index in range(yard.width)]
    assert exits[0] == 1

    hats = _one("hat_line", "en", 8, "saved", seed=4)
    assert rear_parity(hats.hats) == hats.parity
    assert saved_count(hats.hats) == hats.saved
    assert hats.saved == hats.n if hats.hats[-1] == hats.parity else hats.saved == hats.n - 1

    flask = _one("reagent_chain", "en", 8, "product", seed=4)
    trace = react(flask.start_a, flask.start_b, flask.recipes)
    assert trace == flask.trace
    assert trace[-1][3] == flask.product
    assert trace[-1][1] == flask.left_a
    assert trace[-1][1] >= 0 and trace[-1][2] >= 0

    duty = _one("tax_brackets", "en", 8, "band", seed=4)
    tax, band, parts = apply_tax(duty.income, duty.brackets)
    assert tax == duty.tax and band == duty.band
    assert sum(piece for piece, _part, _tax, _left in parts) == duty.income
    assert all(piece * rate % 100 == 0 for (piece, _part, _tax, _left), (_width, rate) in zip(parts, duty.brackets))

    genes = _one("codon_scan", "en", 10, "first", seed=4)
    stops, first, _trace = scan_codons(genes.codons)
    assert stops == genes.stops and first == genes.first
    assert stops == sum(codon in STOPS for codon in genes.codons)

    doses = _one("dose_schedule", "en", 8, "peak", seed=4)
    levels, peak = concentration_trace(doses.doses)
    assert levels == doses.levels
    assert peak == max(levels)
    assert doses.level == levels[-1]

    tune = _one("melody_walk", "en", 10, "peak", seed=4)
    pitches, peak = walk_melody(tune.start, tune.intervals)
    assert pitches == tune.pitches
    assert peak == max([tune.start, *pitches])
    assert tune.final_pitch == tune.start + sum(tune.intervals)

    stock = _one("fifo_cost", "en", 8, "cogs", seed=4)
    cogs, value, _trace = fifo_account(stock.events)
    assert cogs == stock.cogs and value == stock.value
    assert cogs > 0
    bought = sum(qty for kind, qty, _cost in stock.events if kind == "buy")
    sold = sum(qty for kind, qty, _cost in stock.events if kind == "sell")
    assert bought >= sold

    ballots = _one("borda_count", "en", 8, "winner", seed=4)
    history = borda_scores(ballots.rankings, ballots.candidates)
    assert history[-1] == ballots.scores
    assert ballots.winner == borda_winner(ballots.scores)
    assert ballots.score == ballots.scores[ballots.k - 1]

    product = _one("shift_add", "en", 8, "product", seed=4)
    acc, adds, _totals = shift_add(product.value, product.bits)
    assert acc == product.product == product.value * product.multiplier
    assert adds == product.adds == sum(product.bits)

    rally = _one("rally_lead", "en", 10, "swings", seed=4)
    leader, swings, history = rally_trace(rally.points)
    assert leader == rally.leader and swings == rally.swings
    assert history[-1][0] == rally.points.count(1)
    assert history[-1][1] == rally.points.count(2)

    triangle = _one("pascal_row", "en", 10, "entry", seed=4)
    rows = pascal_rows(triangle.n)
    assert rows[triangle.n][triangle.k - 1] == triangle.entry
    assert rows[triangle.n][triangle.n // 2] == triangle.middle
    assert sum(rows[triangle.n]) == 2 ** triangle.n

    fractions = _one("fraction_ops", "en", 8, "numer", seed=4)
    history = apply_fraction_ops(fractions.start, fractions.ops)
    assert history[-1] == fractions.final
    assert fractions.numer == fractions.final.numerator
    assert fractions.denom == fractions.final.denominator

    votes = _one("neighbor_vote", "en", 9, "label", seed=4)
    chosen, label, flips, _history = nearest_votes(votes.points, votes.query, votes.n)
    assert chosen == votes.chosen
    assert label == votes.label and flips == votes.flips
    assert len({abs(x - votes.query) for x, _label in votes.points}) == len(votes.points)

    decay = _one("trace_decay", "en", 8, "cell", seed=4)
    history = decay_visits(decay.states, decay.visits)
    assert history[-1] == decay.values
    assert decay.cell == history[-1][decay.k - 1]
    assert decay.mass == sum(history[-1])

    boost = _one("boost_weights", "en", 8, "weight", seed=4)
    history = double_weights(boost.labels, boost.rounds)
    assert history == boost.history
    assert boost.weight == history[-1][boost.k - 1]
    assert boost.total == sum(history[-1])

    moment = _one("momentum_sgd", "en", 8, "velocity", seed=4)
    weights, velocities = momentum_steps(moment.start, moment.gradients)
    assert weights == moment.weights
    assert velocities[-1] == moment.velocity
    assert moment.weight == moment.start - sum(velocities)

    rules = _one("decision_list", "en", 8, "fired", seed=4)
    label, fired = first_match(rules.bits, rules.rules, rules.default)
    assert label == rules.label and fired == rules.fired

    table = _one("td_table", "en", 8, "value", seed=4)
    history = td_updates(table.states, table.jumps)
    assert history[-1] == table.values
    assert table.value == history[-1][table.k - 1]
    assert table.total == sum(history[-1])

    motion = _one("motion_segments", "en", 8, "place", seed=4)
    trace = integrate_motion(motion.segments)
    assert trace == motion.trace
    assert motion.place == trace[-1][0]
    assert motion.speed == trace[-1][1]
    replay_x, replay_v = 0, 0
    for accel, duration in motion.segments:
        assert duration % 2 == 0
        replay_x += replay_v * duration + accel * duration * duration // 2
        replay_v += accel * duration
    assert (replay_x, replay_v) == (motion.place, motion.speed)

    slopes = _one("slope_run", "en", 8, "stop", seed=4)
    trace = run_slopes(slopes.segments)
    assert trace == slopes.trace
    assert slopes.speed2 == trace[-1][0]
    assert slopes.stop == trace[-1][1]
    if slopes.stop:
        assert slopes.speed2 == 0
        assert 1 <= slopes.stop <= slopes.n

    echo = _one("echo_bounce", "en", 8, "last", seed=4)
    hits = echo_hits(echo.length, echo.start, echo.direction, echo.n)
    assert hits == echo.hits
    assert echo.last == hits[-1][0]
    assert echo.at_k == hits[echo.k - 1][0]
    assert all(hits[i][0] < hits[i + 1][0] for i in range(len(hits) - 1))
    assert {wall for _, wall in hits} <= {0, echo.length}

    assert stern_walk([1, 1, 0])[-1] == (3, 4)
    stern = _one("stern_path", "en", 8, "numer", seed=4)
    trace = stern_walk(stern.moves)
    assert trace == stern.trace
    assert (stern.numer, stern.denom) == trace[-1]
    assert math.gcd(stern.numer, stern.denom) == 1

    assert partition_ways(5)[-1] == 7
    assert distinct_ways(5)[-1] == 3
    parts = _one("partition_count", "en", 8, "distinct", seed=4)
    assert parts.count_trace == partition_ways(parts.n)
    assert parts.distinct_trace == distinct_ways(parts.n)
    assert parts.distinct == parts.distinct_trace[-1]
    assert parts.count >= parts.distinct >= 1

    assert derange_table(5)[4] == 9
    assert derange_table(5)[5] == 44
    assert binom(5, 2) == 10
    derange = _one("derange_count", "en", 8, "exact", seed=4)
    table = derange_table(derange.n)
    assert table == derange.table
    assert derange.none == table[derange.n]
    assert derange.exact == binom(derange.n, derange.fixed) * table[derange.n - derange.fixed]

    assert multiply_gauss([(1, 1), (1, -1)])[-1] == (2, 0)
    gauss = _one("gauss_mul", "en", 8, "real", seed=4)
    trace = multiply_gauss(gauss.factors)
    assert trace == gauss.trace
    assert (gauss.real, gauss.imag) == trace[-1]
    assert gauss.real != 0 or gauss.imag != 0

    images, signs, inversions = compose_perms([[2, 1, 3], [1, 3, 2]])
    assert images[-1] == [3, 1, 2]
    assert signs[-1] == 0
    perm = _one("perm_compose", "en", 8, "image", seed=4)
    images, signs, inversions = compose_perms(perm.perms)
    assert images == perm.images
    assert signs == perm.signs
    assert perm.image == images[-1][perm.k - 1]
    assert perm.sign == signs[-1] == inversion_count(images[-1]) % 2

    assert sweep_cover([(1, 2), (2, 3)]) == (2, 2)
    assert sweep_cover([(1, 4)]) == (3, 1)
    cover = _one("cover_span", "en", 8, "depth", seed=4)
    trace = cover_trace(cover.intervals)
    assert trace == cover.trace
    assert (cover.length, cover.depth) == trace[-1]
    assert cover.length >= 1
    assert 1 <= cover.depth <= cover.n

    assert reverse_add_trace(19, 1) == [110]
    assert is_palindrome(121) == 1
    rev = _one("reverse_add", "en", 8, "value", seed=4)
    trace = reverse_add_trace(rev.start, rev.n)
    assert trace == rev.trace
    assert rev.value == trace[-1]
    assert rev.pal == is_palindrome(rev.value)

    assert median_trace([3, 1, 2]) == ([3, 1, 2], 2)
    med = _one("stream_median", "en", 8, "flips", seed=4)
    medians, flips = median_trace(med.values)
    assert medians == med.medians
    assert med.median == medians[-1]
    assert med.flips == flips
    assert len(med.values) == med.n
    assert med.n % 2 == 1

    phi = totient_values(6)
    assert phi[6] == 2
    assert sum(phi[d] for d in range(1, 7) if 6 % d == 0) == 6
    row = _one("totient_row", "en", 8, "total", seed=4)
    values = totient_values(row.n)
    assert values == row.phi_row
    assert row.phi == values[row.n]
    assert row.total == sum(values[1:])
    assert sum(values[d] for d in range(1, row.n + 1) if row.n % d == 0) == row.n

    assert inclusion_rows(10, [2, 3])[-1][3] == 3
    coprime = _one("coprime_count", "en", 8, "free", seed=4)
    rows = inclusion_rows(coprime.limit, coprime.primes)
    assert rows == coprime.rows
    assert coprime.free == rows[-1][3]
    assert coprime.hit == coprime.limit - coprime.free
    assert coprime.free >= 1

    assert divide_digits([1, 0], 5) == (2, 0, [0, 2])
    division = _one("digit_div", "en", 8, "remainder", seed=4)
    quotient, remainder, quot_digits = divide_digits(division.digits, division.divisor)
    assert (quotient, remainder, quot_digits) == (division.quotient, division.remainder, division.quot_digits)
    assert division.number == division.quotient * division.divisor + division.remainder
    assert 0 <= division.remainder < division.divisor

    assert tree_depths([0, 0, 1, 2]) == [0, 0, 1, 2]
    tree = _one("tree_depth", "en", 8, "total", seed=4)
    depths = tree_depths(tree.parents)
    assert depths == tree.depths
    assert tree.depth == depths[tree.k]
    assert tree.total == sum(depths[1:])
    assert tree.total >= 0

    assert walk_signs([1, 1, -1]) == [(1, 1), (2, 2), (1, 3)]
    walk = _one("sign_walk", "en", 8, "place", seed=4)
    trace = walk_signs(walk.moves)
    assert trace == walk.trace
    assert walk.place == sum(walk.moves)
    assert walk.highs == trace[-1][1]
    assert 0 <= walk.highs <= walk.n

    digits, running = factorial_rank([2, 1, 3])
    assert digits == [1, 0, 0] and running[-1] == 2
    assert factorial_rank([1, 2, 3])[1][-1] == 0
    ranked = _one("perm_rank", "en", 8, "digit", seed=4)
    digits, running = factorial_rank(ranked.perm)
    assert digits == ranked.digits and running == ranked.running
    assert ranked.rank == running[-1]
    assert ranked.digit == digits[ranked.k - 1]
    assert 0 <= ranked.rank < math.factorial(ranked.n)

    assert lcm_trace([2, 4, 6]) == [(2, 1), (4, 2), (12, 3)]
    risen = _one("lcm_rise", "en", 8, "value", seed=4)
    trace = lcm_trace(risen.numbers)
    assert trace == risen.trace
    assert risen.value == trace[-1][0]
    assert risen.rises == trace[-1][1]
    folded = 1
    for value in risen.numbers:
        folded = folded // math.gcd(folded, value) * value
    assert folded == risen.value

    assert entringer_rows(5)[-1][-1] == 16
    assert entringer_rows(6)[-1][-1] == 61
    zigzag = _one("zigzag_row", "en", 8, "entry", seed=4)
    rows = entringer_rows(zigzag.n)
    assert rows == zigzag.rows
    assert zigzag.corner == rows[-1][-1]
    assert zigzag.entry == rows[-1][zigzag.k]
    assert len(rows) == zigzag.n

    assert record_trace([1, 3, 2, 3]) == [(1, 1), (3, 2), (3, 2), (3, 2)]
    records = _one("record_highs", "en", 8, "records", seed=4)
    trace = record_trace(records.values)
    assert trace == records.trace
    assert records.peak == max(records.values)
    assert records.records == trace[-1][1]
    assert 1 <= records.records <= records.n

    counts, history = subset_growth([1, 1])
    assert counts == [2, 3] and history[-1] == {0, 1, 2}
    kinds = _one("sum_kinds", "en", 8, "hit", seed=4)
    counts, history = subset_growth(kinds.numbers)
    assert counts == kinds.counts
    assert kinds.kinds == counts[-1] >= kinds.n + 1
    assert kinds.hit == int(kinds.target in history[-1])
    assert all(counts[i] > counts[i - 1] for i in range(1, len(counts)))

    assert fib_word_stats(5)[-1] == (8, 3)
    word = _one("fib_word", "en", 8, "ones", seed=4)
    stats = fib_word_stats(word.n)
    assert stats == word.stats
    assert (word.length, word.ones) == stats[-1]
    for index in range(2, len(stats)):
        assert stats[index][0] == stats[index - 1][0] + stats[index - 2][0]
        assert stats[index][1] == stats[index - 1][1] + stats[index - 2][1]

    modes, switches = mode_trace([2, 1, 1])
    assert modes == [(2, 1), (1, 1), (1, 2)] and switches == 1
    tracked = _one("mode_track", "en", 8, "switches", seed=4)
    modes, switches = mode_trace(tracked.values)
    assert modes == tracked.modes
    assert tracked.mode == modes[-1][0]
    assert tracked.switches == switches
    best_count = max(modes[-1][1], max(tracked.values.count(item) for item in tracked.values))
    winners = [item for item in set(tracked.values) if tracked.values.count(item) == best_count]
    assert tracked.mode == min(winners)

    assert fall_trace(0, 3, 3) == [(3, 2), (5, 1), (6, 0)]
    flight = _one("fall_ticks", "en", 8, "height", seed=4)
    trace = fall_trace(flight.height0, flight.speed0, flight.n)
    assert trace == flight.trace
    assert flight.speed == flight.speed0 - flight.n
    assert flight.height == flight.height0 + flight.n * flight.speed0 - flight.n * (flight.n - 1) // 2

    assert slide_trace(5, [2, 2, 2]) == [(5, 3), (8, 1), (9, 0)]
    slide = _one("friction_slide", "en", 8, "place", seed=4)
    trace = slide_trace(slide.speed0, slide.frictions)
    assert trace == slide.trace
    assert slide.place == trace[-1][0]
    assert slide.speed == trace[-1][1]
    assert all(trace[i][1] <= trace[i - 1][1] for i in range(1, len(trace))) or slide.n == 1

    assert mix_temperature(1, 0, [(1, 2)]) == [(1, 1, 2)]
    mixed = _one("heat_mix", "en", 8, "peak", seed=4)
    trace = mix_temperature(mixed.mass0, mixed.temp0, mixed.samples)
    assert trace == mixed.trace
    assert mixed.temp == trace[-1][0]
    assert mixed.peak == max([mixed.temp0, *(item[0] for item in trace)])

    assert heat_ticks([0, 0, 10], 1) == [[0, 5, 10]]
    rod = _one("heat_rod", "en", 8, "cell", seed=4)
    history = heat_ticks(rod.cells, rod.n)
    assert history == rod.history
    assert rod.cell == history[-1][rod.k - 1]
    assert rod.total == sum(history[-1])
    assert all(row[0] == rod.cells[0] and row[-1] == rod.cells[-1] for row in history)

    assert wave_ticks([0, 1, 0], 1) == [[0, -1, 0]]
    wave = _one("wave_row", "en", 8, "energy", seed=4)
    history = wave_ticks(wave.cells, wave.n)
    assert history == wave.history
    assert wave.cell == history[-1][wave.k - 1]
    assert wave.energy == sum(value * value for value in history[-1])
    assert all(row[0] == 0 and row[-1] == 0 for row in history)

    assert leak_trace(10, [2, 2]) == [(5, 5), (3, 7)]
    leaked = _one("leak_charge", "en", 8, "left", seed=4)
    trace = leak_trace(leaked.charge0, leaked.divisors)
    assert trace == leaked.trace
    assert leaked.left + leaked.leaked == leaked.charge0

    assert ladder_trace(4, [(4, 8)]) == [4]
    ladder = _one("resistor_ladder", "en", 8, "equivalent", seed=4)
    trace = ladder_trace(ladder.start, ladder.sections)
    assert trace == ladder.trace
    assert ladder.equivalent == trace[-1] > 0
    assert ladder.peak == max([ladder.start, *trace])

    assert doppler_trace(2, [6], 12) == [(4, 1)]
    doppler = _one("doppler_chain", "en", 8, "final", seed=4)
    trace = doppler_trace(doppler.start, doppler.speeds, doppler.sound)
    assert trace == doppler.trace
    assert doppler.final == trace[-1][0]
    assert doppler.rises == trace[-1][1]
    assert all(doppler.sound > speed >= 0 for speed in doppler.speeds)

    assert load_trace(3, [(5, 2), (1, 4)]) == [(2, 0), (3, 2)]
    loaded = _one("float_load", "en", 8, "level", seed=4)
    trace = load_trace(loaded.limit, loaded.objects)
    assert trace == loaded.trace
    assert loaded.level == trace[-1][0] <= loaded.limit
    assert loaded.full == trace[-1][1]

    assert melt_trace(2, 1, [2]) == [(0, 0, 3)]
    assert melt_trace(0, 2, [4]) == [(2, 0, 2)]
    melted = _one("melt_heat", "en", 8, "ice", seed=4)
    trace = melt_trace(melted.ice0, melted.water0, melted.packets)
    assert trace == melted.trace
    assert melted.temp == trace[-1][0]
    assert melted.ice == trace[-1][1]
    assert melted.ice + melted.water == melted.ice0 + melted.water0

    assert throw_trace(0, 2, 1) == [(-1, 2, 1, 2)]
    thrown = _one("throw_ticks", "en", 8, "land", seed=4)
    trace = throw_trace(thrown.height0, thrown.vx, thrown.n)
    assert trace == thrown.trace
    assert thrown.land == trace[-1][2] and thrown.span == trace[-1][3]

    assert impulse_trace(2, [-1, 2]) == [(-2, -2, -1), (4, 2, 1)]
    kicked = _one("impulse_run", "en", 8, "speed", seed=4)
    trace = impulse_trace(kicked.mass, kicked.kicks)
    assert trace == kicked.trace
    assert kicked.momentum == trace[-1][1] and kicked.speed == trace[-1][2]

    assert beam_trace([(2, 3), (1, -1)], 5) == [(6, 1), (5, 1)]
    beam = _one("beam_load", "en", 8, "moment", seed=4)
    trace = beam_trace(beam.loads, beam.limit)
    assert trace == beam.trace
    assert beam.moment == trace[-1][0] and beam.tip == trace[-1][1]

    assert shift_trace(4, 2, 2) == [(3, 3, 0, 1), (2, 4, -2, 1)]
    shifted = _one("mass_shift", "en", 8, "pull", seed=4)
    trace = shift_trace(shifted.left0, shifted.right0, shifted.n)
    assert trace == shifted.trace
    assert shifted.pull == trace[-1][2] and shifted.even == trace[-1][3]

    assert join_trace(6, [2, 2, 2]) == [(2, 3), (4, 1), (6, 1)]
    joined = _one("spring_join", "en", 8, "stretch", seed=4)
    trace = join_trace(joined.force, joined.springs)
    assert trace == joined.trace
    assert joined.stiffness == trace[-1][0] and joined.stretch == trace[-1][1]
    assert joined.force % joined.stiffness == 0

    assert optic_trace([(2, 3)]) == [(6, 6, 1)]
    optical = _one("optic_path", "en", 8, "path", seed=4)
    trace = optic_trace(optical.layers)
    assert trace == optical.trace
    assert optical.path == trace[-1][1] and optical.layer == trace[-1][2]

    assert pulse_trace(1, 1, 2, 1) == [(1, 1, 2, 1, 1)]
    pulses = _one("pulse_meet", "en", 8, "place", seed=4)
    trace = pulse_trace(pulses.left_h, pulses.right_h, pulses.gap, pulses.n)
    assert trace == pulses.trace
    assert pulses.peak == trace[-1][2] and pulses.place == trace[-1][4]

    assert cool_trace(5, 1, 2, 1) == [(3, 2)]
    cooled = _one("cool_ticks", "en", 8, "temp", seed=4)
    trace = cool_trace(cooled.temp0, cooled.room, cooled.divisor, cooled.n)
    assert trace == cooled.trace
    assert cooled.temp == trace[-1][0] and cooled.gap == trace[-1][1]

    assert cap_trace(12, [4]) == [(3, 18)]
    caps = _one("series_cap", "en", 8, "voltage", seed=4)
    trace = cap_trace(caps.charge, caps.caps)
    assert trace == caps.trace
    assert caps.voltage == trace[-1][0] and caps.energy == trace[-1][1]

    assert column_trace([(2, 3)]) == [(60, 60, 1)]
    column = _one("column_pressure", "en", 8, "pressure", seed=4)
    trace = column_trace(column.layers)
    assert trace == column.trace
    assert column.pressure == trace[-1][1] and column.layer == trace[-1][2]

    assert cradle_trace(5, [2, 4]) == [(2, 2, 2), (2, 2, 4)]
    cradle = _one("cradle_hit", "en", 8, "fly", seed=4)
    trace = cradle_trace(cradle.moving, cradle.clusters)
    assert trace == cradle.trace
    assert cradle.fly == trace[-1][0] and cradle.total == trace[-1][2]

    assert photon_trace(3, [2, 3, 5]) == [(0, 0, 0), (0, 1, 0), (2, 2, 2)]
    photons = _one("photon_eject", "en", 8, "count", seed=4)
    trace = photon_trace(photons.work, photons.energies)
    assert trace == photons.trace
    assert photons.count == trace[-1][1] and photons.kinetic == trace[-1][2]

    assert orbit_trace([1, 2]) == [(1, 1), (8, 8)]
    orbits = _one("orbit_years", "en", 8, "period", seed=4)
    trace = orbit_trace(orbits.radii)
    assert trace == orbits.trace
    assert orbits.period == trace[orbits.k - 1][0] and orbits.years == trace[orbits.k - 1][1]

    assert grating_trace(10, [3, 6, 11]) == [(3, 3), (1, 4), (0, 4)]
    grating = _one("grating_order", "en", 8, "orders", seed=4)
    trace = grating_trace(grating.spacing, grating.waves)
    assert trace == grating.trace
    assert grating.orders == trace[grating.k - 1][0] and grating.total == trace[-1][1]

    assert wire_trace([(2, 3, 4)]) == [(24, 24, 1)]
    wire = _one("wire_force", "en", 8, "force", seed=4)
    trace = wire_trace(wire.segments)
    assert trace == wire.trace
    assert wire.force == trace[-1][1] and wire.segment == trace[-1][2]

    assert escape_trace(12, [2, 3, 4]) == [(6, 1), (4, 1), (3, 1)]
    escaped = _one("escape_speed", "en", 8, "speed2", seed=4)
    trace = escape_trace(escaped.gravity, escaped.radii)
    assert trace == escaped.trace
    assert escaped.speed2 == trace[escaped.k - 1][0] and escaped.which == trace[-1][1]

    assert node_trace(4) == [(0, 0), (1, 1), (2, 3), (3, 6)]
    nodes = _one("harmonic_nodes", "en", 8, "nodes", seed=4)
    trace = node_trace(nodes.n)
    assert trace == nodes.trace
    assert nodes.nodes == trace[nodes.k - 1][0] and nodes.total == trace[-1][1]

    assert snell_trace(6, [(2, 5), (3, 4)]) == [(15, 15), (8, 23)]
    snell = _one("snell_shift", "en", 8, "shift", seed=4)
    trace = snell_trace(snell.invariant, snell.layers)
    assert trace == snell.trace
    assert snell.shift == trace[-1][1] and snell.layer == trace[snell.k - 1][0]

    assert heat_trace(0, 5, [3, 4, 6]) == [(0, 0, 3), (1, 1, 2), (1, 2, 3)]
    heated = _one("heat_steps", "en", 8, "temp", seed=4)
    trace = heat_trace(heated.temp0, heated.capacity, heated.packets)
    assert trace == heated.trace
    assert heated.temp == trace[-1][1] and heated.stored == trace[-1][2]

    assert hydraulic_trace([(3, 2, 6)]) == [(9, 9)]
    lifted = _one("hydraulic_lift", "en", 8, "output", seed=4)
    trace = hydraulic_trace(lifted.presses)
    assert trace == lifted.trace
    assert lifted.output == trace[lifted.k - 1][0] and lifted.total == trace[-1][1]

    assert look_say_once("1") == "11"
    said = _one("look_say", "en", 6, "length", seed=4)
    trace = look_say_trace(said.start, said.n)
    assert trace == said.trace
    assert said.length == len(trace[-1])
    assert said.count == trace[-1].count(str(said.digit))

    assert fibonacci_list(4) == [1, 2, 3, 5]
    assert [take for _, take, _ in zeckendorf_trace(4, [1, 2, 3, 5])] == [0, 1, 0, 1]
    zeck = _one("zeckendorf", "en", 8, "weight", seed=4)
    trace = zeckendorf_trace(zeck.number, zeck.fibs)
    assert trace == zeck.trace
    assert zeck.weight == sum(take for _, take, _ in trace)
    assert trace[-1][2] == 0
    assert zeck.bit == zeck.takes[zeck.k - 1]

    assert roman_trace(["I", "V"])[-1] == (4, 1)
    roman = _one("roman_value", "en", 8, "value", seed=4)
    trace = roman_trace(roman.symbols)
    assert trace == roman.trace
    assert roman.value == trace[-1][0]
    assert roman.subs == trace[-1][1]

    text, lengths = digit_stream(3)
    assert text == "123" and lengths == [1, 2, 3]
    stream = _one("digit_stream", "en", 8, "digit", seed=4)
    text, lengths = digit_stream(stream.n)
    assert text == stream.text
    assert stream.length == lengths[-1]
    assert stream.digit == int(text[stream.k - 1])

    assert deque_trace([("L", 1), ("R", 2), ("l",)]) == [(1, 1), (1, 2), (2, 1)]
    deck = _one("deque_trace", "en", 8, "size", seed=4)
    trace = deque_trace(deck.ops)
    assert trace == deck.trace
    assert deck.front == trace[-1][0]
    assert deck.size == trace[-1][1]

    turns, stats = dragon_folds(3)
    assert turns == [1, 1, 0, 1, 1, 0, 0]
    assert stats[-1] == (4, 7)
    dragon = _one("dragon_fold", "en", 8, "at_k", seed=4)
    turns, stats = dragon_folds(dragon.n)
    assert turns == dragon.turns
    assert dragon.lefts == sum(turns)
    assert dragon.at_k == turns[dragon.k - 1]
    assert len(turns) == 2 ** dragon.n - 1

    assert permanent_trace([[1, 0], [0, 1]])[-1] == 1
    assert permanent_trace([[1, 1], [1, 1]])[-1] == 2
    perm = _one("permanent", "en", 5, "value", seed=4)
    trace = permanent_trace(perm.matrix)
    assert trace == perm.trace
    assert perm.value == trace[-1]
    assert perm.parity == perm.value % 2
    assert len(trace) == 2 ** perm.n

    assert bead_trace(3)[-1][2] // 3 == 4
    beads = _one("bead_count", "en", 8, "count", seed=4)
    trace = bead_trace(beads.n)
    assert trace == beads.trace
    assert beads.count == trace[-1][2] // beads.n
    assert beads.fixed == trace[beads.k - 1][1]

    assert negabase_trace([1, 0]) == [1, -2]
    base = _one("negabase", "en", 8, "value", seed=4)
    trace = negabase_trace(base.bits)
    assert trace == base.trace
    assert base.value == trace[-1]
    assert base.ones == sum(base.bits)
    assert base.bits[0] == 1

    assert ulam_trace(6) == [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)]
    spiral = _one("ulam_walk", "en", 8, "manhattan", seed=4)
    trace = ulam_trace(spiral.n)
    assert trace == spiral.trace
    assert (spiral.x, spiral.y) == trace[-1]
    assert spiral.manhattan == abs(spiral.x) + abs(spiral.y)

    rows, total, check = luhn_trace([7, 9, 9, 2, 7, 3, 9, 8, 7, 1])
    assert total == 67 and check == 3
    luhn = _one("luhn_sum", "en", 8, "check", seed=4)
    rows, total, check = luhn_trace(luhn.digits)
    assert (rows, total, check) == (luhn.rows, luhn.total, luhn.check)
    assert (luhn.total + luhn.check) % 10 == 0

    assert kaprekar_once(21, 2) == 9
    kap = _one("kaprekar_step", "en", 8, "peak", seed=4)
    trace = kaprekar_trace(kap.start, kap.width, kap.n)
    assert trace == kap.trace
    assert kap.value == trace[-1]
    assert kap.peak == max(trace)
    assert len(set(f"{kap.start:0{kap.width}d}")) > 1

    assert morton_trace(1, 1, 2) == [0, 3]
    morton = _one("morton_code", "en", 8, "code", seed=4)
    trace = morton_trace(morton.x, morton.y, morton.n)
    assert trace == morton.trace
    assert morton.code == trace[-1]
    assert morton.bit == (morton.x >> (morton.k - 1)) & 1

    assert stock_spans([2, 1, 3]) == [1, 1, 3]
    span = _one("stock_span", "en", 8, "total", seed=4)
    spans = stock_spans(span.prices)
    assert spans == span.spans
    assert span.total == sum(spans)
    assert span.at_k == spans[span.k - 1]
    assert all(item >= 1 for item in spans)

    left, final = candy_passes([1, 0, 2])
    assert left == [1, 1, 2] and final == [2, 1, 2]
    candy = _one("candy_row", "en", 8, "total", seed=4)
    left, final = candy_passes(candy.ratings)
    assert left == candy.left and final == candy.final
    assert candy.total == sum(final)
    assert candy.at_k == final[candy.k - 1]
    assert all(item >= 1 for item in final)

    assert digit_fact_trace(145, 1) == [145]
    facts = _one("digit_fact", "en", 8, "value", seed=4)
    trace = digit_fact_trace(facts.start, facts.n)
    assert trace == facts.trace
    assert facts.value == trace[-1]
    assert facts.peak == max([facts.start, *trace])

    assert recaman_trace(4) == [(1, 0), (3, 0), (6, 0), (2, 1)]
    rec = _one("recaman", "en", 8, "last", seed=4)
    trace = recaman_trace(rec.n)
    assert trace == rec.trace
    assert rec.last == trace[-1][0]
    assert rec.subs == trace[-1][1]

    assert xor_basis_trace([1, 1], 1) == [(1, 1), (1, 1)]
    assert xor_basis_trace([1], 2) == [(1, 0)]
    basis = _one("xor_basis", "en", 8, "rank", seed=4)
    trace = xor_basis_trace(basis.numbers, basis.target)
    assert trace == basis.trace
    assert basis.rank == trace[-1][0]
    assert basis.hit == trace[-1][1]
    assert 1 <= basis.rank <= basis.n

    assert palindrome_radii("010") == [0, 1, 0]
    radius = _one("palindrome_radius", "en", 8, "longest", seed=4)
    radii = palindrome_radii(radius.symbols)
    assert radii == radius.radii
    assert radius.longest == 2 * max(radii) + 1
    assert radius.at_k == radii[radius.k - 1]

    flags = squarefree_flags(10)
    assert sum(flags[1:]) == 7 and flags[1] == 1 and flags[4] == 0
    free = _one("squarefree_row", "en", 8, "count", seed=4)
    flags = squarefree_flags(free.n)
    assert flags == free.marks
    assert free.count == sum(flags[1:])
    assert free.free == flags[free.k]

    tree, values = fenwick_build(2, [(1, 1), (2, 1)])
    assert fenwick_prefix(tree, 1) == 1 and fenwick_prefix(tree, 2) == 2 and tree[2] == 2
    fenwick = _one("fenwick_sum", "en", 8, "prefix", seed=4)
    tree, values = fenwick_build(fenwick.n, fenwick.updates)
    assert tree == fenwick.tree
    assert fenwick.prefix == fenwick_prefix(tree, fenwick.k) == sum(values[1:fenwick.k + 1])
    assert fenwick.node == tree[fenwick.k]

    table = build_sparse([3, 1, 4])
    assert sparse_min(table, 0, 2) == 1 and table[1][0] == 1
    sparse = _one("sparse_min", "en", 8, "range", seed=4)
    table = build_sparse(sparse.values)
    assert table == sparse.table
    assert sparse.range_min == min(sparse.values[sparse.left - 1:sparse.right])
    assert sparse.cell == table[sparse.level][sparse.index - 1]

    assert z_values("aaa") == [0, 2, 1]
    zeta = _one("z_array", "en", 8, "total", seed=4)
    values = z_values(zeta.symbols)
    assert values == zeta.values
    assert zeta.total == sum(values[1:])
    assert zeta.at_k == values[zeta.k - 1]

    swaps, picks = selection_trace([3, 1, 2])
    assert swaps == 2 and picks == [2, 3]
    chosen = _one("selection_swaps", "en", 8, "swaps", seed=4)
    swaps, picks = selection_trace(chosen.values)
    assert swaps == chosen.swaps and picks == chosen.picks
    assert chosen.pick == picks[chosen.k - 1]

    assert rho_cycle([0, 2, 1], 1) == (1, 2)
    rho = _one("rho_cycle", "en", 8, "cycle", seed=4)
    meet, length = rho_cycle(rho.succ, rho.start)
    assert (meet, length) == (rho.meet, rho.cycle)
    cursor = rho.meet
    for _ in range(rho.cycle):
        cursor = rho.succ[cursor]
    assert cursor == rho.meet
    assert rho.cycle >= 1

    enter, sizes = tree_times([0, 0, 1, 1])
    assert enter[1:] == [1, 2, 3] and sizes[1:] == [3, 1, 1]
    timed = _one("tree_times", "en", 8, "size", seed=4)
    enter, sizes = tree_times(timed.parents)
    assert enter == timed.enter and sizes == timed.sizes
    assert timed.enter_k == enter[timed.k]
    assert timed.size == sizes[timed.k]
    assert sizes[1] == timed.n

    swaps, moved, final = dutch_trace([2, 0])
    assert swaps == 1 and moved == 1 and final == [0, 2]
    flag = _one("dutch_flag", "en", 8, "swaps", seed=4)
    swaps, moved, final = dutch_trace(flag.colors)
    assert (swaps, moved, final) == (flag.swaps, flag.twos, flag.final)
    assert final == sorted(flag.colors)

    assert distinct_windows([0, 0, 1], 2) == [1, 2]
    window = _one("window_distinct", "en", 8, "total", seed=4)
    counts = distinct_windows(window.values, window.width)
    assert counts == window.counts
    assert window.total == sum(counts)
    assert len(counts) == window.n

    place, order = stable_order([2, 1, 2])
    assert place == [2, 1, 3] and order == [1, 0, 2]
    stable = _one("stable_place", "en", 8, "place", seed=4)
    place, order = stable_order(stable.values)
    assert place == stable.place and order == stable.order
    assert stable.who == order[stable.k - 1] + 1

    assert naive_scan("010", "10") == (2, 3, [1, 2])
    found = _one("naive_find", "en", 8, "checks", seed=4)
    index, checks, used = naive_scan(found.text, found.pattern)
    assert (index, checks, used) == (found.index, found.checks, found.used)
    assert len(used) == found.n
    assert checks == sum(used)

    assert budget_take([5, 1, 1], 2) == [(0, 0, 2), (1, 1, 1), (1, 2, 0)]
    budget = _one("budget_take", "en", 8, "taken", seed=4)
    trace = budget_take(budget.costs, budget.budget)
    assert trace == budget.trace
    assert budget.taken == trace[-1][1]
    assert budget.left == trace[-1][2]
    assert budget.left == budget.budget - sum(
        cost for cost, (flag, _, _) in zip(budget.costs, trace) if flag
    )

    assert apply_ops(2, [("add", 3), ("mul", 2)]) == [5, 10]
    skipped = _one("skip_op", "en", 8, "without", seed=4)
    assert apply_ops(skipped.start, skipped.ops)[-1] == skipped.final
    reduced = skipped.ops[:skipped.k - 1] + skipped.ops[skipped.k:]
    assert (apply_ops(skipped.start, reduced)[-1] if reduced else skipped.start) == skipped.without

    assert retry_until([1, 0, 0], 2)[-1] == (4, 2, 2)
    retry = _one("retry_goal", "en", 8, "tries", seed=4)
    trace = retry_until(retry.pattern, retry.n)
    assert trace == retry.trace
    assert retry.tries == trace[-1][0]
    assert retry.fails == retry.tries - retry.n
    assert 1 in retry.pattern

    assert signal_trace([0, 1, 1, 0])[-1] == (1, 2)
    signal = _one("signal_edges", "en", 8, "rises", seed=4)
    trace = signal_trace(signal.bits)
    assert trace == signal.trace
    assert (signal.rises, signal.longest) == trace[-1]

    trace, state = plan_trace([(1, 2), (2, 3), (4, 5)])
    assert trace[-1][0] == 2 and state == {1, 2, 3}
    plan = _one("plan_gate", "en", 8, "fired", seed=4)
    trace, state = plan_trace(plan.actions)
    assert trace == plan.trace and state == plan.state
    assert plan.fired == trace[-1][0]
    assert plan.has == int(plan.bit in state)

    chosen, cost = tool_assign([1, 2], [(5, (1,)), (2, (1, 2))])
    assert chosen == [2, 2] and cost == 4
    tools = _one("tool_pick", "en", 8, "cost", seed=4)
    chosen, cost = tool_assign(tools.queries, tools.tools)
    assert chosen == tools.chosen and cost == tools.cost
    assert tools.tool == chosen[tools.k - 1]

    assert diff_trace([1, 2, 3], [1, 0, 3])[-1] == (1, 2)
    diff = _one("diff_count", "en", 8, "diffs", seed=4)
    trace = diff_trace(diff.left, diff.right)
    assert trace == diff.trace
    assert diff.diffs == sum(a != b for a, b in zip(diff.left, diff.right))
    assert diff.first == trace[-1][1]

    trace, cells = patch_trace(2, [(1, 4), (1, 4), (2, 1)])
    assert trace[-1][0] == 2 and cells[1] == 4
    patch = _one("cell_patch", "en", 8, "writes", seed=4)
    trace, cells = patch_trace(patch.n, patch.edits)
    assert trace == patch.trace and cells == patch.cells
    assert patch.writes == trace[-1][0]
    assert patch.cell == cells[patch.k]

    assert pred_trace([(1, "<", 2), (3, "=", 4)])[-1] == (1, 2)
    preds = _one("pred_scan", "en", 8, "trues", seed=4)
    trace = pred_trace(preds.preds)
    assert trace == preds.trace
    assert preds.trues == trace[-1][0]
    assert preds.first == trace[-1][1]

    assert rate_flags([1, 2, 3], 2, 1) == [1, 0, 1]
    limited = _one("rate_limit", "en", 8, "served", seed=4)
    flags = rate_flags(limited.times, limited.window, limited.quota)
    assert flags == limited.flags
    assert limited.served == sum(flags)
    assert limited.at_k == flags[limited.k - 1]

    assert lateness_trace([(2, 1), (1, 10)]) == [(2, 1, 1), (3, 1, 1)]
    late = _one("lateness", "en", 8, "sum", seed=4)
    trace = lateness_trace(late.jobs)
    assert trace == late.trace
    assert late.sum == trace[-1][1] and late.count == trace[-1][2]

    trace, state = flip_trace(2, [1, 1, 2])
    assert trace[-1] == (1, 1) and state[1:] == [0, 1]
    flips = _one("switch_flip", "en", 8, "ons", seed=4)
    trace, state = flip_trace(flips.n, flips.toggles)
    assert trace == flips.trace and state == flips.state
    assert flips.ons == trace[-1][1]
    assert flips.bit == state[flips.k]

    assert turn_trace([(0, 0), (1, 0), (1, 1)]) == [(1, 1, 0)]
    turns = _one("turn_signs", "en", 8, "lefts", seed=4)
    trace = turn_trace(turns.points)
    assert trace == turns.trace
    assert turns.lefts == trace[-1][1] and turns.rights == trace[-1][2]

    assert first_fit(4, [2, 2, 3]) == (2, [1, 3, 0])
    fit = _one("first_fit", "en", 8, "placed", seed=4)
    placed, starts = first_fit(fit.tape, fit.sizes)
    assert placed == fit.placed and starts == fit.starts
    assert fit.start == starts[fit.k - 1]

    scores, winners = plurality_trace([1, 2, 1], 2)
    assert scores == [0, 2, 1] and winners == [1, 1, 1]
    votes = _one("plurality", "en", 8, "winner", seed=4)
    scores, winners = plurality_trace(votes.votes, votes.candidates)
    assert scores == votes.scores and winners == votes.winners
    assert votes.score == scores[votes.k]
    assert votes.winner == winners[-1]

    assert floor_trace(1, [3, 3]) == [(3, 2), (3, 2)]
    floors = _one("floor_run", "en", 8, "distance", seed=4)
    trace = floor_trace(floors.start, floors.stops)
    assert trace == floors.trace
    assert floors.floor == trace[-1][0] and floors.distance == trace[-1][1]

    assert saturate_trace([1, 1, 1], 2) == [(1, 0), (2, 0), (2, 1)]
    counter = _one("saturate_count", "en", 8, "hits", seed=4)
    trace = saturate_trace(counter.ops, counter.cap)
    assert trace == counter.trace
    assert counter.value == trace[-1][0] and counter.hits == trace[-1][1]

    assert undo_trace([("set", 4), ("set", 7), ("undo", 0)]) == [(4, 1), (7, 2), (4, 1)]
    undone = _one("undo_reg", "en", 8, "depth", seed=4)
    trace = undo_trace(undone.commands)
    assert trace == undone.trace
    assert undone.value == trace[-1][0] and undone.depth == trace[-1][1]

    assert cover_point_trace([(0, 2), (3, 5), (1, 1)], 1) == [(1, 1), (1, 1), (2, 1)]
    covered = _one("cover_point", "en", 8, "count", seed=4)
    trace = cover_point_trace(covered.intervals, covered.point)
    assert trace == covered.trace
    assert covered.count == trace[-1][0] and covered.first == trace[-1][1]

    assert next_fit([3, 3, 2], 5) == [(1, 3), (2, 3), (2, 5)]
    packed = _one("next_fit", "en", 8, "bins", seed=4)
    trace = next_fit(packed.items, packed.capacity)
    assert trace == packed.trace
    assert packed.bins == trace[-1][0] and packed.fill == trace[-1][1]

    assert sgd_trace(0, [(1, 2)]) == [(-2, 2, 4)]
    online = _one("sgd_online", "en", 8, "weight", seed=4)
    trace = sgd_trace(online.start, online.points)
    assert trace == online.trace
    assert online.weight == trace[-1][1] and online.loss == trace[-1][2]

    trace, values, prefs = critic_trace(1, [(0, 0, 3, 0)])
    assert trace == [(3, 3, 1, 0)] and values == [3] and preferred_action(prefs[0]) == 1
    actor = _one("actor_critic", "en", 8, "value", seed=4)
    trace, values, prefs = critic_trace(actor.states, actor.jumps)
    assert trace == actor.trace and values == actor.values and prefs == actor.prefs
    assert actor.value == values[actor.k - 1]
    assert actor.action == preferred_action(prefs[actor.k - 1])

    trace = ucb_trace([[1, 9, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]])
    assert [step[0] for step in trace] == [1, 2, 3, 1]
    assert trace[-1][2] == 10
    bandit = _one("ucb_bandit", "en", 8, "reward", seed=4)
    trace = ucb_trace(bandit.columns)
    assert trace == bandit.trace
    assert bandit.reward == trace[-1][2]
    assert bandit.arm == min(
        index for index, count in enumerate(trace[-1][3]) if count == max(trace[-1][3])
    ) + 1

    assert clip_trace(0, [3, -3], 1) == [(1, -1, 1), (-1, 0, 2)]
    clipped = _one("grad_clip", "en", 8, "weight", seed=4)
    trace = clip_trace(clipped.start, clipped.gradients, clipped.limit)
    assert trace == clipped.trace
    assert clipped.weight == trace[-1][1] and clipped.clips == trace[-1][2]

    assert decay_trace(4, [1]) == [(2, 1, 2)]
    assert decay_trace(-3, [0]) == [(-2, -1, -2)]
    decayed = _one("weight_decay", "en", 8, "decay", seed=4)
    trace = decay_trace(decayed.start, decayed.gradients)
    assert trace == decayed.trace
    assert decayed.weight == trace[-1][1] and decayed.decay == trace[-1][2]

    assert stop_trace([5, 4, 4, 4], 2)[-1] == (4, 2, 4)
    stopped = _one("early_stop", "en", 8, "stop", seed=4)
    trace = stop_trace(stopped.losses, stopped.patience)
    assert trace == stopped.trace
    assert stopped.best == trace[-1][0] and stopped.stop == trace[-1][2]

    assert prototype_trace([(0, 0), (2, 1)]) == [(0, 1, 0, 0), (0, 1, 2, 1)]
    assert nearer_class(2, [0, 2], [1, 1]) == 2
    proto = _one("prototype_mean", "en", 8, "label", seed=4)
    trace = prototype_trace(proto.points)
    assert trace == proto.trace
    assert proto.total == proto.sums[proto.k - 1]
    assert proto.label == nearer_class(proto.query, proto.sums, proto.counts)

    trace = sync_trace(1, [(0, 3, 0)], 1)
    assert trace[0][0] == 3 and trace[0][1] == 1 and trace[0][3] == [3]
    synced = _one("target_sync", "en", 8, "target", seed=4)
    trace = sync_trace(synced.states, synced.jumps, synced.period)
    assert trace == synced.trace
    assert synced.online_value == trace[-1][2][synced.k - 1]
    assert synced.target_value == trace[-1][3][synced.k - 1]

    assert fifo_trace([1, 2, 3], 2)[-1] == ([2, 3], 1)
    replay = _one("replay_fifo", "en", 8, "slot", seed=4)
    trace = fifo_trace(replay.values, replay.capacity)
    assert trace == replay.trace
    assert replay.slot == trace[-1][0][replay.k - 1]
    assert replay.overwrites == trace[-1][1]

    assert shape_trace([0, 5], [(0, 1, 1)]) == [(5, 6, 6, 5)]
    shaped = _one("shape_reward", "en", 8, "total", seed=4)
    trace = shape_trace(shaped.potentials, shaped.jumps)
    assert trace == shaped.trace
    assert shaped.total == trace[-1][2] and shaped.bonus == trace[-1][3]

    assert eps_trace([(0, 7, 8)], 1) == [(1, 7, 1, 1)]
    assert eps_trace([(0, 7, 8)], 0) == [(0, 8, 0, 0)]
    scheduled = _one("eps_schedule", "en", 8, "explores", seed=4)
    trace = eps_trace(scheduled.rows, scheduled.start)
    assert trace == scheduled.trace
    assert scheduled.explores == trace[-1][3]
    assert scheduled.taken == trace[scheduled.k - 1][1]

    assert scope_lookup([{1: 4}, {1: 9}], 1) == 9
    assert scope_trace([("set", 1, 4), ("in",), ("set", 1, 9), ("out",)])[-1] == (1, 4, 0, 0)
    scopes = _one("scope_lookup", "en", 8, "value", seed=4)
    trace = scope_trace(scopes.commands)
    assert trace == scopes.trace
    assert scopes.value == trace[-1][scopes.k] and scopes.depth == trace[-1][0]

    assert lock_trace(2, [("get", 1), ("get", 1), ("put", 1)])[-1] == (1, [0, 0, 0])
    locks = _one("lock_log", "en", 8, "fails", seed=4)
    trace = lock_trace(locks.locks, locks.ops)
    assert trace == locks.trace
    assert locks.fails == trace[-1][0] and locks.held == trace[-1][1][locks.k]

    assert toll_trace({(1, 2): 3}, [1, 2, 2]) == [(3, 0), (3, 2)]
    route = _one("path_toll", "en", 8, "toll", seed=4)
    trace = toll_trace(route.edges, route.walk)
    assert trace == route.trace
    assert route.toll == trace[-1][0] and route.stop == trace[-1][1]

    assert backoff_trace([0, 0]) == [(1, 1, 1, 2), (0, 1, 1, 2)]
    waits = _one("backoff_wait", "en", 8, "successes", seed=4)
    trace = backoff_trace(waits.times)
    assert trace == waits.trace
    assert waits.successes == trace[-1][1] and waits.wait == trace[-1][3]

    assert priority_order([(2, 1), (1, 1)]) == [1, 2]
    assert priority_order([(1, 2), (1, 1)]) == [1, 1, 2]
    ranked = _one("priority_run", "en", 8, "total", seed=4)
    order = priority_order(ranked.jobs)
    assert order == ranked.order
    assert ranked.total == len(order) and ranked.tick == order[ranked.k - 1]

    assert inbox_trace([("send", 1, 4), ("send", 1, 5), ("take", 1)])[-1] == (5, 1, 0, 0)
    inbox = _one("inbox_take", "en", 8, "front", seed=4)
    trace = inbox_trace(inbox.commands)
    assert trace == inbox.trace
    assert inbox.front == trace[-1][(inbox.k - 1) * 2]
    assert inbox.pending == trace[-1][(inbox.k - 1) * 2 + 1]

    assert goal_trace([("push", 1), ("push", 2), ("close", 1), ("close", 2)])[-1] == (1, 1, 2)
    goals = _one("goal_match", "en", 8, "bad", seed=4)
    trace = goal_trace(goals.commands)
    assert trace == goals.trace
    assert goals.top == trace[-1][0] and goals.bad == trace[-1][1]

    assert craft_trace([("gather", 1), ("gather", 2), ("craft",)])[-1] == (0, 0, 1, 0)
    crafted = _one("craft_need", "en", 8, "stock", seed=4)
    trace = craft_trace(crafted.commands)
    assert trace == crafted.trace
    assert crafted.stock == trace[-1][crafted.k - 1] and crafted.fails == trace[-1][3]

    assert checkpoint_trace([("add", 3), ("mark",), ("add", -1), ("roll",)])[-1] == (3, 1)
    saved = _one("checkpoint_roll", "en", 8, "value", seed=4)
    trace = checkpoint_trace(saved.commands)
    assert trace == saved.trace
    assert saved.value == trace[-1][0] and saved.saves == trace[-1][1]

    assert schema_trace([(0, 1, 2), (1, 2, 2), (1, 2, 3)])[-1] == (1, 1)
    checked = _one("schema_check", "en", 8, "valid", seed=4)
    trace = schema_trace(checked.records)
    assert trace == checked.trace
    assert checked.valid == trace[-1][0] and checked.first == trace[-1][1]

    value, muls, steps = eval_infix("2 + 3 * 4")
    assert value == 14 and muls == 1 and steps[-1][0] == "+"
    value, muls, steps = eval_infix("(2 + 3) * 4")
    assert value == 20 and muls == 1 and [step[0] for step in steps] == ["+", "*"]
    expr = _one("infix_value", "en", 8, "value", seed=4)
    parsed, parsed_muls, parsed_steps = eval_infix(expr.expr)
    assert parsed == expr.value and parsed_muls == expr.muls and parsed_steps == expr.trace

    assert ballot_trace([1, 0, 0]) == [(1, 0, 0), (0, 0, 0), (-1, -1, 3)]
    walk = _one("ballot_walk", "en", 8, "low", seed=4)
    trace = ballot_trace(walk.steps)
    assert trace == walk.trace
    assert walk.low == trace[-1][1] and walk.fall == trace[-1][2]

    running, folds, root, rounds = digit_trace([9, 9])
    assert running == [9, 18] and folds == [(99, 18), (18, 9)] and root == 9 and rounds == 2
    rooted = _one("digit_root", "en", 8, "root", seed=4)
    running, folds, root, rounds = digit_trace(rooted.digits)
    assert (running, folds, root, rounds) == (rooted.running, rooted.rounds, rooted.root, rooted.round_count)

    trace = crt_search(1, 2, 0, 3)
    assert trace[1] == (3, 0, 1)
    lifted = _one("crt_lift", "en", 8, "value", seed=4)
    trace = crt_search(lifted.remain_a, lifted.mod_a, lifted.remain_b, lifted.mod_b)
    assert trace == lifted.trace
    assert lifted.value % lifted.mod_a == lifted.remain_a
    assert lifted.value % lifted.mod_b == lifted.remain_b
    assert lifted.lift == next(index for index, row in enumerate(trace) if row[2])

    assert order_trace(2, 5, 4)[-1] == (1, 4)
    ordered = _one("mod_order", "en", 8, "order", seed=4)
    trace = order_trace(ordered.base, ordered.modulus, ordered.n)
    assert trace == ordered.trace
    assert ordered.order == trace[-1][1] and ordered.at == trace[ordered.k - 1][0]

    assert repeat_trace([1, 2, 1]) == [(0, 1), (0, 2), (3, 2)]
    repeated = _one("first_repeat", "en", 8, "at", seed=4)
    trace = repeat_trace(repeated.values)
    assert trace == repeated.trace
    assert repeated.at == trace[-1][0] and repeated.span == trace[-1][1]

    assert coupon_trace([1, 2, 1], 2)[-1] == (2, 2, 1)
    coupons = _one("coupon_cover", "en", 8, "cover", seed=4)
    trace = coupon_trace(coupons.items, coupons.kinds)
    assert trace == coupons.trace
    assert coupons.cover == trace[-1][1] and coupons.extra == trace[-1][2]

    trace = weigh_trace(3, [((1,), (2,), 1)])
    assert trace == [(1, 1, 2)]
    coins = _one("coin_weigh", "en", 8, "heavy", seed=4)
    trace = weigh_trace(coins.items, coins.weighings)
    assert trace == coins.trace
    assert coins.only == trace[-1][2] and coins.seen == trace[-1][1]
    if coins.only:
        assert coins.only == coins.heavy

    assert color_trace(3, [(1, 2), (2, 3), (1, 3)])[-1] == (0, 1, 3)
    colored = _one("two_color", "en", 8, "conflicts", seed=4)
    trace = color_trace(colored.n, colored.edges)
    assert trace == colored.trace
    assert colored.conflicts == trace[-1][1] and colored.first == trace[-1][2]

    assert lattice_trace(3, 1, 2, 2) == [(0, 0, 0), (1, 1, 0), (1, 2, 3)]
    lattice = _one("lattice_sum", "en", 8, "total", seed=4)
    trace = lattice_trace(lattice.n, lattice.numer, lattice.denom, lattice.threshold)
    assert trace == lattice.trace
    assert lattice.total == trace[-1][1] and lattice.cross == trace[-1][2]

    assert roc_trace([(1, 0), (3, 1), (2, 0)])[0] == (3, 1, 1, 0)
    ranked = _one("roc_walk", "en", 8, "top", seed=4)
    trace = roc_trace(ranked.pairs)
    assert trace == ranked.trace
    assert ranked.top == next(index for index, row in enumerate(trace, 1) if row[1] == 1)
    assert ranked.traps == ranked.top - 1

    assert ema_trace([1, 1]) == [(1, 1), (1, 1)]
    averaged = _one("ema_loss", "en", 8, "ema", seed=4)
    trace = ema_trace(averaged.losses)
    assert trace == averaged.trace
    assert averaged.ema == trace[-1][0] and averaged.peak == trace[-1][1]

    assert lr_trace(0, [1, 1], 4, 2) == [(4, -4, 4), (4, -8, 2)]
    cooled = _one("lr_decay", "en", 8, "weight", seed=4)
    trace = lr_trace(cooled.start, cooled.gradients, cooled.rate0, cooled.period)
    assert trace == cooled.trace
    assert cooled.weight == trace[-1][1] and cooled.rate == trace[-1][2]

    assert batch_trace(0, [((1, 1), (1, 1))]) == [(-2, 2)]
    batched = _one("batch_grad", "en", 8, "grad", seed=4)
    trace = batch_trace(batched.start, batched.batches)
    assert trace == batched.trace
    assert batched.grad == trace[-1][0] and batched.weight == trace[-1][1]

    assert margin_trace([(5, 1), (2, 0)]) == [(5, 0, 0), (5, 2, 3)]
    margin = _one("best_margin", "en", 8, "margin", seed=4)
    trace = margin_trace(margin.pairs)
    assert trace == margin.trace
    assert margin.pos == trace[-1][0] and margin.margin == trace[-1][2]

    assert base_trace([4, 1]) == [(0, 4, 4), (4, -3, 2)]
    based = _one("online_base", "en", 8, "adv", seed=4)
    trace = base_trace(based.rewards)
    assert trace == based.trace
    assert based.adv == trace[based.k - 1][1] and based.mean == trace[-1][2]

    assert td_clip_trace([(5, 0, 0)], 1) == [(5, 1, 1, 1)]
    clipped = _one("td_clip", "en", 8, "total", seed=4)
    trace = td_clip_trace(clipped.rows, clipped.limit)
    assert trace == clipped.trace
    assert clipped.total == trace[-1][2] and clipped.clips == trace[-1][3]

    assert bonus_trace(1, [(1, 0)], 4) == [(4, 4, 4)]
    bonus = _one("count_bonus", "en", 8, "bonus", seed=4)
    trace = bonus_trace(bonus.states, bonus.visits, bonus.pool)
    assert trace == bonus.trace
    assert bonus.bonus == trace[-1][1] and bonus.score == trace[-1][2]

    assert hold_trace([(2, 1), (3, 2)]) == [2, 3, 3]
    held = _one("option_hold", "en", 8, "tick", seed=4)
    ticks = hold_trace(held.options)
    assert ticks == held.ticks
    assert held.total == len(ticks) and held.tick == ticks[held.k - 1]

    assert eval_sweeps([1, 0], [0, 0], 2) == [[1, 0], [2, 1]]
    evaluated = _one("policy_eval", "en", 8, "value", seed=4)
    history = eval_sweeps(evaluated.rewards, evaluated.nxt, evaluated.n)
    assert history == evaluated.history
    assert evaluated.value == history[-1][evaluated.k - 1]
    assert evaluated.total == sum(history[-1])

    assert horner_trace([2, 0, 1], 3, 5)[-1] == (19, 4)
    assert horner_plain([2, 0, 1], 3) == 19
    horner = _one("horner_mod", "en", 8, "plain", seed=4)
    trace = horner_trace(horner.coeffs, horner.point, horner.modulus)
    assert trace == horner.trace
    assert horner.plain == trace[-1][0] and horner.folded == trace[-1][1]

    assert root_trace([1, -1], [1, 2]) == [0, 1]
    rooted = _one("rational_root", "en", 8, "count", seed=4)
    values = root_trace(rooted.coeffs, rooted.candidates)
    assert values == rooted.values
    assert rooted.count == sum(value == 0 for value in values)
    assert rooted.small == min((point for point, value in zip(rooted.candidates, values) if value == 0))

    assert geom_trace(2, 3) == [(1, 1), (2, 3), (4, 7)]
    assert geom_closed(2, 3) == 7
    geometric = _one("geom_sum", "en", 8, "total", seed=4)
    trace = geom_trace(geometric.ratio, geometric.n)
    assert trace == geometric.trace
    assert geometric.total == trace[-1][1] and geometric.last == trace[-1][0]

    coeffs = cyclo_coeffs(5)
    assert coeffs == [1, 1, 1, 1, 1]
    assert cyclo_trace(coeffs, 2)[-1] == 31
    cyclo = _one("cyclo_eval", "en", 8, "value", seed=4)
    trace = cyclo_trace(cyclo.coeffs, cyclo.point)
    assert trace == cyclo.trace
    assert cyclo.value == trace[-1] and cyclo.degree == len(cyclo.coeffs) - 1

    assert chebyshev_trace(2, 3)[-1] == 17
    cheb = _one("chebyshev_row", "en", 8, "value", seed=4)
    trace = chebyshev_trace(cheb.n, cheb.point)
    assert trace == cheb.trace
    assert cheb.value == trace[-1] and cheb.total == sum(trace)

    assert hermite_trace(2, 1)[-1] == 2
    hermite = _one("hermite_row", "en", 8, "value", seed=4)
    trace = hermite_trace(hermite.n, hermite.point)
    assert trace == hermite.trace
    assert hermite.value == trace[-1] and hermite.total == sum(trace)

    assert conv_full([1, 2], [3, 4]) == [3, 10, 8]
    convolved = _one("series_conv", "en", 8, "total", seed=4)
    output = conv_full(convolved.left, convolved.right)
    assert output == convolved.output
    assert convolved.at == output[convolved.k - 1] and convolved.total == sum(output)

    assert transport_trace([3, 1], [2, 8]) == [1, 5]
    moved = _one("transport_cost", "en", 8, "cost", seed=4)
    gaps = transport_trace(moved.left, moved.right)
    assert gaps == moved.trace
    assert moved.cost == sum(gaps) and moved.gap == gaps[moved.k - 1]

    assert poch_trace(3, 3) == [3, 12, 60]
    rising = _one("pochhammer", "en", 8, "value", seed=4)
    trace = poch_trace(rising.start, rising.n)
    assert trace == rising.trace
    assert rising.value == trace[-1] and rising.factor == rising.start + rising.n - 1

    assert binom_trace(5, 2) == [4, 10]
    binomial = _one("binom_build", "en", 8, "value", seed=4)
    trace = binom_trace(binomial.upper, binomial.n)
    assert trace == binomial.trace
    assert binomial.value == trace[-1] and binomial.mod == trace[-1] % binomial.modulus

    assert farey_trace(0, 1, 5)[-1] == (1, 5)
    farey = _one("farey_next", "en", 8, "numer", seed=4)
    trace = farey_trace(farey.numer, farey.denom, farey.n)
    assert trace == farey.trace
    assert farey.next_numer == trace[-1][0] and farey.next_denom == trace[-1][1]

    assert mobius(1) == 1 and mobius(4) == 0 and mobius(6) == 1
    assert mobius_trace(4)[-1] == (0, -1)
    mobius_task = _one("mobius_sum", "en", 8, "sum", seed=4)
    trace = mobius_trace(mobius_task.n)
    assert trace == mobius_task.trace
    assert mobius_task.sum == trace[-1][1] and mobius_task.mu == trace[mobius_task.k - 1][0]

    assert involution_trace(5)[-1] == (26, 16)
    involution = _one("involution_count", "en", 8, "count", seed=4)
    trace = involution_trace(involution.n)
    assert trace == involution.trace
    assert involution.count == trace[-1][0] and involution.added == trace[-1][1]

    assert jacobi(2, 7) == 1 and jacobi(3, 7) == -1
    jacobi_task = _one("jacobi_row", "en", 8, "sum", seed=4)
    trace = jacobi_trace(jacobi_task.number, jacobi_task.n)
    assert trace == jacobi_task.trace
    assert jacobi_task.sum == trace[-1][1] and jacobi_task.symbol == trace[jacobi_task.k - 1][0]

    assert valuation(4) == 2 and ruler_trace(4)[-1] == (2, 3)
    ruler = _one("ruler_sum", "en", 8, "total", seed=4)
    trace = ruler_trace(ruler.n)
    assert trace == ruler.trace
    assert ruler.total == trace[-1][1] and ruler.power == trace[ruler.k - 1][0]

    assert thue_trace(4)[-1] == (0, 2)
    thue = _one("thue_count", "en", 8, "ones", seed=4)
    trace = thue_trace(thue.n)
    assert trace == thue.trace
    assert thue.ones == trace[-1][1] and thue.bit == trace[thue.k][0]

    assert divisor_sum(6) == 6 and divisor_sum(10) == 8 and divisor_sum(4) == 3
    assert divisor_sum(1) == 0 and aliquot_trace(6, 2) == [6, 6]
    aliquot = _one("aliquot_walk", "en", 8, "final", seed=4)
    trace = aliquot_trace(aliquot.start, aliquot.n)
    assert trace == aliquot.trace
    assert aliquot.final == trace[-1] and aliquot.peak == max(trace)

    assert carmichael(1) == 1 and carmichael(6) == 2 and carmichael(8) == 2
    carmichael_task = _one("carmichael_row", "en", 8, "lcm", seed=4)
    trace = carmichael_trace(carmichael_task.n)
    assert trace == carmichael_task.trace
    assert carmichael_task.lcm == trace[-1][1] and carmichael_task.lam == trace[carmichael_task.k - 1][0]

    assert cayley_trace(4) == [4, 16]
    trees = _one("cayley_trees", "en", 8, "trees", seed=4)
    trace = cayley_trace(trees.vertices)
    assert trace == trees.trace
    assert trees.trees == trace[-1] and trees.part == trace[trees.k - 1]

    assert factoradic_trace(5, 3) == [1, 2, 0]
    factorial = _one("factoradic", "en", 8, "sum", seed=4)
    trace = factoradic_trace(factorial.number, factorial.n)
    assert trace == factorial.trace
    assert factorial.total == sum(trace) and factorial.digit == trace[factorial.k - 1]

    assert stirling_rows(5)[-1] == [0, 24, 50, 35, 10, 1]
    stirling = _one("stirling_first", "en", 8, "total", seed=4)
    rows = stirling_rows(stirling.n)
    assert rows == stirling.rows
    assert stirling.total == sum(rows[-1]) and stirling.entry == rows[-1][stirling.k]

    assert bell_trace(5)[0] == [1, 1, 2, 5, 15, 52]
    bells = _one("bell_row", "en", 8, "value", seed=4)
    values, terms = bell_trace(bells.n)
    assert values == bells.values and terms == bells.terms
    assert bells.value == values[-1]
    assert bells.term == next(item[4] for item in terms if item[0] == bells.n and item[1] == bells.k)

    assert andre_rows(5)[-1][-1] == 16
    andre = _one("andre_row", "en", 8, "value", seed=4)
    rows = andre_rows(andre.n)
    assert rows == andre.rows
    assert andre.value == rows[-1][-1] and andre.cell == rows[-1][andre.k]

    assert bernoulli_den_trace(4)[-1] == (1, 30, 3)
    assert bernoulli_den_trace(6)[-1][1] == 42
    bernoulli = _one("bernoulli_den", "en", 8, "den", seed=4)
    trace = bernoulli_den_trace(bernoulli.n)
    assert trace == bernoulli.trace
    assert bernoulli.den == trace[-1][1] and bernoulli.count == trace[-1][2]

    assert chebyshev_u_trace(3, 2)[-1] == 56
    second = _one("chebyshev_u", "en", 8, "value", seed=4)
    trace = chebyshev_u_trace(second.n, second.point)
    assert trace == second.trace
    assert second.value == trace[-1] and second.total == sum(trace)

    assert sigma(6) == 12 and sigma_trace(4)[-1] == (7, 15)
    divisors = _one("sigma_row", "en", 8, "total", seed=4)
    trace = sigma_trace(divisors.n)
    assert trace == divisors.trace
    assert divisors.total == trace[-1][1] and divisors.at == trace[divisors.k - 1][0]

    assert prime_omega(1) == 0 and prime_omega(12) == 3
    omega = _one("prime_omega", "en", 8, "total", seed=4)
    trace = omega_trace(omega.n)
    assert trace == omega.trace
    assert omega.total == trace[-1][1] and omega.at == trace[omega.k - 1][0]

    assert [item[2] for item in motzkin_trace(5)] == [1, 1, 2, 4, 9, 21]
    motzkin = _one("motzkin_row", "en", 8, "value", seed=4)
    trace = motzkin_trace(motzkin.n)
    assert trace == motzkin.trace
    assert motzkin.value == trace[-1][2] and motzkin.numer == trace[-1][0]

    assert primorial_trace(4) == [(2, 2), (3, 6), (5, 30), (7, 210)]
    product = _one("primorial", "en", 8, "value", seed=4)
    trace = primorial_trace(product.n)
    assert trace == product.trace
    assert product.value == trace[-1][1] and product.prime == trace[product.k - 1][0]

    table, _cells = growth_table(5)
    assert rank_parts([0, 1, 2, 1, 3], table)[0] == 42
    growth = _one("rgs_rank", "en", 8, "rank", seed=4)
    table, cells = growth_table(growth.n)
    rank, parts = rank_parts(growth.word, table)
    assert cells == growth.cells and parts == growth.parts
    assert growth.rank == rank and growth.part == parts[growth.k - 1][3]

    assert bernoulli_trace(2)[0][2] == (1, 6)
    assert bernoulli_trace(4)[0][4] == (-1, 30)
    bernoulli = _one("bernoulli_numer", "en", 8, "numer", seed=4)
    values, terms = bernoulli_trace(bernoulli.n)
    assert values == bernoulli.values and terms == bernoulli.terms
    assert (bernoulli.numer, bernoulli.denom) == values[-1]

    assert genocchi_value(2) == -1 and genocchi_value(4) == 1 and genocchi_value(6) == -3
    genocchi = _one("genocchi_row", "en", 8, "value", seed=4)
    assert genocchi.value == genocchi_value(genocchi.n)
    assert genocchi.numer == bernoulli_trace(genocchi.n)[0][-1][0]

    assert kronecker(3, 2)[0] == -1 and kronecker(1, 8)[0] == 1
    symbol_row = _one("kronecker_row", "en", 8, "sum", seed=4)
    trace = kronecker_trace(symbol_row.number, symbol_row.n)
    assert trace == symbol_row.trace
    assert symbol_row.sum == trace[-1][1] and symbol_row.symbol == trace[symbol_row.k - 1][0]

    cells, dimension = hook_trace([2, 1])
    assert [cell[2] for cell in cells] == [3, 1, 1] and dimension == 2
    assert hook_trace([3, 2])[1] == 5
    diagram = _one("hook_length", "en", 8, "dim", seed=4)
    cells, dimension = hook_trace(diagram.parts)
    assert cells == diagram.cells and diagram.dim == dimension
    assert diagram.hook == cells[diagram.k - 1][2]

    assert legendre_trace(2, 2)[-1] == (11, 2)
    legendre = _one("legendre_frac", "en", 8, "numer", seed=4)
    trace = legendre_trace(legendre.n, legendre.point)
    assert trace == legendre.trace and (legendre.numer, legendre.denom) == trace[-1]

    assert laguerre_trace(2, 1)[-1] == (-1, 2)
    laguerre = _one("laguerre_frac", "en", 8, "numer", seed=4)
    trace = laguerre_trace(laguerre.n, laguerre.point)
    assert trace == laguerre.trace and (laguerre.numer, laguerre.denom) == trace[-1]

    assert harmonic_trace(4)[-1] == (25, 12) and harmonic_trace(5)[-1] == (137, 60)
    harmonic = _one("harmonic_frac", "en", 8, "numer", seed=4)
    trace = harmonic_trace(harmonic.n)
    assert trace == harmonic.trace and (harmonic.numer, harmonic.denom) == trace[-1]

    assert eulerian_rows(5)[-1] == [1, 26, 66, 26, 1]
    eulerian = _one("eulerian_row", "en", 8, "total", seed=4)
    rows = eulerian_rows(eulerian.n)
    assert rows == eulerian.rows
    assert eulerian.total == sum(rows[-1]) and eulerian.entry == rows[-1][eulerian.k]

    assert fubini_trace(5)[0] == [1, 1, 3, 13, 75, 541]
    ordered = _one("fubini_row", "en", 8, "value", seed=4)
    values, terms = fubini_trace(ordered.n)
    assert values == ordered.values and terms == ordered.terms
    assert ordered.value == values[-1]
    assert ordered.term == next(item[4] for item in terms if item[0] == ordered.n and item[1] == ordered.k)

    assert delannoy_trace(3)[-1][2] == 63 and delannoy_recur(5) == 1683
    delannoy = _one("delannoy_row", "en", 8, "value", seed=4)
    trace = delannoy_trace(delannoy.n)
    assert trace == delannoy.trace
    assert delannoy.value == trace[-1][2] and delannoy.term == trace[delannoy.k][1]

    assert tau(1) == 1 and tau(6) == 4 and tau_trace(4)[-1] == (3, 8)
    counted = _one("tau_row", "en", 8, "total", seed=4)
    trace = tau_trace(counted.n)
    assert trace == counted.trace
    assert counted.total == trace[-1][1] and counted.at == trace[counted.k - 1][0]

    assert prime_nu(1) == 0 and prime_nu(12) == 2 and prime_nu(8) == 1
    distinct = _one("prime_nu", "en", 8, "total", seed=4)
    trace = nu_trace(distinct.n)
    assert trace == distinct.trace
    assert distinct.total == trace[-1][1] and distinct.at == trace[distinct.k - 1][0]

    assert sopfr(1) == 0 and sopfr(12) == 7 and sopfr(8) == 6
    factors = _one("sopfr_row", "en", 8, "total", seed=4)
    trace = sopfr_trace(factors.n)
    assert trace == factors.trace
    assert factors.total == trace[-1][1] and factors.at == trace[factors.k - 1][0]

    pell, partner = pell_trace(5)
    assert pell == [0, 1, 2, 5, 12, 29] and partner == [1, 1, 3, 7, 17, 41]
    pell_task = _one("pell_row", "en", 8, "value", seed=4)
    left, right = pell_trace(pell_task.n)
    assert left == pell_task.pell and right == pell_task.partner
    assert pell_task.value == left[-1] and pell_task.other == right[-1]

    assert tribonacci_trace(6) == [0, 1, 1, 2, 4, 7, 13]
    triple = _one("tribonacci_row", "en", 8, "value", seed=4)
    trace = tribonacci_trace(triple.n)
    assert trace == triple.trace and triple.value == trace[-1] and triple.total == sum(trace)

    assert [item[2] for item in narayana_trace(5)] == [1, 10, 20, 10, 1]
    narayana = _one("narayana_row", "en", 8, "total", seed=4)
    trace = narayana_trace(narayana.n)
    assert trace == narayana.trace
    assert narayana.total == sum(item[2] for item in trace)
    assert narayana.entry == trace[narayana.k - 1][2]

    assert schroder_trace(5)[0] == [1, 2, 6, 22, 90, 394]
    schroder = _one("schroder_row", "en", 8, "value", seed=4)
    values, numerators = schroder_trace(schroder.n)
    assert values == schroder.values and numerators == schroder.numerators
    assert schroder.value == values[-1] and schroder.numer == numerators[-1]

    assert gauss_product(4, 2, 2) == 35
    assert gauss_rows(4, 2)[-1] == [1, 15, 35, 15, 1]
    gaussian = _one("gaussian_bin", "en", 8, "entry", seed=4)
    rows = gauss_rows(gaussian.n, gaussian.base)
    assert rows == gaussian.rows
    assert gaussian.entry == rows[-1][gaussian.k] and gaussian.total == sum(rows[-1])

    prefix = kolakoski_full(20)[:20]
    assert prefix[:10] == [1, 2, 2, 1, 1, 2, 1, 2, 2, 1]
    assert run_lengths(kolakoski_full(20)) == kolakoski_full(20)[:len(run_lengths(kolakoski_full(20)))]
    kolakoski = _one("kolakoski", "en", 8, "ones", seed=4)
    assert kolakoski.trace == kolakoski_full(kolakoski.n)[:kolakoski.n]
    assert kolakoski.ones == kolakoski.trace.count(1)
    assert kolakoski.symbol == kolakoski.trace[kolakoski.k - 1]

    assert cantor_pair(1, 2) == 8 and cantor_unpair(8) == (1, 2)
    assert cantor_fold([1, 2, 0]) == [8, 36]
    paired = _one("cantor_pair", "en", 8, "code", seed=4)
    trace = cantor_fold(paired.numbers)
    assert trace == paired.trace
    assert paired.code == trace[-1] and paired.part == trace[paired.k - 1]

    trace, known = horn_trace([(1, 1, 2), (2, 0, 3)])
    assert trace[-1][1] == 1 and known == {1, 2}
    horn = _one("horn_fire", "en", 8, "fired", seed=4)
    trace, known = horn_trace(horn.rules)
    assert trace == horn.trace and horn.fired == trace[-1][1]
    assert horn.holds == (1 if horn.k in known else 0)

    assert carry_trace([9], [1])[1:] == (10, 1)
    assert carry_trace([2, 9], [3, 0])[1:] == (95, 0)
    added = _one("carry_row", "en", 8, "sum", seed=4)
    trace, total, carries = carry_trace(added.left, added.right)
    assert trace == added.trace and added.sum == total and added.carries == carries

    assert lamp_trace(3, [2])[1] == [1, 1, 1]
    lamps = _one("lamp_trio", "en", 8, "ons", seed=4)
    trace, state = lamp_trace(lamps.n, lamps.presses)
    assert trace == lamps.trace and lamps.state == state
    assert lamps.ons == trace[-1][1] and lamps.bit == state[lamps.k - 1]

    assert parity_trace([[1, 0, 0, 0], [1, 1, 0, 0]]) == [(1, 1), (0, 1)]
    sheet = _one("parity_sheet", "en", 8, "odds", seed=4)
    trace = parity_trace(sheet.rows)
    assert trace == sheet.trace
    assert sheet.odds == trace[-1][1] and sheet.bit == trace[sheet.k - 1][0]

    assert mux_trace([1, 0]) == [1, 2]
    mux = _one("mux_index", "en", 8, "index", seed=4)
    trace = mux_trace(mux.bits)
    assert trace == mux.trace and mux.index == trace[-1]
    assert mux.value == mux.values[mux.index]

    trace, convict = jury_trace([1, 1, 0], 2, 3)
    assert trace[-1] == (2, 1) and convict == 0
    assert jury_trace([1, 1, 1], 2, 3)[1] == 1
    jury = _one("jury_veto", "en", 8, "convict", seed=4)
    trace, convict = jury_trace(jury.votes, jury.threshold, jury.veto)
    assert trace == jury.trace and jury.yes == trace[-1][0] and jury.convict == convict

    assert gate_trace(1, [2], [1]) == [0]
    folded = _one("gate_fold", "en", 8, "bit", seed=4)
    trace = gate_trace(folded.start, folded.ops, folded.bits)
    assert trace == folded.trace and folded.bit == trace[-1] and folded.highs == sum(trace)

    assert exact_trace([[1, 0, 0], [1, 1, 0]]) == [(1, 1), (0, 1)]
    groups = _one("exactly_one", "en", 8, "count", seed=4)
    trace = exact_trace(groups.groups)
    assert trace == groups.trace
    assert groups.count == trace[-1][1] and groups.hit == trace[groups.k - 1][0]

    assert knave_trace(1, [0, 0]) == [1, 0, 1]
    line = _one("knave_next", "en", 8, "knights", seed=4)
    kinds = knave_trace(line.first, line.claims)
    assert kinds == line.kinds and line.knights == sum(kinds)
    assert line.kind == kinds[line.k - 1]

    assert priority_trace([0, 0, 1])[-1] == (3, 2)
    assert priority_trace([0, 0])[-1] == (0, 2)
    assert priority_trace([1, 0])[-1] == (1, 0)
    priority = _one("priority_bit", "en", 8, "index", seed=4)
    trace = priority_trace(priority.bits)
    assert trace == priority.trace
    assert priority.index == trace[-1][0] and priority.zeros == trace[-1][1]

    assert interval_trace([(1, 3), (4, 6)])[-1] == (1, 6)
    assert interval_trace([(1, 2), (4, 5)])[-1] == (2, 4)
    merged = _one("interval_merge", "en", 8, "pieces", seed=4)
    trace = interval_trace(merged.intervals)
    assert trace == merged.trace
    assert merged.pieces == trace[-1][0] and merged.cover == trace[-1][1]

    trace, lengths = cycle_trace([0, 1, 2, 3])
    assert trace[-1][1] == 3 and lengths == [0, 1, 1, 1]
    cycled = _one("cycle_count", "en", 8, "cycles", seed=4)
    trace, lengths = cycle_trace(cycled.perm)
    assert trace == cycled.trace and cycled.cycles == trace[-1][1]
    assert cycled.length == lengths[cycled.k]

    assert stack_trace([1, 2, 3])[-1][3] == 1 and stack_trace([1, 2, 3])[-1][1] == 3
    assert stack_trace([3, 1, 2])[-1][3] == 0
    stacked = _one("stack_perm", "en", 8, "ok", seed=4)
    trace = stack_trace(stacked.target)
    assert trace == stacked.trace and stacked.ok == trace[-1][3] and stacked.pops == trace[-1][1]

    assert inversion_trace([3, 2, 1])[-1] == (0, 3)
    inverted = _one("inversion_row", "en", 8, "total", seed=4)
    trace = inversion_trace(inverted.values)
    assert trace == inverted.trace
    assert inverted.total == trace[-1][1] and inverted.here == trace[inverted.k - 1][0]

    trace, full = run_trace([1, 1, 1, 0])
    assert trace[-1][1] == 2 and full[1] == 3
    runs = _one("run_length", "en", 8, "runs", seed=4)
    trace, full = run_trace(runs.symbols)
    assert trace == runs.trace and runs.runs == trace[-1][1] and runs.span == full[runs.r]

    merged_values, trace = list_merge([1, 3, 5], [2, 4, 6])
    assert merged_values[2] == 3 and trace[2][2] == 2
    middle = _one("median_merge", "en", 8, "median", seed=4)
    values, trace = list_merge(middle.left, middle.right)
    assert values == middle.merged and trace == middle.trace
    assert middle.median == values[middle.n - 1] and middle.lefts == trace[middle.n - 1][2]

    assert len(diag_quads(5)) == 5 and len(diag_quads(6)) == 15
    diagonals = _one("diag_cross", "en", 8, "count", seed=4)
    quads = diag_quads(diagonals.vertices)
    assert quads == diagonals.quads and diagonals.count == len(quads)
    assert diagonals.top == quads[diagonals.k - 1][3]

    trace, corners = cross_trace(2, 3)
    assert len(trace) == 4 and corners == 1
    table = _one("billiard_cross", "en", 8, "squares", seed=4)
    trace, corners = cross_trace(table.width, table.height)
    assert trace == table.trace and table.squares == len(trace) and table.corners == corners

    assert pop_trace(4)[-1] == (1, 5)
    ones = _one("popcount_sum", "en", 8, "total", seed=4)
    trace = pop_trace(ones.n)
    assert trace == ones.trace and ones.total == trace[-1][1] and ones.bits == trace[ones.k - 1][0]

    assert rencontres_row(5) == [44, 45, 20, 10, 0, 1]
    fixed = _one("rencontres_row", "en", 8, "total", seed=4)
    row = rencontres_row(fixed.n)
    assert row == fixed.row and fixed.total == sum(row) and fixed.fixed == row[fixed.k]

    assert ballot_rows(4)[4] == [1, 4, 9, 14, 14]
    ballot = _one("ballot_tri", "en", 8, "catalan", seed=4)
    rows = ballot_rows(ballot.n)
    assert rows == ballot.rows and ballot.catalan == rows[-1][-1]
    assert ballot.entry == rows[-1][ballot.k]

    assert dedekind_psi(1) == 1 and dedekind_psi(6) == 12 and dedekind_psi(4) == 6
    psi = _one("dedekind_psi", "en", 8, "total", seed=4)
    trace = psi_trace(psi.n)
    assert trace == psi.trace and psi.total == trace[-1][1] and psi.at == trace[psi.k - 1][0]

    assert [jordan_two(i) for i in range(1, 7)] == [1, 3, 8, 12, 24, 24]
    jordan = _one("jordan_tot", "en", 8, "total", seed=4)
    assert jordan.at == jordan_two(jordan.k) and jordan.total == sum(jordan_two(i) for i in range(1, jordan.n + 1))

    assert sylvester_trace(4) == [2, 3, 7, 43, 1807]
    sylvester = _one("sylvester_row", "en", 8, "value", seed=4)
    trace = sylvester_trace(sylvester.n)
    assert trace == sylvester.trace and sylvester.value == trace[-1] and sylvester.prev == trace[-2]

    assert lucas_trace(6)[-1] == 18
    lucas = _one("lucas_row", "en", 8, "value", seed=4)
    trace = lucas_trace(lucas.n)
    assert trace == lucas.trace and lucas.value == trace[-1] and lucas.total == sum(trace)

    assert liouville(1) == 1 and liouville(4) == 1 and liouville(12) == -1
    assert liouville_trace(4)[-1] == (1, 0)
    signs = _one("liouville_row", "en", 8, "sum", seed=4)
    trace = liouville_trace(signs.n)
    assert trace == signs.trace and signs.sum == trace[-1][1] and signs.at == trace[signs.k - 1][0]

    assert necklace_trace(5)[-1] == 32
    beads = _one("necklace_count", "en", 8, "count", seed=4)
    trace = necklace_trace(beads.n)
    assert trace == beads.trace and beads.power == trace[-1]
    assert beads.count == (beads.power + (beads.n - 1) * 2) // beads.n

    assert [item[0] for item in hamming_trace(10)] == [1, 2, 3, 4, 5, 6, 8, 9, 10, 12]
    smooth = _one("hamming_smooth", "en", 8, "value", seed=4)
    trace = hamming_trace(smooth.n)
    assert trace == smooth.trace and smooth.value == trace[-1][0]
    assert smooth.total == sum(item[0] for item in trace)

    assert [item[1] for item in menage_trace(5)][-1] == 13
    assert menage_trace(3)[-1][1] == 1 and menage_trace(4)[-1][1] == 2
    seats = _one("menage_count", "en", 8, "value", seed=4)
    trace = menage_trace(seats.n)
    assert trace == seats.trace and seats.value == trace[-1][1] and seats.term == trace[seats.k][0]

    trace, champion, finalist = bracket_trace([1, 4, 2, 3])
    assert len(trace) == 3 and champion == 2 and finalist == 4
    bracket = _one("bracket_final", "en", 8, "champion", seed=4)
    trace, champion, finalist = bracket_trace(bracket.scores)
    assert trace == bracket.trace and bracket.champion == champion and bracket.finalist == finalist

    trace, values = unit_trace(1, [(1, 1, 2, 0), (2, 0, 3, 1)])
    assert values[1:] == [1, 0, 1]
    forced = _one("unit_prop", "en", 6, "bit", seed=4)
    trace, values = unit_trace(forced.start, forced.rules)
    assert trace == forced.trace and forced.bit == (2 if values[forced.k] is None else values[forced.k])

    assert gf2_trace([([], 1), ([0], 1), ([0, 1], 0)]) == [1, 0, 1]
    system = _one("gf2_solve", "en", 6, "weight", seed=4)
    assert gf2_trace(system.equations) == system.values and system.weight == sum(system.values)

    clauses, derived = resolution_trace(3, True)
    assert derived[-1] == [] and resolve([1], [-1, 2], 1) == [2]
    clauses, derived = resolution_trace(3, False)
    assert derived[-1] == [4]
    proof = _one("resolve_proof", "en", 6, "empty", seed=4)
    _clauses, derived = resolution_trace(proof.n, bool(proof.cancel))
    assert derived == proof.derived and proof.empty == (1 if not derived[-1] else 0)

    assert eq_trace(2, [(1, 2, 0), (1, 2, 1)])[-1] == (0, 2)
    assert eq_trace(2, [(1, 1, 0), (1, 2, 1)])[-1][0] == 1
    equal = _one("bool_eq", "en", 6, "ok", seed=4)
    trace = eq_trace(equal.n, equal.constraints)
    assert trace == equal.trace and equal.ok == trace[-1][0] and equal.broke == trace[-1][1]

    assert check_trace([[1, -2], [-1]], [0, 1, 0])[0][0] == 1
    assert check_trace([[-1]], [0, 1])[-1][2] == 1
    checked = _one("assign_check", "en", 6, "sat", seed=4)
    trace = check_trace(checked.clauses, checked.bits)
    assert trace == checked.trace and checked.sat == trace[-1][1] and checked.fail == trace[-1][2]

    assert pigeon_trace(2, [1, 2, 1])[-1][0] == 1
    birds = _one("pigeon_place", "en", 6, "hole", seed=4)
    trace = pigeon_trace(birds.holes, birds.places)
    assert trace == birds.trace and birds.hole == trace[-1][0] and birds.load == trace[-1][2]

    assert box_trace([0, 1, 0]) == [(1, 1), (0, 1), (1, 2)]
    worlds = _one("kripke_box", "en", 6, "boxes", seed=4)
    trace = box_trace(worlds.bits)
    assert trace == worlds.trace and worlds.boxes == trace[-1][1] and worlds.here == trace[worlds.k - 1][0]

    assert all_trace([1, 1, 0, 1]) == [(1, 1), (2, 2), (2, 2), (2, 3)]
    chain = _one("all_are", "en", 6, "far", seed=4)
    trace = all_trace(chain.links)
    assert trace == chain.trace and chain.far == trace[-1][0] and chain.opened == trace[-1][1]

    assert clash_trace([1, 2, -1])[-1] == (3, 1)
    assert clash_trace([1, 1, 2])[-1] == (0, 0)
    clash = _one("literal_clash", "en", 6, "at", seed=4)
    trace = clash_trace(clash.literals)
    assert trace == clash.trace and clash.at == trace[-1][0] and clash.var == trace[-1][1]

    assert until_trace([1, 1, 0], [0, 1, 0]) == [(1, 1), (1, 2), (0, 2)]
    timed = _one("until_line", "en", 6, "count", seed=4)
    trace = until_trace(timed.hold, timed.stop)
    assert trace == timed.trace and timed.count == trace[-1][1] and timed.here == trace[timed.k - 1][0]

    assert ground_trace([[], [1], [1]]) == [(1, 1), (0, 1), (0, 1)]
    assert grounded_labels([[], [], [2]])[1:] == [1, 1, 0]
    argued = _one("dung_ground", "en", 6, "inside", seed=4)
    trace = ground_trace(argued.attacks)
    assert trace == argued.trace and argued.inside == trace[-1][1]
    assert grounded_labels(argued.attacks)[argued.k] == argued.here

    assert causal_values(1, [(1, 1, 0)], 1, 0)[1:] == [0, 1]
    assert causal_values(1, [(1, 1, 0)], 0, 0)[1:] == [1, 0]
    caused = _one("causal_do", "en", 6, "shift", seed=4)
    trace = causal_pair(caused.start, caused.rules, caused.cut, caused.bit)
    assert trace == caused.trace and caused.shift == trace[-1][2] and caused.after == trace[caused.k - 1][1]

    assert lukas_apply(4, 0, 4, 4) == 4
    assert lukas_apply(3, 1, 3, 4) == 4
    assert lukas_apply(4, 2, 0, 4) == 0
    assert lukas_trace(4, [(2, 0), (0, 4)], 4) == [(0, 1), (0, 2)]
    folded = _one("lukas_fold", "en", 6, "degree", seed=4)
    trace = lukas_trace(folded.start, folded.ops, folded.bound)
    assert trace == folded.trace and folded.degree == trace[-1][0] and folded.zeros == trace[-1][1]

    trace, premise, stated, clash = doctrine_result([(1, 1), (1, 0), (0, 1)])
    assert premise == 1 and stated == 0 and clash == 1
    judges = _one("doctrinal", "en", 6, "premise", seed=4)
    trace, premise, stated, clash = doctrine_result(judges.votes)
    assert trace == judges.trace and judges.premise == premise and judges.clash == clash

    assert knows_trace([1, 0], [0]) == [(1, 1), (0, 1)]
    assert knows_trace([1, 0], [1]) == [(0, 0), (0, 0)]
    assert knows_trace([1, 1], [1]) == [(1, 1), (1, 2)]
    agent = _one("knows_line", "en", 6, "known", seed=4)
    trace = knows_trace(agent.bits, agent.doors)
    assert trace == agent.trace and agent.known == trace[-1][1] and agent.here == trace[agent.k - 1][0]

    assert rough_trace([(1, 0, 1), (1, 0, 0)])[-1][2:] == (0, 2)
    assert rough_trace([(1, 0, 1), (1, 0, 1)])[-1][2:] == (2, 2)
    assert rough_trace([(1, 0, 0), (0, 1, 1)])[-1][2:] == (1, 1)
    approx = _one("rough_set", "en", 6, "lower", seed=4)
    trace = rough_trace(approx.rows)
    assert trace == approx.trace and approx.lower == trace[-1][2] and approx.upper == trace[-1][3]

    trace, values = naf_trace(1, [(0, 1), (2, 0)])
    assert values[1:] == [1, 0, 0]
    trace, values = naf_trace(0, [(0, 1)])
    assert values[1:] == [0, 1]
    reduct_matches(0, [(0, 1)], values)
    program = _one("naf_fire", "en", 6, "trues", seed=4)
    trace, values = naf_trace(program.fact, program.rules)
    assert trace == program.trace and program.trues == trace[-1][1] and program.here == values[program.k]

    pairs = [(1, 2, 1), (1, 3, 3), (2, 3, 2)]
    assert agenda_trace([1, 2, 3], pairs)[-1][2:] == (3, 1)
    ballot = _one("agenda_vote", "en", 6, "winner", seed=4)
    trace = agenda_trace(ballot.agenda, ballot.pairs)
    assert trace == ballot.trace and ballot.winner == trace[-1][2] and ballot.changes == trace[-1][3]

    assert ctc_trace([1, 1, 0, 1]) == [(1, 1), (1, 1), (1, 1), (2, 1)]
    assert ctc_trace([0, 0]) == [(0, 0), (0, 0)]
    collapsed = _one("ctc_collapse", "en", 6, "length", seed=4)
    trace = ctc_trace(collapsed.labels)
    assert trace == collapsed.trace and collapsed.length == trace[-1][0] and collapsed.last == trace[-1][1]

    assert relu_trace(1, [(0, 2), (1, 0)]) == [(2, 2, 0), (2, 2, 0)]
    assert relu_trace(3, [(-1, 0)]) == [(-3, 0, 0)]
    gated = _one("relu_chain", "en", 6, "final", seed=4)
    trace = relu_trace(gated.start, gated.layers)
    assert trace == gated.trace and gated.final == trace[-1][1] and gated.factor == trace[-1][2]

    assert prefix_choice([2, 2, 1]) == [(1, 2, 0), (1, 2, 1), (1, 2, 2)]
    picked = _one("causal_pick", "en", 6, "chosen", seed=4)
    trace = prefix_choice(picked.scores)
    assert trace == picked.trace and picked.chosen == trace[-1][0] and picked.look == trace[-1][2]

    assert triplet_trace([(0, 1, 5), (0, 2, 1)]) == [(4, 0, 4), (-1, 1, -1)]
    triples = _one("triplet_gap", "en", 6, "bad", seed=4)
    trace = triplet_trace(triples.rows)
    assert trace == triples.trace and triples.bad == trace[-1][1] and triples.worst == trace[-1][2]

    assert keep_trace([(1, 3), (0, 2)]) == [(3, 1, 1), (5, 3, 1)]
    beam = _one("beam_keep", "en", 6, "best", seed=4)
    trace = keep_trace(beam.rows)
    assert trace == beam.trace and beam.best == trace[-1][0] and beam.token == trace[-1][2]

    assert hindsight_trace([1, 2, 1], 2) == [(0, 1), (1, 1), (1, 2)]
    revised = _one("hindsight_hit", "en", 6, "revised", seed=4)
    trace = hindsight_trace(revised.states, revised.goal)
    assert trace == revised.trace and revised.original == trace[-1][0] and revised.revised == trace[-1][1]

    assert legal_trace([(2, 9, 1, 0), (1, 4, 1, 1), (3, 3, 1, 1)]) == [(0, 0), (1, 1), (0, 1)]
    masked = _one("legal_greedy", "en", 6, "total", seed=4)
    trace = legal_trace(masked.rows)
    assert trace == masked.trace and masked.total == trace[-1][1] and masked.last == trace[-1][0]

    assert machine_trace([1, 2, 0, 1]) == [(1, 0, 0), (2, 4, 4), (2, 1, 5), (2, 1, 6)]
    machine = _one("reward_machine", "en", 6, "reward", seed=4)
    trace = machine_trace(machine.events)
    assert trace == machine.trace and machine.reward == trace[-1][2] and machine.phase == trace[-1][0]

    assert cut_trace([1, 2, 2], [3, -1, 4], 2) == [(3, 3, 0), (2, 2, 2), (2, 6, 2)]
    episode = _one("episode_cut", "en", 6, "kept", seed=4)
    trace = cut_trace(episode.states, episode.rewards, episode.goal)
    assert trace == episode.trace and episode.kept == trace[-1][0] and episode.stop == trace[-1][2]

    agent = ((1, 0), (0, 2))
    opponent = ((0, 1), (2, 0))
    assert reply_trace(agent, opponent, 0, 2) == [(0, 1, 1, 1), (1, 2, 0, 3)]
    replies = _one("best_reply", "en", 6, "total", seed=4)
    trace = reply_trace(replies.agent, replies.opponent, replies.opp, replies.n)
    assert trace == replies.trace and replies.total == trace[-1][3] and replies.action == trace[-1][0]

    assert draft_trace([(1, 1), (1, 0), (0, 0)]) == [(1, 0), (1, 2), (1, 2)]
    assert draft_trace([(1, 1), (2, 2)])[-1] == (2, 0)
    drafted = _one("draft_accept", "en", 6, "taken", seed=4)
    trace = draft_trace(drafted.pairs)
    assert trace == drafted.trace and drafted.taken == trace[-1][0] and drafted.at == trace[-1][1]

    assert score_gap([(5, 1, 0, 0), (1, 3, 4, 0)]) == [(4, 0, 4), (-3, 1, -3)]
    margins = _one("class_margin", "en", 6, "bad", seed=4)
    trace = score_gap(margins.rows)
    assert trace == margins.trace and margins.bad == trace[-1][1] and margins.worst == trace[-1][2]

    assert bin_trace([(1, 1), (2, 0), (1, 0)], 1) == [(1, 0), (1, 0), (1, 1)]
    binned = _one("bin_tally", "en", 6, "correct", seed=4)
    trace = bin_trace(binned.rows, binned.bucket)
    assert trace == binned.trace and binned.correct == trace[-1][0] and binned.wrong == trace[-1][1]

    assert accum_trace(0, [1, 2, 3, 4]) == [(0, 0, 1), (3, -3, 0), (0, -3, 3), (7, -10, 0)]
    accumulated = _one("grad_accum", "en", 6, "weight", seed=4)
    trace = accum_trace(accumulated.start, accumulated.grads)
    assert trace == accumulated.trace and accumulated.weight == trace[-1][1] and accumulated.pair == trace[-1][0]

    assert skip_trace(2, [(1, 3), (0, 5), (1, -1)]) == [(5, 1), (5, 1), (4, 2)]
    skipped = _one("skip_add", "en", 6, "value", seed=4)
    trace = skip_trace(skipped.start, skipped.steps)
    assert trace == skipped.trace and skipped.value == trace[-1][0] and skipped.opens == trace[-1][1]

    assert arm_trace([(1, 1), (1, 0), (2, 1)]) == [(1, 1, 0, 1, 0), (1, 1, 0, 2, 0), (2, 1, 1, 2, 1)]
    arms = _one("arm_rate", "en", 6, "leader", seed=4)
    trace = arm_trace(arms.pulls)
    assert trace == arms.trace and arms.leader == trace[-1][0] and arms.hits == trace[-1][1]

    assert budget_trace(1, [1, 1, 0]) == [(1, 0, 0), (1, 0, 1), (1, 0, 1)]
    spent = _one("budget_step", "en", 6, "place", seed=4)
    trace = budget_trace(spent.budget, spent.actions)
    assert trace == spent.trace and spent.place == trace[-1][0] and spent.blocked == trace[-1][2]

    assert boot_trace([(2, 5, 0), (1, 9, 1)]) == [(7, 7, 0), (1, 8, 1)]
    booted = _one("done_boot", "en", 6, "total", seed=4)
    trace = boot_trace(booted.rows)
    assert trace == booted.trace and booted.total == trace[-1][1] and booted.terminals == trace[-1][2]

    assert gap_trace([(4, 1), (2, 2)]) == [(3, 3, 0), (0, 3, 1)]
    gaps = _one("greedy_gap", "en", 6, "total", seed=4)
    trace = gap_trace(gaps.rows)
    assert trace == gaps.trace and gaps.total == trace[-1][1] and gaps.ties == trace[-1][2]

    assert switch_trace([3, 1, 4], [0, 0, 1]) == [(0, 3, 3), (0, 4, 4), (1, 8, 7)]
    switched = _one("switch_cost", "en", 6, "net", seed=4)
    trace = switch_trace(switched.rewards, switched.actions)
    assert trace == switched.trace and switched.net == trace[-1][2] and switched.switches == trace[-1][0]

    assert short_trace(0, [(0, 1), (1, 1)]) == [(0, 1), (0, 1), (1, 2)]
    assert short_trace(1, [(1, 0)]) == [(1, 1), (1, 1)]
    gated = _one("short_circuit", "en", 6, "value", seed=4)
    trace = short_trace(gated.start, gated.steps)
    assert trace == gated.trace and gated.value == trace[-1][0] and gated.reads == trace[-1][1]

    assert ref_trace([1, -1, -1, -1]) == [(2, 0), (1, 0), (0, 1), (0, 1)]
    refs = _one("ref_count", "en", 6, "count", seed=4)
    trace = ref_trace(refs.events)
    assert trace == refs.trace and refs.count == trace[-1][0] and refs.frees == trace[-1][1]

    assert wrap_trace(3, [1, 1, 1]) == [(1, 0), (2, 0), (0, 1)]
    ring = _one("wrap_index", "en", 6, "index", seed=4)
    trace = wrap_trace(ring.n, ring.steps)
    assert trace == ring.trace and ring.index == trace[-1][0] and ring.visits == trace[-1][1]

    assert bit_trace(3, [(3, 0), (0, 7), (2, 6)]) == [(6, 2), (6, 2), (0, 0)]
    program = _one("bit_prog", "en", 6, "reg", seed=4)
    trace = bit_trace(program.start, program.ops)
    assert trace == program.trace and program.reg == trace[-1][0] and program.ones == trace[-1][1]

    assert break_trace([(4, 0), (5, 1), (6, 0)]) == [(4, 0), (4, 2), (4, 2)]
    broken = _one("break_sum", "en", 6, "total", seed=4)
    trace = break_trace(broken.rows)
    assert trace == broken.trace and broken.total == trace[-1][0] and broken.stop == trace[-1][1]

    assert bounds_trace(3, [1, 1, 1]) == [(1, 0), (2, 0), (2, 1)]
    bounded = _one("bounds_step", "en", 6, "index", seed=4)
    trace = bounds_trace(bounded.n, bounded.steps)
    assert trace == bounded.trace and bounded.index == trace[-1][0] and bounded.faults == trace[-1][1]

    assert reg_trace(1, 2, -1, [0, 1, 2]) == [(2, 1, 1), (3, 1, 1), (3, 0, 1)]
    regs = _one("reg_swap", "en", 6, "left", seed=4)
    trace = reg_trace(regs.left, regs.right, regs.extra, regs.ops)
    assert trace == regs.trace and regs.final_left == trace[-1][0] and regs.swaps == trace[-1][2]

    assert elif_trace([(0, 5), (1, 3), (1, 9)]) == [(0, 0), (3, 2), (3, 2)]
    chosen = _one("elif_pick", "en", 6, "value", seed=4)
    trace = elif_trace(chosen.branches)
    assert trace == chosen.trace and chosen.value == trace[-1][0] and chosen.at == trace[-1][1]

    assert post_trace(3, [0, 1, 0]) == [(4, 3), (5, 8), (6, 13)]
    posted = _one("post_inc", "en", 6, "value", seed=4)
    trace = post_trace(posted.start, posted.ops)
    assert trace == posted.trace and posted.value == trace[-1][0] and posted.used == trace[-1][1]

    assert stack_min([(0, 3), (0, 1), (1, 0), (1, 0)]) == [(3, 0), (1, 0), (3, 1), (0, 4)]
    held = _one("min_hold", "en", 6, "low", seed=4)
    trace = stack_min(held.ops)
    assert trace == held.trace and held.low == trace[-1][0] and held.popped == trace[-1][1]

    assert jump_trace([(0, 2), (1, 2), (0, 5), (0, 1)]) == [(2, 1), (2, 2), (2, 2), (3, 3)]
    jumped = _one("jump_add", "en", 6, "acc", seed=4)
    trace = jump_trace(jumped.ops)
    assert trace == jumped.trace and jumped.acc == trace[-1][0] and jumped.ran == trace[-1][1]

    assert div_trace(17, [3, 2]) == [(5, 2), (2, 3)]
    divided = _one("div_chain", "en", 6, "quot", seed=4)
    trace = div_trace(divided.start, divided.divisors)
    assert trace == divided.trace and divided.quot == trace[-1][0] and divided.rems == trace[-1][1]

    assert clamp_trace(1, 3, [4, -5, 1]) == [(3, 1), (0, 2), (1, 2)]
    clamped = _one("clamp_add", "en", 6, "value", seed=4)
    trace = clamp_trace(clamped.start, clamped.n, clamped.deltas)
    assert trace == clamped.trace and clamped.value == trace[-1][0] and clamped.clips == trace[-1][1]

    assert ptr_trace([1, 2, 0]) == [(1, 0), (2, 0), (0, 1)]
    walked = _one("ptr_walk", "en", 6, "land", seed=4)
    trace = ptr_trace(walked.nxt)
    assert trace == walked.trace and walked.land == trace[-1][0] and walked.zeros == trace[-1][1]

    assert cont_trace([(4, 0), (5, 1), (6, 0)]) == [(4, 1), (4, 1), (10, 2)]
    continued = _one("continue_sum", "en", 6, "total", seed=4)
    trace = cont_trace(continued.rows)
    assert trace == continued.trace and continued.total == trace[-1][0] and continued.kept == trace[-1][1]

    assert delay_trace([4, 5, 6, 7]) == [(0, 0), (0, 0), (4, 4), (5, 9)]
    delayed = _one("delay_line", "en", 6, "out", seed=4)
    trace = delay_trace(delayed.values)
    assert trace == delayed.trace and delayed.out == trace[-1][0] and delayed.total == trace[-1][1]

    assert case_trace(2, [(1, 5), (2, 7), (2, 9)], 0) == [(0, 0), (7, 2), (7, 2)]
    picked = _one("switch_case", "en", 6, "chosen", seed=4)
    trace = case_trace(picked.value, picked.rows, picked.default)
    assert trace == picked.trace and picked.chosen == trace[-1][0] and picked.at == trace[-1][1]

    assert scan_trace([1, 2, -1, 4]) == [(1, 1, 0), (12, 2, 0), (12, 2, 3), (12, 2, 3)]
    scanned = _one("digit_scan", "en", 6, "value", seed=4)
    trace = scan_trace(scanned.tokens)
    assert trace == scanned.trace and scanned.value == trace[-1][0] and scanned.length == trace[-1][1]

    assert rot_trace(1, [1, 1]) == [(2, 1), (4, 2)]
    assert rot_trace(9, [1]) == [(3, 1)]
    rotated = _one("rot_nibble", "en", 6, "value", seed=4)
    trace = rot_trace(rotated.start, rotated.shifts)
    assert trace == rotated.trace and rotated.value == trace[-1][0] and rotated.changed == trace[-1][1]

    assert buf_trace([(0, 3), (0, 2), (1, 4), (1, 1)]) == [(3, 3), (5, 5), (1, 5), (0, 5)]
    buffer = _one("buf_len", "en", 6, "length", seed=4)
    trace = buf_trace(buffer.ops)
    assert trace == buffer.trace and buffer.length == trace[-1][0] and buffer.peak == trace[-1][1]

    assert cmp_trace(4, [(5, 1, 10), (3, 2, -1)]) == [(5, 1), (4, 1)]
    branched = _one("cmp_branch", "en", 6, "value", seed=4)
    trace = cmp_trace(branched.start, branched.steps)
    assert trace == branched.trace and branched.value == trace[-1][0] and branched.lows == trace[-1][1]

    assert bitset_trace([(1, 0), (1, 0), (0, 0), (1, 1)]) == [(1, 1), (1, 1), (0, 1), (2, 2)]
    bits = _one("bit_set", "en", 6, "mask", seed=4)
    trace = bitset_trace(bits.ops)
    assert trace == bits.trace and bits.mask == trace[-1][0] and bits.news == trace[-1][1]

    assert write_trace(3, [(1, 4), (0, 2), (1, 7)], 1) == [(4, 4), (4, 6), (7, 9)]
    cells = _one("cell_write", "en", 6, "cell", seed=4)
    trace = write_trace(cells.n, cells.writes, cells.query)
    assert trace == cells.trace and cells.cell == trace[-1][0] and cells.total == trace[-1][1]

    assert lcg_trace(3, [(2, 1), (3, 0)]) == [(7, 0), (1, 0)]
    generated = _one("lcg_step", "en", 6, "value", seed=4)
    trace = lcg_trace(generated.start, generated.steps)
    assert trace == generated.trace and generated.value == trace[-1][0] and generated.zeros == trace[-1][1]

    assert queue_trace([(0, 4), (0, 5), (1, 0), (1, 0), (1, 0)]) == [
        (0, 0, 0), (0, 0, 0), (4, 4, 1), (5, 9, 1), (0, 9, 1),
    ]
    queued = _one("two_stack", "en", 6, "got", seed=4)
    trace = queue_trace(queued.ops)
    assert trace == queued.trace and queued.got == trace[-1][1] and queued.pours == trace[-1][2]

    assert rank_trace([3, 1, 3]) == [(1, 3), (1, 3), (3, 3)]
    inserted = _one("sorted_insert", "en", 6, "rank", seed=4)
    trace = rank_trace(inserted.values)
    assert trace == inserted.trace and inserted.rank == trace[-1][0] and inserted.max == trace[-1][1]

    trace, left_open = brace_trace([0, 2, 1])
    assert trace == [(1, 0), (2, 0), (2, 1)] and left_open == 2
    braces = _one("brace_pair", "en", 6, "errors", seed=4)
    trace, left_open = brace_trace(braces.tokens)
    assert trace == braces.trace and braces.errors == trace[-1][1] and braces.open == left_open

    assert probe_trace(4, [1, 5, 2]) == [(1, 1), (2, 3), (3, 5)]
    probed = _one("hash_probe", "en", 6, "slot", seed=4)
    trace = probe_trace(probed.n, probed.keys)
    assert trace == probed.trace and probed.slot == trace[-1][0] and probed.probes == trace[-1][1]

    assert part_trace([3, 1, 4, 1], 3) == [(0, 1), (1, 1), (1, 1), (2, 1)]
    parts = _one("part_count", "en", 6, "left", seed=4)
    trace = part_trace(parts.values, parts.pivot)
    assert trace == parts.trace and parts.left == trace[-1][0] and parts.equal == trace[-1][1]

    assert fill_trace([0, 4, 0, 0, 2]) == [(0, 0, 0), (4, 4, 0), (4, 8, 1), (4, 12, 2), (2, 14, 2)]
    filled = _one("fill_forward", "en", 6, "total", seed=4)
    trace = fill_trace(filled.values)
    assert trace == filled.trace and filled.total == trace[-1][1] and filled.replaced == trace[-1][2]

    assert xor_trace([3, 1, 2]) == [(3, 0), (2, 0), (0, 1)]
    folded = _one("xor_fold", "en", 6, "acc", seed=4)
    trace = xor_trace(folded.values)
    assert trace == folded.trace and folded.acc == trace[-1][0] and folded.zeros == trace[-1][1]

    assert bubble_trace([3, 1, 2]) == [(1, 1), (2, 1)]
    bubbled = _one("bubble_pass", "en", 6, "swaps", seed=4)
    trace = bubble_trace(bubbled.values)
    assert trace == bubbled.trace and bubbled.swaps == trace[-1][0] and bubbled.first == trace[-1][1]

    assert mtf_trace(3, [2, 2, 0]) == [(2, 2), (0, 2), (1, 3)]
    moved = _one("mtf_list", "en", 6, "cost", seed=4)
    trace = mtf_trace(moved.n, moved.queries)
    assert trace == moved.trace and moved.cost == trace[-1][1] and moved.place == trace[-1][0]

    assert stile_trace([0, 1, 1, 0, 1]) == [(1, 0), (0, 1), (0, 1), (1, 1), (0, 2)]
    gate = _one("turnstile", "en", 6, "entries", seed=4)
    trace = stile_trace(gate.events)
    assert trace == gate.trace and gate.entries == trace[-1][1] and gate.state == trace[-1][0]

    assert ham_trace([1, 3, 0]) == [(1, 1, 1), (2, 3, 2)]
    bits = _one("hamming_step", "en", 6, "total", seed=4)
    trace = ham_trace(bits.values)
    assert trace == bits.trace and bits.total == trace[-1][1] and bits.peak == trace[-1][2]

    assert index_trace(4, [5, 0, 7]) == [(1, 1, 1), (0, 0, 1), (1, 3, 4)]
    grid = _one("row_major", "en", 6, "row", seed=4)
    trace = index_trace(grid.n, grid.indices)
    assert trace == grid.trace and grid.row == trace[-1][0] and grid.cols == trace[-1][2]

    assert link_trace(4, [(0, 1), (1, 2), (0, 2)]) == [(3, 1), (2, 2), (2, 2)]
    linked = _one("union_count", "en", 6, "parts", seed=4)
    trace = link_trace(linked.n, linked.pairs)
    assert trace == linked.trace and linked.parts == trace[-1][0] and linked.joined == trace[-1][1]

    assert trie_trace([(0, 1), (0, 1), (1, 0)]) == [(2, 1), (2, 1), (4, 2)]
    tree = _one("trie_node", "en", 6, "nodes", seed=4)
    trace = trie_trace(tree.words)
    assert trace == tree.trace and tree.nodes == trace[-1][0] and tree.fresh == trace[-1][1]

    assert minute_trace(1, 50, [20, 70]) == [(10, 2, 1), (20, 3, 2)]
    clock = _one("minute_add", "en", 6, "minute", seed=4)
    trace = minute_trace(clock.hour, clock.minute, clock.adds)
    assert trace == clock.trace and clock.final_minute == trace[-1][0] and clock.carries == trace[-1][2]

    assert mod_ops(4, [(0, 8), (1, 3), (2, 3)]) == [(2, 0), (9, 0), (7, 0)]
    reduced = _one("mod_accum", "en", 6, "value", seed=4)
    trace = mod_ops(reduced.start, reduced.ops)
    assert trace == reduced.trace and reduced.value == trace[-1][0] and reduced.zeros == trace[-1][1]

    nfa_trans = [[(1, 2), (0,)], [(1,), (0, 2)], [(2,), (1,)]]
    assert nfa_trace(nfa_trans, [2], [0, 1]) == [(2, 1, 1), (3, 1, 2)]
    branched = _one("nfa_run", "en", 6, "visits", seed=4)
    trace = nfa_trace(branched.trans, branched.accept, branched.word)
    assert trace == branched.trace and branched.visits == trace[-1][2] and branched.hit == trace[-1][1]

    assert moore_trace([2, 0, 4], [[1, 0], [1, 2], [0, 2]], [0, 1]) == [(1, 0, 2), (2, 4, 6)]
    printed = _one("moore_run", "en", 6, "total", seed=4)
    trace = moore_trace(printed.outputs, printed.trans, printed.word)
    assert trace == printed.trace and printed.total == trace[-1][2] and printed.last == trace[-1][1]

    assert image_trace([[1, 0], [1, 2], [1, 0]], [1, 0]) == [(2, 0), (1, 1)]
    glued = _one("sync_run", "en", 6, "left", seed=4)
    trace = image_trace(glued.trans, glued.word)
    assert trace == glued.trace and glued.left == trace[-1][0] and glued.synced == trace[-1][1]

    assert meet_trace([[1, 0], [1, 0]], [1], [[1, 0], [0, 1]], [1], [0, 1]) == [(1, 1, 1, 1), (0, 1, 1, 0)]
    paired = _one("meet_run", "en", 6, "both", seed=4)
    trace = meet_trace(paired.trans_a, paired.accept_a, paired.trans_b, paired.accept_b, paired.word)
    assert trace == paired.trace and paired.both == trace[-1][2] and paired.at_end == trace[-1][3]

    assert lfsr_trace([1, 0, 1], [0, 2]) == [(1, 1, 2), (0, 1, 4), (1, 2, 1)]
    shifted = _one("lfsr_run", "en", 6, "ones", seed=4)
    trace = lfsr_trace(shifted.bits, shifted.taps)
    assert trace == shifted.trace and shifted.ones == trace[-1][1] and shifted.reg == trace[-1][2]

    assert crc_trace([1, 1, 0, 1, 1], 5) == [(1, 0), (3, 0), (6, 0), (13, 0), (14, 1)]
    summed = _one("crc_rem", "en", 6, "rem", seed=4)
    trace = crc_trace(summed.bits, summed.mask)
    assert trace == summed.trace and summed.rem == trace[-1][0] and summed.xors == trace[-1][1]

    assert feistel_trace(3, 1, [2, 1]) == [(1, 0), (0, 0)]
    rounds = _one("feistel_run", "en", 6, "left", seed=4)
    trace = feistel_trace(rounds.left, rounds.right, rounds.keys)
    assert trace == rounds.trace and rounds.final_left == trace[-1][0] and rounds.pack == trace[-1][0] * 16 + trace[-1][1]

    assert elgamal_trace(3, 5, 7, [1, 0], 17) == [(3, 1), (9, 5)]
    hidden = _one("elgamal_enc", "en", 6, "hint", seed=4)
    trace = elgamal_trace(hidden.base, hidden.public, hidden.message, hidden.bits, hidden.prime)
    assert trace == hidden.trace and hidden.hint == trace[-1][0] and hidden.mask == trace[-1][1]
