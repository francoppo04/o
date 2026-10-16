-- Arsenal de Chatarra: agrega las armas al loot.
-- Cada lista se busca antes de usarla; las que no existen en esta versión del
-- juego se saltean y se avisan en console.txt con el prefijo [ArsenalChatarra].

require "Items/ProceduralDistributions"

local LOOT = {
    -- lista vanilla            = { {item, peso}, ... }
    GarageTools         = { {"ArsenalChatarra.AC_BateErizo", 0.6}, {"ArsenalChatarra.AC_Hachamazo", 0.2},
                            {"ArsenalChatarra.AC_GarrasCarnicero", 0.3}, {"ArsenalChatarra.AC_RemoDestripador", 0.2},
                            {"ArsenalChatarra.AC_TridenteCarnicero", 0.3}, {"ArsenalChatarra.AC_PalaTiburon", 0.5},
                            {"ArsenalChatarra.AC_LanzaTijera", 0.3}, {"ArsenalChatarra.AC_GuadanaGolf", 0.2} },
    CrateTools          = { {"ArsenalChatarra.AC_Hachamazo", 0.3}, {"ArsenalChatarra.AC_PareDefinitivo", 0.2},
                            {"ArsenalChatarra.AC_GarrasCarnicero", 0.3}, {"ArsenalChatarra.AC_RemoDestripador", 0.2},
                            {"ArsenalChatarra.AC_SartenInfierno", 0.3}, {"ArsenalChatarra.AC_KatanaBallesta", 0.1},
                            {"ArsenalChatarra.AC_GuadanaGolf", 0.2} },
    ToolStoreTools      = { {"ArsenalChatarra.AC_PareDefinitivo", 0.2}, {"ArsenalChatarra.AC_PalaTiburon", 0.3} },
    FireStorageTools    = { {"ArsenalChatarra.AC_Hachamazo", 1.0} },
    MusicStoreOthers    = { {"ArsenalChatarra.AC_LaDesafinada", 0.8} },
    MusicStoreGuitar    = { {"ArsenalChatarra.AC_LaDesafinada", 1.0} },
    BandPracticeInstruments = { {"ArsenalChatarra.AC_LaDesafinada", 1.0} },
    CrateInstruments    = { {"ArsenalChatarra.AC_LaDesafinada", 0.6} },
}

local function addLoot()
    if not ProceduralDistributions or not ProceduralDistributions.list then
        print("[ArsenalChatarra] ProceduralDistributions no disponible; loot no agregado")
        return
    end
    for listName, entries in pairs(LOOT) do
        local dist = ProceduralDistributions.list[listName]
        if dist and dist.items then
            for _, entry in ipairs(entries) do
                table.insert(dist.items, entry[1])
                table.insert(dist.items, entry[2])
            end
        else
            print("[ArsenalChatarra] lista de loot no encontrada: " .. listName)
        end
    end
end

Events.OnPreDistributionMerge.Add(addLoot)
