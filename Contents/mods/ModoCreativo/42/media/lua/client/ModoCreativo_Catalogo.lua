-- Modo Creativo: catálogo de construcción. Todos los tiles del juego (paredes, pisos, muebles, accesorios,
-- cercas, techos, vegetación...) agrupados por categoría y hoja de tiles, con buscador. Click en un tile y
-- después click en el mundo para colocarlo (también los que el juego no deja construir). Modo "Borrar" para
-- sacar el objeto de más arriba de un cuadro. Click derecho o Esc suelta la herramienta.
-- Igual que el resto del mod, cada llamada al juego va protegida y deja rastro [ModoCreativo] en la consola.

require "ISUI/ISCollapsableWindow"
require "ISUI/ISPanel"
require "BuildingObjects/ISBuildingObject"

ModoCreativo = ModoCreativo or {}
local MC = ModoCreativo

local CELDA = 76
local CATEGORIAS = {
    walls = "Paredes", floors = "Pisos", furniture = "Muebles", fixtures = "Accesorios", appliances = "Electrodomesticos",
    location = "Lugares", fencing = "Cercas", vegetation = "Vegetacion", roofs = "Techos", street = "Calle",
    construction = "Construccion", lighting = "Luces", carpentry = "Carpinteria", industry = "Industria",
    trashcontainers = "Basura", signs = "Carteles", blends = "Mezclas de suelo", d = "Puertas", doors = "Puertas",
    fixtures_doors = "Puertas", recreational = "Recreacion", camping = "Campamento", security = "Seguridad",
}

local function log(msg)
    print("[ModoCreativo] " .. msg)
end

local function categoriaDe(tileset)
    local pre = string.match(tileset, "^([^_]+)") or tileset
    return CATEGORIAS[pre] or pre
end

-- ------------------------------------------------------------ datos
function MC.tilesets()
    if MC._tilesets then return MC._tilesets end
    local lista = {}
    local ok, nombres = pcall(function() return getWorld():getAllTilesName() end)
    if ok and nombres then
        for i = 0, nombres:size() - 1 do table.insert(lista, nombres:get(i)) end
    else
        log("no se pudo leer la lista de hojas de tiles (getAllTilesName): " .. tostring(nombres))
    end
    table.sort(lista)
    MC._tilesets = lista
    return lista
end

function MC.tilesDe(tileset)
    MC._tiles = MC._tiles or {}
    if MC._tiles[tileset] then return MC._tiles[tileset] end
    local lista = {}
    local ok, t = pcall(function() return getWorld():getAllTiles(tileset) end)
    if ok and t then
        for i = 0, t:size() - 1 do
            local nombre = t:get(i)
            if getTexture(nombre) then table.insert(lista, nombre) end      -- solo los que tienen imagen
        end
    else
        log("no se pudieron leer los tiles de " .. tileset .. ": " .. tostring(t))
    end
    MC._tiles[tileset] = lista
    return lista
end

-- ------------------------------------------------------------ colocar y borrar en el mundo
local function cuadro(x, y, z)
    local cell = getCell()
    local sq = cell:getGridSquare(x, y, z)
    if not sq then
        local ok, nuevo = pcall(function() return cell:createNewGridSquare(x, y, z, true) end)
        if ok then sq = nuevo end
    end
    return sq
end

function MC.colocar(sprite, x, y, z)
    local sq = cuadro(x, y, z)
    if not sq then log("no hay cuadro en " .. x .. "," .. y .. "," .. z) return end
    local obj
    local ok = pcall(function() obj = IsoObject.new(getCell(), sq, sprite) end)
    if not (ok and obj) then
        ok = pcall(function() obj = IsoObject.new(sq, sprite, nil, false) end)
    end
    if not (ok and obj) then log("no se pudo crear el objeto " .. sprite) return end
    pcall(function() obj:createContainersFromSpriteProperties() end)     -- muebles con contenedor
    sq:AddTileObject(obj)
    pcall(function() obj:transmitCompleteItemToServer() end)
    pcall(function() sq:RecalcAllWithNeighbours(true) end)
    pcall(function() sq:RecalcProperties() end)
end

function MC.borrar(x, y, z)
    local sq = getCell():getGridSquare(x, y, z)
    if not sq then return end
    local objs = sq:getObjects()
    if objs:size() == 0 then return end
    local obj = objs:get(objs:size() - 1)                -- el de más arriba (el piso queda último)
    local ok = pcall(function() sq:transmitRemoveItemFromSquare(obj) end)
    if not ok then pcall(function() sq:RemoveTileObject(obj) end) end
    pcall(function() sq:RecalcAllWithNeighbours(true) end)
end

-- ------------------------------------------------------------ herramienta en el mundo (cursor)
MC.Cursor = ISBuildingObject:derive("ModoCreativoCursor")

function MC.Cursor:new(sprite, borrar)
    local o = {}
    setmetatable(o, self)
    self.__index = self
    o:init()
    o:setSprite(sprite)
    o:setNorthSprite(sprite)
    o.player = 0
    o.borrarModo = borrar
    o.skipBuildAction = true
    o.noNeedHammer = true
    o.canBeAlwaysPlaced = true
    o.dragNilAfterPlace = false
    return o
end

function MC.Cursor:isValid(square)
    return square ~= nil or not self.borrarModo
end

function MC.Cursor:tryBuild(x, y, z)
    self:create(x, y, z, self.north, self:getSprite())
end

function MC.Cursor:create(x, y, z, north, sprite)
    if self.borrarModo then
        MC.borrar(x, y, z)
    else
        MC.colocar(sprite, x, y, z)
    end
end

function MC.Cursor:render(x, y, z, square)
    if self.borrarModo then
        if MC._resaltado then pcall(function() MC._resaltado:setHighlighted(false) end) end
        MC._resaltado = nil
        local objs = square and square:getObjects()
        if objs and objs:size() > 0 then
            local obj = objs:get(objs:size() - 1)
            pcall(function()
                obj:setHighlighted(true)
                obj:setHighlightColor(1, 0.2, 0.2, 0.8)
            end)
            MC._resaltado = obj
        end
        return
    end
    ISBuildingObject.render(self, x, y, z, square)
end

function MC.soltar()
    if MC._resaltado then pcall(function() MC._resaltado:setHighlighted(false) end) end
    MC._resaltado = nil
    pcall(function() getCell():setDrag(nil, 0) end)
end

function MC.empezar(sprite, borrar)
    local ok, err = pcall(function() getCell():setDrag(MC.Cursor:new(sprite, borrar), 0) end)
    if not ok then log("no se pudo tomar la herramienta: " .. tostring(err)) end
end

-- ------------------------------------------------------------ grilla de tiles
MC.Grilla = ISPanel:derive("ModoCreativoGrilla")

function MC.Grilla:new(x, y, w, h)
    local o = ISPanel.new(self, x, y, w, h)
    o.tiles = {}
    o.fila = 0
    o.backgroundColor = {r = 0.05, g = 0.05, b = 0.05, a = 0.9}
    return o
end

function MC.Grilla:columnas()
    return math.max(1, math.floor(self.width / CELDA))
end

function MC.Grilla:filasVisibles()
    return math.max(1, math.floor(self.height / CELDA))
end

function MC.Grilla:setTiles(tiles)
    self.tiles = tiles
    self.fila = 0
end

function MC.Grilla:prerender()
    ISPanel.prerender(self)
    local cols = self:columnas()
    local inicio = self.fila * cols
    local fin = math.min(#self.tiles, inicio + cols * self:filasVisibles())
    local sel = MC.ventanaCatalogo and MC.ventanaCatalogo.elegido
    for i = inicio + 1, fin do
        local k = i - inicio - 1
        local cx = (k % cols) * CELDA
        local cy = math.floor(k / cols) * CELDA
        local nombre = self.tiles[i]
        if nombre == sel then
            self:drawRect(cx + 1, cy + 1, CELDA - 2, CELDA - 2, 0.6, 0.15, 0.5, 0.15)
        elseif self:isMouseOver() and self.mx and self.mx >= cx and self.mx < cx + CELDA and self.my >= cy
                and self.my < cy + CELDA then
            self:drawRect(cx + 1, cy + 1, CELDA - 2, CELDA - 2, 0.3, 0.4, 0.4, 0.4)
        end
        local tex = getTexture(nombre)
        if tex then self:drawTextureScaledAspect(tex, cx + 4, cy + 4, CELDA - 8, CELDA - 8, 1, 1, 1, 1) end
    end
    local total = math.ceil(#self.tiles / cols)
    if total > self:filasVisibles() then
        self:drawText(string.format("%d-%d de %d", inicio + 1, fin, #self.tiles), self.width - 110, self.height - 18,
                      0.8, 0.8, 0.8, 1, UIFont.Small)
    end
end

function MC.Grilla:onMouseMove(dx, dy)
    self.mx, self.my = self:getMouseX(), self:getMouseY()
end

function MC.Grilla:onMouseWheel(del)
    local cols = self:columnas()
    local maxFila = math.max(0, math.ceil(#self.tiles / cols) - self:filasVisibles())
    self.fila = math.max(0, math.min(maxFila, self.fila + (del > 0 and 1 or -1)))
    return true
end

function MC.Grilla:onMouseDown(x, y)
    local cols = self:columnas()
    local c, f = math.floor(x / CELDA), math.floor(y / CELDA)
    if c >= cols then return true end
    local i = (self.fila + f) * cols + c + 1
    local nombre = self.tiles[i]
    if nombre and MC.ventanaCatalogo then MC.ventanaCatalogo:elegir(nombre) end
    return true
end

-- ------------------------------------------------------------ ventana del catálogo
MC.Catalogo = ISCollapsableWindow:derive("ModoCreativoCatalogo")

function MC.Catalogo:new(x, y)
    local o = ISCollapsableWindow.new(self, x, y, 820, 560)
    o.title = "Catalogo de construccion"
    o.resizable = false
    return o
end

function MC.Catalogo:createChildren()
    ISCollapsableWindow.createChildren(self)
    local top = self:titleBarHeight() + 8
    local fh = getTextManager():getFontHeight(UIFont.Small) + 8

    self.combo = ISComboBox:new(10, top, 200, fh, self, MC.Catalogo.onCategoria)
    self.combo:initialise()
    self:addChild(self.combo)

    self.buscar = ISTextEntryBox:new("", 220, top, 300, fh)
    self.buscar:initialise()
    self.buscar:instantiate()
    self.buscar.onTextChange = function() self:filtrar() end
    self:addChild(self.buscar)

    self.btnBorrar = ISButton:new(530, top, 130, fh, "Herramienta borrar", self, MC.Catalogo.onBorrar)
    self.btnBorrar:initialise()
    self:addChild(self.btnBorrar)

    self.btnSoltar = ISButton:new(670, top, 140, fh, "Soltar herramienta", self, MC.Catalogo.onSoltar)
    self.btnSoltar:initialise()
    self:addChild(self.btnSoltar)

    local y0 = top + fh + 8
    local hLista = self.height - y0 - 40
    self.lista = ISScrollingListBox:new(10, y0, 220, hLista)
    self.lista:initialise()
    self.lista:instantiate()
    self.lista.itemheight = getTextManager():getFontHeight(UIFont.Small) + 4
    self.lista.font = UIFont.Small
    self.lista.drawBorder = true
    self.lista:setOnMouseDownFunction(self, MC.Catalogo.onHoja)
    self:addChild(self.lista)

    self.grilla = MC.Grilla:new(240, y0, self.width - 250, hLista)
    self.grilla:initialise()
    self:addChild(self.grilla)

    self.info = ISLabel:new(10, self.height - 30, 18, "", 0.9, 0.9, 0.9, 1, UIFont.Small, true)
    self:addChild(self.info)

    -- categorías a partir de los nombres de las hojas de tiles
    self.porCategoria = {}
    local cats = {}
    for _, ts in ipairs(MC.tilesets()) do
        local c = categoriaDe(ts)
        if not self.porCategoria[c] then
            self.porCategoria[c] = {}
            table.insert(cats, c)
        end
        table.insert(self.porCategoria[c], ts)
    end
    table.sort(cats)
    self.combo:addOption("Todas")
    for _, c in ipairs(cats) do self.combo:addOption(c) end
    self.combo.selected = 1
    self:filtrar()
    if #MC.tilesets() == 0 then
        self.info:setName("No se pudo leer el catalogo del juego (ver console.txt, lineas [ModoCreativo]).")
    else
        self.info:setName("Elegi una hoja a la izquierda y un tile. Click en el mundo: colocar. Esc o click derecho: soltar.")
    end
end

function MC.Catalogo:filtrar()
    local cat = self.combo:getOptionText(self.combo.selected)
    local txt = string.lower(self.buscar:getText() or "")
    self.lista:clear()
    local fuente = (cat == "Todas" or not self.porCategoria[cat]) and MC.tilesets() or self.porCategoria[cat]
    for _, ts in ipairs(fuente) do
        if txt == "" or string.find(string.lower(ts), txt, 1, true) then
            self.lista:addItem(ts, ts)
        end
    end
    if #self.lista.items > 0 then
        self.lista.selected = 1
        self:onHoja(self.lista.items[1].item)
    else
        self.grilla:setTiles({})
    end
end

function MC.Catalogo:onCategoria()
    self:filtrar()
end

function MC.Catalogo:onHoja(ts)
    self.hoja = ts
    self.grilla:setTiles(MC.tilesDe(ts))
end

function MC.Catalogo:elegir(nombre)
    self.elegido = nombre
    self.info:setName("Colocando: " .. nombre .. "   (Esc o click derecho para soltar)")
    MC.empezar(nombre, false)
end

function MC.Catalogo:onBorrar()
    self.elegido = nil
    self.info:setName("Borrar: click en el mundo saca el objeto de mas arriba del cuadro (resaltado en rojo).")
    MC.empezar(nil, true)
end

function MC.Catalogo:onSoltar()
    self.elegido = nil
    MC.soltar()
    self.info:setName("Herramienta soltada.")
end

function MC.Catalogo:close()
    MC.soltar()
    self:setVisible(false)
    self:removeFromUIManager()
    MC.ventanaCatalogo = nil
end

function MC.abrirCatalogo()
    if MC.ventanaCatalogo then
        MC.ventanaCatalogo:close()
        return
    end
    MC.ventanaCatalogo = MC.Catalogo:new(getCore():getScreenWidth() / 2 - 410, 120)
    MC.ventanaCatalogo:initialise()
    MC.ventanaCatalogo:addToUIManager()
end
