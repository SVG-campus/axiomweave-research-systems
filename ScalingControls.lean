import Mathlib.Data.Real.Basic
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.NormNum

/- Elementary consistency check of the exponents reported in the paper.
   This does not construct a fluid or prove the claimed blowup. -/
theorem admissible_core_exponents (h : ℝ) (hpos : 0 < h) (hsmall : h < 1 / 100) :
    0 < 1 / 2 - 3 * h ∧ -1 < -1 / 2 - 3 * h ∧ -4 * h < 0 := by
  constructor
  · linarith
  constructor <;> linarith

theorem core_energy_exponent (h : ℝ) :
    (3 / 2 - h) - 2 * (1 / 2 + h) = 1 / 2 - 3 * h := by ring

theorem core_cubic_norm_exponent (h : ℝ) :
    (3 / 2 - h) - 3 * (1 / 2 + h) = -4 * h := by ring

theorem core_radial_dissipation_exponent (h : ℝ) :
    (3 / 2 - h) - 2 * (1 + h) = -1 / 2 - 3 * h := by ring

-- Outside the admissible range, energy need not decay.
example : ¬ (0 < (1 / 2 : ℝ) - 3 * (1 / 5)) := by norm_num

#print axioms admissible_core_exponents
#print axioms core_energy_exponent
