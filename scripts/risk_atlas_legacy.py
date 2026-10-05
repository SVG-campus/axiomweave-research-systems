"""Frozen legacy synthetic gate only. No performance or physical-mechanism claim."""
import math
SENSOR_TYPES = {'z_score': 'number', 'perp_vel_30s': 'number', 'quantum_optomechanical_decoherence': 'boolean', 'merkle_solvency_inconsistent': 'boolean', 'snn_synaptic_backpressure_flag': 'boolean', 'utc_hour': 'number', 'coalescing_eigenstate_loss_flag': 'boolean', 'multi_exchange_collateral_shred_flag': 'boolean', 'chern_number_inversion_flag': 'boolean', 'homeostatic_plasticity_breakdown_flag': 'boolean', 'neural_sde_diverged': 'boolean', 'verilog_ams_synthesis_glitch': 'boolean', 'pbs_proposer_inversion_risk': 'boolean', 'cross_margin_haircut_shock': 'boolean', 'subtick_strike_distance_bps': 'number', 'price_velocity_60s_sigma': 'number', 'validator_reorg_delay': 'boolean', 'exchange_circuit_breaker': 'boolean', 'l2_resting_contracts': 'number', 'spread_cents': 'number', 'kalman_mean_rev_theta': 'number', 'tradfi_pinning': 'boolean', 'basis_bps': 'number', 'macro_trend': 'number', 'is_shock': 'boolean', 'order_budget_dollars': 'number', 'iceberg_replenish_rate': 'number', 'cross_venue_aggregated_depth': 'number', 'drl_dynamic_kelly_lambda': 'number', 'optical_phase_slip_fs': 'number', 'sfq_thermal_quench_flag': 'boolean', 'stark_recursion_soundness_split': 'boolean', 'multiprover_arbitration_delay_ms': 'number', 'rough_bergomi_hurst': 'number', 'f_vecm_cointegration_break': 'boolean', 'anyon_braiding_noise_flag': 'boolean', 'fqhe_edge_break_flag': 'boolean', 'topological_qubit_quench': 'boolean', 'gpd_tail_explosion_flag': 'boolean', 'extreme_mae_shock_flag': 'boolean', 'ricci_curvature_singularity': 'boolean', 'complex_network_percolation': 'boolean', 'ultrametric_partition_flag': 'boolean', 'rsa_sluggishness_flag': 'boolean', 'zk_timed_deadlock_flag': 'boolean', 'snark_prover_race_flag': 'boolean', 'photonic_reservoir_saturated': 'boolean', 'microring_bistability_flag': 'boolean', 'mzi_dispersion_flag': 'boolean', 'frequency_comb_drift_flag': 'boolean', 'waveguide_phase_break_flag': 'boolean', 'inter_dc_sync_shock_flag': 'boolean', 'lorentz_dilation_drift_flag': 'boolean', 'hyperdimensional_singularity_flag': 'boolean', 'concurrent_count': 'number', 'pt_symmetry_breaking_flag': 'boolean', 'voronoi_partition_shock': 'boolean', 'delaunay_congestion_flag': 'boolean', 'spatial_anisotropy_flag': 'boolean', 'volterra_kernel_persistence_flag': 'boolean', 'riemann_liouville_singular_flag': 'boolean', 'multiscale_roughness_inversion_flag': 'boolean', 'bsm_fidelity_drop_flag': 'boolean', 'teleportation_noise_flag': 'boolean', 'nonlocal_correlation_collapse_flag': 'boolean', 'hjb_viscosity_blowup_flag': 'boolean', 'nonlinear_drift_control_singularity_flag': 'boolean', 'feynman_kac_dispersion_flag': 'boolean', 'sagnac_orbital_offset_flag': 'boolean', 'cosmic_ray_seu_bitflip_flag': 'boolean', 'total_cosmic_collapse_flag': 'boolean', 'singular_volterra_kernel_flag': 'boolean', 'fractional_bridge_drift_flag': 'boolean', 'non_markovian_jump_cluster_flag': 'boolean', 'braid_invariance_rupture_flag': 'boolean', 'topological_knot_deadlock_flag': 'boolean', 'ricci_singularity_flag': 'boolean', 'manifold_tear_flag': 'boolean', 'lob_volume_evaporation_flag': 'boolean', 'kerr_metric_shock_flag': 'boolean', 'fiber_birefringence_flag': 'boolean', 'relativistic_arbitration_lock_flag': 'boolean', 'memristor_conductance_drift_flag': 'boolean', 'sneak_path_leakage_flag': 'boolean', 'analog_thermal_quench_flag': 'boolean', 'pedersen_blinding_breach_flag': 'boolean', 'garbled_circuit_collusion_flag': 'boolean', 'total_multiverse_entropy_flag': 'boolean', 'radiation_pressure_shock_flag': 'boolean', 'nanocavity_thermal_runaway_flag': 'boolean', 'optomechanical_ep_annihilation_flag': 'boolean', 'chiral_edge_scattering_flag': 'boolean', 'quasiparticle_dissipation_flag': 'boolean', 'shrinking_soliton_shock_flag': 'boolean', 'metric_tensor_anisotropy_flag': 'boolean', 'order_flow_curvature_decoupling_flag': 'boolean', 'schwarzschild_deflection_flag': 'boolean', 'shapiro_delay_flag': 'boolean', 'lense_thirring_lock_flag': 'boolean', 'gliotransmitter_depletion_flag': 'boolean', 'tripartite_synapse_calcium_wave_saturation_flag': 'boolean', 'tfhe_noise_overflow_flag': 'boolean', 'plonky3_timeout_flag': 'boolean', 'total_omniverse_quench_flag': 'boolean', 'lean4_formal_proof_verified': 'boolean', 'photonic_cpo_jitter_fs': 'number', 'homomorphic_routing_delay_ms': 'number', 'zk_rollup_bridge_delay_ms': 'number', 'copula_tail_burst': 'boolean', 'hurst_non_markovian': 'number', 'rlmf_invariant_drift': 'boolean', 'adversarial_crucible_attack': 'boolean', 'cdc_metastability_flag': 'boolean', 'bram_contention_flag': 'boolean', 'serdes_lane_jitter_ps': 'number', 'gas_gwei_spike': 'number', 'amm_constant_product_slip': 'number', 'multihop_sandwich_risk': 'boolean', 'heston_vol_skew_ratio': 'number', 'flash_loan_attack': 'boolean', 'validator_slashed_blackout': 'boolean', 'fx_depeg_basis_bps': 'number', 'adversarial_rl_stophunt': 'boolean', 'amm_spread_gouging': 'boolean', 'time_to_macro_release_seconds': 'number', 'mean_reversion_halflife_seconds': 'number', 'ccp_emergency_halt': 'boolean', 'bgp_fiber_partition': 'boolean', 'wormhole_relay_delay_ms': 'number', 'gmm_regime_cluster_entropy': 'number', 'systemic_blackhole_shock': 'boolean', 'multi_oracle_dispersion_bps': 'number', 'dma_packet_dropped': 'boolean', 'clearing_margin_shock': 'boolean', 'merton_jump_intensity': 'number', 'rfq_latency_injected_ms': 'number', 'terminal_settlement_dispute': 'boolean', 'settlement_boundary_subsecond_ms': 'number', 'pyth_subslot_latency_ms': 'number', 'pyth_confidence_pct': 'number', 'mev_sandwich_risk': 'boolean', 'consecutive_losses': 'number', 'concurrency_count': 'number', 'photonic_ring_drift_nm': 'number', 'qubo_spectral_gap': 'number', 'ks_divergence_statistic': 'number', 'majorana_parity_error_ppm': 'number', 'evt_frechet_tail_max_bps': 'number', 'power_law_alpha': 'number', 'hyperbolic_poincare_curvature': 'number', 'vdf_delay_ms': 'number', 'kurtosis_60s': 'number', 'pt_symmetry_impedance_ppm': 'number', 'ppp_cluster_density': 'number', 'rough_heston_hurst': 'number', 'qeaba_ghz_fidelity': 'number', 'bsde_viscosity_gradient': 'number', 'gravitational_redshift_offset_ps': 'number', 'volterra_singular_kernel_ratio': 'number', 'ricci_curvature_gradient': 'number', 'kerr_metric_drift_ps': 'number', 'memristor_conductance_residual': 'number', 'zk_mpc_info_leakage_bps': 'number', 'qnm_dispersion_ratio': 'number', 'ricci_soliton_gradient': 'number', 'lensing_phase_offset_ps': 'number', 'astrocyte_calcium_saturation': 'number', 'tfhe_bootstrap_noise_ratio': 'number', 'copula_dof': 'number', 'particle_filter_n_eff': 'number', 'particle_filter_drift_var': 'number', 'private_mempool_routed': 'boolean', 'ptp_sync_drift_us': 'number', 'neural_hawkes_excitation': 'number', 'hawkes_intensity_vpin': 'number', 'latency_ms': 'number', 'clock_skew_ms': 'number', 'rpc_delay_ms': 'number', 'funding_rate_annualized': 'number'}

def legacy_policy(trade):
    a = trade['asset']
    p = trade['price']
    rem = trade['rem']
    norm = trade['norm_lead']
    lead = trade['lead_bps']
    side = trade['side']
    z_score = trade.get('z_score', lead / max(0.1, math.sqrt(rem)))
    if a in ('SOL', 'XRP'):
        return (False, 'quarantined_asset_topology', 0.0, 0.0)
    if a == 'DOGE' and side != 'NO':
        return (False, 'doge_direction_bias', 0.0, 0.0)
    if a == 'BTC' and rem <= 5.5 and (p >= 0.65):
        z_score = trade.get('z_score', lead / max(0.1, math.sqrt(rem)))
        if lead < 8.5 or abs(z_score) < 1.5:
            return (False, 'btc_high_price_low_lead_asymmetry_trap_veto', 0.0, 0.0)
    if rem <= 5.5 and p >= 0.65:
        if a == 'ETH' and (lead < 11.5 or abs(z_score) < 1.65):
            return (False, 'eth_high_price_volatility_lead_veto', 0.0, 0.0)
        if a == 'DOGE' and (lead < 16.0 or abs(z_score) < 1.85):
            return (False, 'doge_high_price_volatility_lead_veto', 0.0, 0.0)
    if rem <= 2.5 and p >= 0.7:
        if lead < 10.0 or abs(z_score) < 1.7:
            return (False, 'near_expiry_micro_horizon_distance_veto', 0.0, 0.0)
    perp_vel = trade.get('perp_vel_30s', 0.0)
    if side == 'NO' and perp_vel > 25.0:
        return (False, 'perp_velocity_surging_upward_against_no', 0.0, 0.0)
    if side == 'YES' and perp_vel < -25.0:
        return (False, 'perp_velocity_dumping_downward_against_yes', 0.0, 0.0)
    if trade.get('optical_phase_slip_fs', 25.0) > 50.0:
        return (False, 'subfemtosecond_optical_phase_slip_jitter', 0.0, 0.0)
    if trade.get('sfq_thermal_quench_flag', False) or trade.get('photonic_ring_drift_nm', 0.005) > 0.02:
        return (False, 'cryogenic_sfq_quench_or_photonic_ring_drift', 0.0, 0.0)
    if trade.get('quantum_optomechanical_decoherence', False):
        return (False, 'quantum_coherent_state_decoherence_trap', 0.0, 0.0)
    if trade.get('qubo_spectral_gap', 2.5) < 1.0 or trade.get('stark_recursion_soundness_split', False):
        return (False, 'qubo_spin_glass_frustration_or_stark_split', 0.0, 0.0)
    if trade.get('multiprover_arbitration_delay_ms', 45.0) > 350.0:
        return (False, 'decentralized_multiprover_settlement_timeout', 0.0, 0.0)
    if trade.get('merkle_solvency_inconsistent', False):
        return (False, 'realtime_merkle_sum_solvency_inconsistency', 0.0, 0.0)
    if trade.get('rough_bergomi_hurst', 0.5) < 0.1:
        return (False, 'rough_bergomi_hurst_subdiffusive_crash_veto', 0.0, 0.0)
    if trade.get('snn_synaptic_backpressure_flag', False):
        return (False, 'neuromorphic_snn_synaptic_backpressure_overflow', 0.0, 0.0)
    if trade.get('ks_divergence_statistic', 0.04) > 0.18 or trade.get('f_vecm_cointegration_break', False):
        return (False, 'ks_non_gaussian_fracture_or_fvecm_break', 0.0, 0.0)
    if rem <= 0.0075:
        return (False, 'settlement_boundary_timing_lock', 0.0, 0.0)
    if lead <= 3.5 and p >= 0.6 and (trade.get('spread_cents', 0.02) > 0.03):
        return (False, 'strike_adjacent_liquidity_vacuum_veto', 0.0, 0.0)
    if a != 'BTC' and side == 'YES' and (trade.get('perp_vel_30s', 0.0) < -40.0):
        return (False, 'correlated_downside_contagion_veto', 0.0, 0.0)
    if p >= 0.88 and (lead < 12.0 or abs(z_score) < 1.8):
        return (False, 'asymmetric_parity_payoff_friction_veto', 0.0, 0.0)
    if trade.get('majorana_parity_error_ppm', 0.5) > 5.0 or trade.get('anyon_braiding_noise_flag', False):
        return (False, 'topological_majorana_parity_error_or_braiding_noise', 0.0, 0.0)
    if trade.get('fqhe_edge_break_flag', False) or trade.get('topological_qubit_quench', False):
        return (False, 'topological_fqhe_edge_or_qubit_quench_veto', 0.0, 0.0)
    if trade.get('evt_frechet_tail_max_bps', 3.0) > 20.0 or trade.get('gpd_tail_explosion_flag', False):
        return (False, 'evt_frechet_tail_or_gpd_explosion_veto', 0.0, 0.0)
    if trade.get('power_law_alpha', 2.5) < 1.8 or trade.get('extreme_mae_shock_flag', False):
        return (False, 'power_law_alpha_collapse_or_mae_shock_veto', 0.0, 0.0)
    if trade.get('hyperbolic_poincare_curvature', -0.45) < -0.85 or trade.get('ricci_curvature_singularity', False):
        return (False, 'hyperbolic_poincare_or_ricci_curvature_veto', 0.0, 0.0)
    if trade.get('complex_network_percolation', False) or trade.get('ultrametric_partition_flag', False):
        return (False, 'network_percolation_or_ultrametric_partition_veto', 0.0, 0.0)
    if trade.get('vdf_delay_ms', 120.0) > 500.0 or trade.get('rsa_sluggishness_flag', False):
        return (False, 'fhe_vdf_slot_delay_or_rsa_sluggishness_veto', 0.0, 0.0)
    if trade.get('zk_timed_deadlock_flag', False) or trade.get('snark_prover_race_flag', False):
        return (False, 'zk_timed_deadlock_or_snark_race_veto', 0.0, 0.0)
    if trade.get('photonic_reservoir_saturated', False) or trade.get('microring_bistability_flag', False):
        return (False, 'photonic_reservoir_saturation_or_bistability_veto', 0.0, 0.0)
    if trade.get('mzi_dispersion_flag', False) or trade.get('frequency_comb_drift_flag', False):
        return (False, 'mzi_dispersion_or_comb_drift_veto', 0.0, 0.0)
    if trade.get('waveguide_phase_break_flag', False) or trade.get('inter_dc_sync_shock_flag', False):
        return (False, 'metamaterial_waveguide_or_sync_shock_veto', 0.0, 0.0)
    if trade.get('lorentz_dilation_drift_flag', False) or trade.get('hyperdimensional_singularity_flag', False):
        return (False, 'lorentz_dilation_or_singularity_dissolution_veto', 0.0, 0.0)
    utc_h = trade.get('utc_hour', 12.0)
    if 2.0 <= utc_h <= 7.0 and trade.get('spread_cents', 0.02) > 0.03:
        return (False, 'diurnal_thin_tape_spread_excess_veto', 0.0, 0.0)
    if trade.get('concurrent_count', 0) >= 2:
        return (False, 'multi_asset_concurrency_overflow_lock', 0.0, 0.0)
    if trade.get('kurtosis_60s', 3.0) > 6.0 and (lead < 14.0 or abs(z_score) < 1.9):
        return (False, 'high_kurtosis_jump_cluster_veto', 0.0, 0.0)
    if trade.get('pt_symmetry_impedance_ppm', 1.0) > 15.0 or trade.get('pt_symmetry_breaking_flag', False):
        return (False, 'pt_symmetry_impedance_jump_or_symmetry_breaking_veto', 0.0, 0.0)
    if trade.get('coalescing_eigenstate_loss_flag', False):
        return (False, 'coalescing_eigenstate_transmission_loss_veto', 0.0, 0.0)
    if trade.get('ppp_cluster_density', 1.0) > 4.0 or trade.get('voronoi_partition_shock', False):
        return (False, 'ppp_mev_cluster_or_voronoi_partition_veto', 0.0, 0.0)
    if trade.get('delaunay_congestion_flag', False) or trade.get('spatial_anisotropy_flag', False):
        return (False, 'delaunay_relay_congestion_or_spatial_anisotropy_veto', 0.0, 0.0)
    if trade.get('rough_heston_hurst', 0.5) < 0.05 or trade.get('volterra_kernel_persistence_flag', False):
        return (False, 'rough_heston_hurst_or_volterra_persistence_veto', 0.0, 0.0)
    if trade.get('riemann_liouville_singular_flag', False) or trade.get('multiscale_roughness_inversion_flag', False):
        return (False, 'riemann_liouville_singular_or_roughness_inversion_veto', 0.0, 0.0)
    if trade.get('qeaba_ghz_fidelity', 0.99) < 0.95 or trade.get('bsm_fidelity_drop_flag', False):
        return (False, 'qeaba_ghz_fidelity_or_bsm_drop_veto', 0.0, 0.0)
    if trade.get('teleportation_noise_flag', False) or trade.get('nonlocal_correlation_collapse_flag', False):
        return (False, 'teleportation_noise_or_correlation_collapse_veto', 0.0, 0.0)
    if trade.get('bsde_viscosity_gradient', 0.04) > 0.15 or trade.get('hjb_viscosity_blowup_flag', False):
        return (False, 'deep_bsde_gradient_or_hjb_blowup_veto', 0.0, 0.0)
    if trade.get('nonlinear_drift_control_singularity_flag', False) or trade.get('feynman_kac_dispersion_flag', False):
        return (False, 'nonlinear_drift_or_feynman_kac_dispersion_veto', 0.0, 0.0)
    if trade.get('gravitational_redshift_offset_ps', 5.0) > 45.0 or trade.get('sagnac_orbital_offset_flag', False):
        return (False, 'gravitational_redshift_or_sagnac_offset_veto', 0.0, 0.0)
    if trade.get('cosmic_ray_seu_bitflip_flag', False) or trade.get('total_cosmic_collapse_flag', False):
        return (False, 'cosmic_ray_seu_or_total_cosmic_collapse_veto', 0.0, 0.0)
    if trade.get('volterra_singular_kernel_ratio', 1.0) > 3.5 or trade.get('singular_volterra_kernel_flag', False):
        return (False, 'volterra_singular_kernel_or_bridge_variance_veto', 0.0, 0.0)
    if trade.get('fractional_bridge_drift_flag', False) or trade.get('non_markovian_jump_cluster_flag', False):
        return (False, 'fractional_bridge_drift_or_jump_clustering_veto', 0.0, 0.0)
    if trade.get('braid_invariance_rupture_flag', False) or trade.get('topological_knot_deadlock_flag', False):
        return (False, 'non_abelian_braid_rupture_or_knot_deadlock_veto', 0.0, 0.0)
    if trade.get('multi_exchange_collateral_shred_flag', False):
        return (False, 'multi_exchange_collateral_shred_veto', 0.0, 0.0)
    if trade.get('ricci_curvature_gradient', 0.03) > 0.12 or trade.get('ricci_singularity_flag', False):
        return (False, 'ricci_curvature_gradient_or_singularity_veto', 0.0, 0.0)
    if trade.get('manifold_tear_flag', False) or trade.get('lob_volume_evaporation_flag', False):
        return (False, 'manifold_tear_or_lob_volume_evaporation_veto', 0.0, 0.0)
    if trade.get('kerr_metric_drift_ps', 2.0) > 30.0 or trade.get('kerr_metric_shock_flag', False):
        return (False, 'kerr_spacetime_metric_drift_veto', 0.0, 0.0)
    if trade.get('fiber_birefringence_flag', False) or trade.get('relativistic_arbitration_lock_flag', False):
        return (False, 'quantum_fiber_birefringence_or_arbitration_lock_veto', 0.0, 0.0)
    if trade.get('memristor_conductance_residual', 0.01) > 0.08 or trade.get('memristor_conductance_drift_flag', False):
        return (False, 'memristor_conductance_drift_or_residual_veto', 0.0, 0.0)
    if trade.get('sneak_path_leakage_flag', False) or trade.get('analog_thermal_quench_flag', False):
        return (False, 'sneak_path_leakage_or_analog_thermal_quench_veto', 0.0, 0.0)
    if trade.get('zk_mpc_info_leakage_bps', 0.0) > 0.0 or trade.get('pedersen_blinding_breach_flag', False):
        return (False, 'pedersen_blinding_breach_or_info_leakage_veto', 0.0, 0.0)
    if trade.get('garbled_circuit_collusion_flag', False) or trade.get('total_multiverse_entropy_flag', False):
        return (False, 'garbled_circuit_collusion_or_multiverse_entropy_veto', 0.0, 0.0)
    if trade.get('qnm_dispersion_ratio', 1.0) > 3.0 or trade.get('radiation_pressure_shock_flag', False):
        return (False, 'qnm_dispersion_or_radiation_pressure_veto', 0.0, 0.0)
    if trade.get('nanocavity_thermal_runaway_flag', False) or trade.get('optomechanical_ep_annihilation_flag', False):
        return (False, 'nanocavity_thermal_or_ep_annihilation_veto', 0.0, 0.0)
    if trade.get('chiral_edge_scattering_flag', False) or trade.get('quasiparticle_dissipation_flag', False):
        return (False, 'chiral_edge_scattering_or_dissipation_veto', 0.0, 0.0)
    if trade.get('chern_number_inversion_flag', False):
        return (False, 'chern_number_inversion_veto', 0.0, 0.0)
    if trade.get('ricci_soliton_gradient', 0.02) > 0.1 or trade.get('shrinking_soliton_shock_flag', False):
        return (False, 'ricci_soliton_gradient_or_singularity_veto', 0.0, 0.0)
    if trade.get('metric_tensor_anisotropy_flag', False) or trade.get('order_flow_curvature_decoupling_flag', False):
        return (False, 'metric_anisotropy_or_curvature_decoupling_veto', 0.0, 0.0)
    if trade.get('lensing_phase_offset_ps', 3.0) > 25.0 or trade.get('schwarzschild_deflection_flag', False):
        return (False, 'gravitational_lensing_or_schwarzschild_veto', 0.0, 0.0)
    if trade.get('shapiro_delay_flag', False) or trade.get('lense_thirring_lock_flag', False):
        return (False, 'shapiro_delay_or_lense_thirring_veto', 0.0, 0.0)
    if trade.get('astrocyte_calcium_saturation', 0.1) > 0.7 or trade.get('gliotransmitter_depletion_flag', False) or trade.get('tripartite_synapse_calcium_wave_saturation_flag', False):
        return (False, 'astrocyte_saturation_or_gliotransmitter_veto', 0.0, 0.0)
    if trade.get('homeostatic_plasticity_breakdown_flag', False):
        return (False, 'homeostatic_plasticity_breakdown_veto', 0.0, 0.0)
    if trade.get('tfhe_bootstrap_noise_ratio', 0.05) > 0.2 or trade.get('tfhe_noise_overflow_flag', False):
        return (False, 'tfhe_bootstrap_noise_overflow_veto', 0.0, 0.0)
    if trade.get('plonky3_timeout_flag', False) or trade.get('total_omniverse_quench_flag', False):
        return (False, 'plonky3_timeout_or_omniverse_quench_veto', 0.0, 0.0)
    if not trade.get('lean4_formal_proof_verified', True):
        return (False, 'lean4_formal_proof_verification_failed', 0.0, 0.0)
    if trade.get('photonic_cpo_jitter_fs', 450.0) > 850.0:
        return (False, 'photonic_optical_interconnect_jitter_degradation', 0.0, 0.0)
    if trade.get('homomorphic_routing_delay_ms', 12.0) > 45.0:
        return (False, 'homomorphic_encryption_routing_delay_stall', 0.0, 0.0)
    if trade.get('neural_sde_diverged', False):
        return (False, 'deep_equilibrium_neural_sde_divergence_trap', 0.0, 0.0)
    if trade.get('verilog_ams_synthesis_glitch', False):
        return (False, 'lean4_verilog_ams_synthesis_glitch', 0.0, 0.0)
    if trade.get('pbs_proposer_inversion_risk', False):
        return (False, 'mev_boost_pbs_proposer_slot0_racing_risk', 0.0, 0.0)
    if trade.get('cross_margin_haircut_shock', False):
        return (False, 'cross_margining_liquidation_cascade_shock', 0.0, 0.0)
    if trade.get('zk_rollup_bridge_delay_ms', 35.0) > 300.0:
        return (False, 'zk_rollup_l3_settlement_bridge_delay', 0.0, 0.0)
    if trade.get('copula_tail_burst', False) or trade.get('copula_dof', 8.0) < 4.0:
        return (False, 'students_t_copula_asymmetric_tail_burst', 0.0, 0.0)
    if trade.get('hurst_non_markovian', 0.5) > 0.72:
        return (False, 'quantum_random_walk_non_markovian_friction', 0.0, 0.0)
    if trade.get('rlmf_invariant_drift', False) or trade.get('adversarial_crucible_attack', False):
        return (False, 'adversarial_red_team_or_rlmf_drift_attack', 0.0, 0.0)
    if trade.get('cdc_metastability_flag') or trade.get('bram_contention_flag'):
        return (False, 'asic_cdc_metastability_or_bram_contention', 0.0, 0.0)
    if trade.get('serdes_lane_jitter_ps', 2.5) > 35.0:
        return (False, 'pcie_gen5_serdes_lane_jitter_degradation', 0.0, 0.0)
    if trade.get('particle_filter_n_eff', 45000) < 5000 or trade.get('particle_filter_drift_var', 0.02) > 0.1:
        return (False, 'bayesian_particle_filter_degeneracy_whipsaw', 0.0, 0.0)
    if trade.get('gas_gwei_spike', 22.0) > 120.0:
        return (False, 'cross_contract_gas_spike_block_exhaustion', 0.0, 0.0)
    if trade.get('amm_constant_product_slip', 0.001) > 0.0045:
        return (False, 'constant_product_invariant_slippage_trap', 0.0, 0.0)
    if trade.get('multihop_sandwich_risk') and (not trade.get('private_mempool_routed')):
        return (False, 'multihop_dex_sandwich_inclusion_risk', 0.0, 0.0)
    if trade.get('heston_vol_skew_ratio', 0.15) > 0.45:
        return (False, 'heston_vol_skew_pde_violation', 0.0, 0.0)
    if trade.get('flash_loan_attack') or trade.get('validator_slashed_blackout'):
        return (False, 'flash_loan_or_validator_blackout_risk', 0.0, 0.0)
    if trade.get('fx_depeg_basis_bps', 0.5) > 200.0:
        return (False, 'sovereign_fiat_fx_depeg_partition', 0.0, 0.0)
    if trade.get('adversarial_rl_stophunt') or trade.get('amm_spread_gouging'):
        return (False, 'adversarial_rl_stophunt_or_amm_gouging', 0.0, 0.0)
    if trade.get('time_to_macro_release_seconds', 3600.0) <= 180.0:
        return (False, 'macro_economic_calendar_pre_release_freeze', 0.0, 0.0)
    if trade.get('mean_reversion_halflife_seconds', 600.0) < 90.0:
        return (False, 'mean_reversion_halflife_decay_trap', 0.0, 0.0)
    if trade.get('ccp_emergency_halt') or trade.get('bgp_fiber_partition'):
        return (False, 'ccp_emergency_halt_or_fiber_partition', 0.0, 0.0)
    if trade.get('wormhole_relay_delay_ms', 45.0) > 400.0:
        return (False, 'cross_chain_wormhole_bridge_delay', 0.0, 0.0)
    if trade.get('gmm_regime_cluster_entropy', 0.1) > 0.6:
        return (False, 'gmm_regime_cluster_entropy_ambiguity', 0.0, 0.0)
    subtick_dist = trade.get('subtick_strike_distance_bps', 10.0)
    if rem <= 0.75 and subtick_dist < 0.35:
        return (False, 'subtick_quantization_snapping_hazard', 0.0, 0.0)
    vel_sigma = trade.get('price_velocity_60s_sigma', 1.0)
    if vel_sigma > 4.5 or trade.get('systemic_blackhole_shock'):
        return (False, 'catastrophic_velocity_jump_breaker_active', 0.0, 0.0)
    if trade.get('multi_oracle_dispersion_bps', 0.8) > 3.0:
        return (False, 'byzantine_oracle_dispersion_split', 0.0, 0.0)
    if trade.get('dma_packet_dropped') or trade.get('ptp_sync_drift_us', 1.0) > 10.0:
        return (False, 'hardware_dma_packet_drop_or_ptp_drift', 0.0, 0.0)
    if trade.get('neural_hawkes_excitation', 0.15) > 0.65 or trade.get('hawkes_intensity_vpin', 0.15) > 0.6:
        return (False, 'neural_hawkes_toxic_excitation_spike', 0.0, 0.0)
    if trade.get('clearing_margin_shock') or abs(trade.get('funding_rate_annualized', 12.0)) > 150.0:
        return (False, 'clearing_margin_or_funding_squeeze_risk', 0.0, 0.0)
    if trade.get('validator_reorg_delay'):
        return (False, 'validator_reorg_censorship_active', 0.0, 0.0)
    if trade.get('merton_jump_intensity', 0.0) > 0.4:
        return (False, 'merton_jump_intensity_hazard', 0.0, 0.0)
    if trade.get('exchange_circuit_breaker'):
        return (False, 'matching_engine_halt_active', 0.0, 0.0)
    if trade.get('rfq_latency_injected_ms', 0.0) > 150.0:
        return (False, 'predatory_broker_rfq_latency_freeze', 0.0, 0.0)
    if trade.get('terminal_settlement_dispute') and lead < 0.2:
        return (False, 'terminal_settlement_quantum_dispute', 0.0, 0.0)
    resting_depth = trade.get('l2_resting_contracts', 5000)
    if resting_depth < 300:
        return (False, 'insufficient_l2_resting_depth', 0.0, 0.0)
    spread = trade.get('spread_cents', 0.02)
    if spread <= 0 or spread > 0.06:
        return (False, 'abnormal_or_inverted_spread', 0.0, 0.0)
    if trade.get('latency_ms', 0) > 400.0 or trade.get('clock_skew_ms', 0) > 250.0 or trade.get('rpc_delay_ms', 0) > 1500.0:
        return (False, 'stale_clock_or_gateway_latency', 0.0, 0.0)
    if trade.get('settlement_boundary_subsecond_ms', 500) < 100.0:
        return (False, 'settlement_boundary_racing_hazard', 0.0, 0.0)
    if trade.get('pyth_subslot_latency_ms', 18.0) > 150.0:
        return (False, 'pyth_subslot_latency_degraded', 0.0, 0.0)
    if trade.get('pyth_confidence_pct', 0.008) > 0.025:
        return (False, 'pyth_confidence_interval_exploded', 0.0, 0.0)
    if trade.get('mev_sandwich_risk') and (not trade.get('private_mempool_routed')):
        return (False, 'adversarial_mev_frontrunning_risk', 0.0, 0.0)
    theta = trade.get('kalman_mean_rev_theta', 0.015)
    if theta > 0.08:
        return (False, 'kalman_mean_reversion_whipsaw_risk', 0.0, 0.0)
    if rem < 0.8 or rem > 11.0:
        return (False, 'expiry_window_closed', 0.0, 0.0)
    if trade.get('consecutive_losses', 0) >= 2:
        return (False, 'streak_cooldown_active', 0.0, 0.0)
    if trade.get('concurrency_count', 1) > 2:
        return (False, 'concurrency_budget_exhausted', 0.0, 0.0)
    if trade.get('tradfi_pinning'):
        if rem > 3.0:
            return (False, 'tradfi_pinning_whipsaw_risk', 0.0, 0.0)
    basis = trade.get('basis_bps', 0.0)
    if side == 'YES' and basis < -3.5:
        return (False, 'binance_perp_opposing_yes', 0.0, 0.0)
    if side == 'NO' and basis > +3.5:
        return (False, 'binance_perp_opposing_no', 0.0, 0.0)
    macro_trend = trade.get('macro_trend', 0)
    if macro_trend == 1 and side == 'NO':
        return (False, 'trend_concordance_opposing_bull', 0.0, 0.0)
    if macro_trend == -1 and side == 'YES':
        return (False, 'trend_concordance_opposing_bear', 0.0, 0.0)
    if trade.get('is_shock'):
        if norm < 3.2:
            return (False, 'insufficient_shock_cushion', 0.0, 0.0)
    elif norm < 2.0:
        return (False, 'insufficient_norm_lead', 0.0, 0.0)
    if a == 'DOGE':
        if rem <= 4.0 and lead < 4.5:
            return (False, 'doge_short_lead_low', 0.0, 0.0)
        if rem > 4.0 and lead < 8.0:
            return (False, 'doge_mid_lead_low', 0.0, 0.0)
        if rem > 7.5 and p > 0.56 and (lead < 13.1):
            return (False, 'doge_long_discount_required', 0.0, 0.0)
    if a == 'BTC' and lead < 6.0:
        return (False, 'btc_lead_low', 0.0, 0.0)
    p_cap_max = 0.8 if a == 'BTC' else 0.75 if a == 'ETH' else 0.7
    cap = min(p_cap_max, 0.56 + 0.05 * max(0.0, 11.0 - rem) + 0.04 * (norm / 10.0))
    if p > cap:
        return (False, 'price_exceeds_convex_cap', 0.0, 0.0)
    budget_requested = trade.get('order_budget_dollars', 500.0)
    replenish = trade.get('iceberg_replenish_rate', 1.0)
    effective_depth = trade.get('cross_venue_aggregated_depth', resting_depth * (1.0 + 0.5 * replenish))
    drl_lambda = trade.get('drl_dynamic_kelly_lambda', 0.25)
    max_safe_budget = min(4000.0, effective_depth * p * 0.35 * (drl_lambda / 0.25))
    if max_safe_budget < 50.0:
        return (False, 'insufficient_book_capacity_for_budget', 0.0, 0.0)
    actual_budget = max(50.0, min(max_safe_budget, budget_requested))
    alpha_amm = 0.025 / math.sqrt(6.0)
    amm_convex_slippage = alpha_amm * math.pow(actual_budget / effective_depth, 0.65)
    effective_fill_price = min(cap, p + amm_convex_slippage)
    if effective_fill_price > cap:
        actual_budget = max(50.0, actual_budget * 0.6)
        amm_convex_slippage = alpha_amm * math.pow(actual_budget / effective_depth, 0.65)
        effective_fill_price = min(cap, p + amm_convex_slippage)
    fair = min(0.99, effective_fill_price + 0.15)
    unit_cost = 1.05 * effective_fill_price + 0.02
    if fair - unit_cost < 0.01:
        return (False, 'net_edge_eroded_by_amm_taker_curve', 0.0, 0.0)
    return (True, 'passed_apex_108_shield', actual_budget, effective_fill_price)
