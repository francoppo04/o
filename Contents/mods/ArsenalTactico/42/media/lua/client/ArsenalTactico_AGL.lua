-- Arsenal Tactico: Cyclone-AGL. El disparo es el de una escopeta vanilla (un proyectil, mucho dano al
-- blanco directo); en el momento del disparo se busca el punto de impacto sobre la linea de tiro (primer
-- zombi cerca de la linea o primera pared) y ahi explota la granada. No arma a menos de 3 casillas.
ArsenalTactico = ArsenalTactico or {}

local AGL = "Base.AT_CycloneAGL"
local ARM_DIST = 3.0
local pending = {}

local function impact(player, weapon)
    local cell = getCell()
    local px, py, pz = player:getX(), player:getY(), math.floor(player:getZ())
    local dir = player:getForwardDirection()
    local dx, dy = dir:getX(), dir:getY()
    local len = math.sqrt(dx * dx + dy * dy)
    if len < 0.001 then return nil end
    dx, dy = dx / len, dy / len
    local range = weapon:getMaxRange() or 24
    -- primer zombi cerca de la linea de tiro
    local best = range
    local zs = cell:getZombieList()
    for i = 0, zs:size() - 1 do
        local z = zs:get(i)
        if z and not z:isDead() and math.floor(z:getZ()) == pz then
            local rx, ry = z:getX() - px, z:getY() - py
            local along = rx * dx + ry * dy
            if along > 0.5 and along < best and math.abs(rx * dy - ry * dx) < 0.8 then
                best = along
            end
        end
    end
    -- primera pared o puerta cerrada en el camino
    local prev = cell:getGridSquare(math.floor(px), math.floor(py), pz)
    local t = 0.4
    while t <= best do
        local sq = cell:getGridSquare(math.floor(px + dx * t), math.floor(py + dy * t), pz)
        if not sq then break end
        if prev and sq ~= prev then
            local blocked = false
            pcall(function() blocked = prev:isBlockedTo(sq) end)
            if blocked then return prev, t end
        end
        prev = sq
        t = t + 0.4
    end
    return cell:getGridSquare(math.floor(px + dx * best), math.floor(py + dy * best), pz) or prev, best
end

-- antes del disparo: anotar si el arma va a disparar de verdad (tiene granada en la recamara)
local function onAttack(character, chargeDelta, weapon)
    if weapon and weapon:getFullType() == AGL and ISReloadWeaponAction.canShoot(character, weapon) then
        pending[character] = true
    end
end

-- en el disparo (mismo evento que usa vanilla para gastar la municion)
local function onHitPoint(player, weapon)
    if not weapon or weapon:getFullType() ~= AGL or not pending[player] then return end
    pending[player] = nil
    local sq, dist = impact(player, weapon)
    if not sq or dist < ARM_DIST then return end      -- sin armar: solo el golpe directo
    if isClient() then
        sendClientCommand(player, "ArsenalTactico", "granada", {x = sq:getX(), y = sq:getY(), z = sq:getZ()})
    else
        ArsenalTactico.explode(sq, player)
    end
end

Hook.Attack.Add(onAttack)
Events.OnWeaponSwingHitPoint.Add(onHitPoint)
