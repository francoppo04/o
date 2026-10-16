-- Arsenal Táctico: botín. Generado por tools/build_arsenal_tactico.py (editar la tabla LOOT).
-- Tolera contenedores que no existan (versiones del juego / otros mods).
local LOOT = {
    FirearmWeapons_Mid = { "Base.AT_M4", 1, "Base.AT_MCX", 0.5, "Base.AT_AK101", 0.5, "Base.AT_G19", 2, "Base.AT_Marlin336", 1, "Base.AT_GXP", 1, "Base.AT_GravRecon", 1, "Base.AT_VikorS1", 1, "Base.AT_MD34", 0.7, "Base.AT_MX4", 0.5 },
    FirearmWeapons_Late = { "Base.AT_M4", 1, "Base.AT_MCX", 0.5, "Base.AT_AK101", 0.5, "Base.AT_G19", 2, "Base.AT_Marlin336", 1, "Base.AT_TacLight", 0.5, "Base.AT_HoloSight", 0.5, "Base.AT_AUGA5", 0.5, "Base.AT_Komodo", 0.4, "Base.AT_AG203", 0.4, "Base.AT_FNSAR", 0.3, "Base.AT_QDX99", 0.3 },
    GunStoreGuns = { "Base.AT_G19", 2, "Base.AT_Marlin336", 1, "Base.AT_GXP", 1, "Base.AT_MD34", 1 },
    GunStorePistols = { "Base.AT_G19", 4, "Base.AT_TacLight", 1, "Base.AT_GXP", 2, "Base.AT_GravRecon", 2, "Base.AT_VikorS1", 2, "Base.AT_MD34", 1.5, "Base.AT_FNPR", 0.5 },
    GunStoreRifles = { "Base.AT_Marlin336", 2, "Base.AT_MCX", 0.5, "Base.AT_LPVO", 1, "Base.AT_MX4", 0.7, "Base.AT_AUGA5", 0.5, "Base.AT_Komodo", 0.4 },
    GunStoreAccessories = { "Base.AT_ACOG", 1, "Base.AT_LPVO", 1, "Base.AT_HoloSight", 2, "Base.AT_Thermal", 0.3, "Base.AT_TacLight", 2 },
    GunStoreMagsAmmo = { "Base.AT_SkullMag", 1, "Base.AT_LancerMag", 1, "Base.AT_AKMag", 1, "Base.AT_G19Mag", 2, "Base.AT_GXPMag", 1, "Base.AT_GravMag", 1, "Base.AT_VikorMag", 1, "Base.AT_MD34Mag", 1, "Base.AT_MX4Mag", 0.7, "Base.AT_AUGMag", 0.5, "Base.AT_KomodoMag", 0.4 },
    PawnShopGunsSpecial = { "Base.AT_M4", 1, "Base.AT_MCX", 1, "Base.AT_AK101", 1, "Base.AT_Thermal", 0.3, "Base.AT_FNPR", 0.5, "Base.AT_QDX99", 0.5, "Base.AT_AG203", 0.5 },
    PoliceStorageGuns = { "Base.AT_G19", 4, "Base.AT_TacLight", 1, "Base.AT_GXP", 2, "Base.AT_GravRecon", 2, "Base.AT_MX4", 1 },
    PoliceStorageAmmunition = { "Base.AT_G19Mag", 4, "Base.AT_GXPMag", 2, "Base.AT_GravMag", 2, "Base.AT_MX4Mag", 1 },
    SWATStorageGuns = { "Base.AT_M4", 4, "Base.AT_MCX", 3, "Base.AT_G19", 4, "Base.AT_TacLight", 3, "Base.AT_HoloSight", 2, "Base.AT_ACOG", 2, "Base.AT_FNSAR", 2, "Base.AT_QDX99", 1, "Base.AT_AUGA5", 1, "Base.AT_PSR", 0.5, "Base.AT_FNPR", 1 },
    SWATStorageAmmunition = { "Base.AT_SkullMag", 4, "Base.AT_LancerMag", 3, "Base.AT_G19Mag", 4, "Base.AT_SARMag", 2, "Base.AT_QDXMag", 1, "Base.AT_AUGMag", 1, "Base.AT_PSRMag", 0.5, "Base.AT_FNPRMag", 1 },
    ArmyStorageGuns = { "Base.AT_M4", 4, "Base.AT_ACOG", 2, "Base.AT_Thermal", 0.5, "Base.AT_RPK101", 1, "Base.AT_Komodo", 1, "Base.AT_AG203", 1, "Base.AT_PSR", 0.5, "Base.AT_CycloneAGL", 0.4 },
    ArmyStorageAmmunition = { "Base.AT_SkullMag", 4, "Base.AT_RPKDrum", 1, "Base.AT_KomodoMag", 1, "Base.AT_AG203Mag", 1, "Base.AT_PSRMag", 0.5, "Base.AT_Granada40", 2 },
    DrugLabGuns = { "Base.AT_AK101", 2, "Base.AT_G19", 2, "Base.AT_AKMag", 2, "Base.AT_VikorS1", 1, "Base.AT_QDX99", 0.5 },
    DrugShackWeapons = { "Base.AT_AK101", 1, "Base.AT_G19", 1, "Base.AT_VikorS1", 1 },
    Hunter = { "Base.AT_Marlin336", 2 },
    HuntingLockers = { "Base.AT_Marlin336", 2, "Base.AT_LPVO", 1, "Base.AT_PSR", 0.2 },
}

local function addLoot()
    local dist = ProceduralDistributions and ProceduralDistributions.list
    if not dist then return end
    for name, entries in pairs(LOOT) do
        local cont = dist[name]
        if cont and cont.items then
            for i = 1, #entries do table.insert(cont.items, entries[i]) end
        end
    end
end

Events.OnPreDistributionMerge.Add(addLoot)
