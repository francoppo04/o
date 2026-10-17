-- Modo Creativo (núcleo): estado guardado con la partida, opciones y botón flotante.
--   * construir sin materiales ni herramientas (poder "BuildCheat" del jugador)
--   * acciones instantáneas, sin barra de progreso (poder "TimedActionInstant")
--   * todas las recetas, aunque no estén aprendidas (se olvidan al apagar)
-- La ventana está en ModoCreativo_UI.lua y el catálogo en ModoCreativo_Catalogo.lua.
-- Pensado para un jugador. Cada llamada al juego va protegida: si un nombre cambió, la ventana lo muestra
-- como "no disponible" y la consola lo anota con [ModoCreativo]; nada se rompe.

ModoCreativo = ModoCreativo or {}
local MC = ModoCreativo

MC.TECLA = Keyboard.KEY_INSERT
MC.OPCIONES = {
    {clave = "construir", titulo = "Construir gratis", metodo = "setBuildCheat",
     texto = "Todo lo del menu de construccion se puede hacer sin materiales ni herramientas."},
    {clave = "instantaneo", titulo = "Acciones instantaneas", metodo = "setTimedActionInstantCheat",
     texto = "Construir, desarmar, craftear o mover muebles se hace al instante, sin barra de progreso."},
    {clave = "recetas", titulo = "Todas las recetas", metodo = "learnRecipe",
     texto = "Aparecen todas las construcciones y recetas aunque no las hayas aprendido. Al apagar se olvidan.",
     aplicar = function(j, on) MC.recetas(j, on) end},
}

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
        md.ModoCreativo = {activo = false, construir = true, instantaneo = true, recetas = true}
    end
    if md.ModoCreativo.recetas == nil then md.ModoCreativo.recetas = true end     -- partidas de la versión anterior
    return md.ModoCreativo
end

function MC.disponible(metodo)
    local j = jugador()
    return j ~= nil and j[metodo] ~= nil
end

-- recetas: al prender se enseñan todas las que el personaje no sabía (construcción incluida) y se anotan;
-- al apagar se olvidan solo esas, así el personaje vuelve a saber exactamente lo que había aprendido jugando.
local function todasLasRecetas()
    local sm = getScriptManager()
    for _, metodo in ipairs({"getAllCraftRecipes", "getAllRecipes"}) do
        if sm[metodo] then
            local ok, lista = pcall(sm[metodo], sm)
            if ok and lista then return lista end
        end
    end
    print("[ModoCreativo] no se pudo leer la lista de recetas")
    return nil
end

function MC.recetas(j, on)
    local md = j:getModData()
    md.ModoCreativoRecetas = md.ModoCreativoRecetas or {}
    local ensenadas = md.ModoCreativoRecetas
    if on then
        local lista = todasLasRecetas()
        if not lista then return end
        local n = 0
        for i = 0, lista:size() - 1 do
            local r = lista:get(i)
            local ok, nombre = pcall(function() return r:getName() end)
            if ok and nombre and not ensenadas[nombre] then
                local sabe = false
                pcall(function() sabe = j:isRecipeKnown(r) end)
                if not sabe then pcall(function() sabe = j:isRecipeKnown(nombre) end) end
                if not sabe and llamar(j, "learnRecipe", nombre) then
                    ensenadas[nombre] = true
                    n = n + 1
                end
            end
        end
        if n > 0 then print("[ModoCreativo] recetas enseñadas: " .. n) end
    else
        local conocidas
        pcall(function() conocidas = j:getKnownRecipes() end)
        for nombre, _ in pairs(ensenadas) do
            if conocidas then pcall(function() conocidas:remove(nombre) end) end
        end
        md.ModoCreativoRecetas = {}
    end
end

function MC.aplicar(j)
    j = j or jugador()
    local e = MC.estado(j)
    if not e then return end
    for _, op in ipairs(MC.OPCIONES) do
        local on = e.activo and e[op.clave] == true
        if op.aplicar then op.aplicar(j, on) else llamar(j, op.metodo, on) end
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

MC.jugador = jugador
MC.llamar = llamar

-- ------------------------------------------------------------ botón flotante (arrastrable, con ícono)
MC.Lanzador = ISPanel:derive("ModoCreativoLanzador")
MC.ICONO = "media/textures/ModoCreativo_icono.png"

function MC.Lanzador:new(x, y)
    local o = ISPanel.new(self, x, y, 48, 48)
    o.moveWithMouse = true
    o.background = false
    o.icono = getTexture(MC.ICONO)
    return o
end

function MC.Lanzador:prerender()
    local e = MC.estado()
    local on = e and e.activo
    local hover = self:isMouseOver()
    self:drawRect(0, 0, self.width, self.height, hover and 0.85 or 0.7, 0.08, 0.09, 0.1)
    if on then
        self:drawRectBorder(0, 0, self.width, self.height, 1, 0.35, 0.85, 0.35)
        self:drawRectBorder(1, 1, self.width - 2, self.height - 2, 1, 0.35, 0.85, 0.35)
    else
        self:drawRectBorder(0, 0, self.width, self.height, 0.8, 0.5, 0.5, 0.5)
    end
    if self.icono then
        self:drawTextureScaledAspect(self.icono, 6, 6, self.width - 12, self.height - 12, 1, 1, 1, 1)
    else
        self:drawTextCentre("MC", self.width / 2, self.height / 2 - 8, 1, 1, 1, 1, UIFont.Medium)
    end
    if hover then
        local txt = (on and "Modo Creativo: activado" or "Modo Creativo: apagado") .. "  (Insert)"
        local w = getTextManager():MeasureStringX(UIFont.Small, txt) + 12
        self:drawRect(self.width + 6, 12, w, 22, 0.85, 0.05, 0.05, 0.05)
        self:drawText(txt, self.width + 12, 15, 1, 1, 1, 1, UIFont.Small)
    end
end

function MC.Lanzador:onMouseDown(x, y)
    self.clickX, self.clickY = getMouseX(), getMouseY()
    return ISPanel.onMouseDown(self, x, y)
end

function MC.Lanzador:onMouseUp(x, y)
    ISPanel.onMouseUp(self, x, y)
    -- click sin arrastrar: abre la ventana; si se arrastró, guarda la posición
    if self.clickX and math.abs(getMouseX() - self.clickX) < 4 and math.abs(getMouseY() - self.clickY) < 4 then
        MC.abrirCerrar()
    else
        local e = MC.estado()
        if e then e.lanzadorX, e.lanzadorY = self:getX(), self:getY() end
    end
    self.clickX = nil
    return true
end

function MC.Lanzador:actualizar() end

local function alCrearJugador(indice, j)
    if indice ~= 0 then return end
    if not MC.lanzador then
        local e = MC.estado(j)
        local x = (e and e.lanzadorX) or 12
        local y = (e and e.lanzadorY) or (getCore():getScreenHeight() / 2 - 24)
        MC.lanzador = MC.Lanzador:new(x, y)
        MC.lanzador:initialise()
        MC.lanzador:addToUIManager()
    end
    MC.aplicar(j)                 -- los poderes del jugador no se guardan: se reaplican al cargar
end

local function alTecla(tecla)
    if tecla == MC.TECLA and jugador() then MC.abrirCerrar() end
    if tecla == Keyboard.KEY_R and MC.rotar then MC.rotar() end                 -- rota el objeto del catálogo
    if tecla == Keyboard.KEY_ESCAPE and MC.soltar then MC.soltar() end          -- suelta la herramienta
end

Events.OnCreatePlayer.Add(alCrearJugador)
Events.OnKeyPressed.Add(alTecla)
