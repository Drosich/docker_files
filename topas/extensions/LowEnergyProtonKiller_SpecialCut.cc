// Physics Module for LowEnergyProtonKiller_SpecialCut

#include "LowEnergyProtonKiller_SpecialCut.hh"

#include "TsParameterManager.hh"

#include "G4Proton.hh"
#include "G4ProcessManager.hh"
#include "G4UserSpecialCuts.hh"
#include "G4UserLimits.hh"
#include "G4LogicalVolume.hh"
#include "G4LogicalVolumeStore.hh"
#include "G4AutoLock.hh"
#include "G4SystemOfUnits.hh"
#include "G4ios.hh"

namespace { G4Mutex limitsMutex = G4MUTEX_INITIALIZER; }

LowEnergyProtonKiller_SpecialCut::LowEnergyProtonKiller_SpecialCut(TsParameterManager* pM)
  : G4VPhysicsConstructor("LowEnergyProtonKiller_SpecialCut"), fPm(pM) {}

void LowEnergyProtonKiller_SpecialCut::ConstructProcess()
{
    //Definir parámetro para controlar el corte en energia desde TOPAS
    G4String name = "Ph/" + fPm->GetStringParameter("Ph/ListName")
                + "/LowEnergyProtonKiller_SpecialCut/Threshold";
    G4double eMin = 10*MeV;
    if (fPm->ParameterExists(name))
    {
        eMin = fPm->GetDoubleParameter(name, "Energy");
    }

    // Registrar el proceso de corte solo para los protones
    G4ProcessManager* pm = G4Proton::Proton()->GetProcessManager();
    pm->AddDiscreteProcess(new G4UserSpecialCuts());

    // Los cortes en geant se aplican a regiones concretas. Como nosotros lo 
    // queremos para toda la simulacon, lo hacemos con un bucle
    G4AutoLock lock(&limitsMutex);
    G4int nVolumes = 0;
    for (G4LogicalVolume* lv : *G4LogicalVolumeStore::GetInstance()) 
    {
        G4UserLimits* ul = lv->GetUserLimits();
        if (ul)
        {
            ul->SetUserMinEkine(eMin);
        }
        else
        {
            lv->SetUserLimits(new G4UserLimits(DBL_MAX, DBL_MAX, DBL_MAX, eMin));
        }   
        ++nVolumes;
    }

    G4cout << "LowEnergyProtonKiller_SpecialCut: proton cut of " << eMin/MeV
            << " MeV set on " << nVolumes << " logical volumes" << G4endl;
    if (nVolumes == 0)
    G4cout << "LowEnergyProtonKiller_SpecialCut: WARNING, no volumes found; "
                "geometry was not built yet, so the cut is NOT active" << G4endl;
}
