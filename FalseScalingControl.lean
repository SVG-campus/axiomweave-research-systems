import Mathlib.Data.Real.Basic
import Mathlib.Tactic.NormNum

-- Deliberately false. This file MUST fail; it tests the verifier's rejection.
theorem deliberately_false_energy_decay : 0 < (1 / 2 : ℝ) - 3 * (1 / 5) := by
  norm_num
