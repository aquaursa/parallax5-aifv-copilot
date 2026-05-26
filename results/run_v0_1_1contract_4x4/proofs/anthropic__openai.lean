namespace Parallax5.Copilot.a1_trivial_constant_balance

/-- ConstantBalance contract state: a single immutable balance set at deployment. -/
structure ContractState where
  balance : Nat
  deriving Repr

/-- Deployment operation: produces the initial state from an `initial` parameter
    passed to the constructor. There are no further state-mutating operations:
    the Solidity `immutable` qualifier prevents any write after deployment. -/
def deploy (initial : Nat) : ContractState :=
  { balance := initial }

/-- The A1 value-conservation predicate for this contract: the deployed-state
    balance is exactly the value the contract was deployed with. Because
    no transition can mutate `balance` (it is `immutable` in Solidity),
    this predicate is equivalent to the invariant property `s.balance = initial`
    for the state `s` returned by `deploy initial`. -/
def obligationPredicate (s : ContractState) (initial : Nat) : Prop :=
  s.balance = initial

/-- Theorem: every deployment satisfies the A1 predicate. -/
theorem a1_trivial_constant_balance_safety :
    ∀ (initial : Nat), obligationPredicate (deploy initial) initial := by
  intro initial
  rfl

end Parallax5.Copilot.a1_trivial_constant_balance
