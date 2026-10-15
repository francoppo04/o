-- Arsenal de Chatarra: agrega las armas al loot.
-- Cada lista se busca antes de usarla; las que no existen en esta versión del
-- juego se saltean y se avisan en console.txt con el prefijo [ArsenalChatarra].

require "Items/ProceduralDistributions"

local LOOT = {
    -- lista vanilla           = { {item, peso}, ... }
    GarageTools     = { {"ArsenalChatarra.AC_MacheteSierra", 0.5}, {"ArsenalChatarra.AC_BateEncadenado", 0.8} },
    CrateTools      = { {"ArsenalChatarra.AC_HachaRemachada", 0.4}, {"ArsenalChatarra.AC_MazoSenal", 0.3} },
    ToolStoreTools  = { {"ArsenalChatarra.AC_HachaRemachada", 0.3}, {"ArsenalChatarra.AC_EstoqueBarra", 0.5} },
    CampingStoreGear = { {"ArsenalChatarra.AC_MacheteSierra", 0.4} },
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
