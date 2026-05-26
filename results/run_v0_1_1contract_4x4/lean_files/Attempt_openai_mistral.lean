namespace Parallax5.Copilot.a1_trivial_constant_balance

structure ConstantBalanceState where
  initialBalance : Nat
  balance : Nat
  deriving Repr

def getBalance (s : ConstantBalanceState) : ConstantBalanceState :=
  s

def valueConservationA1 (s : ConstantBalanceState) : Prop :=
  s.balance = s.initialBalance

theorem a1_trivial_constant_balance_safety :
    ∀ (s : ConstantBalanceState),
      valueConservationA1 s → valueConservationA1 (getBalance s) := by
  intros s h
  exact h

end Parallax5.Copilot.a1_trivial_constant_balance
