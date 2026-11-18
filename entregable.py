class Intermedio:
    def __init__(self, sinLex):
        self.sinLex = sinLex
        self.tokComp = sinLex.tokComp
        self.varTipo = sinLex.varTipo
        self.expresiones = []
        self.reiniciar()

    def reiniciar(self):
        # tablas de la interfaz
        self.cuad_operador=[]
        self.cuad_op1=[]
        self.cuad_op2=[]
        self.cuad_res=[]
        self.trip_dir=[]
        self.trip_operador=[]
        self.trip_op1=[]
        self.trip_op2=[]
        self.lista_pcode = []
        self.pol_pila1 = []
        self.pol_pila2 = []
        self.pol_cadena = []

    def generar_codigo(self):
        self.reiniciar()
        self.sacarExpresiones()
        print("Expresiones encontradas: ", len(self.expresiones))
        for i in range(len(self.expresiones)):
            destino = self.expresiones[i][0]
            tokens = self.expresiones[i][1]
            self.rayas()
            operaciones = self.ordenar(tokens)
            self.llenaCuad(operaciones, destino)
            self.llenaTrip(operaciones, destino)
            cadena = self.armarPolaca(tokens, destino)
            self.pasarPcode(cadena)   # el pcode sale de la cadena de la polaca

    def sacarExpresiones(self):
        # agarro cada sentencia hasta el ; y veo si es asignacion con operaciones
        self.expresiones = []
        sentencia = []
        for tk in self.tokComp:
            if tk != ";":
                sentencia.append(tk)
                continue
            if len(sentencia) > 2 and sentencia[0] in self.varTipo and sentencia[1] == "=":
                der = sentencia[2:]
                ban = 0
                for t in der:
                    if t == '"' or t == "True" or t == "False":
                        ban = 2  # cadenas y booleanos no
                        break
                    if t == "+" or t == "-" or t == "*" or t == "/":
                        ban = 1
                if ban == 1:
                    self.expresiones.append([sentencia[0], der])
            sentencia = []

    def rayas(self):
        # separa una expresion de otra en las tablas
        tablas = [self.cuad_operador, self.cuad_op1, self.cuad_op2, self.cuad_res,
                  self.trip_dir, self.trip_operador, self.trip_op1, self.trip_op2,
                  self.lista_pcode, self.pol_pila1, self.pol_pila2, self.pol_cadena]
        for t in tablas:
            t.append("---")

    def ordenar(self, tokens):
        # copio los tokens pa no mover los originales
        lista = []
        for t in tokens:
            lista.append(t)

        operaciones = []
        nivel = 1
        while nivel <= 2:
            if nivel == 1:
                buscar = ["*", "/"]   # primero estas
            else:
                buscar = ["+", "-"]
            while True:
                pos = -1
                for i in range(len(lista)):
                    if lista[i] in buscar:
                        pos = i
                        break
                if pos == -1:
                    break
                # la operacion sale y en su lugar queda su temporal v0, v1...
                temporal = "v" + str(len(operaciones))
                operaciones.append([lista[pos], lista[pos-1], lista[pos+1]])
                lista.pop(pos+1)
                lista.pop(pos)
                lista[pos-1] = temporal
            nivel += 1
        return operaciones

    def llenaCuad(self, operaciones, destino):
        for i, op in enumerate(operaciones):
            self.cuad_operador.append(op[0])
            self.cuad_op1.append(op[1])
            self.cuad_op2.append(op[2])
            self.cuad_res.append(f"v{i}")
        #la asignacion
        self.cuad_operador.append("=")
        self.cuad_op1.append(f"v{len(operaciones)-1}")
        self.cuad_op2.append("")
        self.cuad_res.append(destino)

    def llenaTrip(self, operaciones, destino):
        n = len(operaciones)
        for i in range(n):
            self.trip_dir.append(f"[{i}]")
            self.trip_operador.append(operaciones[i][0])
            self.trip_op1.append(self.cambiaTemp(operaciones[i][1]))
            self.trip_op2.append(self.cambiaTemp(operaciones[i][2]))
        self.trip_dir.append(f"[{n}]")
        self.trip_operador.append("=")
        self.trip_op1.append(f"[{n-1}]")
        self.trip_op2.append(destino)

    def cambiaTemp(self, valor):
        # en triplos no van temporales, v2 es la fila [2]
        if valor[0] == "v" and valor[1:].isdigit():
            return "[" + valor[1:] + "]"
        return valor

    def armarPolaca(self, tokens, destino):
        # pila de operandos, cada uno es [ya salio?, texto pal pcode, texto pa la tabla]
        # ya salio = 1 cuando es el resultado de una operacion
        # Nota: el = va hasta abajo pa q salga al final
        pila = [[0, destino, destino]]
        ops = ["="]
        nivel = {"=": 0, "+": 1, "-": 1, "*": 2, "/": 2}
        for tk in tokens:
            if tk in nivel:
                while nivel[ops[len(ops)-1]] >= nivel[tk]:
                    self.sacarOp(pila, ops)
                ops.append(tk)
            else:
                pila.append([0, tk, tk])
        while len(ops) > 0:
            self.sacarOp(pila, ops)
        return pila[0][1]

    def sacarOp(self, pila, ops):
        # antes de sacar guardo como estaban las pilas
        texto = ""
        for p in pila:
            if p[0] == 0:
                texto = texto + p[1] + " "
        self.pol_pila1.append(texto.strip())
        texto = ""
        for o in ops:
            texto = texto + o + " "
        self.pol_pila2.append(texto.strip())

        op = ops.pop()
        seg = pila.pop()
        pri = pila.pop()
        # en la tabla primero el de arriba (2 5 * x =), menos cuando los dos ya eran resultado
        if pri[0] == 1 and seg[0] == 1:
            tabla = pri[2] + " " + seg[2] + " " + op
        else:
            tabla = seg[2] + " " + pri[2] + " " + op
        pila.append([1, pri[1] + " " + seg[1] + " " + op, tabla])

        texto = ""
        for p in pila:
            if p[0] == 1:
                texto = texto + p[2] + " "
        self.pol_cadena.append(texto.strip())

    def pasarPcode(self, cadena):
        inst = {"=": "sto;", "+": "adi;", "-": "sbi;", "*": "mpi;", "/": "div;"}
        partes = cadena.split(" ")
        self.lista_pcode.append("lda " + partes[0] + ";")
        for i in range(1, len(partes)):
            p = partes[i]
            if p in inst:
                self.lista_pcode.append(inst[p])
            elif p[0] in self.sinLex.num:
                self.lista_pcode.append("ldc " + p + ";")
            else:
                self.lista_pcode.append("lod " + p + ";")





                

class Optimizacion: # Optimizacion, se hace sobre las asignaciones del programa (ocupa lo del lexico)
    def __init__(self, sinLex):
        self.sinLex = sinLex
        self.lineas = sinLex.lineas
        self.tokComp = sinLex.tokComp
        self.linComp = sinLex.linComp
        self.varTipo = sinLex.varTipo
        self.tipoVar = sinLex.tipoVar
        self.vueltas = 1000 # la 2da vuelta es x si una optimizacion deja algo pa otra
        self.maxPotencia = 100 # x * 6 ya son muchas sumas, ya no conviene
        self.sentLin=[]
        self.sentTok=[]
        self.sentBorrada=[]
        # lo de la tabla de cambios
        self.regVuelta=[]
        self.regLinea=[]
        self.regOpt=[]
        self.regAntes=[]
        self.regDespues=[]
        self.regCodigo=[] # el codigo como iba en cada cambio (pa la interfaz)
        self.regLinCod=[]
        self.codOri=[]
        self.codOpt=[]

    def optimiza(self):
        self.armaSentencias()
        self.vuelta = 1
        while self.vuelta <= self.vueltas:
            antes = len(self.regOpt)
            self.precalculoExprecionesConst()
            self.eliminacionSecNulas()
            self.reduccionPotencia()
            self.propagacionCopias()
            if len(self.regOpt) == antes:
                break # por si las moscas
            self.vuelta += 1
        self.armaCodigo()
        return self.codOpt

    def precalculoExprecionesConst(self):
        # operaciones entre puros numeros se hacen de una vez, con la jerarquia
        self.ind = 0
        while self.ind < len(self.sentTok):
            if self.esAsigArit(self.ind) == 1:
                self.antes = self.textoSent(self.ind)
                self.der = self.sacaDer(self.ind)
                self.cambio = 0
                self.precalcMul()
                self.precalcSum()
                if self.cambio == 1:
                    # redondeo si es Ent, igual q en el arbol del semantico
                    if len(self.der) == 1 and '.' in self.der[0] and self.tipoDe(self.sentTok[self.ind][0]) == "Ent":
                        self.der[0] = str(round(float(self.der[0])))
                    self.ponDer(self.ind, self.der)
                    self.guardaCambio(self.ind, "Precalculo de expresiones constantes", self.antes)
            self.ind = self.ind + 1

    def precalcMul(self):
        # * y / , bloq es pa cuando una ya no se pudo y lo q sigue del termino depende de esa
        bloq = 0
        i = 1
        while i < len(self.der) - 1:
            if self.der[i] == "+" or self.der[i] == "-":
                bloq = 0
                i += 2
                continue
            sePuede = 0
            if bloq == 0 and self.esNumero(self.der[i-1]) == 1 and self.esNumero(self.der[i+1]) == 1:
                if self.esNeutro(self.der[i-1], self.der[i], self.der[i+1]) == 0:
                    sePuede = 1
            if self.der[i] == "/" and self.esCero(self.der[i+1]) == 1:
                sePuede = 0
            elif self.der[i] == "/" and sePuede == 1 and self.divInexacta(self.der[i-1], self.der[i+1]) == 1:
                # Nota: 10 / 3 en un Ent el semantico lo marcaba como decimal, asi q solo en Dec
                if self.tipoDe(self.sentTok[self.ind][0]) != "Dec":
                    sePuede = 0
            if sePuede == 1:
                self.der[i-1] = self.opera(self.der[i-1], self.der[i], self.der[i+1])
                self.der.pop(i+1)
                self.der.pop(i)
                self.cambio = 1
            else:
                bloq = 1
                i += 2

    def esNeutro(self, izq, oper, der):
        # Funicion para cuando se tenga que diferenciar de precalculo 
        if (oper == "*" or oper == "/") and self.esUno(der) == 1:
            return 1
        if oper == "*" and self.esUno(izq) == 1:
            return 1
        if (oper == "+" or oper == "-") and self.esCero(der) == 1:
            return 1
        if oper == "+" and self.esCero(izq) == 1:
            return 1
        return 0
    
    def precalcSum(self):
        # + y - nomas desde el principio, x + 2 + 3 no se puede pq va primero x + 2
        while len(self.der) >= 3:
            if self.der[1] != "+" and self.der[1] != "-":
                return
            if self.esNumero(self.der[0]) == 0 or self.esNumero(self.der[2]) == 0:
                return
            if self.der[1] == "-" and self.valorNum(self.der[0]) < self.valorNum(self.der[2]):
                return # sin negativos
            if self.esNeutro(self.der[0], self.der[1], self.der[2]) == 1:
                return # sec nulas en lugar de este
            if len(self.der) > 3 and self.der[3] != "+" and self.der[3] != "-":
                return
            self.der[0] = self.opera(self.der[0], self.der[1], self.der[2])
            self.der.pop(2)
            self.der.pop(1)
            self.cambio = 1

    def eliminacionSecNulas(self):
        # x + 0, 0 + x, x - 0, x * 1, 1 * x, x / 1 y si queda x = x se quita la linea
        for n in range(len(self.sentTok)):
            if self.esAsigArit(n) == 0:
                continue
            antes = self.textoSent(n)
            der = self.sacaDer(n)
            cambio = 0
            i = 1
            while i < len(der) - 1:
                op = der[i]
                if (op == "*" or op == "/") and self.esUno(der[i+1]) == 1:
                    der.pop(i+1)
                    der.pop(i)
                    cambio = 1
                elif op == "*" and self.esUno(der[i-1]) == 1 and (i == 1 or der[i-2] == "+" or der[i-2] == "-"):
                    der.pop(i)
                    der.pop(i-1)
                    cambio = 1
                elif (op == "+" or op == "-") and self.esCero(der[i+1]) == 1 and (i+2 >= len(der) or der[i+2] == "+" or der[i+2] == "-"):
                    der.pop(i+1)
                    der.pop(i)
                    cambio = 1
                elif op == "+" and i == 1 and self.esCero(der[0]) == 1:
                    der.pop(1)
                    der.pop(0)
                    cambio = 1
                else:
                    i = i + 2
            #print(der)
            if cambio == 1:
                self.ponDer(n, der)
            if len(der) == 1 and der[0] == self.sentTok[n][0]:
                self.sentBorrada[n] = 1
                cambio = 1
            if cambio == 1:
                self.guardaCambio(n, "Eliminacion de secuencias nulas", antes)

    def reduccionPotencia(self):
        # x * 3 -> x + x + x , solo si el termino es nomas eso (x * 2 * y no)
        n = 0
        while n < len(self.sentTok):
            if self.esAsigArit(n) == 1:
                antes = self.textoSent(n)
                der = self.sacaDer(n)
                nuevo = [] # aqui se va armando como queda
                cambio = 0
                k = 0
                while k < len(der):
                    x = ""
                    veces = 0
                    if k + 2 < len(der) and der[k+1] == "*":
                        iniTerm = k == 0 or der[k-1] == "+" or der[k-1] == "-"
                        finTerm = k + 3 >= len(der) or der[k+3] == "+" or der[k+3] == "-"
                        if iniTerm and finTerm:
                            if self.cuantasVeces(der[k+2]) > 0 and self.esNumero(der[k]) == 0:
                                x = der[k]
                                veces = self.cuantasVeces(der[k+2])
                            elif self.cuantasVeces(der[k]) > 0 and self.esNumero(der[k+2]) == 0:
                                x = der[k+2]
                                veces = self.cuantasVeces(der[k])
                    if x == "":
                        nuevo.append(der[k])
                        k += 1
                    else:
                        # si venia un - antes queda a - x - x , si no a + x + x
                        signo = "+"
                        if k > 0 and der[k-1] == "-":
                            signo = "-"
                        nuevo.append(x)
                        for c in range(veces - 1):
                            nuevo.append(signo)
                            nuevo.append(x)
                        #nuevo = nuevo + [x, signo, x]   asi estaba cuando era solo * 2
                        cambio = 1
                        k += 3
                if cambio == 1:
                    self.ponDer(n, nuevo)
                    self.guardaCambio(n, "Reduccion de potencia", antes)
            n = n + 1

    def propagacionCopias(self):
        # z = a ; en las de abajo z se cambia x a, hasta q z o a cambien (o los pidan con Entrada)
        # Nota pra mi: constantes no, eso no es copia
        self.copias = {}
        n = 0
        while n < len(self.sentTok):
            toks = self.sentTok[n]
            if self.sentBorrada[n] == 0:
                if toks[0] == "Entrada" and len(toks) > 1:
                    self.quitaCopia(toks[1])
                elif self.esAsig(n) == 1:
                    nomV = toks[0]
                    der = self.sacaDer(n)
                    if self.esArit(der) == 1:
                        antes = self.textoSent(n)
                        cambio = 0
                        i = 0
                        while i < len(der): # solo operandos, van en par
                            if der[i] in self.copias:
                                der[i] = self.copias[der[i]]
                                cambio = 1
                            i = i + 2
                        if cambio == 1:
                            self.ponDer(n, der)
                            self.guardaCambio(n, "Propagacion de copias", antes)
                    self.quitaCopia(nomV)
                    if self.esArit(der) == 1 and len(der) == 1 and der[0] != nomV and self.esNumero(der[0]) == 0:
                        self.copias[nomV] = der[0]
            n = n + 1

        # la copia q ya nadie lee abajo sobra
        for n in range(len(self.sentTok)):
            if self.esCopia(n) == 1 and self.seUsaDespues(n, self.sentTok[n][0]) == 0:
                antes = self.textoSent(n)
                self.sentBorrada[n] = 1
                self.guardaCambio(n, "Propagacion de copias", antes)

    def quitaCopia(self, nomV):
        # sale si es la q cambio o si otra copia valia eso
        for nom in list(self.copias):
            if nom == nomV or self.copias[nom] == nomV:
                del self.copias[nom]

    def esCopia(self, n):
        if self.esAsig(n) == 0:
            return 0
        der = self.sacaDer(n)
        if len(der) == 1 and der[0] in self.varTipo and der[0] != self.sentTok[n][0]:
            return 1
        return 0

    def seUsaDespues(self, n, nomV):
        k = n + 1
        while k < len(self.sentTok):
            toks = self.sentTok[k]
            if self.sentBorrada[k] == 1 or self.esTipo(toks[0]) == 1:
                k = k + 1
                continue
            if toks[0] == "Entrada":
                if len(toks) > 1 and toks[1] == nomV:
                    return 0 # le piden otro valor
            elif len(toks) > 1 and toks[1] == "=":
                if nomV in toks[2:]:
                    return 1
                if toks[0] == nomV:
                    return 0 # le ponen otro valor sin leerla
            elif nomV in toks:
                return 1
            k = k + 1
        return 0

    def esTipo(self, tk):
        if tk == "Ent" or tk == "Dec" or tk == "Ban" or tk == "Sim" or tk == "Sen":
            return 1
        return 0

    def armaSentencias(self):
        # el tokComp por sentencias hasta el ; , Begin End y && van solos
        # la cadena se junta en un token con su texto
        self.sentLin=[]
        self.sentTok=[]
        self.sentBorrada=[]
        self.regVuelta=[]
        self.regLinea=[]
        self.regOpt=[]
        self.regAntes=[]
        self.regDespues=[]
        self.regCodigo=[]
        self.regLinCod=[]
        ind = 0
        largo = len(self.tokComp)
        while ind < largo:
            tk = self.tokComp[ind]
            lin = self.linComp[ind]
            if tk == "Begin" or tk == "End":
                toks = [tk]
                ind = ind + 1
            elif tk == "&&":
                linea = self.lineas[lin - 1]  # el lexico no guarda el texto del comentario
                toks = [linea[linea.find('&&'):].strip()]
                ind = ind + 1
            else:
                toks = []
                while ind < largo and self.tokComp[ind] != ";":
                    if self.tokComp[ind] == '"' and ind + 1 < largo and self.tokComp[ind+1] == '"':
                        toks.append('"' + self.textoCadena(ind) + '"')
                        ind = ind + 2
                    else:
                        toks.append(self.tokComp[ind])
                        ind = ind + 1
                if ind < largo:
                    toks.append(";")
                    ind = ind + 1
            self.sentLin.append(lin)
            self.sentTok.append(toks)
            self.sentBorrada.append(0)

    def armaCodigo(self):
        self.codOri = []
        for linea in self.lineas:
            if linea.strip() != "":
                self.codOri.append(linea.rstrip())
        self.codOpt = self.juntaCodigo(-1)

    def juntaCodigo(self, nBusca):
        # otra vez por linea, sin las borradas. linEncontrada = renglon donde quedo nBusca
        codigo = []
        self.linEncontrada = -1
        linAnt = -1
        texto = ""
        n = 0
        while n < len(self.sentTok):
            if self.sentBorrada[n] == 0:
                if self.sentLin[n] != linAnt and texto != "":
                    codigo.append(texto)
                    texto = ""
                if texto == "":
                    texto = self.textoSent(n)
                else:
                    texto = texto + " " + self.textoSent(n)
                if n == nBusca:
                    self.linEncontrada = len(codigo)
                linAnt = self.sentLin[n]
            n = n + 1
        if texto != "":
            codigo.append(texto)
        return codigo

    def esAsig(self, n):
        toks = self.sentTok[n]
        if self.sentBorrada[n] == 1 or len(toks) < 3:
            return 0
        if toks[0] in self.varTipo and toks[1] == "=":
            return 1
        return 0

    def esArit(self, der):
        # que no traiga cadenas ni True/False
        if len(der) == 0:
            return 0
        for tk in der:
            if tk[0] == '"' or tk == "True" or tk == "False":
                return 0
        return 1

    def esAsigArit(self, n):
        if self.esAsig(n) == 1 and self.esArit(self.sacaDer(n)) == 1:
            return 1
        return 0

    def sacaDer(self, n):
        # lo de despues del = sin el ; , es copia
        toks = self.sentTok[n]
        fin = len(toks)
        if toks[fin-1] == ";":
            fin = fin - 1
        return toks[2:fin]

    def ponDer(self, n, der):
        toks = self.sentTok[n]
        nuevo = [toks[0], toks[1]] + der
        if toks[len(toks)-1] == ";":
            nuevo.append(";")
        self.sentTok[n] = nuevo

    def textoSent(self, n):
        return " ".join(self.sentTok[n])

    def guardaCambio(self, n, nomOpt, antes):
        self.regVuelta.append(self.vuelta)
        self.regLinea.append(self.sentLin[n])
        self.regOpt.append(nomOpt)
        self.regAntes.append(antes)
        if self.sentBorrada[n] == 1:
            self.regDespues.append("(se elimina)")
        else:
            self.regDespues.append(self.textoSent(n))
        self.regCodigo.append(self.juntaCodigo(n))
        self.regLinCod.append(self.linEncontrada)

    def tipoDe(self, nomV):
        tipo = ""
        c = 0
        while c < len(self.varTipo):
            if self.varTipo[c] == nomV:
                tipo = self.tipoVar[c]
            c = c + 1
        return tipo

    def esNumero(self, tk):
        if len(tk) == 0 or tk == '.':
            return 0
        puntos = 0
        for car in tk:
            if car == '.':
                puntos = puntos + 1
            elif car not in self.sinLex.num:
                return 0
        if puntos > 1:
            return 0
        return 1

    def valorNum(self, tk):
        if '.' in tk:
            return float(tk)
        return int(tk)

    def esCero(self, tk):
        if self.esNumero(tk) == 1 and self.valorNum(tk) == 0:
            return 1
        return 0

    def esUno(self, tk):
        if self.esNumero(tk) == 1 and self.valorNum(tk) == 1:
            return 1
        return 0

    def cuantasVeces(self, tk):
        # cuantas x van, 0 si no es entero de 2 a maxPotencia
        if self.esNumero(tk) == 0:
            return 0
        val = self.valorNum(tk)
        if val != int(val) or val < 2 or val > self.maxPotencia:
            return 0
        return int(val)

    def divInexacta(self, a, b):
        if '.' in a or '.' in b:
            return 0
        if self.valorNum(a) % self.valorNum(b) != 0:
            return 1
        return 0

    def opera(self, a, oper, b):
        va = self.valorNum(a)
        vb = self.valorNum(b)
        if oper == "+":
            res = va + vb
        elif oper == "-":
            res = va - vb
        elif oper == "*":
            res = va * vb
        else:
            res = va / vb
        esDec = 0
        if '.' in a or '.' in b:
            esDec = 1
        if oper == "/" and va % vb != 0:
            esDec = 1 # division q no da exacta
        if esDec == 0:
            return str(int(res))
        return str(round(float(res), 4))

    def textoCadena(self, idxTok):
        # igual q en semantico
        lin = self.linComp[idxTok]
        comillas = 0
        c = 0
        while c < idxTok:
            if self.tokComp[c] == '"' and self.linComp[c] == lin:
                comillas = comillas + 1
            c = c + 1
        textos = re.findall(r'"([^"]*)"', self.lineas[lin - 1])
        if comillas // 2 < len(textos):
            return textos[comillas // 2]
        return ""