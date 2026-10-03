# Bounded theorem/statement correspondence review

This is an agent's initial review, not independent mathematical adjudication.
The pin is OpenAI `f9e8bc5b38b6e212696e8a30e3e91517af887bbd`.
Reference source: Formal Conjectures `8bf45ed70d48b2b2a501de9c00b26bfa38c573ee`.
The source path at that commit used `Millenium`; current main uses `Millennium`.
The original 404 on the old main path was a path drift, not absent public evidence.

| Clay requirement | Public reference encoding | Initial review / remaining obligation |
|---|---|---|
| Three spatial dimensions | `EuclideanSpace ℝ (Fin 3)` | Matches dimension; inspect Euclidean differential conventions |
| Every positive viscosity | Explicit `nu : ℝ`, `hnu : nu > 0` | Quantifier appears in both C/D roots |
| Smooth divergence-free initial data | `InitialVelocityCondition` | Uses `ContDiff ℝ ∞` and derivative trace |
| Rapid spatial decay of every initial derivative | `InitialVelocityConditionDecay.decay` | One bound per order and decay power, uniform over x |
| Smooth force on closed t≥0 half-line | `ForceCondition.smooth` | Joint `ContDiffOn` on `univ × Ici 0`; verify boundary extension semantics |
| Force derivative decay uniform in x,t | `ForceConditionDecay.decay` | Joint iterated Fréchet derivative bounds; compare multi-index formulation |
| Momentum equation and incompressibility | `NavierStokesExistenceAndSmoothness` | Time derivative within `Ici 0`, spatial derivative application and Laplacian/gradient |
| Initial condition | `initial_condition` | Explicit equality at time zero |
| Global velocity and pressure smoothness | `velocity_smooth`, `pressure_smooth` | Joint all-order smoothness on closed half-line |
| Uniformly bounded R3 kinetic energy | `MemLp` plus `globally_bounded_energy` | Explicit integrability prevents junk-value integral from hiding divergent energy |
| Periodic initial data and forcing | `InitialVelocityConditionPeriodic`, `ForceConditionPeriodic` | Period one in each coordinate; force also decays in time |
| Periodic velocity and pressure | Periodic solution's two periodicity fields | Pressure requirement appears explicitly and matches Clay's appended erratum |
| Nonexistence of global admissible solution | `¬ (∃ v p, ...)` | Stronger than merely showing one trajectory diverges; comparison bridge must prove it |

The PDF's Theorem 1.1 asserts rest initial data, smooth compact force, uniform
pre-singularity energy, velocity supremum blowup, and a nonexistence consequence.
Compact support can imply rapid derivative decay when the required smoothness
and all-order bounds are proved, but compact support alone does not supply these
proofs. The whole-space and periodic bridges require separate scrutiny.

The proof file `NavierStokes/ComparatorSolution.lean` exports the same named
existential C/D statements as the challenge. The submission uses copied definition
modules rather than importing the challenge's deliberate `sorry` placeholders.
Comparator must check definitional identity and axioms at runtime. The current
source audit alone cannot do that.

Clay accepts any of A/B/C/D; A/B impose zero force and C/D permit smooth force.
Therefore external forcing by itself does not disqualify the submitted C/D scope.
This also means a C/D result must not be described as solving unforced A/B.

Sources: [Clay's six-page PDF including errata](https://www.claymath.org/wp-content/uploads/2022/06/navierstokes.pdf),
[public paper](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf),
[pinned proof root](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/ComparatorSolution.lean),
and the pinned public challenge source linked above.

