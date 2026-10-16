-- Arsenal Tactico: en multijugador la explosion la hace el servidor (pedido del cliente que disparo).
if not isServer() then return end

local function onClientCommand(module, command, player, args)
    if module ~= "ArsenalTactico" or command ~= "granada" then return end
    local sq = getCell():getGridSquare(args.x, args.y, args.z)
    if sq and player and math.abs(player:getX() - args.x) < 40 and math.abs(player:getY() - args.y) < 40 then
        ArsenalTactico.explode(sq, player)
    end
end

Events.OnClientCommand.Add(onClientCommand)
