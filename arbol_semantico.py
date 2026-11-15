"""
Visualizador de árbol semántico jerárquico embebido en CustomTkinter.
Cada nodo tiene 3 compartimentos: uno ancho arriba (nombre/valor del nodo)
y dos del mismo tamaño abajo (por ejemplo línea y tipo).
Los nodos son arrastrables con el mouse.
"""

import json
import re
import sys
import textwrap
import customtkinter as ctk
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ---------------------------------------------------------------------------
# Modelo del nodo
# ---------------------------------------------------------------------------

class NodoArbol:
    """Nodo de árbol con 3 campos: top (ancho), left y right (iguales)."""

    def __init__(self, top, left="", right="", hijos=None):
        self.top = top
        self.left = left
        self.right = right
        self.hijos = hijos or []
        self.x = 0.0
        self.y = 0.0


# ---------------------------------------------------------------------------
# Construcción del árbol a partir de un dict / JSON
# ---------------------------------------------------------------------------
#
# Formato esperado (cada nodo):
#   {
#     "top": "SUMA",             -> obligatorio, campo ancho de arriba
#     "left": "línea 1",         -> opcional, campo inferior izquierdo
#     "right": "tipo: int",      -> opcional, campo inferior derecho
#     "hijos": [ {...}, {...} ]  -> opcional, lista de nodos hijos
#   }

def arbol_desde_dict(data):
    """Convierte un dict (o el resultado de json.load) en un NodoArbol,
    recorriendo 'hijos' recursivamente."""
    if not isinstance(data, dict) or "top" not in data:
        raise ValueError(
            "Cada nodo necesita al menos la clave 'top'. Recibido: %r" % (data,)
        )

    hijos_data = data.get("hijos", [])
    hijos = [arbol_desde_dict(h) for h in hijos_data]

    return NodoArbol(
        top=str(data["top"]),
        left=str(data.get("left", "")),
        right=str(data.get("right", "")),
        hijos=hijos,
    )


def cargar_arbol(self, nueva_raiz, conservar_vista=False):
    asignar_posiciones(nueva_raiz)
    self.raiz = nueva_raiz
    self.nodo_arrastrado = None
    if not conservar_vista:
        self.xlim = None
        self.ylim = None
        self._ancho_base = None   # <-- NUEVO
    self._dibujar()

# ---------------------------------------------------------------------------
# Layout jerárquico (posiciones x, y por nivel)
# ---------------------------------------------------------------------------

def asignar_posiciones(nodo, profundidad=0, contador=None):
    if contador is None:
        contador = [0]

    if not nodo.hijos:
        nodo.x = contador[0]
        contador[0] += 1
    else:
        for hijo in nodo.hijos:
            asignar_posiciones(hijo, profundidad + 1, contador)
        xs = [h.x for h in nodo.hijos]
        nodo.x = sum(xs) / len(xs)

    nodo.y = -profundidad
    return nodo


def recorrer(nodo):
    """Generador de todos los nodos del árbol (para dibujar/enlazar eventos)."""
    yield nodo
    for hijo in nodo.hijos:
        yield from recorrer(hijo)


# ---------------------------------------------------------------------------
# Widget de árbol embebido en CTk
# ---------------------------------------------------------------------------

class VisorArbolSemantico(ctk.CTkFrame):

    # Tamaño de nodo: ahora es dinámico según el texto, estos son sólo
    # los límites razonables (mínimo / máximo) para que un nodo nunca
    # quede demasiado chico ni crezca sin control.
    ANCHO_NODO_MIN = 2.0
    ANCHO_NODO_MAX = 5.5
    ALTO_NODO = 1.1
    ALTO_LINEA_EXTRA = 0.42        # alto adicional por cada línea extra de "top"
    ESCALA_X = 0.9                 # separación horizontal entre nodos hermanos
    ESCALA_Y = 2.6                 # separación vertical entre niveles

    MAX_CARACTERES_TOP = 16        # ancho máx. (en caracteres) de una línea de "top"
    MAX_CARACTERES_LR = 13         # ancho máx. (en caracteres) para "left"/"right"

    FUENTE_TOP_BASE = 10
    FUENTE_LR_BASE = 8.5
    ANCHO_POR_CARACTER = 0.021     # estimación: unidades de dato por punto·carácter

    def __init__(self, master, raiz, **kwargs):
        super().__init__(master, **kwargs)

        self.raiz = raiz
        self.nodo_arrastrado = None

        self.fig, self.ax = plt.subplots(figsize=(8, 5.5))
        self.fig.patch.set_facecolor("#2b2b2b")
        self.ax.set_facecolor("#2b2b2b")

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # Eventos de arrastre
        self.canvas.mpl_connect("button_press_event", self._on_press)
        self.canvas.mpl_connect("motion_notify_event", self._on_motion)
        self.canvas.mpl_connect("button_release_event", self._on_release)
        self.canvas.mpl_connect("scroll_event", self._on_scroll)

        # límites "naturales" del árbol (se recalculan en _dibujar);
        # se usan como referencia para no perder el zoom al redibujar
        self.xlim = None
        self.ylim = None
        self._ancho_base = None

        # estado del desplazamiento (pan) con click derecho
        self.pan_activo = False
        self.pan_origen = None  # (x_dato, y_dato) al presionar

        self._calcular_layout(self.raiz)
        self._dibujar()

    # -- reemplazar el árbol completo (dinámico) -----------------------
    def cargar_arbol(self, nueva_raiz, conservar_vista=False):
        """Sustituye el árbol mostrado por otro NodoArbol ya construido
        (por ejemplo, el resultado de arbol_desde_dict / cargar_arbol_json).
        Si conservar_vista=False, el zoom/pan se resetea al nuevo árbol."""
        self.raiz = nueva_raiz
        self.nodo_arrastrado = None
        self._calcular_layout(self.raiz)
        if not conservar_vista:
            self.xlim = None
            self.ylim = None
        self._dibujar()

    # -- utilidades de texto -------------------------------------------
    def _envolver(self, texto):
        """Divide un texto largo en varias líneas cortas para que nunca
        se salga del recuadro del nodo."""
        if not texto:
            return [""]
        return textwrap.wrap(texto, width=self.MAX_CARACTERES_TOP) or [""]

    def _acortar(self, texto, maximo):
        """Recorta un texto (left/right) que no quepa en una sola línea,
        en vez de dejar que se dibuje fuera del nodo."""
        if len(texto) <= maximo:
            return texto
        return texto[: max(1, maximo - 1)] + "…"

    def _ancho_texto(self, lineas, fontsize):
        if not lineas:
            return 0.0
        mas_larga = max((len(linea) for linea in lineas), default=0)
        return mas_larga * fontsize * self.ANCHO_POR_CARACTER

    # -- calcula tamaño (ancho/alto) y posición (x, y) de cada nodo --------
    def _calcular_layout(self, raiz):
        """Calcula, en una sola pasada y con tamaños de fuente de
        referencia, el tamaño real de cada nodo según su contenido y su
        posición final. El zoom sólo afecta la presentación (tamaño de
        letra visible) y nunca el layout, así las cajas no se desalinean
        ni se salen de su lugar al hacer zoom o desplazar la vista."""

        # 1) texto a mostrar (envuelto/recortado) y tamaño de cada nodo
        for nodo in recorrer(raiz):
            nodo.lineas_top = self._envolver(nodo.top)
            nodo.left_mostrado = self._acortar(nodo.left, self.MAX_CARACTERES_LR)
            nodo.right_mostrado = self._acortar(nodo.right, self.MAX_CARACTERES_LR)

            ancho_top = self._ancho_texto(nodo.lineas_top, self.FUENTE_TOP_BASE) + 0.5
            ancho_lr = (
                self._ancho_texto([nodo.left_mostrado], self.FUENTE_LR_BASE)
                + self._ancho_texto([nodo.right_mostrado], self.FUENTE_LR_BASE)
                + 0.6
            )
            nodo.ancho = min(self.ANCHO_NODO_MAX,
                              max(self.ANCHO_NODO_MIN, ancho_top, ancho_lr))

            lineas_extra = max(0, len(nodo.lineas_top) - 1)
            nodo.alto = self.ALTO_NODO + lineas_extra * self.ALTO_LINEA_EXTRA

        # 2) posición x: las hojas se colocan una tras otra según su
        #    ancho real (en vez de una separación fija por índice), y
        #    cada padre se centra sobre sus hijos.
        contador = [0.0]

        def _asignar_x(nodo):
            if not nodo.hijos:
                nodo.x = contador[0] + nodo.ancho / 2
                contador[0] += nodo.ancho + self.ESCALA_X
            else:
                for hijo in nodo.hijos:
                    _asignar_x(hijo)
                nodo.x = (nodo.hijos[0].x + nodo.hijos[-1].x) / 2

        _asignar_x(raiz)

        # 3) posición y: la altura de cada nivel depende del nodo más
        #    alto de ese nivel (por si algún "top" se envolvió en varias
        #    líneas), evitando que un nivel se encime con el siguiente.
        alturas_nivel = {}

        def _medir_niveles(nodo, profundidad=0):
            alturas_nivel[profundidad] = max(alturas_nivel.get(profundidad, 0.0), nodo.alto)
            for hijo in nodo.hijos:
                _medir_niveles(hijo, profundidad + 1)

        _medir_niveles(raiz)

        y_para_nivel = {}
        y_actual = 0.0
        separacion_extra = max(0.4, self.ESCALA_Y - self.ALTO_NODO)
        for nivel in sorted(alturas_nivel):
            y_para_nivel[nivel] = y_actual - alturas_nivel[nivel] / 2
            y_actual -= alturas_nivel[nivel] + separacion_extra

        def _asignar_y(nodo, profundidad=0):
            nodo.y = y_para_nivel[profundidad]
            for hijo in nodo.hijos:
                _asignar_y(hijo, profundidad + 1)

        _asignar_y(raiz)

    # -- posición real de un nodo (ya en unidades de dato finales) ---------
    def _pos(self, nodo):
        return nodo.x, nodo.y

    # -- dibujo completo -----------------------------------------------------
    def _dibujar(self):
        self.ax.clear()
        self.ax.set_facecolor("#2b2b2b")
        self.ax.axis("off")

        # factor de escala de fuente segun el zoom actual
        if self.xlim is not None and self._ancho_base:
            ancho_actual = self.xlim[1] - self.xlim[0]
            factor_zoom = self._ancho_base / ancho_actual if ancho_actual > 0 else 1.0
        else:
            factor_zoom = 1.0
        factor_zoom = max(0.7, min(factor_zoom, 2.2))  # limites razonables

        fuente_top = self.FUENTE_TOP_BASE * factor_zoom
        fuente_lr = self.FUENTE_LR_BASE * factor_zoom

        # líneas de conexión padre -> hijo (siempre recortadas a los ejes,
        # para que nunca queden "flotando" fuera del área visible)
        for nodo in recorrer(self.raiz):
            px, py = self._pos(nodo)
            for hijo in nodo.hijos:
                cx, cy = self._pos(hijo)
                self.ax.plot(
                    [px, cx], [py - nodo.alto / 2, cy + hijo.alto / 2],
                    color="#888888", linewidth=1.2, zorder=1, clip_on=True,
                )

        for nodo in recorrer(self.raiz):
            x, y = self._pos(nodo)
            w, h = nodo.ancho, nodo.alto

            rect = patches.FancyBboxPatch(
                (x - w / 2, y - h / 2), w, h,
                boxstyle="round,pad=0.02,rounding_size=0.06",
                linewidth=1.3, edgecolor="#4da3ff",
                facecolor="#1f2937", zorder=2, clip_on=True,
            )
            self.ax.add_patch(rect)

            # el compartimento inferior (left/right) siempre mide lo mismo;
            # el superior ("top") crece si el texto se envolvió en más líneas
            alto_inferior = self.ALTO_NODO / 2
            alto_superior = h - alto_inferior
            y_divisor = y - h / 2 + alto_inferior
            y_centro_top = y_divisor + alto_superior / 2
            y_centro_inf = y - h / 2 + alto_inferior / 2

            self.ax.plot([x - w / 2, x + w / 2], [y_divisor, y_divisor],
                         color="#4da3ff", linewidth=1.0, zorder=3, clip_on=True)
            self.ax.plot([x, x], [y - h / 2, y_divisor],
                         color="#4da3ff", linewidth=1.0, zorder=3, clip_on=True)

            # IMPORTANTE: clip_on=True en todo el texto -- por defecto
            # matplotlib NO recorta los textos a los límites del eje, así
            # que al desplazar o arrastrar un nodo fuera de la vista el
            # recuadro (que sí se recorta) desaparecía pero el texto se
            # quedaba "flotando" solo en la pantalla. Con clip_on=True el
            # texto se oculta junto con su nodo, como debe ser.
            self.ax.text(x, y_centro_top, "\n".join(nodo.lineas_top),
                         ha="center", va="center", fontsize=fuente_top,
                         color="white", fontweight="bold", zorder=4,
                         clip_on=True)
            self.ax.text(x - w / 4, y_centro_inf, nodo.left_mostrado,
                         ha="center", va="center", fontsize=fuente_lr,
                         color="#c9d6e3", zorder=4, clip_on=True)
            self.ax.text(x + w / 4, y_centro_inf, nodo.right_mostrado,
                         ha="center", va="center", fontsize=fuente_lr,
                         color="#c9d6e3", zorder=4, clip_on=True)

        if self.xlim is None or self.ylim is None:
            # el área "natural" se calcula a partir de los bordes reales
            # de cada nodo (no sólo su centro), para que ningún nodo
            # ancho quede cortado en la vista inicial
            xs_min = min(n.x - n.ancho / 2 for n in recorrer(self.raiz))
            xs_max = max(n.x + n.ancho / 2 for n in recorrer(self.raiz))
            ys_min = min(n.y - n.alto / 2 for n in recorrer(self.raiz))
            ys_max = max(n.y + n.alto / 2 for n in recorrer(self.raiz))
            self.xlim = (xs_min - 1.0, xs_max + 1.0)
            self.ylim = (ys_min - 1.0, ys_max + 1.0)
            self._ancho_base = self.xlim[1] - self.xlim[0]   # <-- referencia

        self.ax.set_xlim(*self.xlim)
        self.ax.set_ylim(*self.ylim)
        # Antes se forzaba aspect="equal": como el ancho de un nodo y la
        # separación entre niveles usan escalas distintas, eso hacía que
        # el área útil de dibujo quedara angosta y casi vertical. Con
        # aspect="auto" (el valor por defecto) el árbol aprovecha todo el
        # ancho disponible del widget.
        self.ax.set_aspect("auto")
        self.canvas.draw_idle()

    # -- desplazamiento (pan) con click derecho -----------------------------
    def _on_scroll(self, event):
        if event.inaxes != self.ax or event.xdata is None:
            return
        factor = 0.9 if event.button == "up" else 1.1
        x0, x1 = self.ax.get_xlim()
        y0, y1 = self.ax.get_ylim()
        xc, yc = event.xdata, event.ydata

        nuevo_x0 = xc - (xc - x0) * factor
        nuevo_x1 = xc + (x1 - xc) * factor
        ancho_nuevo = nuevo_x1 - nuevo_x0

        # no dejar que se acerque/aleje mas de lo razonable
        if self._ancho_base:
            if ancho_nuevo < self._ancho_base * 0.15 or ancho_nuevo > self._ancho_base * 4.0:
                return

        self.xlim = (nuevo_x0, nuevo_x1)
        self.ylim = (yc - (yc - y0) * factor, yc + (y1 - yc) * factor)
        self._dibujar()

    # -- detección de nodo bajo el cursor -------------------------------
    def _nodo_en(self, xdata, ydata):
        for nodo in recorrer(self.raiz):
            x, y = self._pos(nodo)
            w, h = nodo.ancho, nodo.alto
            if (x - w / 2) <= xdata <= (x + w / 2) and (y - h / 2) <= ydata <= (y + h / 2):
                return nodo
        return None

    # -- eventos de mouse -----------------------------------------------
    def _on_press(self, event):
        if event.inaxes != self.ax or event.xdata is None:
            return

        if event.button == 3:  # click derecho: iniciar desplazamiento (pan)
            self.pan_activo = True
            self.pan_origen = (event.xdata, event.ydata)
            return

        if event.button == 1:  # click izquierdo: iniciar arrastre de nodo
            self.nodo_arrastrado = self._nodo_en(event.xdata, event.ydata)

    def _on_motion(self, event):
        if event.inaxes != self.ax or event.xdata is None or event.ydata is None:
            return

        if self.pan_activo and self.pan_origen is not None:
            dx = event.xdata - self.pan_origen[0]
            dy = event.ydata - self.pan_origen[1]
            x0, x1 = self.xlim
            y0, y1 = self.ylim
            self.xlim = (x0 - dx, x1 - dx)
            self.ylim = (y0 - dy, y1 - dy)
            self._dibujar()
            return

        if self.nodo_arrastrado is not None:
            # nodo.x / nodo.y ya están en unidades de dato reales (no hay
            # que dividir entre ninguna escala, a diferencia de antes)
            self.nodo_arrastrado.x = event.xdata
            self.nodo_arrastrado.y = event.ydata
            self._dibujar()

    def _on_release(self, event):
        self.nodo_arrastrado = None
        self.pan_activo = False
        self.pan_origen = None


# ---------------------------------------------------------------------------
# Analizador de expresiones simples: convierte una cadena en el dict/JSON
# que espera arbol_desde_dict (asignación, +, -, *, /, paréntesis, ids, números)
# ---------------------------------------------------------------------------

class ErrorSintactico(Exception):
    pass


_ESPECIFICACION_TOKENS = [
    ("NUMBER", r"\d+(\.\d+)?"),
    ("ID", r"[A-Za-z_][A-Za-z0-9_]*"),
    ("ASSIGN", r"="),
    ("PLUS", r"\+"),
    ("MINUS", r"-"),
    ("MUL", r"\*"),
    ("DIV", r"/"),
    ("LPAREN", r"\("),
    ("RPAREN", r"\)"),
    ("SKIP", r"[ \t]+"),
    ("MISMATCH", r"."),
]
_REGEX_TOKENS = "|".join(f"(?P<{nombre}>{patron})" for nombre, patron in _ESPECIFICACION_TOKENS)


class AnalizadorExpresiones:
    """Recursive-descent simple para: [ID '='] expresión
    expresión := término (('+'|'-') término)*
    término   := factor (('*'|'/') factor)*
    factor    := NUMBER | ID | '(' expresión ')'
    """

    def __init__(self, cadena):
        self.tokens = self._tokenizar(cadena)
        self.pos = 0

    def _tokenizar(self, cadena):
        tokens = []
        for m in re.finditer(_REGEX_TOKENS, cadena):
            tipo = m.lastgroup
            valor = m.group()
            if tipo == "SKIP":
                continue
            if tipo == "MISMATCH":
                raise ErrorSintactico(f"Carácter inesperado: {valor!r}")
            tokens.append((tipo, valor))
        tokens.append(("EOF", ""))
        return tokens

    def _actual(self):
        return self.tokens[self.pos]

    def _avanzar(self):
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def _esperar(self, tipo):
        tok = self._actual()
        if tok[0] != tipo:
            raise ErrorSintactico(
                f"Se esperaba '{tipo}' pero se encontró '{tok[1] or 'fin de la cadena'}'"
            )
        return self._avanzar()

    def analizar(self):
        nodo = self._asignacion_o_expresion()
        self._esperar("EOF")
        return nodo

    def _asignacion_o_expresion(self):
        if self._actual()[0] == "ID" and self.tokens[self.pos + 1][0] == "ASSIGN":
            nombre = self._avanzar()
            self._esperar("ASSIGN")
            expr = self._expresion()
            return {
                "top": "ASIGNACION",
                "hijos": [
                    {"top": f"id: {nombre[1]}", "right": "tipo: var"},
                    expr,
                ],
            }
        return self._expresion()

    def _expresion(self):
        nodo = self._termino()
        while self._actual()[0] in ("PLUS", "MINUS"):
            op = self._avanzar()
            derecho = self._termino()
            nombre = "SUMA" if op[0] == "PLUS" else "RESTA"
            nodo = {"top": nombre, "hijos": [nodo, derecho]}
        return nodo

    def _termino(self):
        nodo = self._factor()
        while self._actual()[0] in ("MUL", "DIV"):
            op = self._avanzar()
            derecho = self._factor()
            nombre = "MULT" if op[0] == "MUL" else "DIV"
            nodo = {"top": nombre, "hijos": [nodo, derecho]}
        return nodo

    def _factor(self):
        tok = self._actual()
        if tok[0] == "NUMBER":
            self._avanzar()
            return {"top": f"num: {tok[1]}", "right": "tipo: num"}
        if tok[0] == "ID":
            self._avanzar()
            return {"top": f"id: {tok[1]}", "right": "tipo: var"}
        if tok[0] == "LPAREN":
            self._avanzar()
            nodo = self._expresion()
            self._esperar("RPAREN")
            return nodo
        raise ErrorSintactico(f"Token inesperado: '{tok[1] or 'fin de la cadena'}'")


def _agregar_linea(nodo_dict, linea):
    """Rellena el campo 'left' con el número de línea en todo el árbol."""
    nodo_dict.setdefault("left", f"línea {linea}")
    for hijo in nodo_dict.get("hijos", []):
        _agregar_linea(hijo, linea)


def arbol_desde_cadena(cadena, linea=1):
    """Convierte una cadena tipo 'x = a + b * c' directamente en un NodoArbol."""
    analizador = AnalizadorExpresiones(cadena)
    datos = analizador.analizar()
    _agregar_linea(datos, linea)
    return arbol_desde_dict(datos)


# ---------------------------------------------------------------------------
# Árbol semántico de ejemplo: x = a + b * c
# ---------------------------------------------------------------------------

def construir_arbol_ejemplo():
    id_a = NodoArbol("id: a", "línea 1", "tipo: int")
    id_b = NodoArbol("id: b", "línea 1", "tipo: int")
    id_c = NodoArbol("id: c", "línea 1", "tipo: int")

    mult = NodoArbol("MULT", "línea 1", "tipo: int", hijos=[id_b, id_c])
    suma = NodoArbol("SUMA", "línea 1", "tipo: int", hijos=[id_a, mult])
    id_x = NodoArbol("id: x", "línea 1", "tipo: int")

    raiz = NodoArbol("ASIGNACION", "línea 1", "tipo: int", hijos=[id_x, suma])
    return raiz


# ---------------------------------------------------------------------------
# App principal
# ---------------------------------------------------------------------------

class App(ctk.CTk):
    def __init__(self, raiz=None, ruta_json=None):
        super().__init__()
        self.title("Árbol semántico — Solaris")
        self.geometry("950x700")

        ctk.set_appearance_mode("dark")

        titulo = ctk.CTkLabel(
            self, text="Árbol semántico",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        titulo.pack(pady=(10, 0))

        # -- barra para escribir una expresión y generar el árbol -----
        barra = ctk.CTkFrame(self, fg_color="transparent")
        barra.pack(fill="x", padx=10, pady=(8, 0))

        self.entrada = ctk.CTkEntry(
            barra, placeholder_text="ej. x = a + b * c",
        )
        self.entrada.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.entrada.bind("<Return>", lambda e: self._generar_desde_entrada())

        boton = ctk.CTkButton(
            barra, text="Generar árbol", width=130,
            command=self._generar_desde_entrada,
        )
        boton.pack(side="left")

        self.error_label = ctk.CTkLabel(
            self, text="", text_color="#ff6b6b", font=ctk.CTkFont(size=12),
        )
        self.error_label.pack(fill="x", padx=12, pady=(4, 0))

        # Prioridad: árbol pasado por código > archivo JSON > ejemplo fijo
        if raiz is None and ruta_json:
            raiz = cargar_arbol_json(ruta_json)
        if raiz is None:
            raiz = construir_arbol_ejemplo()

        self.visor = VisorArbolSemantico(self, raiz)
        self.visor.pack(fill="both", expand=True, padx=10, pady=10)

    def _generar_desde_entrada(self):
        cadena = self.entrada.get().strip()
        if not cadena:
            return
        try:
            nueva_raiz = arbol_desde_cadena(cadena)
        except ErrorSintactico as e:
            self.error_label.configure(text=f"Error de sintaxis: {e}")
            return
        self.error_label.configure(text="")
        self.visor.cargar_arbol(nueva_raiz)


if __name__ == "__main__":
    # Uso:
    #   python arbol_semantico_ctk.py                -> muestra el ejemplo fijo
    #   python arbol_semantico_ctk.py mi_arbol.json   -> carga el árbol desde JSON
    ruta = sys.argv[1] if len(sys.argv) > 1 else None
    app = App(ruta_json=ruta)
    app.mainloop()