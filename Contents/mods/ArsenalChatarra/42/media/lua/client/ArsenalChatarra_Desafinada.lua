-- Arsenal de Chatarra: "Acorde final" de La Desafinada.
-- Cada swing con la guitarra hace ruido y atrae a los zombis cercanos.

local WEAPON = "ArsenalChatarra.AC_LaDesafinada"
local RADIUS = 20   -- casillas
local VOLUME = 20

local function onSwing(character, weapon)
    if not character or not weapon or weapon:getFullType() ~= WEAPON then
        return
    end
    addSound(character, character:getX(), character:getY(), character:getZ(), RADIUS, VOLUME)
end

Events.OnWeaponSwing.Add(onSwing)
