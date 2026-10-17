-- Modo Creativo: ventana principal (ajustable).
--   Encabezado: título y el interruptor general (ACTIVADO / DESACTIVADO).
--   Menú lateral: Ajustes (tarjetas con interruptor y explicación), Catálogo (todos los objetos del juego para
--   colocar en el mundo) y Ayuda.
-- Todas las medidas salen del alto real de la letra (U) y del tamaño de la ventana, y se recalculan cuando la
-- ventana cambia de tamaño (esquina inferior derecha): se ve igual en un monitor chico que en una TV 4K.

require "ISUI/ISCollapsableWindow"
require "ISUI/ISPanel"
require "ISUI/ISTextEntryBox"

ModoCreativo = ModoCreativo or {}
local MC = ModoCreativo

local TM = getTextManager()
local FS, FM, FL = UIFont.Small, UIFont.Medium, UIFont.Large
local function alto(f) return TM:getFontHeight(f) end
local function ancho(f, t) return TM:MeasureStringX(f, t) end
local function U() return alto(FS) end                       -- unidad de medida: alto de la letra chica
local function P() return math.floor(U() * 0.6 + 0.5) end   -- margen

local C = {
    fondo = {0.09, 0.10, 0.11}, panel = {0.13, 0.14, 0.16}, tarjeta = {0.17, 0.18, 0.20},
    hover = {0.22, 0.24, 0.27}, borde = {0.30, 0.32, 0.35}, texto = {0.92, 0.92, 0.90},
    suave = {0.62, 0.64, 0.66}, verde = {0.30, 0.72, 0.36}, verdeOsc = {0.13, 0.32, 0.16},
    rojo = {0.85, 0.32, 0.28}, rojoOsc = {0.45, 0.14, 0.12},
}
local function rect(p, x, y, w, h, c, a) p:drawRect(x, y, w, h, a or 1, c[1], c[2], c[3]) end
local function borde(p, x, y, w, h, c, a) p:drawRectBorder(x, y, w, h, a or 1, c[1], c[2], c[3]) end
local function texto(p, t, x, y, c, f, a) p:drawText(t, x, y, c[1], c[2], c[3], a or 1, f or FS) end

local function renglones(t, f, w)
    local out, linea = {}, ""
    for palabra in string.gmatch(t, "%S+") do
        local prueba = linea == "" and palabra or (linea .. " " .. palabra)
        if ancho(f, prueba) > w and linea ~= "" then
            table.insert(out, linea)
            linea = palabra
        else
            linea = prueba
        end
    end
    if linea ~= "" then table.insert(out, linea) end
    return out
end

-- escribe un párrafo ajustado al ancho y devuelve la y siguiente
local function parrafo(p, t, x, y, w, c, f)
    f = f or FS
    for _, l in ipairs(renglones(t, f, w)) do
        texto(p, l, x, y, c, f)
        y = y + alto(f) + 2
    end
    return y
end

local function recortar(t, f, w)
    if ancho(f, t) <= w then return t end
    while #t > 1 and ancho(f, t .. "...") > w do t = string.sub(t, 1, -2) end
    return t .. "..."
end

local function interruptor(p, x, y, on, habilitado)
    local h = math.floor(U() * 1.2)
    local w = h * 2
    rect(p, x, y, w, h, habilitado == false and C.borde or (on and C.verde or C.borde))
    local k = h - 6
    rect(p, on and (x + w - k - 3) or (x + 3), y + 3, k, k, C.texto)
    return w, h
end

-- ------------------------------------------------------------ botón plano
MC.Boton = ISPanel:derive("ModoCreativoBoton")

function MC.Boton:new(titulo, color, accion, fuente)
    local o = ISPanel.new(self, 0, 0, 10, 10)
    o.titulo, o.color, o.accion, o.fuente = titulo, color, accion, fuente or FS
    o.background = false
    o.habilitado = true
    return o
end

function MC.Boton:altoIdeal() return alto(self.fuente) + P() * 2 end

function MC.Boton:prerender()
    local c = self.habilitado and self.color or C.borde
    local hover = self.habilitado and self:isMouseOver()
    rect(self, 0, 0, self.width, self.height, c, hover and 1 or 0.85)
    if hover then borde(self, 0, 0, self.width, self.height, C.texto, 0.6) end
    local t = recortar(self.titulo, self.fuente, self.width - P())
    self:drawTextCentre(t, self.width / 2, (self.height - alto(self.fuente)) / 2, 1, 1, 1,
                        self.habilitado and 1 or 0.5, self.fuente)
end

function MC.Boton:onMouseDown(x, y) return true end

function MC.Boton:onMouseUp(x, y)
    if self.habilitado and self.accion then self.accion() end
    return true
end

local function poner(el, x, y, w, h)
    el:setX(x)
    el:setY(y)
    el:setWidth(math.max(1, w))
    el:setHeight(math.max(1, h))
end

-- ------------------------------------------------------------ página Ajustes
MC.PaginaAjustes = ISPanel:derive("ModoCreativoAjustes")

function MC.PaginaAjustes:new()
    local o = ISPanel.new(self, 0, 0, 10, 10)
    o.background = false
    return o
end

function MC.PaginaAjustes:tarjetas()
    local p = P()
    local out, y = {}, alto(FM) + alto(FS) + p * 3
    local anchoTexto = self.width - p * 4 - U() * 3
    for _, op in ipairs(MC.OPCIONES) do
        local lineas = renglones(op.texto, FS, anchoTexto)
        local h = p * 2 + alto(FM) + p + #lineas * (alto(FS) + 2) + (MC.disponible(op.metodo) and 0 or alto(FS) + 4) + p
        table.insert(out, {op = op, y = y, h = h, lineas = lineas})
        y = y + h + p
    end
    return out
end

function MC.PaginaAjustes:prerender()
    local e = MC.estado()
    if not e then return end
    local p = P()
    texto(self, "Ajustes del modo creativo", 0, 0, C.texto, FM)
    texto(self, "Funcionan mientras el interruptor general (arriba a la derecha) este ACTIVADO.", 0,
          alto(FM) + 4, C.suave, FS)
    local my = self:getMouseY()
    for _, t in ipairs(self:tarjetas()) do
        local hover = self:isMouseOver() and my >= t.y and my < t.y + t.h
        rect(self, 0, t.y, self.width, t.h, hover and C.hover or C.tarjeta)
        local disp = MC.disponible(t.op.metodo)
        local on = e[t.op.clave] == true
        rect(self, 0, t.y, 4, t.h, (on and e.activo) and C.verde or C.borde)
        texto(self, t.op.titulo, p * 2, t.y + p, C.texto, FM)
        local y = t.y + p * 2 + alto(FM)
        for _, l in ipairs(t.lineas) do
            texto(self, l, p * 2, y, C.suave, FS)
            y = y + alto(FS) + 2
        end
        if not disp then texto(self, "No disponible en esta version del juego", p * 2, y + 2, C.rojo, FS) end
        local sw = U() * 2.4
        interruptor(self, self.width - sw - p * 2, t.y + (t.h - U() * 1.2) / 2, on, disp)
    end
end

function MC.PaginaAjustes:onMouseUp(x, y)
    local e = MC.estado()
    if not e then return true end
    for _, t in ipairs(self:tarjetas()) do
        if y >= t.y and y < t.y + t.h then
            e[t.op.clave] = not (e[t.op.clave] == true)
            MC.aplicar()
        end
    end
    return true
end

-- ------------------------------------------------------------ lista de categorías
MC.ListaCategorias = ISPanel:derive("ModoCreativoCategorias")

function MC.ListaCategorias:new(alElegir)
    local o = ISPanel.new(self, 0, 0, 10, 10)
    o.background = false
    o.alElegir = alElegir
    o.sel = 1
    o.desde = 0
    return o
end

function MC.ListaCategorias:items()
    local out = {{nombre = "Todo", todo = true}}
    for _, c in ipairs(MC.categorias()) do table.insert(out, c) end
    return out
end

function MC.ListaCategorias:fila() return alto(FS) + P() * 2 end

function MC.ListaCategorias:prerender()
    rect(self, 0, 0, self.width, self.height, C.panel)
    local fila = self:fila()
    local items = self:items()
    local my = self:getMouseY()
    for k = 1, math.floor(self.height / fila) do
        local i = k + self.desde
        local it = items[i]
        if not it then break end
        local y = (k - 1) * fila
        if i == self.sel then
            rect(self, 0, y, self.width, fila, C.verdeOsc)
            rect(self, 0, y, 4, fila, C.verde)
        elseif self:isMouseOver() and my >= y and my < y + fila then
            rect(self, 0, y, self.width, fila, C.hover)
        end
        texto(self, recortar(it.nombre, FS, self.width - P() * 3), P() * 2, y + P(), C.texto, FS)
    end
    if #items <= 1 then
        parrafo(self, "Cargando el catalogo... si no aparece nada, mira la Ayuda.", P(), fila + P(),
                self.width - P() * 2, C.suave)
    end
end

function MC.ListaCategorias:onMouseWheel(d)
    local maxDesde = math.max(0, #self:items() - math.floor(self.height / self:fila()))
    self.desde = math.max(0, math.min(maxDesde, self.desde + (d > 0 and 1 or -1)))
    return true
end

function MC.ListaCategorias:onMouseUp(x, y)
    local i = math.floor(y / self:fila()) + 1 + self.desde
    local items = self:items()
    if items[i] then
        self.sel = i
        self.alElegir(items[i])
    end
    return true
end

-- ------------------------------------------------------------ grilla de objetos
MC.Grilla = ISPanel:derive("ModoCreativoGrilla")

function MC.Grilla:new(alElegir)
    local o = ISPanel.new(self, 0, 0, 10, 10)
    o.background = false
    o.objetos = {}
    o.fila = 0
    o.alElegir = alElegir
    return o
end

function MC.Grilla:celda()
    local w = math.floor(U() * 5.5)
    return w, w + alto(FS) + P()
end
function MC.Grilla:cols() return math.max(1, math.floor((self.width - 8) / (self:celda()))) end
function MC.Grilla:filas()
    local _, h = self:celda()
    return math.max(1, math.floor(self.height / h))
end

function MC.Grilla:setObjetos(lista)
    self.objetos = lista
    self.fila = 0
end

function MC.Grilla:celdaEn(x, y)
    local cw, ch = self:celda()
    local c, f = math.floor(x / cw), math.floor(y / ch)
    if c >= self:cols() or c < 0 or f < 0 then return nil end
    return (self.fila + f) * self:cols() + c + 1
end

function MC.Grilla:prerender()
    rect(self, 0, 0, self.width, self.height, C.panel)
    local cw, ch = self:celda()
    local cols, filas = self:cols(), self:filas()
    local inicio = self.fila * cols
    local sel = MC.ventana and MC.ventana.elegido
    local hoverI = self:isMouseOver() and self:celdaEn(self:getMouseX(), self:getMouseY())
    local m = 4
    for i = inicio + 1, math.min(#self.objetos, inicio + cols * filas) do
        local k = i - inicio - 1
        local x, y = (k % cols) * cw + m, math.floor(k / cols) * ch + m
        local obj = self.objetos[i]
        rect(self, x, y, cw - m * 2, ch - m * 2, (obj == sel and C.verdeOsc) or (i == hoverI and C.hover) or C.tarjeta)
        if obj == sel then borde(self, x, y, cw - m * 2, ch - m * 2, C.verde) end
        local tex = getTexture(obj.icono)
        local img = ch - m * 2 - alto(FS) - P()
        if tex then self:drawTextureScaledAspect(tex, x + 4, y + 4, cw - m * 2 - 8, img - 4, 1, 1, 1, 1) end
        texto(self, recortar(obj.nombre, FS, cw - m * 2 - 8), x + 4, y + img + 2, C.texto, FS)
    end
    local total = math.ceil(#self.objetos / cols)
    if total > filas then
        local h = math.max(U() * 2, self.height * filas / total)
        local y = (self.height - h) * self.fila / (total - filas)
        rect(self, self.width - 6, 0, 6, self.height, C.fondo)
        rect(self, self.width - 6, y, 6, h, C.borde)
    end
    if #self.objetos == 0 then
        self:drawTextCentre("No hay objetos para mostrar", self.width / 2, self.height / 2 - alto(FM) / 2,
                            0.6, 0.6, 0.6, 1, FM)
    end
    if hoverI and self.objetos[hoverI] then
        local t = self.objetos[hoverI].nombre
        local w = ancho(FS, t) + P() * 2
        local tx = math.min(self:getMouseX() + U(), self.width - w - 4)
        local ty = math.min(self:getMouseY() + U(), self.height - alto(FS) - P() * 2)
        rect(self, tx, ty, w, alto(FS) + P(), C.fondo, 0.95)
        borde(self, tx, ty, w, alto(FS) + P(), C.borde)
        texto(self, t, tx + P(), ty + P() / 2, C.texto, FS)
    end
end

function MC.Grilla:onMouseWheel(d)
    local maxFila = math.max(0, math.ceil(#self.objetos / self:cols()) - self:filas())
    self.fila = math.max(0, math.min(maxFila, self.fila + (d > 0 and 1 or -1)))
    return true
end

function MC.Grilla:onMouseUp(x, y)
    local i = self:celdaEn(x, y)
    if i and self.objetos[i] then self.alElegir(self.objetos[i]) end
    return true
end

-- ------------------------------------------------------------ página Catálogo
MC.PaginaCatalogo = ISPanel:derive("ModoCreativoCatalogo")

function MC.PaginaCatalogo:new()
    local o = ISPanel.new(self, 0, 0, 10, 10)
    o.background = false
    o.textoBusqueda = ""
    return o
end

function MC.PaginaCatalogo:createChildren()
    self.buscar = ISTextEntryBox:new("", 0, 0, 100, alto(FS) + P())
    self.buscar:initialise()
    self.buscar:instantiate()
    self:addChild(self.buscar)
    self.cats = MC.ListaCategorias:new(function(c) self:elegirCategoria(c) end)
    self.grilla = MC.Grilla:new(function(obj) self:elegirObjeto(obj) end)
    self.btnColocar = MC.Boton:new("Colocar en el mundo", C.verdeOsc,
                                   function() if self.elegido then MC.tomarObjeto(self.elegido, self.variante) end end, FM)
    self.btnRotar = MC.Boton:new("Rotar  (R)", C.tarjeta, function() self:rotar() end)
    self.btnBorrar = MC.Boton:new("Herramienta borrar", C.rojoOsc, function() MC.tomarBorrar() end)
    self.btnSoltar = MC.Boton:new("Soltar herramienta  (Esc)", C.tarjeta, function() MC.soltar() end)
    for _, el in ipairs({self.cats, self.grilla, self.btnColocar, self.btnRotar, self.btnBorrar, self.btnSoltar}) do
        el:initialise()
        self:addChild(el)
    end
    self:disponer()
    self:elegirCategoria(self.cats:items()[1])
end

function MC.PaginaCatalogo:disponer()
    local p, u = P(), U()
    local w, h = self.width, self.height
    local barra = alto(FS) + p * 2
    local lx = ancho(FS, "Buscar:") + p
    poner(self.buscar, lx, 0, math.min(u * 22, w * 0.4), alto(FS) + p)
    local catW = 0
    for _, c in ipairs(self.cats:items()) do catW = math.max(catW, ancho(FS, c.nombre)) end
    catW = math.max(u * 8, math.min(u * 14, catW + p * 4))
    self.detalleW = math.max(u * 13, math.min(u * 20, w * 0.26))
    local top = barra + p
    poner(self.cats, 0, top, catW, h - top)
    poner(self.grilla, catW + p, top, w - catW - self.detalleW - p * 2, h - top)
    self.detalleX, self.detalleTop = w - self.detalleW, top
    self.cantidadX = lx + self.buscar.width + p
end

function MC.PaginaCatalogo:elegirCategoria(c)
    self.categoria = c
    self:filtrar()
end

function MC.PaginaCatalogo:filtrar()
    local c = self.categoria
    if not c then return end
    local fuente = {}
    local q = string.lower(self.textoBusqueda)
    if c.todo then
        for _, cat in ipairs(MC.categorias()) do
            if q ~= "" or cat.orden == 1 then              -- sin búsqueda, "Todo" muestra los muebles
                for _, o in ipairs(MC.objetosDeCategoria(cat)) do table.insert(fuente, o) end
            end
        end
    else
        fuente = MC.objetosDeCategoria(c)
    end
    local lista = {}
    for _, o in ipairs(fuente) do
        if q == "" or string.find(string.lower(o.nombre), q, 1, true) or string.find(string.lower(o.hoja), q, 1, true) then
            table.insert(lista, o)
        end
    end
    self.grilla:setObjetos(lista)
    self.cantidad = #lista
end

function MC.PaginaCatalogo:elegirObjeto(obj)
    self.elegido = obj
    self.variante = 1
    if MC.ventana then MC.ventana.elegido = obj end
    MC.tomarObjeto(obj, 1)               -- un click en la grilla ya deja listo para colocar
end

function MC.PaginaCatalogo:rotar()
    if not self.elegido then return end
    self.variante = self.variante % #self.elegido.variantes + 1
    MC.tomarObjeto(self.elegido, self.variante)
end

function MC.PaginaCatalogo:prerender()
    local p = P()
    if self.ultW ~= self.width or self.ultH ~= self.height then
        self.ultW, self.ultH = self.width, self.height
        self:disponer()
    end
    local t = self.buscar:getText() or ""              -- búsqueda revisada en cada cuadro
    if t ~= self.textoBusqueda then
        self.textoBusqueda = t
        self:filtrar()
    end
    texto(self, "Buscar:", 0, p / 2, C.texto, FS)
    local cant = (self.cantidad or 0) .. " objetos"
    if self.categoria and self.categoria.todo and self.textoBusqueda == "" then
        cant = cant .. "  -  escribi para buscar en todo el catalogo"
    end
    texto(self, recortar(cant, FS, self.width - self.cantidadX), self.cantidadX, p / 2, C.suave, FS)

    -- panel de detalle: todo se apila de arriba hacia abajo, sin coordenadas fijas
    local x, w = self.detalleX, self.detalleW
    local y = self.detalleTop
    rect(self, x, y, w, self.height - y, C.panel)
    local cx, cw = x + p, w - p * 2
    y = y + p
    if self.elegido then
        local prev = math.min(cw, U() * 9)
        rect(self, cx, y, cw, prev, C.fondo)
        local tex = getTexture(self.elegido.variantes[self.variante or 1])
        if tex then self:drawTextureScaledAspect(tex, cx + p, y + p, cw - p * 2, prev - p * 2, 1, 1, 1, 1) end
        y = y + prev + p
        y = parrafo(self, self.elegido.nombre, cx, y, cw, C.texto, FM)
        y = parrafo(self, self.elegido.hoja, cx, y + 2, cw, C.suave, FS)
        y = parrafo(self, "Orientacion " .. (self.variante or 1) .. " de " .. #self.elegido.variantes, cx, y, cw,
                    C.suave, FS)
    else
        y = parrafo(self, "Elegi una categoria a la izquierda y despues un objeto. Con un click queda listo: "
                .. "cada click en el mundo lo coloca.", cx, y, cw, C.suave, FS)
    end
    y = y + p
    for _, b in ipairs({self.btnColocar, self.btnRotar, self.btnBorrar, self.btnSoltar}) do
        poner(b, cx, y, cw, b:altoIdeal())
        y = y + b.height + p / 2
    end
    local h = MC.herramienta
    local estado, col = "Sin herramienta en la mano", C.suave
    if h and h.borrar then
        estado, col = "BORRANDO: click en el mundo saca el objeto resaltado en rojo", C.rojo
    elseif h and h.objeto then
        estado, col = "COLOCANDO: click en el mundo. R rota, Esc suelta.", C.verde
    end
    parrafo(self, estado, cx, y + p / 2, cw, col, FS)
    self.btnRotar.habilitado = self.elegido ~= nil and #self.elegido.variantes > 1
    self.btnColocar.habilitado = self.elegido ~= nil
    self.btnSoltar.habilitado = h ~= nil
end

-- ------------------------------------------------------------ página Ayuda
MC.PaginaAyuda = ISPanel:derive("ModoCreativoAyuda")

function MC.PaginaAyuda:new()
    local o = ISPanel.new(self, 0, 0, 10, 10)
    o.background = false
    return o
end

local AYUDA = {
    {"Abrir y cerrar", "Tecla Insert o el boton flotante con el icono (se puede arrastrar a cualquier lugar)."},
    {"Tamaño de la ventana", "Arrastra la esquina de abajo a la derecha para agrandarla o achicarla; todo se acomoda."},
    {"Interruptor general", "Arriba a la derecha. Apagado, el juego vuelve a ser normal: lo que se enseno con el "
        .. "modo creativo se olvida y las acciones vuelven a tardar."},
    {"Ajustes", "Cada tarjeta prende o apaga una parte: construir gratis, acciones instantaneas y todas las recetas."},
    {"Catalogo", "Todos los objetos del juego, por categoria. Un click en un objeto lo toma; despues cada click en "
        .. "el mundo lo coloca. Los muebles de varias piezas se colocan enteros. R rota, Esc suelta."},
    {"Borrar", "La herramienta borrar resalta en rojo el objeto de mas arriba del cuadro; un click lo saca."},
    {"Si el catalogo esta vacio", "El juego no dio la lista de objetos. Hay que generar la lista del mod con "
        .. "tools/pz_tiles_lista.py (lo corre quien mantiene el mod) y volver a cargar la partida."},
    {"Partida", "Pensado para partidas de un jugador."},
}

function MC.PaginaAyuda:prerender()
    local p = P()
    texto(self, "Como se usa", 0, 0, C.texto, FM)
    local y = alto(FM) + p * 2
    for _, par in ipairs(AYUDA) do
        texto(self, par[1], 0, y, C.verde, FS)
        y = parrafo(self, par[2], p * 2, y + alto(FS) + 4, self.width - p * 3, C.suave) + p
    end
end

-- ------------------------------------------------------------ ventana
MC.Ventana = ISCollapsableWindow:derive("ModoCreativoVentana")

local function tamanoInicial()
    local sw, sh = getCore():getScreenWidth(), getCore():getScreenHeight()
    local u = U()
    local w = math.min(sw - 40, math.max(u * 52, sw * 0.62))
    local h = math.min(sh - 40, math.max(u * 34, sh * 0.72))
    return w, h
end

function MC.Ventana:new(x, y, w, h)
    local o = ISCollapsableWindow.new(self, x, y, w, h)
    o.title = "Modo Creativo"
    o.resizable = true
    o.minimumWidth = U() * 40
    o.minimumHeight = U() * 26
    o.backgroundColor = {r = C.fondo[1], g = C.fondo[2], b = C.fondo[3], a = 0.97}
    o.borderColor = {r = C.borde[1], g = C.borde[2], b = C.borde[3], a = 1}
    o.tamano = {w, h}
    return o
end

function MC.Ventana:initialise()
    ISCollapsableWindow.initialise(self)
    self:setWidth(self.tamano[1])               -- medidas explícitas: que nada las achique
    self:setHeight(self.tamano[2])
end

function MC.Ventana:createChildren()
    ISCollapsableWindow.createChildren(self)
    self.interruptor = MC.Boton:new("", C.borde, function()
        local e = MC.estado()
        if e then MC.setActivo(not e.activo) end
    end, FM)
    self.interruptor:initialise()
    self:addChild(self.interruptor)
    self.navItems = {}
    for _, n in ipairs({{"ajustes", "Ajustes"}, {"catalogo", "Catalogo de objetos"}, {"ayuda", "Ayuda"}}) do
        local b = MC.Boton:new(n[2], C.tarjeta, function() self:mostrar(n[1]) end, FM)
        b.clave = n[1]
        b:initialise()
        self:addChild(b)
        table.insert(self.navItems, b)
    end
    self.paginas = {ajustes = MC.PaginaAjustes:new(), catalogo = MC.PaginaCatalogo:new(), ayuda = MC.PaginaAyuda:new()}
    for _, p in pairs(self.paginas) do
        p:initialise()
        self:addChild(p)
    end
    self:disponer()
    self:mostrar(MC.ultimaPagina or "ajustes")
    self:actualizar()
end

function MC.Ventana:disponer()
    local p, u = P(), U()
    local th = self:titleBarHeight()
    self.cabeceraH = p * 2 + alto(FL) + 4 + alto(FS) + p
    local ib = self.interruptor
    local iw = ancho(FM, "DESACTIVADO") + p * 6
    poner(ib, self.width - iw - p * 2, th + (self.cabeceraH - ib:altoIdeal()) / 2, iw, ib:altoIdeal())
    local navW = 0
    for _, b in ipairs(self.navItems) do navW = math.max(navW, ancho(FM, b.titulo)) end
    self.navW = navW + p * 6
    local y = th + self.cabeceraH + p * 2
    for _, b in ipairs(self.navItems) do
        poner(b, p, y, self.navW - p * 2, b:altoIdeal())
        y = y + b.height + p
    end
    local cx = self.navW + p * 2
    local cy = th + self.cabeceraH + p * 2
    local rz = u                                      -- lugar para la esquina de redimensionar
    for _, pg in pairs(self.paginas) do
        poner(pg, cx, cy, self.width - cx - p * 2, self.height - cy - p - rz)
        if pg.disponer and pg.buscar then pg:disponer() end
    end
    self.ultW, self.ultH = self.width, self.height
end

function MC.Ventana:mostrar(clave)
    MC.ultimaPagina = clave
    for k, p in pairs(self.paginas) do p:setVisible(k == clave) end
    for _, b in ipairs(self.navItems) do b.color = (b.clave == clave) and C.verdeOsc or C.tarjeta end
end

function MC.Ventana:prerender()
    if self.ultW ~= self.width or self.ultH ~= self.height then self:disponer() end
    ISCollapsableWindow.prerender(self)
    local p = P()
    local y = self:titleBarHeight()
    rect(self, 0, y, self.width, self.cabeceraH, C.panel)
    rect(self, 0, y + self.cabeceraH - 2, self.width, 2, C.borde)
    texto(self, "MODO CREATIVO", p * 2, y + p, C.texto, FL)
    local e = MC.estado()
    local on = e and e.activo
    local sub = on and "Activado: construi y coloca lo que quieras." or "Apagado: el juego funciona normal."
    texto(self, recortar(sub, FS, self.interruptor:getX() - p * 4), p * 2, y + p + alto(FL) + 4,
          on and C.verde or C.suave, FS)
    rect(self, self.navW, y + self.cabeceraH, 1, self.height - y - self.cabeceraH, C.borde)
end

function MC.Ventana:actualizar()
    local e = MC.estado()
    if not e or not self.interruptor then return end
    self.interruptor.titulo = e.activo and "ACTIVADO" or "DESACTIVADO"
    self.interruptor.color = e.activo and C.verde or C.borde
end

function MC.Ventana:close()
    MC.tamanoVentana = {self:getX(), self:getY(), self.width, self.height}      -- se reabre igual
    self:setVisible(false)
    self:removeFromUIManager()
    MC.ventana = nil
end

function MC.abrirCerrar()
    if MC.ventana then
        MC.ventana:close()
        return
    end
    local x, y, w, h
    if MC.tamanoVentana then
        x, y, w, h = MC.tamanoVentana[1], MC.tamanoVentana[2], MC.tamanoVentana[3], MC.tamanoVentana[4]
    else
        w, h = tamanoInicial()
        x = (getCore():getScreenWidth() - w) / 2
        y = (getCore():getScreenHeight() - h) / 2
    end
    MC.ventana = MC.Ventana:new(x, y, w, h)
    MC.ventana:initialise()
    MC.ventana:addToUIManager()
    MC.ventana:bringToTop()
end
