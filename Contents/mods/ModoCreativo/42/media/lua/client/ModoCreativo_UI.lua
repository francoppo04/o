-- Modo Creativo: ventana principal.
--   Encabezado: título y el interruptor general (ACTIVADO / DESACTIVADO).
--   Menú lateral: Ajustes (tarjetas con interruptor y explicación), Catálogo (todos los objetos del juego para
--   colocar en el mundo) y Ayuda.
-- Todo se dibuja a mano (colores, tarjetas, grilla) y las medidas se fijan explícitamente, para que el texto
-- no quede cortado con ningún tamaño de letra.

require "ISUI/ISCollapsableWindow"
require "ISUI/ISPanel"
require "ISUI/ISButton"
require "ISUI/ISTextEntryBox"

ModoCreativo = ModoCreativo or {}
local MC = ModoCreativo

local TM = getTextManager()
local FS, FM, FL = UIFont.Small, UIFont.Medium, UIFont.Large
local function alto(f) return TM:getFontHeight(f) end
local function ancho(f, t) return TM:MeasureStringX(f, t) end

-- paleta
local C = {
    fondo = {0.09, 0.10, 0.11}, panel = {0.13, 0.14, 0.16}, tarjeta = {0.17, 0.18, 0.20},
    hover = {0.22, 0.24, 0.27}, borde = {0.30, 0.32, 0.35}, texto = {0.92, 0.92, 0.90},
    suave = {0.62, 0.64, 0.66}, verde = {0.30, 0.72, 0.36}, verdeOsc = {0.13, 0.32, 0.16},
    rojo = {0.85, 0.32, 0.28}, ambar = {0.95, 0.72, 0.30},
}
local function rect(p, x, y, w, h, c, a) p:drawRect(x, y, w, h, a or 1, c[1], c[2], c[3]) end
local function borde(p, x, y, w, h, c, a) p:drawRectBorder(x, y, w, h, a or 1, c[1], c[2], c[3]) end
local function texto(p, t, x, y, c, f, a) p:drawText(t, x, y, c[1], c[2], c[3], a or 1, f or FS) end

-- corta un texto en renglones que entren en w
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

local function recortar(t, f, w)
    if ancho(f, t) <= w then return t end
    while #t > 1 and ancho(f, t .. "...") > w do t = string.sub(t, 1, -2) end
    return t .. "..."
end

-- interruptor dibujado (píldora con perilla)
local function interruptor(p, x, y, on, habilitado)
    local w, h = 54, 26
    rect(p, x, y, w, h, habilitado == false and C.borde or (on and C.verde or C.borde))
    local k = h - 6
    rect(p, on and (x + w - k - 3) or (x + 3), y + 3, k, k, C.texto)
end

-- ------------------------------------------------------------ botón plano con estilo
MC.Boton = ISPanel:derive("ModoCreativoBoton")

function MC.Boton:new(x, y, w, h, titulo, color, accion)
    local o = ISPanel.new(self, x, y, w, h)
    o.titulo, o.color, o.accion = titulo, color, accion
    o.background = false
    o.habilitado = true
    return o
end

function MC.Boton:prerender()
    local c = self.habilitado and self.color or C.borde
    local hover = self.habilitado and self:isMouseOver()
    rect(self, 0, 0, self.width, self.height, c, hover and 1 or 0.85)
    if hover then borde(self, 0, 0, self.width, self.height, C.texto, 0.6) end
    local f = self.fuente or FS
    self:drawTextCentre(self.titulo, self.width / 2, (self.height - alto(f)) / 2, 1, 1, 1,
                        self.habilitado and 1 or 0.5, f)
end

function MC.Boton:onMouseUp(x, y)
    if self.habilitado and self.accion then self.accion() end
    return true
end

function MC.Boton:onMouseDown(x, y) return true end

-- ------------------------------------------------------------ página Ajustes
MC.PaginaAjustes = ISPanel:derive("ModoCreativoAjustes")

function MC.PaginaAjustes:new(x, y, w, h)
    local o = ISPanel.new(self, x, y, w, h)
    o.background = false
    return o
end

function MC.PaginaAjustes:tarjetas()
    local out, y = {}, 44
    for i, op in ipairs(MC.OPCIONES) do
        local lineas = renglones(op.texto, FS, self.width - 120)
        local h = 20 + alto(FM) + 6 + #lineas * (alto(FS) + 2) + 16
        table.insert(out, {op = op, y = y, h = h, lineas = lineas, i = i})
        y = y + h + 10
    end
    return out
end

function MC.PaginaAjustes:prerender()
    local e = MC.estado()
    if not e then return end
    texto(self, "Ajustes del modo creativo", 0, 4, C.texto, FM)
    texto(self, "Funcionan mientras el interruptor general (arriba a la derecha) este ACTIVADO.", 0, 8 + alto(FM),
          C.suave, FS)
    local mx, my = self:getMouseX(), self:getMouseY()
    for _, t in ipairs(self:tarjetas()) do
        local hover = self:isMouseOver() and my >= t.y and my < t.y + t.h
        rect(self, 0, t.y, self.width, t.h, hover and C.hover or C.tarjeta)
        local disp = MC.disponible(t.op.metodo)
        local on = e[t.op.clave] == true
        rect(self, 0, t.y, 4, t.h, (on and e.activo) and C.verde or C.borde)
        texto(self, t.op.titulo, 20, t.y + 14, C.texto, FM)
        local y = t.y + 20 + alto(FM)
        for _, l in ipairs(t.lineas) do
            texto(self, l, 20, y, C.suave, FS)
            y = y + alto(FS) + 2
        end
        if not disp then
            texto(self, "No disponible en esta version del juego", 20, y + 2, C.rojo, FS)
        end
        interruptor(self, self.width - 74, t.y + (t.h - 26) / 2, on, disp)
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

function MC.ListaCategorias:new(x, y, w, h, alElegir)
    local o = ISPanel.new(self, x, y, w, h)
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

function MC.ListaCategorias:prerender()
    rect(self, 0, 0, self.width, self.height, C.panel)
    local fila = alto(FS) + 14
    local items = self:items()
    local my = self:getMouseY()
    local visibles = math.floor(self.height / fila)
    for k = 1, visibles do
        local i = k + self.desde
        local it = items[i]
        if not it then break end
        local y = (k - 1) * fila
        if i == self.sel then
            rect(self, 0, y, self.width, fila, C.verdeOsc)
            rect(self, 0, y, 3, fila, C.verde)
        elseif self:isMouseOver() and my >= y and my < y + fila then
            rect(self, 0, y, self.width, fila, C.hover)
        end
        texto(self, recortar(it.nombre, FS, self.width - 20), 12, y + 7, C.texto, FS)
    end
end

function MC.ListaCategorias:onMouseWheel(d)
    local fila = alto(FS) + 14
    local maxDesde = math.max(0, #self:items() - math.floor(self.height / fila))
    self.desde = math.max(0, math.min(maxDesde, self.desde + (d > 0 and 1 or -1)))
    return true
end

function MC.ListaCategorias:onMouseUp(x, y)
    local fila = alto(FS) + 14
    local i = math.floor(y / fila) + 1 + self.desde
    local items = self:items()
    if items[i] then
        self.sel = i
        self.alElegir(items[i])
    end
    return true
end

-- ------------------------------------------------------------ grilla de objetos
local CELDA_W, CELDA_H = 96, 104

MC.Grilla = ISPanel:derive("ModoCreativoGrilla")

function MC.Grilla:new(x, y, w, h, alElegir)
    local o = ISPanel.new(self, x, y, w, h)
    o.background = false
    o.objetos = {}
    o.fila = 0
    o.alElegir = alElegir
    return o
end

function MC.Grilla:cols() return math.max(1, math.floor((self.width - 10) / CELDA_W)) end
function MC.Grilla:filas() return math.max(1, math.floor(self.height / CELDA_H)) end

function MC.Grilla:setObjetos(lista)
    self.objetos = lista
    self.fila = 0
end

function MC.Grilla:celdaEn(x, y)
    local c, f = math.floor(x / CELDA_W), math.floor(y / CELDA_H)
    if c >= self:cols() or c < 0 or f < 0 then return nil end
    return (self.fila + f) * self:cols() + c + 1
end

function MC.Grilla:prerender()
    rect(self, 0, 0, self.width, self.height, C.panel)
    local cols, filas = self:cols(), self:filas()
    local inicio = self.fila * cols
    local sel = MC.ventana and MC.ventana.elegido
    local hoverI = self:isMouseOver() and self:celdaEn(self:getMouseX(), self:getMouseY())
    for i = inicio + 1, math.min(#self.objetos, inicio + cols * filas) do
        local k = i - inicio - 1
        local x, y = (k % cols) * CELDA_W + 4, math.floor(k / cols) * CELDA_H + 4
        local obj = self.objetos[i]
        local bg = (obj == sel and C.verdeOsc) or (i == hoverI and C.hover) or C.tarjeta
        rect(self, x, y, CELDA_W - 8, CELDA_H - 8, bg)
        if obj == sel then borde(self, x, y, CELDA_W - 8, CELDA_H - 8, C.verde) end
        local tex = getTexture(obj.icono)
        if tex then self:drawTextureScaledAspect(tex, x + 8, y + 4, CELDA_W - 24, CELDA_H - 34, 1, 1, 1, 1) end
        texto(self, recortar(obj.nombre, FS, CELDA_W - 14), x + 4, y + CELDA_H - 8 - alto(FS) - 4, C.texto, FS)
    end
    -- barra de desplazamiento
    local total = math.ceil(#self.objetos / cols)
    if total > filas then
        local h = math.max(30, self.height * filas / total)
        local y = (self.height - h) * self.fila / (total - filas)
        rect(self, self.width - 6, 0, 6, self.height, C.fondo)
        rect(self, self.width - 6, y, 6, h, C.borde)
    end
    if #self.objetos == 0 then
        self:drawTextCentre("No hay objetos para mostrar", self.width / 2, self.height / 2 - 10, 0.6, 0.6, 0.6, 1, FM)
    end
    -- nombre completo del objeto bajo el mouse
    if hoverI and self.objetos[hoverI] then
        local t = self.objetos[hoverI].nombre
        local w = ancho(FS, t) + 14
        local tx = math.min(self:getMouseX() + 16, self.width - w - 4)
        rect(self, tx, self:getMouseY() + 14, w, alto(FS) + 8, C.fondo, 0.95)
        borde(self, tx, self:getMouseY() + 14, w, alto(FS) + 8, C.borde)
        texto(self, t, tx + 7, self:getMouseY() + 18, C.texto, FS)
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

function MC.PaginaCatalogo:new(x, y, w, h)
    local o = ISPanel.new(self, x, y, w, h)
    o.background = false
    o.textoBusqueda = ""
    return o
end

function MC.PaginaCatalogo:createChildren()
    local fh = alto(FS) + 12
    local detalleW = 230
    self.buscar = ISTextEntryBox:new("", 70, 0, 300, fh)
    self.buscar:initialise()
    self.buscar:instantiate()
    self:addChild(self.buscar)

    local top = fh + 12
    self.cats = MC.ListaCategorias:new(0, top, 170, self.height - top, function(c) self:elegirCategoria(c) end)
    self.cats:initialise()
    self:addChild(self.cats)

    self.grilla = MC.Grilla:new(180, top, self.width - 180 - detalleW - 10, self.height - top,
                                function(obj) self:elegirObjeto(obj) end)
    self.grilla:initialise()
    self:addChild(self.grilla)

    local dx = self.width - detalleW
    local by = top + 330
    local bw = detalleW
    self.btnColocar = MC.Boton:new(dx, by, bw, 36, "Colocar en el mundo", C.verdeOsc,
                                   function() if self.elegido then MC.tomarObjeto(self.elegido, self.variante) end end)
    self.btnColocar.fuente = FM
    self.btnRotar = MC.Boton:new(dx, by + 44, bw, 30, "Rotar  (tecla R)", C.tarjeta, function() self:rotar() end)
    self.btnBorrar = MC.Boton:new(dx, by + 82, bw, 30, "Herramienta borrar", {0.45, 0.14, 0.12},
                                  function() MC.tomarBorrar() end)
    self.btnSoltar = MC.Boton:new(dx, by + 120, bw, 30, "Soltar herramienta  (Esc)", C.tarjeta,
                                  function() MC.soltar() end)
    for _, b in ipairs({self.btnColocar, self.btnRotar, self.btnBorrar, self.btnSoltar}) do
        b:initialise()
        self:addChild(b)
    end
    self.detalleX, self.detalleTop = dx, top
    self:elegirCategoria(self.cats:items()[1])
end

function MC.PaginaCatalogo:elegirCategoria(c)
    self.categoria = c
    self:filtrar()
end

function MC.PaginaCatalogo:filtrar()
    local c = self.categoria
    if not c then return end
    local fuente
    if c.todo then
        if self.textoBusqueda == "" then
            fuente = {}            -- "Todo" sin búsqueda: muestra muebles para no cargar miles de tiles de golpe
            for _, cat in ipairs(MC.categorias()) do
                if cat.orden == 1 then fuente = MC.objetosDeCategoria(cat) end
            end
        else
            fuente = {}
            for _, cat in ipairs(MC.categorias()) do
                for _, o in ipairs(MC.objetosDeCategoria(cat)) do table.insert(fuente, o) end
            end
        end
    else
        fuente = MC.objetosDeCategoria(c)
    end
    local q = string.lower(self.textoBusqueda)
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
    -- búsqueda: se revisa el texto en cada cuadro (no depende de eventos del cuadro de texto)
    local t = self.buscar:getText() or ""
    if t ~= self.textoBusqueda then
        self.textoBusqueda = t
        self:filtrar()
    end
    texto(self, "Buscar:", 0, 6, C.texto, FS)
    texto(self, (self.cantidad or 0) .. " objetos", 384, 6, C.suave, FS)
    if self.categoria and self.categoria.todo and self.textoBusqueda == "" then
        texto(self, "(escribi algo para buscar en todo el catalogo)", 384 + ancho(FS, "0000 objetos  "), 6, C.suave, FS)
    end
    -- panel de detalle
    local x, y, w = self.detalleX, self.detalleTop, self.width - self.detalleX
    rect(self, x, y, w, 320, C.panel)
    local h = MC.herramienta
    if self.elegido then
        local sprite = self.elegido.variantes[self.variante or 1]
        local tex = getTexture(sprite)
        rect(self, x + 10, y + 10, w - 20, 170, C.fondo)
        if tex then self:drawTextureScaledAspect(tex, x + 20, y + 14, w - 40, 162, 1, 1, 1, 1) end
        local ty = y + 190
        for _, l in ipairs(renglones(self.elegido.nombre, FM, w - 20)) do
            texto(self, l, x + 10, ty, C.texto, FM)
            ty = ty + alto(FM) + 2
        end
        texto(self, recortar(self.elegido.hoja, FS, w - 20), x + 10, ty + 4, C.suave, FS)
        texto(self, "Orientacion " .. (self.variante or 1) .. " de " .. #self.elegido.variantes, x + 10,
              ty + 8 + alto(FS), C.suave, FS)
    else
        local ty = y + 20
        for _, l in ipairs(renglones("Elegi una categoria a la izquierda y despues un objeto de la grilla. "
                .. "Con un click queda listo: hace click en el mundo para colocarlo, cuantas veces quieras.",
                FS, w - 24)) do
            texto(self, l, x + 12, ty, C.suave, FS)
            ty = ty + alto(FS) + 3
        end
    end
    -- herramienta activa
    local estado = "Sin herramienta"
    local col = C.suave
    if h and h.borrar then
        estado, col = "BORRANDO: click en el mundo saca el objeto resaltado", C.rojo
    elseif h and h.objeto then
        estado, col = "COLOCANDO: click en el mundo", C.verde
    end
    local ly = self.detalleTop + 330 + 160
    for _, l in ipairs(renglones(estado, FS, w)) do
        texto(self, l, x, ly, col, FS)
        ly = ly + alto(FS) + 2
    end
    self.btnRotar.habilitado = self.elegido ~= nil and #self.elegido.variantes > 1
    self.btnColocar.habilitado = self.elegido ~= nil
    self.btnSoltar.habilitado = h ~= nil
end

-- ------------------------------------------------------------ página Ayuda
MC.PaginaAyuda = ISPanel:derive("ModoCreativoAyuda")

function MC.PaginaAyuda:new(x, y, w, h)
    local o = ISPanel.new(self, x, y, w, h)
    o.background = false
    return o
end

local AYUDA = {
    {"Abrir y cerrar", "Tecla Insert o el boton flotante con el icono (se puede arrastrar a cualquier lugar)."},
    {"Interruptor general", "Arriba a la derecha. Apagado, el juego vuelve a ser normal: lo que se enseno con el "
        .. "modo creativo se olvida y las acciones vuelven a tardar."},
    {"Ajustes", "Cada tarjeta prende o apaga una parte: construir gratis, acciones instantaneas y todas las recetas."},
    {"Catalogo", "Todos los objetos del juego, por categoria. Un click en un objeto lo toma; despues cada click en "
        .. "el mundo lo coloca. Los muebles de varias piezas se colocan enteros. R rota, Esc suelta."},
    {"Borrar", "La herramienta borrar resalta en rojo el objeto de mas arriba del cuadro; un click lo saca."},
    {"Partida", "Pensado para partidas de un jugador."},
}

function MC.PaginaAyuda:prerender()
    texto(self, "Como se usa", 0, 4, C.texto, FM)
    local y = 14 + alto(FM)
    for _, par in ipairs(AYUDA) do
        texto(self, par[1], 0, y, C.verde, FS)
        y = y + alto(FS) + 4
        for _, l in ipairs(renglones(par[2], FS, self.width - 20)) do
            texto(self, l, 12, y, C.suave, FS)
            y = y + alto(FS) + 2
        end
        y = y + 12
    end
end

-- ------------------------------------------------------------ ventana
MC.Ventana = ISCollapsableWindow:derive("ModoCreativoVentana")
local VW, VH = 1040, 680

function MC.Ventana:new(x, y)
    local o = ISCollapsableWindow.new(self, x, y, VW, VH)
    o.title = "Modo Creativo"
    o.resizable = false
    o.backgroundColor = {r = C.fondo[1], g = C.fondo[2], b = C.fondo[3], a = 0.97}
    o.borderColor = {r = C.borde[1], g = C.borde[2], b = C.borde[3], a = 1}
    return o
end

function MC.Ventana:initialise()
    ISCollapsableWindow.initialise(self)
    self:setWidth(VW)                -- medidas fijas: que nada las achique
    self:setHeight(VH)
end

function MC.Ventana:createChildren()
    ISCollapsableWindow.createChildren(self)
    local th = self:titleBarHeight()
    self.cabeceraY = th
    self.cabeceraH = 70
    local y0 = th + self.cabeceraH
    local navW = 190

    self.interruptor = MC.Boton:new(self.width - 280, th + 15, 260, 40, "", C.borde, function()
        local e = MC.estado()
        if e then MC.setActivo(not e.activo) end
    end)
    self.interruptor.fuente = FM
    self.interruptor:initialise()
    self:addChild(self.interruptor)

    self.navItems = {}
    local ny = y0 + 16
    for _, n in ipairs({{"ajustes", "Ajustes"}, {"catalogo", "Catalogo de objetos"}, {"ayuda", "Ayuda"}}) do
        local b = MC.Boton:new(12, ny, navW - 24, 40, n[2], C.tarjeta, function() self:mostrar(n[1]) end)
        b.clave = n[1]
        b:initialise()
        self:addChild(b)
        table.insert(self.navItems, b)
        ny = ny + 48
    end

    local cx, cw, ch = navW + 10, self.width - navW - 30, self.height - y0 - 30
    self.paginas = {
        ajustes = MC.PaginaAjustes:new(cx, y0 + 16, cw, ch),
        catalogo = MC.PaginaCatalogo:new(cx, y0 + 16, cw, ch),
        ayuda = MC.PaginaAyuda:new(cx, y0 + 16, cw, ch),
    }
    for _, p in pairs(self.paginas) do
        p:initialise()
        self:addChild(p)
    end
    self:mostrar(MC.ultimaPagina or "ajustes")
    self:actualizar()
end

function MC.Ventana:mostrar(clave)
    MC.ultimaPagina = clave
    for k, p in pairs(self.paginas) do p:setVisible(k == clave) end
    for _, b in ipairs(self.navItems) do b.color = (b.clave == clave) and C.verdeOsc or C.tarjeta end
end

function MC.Ventana:prerender()
    ISCollapsableWindow.prerender(self)
    local y = self.cabeceraY
    rect(self, 0, y, self.width, self.cabeceraH, C.panel)
    rect(self, 0, y + self.cabeceraH - 2, self.width, 2, C.borde)
    texto(self, "MODO CREATIVO", 20, y + 12, C.texto, FL)
    local e = MC.estado()
    local sub = (e and e.activo) and "Activado: construi y coloca lo que quieras." or
            "Apagado: el juego funciona normal."
    texto(self, sub, 20, y + 16 + alto(FL), (e and e.activo) and C.verde or C.suave, FS)
    rect(self, 190, y + self.cabeceraH, 1, self.height - y - self.cabeceraH, C.borde)
end

function MC.Ventana:actualizar()
    local e = MC.estado()
    if not e or not self.interruptor then return end
    self.interruptor.titulo = e.activo and "ACTIVADO" or "DESACTIVADO"
    self.interruptor.color = e.activo and C.verde or C.borde
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
    local x = math.max(0, (getCore():getScreenWidth() - VW) / 2)
    local y = math.max(0, (getCore():getScreenHeight() - VH) / 2)
    MC.ventana = MC.Ventana:new(x, y)
    MC.ventana:initialise()
    MC.ventana:addToUIManager()
    MC.ventana:bringToTop()
end
