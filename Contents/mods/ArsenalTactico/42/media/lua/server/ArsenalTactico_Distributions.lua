-- Arsenal Táctico: botín. Generado por tools/build_arsenal_tactico.py (editar la tabla LOOT).
-- Tolera contenedores que no existan (versiones del juego / otros mods).
local LOOT = {
    FirearmWeapons_Mid = { "Base.AT_M4", 1, "Base.AT_MCX", 0.5, "Base.AT_AK101", 0.5, "Base.AT_G19", 2, "Base.AT_Marlin336", 1 },
    FirearmWeapons_Late = { "Base.AT_M4", 1, "Base.AT_MCX", 0.5, "Base.AT_AK101", 0.5, "Base.AT_G19", 2, "Base.AT_Marlin336", 1, "Base.AT_TacLight", 0.5, "Base.AT_HoloSight", 0.5 },
    GunStoreGuns = { "Base.AT_G19", 2, "Base.AT_Marlin336", 1 },
    GunStorePistols = { "Base.AT_G19", 4, "Base.AT_TacLight", 1 },
    GunStoreRifles = { "Base.AT_Marlin336", 2, "Base.AT_MCX", 0.5, "Base.AT_LPVO", 1 },
    GunStoreAccessories = { "Base.AT_ACOG", 1, "Base.AT_LPVO", 1, "Base.AT_HoloSight", 2, "Base.AT_Thermal", 0.3, "Base.AT_TacLight", 2 },
    GunStoreMagsAmmo = { "Base.AT_SkullMag", 1, "Base.AT_LancerMag", 1, "Base.AT_AKMag", 1, "Base.AT_G19Mag", 2 },
    PawnShopGunsSpecial = { "Base.AT_M4", 1, "Base.AT_MCX", 1, "Base.AT_AK101", 1, "Base.AT_Thermal", 0.3 },
    PoliceStorageGuns = { "Base.AT_G19", 4, "Base.AT_TacLight", 1 },
    PoliceStorageAmmunition = { "Base.AT_G19Mag", 4 },
    SWATStorageGuns = { "Base.AT_M4", 4, "Base.AT_MCX", 3, "Base.AT_G19", 4, "Base.AT_TacLight", 3, "Base.AT_HoloSight", 2, "Base.AT_ACOG", 2 },
    SWATStorageAmmunition = { "Base.AT_SkullMag", 4, "Base.AT_LancerMag", 3, "Base.AT_G19Mag", 4 },
    ArmyStorageGuns = { "Base.AT_M4", 4, "Base.AT_ACOG", 2, "Base.AT_Thermal", 0.5 },
    ArmyStorageAmmunition = { "Base.AT_SkullMag", 4 },
    DrugLabGuns = { "Base.AT_AK101", 2, "Base.AT_G19", 2, "Base.AT_AKMag", 2 },
    DrugShackWeapons = { "Base.AT_AK101", 1, "Base.AT_G19", 1 },
    Hunter = { "Base.AT_Marlin336", 2 },
    HuntingLockers = { "Base.AT_Marlin336", 2, "Base.AT_LPVO", 1 },
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
