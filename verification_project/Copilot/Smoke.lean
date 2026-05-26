namespace Parallax5.Copilot.Smoke

structure VaultState where
  totalShares : Nat
  totalAssets : Nat
  deriving Repr

def conservationInvariant (s : VaultState) : Prop :=
  s.totalShares + 1000 > 0

theorem smoke_conservation (s : VaultState) :
    conservationInvariant s := by
  unfold conservationInvariant
  omega

end Parallax5.Copilot.Smoke
