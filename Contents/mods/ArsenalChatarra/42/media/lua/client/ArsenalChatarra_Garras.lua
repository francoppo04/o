-- Arsenal de Chatarra: Garras de Carnicero en las dos manos.
-- El arma (guante derecho) va en la mano principal; mientras esté equipada se pone
-- automáticamente el guante izquierdo en la mano secundaria y se quita al desequiparla.

local MAIN = "ArsenalChatarra.AC_GarrasCarnicero"
local LEFT = "ArsenalChatarra.AC_GarrasCarniceroL"

local function removeLeftGloves(inv)
    -- también dentro de mochilas y bolsos
    local list = inv:getAllTypeRecurse(LEFT)
    for i = list:size() - 1, 0, -1 do
        local item = list:get(i)
        local container = item:getContainer() or inv
        container:Remove(item)
    end
end

local function syncGloves(player)
    if not player or not player.getInventory then return end
    local inv = player:getInventory()
    local primary = player:getPrimaryHandItem()
    local secondary = player:getSecondaryHandItem()
    local leftInHand = secondary and secondary:getFullType() == LEFT
    if primary and primary:getFullType() == MAIN then
        if leftInHand or secondary then return end   -- ya puesto, o la mano izquierda está ocupada
        local left = inv:getFirstTypeRecurse(LEFT) or inv:AddItem(LEFT)
        player:setSecondaryHandItem(left)
    else
        if leftInHand then player:setSecondaryHandItem(nil) end
        removeLeftGloves(inv)
    end
end

Events.OnEquipPrimary.Add(function(character) syncGloves(character) end)
Events.OnEquipSecondary.Add(function(character) syncGloves(character) end)
Events.OnGameStart.Add(function() syncGloves(getPlayer()) end)
