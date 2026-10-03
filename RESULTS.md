# Research results and what they mean

The executed three-round portfolio expands finite inputs, retains negative controls, then rechecks known cases. No universal-proof gate closed from these finite experiments. Stop reason: the frozen expansion budget was exhausted with no new universal proof, not exhaustion of all research possible for the assistants.

## Navier–Stokes

OpenAI publicly released a paper and Lean project claiming breakdown for the smooth **forced** alternatives C/D of Clay's statement. This does not claim the unforced A/B alternatives. [Announcement](https://openai.com/index/navier-stokes-solution/), [paper](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf), [formal source](https://github.com/openai/NavierStokesAndEuler), [Clay announcement](https://www.claymath.org/news/navier-stokes-announcement/), [official problem](https://www.claymath.org/wp-content/uploads/2022/06/navierstokes.pdf).

Replay source pin: `f9e8bc5b38b6e212696e8a30e3e91517af887bbd`; toolchain `leanprover/lean4:v4.34.0-rc2`; target `NavierStokes.ComparatorSolution`. The fresh compiler replay passed all **9,371 jobs** and standalone axiom printing exited zero, with only `propext`, `Classical.choice`, and `Quot.sound` for both comparator theorems. **The independent Comparator replay also passed: nanoda and Lean's default kernel accepted the solution, Comparator exited zero, and trusted reference hashes matched before and after.** Comparator runtime was **21min 26.974s**. See [raw comparator receipt](receipts/comparator.log) and [machine gates](receipts/validation-gates.json).

This closes the machine replay gate for the pinned submission. It does not close the independent theorem-to-Clay correspondence or analytic-review gate. The trusted challenge's intentional `sorry` placeholders specify theorem targets; they are separate from the checked solution, whose allowed-axiom closure excludes `sorryAx`.

Symbolic pilot: the seven-atom, three-operation, depth-one grammar has 154 candidates. Full beam finds `3*b-2*a`, `3*b-3*a`, and `b-2*a`; beam width three misses a known target. This tests a restricted isotropic scaling grammar, not the published construction's anisotropic analytic estimates. A singular-term cancellation control proves that termwise rejection need not be hereditary.

The affine check corrects an earlier shortcut: for `u_i=c_i*x_i/(T-t)`, a quadratic pressure can cancel the time and convection residual. Singular forcing with pressure fixed to zero is therefore not an invariant obstruction. Every nonzero such affine field nevertheless fails finite energy and rapid decay on R³; it cannot supply the required Clay counterexample. Independent fixed-symbol differentiation confirms the cancellation.

Next: independently audit quantifiers, forcing, energy and regularity in the trusted formal statement; examine the analytic construction and the paper's deferred components. A matching field list or AST is insufficient to settle mathematical meaning.

## Riemann hypothesis

FLINT/Arb at 128-bit precision returns total nontrivial-zero counts **1, 3, 10, 29** below positive heights **15, 30, 50, 100**. The corresponding distinct critical-line root balls lie inside each window and are disjoint; their residual balls contain zero. An ambiguous height interval straddling the first zero abstains as expected. Exact line-root existence and complete count depend on the documented library routines, not on residual containment alone. [Arb routines](https://python-flint.readthedocs.io/en/latest/arb.html), [Acb routines](https://python-flint.readthedocs.io/en/latest/acb.html).

This is a bounded certified-library computation, not a kernel-checked all-height RH proof. Further computation can enlarge the window and cross-check counts; a solution requires an argument covering every nontrivial zero, or a certified off-line counterexample.

## P versus NP

The earlier exhaustive three-variable census has 256 formulas, 255 satisfiable and one unsatisfiable. Expanded finite CNF tests retain exact exhaustive witnesses/decisions and contradicting-clause controls. These establish finite correctness, not an asymptotic separation.

Barrier auditing now returns conditional obligations, never an admissibility certificate from false flags. A natural-proofs warning needs constructive, large and useful properties for a specified circuit target plus the relevant pseudorandom-function hardness assumption. Relativization and algebrization also require precisely demonstrated scope. Proving superpolynomial general circuit lower bounds would be a stronger route to a separation; it is not a necessary condition for every conceivable P≠NP proof. Next: specify a theorem family, exact model and quantifiers; test small instances as falsification controls while developing an asymptotic argument. [Natural proofs](https://www.cs.umd.edu/~gasarch/BLOGPAPERS/natural.pdf).

## Birch–Swinnerton-Dyer

For `E:y²=x³−2`, `P=(3,5)` and `2P=(129/100,−383/1000)` are exact curve points. Nonintegral coordinates of `2P` imply P has infinite order under Lutz–Nagell, hence rank at least one. Two independent point-counting algorithms agree at nine good primes; their counts are **6,7,12,19,18,27,24,30,28** for primes **5,7,11,13,17,19,23,29,31**, satisfying Hasse's bound.

PARI descent additionally returns lower/upper rank **[1,1]**, conductor **1728**, and torsion order **1**. This is trusted-backend arithmetic, not a separately kernel-verified certificate. It corrects the earlier 3888 claim. Rank one alone does not certify P as a generator: saturation/index remains separate. [Lutz–Nagell lecture](https://math.mit.edu/classes/18.782/2013fa/LectureNotes24.pdf), [PARI rank documentation](https://pari.math.u-bordeaux.fr/dochtml/html/Elliptic_curves.html#ellrank).

Next: saturation and a documented analytic-rank/leading-coefficient comparison for this example, followed by certified arithmetic and formalization. Even a complete proof for this curve does not prove BSD for every elliptic curve.

## Hodge conjecture

For `(P¹)^n`, exact complementary intersection matrices have full rank in each codimension, with dimensions `choose(n,k)`. Tests cover n=1..6; the research expansion covers n=3..5. This is conditional on the known product cohomology ring and coordinate-cycle interpretation. It implements the finite algebra inside an already understood special family.

Next: formalize the cycle-class identification and move to a specified nontrivial family. Producing all rational Hodge classes as algebraic cycle combinations on arbitrary smooth projective complex varieties is a separate general construction.

## Yang–Mills existence and mass gap

The one-dimensional Dirichlet-chain model has ball-enclosed gap `4*sin²(pi/(2(N+1)))`. Every tested finite gap is positive, yet the unscaled gaps approach zero, bounded by `pi²/(N+1)²`. With the stated rescaling they approach pi². This demonstrates how a positive finite-grid gap can disappear in a limit; it is not a four-dimensional non-Abelian quantum field theory.

Next: define the actual gauge group, continuum construction, observables, scaling, positivity and uniform gap estimate. A finite lattice plot cannot establish continuum existence or a positive physical mass gap.

## Poincaré conjecture

Poincaré is already proved. We now compute the actual boundary of a 4-simplex: rational Betti numbers **[1,0,0,1]**, with exact boundary-squared-zero checks. S¹, S², and a contractible tetrahedron provide independent known-case controls. This corrects the earlier S²-only pilot.

Homology does not establish simple connectivity or recognize arbitrary homology 3-spheres. Next: explicit fundamental-group/presentation certificates and sphere-recognition tooling for a specified finite input, not a new claim to solve the already settled theorem.
