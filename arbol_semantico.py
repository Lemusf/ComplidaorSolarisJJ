"""
Visor del arbol semantico para la interfaz del compilador Solaris.

Cada nodo tiene 3 compartimentos: uno ancho arriba (top) y dos abajo
(left / right, por ejemplo "valor" y el valor calculado).

Se dibuja en un tk.Canvas: las cajas se miden en pixeles con la fuente real,
asi el texto siempre cabe en su caja aunque el arbol sea grande.

Controles:
  - rueda del mouse ........ zoom (sobre el punto donde esta el cursor)
  - arrastrar el fondo ..... mover la vista (clic izquierdo o derecho)
  - arrastrar un nodo ...... mover ese nodo junto con sus hijos
  - doble clic / Ajustar ... volver a encuadrar todo el arbol
"""

import sys
import tkinter as tk
import tkinter.font as tkfont
import customtkinter as ctk


# ---------------------------------------------------------------------------
# Modelo
# ---------------------------------------------------------------------------

class NodoArbol:
    """Nodo con 3 campos: top (arriba), left y right (abajo)."""

    def __init__(self, top, left="", right="", hijos=None):
        self.top = top
        self.left = left
        self.right = right
        self.hijos = hijos or []
        self.x = 0.0      # centro de la caja, en pixeles con zoom 1
        self.y = 0.0      # borde de arriba de la caja
        self.ancho = 0.0
        self.alto = 0.0


def arbol_desde_dict(data):
    """Convierte el dict que arma el semantico ({"top", "left", "right", "hijos"})
    en un NodoArbol."""
    if not isinstance(data, dict) or "top" not in data:
        raise ValueError("Cada nodo necesita al menos la clave 'top'. Recibido: %r" % (data,))
    hijos = [arbol_desde_dict(h) for h in data.get("hijos", [])]
    return NodoArbol(
        top=str(data["top"]),
        left=str(data.get("left", "")),
        right=str(data.get("right", "")),
        hijos=hijos,
    )


def recorrer(nodo):
    """Todos los nodos del arbol, del padre a los hijos."""
    yield nodo
    for hijo in nodo.hijos:
        yield from recorrer(hijo)


# ---------------------------------------------------------------------------
# Visor
# ---------------------------------------------------------------------------

COLORES = {
    #                  claro       oscuro
    "fondo":        ("#F5F7FA", "#1E1E22"),
    "caja":         ("#FFFFFF", "#1F2937"),
    "borde":        ("#3B6FE0", "#4DA3FF"),
    "textoTop":     ("#1A202C", "#FFFFFF"),
    "textoAbajo":   ("#4A5568", "#C9D6E3"),
    "linea":        ("#9AA3AF", "#7A808A"),
    "ayuda":        ("#6B7280", "#9AA3AF"),
}


class VisorArbolSemantico(ctk.CTkFrame):

    PIX_TOP = 14          # tamaño de letra (pixeles) del nombre del nodo, con zoom 1
    PIX_ABAJO = 12        # tamaño de letra de left / right
    PAD = 8               # margen interno de la caja
    ANCHO_MIN = 60
    ANCHO_MAX = 240       # si el texto es mas largo se parte en renglones
    MAX_RENGLONES = 6     # renglones maximos del valor (right) antes de recortar
    SEP_X = 22            # espacio horizontal entre subarboles
    SEP_Y = 44            # espacio vertical entre niveles
    ZOOM_MIN = 0.15
    ZOOM_MAX = 3.0

    def __init__(self, master, raiz, **kwargs):
        super().__init__(master, **kwargs)

        self.canvas = tk.Canvas(self, highlightthickness=0, bd=0)
        self.canvas.pack(fill="both", expand=True)

        familia = tkfont.nametofont("TkDefaultFont").actual()["family"]
        self.fuenteTop = tkfont.Font(family=familia, size=-self.PIX_TOP, weight="bold")
        self.fuenteAbajo = tkfont.Font(family=familia, size=-self.PIX_ABAJO)
        # copias que no cambian con el zoom, solo para medir al calcular el layout
        self.medidaTop = tkfont.Font(family=familia, size=-self.PIX_TOP, weight="bold")
        self.medidaAbajo = tkfont.Font(family=familia, size=-self.PIX_ABAJO)

        self.zoom = 1.0
        self.offX = 0.0       # donde cae el (0, 0) del arbol en la pantalla
        self.offY = 0.0
        self.itemANodo = {}   # id del canvas -> nodo
        self.nodoArrastrado = None
        self.ultimoMouse = None
        self.moviendoVista = False
        self.ajustePendiente = True

        self._construirControles()
        self._enlazarEventos()
        self.cargar_arbol(raiz)

    # -- API que usa la interfaz -----------------------------------------
    def cargar_arbol(self, nueva_raiz, conservar_vista=False):
        """Pone otro arbol en el visor. Si conservar_vista es False se vuelve
        a encuadrar el arbol completo."""
        self.raiz = nueva_raiz
        self.nodoArrastrado = None
        self._calcularLayout()
        if conservar_vista:
            self.redibujar()
        else:
            self.ajustar()

    def ajustar(self):
        """Encuadra todo el arbol en el espacio visible."""
        ancho = self.canvas.winfo_width()
        alto = self.canvas.winfo_height()
        if ancho < 20 or alto < 20:
            # el visor aun no esta en pantalla: se ajusta cuando tenga tamaño
            self.ajustePendiente = True
            return
        self.ajustePendiente = False
        x0, y0, x1, y1 = self._limitesArbol()
        margen = 30
        zoomX = (ancho - 2 * margen) / max(1.0, x1 - x0)
        zoomY = (alto - 2 * margen - 24) / max(1.0, y1 - y0)   # 24 = renglon de ayuda
        self.zoom = max(self.ZOOM_MIN, min(zoomX, zoomY, 1.3))
        self.offX = ancho / 2 - (x0 + x1) / 2 * self.zoom
        if (y1 - y0) * self.zoom < alto - 2 * margen - 24:
            self.offY = (alto - 24) / 2 - (y0 + y1) / 2 * self.zoom   # cabe: centrado
        else:
            self.offY = margen - y0 * self.zoom                       # no cabe: desde arriba
        self.redibujar()

    def redibujar(self):
        """Vuelve a pintar todo (por ejemplo al cambiar de tema claro/oscuro)."""
        c = self.canvas
        c.delete("all")
        self.itemANodo = {}
        c.configure(bg=self._color("fondo"))
        self.fuenteTop.configure(size=-max(1, round(self.PIX_TOP * self.zoom)))
        self.fuenteAbajo.configure(size=-max(1, round(self.PIX_ABAJO * self.zoom)))
        conTexto = self.PIX_ABAJO * self.zoom >= 5      # muy alejado el texto ya no se lee

        for nodo in recorrer(self.raiz):
            px, py = self._aPantalla(nodo.x, nodo.y + nodo.alto)
            for hijo in nodo.hijos:
                hx, hy = self._aPantalla(hijo.x, hijo.y)
                c.create_line(px, py, hx, hy, fill=self._color("linea"), width=1.2)

        for nodo in recorrer(self.raiz):
            self._dibujarNodo(nodo, conTexto)

        c.create_text(10, c.winfo_height() - 8, anchor="sw", fill=self._color("ayuda"),
                      font=self.medidaAbajo,
                      text="Rueda: zoom   ·   Arrastrar fondo: mover   ·   "
                           "Arrastrar nodo: moverlo   ·   Doble clic: ajustar")

    # -- layout (en pixeles con zoom 1) -----------------------------------
    def _calcularLayout(self):
        for nodo in recorrer(self.raiz):
            self._medirNodo(nodo)

        # alto de cada nivel = el nodo mas alto de ese nivel
        altos = {}
        self._medirNiveles(self.raiz, 0, altos)
        yNivel = {}
        y = 0.0
        for nivel in sorted(altos):
            yNivel[nivel] = y
            y += altos[nivel] + self.SEP_Y

        self._anchoSubarbol(self.raiz)
        self._colocar(self.raiz, 0.0, 0, yNivel)

    def _medirNodo(self, nodo):
        anchoTop = max((self.medidaTop.measure(p) for p in nodo.top.split()), default=0)
        anchoTop = max(anchoTop, self.medidaTop.measure(nodo.top))
        anchoLeft = self.medidaAbajo.measure(nodo.left)
        anchoRight = self.medidaAbajo.measure(nodo.right)
        natural = max(anchoTop + 2 * self.PAD, anchoLeft + anchoRight + 4 * self.PAD)
        nodo.ancho = max(self.ANCHO_MIN, min(self.ANCHO_MAX, natural))

        # la columna de left mide lo que su texto; solo se achica si el valor no cabe
        if nodo.left == "" and nodo.right == "":
            nodo.anchoLeft = nodo.ancho / 2
        else:
            nodo.anchoLeft = min(anchoLeft + 2 * self.PAD,
                                 max(nodo.ancho / 2, nodo.ancho - (anchoRight + 2 * self.PAD)))
        nodo.lineasTop = self._partir(nodo.top, nodo.ancho - 2 * self.PAD, self.medidaTop)
        nodo.lineasLeft = self._partir(nodo.left, nodo.anchoLeft - 2 * self.PAD, self.medidaAbajo)
        nodo.lineasRight = self._partir(nodo.right, nodo.ancho - nodo.anchoLeft - 2 * self.PAD,
                                        self.medidaAbajo)
        if len(nodo.lineasRight) > self.MAX_RENGLONES:
            nodo.lineasRight = nodo.lineasRight[:self.MAX_RENGLONES]
            nodo.lineasRight[-1] = nodo.lineasRight[-1].rstrip() + "…"

        altoLineaTop = self.medidaTop.metrics("linespace")
        altoLineaAbajo = self.medidaAbajo.metrics("linespace")
        renglonesAbajo = max(1, len(nodo.lineasLeft), len(nodo.lineasRight))
        nodo.altoTop = len(nodo.lineasTop) * altoLineaTop + self.PAD
        nodo.altoAbajo = renglonesAbajo * altoLineaAbajo + self.PAD
        nodo.alto = nodo.altoTop + nodo.altoAbajo

    def _partir(self, texto, anchoMax, fuente):
        """Parte el texto en renglones que quepan en anchoMax pixeles."""
        if texto == "":
            return [""]
        if fuente.measure(texto) <= anchoMax:
            return [texto]
        renglones = []
        actual = ""
        for palabra in texto.split(" "):
            prueba = palabra if actual == "" else actual + " " + palabra
            if fuente.measure(prueba) <= anchoMax:
                actual = prueba
                continue
            if actual != "":
                renglones.append(actual)
            # palabra mas larga que el renglon: se corta por letras
            while fuente.measure(palabra) > anchoMax and len(palabra) > 1:
                corte = len(palabra) - 1
                while corte > 1 and fuente.measure(palabra[:corte]) > anchoMax:
                    corte -= 1
                renglones.append(palabra[:corte])
                palabra = palabra[corte:]
            actual = palabra
        if actual != "":
            renglones.append(actual)
        return renglones or [""]

    def _medirNiveles(self, nodo, nivel, altos):
        altos[nivel] = max(altos.get(nivel, 0.0), nodo.alto)
        for hijo in nodo.hijos:
            self._medirNiveles(hijo, nivel + 1, altos)

    def _anchoSubarbol(self, nodo):
        """Ancho que ocupa el nodo con todos sus hijos (para que no se encimen)."""
        if not nodo.hijos:
            nodo.anchoSub = nodo.ancho
        else:
            suma = 0.0
            for hijo in nodo.hijos:
                suma += self._anchoSubarbol(hijo)
            suma += self.SEP_X * (len(nodo.hijos) - 1)
            nodo.anchoSub = max(nodo.ancho, suma)
        return nodo.anchoSub

    def _colocar(self, nodo, izquierda, nivel, yNivel):
        """Pone al nodo centrado en su espacio y a sus hijos uno junto al otro debajo."""
        nodo.x = izquierda + nodo.anchoSub / 2
        nodo.y = yNivel[nivel]
        if nodo.hijos:
            anchoHijos = sum(h.anchoSub for h in nodo.hijos) + self.SEP_X * (len(nodo.hijos) - 1)
            x = izquierda + (nodo.anchoSub - anchoHijos) / 2
            for hijo in nodo.hijos:
                self._colocar(hijo, x, nivel + 1, yNivel)
                x += hijo.anchoSub + self.SEP_X

    def _limitesArbol(self):
        nodos = list(recorrer(self.raiz))
        return (min(n.x - n.ancho / 2 for n in nodos), min(n.y for n in nodos),
                max(n.x + n.ancho / 2 for n in nodos), max(n.y + n.alto for n in nodos))

    # -- dibujo de un nodo -------------------------------------------------
    def _dibujarNodo(self, nodo, conTexto):
        c = self.canvas
        z = self.zoom
        x0, y0 = self._aPantalla(nodo.x - nodo.ancho / 2, nodo.y)
        x1, y1 = self._aPantalla(nodo.x + nodo.ancho / 2, nodo.y + nodo.alto)
        yDiv = y0 + nodo.altoTop * z
        xDiv = x0 + nodo.anchoLeft * z
        borde = self._color("borde")

        ids = [
            c.create_rectangle(x0, y0, x1, y1, fill=self._color("caja"), outline=borde, width=1.4),
            c.create_line(x0, yDiv, x1, yDiv, fill=borde),
            c.create_line(xDiv, yDiv, xDiv, y1, fill=borde),
        ]
        if conTexto:
            ids.append(c.create_text((x0 + x1) / 2, (y0 + yDiv) / 2, text="\n".join(nodo.lineasTop),
                                     font=self.fuenteTop, fill=self._color("textoTop"),
                                     justify="center"))
            ids.append(c.create_text((x0 + xDiv) / 2, (yDiv + y1) / 2, text="\n".join(nodo.lineasLeft),
                                     font=self.fuenteAbajo, fill=self._color("textoAbajo"),
                                     justify="center"))
            ids.append(c.create_text((xDiv + x1) / 2, (yDiv + y1) / 2, text="\n".join(nodo.lineasRight),
                                     font=self.fuenteAbajo, fill=self._color("textoAbajo"),
                                     justify="center"))
        for i in ids:
            self.itemANodo[i] = nodo

    # -- controles y eventos ----------------------------------------------
    def _construirControles(self):
        barra = ctk.CTkFrame(self, fg_color="transparent")
        barra.place(relx=1.0, x=-10, y=10, anchor="ne")
        ctk.CTkButton(barra, text="−", width=32, height=28,
                      command=lambda: self._zoomCentro(1 / 1.2)).pack(side="left", padx=2)
        ctk.CTkButton(barra, text="+", width=32, height=28,
                      command=lambda: self._zoomCentro(1.2)).pack(side="left", padx=2)
        ctk.CTkButton(barra, text="Ajustar", width=70, height=28,
                      command=self.ajustar).pack(side="left", padx=2)

    def _enlazarEventos(self):
        c = self.canvas
        c.bind("<Configure>", self._alCambiarTamano)
        c.bind("<ButtonPress-1>", self._alPresionar)
        c.bind("<B1-Motion>", self._alMover)
        c.bind("<ButtonRelease-1>", self._alSoltar)
        c.bind("<Double-Button-1>", lambda e: self.ajustar())
        # boton derecho (en mac puede ser el 2) siempre mueve la vista
        for boton in ("3", "2"):
            c.bind(f"<ButtonPress-{boton}>", self._alPresionarFondo)
            c.bind(f"<B{boton}-Motion>", self._alMover)
            c.bind(f"<ButtonRelease-{boton}>", self._alSoltar)
        # rueda: Windows y mac mandan <MouseWheel>, Linux manda Button-4 / Button-5
        c.bind("<MouseWheel>", lambda e: self._zoomEn(e.x, e.y, 1.1 if e.delta > 0 else 1 / 1.1))
        c.bind("<Button-4>", lambda e: self._zoomEn(e.x, e.y, 1.1))
        c.bind("<Button-5>", lambda e: self._zoomEn(e.x, e.y, 1 / 1.1))

    def _alCambiarTamano(self, evento):
        if self.ajustePendiente:
            self.ajustar()
        else:
            self.redibujar()     # para reacomodar el texto de ayuda de abajo

    def _alPresionar(self, evento):
        self.ultimoMouse = (evento.x, evento.y)
        encima = self.canvas.find_overlapping(evento.x, evento.y, evento.x, evento.y)
        self.nodoArrastrado = None
        for item in reversed(encima):          # el de mas arriba primero
            if item in self.itemANodo:
                self.nodoArrastrado = self.itemANodo[item]
                break
        self.moviendoVista = self.nodoArrastrado is None
        if self.moviendoVista:
            self.canvas.configure(cursor="fleur")

    def _alPresionarFondo(self, evento):
        self.ultimoMouse = (evento.x, evento.y)
        self.nodoArrastrado = None
        self.moviendoVista = True
        self.canvas.configure(cursor="fleur")

    def _alMover(self, evento):
        if self.ultimoMouse is None:
            return
        dx = evento.x - self.ultimoMouse[0]
        dy = evento.y - self.ultimoMouse[1]
        self.ultimoMouse = (evento.x, evento.y)
        if self.nodoArrastrado is not None:
            for nodo in recorrer(self.nodoArrastrado):   # se mueve con todo y sus hijos
                nodo.x += dx / self.zoom
                nodo.y += dy / self.zoom
            self.redibujar()
        elif self.moviendoVista:
            self.offX += dx
            self.offY += dy
            self.redibujar()

    def _alSoltar(self, evento):
        self.nodoArrastrado = None
        self.moviendoVista = False
        self.ultimoMouse = None
        self.canvas.configure(cursor="")

    def _zoomEn(self, mx, my, factor):
        nuevo = max(self.ZOOM_MIN, min(self.ZOOM_MAX, self.zoom * factor))
        if nuevo == self.zoom:
            return
        # el punto que esta bajo el cursor se queda en el mismo lugar
        self.offX = mx - (mx - self.offX) * nuevo / self.zoom
        self.offY = my - (my - self.offY) * nuevo / self.zoom
        self.zoom = nuevo
        self.redibujar()

    def _zoomCentro(self, factor):
        self._zoomEn(self.canvas.winfo_width() / 2, self.canvas.winfo_height() / 2, factor)

    # -- utilidades ---------------------------------------------------------
    def _aPantalla(self, x, y):
        return x * self.zoom + self.offX, y * self.zoom + self.offY

    def _color(self, clave):
        claro, oscuro = COLORES[clave]
        return claro if ctk.get_appearance_mode() == "Light" else oscuro


# ---------------------------------------------------------------------------
# Prueba suelta: python arbol_semantico.py
# ---------------------------------------------------------------------------

def _arbolEjemplo():
    hoja = lambda t: {"top": t}
    operando = lambda v: {"top": "operando", "left": "valor", "right": v,
                          "hijos": [{"top": "nomVar", "left": "valor", "right": v, "hijos": [hoja(v)]}]}
    return {"top": "operacion", "left": "valor", "right": "a+b*c", "hijos": [
        {"top": "nomVar", "left": "valor", "right": "x", "hijos": [hoja("x")]},
        hoja("="),
        {"top": "expr", "left": "valor", "right": "a+b*c", "hijos": [
            operando("a"), hoja("+"),
            {"top": "termino", "left": "valor", "right": "b*c",
             "hijos": [operando("b"), hoja("*"), operando("c")]}]}]}


if __name__ == "__main__":
    app = ctk.CTk()
    app.title("Arbol semantico")
    app.geometry("950x650")
    visor = VisorArbolSemantico(app, arbol_desde_dict(_arbolEjemplo()))
    visor.pack(fill="both", expand=True, padx=10, pady=10)
    app.mainloop()