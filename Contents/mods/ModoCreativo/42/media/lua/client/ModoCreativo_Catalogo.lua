-- Modo Creativo: datos del catálogo y herramienta para colocar y borrar en el mundo.
-- Lee todas las hojas de tiles del juego y las agrupa en OBJETOS: las orientaciones y las piezas de un mueble
-- grande (GroupName + CustomName del tile) son un solo objeto. Colocar pone el mueble entero (grilla de
-- piezas), R rota entre sus orientaciones, Borrar saca el objeto de más arriba del cuadro.
-- Cada llamada al juego va protegida y deja rastro [ModoCreativo] en la consola.

require "BuildingObjects/ISBuildingObject"

ModoCreativo = ModoCreativo or {}
local MC = ModoCreativo

local function log(msg)
    print("[ModoCreativo] " .. msg)
end

MC.CATEGORIAS = {   -- prefijo de la hoja de tiles -> {nombre, orden}
    furniture = {"Muebles", 1}, appliances = {"Electrodomesticos", 2}, fixtures = {"Accesorios del hogar", 3},
    walls = {"Paredes", 4}, floors = {"Pisos", 5}, roofs = {"Techos", 6}, fencing = {"Cercas y rejas", 7},
    lighting = {"Luces", 8}, location = {"Comercios y lugares", 9}, recreational = {"Recreacion", 10},
    vegetation = {"Vegetacion", 11}, street = {"Calle", 12}, construction = {"Construccion", 13},
    carpentry = {"Carpinteria", 14}, industry = {"Industria", 15}, trashcontainers = {"Basura", 16},
    signs = {"Carteles", 17}, security = {"Seguridad", 18}, camping = {"Campamento", 19},
    blends = {"Suelos naturales", 20}, d = {"Puertas", 21}, doors = {"Puertas", 21},
}

local function categoriaDe(hoja)
    local pre = string.match(hoja, "^([^_]+)") or hoja
    local c = MC.CATEGORIAS[pre]
    if c then return c[1], c[2] end
    return "Otros", 99
end

local function prop(props, clave)
    local v
    pcall(function()
        if props:Is(clave) then v = props:Val(clave) end
    end)
    return v
end

local function nombreLindo(hoja, idx)
    local s = string.gsub(hoja, "_%d+$", "")
    s = string.gsub(s, "_", " ")
    return s .. " " .. idx
end

local function traducir(grupo, nombre)
    local txt = (grupo and grupo ~= "" and (grupo .. " " .. nombre)) or nombre
    local ok, t = pcall(function() return Translator.getMoveableDisplayName(txt) end)
    if ok and t and t ~= "" then return t end
    return txt
end

-- objetos de una hoja: {nombre, hoja, sprites = {...}, variantes = {anclas de cada orientación}}
function MC.objetosDe(hoja)
    MC._objetos = MC._objetos or {}
    if MC._objetos[hoja] then return MC._objetos[hoja] end
    local lista, porClave = {}, {}
    local ok, t = pcall(function() return getWorld():getAllTiles(hoja) end)
    if not (ok and t) then
        log("no se pudieron leer los tiles de " .. hoja .. ": " .. tostring(t))
        MC._objetos[hoja] = lista
        return lista
    end
    for i = 0, t:size() - 1 do
        local nombre = t:get(i)
        if getTexture(nombre) then
            local spr = getSprite(nombre)
            local props = spr and spr:getProperties()
            local custom = props and prop(props, "CustomName")
            local grupo = props and prop(props, "GroupName")
            local clave = custom and ((grupo or "") .. "|" .. custom) or nombre
            local obj = porClave[clave]
            if not obj then
                obj = {clave = clave, hoja = hoja, sprites = {}, variantes = {},
                       nombre = custom and traducir(grupo, custom) or nombreLindo(hoja, i)}
                porClave[clave] = obj
                table.insert(lista, obj)
            end
            table.insert(obj.sprites, nombre)
            -- ancla de la grilla (pieza 0,0) o tile suelto: es una orientación colocable
            local grilla
            pcall(function() grilla = spr:getSpriteGrid() end)
            local esAncla = true
            if grilla then
                pcall(function() esAncla = grilla:getSprite(0, 0) == spr end)
            end
            if esAncla then table.insert(obj.variantes, nombre) end
        end
    end
    for _, obj in ipairs(lista) do
        if #obj.variantes == 0 then obj.variantes = {obj.sprites[1]} end
        obj.icono = obj.variantes[1]
    end
    MC._objetos[hoja] = lista
    return lista
end

-- hojas por categoría: {{nombre, orden, hojas = {...}}}
function MC.categorias()
    if MC._categorias then return MC._categorias end
    local porNombre, lista = {}, {}
    local ok, nombres = pcall(function() return getWorld():getAllTilesName() end)
    if not (ok and nombres) then
        log("no se pudo leer la lista de hojas de tiles (getAllTilesName): " .. tostring(nombres))
        MC._categorias = lista
        return lista
    end
    for i = 0, nombres:size() - 1 do
        local hoja = nombres:get(i)
        local cat, orden = categoriaDe(hoja)
        if not porNombre[cat] then
            porNombre[cat] = {nombre = cat, orden = orden, hojas = {}}
            table.insert(lista, porNombre[cat])
        end
        table.insert(porNombre[cat].hojas, hoja)
    end
    for _, c in ipairs(lista) do table.sort(c.hojas) end
    table.sort(lista, function(a, b)
        if a.orden ~= b.orden then return a.orden < b.orden end
        return a.nombre < b.nombre
    end)
    MC._categorias = lista
    return lista
end

-- todos los objetos de una categoría (se arma la primera vez que se abre)
function MC.objetosDeCategoria(cat)
    if cat._objetos then return cat._objetos end
    local todos = {}
    for _, hoja in ipairs(cat.hojas) do
        for _, obj in ipairs(MC.objetosDe(hoja)) do table.insert(todos, obj) end
    end
    cat._objetos = todos
    return todos
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

local function colocarTile(sprite, x, y, z)
    local sq = cuadro(x, y, z)
    if not sq then log("no hay cuadro en " .. x .. "," .. y .. "," .. z) return end
    local obj
    local ok = pcall(function() obj = IsoObject.new(getCell(), sq, sprite) end)
    if not (ok and obj) then
        ok = pcall(function() obj = IsoObject.new(sq, sprite, nil, false) end)
    end
    if not (ok and obj) then log("no se pudo crear el objeto " .. sprite) return end
    pcall(function() obj:createContainersFromSpriteProperties() end)     -- muebles con cajones o estantes
    sq:AddTileObject(obj)
    pcall(function() obj:transmitCompleteItemToServer() end)
    pcall(function() sq:RecalcAllWithNeighbours(true) end)
end

-- coloca un objeto entero: si el tile es parte de una grilla (mueble de varias piezas) pone todas
function MC.colocar(sprite, x, y, z)
    local spr = getSprite(sprite)
    local grilla
    pcall(function() grilla = spr and spr:getSpriteGrid() end)
    if grilla then
        local w, h = 1, 1
        pcall(function() w, h = grilla:getWidth(), grilla:getHeight() end)
        for gx = 0, w - 1 do
            for gy = 0, h - 1 do
                local pieza
                pcall(function() pieza = grilla:getSprite(gx, gy) end)
                if pieza then colocarTile(pieza:getName(), x + gx, y + gy, z) end
            end
        end
    else
        colocarTile(sprite, x, y, z)
    end
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
    if sprite then
        o:setSprite(sprite)
        o:setNorthSprite(sprite)
    end
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
    if self.borrarModo then MC.borrar(x, y, z) else MC.colocar(sprite, x, y, z) end
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

-- estado de la herramienta: {objeto, variante} para colocar, o {borrar = true}
function MC.soltar()
    if MC._resaltado then pcall(function() MC._resaltado:setHighlighted(false) end) end
    MC._resaltado = nil
    if MC.herramienta then pcall(function() getCell():setDrag(nil, 0) end) end
    MC.herramienta = nil
    if MC.ventana then MC.ventana:actualizar() end
end

local function tomar(sprite, borrar)
    local ok, err = pcall(function() getCell():setDrag(MC.Cursor:new(sprite, borrar), 0) end)
    if not ok then log("no se pudo tomar la herramienta: " .. tostring(err)) end
end

function MC.tomarObjeto(obj, variante)
    variante = variante or 1
    MC.herramienta = {objeto = obj, variante = variante}
    tomar(obj.variantes[variante], false)
    if MC.ventana then MC.ventana:actualizar() end
end

function MC.tomarBorrar()
    MC.herramienta = {borrar = true}
    tomar(nil, true)
    if MC.ventana then MC.ventana:actualizar() end
end

function MC.rotar()
    local h = MC.herramienta
    if not (h and h.objeto) or #h.objeto.variantes < 2 then return end
    MC.tomarObjeto(h.objeto, h.variante % #h.objeto.variantes + 1)
end
