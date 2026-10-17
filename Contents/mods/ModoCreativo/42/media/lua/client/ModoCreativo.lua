-- Modo Creativo: un botón (y la tecla Insert) prende y apaga
--   * construir sin materiales ni herramientas (poder "BuildCheat" del juego)
--   * acciones instantáneas, sin barra de progreso (poder "TimedActionInstant")
-- Pensado para un jugador. Cada llamada va protegida: si un nombre del juego cambió, avisa en la consola y sigue.

ModoCreativo = ModoCreativo or {}
local MC = ModoCreativo

MC.TECLA = Keyboard.KEY_INSERT

local function llamar(obj, metodo, ...)
    local f = obj and obj[metodo]
    if not f then
        print("[ModoCreativo] no existe " .. metodo)
        return false
    end
    local ok, err = pcall(f, obj, ...)
    if not ok then print("[ModoCreativo] error en " .. metodo .. ": " .. tostring(err)) end
    return ok
end

function MC.activo(jugador)
    return jugador and jugador:getModData().ModoCreativo == true
end

function MC.aplicar(jugador)
    if not jugador then return end
    local on = MC.activo(jugador)
    llamar(jugador, "setBuildCheat", on)
    llamar(jugador, "setTimedActionInstantCheat", on)
    if ISBuildMenu then ISBuildMenu.cheat = on end          -- menú de construcción clásico
    if MC.boton then MC.boton:actualizar() end
end

function MC.alternar(jugador)
    jugador = jugador or getSpecificPlayer(0)
    if not jugador then return end
    jugador:getModData().ModoCreativo = not MC.activo(jugador)
    MC.aplicar(jugador)
    local on = MC.activo(jugador)
    llamar(jugador, "setHaloNote", on and "Modo creativo: ON" or "Modo creativo: OFF",
           on and 120 or 255, on and 255 or 120, 120, 300)
end

-- ------------------------------------------------------------ botón en pantalla (arrastrable)
MC.Boton = ISPanel:derive("ModoCreativoBoton")

function MC.Boton:new(x, y)
    local o = ISPanel.new(self, x, y, 150, 28)
    o.moveWithMouse = true
    o.background = true
    o.backgroundColor = {r = 0, g = 0, b = 0, a = 0.6}
    o.borderColor = {r = 1, g = 1, b = 1, a = 0.4}
    return o
end

function MC.Boton:createChildren()
    self.btn = ISButton:new(4, 4, self.width - 8, self.height - 8, "", self, MC.Boton.onClick)
    self.btn:initialise()
    self:addChild(self.btn)
    self:actualizar()
end

function MC.Boton:onClick()
    MC.alternar(getSpecificPlayer(0))
end

function MC.Boton:actualizar()
    if not self.btn then return end
    local on = MC.activo(getSpecificPlayer(0))
    self.btn:setTitle(on and "Creativo: ON" or "Creativo: OFF")
    self.btn.backgroundColor = on and {r = 0.1, g = 0.45, b = 0.1, a = 0.9} or {r = 0.25, g = 0.25, b = 0.25, a = 0.9}
end

local function crearBoton()
    if MC.boton then return end
    MC.boton = MC.Boton:new(getCore():getScreenWidth() / 2 - 75, 8)
    MC.boton:initialise()
    MC.boton:addToUIManager()
end

local function alCrearJugador(indice, jugador)
    if indice ~= 0 then return end
    crearBoton()
    MC.aplicar(jugador)
end

local function alTecla(tecla)
    if tecla == MC.TECLA and getSpecificPlayer(0) then MC.alternar(getSpecificPlayer(0)) end
end

-- los poderes del jugador no se guardan con la partida: se reaplican al cargar
Events.OnCreatePlayer.Add(alCrearJugador)
Events.OnKeyPressed.Add(alTecla)
