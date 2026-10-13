#ifndef LowEnergyProtonKiller_SpecialCut_hh
#define LowEnergyProtonKiller_SpecialCut_hh

#include "G4VPhysicsConstructor.hh"

class TsParameterManager;

// Physics module: adds G4UserSpecialCuts to protons and sets a minimum
// kinetic energy (G4UserLimits) on every logical volume. Protons below the
// threshold are stopped and their remaining kinetic energy is deposited locally.
class LowEnergyProtonKiller_SpecialCut : public G4VPhysicsConstructor
{
public:
  LowEnergyProtonKiller_SpecialCut(TsParameterManager* pM);
  void ConstructParticle() override {}
  void ConstructProcess() override;

private:
  TsParameterManager* fPm;
};

#endif
