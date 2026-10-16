-- Arsenal Tactico: explosion de la granada de 40 mm (Cyclone-AGL).
-- Usa la explosion de trampa vanilla (IsoTrap + item con ExplosionPower, como la bomba casera); si esa
-- API no responde en esta version, hace una explosion manual (dano en area + sonido) y lo avisa en consola.
ArsenalTactico = ArsenalTactico or {}

local CHARGE = "Base.AT_Granada40Carga"
local RADIUS = 3.5          -- casillas: muerte segura en el centro, derribo en el borde

local function viaTrap(sq, player)
    local item = instanceItem(CHARGE)
    if not item then return false, "no existe " .. CHARGE end
    local ok, err = pcall(function()
        local trap = IsoTrap.new(player, item, sq:getCell(), sq)
        trap:triggerExplosion(false)
    end)
    if ok then return true end
    local ok2, err2 = pcall(function()
        local trap = IsoTrap.new(item, sq:getCell(), sq)
        trap:triggerExplosion(false)
    end)
    if ok2 then return true end
    return false, tostring(err) .. " / " .. tostring(err2)
end

local function manual(sq, player)
    local x, y, z = sq:getX() + 0.5, sq:getY() + 0.5, sq:getZ()
    getSoundManager():PlayWorldSound("PipeBombExplode", sq, 0, 40, 1.0, false)
    addSound(player, sq:getX(), sq:getY(), z, 80, 100)
    local zs = sq:getCell():getZombieList()
    for i = zs:size() - 1, 0, -1 do
        local zed = zs:get(i)
        if zed and not zed:isDead() and math.floor(zed:getZ()) == z then
            local d = math.sqrt((zed:getX() - x) ^ 2 + (zed:getY() - y) ^ 2)
            if d <= RADIUS * 0.6 then
                zed:setHealth(0)
                pcall(function() zed:Kill(player) end)
            elseif d <= RADIUS then
                pcall(function() zed:knockDown(true) end)
                zed:setHealth(zed:getHealth() * 0.4)
            end
        end
    end
end

function ArsenalTactico.explode(sq, player)
    if not sq then return end
    local ok, err = viaTrap(sq, player)
    if ok then
        print("[ArsenalTactico] granada 40mm: explosion (IsoTrap) en " .. sq:getX() .. "," .. sq:getY())
    else
        print("[ArsenalTactico] granada 40mm: IsoTrap no disponible (" .. tostring(err) .. "), explosion manual")
        manual(sq, player)
    end
end
