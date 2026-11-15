import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import io, os, tempfile, contextlib
from logLexSinta import SinLex, Sinta, Semantico, Intermedio
import io, os, tempfile, contextlib, json 
from arbol_semantico import VisorArbolSemantico, arbol_desde_dict
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")



COLORES_MANUALES = {
    "editorFondo":     ("#FAFAFA", "#1B1B1F"),
    "editorTexto":     ("#1A202C", "#E6E6E6"),
    "editorCursor":    ("#1A56DB", "#5B8DEF"),
    "editorSeleccion": ("#CBD7F5", "#2D3F66"),
    "lienzoFondo":     ("#ECEEF2", "#202024"),
    "numeroTexto":     ("#9AA3AF", "#6B7280"),
    "tablaFondo":      ("#FFFFFF", "#242428"),
    "tablaTexto":      ("#1A202C", "#E6E6E6"),
    "tablaEncabezado": ("#EDF0F4", "#2A2A30"),
    "tablaSeleccion":  ("#3B6FE0", "#2D3F66"),
    "filaPar":         ("#F5F7FA", "#242428"),
    "filaImpar":       ("#FFFFFF", "#1E1E22"),
    "manija":          ("#C2CAD6", "#3A3A40"),
}

GRAMATICA_OPERACION = [
    ("prinFin → Begin codigo End | Begin codigo End comentario",
     "<prinFin.valor> → Begin <codigo.valor> End | Begin <codigo.valor> End <comentario.valor>",
     False),
    ("codigo → decVar codigo | datoValor codigo | pedValor codigo | operacion codigo | salida codigo | decVar | datoValor | pedValor | operacion | salida",
     "<codigo1.valor> → <decVar.valor> <codigo2.valor> | <datoValor.valor> <codigo3.valor> | <pedValor.valor> <codigo4.valor> | <operacion.valor> <codigo5.valor> | <salida.valor> <codigo6.valor> | <decVar.valor> | <datoValor.valor> | <pedValor.valor> | <operacion.valor> | <salida.valor>",
     False),
    ("decVar → tipoDato nomVar ; | tipoDato nomVar , nomVar ; | tipoDato nomVar ; decVar | tipoDato nomVar , nomVar ; decVar",
     "<decVar1.valor> → <tipoDato.valor> <nomVar.valor> <;.valor> | <tipoDato.valor> <nomVar.valor> <,.valor> <nomVar.valor> <;.valor> | <tipoDato.valor> <nomVar.valor> <;.valor> <decVar2.valor> | <tipoDato.valor> <nomVar1.valor> <,.valor> <nomVar.valor> <;.valor> <decVar3.valor>",
     False),
    ("tipoDato → Ent | Dec | Ban | Sim | Sen",
     "<tipoDato.valor> → <Ent.valor> | <Dec.valor> | <Ban.valor> | <Sim.valor> | <Sen.valor>",
     False),
    ("datoValor → nomVar = numero ; | nomVar = cadena ; | nomVar = True ; | nomVar = False ; | nomVar = concat ; (cada una con su version encadenada + datoValor)",
     "<datoValor.valor> → <nomVar.valor> <=.valor> <numero.valor> <;.valor> | <nomVar.valor> <=.valor> <cadena.valor> <;.valor> | <nomVar.valor> <=.valor> <True.valor> <;.valor> | <nomVar.valor> <=.valor> <False.valor> <;.valor> | <nomVar.valor> <=.valor> <concat.valor> <;.valor>",
     False),
    ("cadena → \" \"",
     "<cadena.valor> → <\".valor> <\".valor>",
     False),
    ("pedValor → Entrada nomVar = cadena ; | Entrada nomVar = cadena ; pedValor",
     "<pedValor1.valor> → <Entrada.valor> <nomVar.valor> <=.valor> <cadena.valor> <;.valor> | <Entrada.valor> <nomVar.valor> <=.valor> <cadena.valor> <;.valor> <pedValor2.valor>",
     False),
    ("operacion → nomVar = expr ; | nomVar = expr ; operacion",
     "<operacion1.valor> → <nomVar.valor> <=.valor> <expr.valor> <;.valor> | <nomVar.valor> <=.valor> <expr.valor> <;.valor> <operacion2.valor>",
     True),
    ("expr → termino | termino opSuma expr",
     "<expr1.valor> → <termino.valor> | <termino.valor> <opSuma.valor> <expr2.valor>",
     True),
    ("termino → operando | operando opMul termino",
     "<termino1.valor> → <operando.valor> | <operando.valor> <opMul.valor> <termino2.valor>",
     True),
    ("operando → nomVar | numero",
     "<operando.valor> → <nomVar.valor> | <numero.valor>",
     True),
    ("opSuma → + | -",
     "<opSuma.valor> → <+.valor> | <-.valor>",
     True),
    ("opMul → * | /",
     "<opMul.valor> → <*.valor> | </.valor>",
     True),
    ("nomVar → (a-z)+",
     "<nomVar.valor> → <(a-z)+.valor>",
     True),
    ("numero → (0-9)+ | (0-9)+ . (0-9)+",
     "<numero.valor> → <(0-9)+.valor> | <(0-9)+1.valor> <..valor> <(0-9)+2.valor>",
     True),
    ("salida → Salida = cadena ; | Salida = cadena , nomVar ; | Salida = concat ; (cada una con su version encadenada + salida)",
     "<salida1.valor> → <Salida2.valor> <=.valor> <cadena.valor> <;.valor> | <Salida3.valor> <=.valor> <cadena.valor> <,.valor> <nomVar.valor> <;.valor> | <Salida4.valor> <=.valor> <concat.valor> <;.valor>",
     False),
    ("concat → cadena + masCat | nomVar + cadena | nomVar + cadena + masCat",
     "<concat.valor> → <cadena.valor> <+.valor> <masCat.valor> | <nomVar.valor> <+.valor> <cadena.valor> | <nomVar.valor> <+1.valor> <cadena.valor> <+2.valor> <masCat.valor>",
     False),
    ("masCat → elemCad | elemCad + masCat",
     "<masCat1.valor> → <elemCad.valor> | <elemCad.valor> <+.valor> <masCat2.valor>",
     False),
    ("elemCad → cadena | nomVar",
     "<elemCad.valor> → <cadena.valor> | <nomVar.valor>",
     False),
    ("comentario → && | && comentario",
     "<comentario1.valor> → <&&.valor> | <&&.valor> <comentario2.valor>",
     False),
]
#Funetes para los widwgets
FUENTE_EDITOR     = ("Courier New", 13)
FUENTE_NUMEROS    = ("Courier New", 11)
FUENTE_TABLA      = ("Courier New", 11)
FUENTE_TABLA_ENC  = ("Courier New", 12, "bold")


def colorTema(clave):
    indice = 0 if ctk.get_appearance_mode() == "Light" else 1
    return COLORES_MANUALES[clave][indice]


class CompiladorInterfaz(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.title("Compilador Solaris")
        self.geometry("1320x780")
        self.minsize(960, 620)
        

       
        self.fuenteTitulo   = ctk.CTkFont(size=20, weight="bold")
        self.fuenteSubtitulo = ctk.CTkFont(size=12)
        self.fuenteEtiqueta = ctk.CTkFont(size=13, weight="bold")
        self.fuenteBoton    = ctk.CTkFont(size=13)
        self.fuenteMono     = ctk.CTkFont(family="Courier New", size=13)
        self.fuenteMonoChica = ctk.CTkFont(family="Courier New", size=11)

       
        self.colorBotonDefecto = ctk.ThemeManager.theme["CTkButton"]["fg_color"]
        self.colorHoverDefecto = ctk.ThemeManager.theme["CTkButton"]["hover_color"]

        # de la aplicacion
        self.analizadorLexico = None
        self.recorridoSintactico = ""     # texto completo del recorrido sintactico
        self.alturaErrores = 170
        self.alturaMinErrores = 90
        self.alturaMaxErrores = 600

        self.construirCabecera()
        self.construirContenedor()
        self.mostrarPaginaPrincipal()
        self.arbolesSemanticos = []
        self.indiceArbolActual = 0
        self.intermedioActual = None

       
        self.after(120, self.dibujarNumerosLinea)

    # Cabecera

    def construirCabecera(self):
        cabecera = ctk.CTkFrame(self, height=66, corner_radius=0)
        cabecera.pack(fill="x")
        cabecera.pack_propagate(False)

        contenido = ctk.CTkFrame(cabecera, fg_color="transparent")
        contenido.pack(fill="both", expand=True, padx=18, pady=10)

        ctk.CTkLabel(contenido, text="⬢  COMPILADOR SOLARIS",
                     font=self.fuenteTitulo).pack(side="left")
        ctk.CTkLabel(contenido, text="v1.0  ·  Analizador léxico y sintáctico",
                     font=self.fuenteSubtitulo,
                     text_color=("gray35", "gray60")).pack(side="left", padx=14)

        self.etiquetaEstado = ctk.CTkLabel(contenido, text="●  listo",
                                           font=self.fuenteEtiqueta,
                                           text_color="#0E9F6E")
        self.etiquetaEstado.pack(side="right", padx=(12, 4))

        self.interruptorTema = ctk.CTkSwitch(contenido, text="Modo oscuro",
                                             command=self.cambiarTema)
        self.interruptorTema.pack(side="right", padx=12)

    def establecerEstado(self, texto, color=None):
        self.etiquetaEstado.configure(text=f"●  {texto}",
                                      text_color=color or "#0E9F6E")

    # Contender y paginas apliadas

    def construirContenedor(self):
        self.contenedorPrincipal = ctk.CTkFrame(self, fg_color="transparent")
        self.contenedorPrincipal.pack(fill="both", expand=True)
        self.contenedorPrincipal.rowconfigure(0, weight=1)
        self.contenedorPrincipal.columnconfigure(0, weight=1)

      
        self.paginaPrincipal = ctk.CTkFrame(self.contenedorPrincipal,
                                            fg_color="transparent")
        self.paginaTablas = ctk.CTkFrame(self.contenedorPrincipal,
                                         fg_color="transparent")
        self.paginaPrincipal.grid(row=0, column=0, sticky="nsew")
        self.paginaTablas.grid(row=0, column=0, sticky="nsew")

        self.construirPaginaPrincipal()
        self.construirPaginaResultados()

    def mostrarPaginaPrincipal(self):
        self.paginaPrincipal.tkraise()
        self.establecerEstado("editor", "#1A56DB")

    def mostrarPaginaResultados(self):
        if self.analizadorLexico is None:
            messagebox.showinfo(
                "Sin análisis",
                "Ejecuta primero el análisis Léxico para generar las tablas.")
            return
        self.poblarTablas()
        self.mostrarVistaLexico()          # vista por defecto al entrar
        self.paginaTablas.tkraise()
        self.establecerEstado("resultados", "#0E9F6E")

 

    def construirPaginaPrincipal(self):
        pagina = self.paginaPrincipal
        pagina.columnconfigure(0, weight=3)   # editor
        pagina.columnconfigure(1, weight=2)   # analisis
        pagina.rowconfigure(0, weight=1)       # contenido (crece)
        pagina.rowconfigure(1, weight=0)       # manija de arrastre
        pagina.rowconfigure(2, weight=0)       # panel de errores

        self.construirPanelEditor(pagina)
        self.construirPanelAnalisis(pagina)
        self.construirManijaRedimension(pagina)
        self.construirPanelErrores(pagina)

    # panel del editor 
    def construirPanelEditor(self, contenedorPadre):
        marcoEditor = ctk.CTkFrame(contenedorPadre, corner_radius=10)
        marcoEditor.grid(row=0, column=0, sticky="nsew",
                         padx=(12, 6), pady=(12, 6))
        marcoEditor.rowconfigure(1, weight=1)
        marcoEditor.columnconfigure(0, weight=1)

        ctk.CTkLabel(marcoEditor, text="Editor de código",
                     font=self.fuenteEtiqueta, anchor="w").grid(
                         row=0, column=0, sticky="ew", padx=14, pady=(12, 6))

        # zona del editor: numeracion + texto + barras
        zonaEditor = ctk.CTkFrame(marcoEditor, fg_color="transparent")
        zonaEditor.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 6))
        zonaEditor.rowconfigure(0, weight=1)
        zonaEditor.columnconfigure(1, weight=1)

        self.lienzoNumeros = tk.Canvas(zonaEditor, width=44, highlightthickness=0,
                                       bd=0, bg=colorTema("lienzoFondo"))
        self.lienzoNumeros.grid(row=0, column=0, sticky="ns")

        self.editorCodigo = tk.Text(
            zonaEditor, wrap="none", relief="flat", bd=0, padx=8, pady=6,
            font=FUENTE_EDITOR,
            bg=colorTema("editorFondo"), fg=colorTema("editorTexto"),
            insertbackground=colorTema("editorCursor"),
            selectbackground=colorTema("editorSeleccion"))
        self.editorCodigo.grid(row=0, column=1, sticky="nsew")

        self.barraVerticalEditor = ctk.CTkScrollbar(
            zonaEditor, command=self.desplazarEditor)
        self.barraVerticalEditor.grid(row=0, column=2, sticky="ns")
        barraHorizontal = ctk.CTkScrollbar(
            zonaEditor, orientation="horizontal", command=self.editorCodigo.xview)
        barraHorizontal.grid(row=1, column=1, sticky="ew")

        self.editorCodigo.configure(yscrollcommand=self.alDesplazarEditor,
                                    xscrollcommand=barraHorizontal.set)
        self.editorCodigo.bind("<KeyRelease>", self.dibujarNumerosLinea)
        self.editorCodigo.bind("<Configure>", self.dibujarNumerosLinea)

        ctk.CTkButton(marcoEditor, text="Cargar archivo", width=150,
                      font=self.fuenteBoton, command=self.cargarArchivo).grid(
                          row=2, column=0, sticky="w", padx=14, pady=(4, 12))

    def alDesplazarEditor(self, primero, ultimo):
        """yscrollcommand del editor: mueve la barra y repinta los numeros."""
        self.barraVerticalEditor.set(primero, ultimo)
        self.dibujarNumerosLinea()

    def desplazarEditor(self, *argumentos):
        """command de la barra: desplaza el texto y repinta los numeros."""
        self.editorCodigo.yview(*argumentos)
        self.dibujarNumerosLinea()

    def dibujarNumerosLinea(self, evento=None):
        self.lienzoNumeros.delete("all")
        indice = self.editorCodigo.index("@0,0")
        while True:
            informacionLinea = self.editorCodigo.dlineinfo(indice)
            if informacionLinea is None:
                break
            posicionY = informacionLinea[1]
            numero = int(str(indice).split(".")[0])
            self.lienzoNumeros.create_text(
                36, posicionY, anchor="ne", text=str(numero),
                font=FUENTE_NUMEROS, fill=colorTema("numeroTexto"))
            indice = self.editorCodigo.index(f"{indice}+1line")
            if self.editorCodigo.compare(indice, ">=", "end"):
                break

    # panel de analisis 
    def construirPanelAnalisis(self, contenedorPadre):
        marcoAnalisis = ctk.CTkFrame(contenedorPadre, corner_radius=10)
        marcoAnalisis.grid(row=0, column=1, sticky="nsew",
                           padx=(6, 12), pady=(12, 6))
        marcoAnalisis.columnconfigure(0, weight=1)
        marcoAnalisis.columnconfigure(1, weight=1)

        ctk.CTkLabel(marcoAnalisis, text="Análisis", font=self.fuenteEtiqueta,
                     anchor="w").grid(row=0, column=0, columnspan=2,
                                      sticky="ew", padx=14, pady=(12, 8))

        # Cada tupla: (texto, activo, accion)
        self.botonesFases = {} 
        fases = [
            ("Léxico",            True,  self.analizarLexico),
            ("Sintáctico",        False, self.analizarSintactico),
            ("Semántico",         False, self.analizarSemantico),
            ("Código intermedio", False, None),
            ("Optimización",      False, None),
            ("Código objeto",     False, None),
        ]
        fila = 1
        for nombre, activo, accion in fases:
            boton = ctk.CTkButton(
                marcoAnalisis, text=nombre, height=34, font=self.fuenteBoton,
                state="normal" if activo else "disabled",
                command=accion if accion else (lambda: None))
            boton.grid(row=fila, column=0, columnspan=2,
                       sticky="ew", padx=14, pady=4)
            self.botonesFases[nombre] = boton  
            fila += 1

        separador = ctk.CTkFrame(marcoAnalisis, height=2,
                                 fg_color=("#D0D5DD", "#3A3A40"))
        separador.grid(row=fila, column=0, columnspan=2,
                       sticky="ew", padx=14, pady=8)
        fila += 1

        self.botonTablas = ctk.CTkButton(
            marcoAnalisis, text="Mostrar tablas", height=34,
            font=self.fuenteBoton, fg_color="#0E9F6E", hover_color="#0B7E58",
            command=self.mostrarPaginaResultados)
        self.botonTablas.grid(row=fila, column=0, sticky="ew",
                              padx=(14, 6), pady=4)
        botonLimpiar = ctk.CTkButton(
            marcoAnalisis, text="Limpiar", height=34, font=self.fuenteBoton,
            fg_color="#C53030", hover_color="#9B2C2C", command=self.limpiar)
        botonLimpiar.grid(row=fila, column=1, sticky="ew", padx=(6, 14), pady=4)
        fila += 1

        

        ctk.CTkLabel(marcoAnalisis, text="Información del compilador",
                     font=self.fuenteSubtitulo, anchor="w",
                     text_color=("gray40", "gray60")).grid(
                         row=fila, column=0, columnspan=2, sticky="ew",
                         padx=14, pady=(10, 4))
        fila += 1

        self.textoInformacion = ctk.CTkTextbox(
            marcoAnalisis, font=self.fuenteMonoChica, wrap="word",
            activate_scrollbars=True)
        self.textoInformacion.grid(row=fila, column=0, columnspan=2,
                                   sticky="nsew", padx=12, pady=(0, 12))
        marcoAnalisis.rowconfigure(fila, weight=1)
        self.poblarInformacion()

    # manija de arrastre 
    def construirManijaRedimension(self, contenedorPadre):
        self.manijaErrores = ctk.CTkFrame(
            contenedorPadre, height=12, corner_radius=6,
            fg_color=colorTema("manija"))
        self.manijaErrores.grid(row=1, column=0, columnspan=2,
                                sticky="ew", padx=12, pady=2)
        self.manijaErrores.grid_propagate(False)

        self.indicadorManija = ctk.CTkLabel(
            self.manijaErrores, text="⠿⠿⠿", height=10,
            text_color=("gray35", "gray65"))
        self.indicadorManija.place(relx=0.5, rely=0.5, anchor="center")

        # El arrastre funciona tanto sobre la barra como sobre su indicador
        for objetivo in (self.manijaErrores, self.indicadorManija):
            objetivo.configure(cursor="sb_v_double_arrow")
            objetivo.bind("<Button-1>", self.iniciarRedimension)
            objetivo.bind("<B1-Motion>", self.redimensionarErrores)

    def iniciarRedimension(self, evento):
        self.yArrastreInicial = evento.y_root
        self.alturaArrastreInicial = self.alturaErrores
        # se limita el maximo para no tapar por completo el editor
        altoPagina = self.paginaPrincipal.winfo_height()
        self.alturaMaxErrores = max(self.alturaMinErrores, altoPagina - 240)

    def redimensionarErrores(self, evento):
        # arrastrar hacia arriba -> el panel crece
        desplazamiento = self.yArrastreInicial - evento.y_root
        nuevaAltura = self.alturaArrastreInicial + desplazamiento
        nuevaAltura = max(self.alturaMinErrores,
                          min(nuevaAltura, self.alturaMaxErrores))
        self.alturaErrores = nuevaAltura
        self.marcoErrores.configure(height=nuevaAltura)

    # panel de errores  (SOLO errores)
    def construirPanelErrores(self, contenedorPadre):
        self.marcoErrores = ctk.CTkFrame(contenedorPadre, corner_radius=10,
                                         height=self.alturaErrores)
        self.marcoErrores.grid(row=2, column=0, columnspan=2,
                               sticky="nsew", padx=12, pady=(0, 12))
        self.marcoErrores.grid_propagate(False)   # respeta la altura fijada
        self.marcoErrores.rowconfigure(1, weight=1)
        self.marcoErrores.columnconfigure(0, weight=1)

        encabezado = ctk.CTkFrame(self.marcoErrores, fg_color="transparent")
        encabezado.grid(row=0, column=0, sticky="ew", padx=12, pady=(10, 4))
        encabezado.columnconfigure(0, weight=1)
        ctk.CTkLabel(encabezado, text="Errores",
                     font=self.fuenteEtiqueta, anchor="w",
                     text_color=("#C53030", "#F87171")).grid(
                         row=0, column=0, sticky="w")
        ctk.CTkLabel(encabezado,
                     text="↕  arrastra la barra superior para expandir",
                     font=self.fuenteSubtitulo,
                     text_color=("gray45", "gray55")).grid(
                         row=0, column=1, sticky="e")

        self.textoErrores = ctk.CTkTextbox(
            self.marcoErrores, font=self.fuenteMonoChica, wrap="none",
            activate_scrollbars=True, state="disabled")
        self.textoErrores.grid(row=1, column=0, sticky="nsew",
                               padx=12, pady=(0, 12))


    def construirPaginaResultados(self):
        pagina = self.paginaTablas
        pagina.columnconfigure(0, weight=1)
        pagina.rowconfigure(2, weight=1)        # area de contenido crece

        # fila 0: barra superior (volver + titulo)
        barra = ctk.CTkFrame(pagina, fg_color="transparent")
        barra.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 6))
        ctk.CTkButton(barra, text="←  Volver al editor", width=180,
                      font=self.fuenteBoton,
                      command=self.mostrarPaginaPrincipal).pack(side="left")
        ctk.CTkLabel(barra, text="Resultados del compilador",
                     font=self.fuenteSubtitulo,
                     text_color=("gray40", "gray60")).pack(side="left", padx=14)

        # fila 1: selector de vistas
        self.construirSelectorVistas(pagina)

        # fila 2: area que contiene las vistas apiladas
        self.areaVistas = ctk.CTkFrame(pagina, fg_color="transparent")
        self.areaVistas.grid(row=2, column=0, sticky="nsew")
        self.areaVistas.rowconfigure(0, weight=1)
        self.areaVistas.columnconfigure(0, weight=1)

        self.vistaLexico = ctk.CTkFrame(self.areaVistas, fg_color="transparent")
        self.vistaSintactico = ctk.CTkFrame(self.areaVistas, fg_color="transparent")
        self.vistaLexico.grid(row=0, column=0, sticky="nsew")
        self.vistaSintactico.grid(row=0, column=0, sticky="nsew")

        self.vistaSemantico = ctk.CTkFrame(self.areaVistas, fg_color="transparent")
        self.vistaSemantico.grid(row=0, column=0, sticky="nsew")

        self.vistaRecorridoTabla = ctk.CTkFrame(self.areaVistas, fg_color="transparent")
        self.vistaRecorridoTabla.grid(row=0, column=0, sticky="nsew")

        self.vistaIntermedio = ctk.CTkFrame(self.areaVistas, fg_color="transparent")
        self.vistaIntermedio.grid(row=0, column=0, sticky="nsew")

        

        self.construirVistaLexico(self.vistaLexico)
        self.construirVistaSintactico(self.vistaSintactico)
        self.construirVistaSemantico(self.vistaSemantico)
        self.construirVistaRecorridoTabla(self.vistaRecorridoTabla)
        self.construirVistaIntermedio(self.vistaIntermedio)



    def construirSelectorVistas(self, contenedorPadre):
        selector = ctk.CTkFrame(contenedorPadre, fg_color="transparent")
        selector.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 8))

        self.botonesVista = {}
        # (texto, activo, accion)
        vistas = [
            ("Tabla léxico",         True,  self.mostrarVistaLexico),
            ("Recorrido sintáctico", True,  self.mostrarVistaSintactico),
            ("Semántico",            True,  self.mostrarVistaSemantico),
            ("Recorrido Semantico",    True, self.mostrarVistaRecorridoTabla),
            ("Código intermedio",    True,  self.mostrarVistaIntermedio),
            ("Optimización",         False, None),
            ("Código objeto",        False, None),
        ]
        for nombre, activo, accion in vistas:
            boton = ctk.CTkButton(
                selector, text=nombre, height=32, font=self.fuenteBoton,
                state="normal" if activo else "disabled",
                command=accion if accion else (lambda: None))
            boton.pack(side="left", padx=(0, 8))
            self.botonesVista[nombre] = boton

    def resaltarBotonVista(self, nombreActivo):
        """Pinta de verde el boton de la vista activa; el resto, color normal."""
        for nombre, boton in self.botonesVista.items():
            if boton.cget("state") == "disabled":
                continue
            if nombre == nombreActivo:
                boton.configure(fg_color="#0E9F6E", hover_color="#0B7E58")
            else:
                boton.configure(fg_color=self.colorBotonDefecto,
                                hover_color=self.colorHoverDefecto)

    def mostrarVistaLexico(self):
        self.vistaLexico.tkraise()
        self.resaltarBotonVista("Tabla léxico")

    def mostrarVistaSintactico(self):
        self.actualizarRecorridoSintactico()
        self.vistaSintactico.tkraise()
        self.resaltarBotonVista("Recorrido sintáctico")

    def mostrarVistaSemantico(self):
        self.vistaSemantico.tkraise()
        self.resaltarBotonVista("Semántico")
        self.update_idletasks()
        self.actualizarArbolMostrado()

    def mostrarVistaRecorridoTabla(self):         
        self.vistaRecorridoTabla.tkraise()   
        self.resaltarBotonVista("Recorrido semantico")  


    def mostrarVistaIntermedio(self):
        self.vistaIntermedio.tkraise()
        self.resaltarBotonVista("Código intermedio")
 
    # Codigo intermedio: la vista se divide en 4 paneles
    def construirVistaIntermedio(self, contenedor):
        contenedor.rowconfigure(0, weight=1)
        contenedor.columnconfigure(0, weight=5)   # notacion polaca
        contenedor.columnconfigure(1, weight=2)   # p-code
        contenedor.columnconfigure(2, weight=4)   # triplos
        contenedor.columnconfigure(3, weight=5)   # cuadruplos
 
        self.tablaPolaca = self.construirPanelIntermedio(
            contenedor, 0, "Notación polaca",
            ("Pila1", "Pila2", "Cadena"), [130, 90, 260])
        self.tablaPCode = self.construirPanelIntermedio(
            contenedor, 1, "P-Code",
            ("P-Code",), [90])
        self.tablaTriplos = self.construirPanelIntermedio(
            contenedor, 2, "Tríplos",
            ("Dirección", "Operador", "Operando1", "Operando2"), [70, 70, 80, 80])
        self.tablaCuadruplos = self.construirPanelIntermedio(
            contenedor, 3, "Cuádruplos",
            ("Operador", "Operando1", "Operando2", "Auxiliar"), [70, 80, 80, 80])
 
    def construirPanelIntermedio(self, contenedorPadre, columnaGrid, titulo, columnas, anchos):
        # cada panel es un marco con su titulo y su tabla (mismo estilo q la tabla de tokens)
        if columnaGrid == 0:
            padX = (12, 6)
        elif columnaGrid == 3:
            padX = (6, 12)
        else:
            padX = (6, 6)
        marco = ctk.CTkFrame(contenedorPadre, corner_radius=10)
        marco.grid(row=0, column=columnaGrid, sticky="nsew", padx=padX, pady=(0, 12))
        marco.rowconfigure(1, weight=1)
        marco.columnconfigure(0, weight=1)
 
        ctk.CTkLabel(marco, text=titulo, font=self.fuenteEtiqueta,
                     anchor="w").grid(row=0, column=0, sticky="ew",
                                      padx=14, pady=(12, 6))
 
        marcoTabla = ctk.CTkFrame(marco, fg_color="transparent")
        marcoTabla.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        marcoTabla.rowconfigure(0, weight=1)
        marcoTabla.columnconfigure(0, weight=1)
 
        tabla = ttk.Treeview(marcoTabla, columns=columnas,
                             show="headings", style="Solaris.Treeview")
        for columna, ancho in zip(columnas, anchos):
            tabla.heading(columna, text=columna)
            tabla.column(columna, width=ancho, anchor="w", stretch=True)
 
        barraVertical = ctk.CTkScrollbar(marcoTabla, command=tabla.yview)
        tabla.configure(yscrollcommand=barraVertical.set)
        tabla.grid(row=0, column=0, sticky="nsew")
        barraVertical.grid(row=0, column=1, sticky="ns")
        return tabla
 
    def llenaTablaIntermedia(self, tabla, listas):
        # listas = una lista por columna, todas del mismo largo
        tabla.delete(*tabla.get_children())
        tabla.tag_configure("par", background=colorTema("filaPar"))
        tabla.tag_configure("impar", background=colorTema("filaImpar"))
        for indice in range(len(listas[0])):
            valores = []
            for lista in listas:
                valores.append(lista[indice])
            etiqueta = "par" if indice % 2 == 0 else "impar"
            tabla.insert("", "end", tags=(etiqueta,), values=tuple(valores))
 
    def poblarIntermedio(self):
        inter = self.intermedioActual
        self.llenaTablaIntermedia(self.tablaPolaca,
                                  [inter.polPila1, inter.polPila2, inter.polCad])
        self.llenaTablaIntermedia(self.tablaPCode, [inter.codP])
        self.llenaTablaIntermedia(self.tablaTriplos,
                                  [inter.lidir, inter.ope, inter.op1, inter.op2])
        self.llenaTablaIntermedia(self.tablaCuadruplos,
                                  [inter.cuOpe, inter.cuOp1, inter.cuOp2, inter.cuAux])
 
    def analizarIntermedio(self):
        try:
            intermedio = Intermedio(self.analizadorLexico)
            intermedio.generaCodigo()
        except Exception as error:
            messagebox.showerror(
                "Error en código intermedio",
                f"El generador de código intermedio lanzó un error:\n{error}")
            self.establecerEstado("error intermedio", "#C81E1E")
            return
 
        if len(intermedio.opers) == 0:
            messagebox.showinfo(
                "Sin operaciones",
                "No hay expresiones aritméticas para generar código intermedio.")
            return
 
        self.intermedioActual = intermedio
        self.poblarTablas()
        self.poblarIntermedio()
        self.paginaTablas.tkraise()
        self.mostrarVistaIntermedio()
        self.establecerEstado("Intermedio ok", "#0E9F6E")
 
 





    def construirVistaLexico(self, contenedor):
        contenedor.columnconfigure(0, weight=3)
        contenedor.columnconfigure(1, weight=1)
        contenedor.rowconfigure(0, weight=1)
        self.construirTablaTokens(contenedor)
        self.construirTablaSimbolos(contenedor)

    def aplicarEstiloTabla(self):
        """Configura el estilo del Treeview segun el tema activo."""
        estilo = ttk.Style()
        estilo.theme_use("default")
        estilo.configure("Solaris.Treeview",
                         background=colorTema("tablaFondo"),
                         foreground=colorTema("tablaTexto"),
                         fieldbackground=colorTema("tablaFondo"),
                         font=FUENTE_TABLA, rowheight=24, borderwidth=0)
        estilo.configure("Solaris.Treeview.Heading",
                         background=colorTema("tablaEncabezado"),
                         foreground=colorTema("tablaTexto"),
                         font=FUENTE_TABLA_ENC, relief="flat")
        estilo.map("Solaris.Treeview",
                   background=[("selected", colorTema("tablaSeleccion"))],
                   foreground=[("selected", "#FFFFFF")])

    def construirTablaTokens(self, contenedorPadre):
        marco = ctk.CTkFrame(contenedorPadre, corner_radius=10)
        marco.grid(row=0, column=0, sticky="nsew", padx=(12, 6), pady=(0, 12))
        marco.rowconfigure(1, weight=1)
        marco.columnconfigure(0, weight=1)

        ctk.CTkLabel(marco, text="Tabla de tokens", font=self.fuenteEtiqueta,
                     anchor="w").grid(row=0, column=0, sticky="ew",
                                      padx=14, pady=(12, 6))

        self.aplicarEstiloTabla()
        marcoTabla = ctk.CTkFrame(marco, fg_color="transparent")
        marcoTabla.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        marcoTabla.rowconfigure(0, weight=1)
        marcoTabla.columnconfigure(0, weight=1)

        columnas = ("Token", "Tipo", "Primera línea", "Repeticiones")
        self.tablaTokens = ttk.Treeview(marcoTabla, columns=columnas,
                                        show="headings", style="Solaris.Treeview")
        anchos = [170, 130, 100, 220]
        for columna, ancho in zip(columnas, anchos):
            self.tablaTokens.heading(columna, text=columna)
            self.tablaTokens.column(columna, width=ancho, anchor="w", stretch=True)

        barraVertical = ctk.CTkScrollbar(marcoTabla,
                                         command=self.tablaTokens.yview)
        barraHorizontal = ctk.CTkScrollbar(marcoTabla, orientation="horizontal",
                                           command=self.tablaTokens.xview)
        self.tablaTokens.configure(yscrollcommand=barraVertical.set,
                                   xscrollcommand=barraHorizontal.set)
        self.tablaTokens.grid(row=0, column=0, sticky="nsew")
        barraVertical.grid(row=0, column=1, sticky="ns")
        barraHorizontal.grid(row=1, column=0, sticky="ew")

    def construirTablaSimbolos(self, contenedorPadre):
        marco = ctk.CTkFrame(contenedorPadre, corner_radius=10)
        marco.grid(row=0, column=1, sticky="nsew", padx=(6, 12), pady=(0, 12))
        marco.rowconfigure(1, weight=1)
        marco.columnconfigure(0, weight=1)

        ctk.CTkLabel(marco, text="Tabla de símbolos", font=self.fuenteEtiqueta,
                     anchor="w", text_color=("#0E9F6E", "#34D399")).grid(
                         row=0, column=0, sticky="ew", padx=14, pady=(12, 6))

        marcoTabla = ctk.CTkFrame(marco, fg_color="transparent")
        marcoTabla.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        marcoTabla.rowconfigure(0, weight=1)
        marcoTabla.columnconfigure(0, weight=1)

        columnas = ("#", "Variable", "Tipo")
        self.tablaSimbolos = ttk.Treeview(marcoTabla, columns=columnas,
                                          show="headings", style="Solaris.Treeview")
        anchos = [40, 110, 80]
        for columna, ancho in zip(columnas, anchos):
            self.tablaSimbolos.heading(columna, text=columna)
            self.tablaSimbolos.column(columna, width=ancho, anchor="w", stretch=True)

        barraVertical = ctk.CTkScrollbar(marcoTabla,
                                         command=self.tablaSimbolos.yview)
        self.tablaSimbolos.configure(yscrollcommand=barraVertical.set)
        self.tablaSimbolos.grid(row=0, column=0, sticky="nsew")
        barraVertical.grid(row=0, column=1, sticky="ns")

    # REcorrido sintactico completo
    def construirVistaSintactico(self, contenedor):
        contenedor.rowconfigure(0, weight=1)
        contenedor.columnconfigure(0, weight=1)

        marco = ctk.CTkFrame(contenedor, corner_radius=10)
        marco.grid(row=0, column=0, sticky="nsew", padx=12, pady=(0, 12))
        marco.rowconfigure(1, weight=1)
        marco.columnconfigure(0, weight=1)

        ctk.CTkLabel(marco, text="Recorrido del análisis sintáctico",
                     font=self.fuenteEtiqueta, anchor="w").grid(
                         row=0, column=0, sticky="ew", padx=14, pady=(12, 6))

        self.textoRecorrido = ctk.CTkTextbox(
            marco, font=self.fuenteMonoChica, wrap="none",
            activate_scrollbars=True, state="disabled")
        self.textoRecorrido.grid(row=1, column=0, sticky="nsew",
                                 padx=12, pady=(0, 12))

    def actualizarRecorridoSintactico(self):
        self.textoRecorrido.configure(state="normal")
        self.textoRecorrido.delete("1.0", "end")
        if self.recorridoSintactico.strip():
            self.textoRecorrido.insert("end", self.recorridoSintactico)
        else:
            self.textoRecorrido.insert(
                "end",
                "Aún no se ha ejecutado el análisis sintáctico.\n"
                "Vuelve al editor y pulsa el botón «Sintáctico».")
        self.textoRecorrido.configure(state="disabled")


    def construirVistaSemantico(self, contenedor):
        contenedor.rowconfigure(1, weight=1)
        contenedor.columnconfigure(0, weight=1)

        barraNav = ctk.CTkFrame(contenedor, fg_color="transparent")
        barraNav.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        ctk.CTkButton(barraNav, text="←", width=36,
                    command=self.arbolAnterior).pack(side="left", padx=4)
        self.etiquetaArbolActual = ctk.CTkLabel(barraNav, text="—",
                                                font=self.fuenteEtiqueta)
        self.etiquetaArbolActual.pack(side="left", padx=8)
        ctk.CTkButton(barraNav, text="→", width=36,
                    command=self.arbolSiguiente).pack(side="left", padx=4)

        raiz_vacia = arbol_desde_dict({"top": "Sin análisis semántico aún"})
        self.visorSemantico = VisorArbolSemantico(contenedor, raiz_vacia)
        self.visorSemantico.grid(row=1, column=0, sticky="nsew", padx=12, pady=12)


    def construirVistaRecorridoTabla(self, contenedor):
        contenedor.rowconfigure(0, weight=1)
        contenedor.columnconfigure(0, weight=1)
        marco = ctk.CTkFrame(contenedor, corner_radius=10)
        marco.grid(row=0, column=0, sticky="nsew", padx=12, pady=(0, 12))
        marco.rowconfigure(1, weight=1)
        marco.columnconfigure(0, weight=1)

        ctk.CTkLabel(marco, text="Gramática de operaciones (atribuida)",
                    font=self.fuenteEtiqueta, anchor="w").grid(
                        row=0, column=0, sticky="ew", padx=14, pady=(12, 6))

        columnas = ("Gramática", "Gramática atribuida (.valor)")
        self.tablaRecorrido = ttk.Treeview(marco, columns=columnas,
                                        show="headings", style="Solaris.Treeview")
        anchos = [280, 480]
        for columna, ancho in zip(columnas, anchos):
            self.tablaRecorrido.heading(columna, text=columna)
            self.tablaRecorrido.column(columna, width=ancho, anchor="w", stretch=True)
        self.tablaRecorrido.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

        self.tablaRecorrido.tag_configure("par", background=colorTema("filaPar"))
        self.tablaRecorrido.tag_configure("impar", background=colorTema("filaImpar"))

        # filas que llevan a las operaciones aritmeticas: negritas y en verde
        self.tablaRecorrido.tag_configure("parOperacion", background=colorTema("filaPar"),
                                        foreground="#0E9F6E", font=FUENTE_TABLA_ENC)
        self.tablaRecorrido.tag_configure("imparOperacion", background=colorTema("filaImpar"),
                                        foreground="#0E9F6E", font=FUENTE_TABLA_ENC)

        for i, (izq, der, esOperacion) in enumerate(GRAMATICA_OPERACION):
            if esOperacion:
                etiqueta = "parOperacion" if i % 2 == 0 else "imparOperacion"
            else:
                etiqueta = "par" if i % 2 == 0 else "impar"
            self.tablaRecorrido.insert("", "end", tags=(etiqueta,), values=(izq, der))


    def cargarArbolDesdeArchivo(self, ruta):
        """Carga un árbol semántico de prueba desde un archivo JSON."""
        try:
            with open(ruta, "r", encoding="utf-8") as archivo:
                return json.load(archivo)
        except (FileNotFoundError, json.JSONDecodeError) as error:
            # si algo falla, se muestra un árbol vacío en vez de romper la app
            return {"top": f"Error al cargar árbol: {error}"}

    def poblarTablas(self):
        lexico = self.analizadorLexico

        self.tablaTokens.delete(*self.tablaTokens.get_children())
        self.tablaSimbolos.delete(*self.tablaSimbolos.get_children())

        self.tablaTokens.tag_configure("par", background=colorTema("filaPar"))
        self.tablaTokens.tag_configure("impar", background=colorTema("filaImpar"))
        self.tablaSimbolos.tag_configure("par", background=colorTema("filaPar"))
        self.tablaSimbolos.tag_configure("impar", background=colorTema("filaImpar"))

        # Tabla de tokens: tok / tiTok / linTok / repTok 
        for indice in range(len(lexico.tok)):
            lexema = lexico.tok[indice]
            tipo = lexico.tiTok[indice]
            linea = lexico.linTok[indice]
            repeticiones = lexico.repTok[indice]
            textoRepeticiones = (", ".join(map(str, repeticiones))
                                 if repeticiones else "-")
            etiqueta = "par" if indice % 2 == 0 else "impar"
            self.tablaTokens.insert(
                "", "end", tags=(etiqueta,),
                values=(lexema, tipo, linea, textoRepeticiones))

        # Tabla de simbolos
        fila = 0
        for indice in range(len(lexico.tok)):
            if lexico.tiTok[indice] == "Identificador":
                etiqueta = "par" if fila % 2 == 0 else "impar"
                self.tablaSimbolos.insert(
                    "", "end", tags=(etiqueta,),
                    values=(fila, lexico.tok[indice], "—"))
                fila += 1

 
    # Acciones
    def poblarInformacion(self):
        informacion = (
            "Compilador:    Beta\n"
            "Lenguaje:      Solaris-Lang\n"
            "Fases activas: Léxico, Sintáctico\n"
            "\n"
            "Tipos soportados:\n"
            "  Ent  - Entero\n"
            "  Dec  - Decimal\n"
            "  Ban  - Booleano\n"
            "  Sim  - Simbolo (1 char)\n"
            "  Sen  - Cadena\n"
            "\n"
            "Palabras reservadas:\n"
            "  Begin, End, Ent, Dec,\n"
            "  Ban, Sim, Sen\n"
        )
        self.textoInformacion.configure(state="normal")
        self.textoInformacion.delete("1.0", "end")
        self.textoInformacion.insert("end", informacion)
        self.textoInformacion.configure(state="disabled")

    def cargarArchivo(self):
        ruta = filedialog.askopenfilename(
            title="Abrir archivo de código",
            filetypes=[("Archivos de texto", "*.txt *.sol *.sl"),
                       ("Todos", "*.*")])
        if not ruta:
            return
        try:
            with open(ruta, "r", encoding="utf-8") as archivo:
                contenido = archivo.read()
            self.editorCodigo.delete("1.0", "end")
            self.editorCodigo.insert("end", contenido)
            self.dibujarNumerosLinea()
        except Exception as error:
            messagebox.showerror("Error",
                                 f"No se pudo cargar el archivo:\n{error}")

    def analizarLexico(self):
        codigo = self.editorCodigo.get("1.0", "end")

        descriptor, rutaTemporal = tempfile.mkstemp(suffix=".sol", text=True)
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as archivo:
                archivo.write(codigo)
            # el archivo ya esta cerrado aqui -> SinLex puede abrirlo

            lexico = SinLex(rutaTemporal)

            # SinLex imprime tokens y errores por consola y se captuar la salida
            bufer = io.StringIO()
            with contextlib.redirect_stdout(bufer):
                lexico.anac()
            salida = bufer.getvalue()
        finally:
            try:
                os.remove(rutaTemporal)
            except OSError:
                pass

        self.analizadorLexico = lexico
        self.botonesFases["Código intermedio"].configure(state="disabled")
        # un nuevo lexico invalida el recorrido sintactico anterior
        self.recorridoSintactico = ""
        PALABRAS_ERROR = ("error", "no reconocido", "inválido", "desconocido", "carácter inválido")

        # Solo mostrar errores
        errores = [
            linea.strip() for linea in salida.splitlines()
            if any(p in linea.lower() for p in PALABRAS_ERROR)
        ]
        self.mostrarErrores(errores)

        if errores:
            self.establecerEstado("errores léxicos", "#C81E1E")
            self.botonesFases["Sintáctico"].configure(state="disabled")
        else:
            self.establecerEstado("léxico ok", "#0E9F6E")
            self.botonesFases["Sintáctico"].configure(state="normal")

    def analizarSintactico(self):
        # El sintactico parte de lo que produjo el lexico
        if self.analizadorLexico is None:
            messagebox.showinfo(
                "Sin análisis",
                "Ejecuta primero el análisis Léxico para generar los tokens.")
            return

        try:
            sintactico = Sinta(self.analizadorLexico)
            sintactico.gram()       # define la gramatica antes de la fun ali()
            sintactico.variable()   # llena la lista de variables
            self.sintactico_actual = sintactico

            # anali() imprime el rastreo por consola: lo capturamos
            bufer = io.StringIO()
            with contextlib.redirect_stdout(bufer):
                sintactico.anali()
            salida = bufer.getvalue()
        except Exception as error:
            messagebox.showerror(
                "Error en análisis sintáctico",
                f"El analizador sintáctico lanzó un error:\n{error}")
            self.establecerEstado("error sintáctico", "#C81E1E")
            return

        # GUardar el recorrido completo
        self.recorridoSintactico = salida
        PALABRAS_ERROR = ("error", "no reconocido", "inválido", "desconocido", "carácter inválido", "rechaz", "inesperado")
        # Solo mostrasr los errores del recorrido
        errores = [
                linea.strip() for linea in salida.splitlines()
                if any(p in linea.lower() for p in PALABRAS_ERROR)
            ]
        self.mostrarErrores(errores)

        if errores:
                self.establecerEstado("errores léxicos", "#C81E1E")
                self.botonesFases["Semántico"].configure(state="disabled")
        else:
            self.establecerEstado("Sintactico ok", "#0E9F6E")
            self.botonesFases["Semántico"].configure(state="normal", command=self.analizarSemantico)

    def analizarSemantico(self):
        semantico = Semantico(self.analizadorLexico)
        errores = semantico.analiSeman()
        self.mostrarErrores(errores)

        if errores:
            # hay errores: solo los mostramos, NO generamos el arbol ni se desbloquea nada
            self.establecerEstado("errores semánticos", "#C81E1E")
            self.botonesFases["Semántico"].configure(state="disabled")
            self.botonesFases["Código intermedio"].configure(state="disabled")
            return

        # solo llegamos aqui si el analisis semantico fue limpio
        self.arbolesSemanticos = semantico.arbolSeman()
        self.indiceArbolActual = 0

        self.establecerEstado("Semántico ok", "#0E9F6E")
        self.botonesFases["Semántico"].configure(state="normal", command=self.analizarSemantico)
        self.botonesFases["Código intermedio"].configure(state="normal", command=self.analizarIntermedio)


    def probarArbolFijo(self):
        """Boton de debug: carga un arbol fijo para probar SOLO el dibujado,
        sin depender del analisis semantico real."""
        import json
        datosPrueba = json.loads('''
        {
        "top": "operacion",
        "hijos": [
            {"top": "r"},
            {"top": "expr", "hijos": [
                {"top": "a"},
                {"top": "+"},
                {"top": "expr", "hijos": [
                    {"top": "termino", "hijos": [
                        {"top": "b"}, {"top": "*"}, {"top": "c"}
                    ]},
                    {"top": "-"},
                    {"top": "termino", "hijos": [
                        {"top": "d"}, {"top": "/"}, {"top": "e"}
                    ]}
                ]}
            ]}
        ]
        }
        ''')

        self.arbolesSemanticos = [datosPrueba]
        self.indiceArbolActual = 0

        # 1) primero navegamos a la pagina/tab correcta
        self.paginaTablas.tkraise()
        self.mostrarVistaSemantico()
        self.establecerEstado("debug árbol", "#1A56DB")

        # 2) y HASTA AHORA dibujamos, con el widget ya visible
        self.update_idletasks()
        self.actualizarArbolMostrado()


    def actualizarArbolMostrado(self):
        if not self.arbolesSemanticos:
            raiz = arbol_desde_dict({"top": "No hay operaciones para graficar"})
            self.etiquetaArbolActual.configure(text="—")
        else:
            datos = self.arbolesSemanticos[self.indiceArbolActual]
            raiz = arbol_desde_dict(datos)
            self.etiquetaArbolActual.configure(
                text=f"Árbol {self.indiceArbolActual + 1} de {len(self.arbolesSemanticos)}")
        self.visorSemantico.cargar_arbol(raiz)

    def arbolAnterior(self):
        if self.arbolesSemanticos and self.indiceArbolActual > 0:
            self.indiceArbolActual -= 1
            self.actualizarArbolMostrado()

    def arbolSiguiente(self):
        if self.arbolesSemanticos and self.indiceArbolActual < len(self.arbolesSemanticos) - 1:
            self.indiceArbolActual += 1
            self.actualizarArbolMostrado()



    def mostrarErrores(self, lineas):
        self.textoErrores.configure(state="normal")
        self.textoErrores.delete("1.0", "end")
        if lineas:
            self.textoErrores.insert("end", "\n".join(lineas))
        else:
            self.textoErrores.insert("end", "Sin errores detectados.")
        self.textoErrores.configure(state="disabled")


   

    def limpiar(self):
        self.editorCodigo.delete("1.0", "end")
        self.textoErrores.configure(state="normal")
        self.textoErrores.delete("1.0", "end")
        self.textoErrores.configure(state="disabled")

        self.analizadorLexico = None
        self.recorridoSintactico = ""
        self.dibujarNumerosLinea()
        self.botonesFases["Sintáctico"].configure(state="disabled")
        self.botonesFases["Semántico"].configure(state="disabled")
        self.botonesFases["Código intermedio"].configure(state="disabled")
        self.intermedioActual = None


    # Elegir el tema normaleme sera blanco

    def cambiarTema(self):
        modo = "Dark" if self.interruptorTema.get() else "Light"
        ctk.set_appearance_mode(modo)
        self.reaplicarColoresManuales()

    def reaplicarColoresManuales(self):
      
        self.editorCodigo.configure(
            bg=colorTema("editorFondo"), fg=colorTema("editorTexto"),
            insertbackground=colorTema("editorCursor"),
            selectbackground=colorTema("editorSeleccion"))
        self.lienzoNumeros.configure(bg=colorTema("lienzoFondo"))
        self.dibujarNumerosLinea()

        self.aplicarEstiloTabla()
        for tabla in (self.tablaTokens, self.tablaSimbolos):
            tabla.tag_configure("par", background=colorTema("filaPar"))
            tabla.tag_configure("impar", background=colorTema("filaImpar"))

        self.manijaErrores.configure(fg_color=colorTema("manija"))
        

if __name__ == "__main__":
    aplicacion = CompiladorInterfaz()
    aplicacion.mainloop()