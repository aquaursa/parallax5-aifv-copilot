namespace Parallax5.Copilot.a1_trivial_constant_balance

structure ContractState where
  balance : Nat
  deriving Repr

def noop (s : ContractState) : ContractState := s

def obligationPredicate (s : ContractState) : Prop :=
  s.balance = 0

theorem a1_trivial_constant_balance_safety :
    ∀ (s : ContractState), obligationPredicate s → obligationPredicate (noop s) := by
  intro s
  intro h
  unfold noop
  exact h

end Parallax5.Copilot.a1_trivial_constant_balance
