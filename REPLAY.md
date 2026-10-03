# Pinned Navier–Stokes replay

Run heavy replay in a disposable Linux environment with ample free disk, not on a nearly full laptop. Do not run arbitrary submitted Lean code with secrets or privileged service credentials. Export checkpoints before any resource deadline. This public repository contains controls and a receipt gate, not the entire upstream mathlib cache.

Pinned target:

```sh
git init NavierStokesAndEuler
cd NavierStokesAndEuler
git remote add origin https://github.com/openai/NavierStokesAndEuler.git
git fetch --depth 1 origin f9e8bc5b38b6e212696e8a30e3e91517af887bbd
git checkout --detach FETCH_HEAD
# Install the exact toolchain in lean-toolchain with elan.
lake exe cache get
lake build NavierStokes.ComparatorSolution
lake env lean NavierStokes/ComparatorSolution.lean
```

The build completed with 9,371 jobs in the fresh follow-up run. Standalone axiom printing exited zero. Allowed axioms were `propext`, `Classical.choice`, `Quot.sound`; `sorryAx` is not allowed. This replays the named theorem's dependency closure, not every otherwise unrelated module in the repository.

Independent check follows the pinned [Comparator documentation](https://github.com/leanprover/comparator) and supplied `ComparatorChallenges/NavierStokes.json`. Comparator pin: `19e111e2141cf333c7daff0f64c5f24acc91dd2e`; landrun pin: `5ed4a3db3a4ad930d577215c6b9abaa19df7f99f`; nanoda pin: `68d5ca9db226849b41a6fff59d796ff19d0a8840`. Verify exact Comparator pin against the upstream `lake-manifest.json` before continuing; a mismatch must abstain. No floating verifier substitution or weakened challenge is permitted.

Build the pinned `lean4export` and `comparator`. Supply `COMPARATOR_LANDRUN`, `COMPARATOR_NANODA`, and `COMPARATOR_LEAN4EXPORT` paths as documented. The checker must run unprivileged. For the documented AF_UNIX sandbox caveat, use a root-managed transient systemd unit restricted by `RestrictAddressFamilies=~AF_UNIX` whose actual process runs as the unprivileged UID; never run the Lean compiler as root. The follow-up environment uses Linux 6.12 and a 25-minute comparator timeout. Sandbox setup and proof-kernel validity are separate checks.

Trusted SHA256 values:

| Artifact | SHA256 |
|---|---|
| `ComparatorChallenges/NavierStokes.lean` | `0cd193b8d5cbd0266e6e2f72e68dd5abcdcf2430ebd435dd9289737e9aa7da61` |
| `NavierStokes/ComparatorDefinitions.lean` | `8d90e0f9eee14f8b01773852083a02fd58bda59d4de2abb60d1787bbc9f6ebf4` |
| `lake-manifest.json` | `5ec1dc8e009008d0efb9601cd38f6ba54e753fd538b0e5f8c3e6c5ec72ee1e09` |

Verify them before and after checking. `proof_gate.py` requires terminal checker exit zero and all prerequisite receipts; missing data or timeout remains open. A passing independent kernel replay still leaves independent mathematical correspondence review open.

Prior runs timed out in the actual checker. They are negative execution receipts, not disprovals of the theorem. Runtime changes may improve completion, but must not weaken reference statements or validator rules.
