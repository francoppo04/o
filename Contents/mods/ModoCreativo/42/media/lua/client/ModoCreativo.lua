-- Modo Creativo: ventana para prender y apagar
--   * construir sin materiales ni herramientas (poder "BuildCheat" del jugador)
--   * acciones instantáneas, sin barra de progreso (poder "TimedActionInstant")
-- Se abre con el botón flotante "Creativo" (arrastrable) o con la tecla Insert.
-- Pensado para un jugador. Cada llamada al juego va protegida: si un nombre cambió, la ventana lo muestra
-- como "no disponible" y la consola lo anota con [ModoCreativo]; nada se rompe.

ModoCreativo = ModoCreativo or {}
local MC = ModoCreativo

MC.TECLA = Keyboard.KEY_INSERT
MC.OPCIONES = {
    {clave = "construir", texto = "Construir sin materiales ni herramientas", metodo = "setBuildCheat"},
    {clave = "instantaneo", texto = "Acciones instantaneas (sin barra de progreso)", metodo = "setTimedActionInstantCheat"},
}

local VERDE = {r = 0.15, g = 0.5, b = 0.15, a = 0.95}
local GRIS = {r = 0.25, g = 0.25, b = 0.25, a = 0.95}

local function jugador()
    return getSpecificPlayer(0)
end

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

-- estado guardado con la partida: {activo = bool, construir = bool, instantaneo = bool}
function MC.estado(j)
    j = j or jugador()
    if not j then return nil end
    local md = j:getModData()
    if type(md.ModoCreativo) ~= "table" then
        md.ModoCreativo = {activo = false, construir = true, instantaneo = true}
    end
    return md.ModoCreativo
end

function MC.disponible(metodo)
    local j = jugador()
    return j ~= nil and j[metodo] ~= nil
end

function MC.aplicar(j)
    j = j or jugador()
    local e = MC.estado(j)
    if not e then return end
    for _, op in ipairs(MC.OPCIONES) do
        llamar(j, op.metodo, e.activo and e[op.clave] == true)
    end
    if ISBuildMenu then ISBuildMenu.cheat = e.activo and e.construir == true end   -- menú de construcción clásico
    if MC.lanzador then MC.lanzador:actualizar() end
    if MC.ventana then MC.ventana:actualizar() end
end

function MC.setActivo(on)
    local j = jugador()
    local e = MC.estado(j)
    if not e then return end
    e.activo = on
    MC.aplicar(j)
    llamar(j, "setHaloNote", on and "Modo creativo: ON" or "Modo creativo: OFF",
           on and 120 or 255, on and 255 or 120, 120, 300)
end

-- ------------------------------------------------------------ ventana
MC.Ventana = ISCollapsableWindow:derive("ModoCreativoVentana")

function MC.Ventana:new(x, y)
    local o = ISCollapsableWindow.new(self, x, y, 380, 230)
    o.title = "Modo Creativo"
    o.resizable = false
    return o
end

function MC.Ventana:createChildren()
    ISCollapsableWindow.createChildren(self)
    local y = self:titleBarHeight() + 10
    local font = getTextManager():getFontHeight(UIFont.Medium)

    self.principal = ISButton:new(10, y, self.width - 20, font + 16, "", self, MC.Ventana.onPrincipal)
    self.principal:initialise()
    self.principal.font = UIFont.Medium
    self:addChild(self.principal)
    y = y + self.principal.height + 12

    self.ticks = ISTickBox:new(10, y, self.width - 20, 20, "", self, MC.Ventana.onTick)
    self.ticks:initialise()
    self:addChild(self.ticks)
    for _, op in ipairs(MC.OPCIONES) do
        self.ticks:addOption(op.texto)
    end
    y = y + self.ticks:getHeight() + 10

    self.catalogo = ISButton:new(10, y, self.width - 20, font + 12, "Catalogo de construccion (todos los objetos)",
                                 self, function() if MC.abrirCatalogo then MC.abrirCatalogo() end end)
    self.catalogo:initialise()
    self:addChild(self.catalogo)
    y = y + self.catalogo.height + 10

    self.aviso = ISLabel:new(10, y, 18, "", 1, 0.8, 0.4, 1, UIFont.Small, true)
    self:addChild(self.aviso)
    y = y + 22

    self.ayuda = ISLabel:new(10, y, 18, "Tecla Insert: abrir o cerrar esta ventana.", 0.7, 0.7, 0.7, 1,
                             UIFont.Small, true)
    self:addChild(self.ayuda)
    self:setHeight(y + 28)
    self:actualizar()
end

function MC.Ventana:onPrincipal()
    local e = MC.estado()
    if e then MC.setActivo(not e.activo) end
end

function MC.Ventana:onTick(indice, marcado)
    local e = MC.estado()
    local op = MC.OPCIONES[indice]
    if not e or not op then return end
    e[op.clave] = marcado
    MC.aplicar()
end

function MC.Ventana:actualizar()
    local e = MC.estado()
    if not e or not self.principal then return end
    self.principal:setTitle(e.activo and "MODO CREATIVO: ACTIVADO" or "MODO CREATIVO: DESACTIVADO")
    self.principal.backgroundColor = e.activo and VERDE or GRIS
    local faltan = {}
    for i, op in ipairs(MC.OPCIONES) do
        self.ticks:setSelected(i, e[op.clave] == true)
        if not MC.disponible(op.metodo) then table.insert(faltan, op.texto) end
    end
    self.aviso:setName(#faltan > 0 and ("No disponible en esta version: " .. table.concat(faltan, ", ")) or "")
end

function MC.Ventana:close()
    self:setVisible(false)
    self:removeFromUIManager()
    MC.ventana = nil
end

function MC.abrirCerrar()
    if MC.ventana then
        MC.ventana:close()
        return
    end
    local x = MC.lanzador and MC.lanzador:getX() or getCore():getScreenWidth() / 2 - 190
    local y = MC.lanzador and (MC.lanzador:getY() + MC.lanzador:getHeight() + 4) or 60
    MC.ventana = MC.Ventana:new(x, y)
    MC.ventana:initialise()
    MC.ventana:addToUIManager()
end

-- ------------------------------------------------------------ botón flotante (arrastrable)
MC.Lanzador = ISPanel:derive("ModoCreativoLanzador")

function MC.Lanzador:new(x, y)
    local o = ISPanel.new(self, x, y, 110, 30)
    o.moveWithMouse = true
    o.background = true
    o.backgroundColor = {r = 0, g = 0, b = 0, a = 0.5}
    o.borderColor = {r = 1, g = 1, b = 1, a = 0.3}
    return o
end

function MC.Lanzador:createChildren()
    self.btn = ISButton:new(4, 4, self.width - 8, self.height - 8, "Creativo", self, MC.abrirCerrar)
    self.btn:initialise()
    self:addChild(self.btn)
    self:actualizar()
end

function MC.Lanzador:actualizar()
    local e = MC.estado()
    if not self.btn or not e then return end
    self.btn.backgroundColor = e.activo and VERDE or GRIS
end

local function alCrearJugador(indice, j)
    if indice ~= 0 then return end
    if not MC.lanzador then
        MC.lanzador = MC.Lanzador:new(getCore():getScreenWidth() / 2 - 55, 8)
        MC.lanzador:initialise()
        MC.lanzador:addToUIManager()
    end
    MC.aplicar(j)                 -- los poderes del jugador no se guardan: se reaplican al cargar
end

local function alTecla(tecla)
    if tecla == MC.TECLA and jugador() then MC.abrirCerrar() end
    if tecla == Keyboard.KEY_ESCAPE and MC.soltar then MC.soltar() end      -- suelta la herramienta del catálogo
end

Events.OnCreatePlayer.Add(alCrearJugador)
Events.OnKeyPressed.Add(alTecla)
