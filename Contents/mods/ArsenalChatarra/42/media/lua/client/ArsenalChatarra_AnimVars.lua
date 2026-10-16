-- Arsenal de Chatarra: variable de animación "ACWeapon".
-- Los AnimSets del mod (media/AnimSets/player/melee/*/AC_*.xml) eligen el ataque propio
-- cuando ACWeapon coincide; con cualquier otra arma queda vacía y se usa el ataque vanilla.

local ANIM = {
    ["ArsenalChatarra.AC_RemoDestripador"] = "remo",
    ["ArsenalChatarra.AC_GarrasCarnicero"] = "garras",
}

local function update(player)
    if not player or not player.setVariable then return end
    local item = player:getPrimaryHandItem()
    local value = item and ANIM[item:getFullType()] or ""
    player:setVariable("ACWeapon", value)
end

Events.OnEquipPrimary.Add(function(character) update(character) end)
Events.OnGameStart.Add(function() update(getPlayer()) end)
