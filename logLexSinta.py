import re

class SinLex:
    def __init__(self, archivo):
        self.num={'0','1','2','3','4','5','6','7','8','9'}
        self.let={'a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z'}
        self.oper={'+','-','*','/','='}
        self.simb={'&&',',',';','"'}
        self.iniFin={"Begin","End"}
        self.tipoDato={"Ent","Dec","Ban","Sim","Sen"}
        self.entSal={"Entrada","Salida"}
        self.bol={"True","False"}
        self.tok=[]
        self.tiTok=[]
        self.linTok=[]
        self.repTok=[]
        self.tokComp=[]
        self.numero=[] # Esta es la q uso para guarda los tokes numeros
        self.linComp=[]
        self.tipoVar=[] # estas 3 las llena el semantico (tabla de variables)
        self.varTipo= []
        self.linVar= []
        with open(archivo, "r", encoding="utf-8") as f:
            self.lineas = f.readlines()

    def tokencitps(self):
        tokLin=[]
        for self.nLinea, linea in enumerate(self.lineas, start=1):
            self.tokens = []
            self.tokenA = ""
            i = 0
            while i < len(linea):
                if i + 1 < len(linea):
                    if linea[i] == '&' and linea[i+1] == '&':
                        if self.tokenA:
                            self.tokens.append(self.tokenA)
                            self.tokComp.append(self.tokenA)
                            self.linComp.append(self.nLinea)
                            self.tokenA = ""
                        self.tokens.append('&&')
                        self.tokComp.append('&&')
                        self.linComp.append(self.nLinea)
                        break
                if linea[i] == '"':
                    j = linea.find('"', i + 1)
                    if j == -1:
                        if self.tokenA:
                            self.tokens.append(self.tokenA)
                            self.tokComp.append(self.tokenA)
                            self.linComp.append(self.nLinea)
                            self.tokenA = ""
                        self.tokens.append('"')
                        self.tokComp.append('"')
                        self.linComp.append(self.nLinea)
                        break
                    else:
                        if self.tokenA:
                            self.tokens.append(self.tokenA)
                            self.tokComp.append(self.tokenA)
                            self.linComp.append(self.nLinea)
                            self.tokenA = ""
                        self.tokens.append('"')
                        self.tokComp.append('"')
                        self.linComp.append(self.nLinea)   
                        self.tokens.append('"')
                        self.tokComp.append('"')
                        self.linComp.append(self.nLinea)
                        i = j + 1
                        continue
                if linea[i].isspace():
                    if self.tokenA:
                        self.tokens.append(self.tokenA)
                        self.tokComp.append(self.tokenA)
                        self.linComp.append(self.nLinea)
                        self.tokenA = ""
                else:
                    self.tokenA += linea[i]
                i += 1
            if self.tokenA:
                self.tokens.append(self.tokenA)
                self.tokComp.append(self.tokenA)
                self.linComp.append(self.nLinea)
            print(f"Línea {self.nLinea}: {self.tokens}")
            tokLin.append((self.nLinea,self.tokens))
        return tokLin

    def anac(self):
        ban = 0
        for self.nLinea, self.tokens in self.tokencitps():
            for self.token in self.tokens:
                ban = 0
                self.tipo=""
                while ban == 0:
                    ban = self.operadores(self.token)
                    if ban == 1:
                        self.tipo="Operador"
                    if ban == 0:
                        ban = self.simbo(self.token)
                        if ban == 1:
                            self.tipo="Caracter"
                    if ban == 0:
                        ban = self.palaR(self.token)
                        if ban == 1:
                            self.tipo="Palabra Reservada"
                    if ban == 0:
                        ban = self.numeros(self.token)
                        if ban == 1:
                            self.numero.append(self.token)
                            self.tipo="Caracter"
                    if ban == 0:
                        ban = self.numeroDec(self.token)
                        if ban == 1:
                            self.tipo="Caracter"
                            self.numero.append(self.token)
                    if ban == 0:
                        ban = self.variables(self.token)
                        if ban == 1:
                            self.tipo="Identificador"
                    if ban != 1: # si numeroDec o variables dieron 2 tambien entra, si no se quedaba sin tipo
                        token = self.token
                        encNum = 0
                        for c in token:
                            if c in self.num:
                                encNum = 1
                                break

                        encLet = 0
                        for c in token:
                            if c in self.let:
                                encLet = 1
                                break
                        # puntin = '.' in token
                        if encLet and encNum:
                            self.tipo = "Error de variable: mezcla letras y números"
                        elif encNum and not encLet:
                            self.tipo = "Error de número"
                        elif encLet and not encNum:
                            self.tipo = "Error de variable"
                        else:
                            self.tipo = "Símbolo desconocido"
                        print(self.tipo, " ",self.token," en línea ",self.nLinea)
                        ban = 2
                if self.token not in self.tok:
                    self.tok.append(self.token)
                    self.tiTok.append(self.tipo)
                    self.linTok.append(self.nLinea)
                    self.repTok.append([])
                else:
                    pos=self.tok.index(self.token)
                    self.repTok[pos].append(self.nLinea)

    def operadores(self,token):
        ban=0
        self.long=len(token)
        if self.long>1:
            ban=1
        for t in range(self.long):
            caracter=token[t]
            if caracter in self.oper and ban==0:
                pass
                # print(f"  operador: {caracter}") no quitarrr
            elif caracter in self.oper and ban==1:
                return 0
            else:
                return 0
        return 1

    def simbo(self,token):
        # Nota pra mi, revisar si debo incluir el coso de igual aqui o em oper
        if token in self.simb:
            return 1
        else:
            return 0


    def palaR(self,token):
        if token in self.iniFin:
            return 1
        elif token in self.entSal:
            return 1
        elif token in self.bol :
            return 1
        elif token in self.tipoDato :
            # las variables con su tipo ya no se guardan aqui, eso lo hace el semantico
            return 1
        else:
            return 0


    def numeros(self,token):
        self.long=len(token)
        for t in range(self.long):
            caracter=token[t]
            if caracter in self.num:
                pass
            else:
                return 0
        return 1

    def numeroDec(self,token):
        ban=0
        b=0
        self.long=len(token)
        if token=='.':
            print("  Carácter inválido ",token," en línea ",self.nLinea)
            return 2
        elif token[0]=='.':
            print("  Error, incluye puntos donde no debería en ",token," en línea ",self.nLinea)
            return 2
        elif token[self.long-1]=='.': # Si me da tiem´p regresar a revisar esta
            print("  Error, incluye puntos donde no debería en ",token," en línea ",self.nLinea)
            return 2
        else:
            for t in range(self.long):
                caracter=token[t]
                if caracter in self.num:
                    b=1 
                elif caracter=='.' and ban==0:
                    ban=1
                elif caracter=='.' and ban==1:
                    print("  Error de número decimal puntos extra ",token," en línea ",self.nLinea)
                    return 2
                elif ban == 1 and caracter not in self.num:
                    print("  Error de número decimal: carácter inválido ",token," en línea ",self.nLinea)
                    return 2
                elif caracter not in self.num and b==1 and caracter not in self.let:
                    print("  Error de número decimal: carácter inválido ",token," en línea ",self.nLinea)
                    return 2
                else:
                    return 0
            
            return 1

    def variables(self,token):
        self.long=len(token)
        for t in range(self.long):
            caracter=token[t]
            if caracter in self.let:
                pass
            else:
                if caracter in self.num:
                    print("  Error de variable: contiene dígitos ",token," en línea ",self.nLinea)
                else:
                    print("  Error de token no valido en ",token," en línea ",self.nLinea)
                return 2
        return 1
    
    
class Sinta: # Ahora si asui comienxa el sintactico esq ocupo de arriba

    def __init__(self,sinLex):
        self.linComp = sinLex.linComp
        self.sinLex = sinLex
        self.tok = sinLex.tok
        self.tiTok = sinLex.tiTok
        self.linTok = sinLex.linTok
        self.repTok = sinLex.repTok
        self.numero = sinLex.numero
        self.tokComp = sinLex.tokComp
        self.var=[]
        
    
    def variable(self):
        c=0
        for i in self.tiTok:
            if self.tiTok[c]=='Identificador':
                self.var.append(self.tok[c])
            c+=1
    def cvar(self):
        #hech dormid revosala
        if self.ind + 1 >= self.long:
            return 1
        c = self.ind + 1
        cvars = 0
        while c < self.long:
            if self.tokComp[c] == ';':
                break
            if self.tokComp[c] in self.var:
                cvars = cvars + 1
            c = c + 1
        return cvars
    def gram(self): # Acuerdme revisar aqui si hay algo mal en alalisis porfa
        # Hay qu revisar que lo haya copiado igual al dela librta a er si no se me fue algo porfi
        self.gramatica = [
            [1,"prinFin",["Begin","codigo","End"]],
            [2,"prinFin",["Begin","codigo","End","comentario"]],
            [1,"codigo", ["decVar","codigo"]],
            [2,"codigo", ["datoValor","codigo"]],
            [3,"codigo", ["pedValor","codigo"]],
            [4,"codigo", ["operacion","codigo"]],
            [5,"codigo", ["salida","codigo"]],
            [6,"codigo", ["decVar"]],
            [7,"codigo", ["datoValor"]],
            [8,"codigo", ["pedValor"]],
            [9,"codigo", ["operacion"]],
            [10,"codigo", ["salida"]],
            [1,"decVar",["tipoDato","nomVar",";"]],
            [2,"decVar",["tipoDato","listVar",";"]],
            [3,"decVar",["tipoDato","nomVar",";","decVar"]],
            [4,"decVar",["tipoDato","listVar",";","decVar"]],
            [1,"listVar",["nomVar",",","nomVar"]],
            [2,"listVar",["nomVar",",","listVar"]],
            [1,"tipoDato",["Ent"]],
            [2,"tipoDato",["Dec"]],
            [3,"tipoDato",["Ban"]],
            [4,"tipoDato",["Sim"]],
            [5,"tipoDato",["Sen"]],
            [1,"nomVar", ["a-z"]], # Nota paea mi, aqui voy a buscar las variables en mi lista
            [2,"nomVar",["a-z","nomVar"]],
            [1,"datoValor",["nomVar","=","numero",";"]],
            [2,"datoValor",["nomVar","=","numero",";","datoValor"]],
            [3,"datoValor",["nomVar","=","cadena",";"]],
            [4,"datoValor",["nomVar","=","cadena",";","datoValor"]],
            [5,"datoValor",["nomVar","=","True",";"]],
            [6,"datoValor",["nomVar","=","True",";","datoValor"]],
            [7,"datoValor",["nomVar","=","False",";"]],
            [8,"datoValor",["nomVar","=","False",";","datoValor"]],
            [9,"datoValor",["nomVar","=","concat",";"]],
            [10,"datoValor",["nomVar","=","concat",";","datoValor"]],
            [1,"numero",["0-9"]],
            [2,"numero",["0-9","numero"]],
            [3,"numero",["0-9",".","0-9"]],
            [4,"numero",["0-9",".","numero"]],
            [1,"cadena",['"','"']],
            [1,"pedValor",["Entrada","nomVar","=","cadena",";"]],
            [2,"pedValor",["Entrada","nomVar","=","cadena",";","pedValor"]],
            [1,"operacion",["nomVar","=","expr",";"]],
            [2,"operacion",["nomVar","=","expr",";","operacion"]],
            [1,"expr",["termino"]],
            [2,"expr",["termino","opSuma","expr"]],
            [1,"termino",["operando"]],
            [2,"termino",["operando","opMul","termino"]],
            [1,"operando",["nomVar"]],
            [2,"operando",["numero"]],
            [1,"opSuma",["+"]],
            [2,"opSuma",["-"]],
            [1,"opMul",["*"]],
            [2,"opMul",["/"]],
            [1,"salida",["Salida","=","cadena",";"]],
            [2,"salida",["Salida","=","cadena",";","salida"]],
            [3,"salida",["Salida","=","cadena",",","nomVar",";"]],
            [4,"salida",["Salida","=","cadena",",","nomVar",";","salida"]],
            [5,"salida",["Salida","=","concat",";"]],
            [6,"salida",["Salida","=","concat",";","salida"]],
            [1,"concat",["cadena","+","masCat"]],
            [2,"concat",["nomVar","+","cadena"]],
            [3,"concat",["nomVar","+","cadena","+","masCat"]],
            [1,"masCat",["elemCad"]],
            [2,"masCat",["elemCad","+","masCat"]],
            [1,"elemCad",["cadena"]],
            [2,"elemCad",["nomVar"]],
            [1,"comentario", ["&&"]],
            [2,"comentario", ["&&","comentario"]]
        ] # Nota pra mi, debo organizar bien esto pq me pierdo
 
        self.nt=['prinFin','codigo','decVar','tipoDato','nomVar','datoValor','numero','cadena','pedValor','operacion','expr','termino','operando','opSuma','opMul','salida','comentario','concat','masCat','elemCad','listVar']
        self.term=["Begin","End","Ent","Dec","Ban","Sim","Sen","Entrada","Salida","True","False",";",",","=","+","-","*","/","&&",".",'"']
        # Son solo pruebas por ahora, borralo si loq uires dejar asi.
    def anali(self):
        
        self.indEror = -1
        self.esperados = []
        self.msgErrorMax = ""
        self.reg='0'
        self.edcad=0
        self.ed='n' #Notra para mi, aqui va solo s,n,r o t o e
        self.ind=0
        self.a=['ε'] # Nota para mi, no entendi el significado pero es lo de el centro cad
        self.b=['prinFin','#'] # Aqui creo q va la graamatica 
        print(self.ed,",",self.ind+1,",",self.a,",",self.b)
        self.a=[]
        self.long=len(self.tokComp)
        #print(self.ed,",",self.ind+1,",",self.a,",",self.b)
        self.visto = set() # estados (ind, pila b) q ya se probaron
        while self.edcad==0:
            # si ya estuve en este mismo punto con la misma pila es q ese camino no jalo,
            # me regreso de una vez, si no se queda probando todas las combinaciones y se traba
            if self.ed=='n':
                estado = (self.ind, tuple(self.b))
                if estado in self.visto:
                    self.ed='r'
                    continue
                self.visto.add(estado)
            if self.ed=='n' and self.b[0]=='decVar':
                self.b.pop(0)
                cvars = self.cvar()
                numGr = 2 if cvars >= 2 else 1
                c = 0
                while c < len(self.gramatica):
                    if self.gramatica[c][1] == 'decVar' and self.gramatica[c][0] == numGr:
                        self.a.append('decVar' + str(numGr))
                        self.b = self.gramatica[c][2] + self.b
                        break
                    c = c + 1
                print(" decVar directo a produccion ", numGr)
                print(self.ed,",",self.ind+1,",",self.a,",",self.b)
                continue  
            #intento de meter var y numero
            if self.ed=='n' and self.b[0]=='nomVar':
                self.encontrado=-1
                if self.ind<self.long:
                    c=0
                    while c<len(self.var):
                        if self.var[c]==self.tokComp[self.ind]:
                            self.encontrado=c
                            break
                        c=c+1
                if self.encontrado!=-1:
                    self.b.pop(0)
                    self.a.append('nomVar'+str(self.encontrado+1))
                    self.ind=self.ind+1
                    print(self.ed,",",self.ind+1,",",self.a,",",self.b)
                else: # Cambios de Juan
                    self.ed='r'
                    
                    if self.ind > self.indEror:
                        self.indEror = self.ind
                        self.esperados = []
                    if self.ind == self.indEror:
                        self.esperados.append('VARIABLE')
                    print(self.ed,",",self.ind+1,",",self.a,",",self.b)
                continue
            elif self.ed=='n' and self.b[0]=='numero':
                self.encontrado=-1
                if self.ind<self.long:
                    c=0
                    while c<len(self.numero):
                        if self.numero[c]==self.tokComp[self.ind]:
                            self.encontrado=c
                            break
                        c=c+1
                if self.encontrado!=-1:
                    self.b.pop(0)
                    self.a.append('numero'+str(self.encontrado+1))
                    self.ind=self.ind+1
                    print(" numero reconocido ")
                    print(self.ed,",",self.ind+1,",",self.a,",",self.b)
                else:#Aqui tambien (yo cambie)
                    self.ed='r'
                    if self.ind > self.indEror:   
                        self.indEror = self.ind
                        self.esperados = []
                    if self.ind == self.indEror:
                        self.esperados.append('NUMERO')
                    print(self.ed,",",self.ind+1,",",self.a,",",self.b)
                
                continue    
            # Aqui analisis de rrgal uno ( debo agg lo de var y numeros de lexico)
            if self.ed=='n' and self.b[0] in self.nt:
                self.actual=self.b[0]
                self.b.pop(0)
                c=0
                while c<len(self.gramatica):
                    if self.gramatica[c][1]==self.actual:
                        if self.gramatica[c][0]==1:
                            self.a.append(self.actual+str(self.gramatica[c][0]))
                            self.tota=self.gramatica[c][2]
                            self.b=self.tota+self.b
                            break
                    c+=1
                print(" Regla 1 usada ")
                print(self.ed,",",self.ind+1,",",self.a,",",self.b)
            # Este es el de regla dos ( debo agg lo de var y numeros de lexico)
            elif self.ed=='n' and self.ind<self.long and self.tokComp[self.ind]==self.b[0]: 
                self.a.append(self.b[0])
                self.b.pop(0)
                self.ind=self.ind+1
                print(" Regla 2 usada ")
                print(self.ed,",",self.ind+1,",",self.a,",",self.b)
            # Aqi regla tres (sepa si este bien, ya me esrese help)
            elif self.ed=='n' and self.ind==self.long and self.b[0]=='#':
                self.ed='t'
                self.ind=self.ind+1
                self.edcad=1
                print(" Regla 3 usada ")
                print(self.ed,",",self.ind+1,",",self.a,",",self.b)
                print(" CADENA ACEPTADA ")
            elif self.ed=='n' and self.ind==self.long:
                # se acabaron los tokens, guardo lo q faltaba
                self.ed='r'
                if self.ind > self.indEror:
                    self.indEror = self.ind
                    self.esperados = []
                if self.ind == self.indEror:
                    self.esperados.append(self.b[0])
                print(self.ed,",",self.ind+1,",",self.a,",",self.b)
            # Regla 4 puse exactmente lo contrario a la dps
            elif self.ed=='n' and self.ind<self.long and self.tokComp[self.ind]!=self.b[0]:
                self.ed='r'
                # no coincidio, guardo q se esperaba aqui
                if self.ind > self.indEror:
                    self.indEror = self.ind
                    self.esperados = []
                if self.ind == self.indEror:
                    self.esperados.append(self.b[0])
                print(" Regla 4 usada ")
                print(self.ed,",",self.ind+1,",",self.a,",",self.b)

            # Regla 5 est puede qu nos de erorr
            elif self.ed=='r':
                self.aux=self.a[len(self.a)-1]
                self.nomReg=""
                self.numReg=""
                c=0
                while c<len(self.aux):
                    caracter=self.aux[c]
                    if caracter in self.sinLex.num:
                        self.numReg=self.numReg+caracter
                    else:
                        self.nomReg=self.nomReg+caracter
                    c=c+1
                if self.numReg=="" and self.nomReg in self.term:
                    self.a.pop(len(self.a)-1)
                    self.b.insert(0,self.nomReg)
                    self.ind=self.ind-1
                    print(" Regla 5 usada ")
                    print(self.ed,",",self.ind+1,",",self.a,",",self.b)
                elif self.nomReg=='nomVar' or self.nomReg=='numero':
                    self.a.pop(len(self.a)-1)
                    self.b.insert(0,self.nomReg)
                    self.ind=self.ind-1
                    #print(" Retroceso nomVar/numero ") habilitar pra pruebas en cosola
                    print(self.ed,",",self.ind+1,",",self.a,",",self.b)
                # Reglas 6
                elif self.nomReg in self.nt:
                    self.numReg=int(self.numReg)
                    self.sigReg=-1
                    c=0
                    while c<len(self.gramatica):
                        if self.gramatica[c][1]==self.nomReg and self.gramatica[c][0]==self.numReg+1:
                            self.sigReg=c
                            break
                        c=c+1
                    # Regla 6a
                    if self.sigReg!=-1:
                        self.a.pop(len(self.a)-1)
                        c=0
                        while c<len(self.gramatica):
                            if self.gramatica[c][1]==self.nomReg and self.gramatica[c][0]==self.numReg:
                                self.elim=len(self.gramatica[c][2])
                                break
                            c=c+1
                        c=0
                        while c<self.elim:
                            self.b.pop(0)
                            c=c+1
                        self.b=self.gramatica[self.sigReg][2]+self.b
                        self.a.append(self.nomReg+str(self.numReg+1))
                        self.ed='n'
                        print(" Regla 6a usada ")
                        print(self.ed,",",self.ind+1,",",self.a,",",self.b)
                    # Regla 6b
                    elif self.ind==0 and self.nomReg=='prinFin':
                        self.ed='e'
                        self.edcad=1
                        print(" Regla 6b usada ")
                        print(self.ed,",",self.ind+1,",",self.a,",",self.b)
                        print(" Cadena rechazada ")
                        
                        if self.indEror < self.long:
                            linea = self.linComp[self.indEror]
                            encontrado = " "+str(self.tokComp[self.indEror])+" "
                        else:
                            linea = self.linComp[len(self.linComp)-1]
                            encontrado = "fin de codigo"
                        # si falto el ; el error es de la linea de antes no de la q sigue
                        if ';' in self.esperados and self.indEror > 0 and self.indEror < self.long:
                            if self.linComp[self.indEror] != self.linComp[self.indEror-1]:
                                linea = self.linComp[self.indEror-1]
                        # si se esperaba End casi siempre es q falto cerrar
                        fiend = 0
                        c = 0
                        while c < len(self.esperados):
                            if self.esperados[c] == 'End':
                                fiend = 1
                            c = c + 1
                        if fiend == 1: # fiend es final con end es var nva
                            msg = "Error en linea "+str(linea)+": "+encontrado+" inesperado. Falta 'End' "
                            if self.indEror < self.long and self.tokComp[self.indEror] == '&&':
                                msg = msg + " (Los comentarios van despues de End )"
                            print(msg)
                        else:
                           
                            openc = 0
                            opsEsp = "" # solo los operadores q si se esperaban
                            tipoenc = 0
                            extr = []
                            c = 0
                            while c < len(self.esperados):
                                e = self.esperados[c]
                                if e=='+' or e=='-' or e=='*' or e=='/':
                                    openc = 1
                                elif e=='Ent' or e=='Dec' or e=='Ban' or e=='Sim' or e=='Sen':
                                    tipoenc = 1
                                else:
                                    rep = 0   # pa q no se repita
                                    d = 0
                                    while d < len(extr):
                                        if extr[d] == e:
                                            rep = 1
                                        d = d + 1
                                    if rep == 0:
                                        extr.append(e)
                                c = c + 1
                            # No pude arreglar el error deq cuando falta el ultimo token me de la otra linea
                            c = 0
                            while c < len(extr):
                                d = 0
                                while d < len(extr)-1:
                                    if extr[d] > extr[d+1]:
                                        aux = extr[d]
                                        extr[d] = extr[d+1]
                                        extr[d+1] = aux
                                    d = d + 1
                                c = c + 1
                            lista = []
                            # nota lo que sigue intenta corregir lo de esperar el siguiente en la pila b pero si no funciona pes regresamos a eso
                            #self.indErrorMax = self.ind
                            #self.msgErrorMax = ("Error en linea ",self.linComp[self.ind],": se encontró " + self.tokComp[self.ind]
                              #      + " pero se esperaba " + self.b[0] + " ") 
                            
                            if openc == 1:
                                ops = ['+','-','*','/']
                                c = 0
                                while c < len(ops):
                                    if ops[c] in self.esperados:
                                        if opsEsp == "":
                                            opsEsp = ops[c]
                                        else:
                                            opsEsp = opsEsp + ", " + ops[c]
                                    c = c + 1
                                lista.append("un operador (" + opsEsp + ")")
                            if tipoenc == 1:
                                lista.append("un tipo de dato (Ent, Dec, Ban, Sim, Sen)")
                            c = 0
                            while c < len(extr):
                                e = extr[c]
                                if e == 'VARIABLE':
                                    e = "una variable"
                                elif e == 'NUMERO':
                                    e = "un numero"
                                elif e == '"':
                                    e = 'una cadena (")'
                                elif e == '#':
                                    e = "fin de programa"
                                elif e == '&&':
                                    e = "un comentario (&&)"
                                else:
                                    e = "'"+e+"'"
                                lista.append(e)
                                c = c + 1
                            texto = ""
                            c = 0
                            while c < len(lista):
                                if c == 0:
                                    texto = lista[c]
                                else:
                                    texto = texto + ", " + lista[c]
                                c = c + 1
                            print("Error en linea "+str(linea)+": "+encontrado+" inesperado. Se esperaba "+texto)
                    # Regla 6c
                    else:
                        self.a.pop(len(self.a)-1)
                        c=0
                        while c<len(self.gramatica):
                            if self.gramatica[c][1]==self.nomReg and self.gramatica[c][0]==self.numReg:
                                self.elim=len(self.gramatica[c][2])
                                break
                            c=c+1
                        c=0
                        while c<self.elim:
                            self.b.pop(0)
                            c=c+1
                        self.b.insert(0,self.nomReg)
                        print(" Regla 6c usada ")
                        print(self.ed,",",self.ind+1,",",self.a,",",self.b)

class Semantico: # nO LO MUEVAS DE ARCHIVO, NECESITO LAS TABLAS DE ARRIBA
    def __init__(self,sinLex):
        self.linComp = sinLex.linComp
        self.sinLex = sinLex
        self.tok = sinLex.tok
        self.tiTok = sinLex.tiTok
        self.linTok = sinLex.linTok
        self.repTok = sinLex.repTok
        self.numero = sinLex.numero
        self.tokComp = sinLex.tokComp
        self.tipoVar=sinLex.tipoVar # la tabla de variables se llena aqui (analiSeman)
        self.varTipo= sinLex.varTipo # son las mismas listas del lexico pa q intermedio y optimizacion las vean
        self.linVar = sinLex.linVar
        self.pasos = []
        self.conValor = [] # variables q ya tienen valor
        self.valGuardados = {}
        self.valCad = {}

    #

    def posVar(self, nomV):
        # posicion de la variable en varTipo (la ultima si se repite), -1 si no esta
        pos = -1
        c = 0
        while c < len(self.varTipo):
            if self.varTipo[c] == nomV:
                pos = c
            c = c + 1
        return pos

    def esTipo(self, tk):
        if tk == "Ent" or tk == "Dec" or tk == "Ban" or tk == "Sim" or tk == "Sen":
            return 1
        return 0

    def esOper(self, tk):
        if tk == "+" or tk == "-" or tk == "*" or tk == "/":
            return 1
        return 0

    def soloLetras(self, tk):
        if len(tk) == 0:
            return 0
        c = 0
        while c < len(tk):
            if tk[c] not in self.sinLex.let:
                return 0
            c = c + 1
        return 1

    def hastaPuntoComa(self):
        # avanza self.ind hasta el ; (se queda parado en el ;)
        while self.ind < self.long and self.tokComp[self.ind] != ";":
            self.ind = self.ind + 1

    # 

    def analiSeman(self):
        self.errSeman = []
        self.ind = 0
        self.long = len(self.tokComp)
        # la tabla se arma conforme se van declarando, asi se sabe si algo se uso antes
        self.varTipo.clear()
        self.tipoVar.clear()
        self.linVar.clear()
        self.conValor = []
        self.valGuardados = {} # lo q vale cada var si se puede saber (pa dividir entre cero)
        self.valCad = {}

        # igual q en intermedio, voy sentencia por sentencia y segun como empieza
        # mando a su revision
        while self.ind < self.long:
            self.tokAct = self.tokComp[self.ind]
            self.linAct = self.linComp[self.ind]

            if self.tokAct == "Begin" or self.tokAct == "End" or self.tokAct == "&&":
                self.ind = self.ind + 1
            elif self.esTipo(self.tokAct) == 1:
                self.revisaDecl()
            elif self.tokAct == "Entrada":
                self.revisaEntrada()
            elif self.tokAct == "Salida":
                self.revisaSalida()
            elif self.posVar(self.tokAct) != -1:
                self.revisaVar()
            elif self.soloLetras(self.tokAct) == 1:
                self.errNoDeclarada(self.tokAct, "la variable " + self.tokAct + " no fue declarada, linea " + str(self.linAct))
                self.hastaPuntoComa()
                self.ind = self.ind + 1
            else:
                self.ind = self.ind + 1

        return self.errSeman

    def revisaDecl(self):
        # Ent a , b ; se meten a la tabla con su tipo y la linea, si ya estaba es duplicada
        tipo = self.tokAct
        self.ind = self.ind + 1
        while self.ind < self.long and self.tokComp[self.ind] != ";":
            nomV = self.tokComp[self.ind]
            if self.soloLetras(nomV) == 1:  # si el nombre esta mal ya lo marco el lexico
                if self.posVar(nomV) != -1:
                    self.errSeman.append("la variable " + nomV + " ya habia sido declarada antes, linea " + str(self.linComp[self.ind]))
                else:
                    self.varTipo.append(nomV)
                    self.tipoVar.append(tipo)
                    self.linVar.append(self.linComp[self.ind])
            self.ind = self.ind + 1
        self.ind = self.ind + 1

    def errNoDeclarada(self, nomV, msg):
        # si si se declara pero mas abajo lo digo, si no va el mensaje normal
        linDec = self.seDeclaraDespues(nomV)
        if linDec != -1:
            self.errSeman.append("la variable " + nomV + " se usa antes de declararse (se declara en la linea " + str(linDec) + "), linea " + str(self.linAct))
        else:
            self.errSeman.append(msg)

    def seDeclaraDespues(self, nomV):
        c = self.ind
        while c < self.long:
            if self.esTipo(self.tokComp[c]) == 1:
                d = c + 1
                while d < self.long and self.tokComp[d] != ";":
                    if self.tokComp[d] == nomV:
                        return self.linComp[d]
                    d = d + 1
            c = c + 1
        return -1

    def usaVar(self, nomV):
        # se esta leyendo nomV, tiene q tener valor antes
        if self.posVar(nomV) != -1 and nomV not in self.conValor:
            self.errSeman.append("la variable " + nomV + " se usa sin tener valor, linea " + str(self.linAct))

    def revisaEntrada(self):
        # Entrada x = "..." ; reviso q x exista y desde aqui ya tiene valor (pero no se sabe cual)
        self.ind = self.ind + 1
        if self.ind < self.long:
            self.nomV = self.tokComp[self.ind]
            self.decVarBus(self.nomV)
            if self.enc == 1 and self.nomV not in self.conValor:
                self.conValor.append(self.nomV)
            if self.nomV in self.valGuardados:
                self.valGuardados.pop(self.nomV)
        self.hastaPuntoComa()
        self.ind = self.ind + 1

    def revisaSalida(self):
        # Salida = "..." ;   Salida = "..." , x ;   Salida = "..." + x + ... ;
        self.ind = self.ind + 1
        if self.ind < self.long and self.tokComp[self.ind] == "=":
            self.ind = self.ind + 1
        if self.ind < self.long and self.tokComp[self.ind] == '"':
            self.ind = self.ind + 2
        if self.ind < self.long and self.tokComp[self.ind] == ",":
            self.ind = self.ind + 1
            if self.ind < self.long:
                self.decVarBus(self.tokComp[self.ind])
                self.usaVar(self.tokComp[self.ind])
            self.ind = self.ind + 1
        elif self.ind < self.long and self.tokComp[self.ind] == "+":
            inicio = self.ind
            self.hastaPuntoComa()
            self.checaVarsConcat(self.tokComp[inicio:self.ind])
        self.hastaPuntoComa()
        self.ind = self.ind + 1

    def revisaVar(self):
        # x = lo q sea ; saco lo de la derecha y lo reviso
        self.nomV = self.tokAct
        self.pos = self.posVar(self.nomV)
        self.tipoDest = self.tipoVar[self.pos]
        self.ind = self.ind + 1
        if self.ind < self.long and self.tokComp[self.ind] == "=":
            self.ind = self.ind + 1
        self.inicio = self.ind
        self.hastaPuntoComa()
        self.der = self.tokComp[self.inicio:self.ind]
        self.revisaAsig(self.nomV, self.tipoDest, self.der)
        self.guardaValor(self.nomV, self.der)
        if self.nomV not in self.conValor:
            self.conValor.append(self.nomV)
        self.ind = self.ind + 1

    def guardaValor(self, nomV, der):
        # lo q vale nomV si se puede calcular, igual q en el arbol (asi a = 5 - 5 ya se sabe q es 0)
        if nomV in self.valGuardados:
            self.valGuardados.pop(nomV)
        if len(der) == 0 or '"' in der or der[0] == "True" or der[0] == "False":
            return
        nodo = self.armaExpr(der)
        valor = nodo["valNum"]
        if valor != None:
            if self.tipoVar[self.posVar(nomV)] == "Ent":
                valor = round(valor)
            self.valGuardados[nomV] = valor

    def decVarBus(self, nomV):
        self.enc = 0
        if self.posVar(nomV) != -1:
            self.enc = 1
        if self.enc == 0:
            self.errNoDeclarada(nomV, "Error, variable " + nomV + " no declarada (linea " + str(self.linAct) + ")")

    def checaVarsConcat(self, lista):
        c = 0
        while c < len(lista):
            if lista[c] != '"' and lista[c] != '+':
                self.decVarBus(lista[c])
                self.usaVar(lista[c])
            c = c + 1

    def tipoTok(self, token):
        # tipo de lo q venga: variable o numero. Si el token esta mal escrito eso ya lo marco el lexico
        self.pos2 = self.posVar(token)
        if self.pos2 != -1:
            self.usaVar(token)
            return self.tipoVar[self.pos2]
        if len(token) > 0 and token[0] in self.sinLex.num:
            if '.' in token:
                return "Dec"
            return "Ent"
        if self.soloLetras(token) == 1:
            self.errNoDeclarada(token, token + " no fue declarada y se uso en linea " + str(self.linAct))
        return "error"

    def esCero(self, token):
        if len(token) == 0:
            return 0
        c = 0
        while c < len(token):
            if token[c] != '0' and token[c] != '.':
                return 0
            c = c + 1
        return 1

    def revisaAsig(self, nomV, tipoDest, der):
        if len(der) == 0:
            self.errSeman.append(nomV + " se quedo sin valor asignado, linea " + str(self.linAct))
            return

        if '"' in der:
            if tipoDest != "Sen" and tipoDest != "Sim":
                self.errSeman.append("no se puede meter una cadena en " + nomV + " (" + tipoDest + "), linea " + str(self.linAct))
            elif tipoDest == "Sim":
                # Sim es de un solo caracter, los espacios de las orillas no cuentan
                if len(der) == 2:
                    texto = self.textoCadena(self.inicio).strip()
                    if len(texto) != 1:
                        self.errSeman.append(nomV + " es Sim y solo guarda un caracter, se le quiso poner \"" + texto + "\", linea " + str(self.linAct))
                else:
                    self.errSeman.append(nomV + " es Sim y solo guarda un caracter, no se le puede poner una concatenacion, linea " + str(self.linAct))
            self.checaVarsConcat(der)
            return

        if der[0] == "True" or der[0] == "False":
            if tipoDest != "Ban":
                self.errSeman.append("no se puede meter un booleano en " + nomV + " (" + tipoDest + "), linea " + str(self.linAct))
            return

        if len(der) == 1:
            self.tipoVal = self.tipoTok(der[0])
            if self.tipoVal != "error":
                self.comparaTipo(nomV, tipoDest, self.tipoVal)
            return

        # ya es operacion, voy alternando: operando, operador, operando...
        self.tipoAcum = ""
        self.esperaOperando = 1
        self.opAnt = ""
        c = 0
        while c < len(der):
            tk = der[c]
            if self.esperaOperando == 0:
                if self.esOper(tk) == 0:
                    self.errSeman.append("faltó operador antes de " + tk + ", linea " + str(self.linAct))
                    return
                self.opAnt = tk
                self.esperaOperando = 1
            else:
                if self.opAnt == "/" and self.esCero(tk) == 1:
                    self.errSeman.append("division entre cero en la asignacion de " + nomV + ", linea " + str(self.linAct))
                    return
                if self.opAnt == "/" and tk in self.valGuardados and self.valGuardados[tk] == 0:
                    self.errSeman.append("division entre " + tk + " que vale 0, en la asignacion de " + nomV + ", linea " + str(self.linAct))
                    return
                self.tipoOp = self.tipoTok(tk)
                if self.tipoOp == "error":
                    return
                if self.tipoOp == "Sen" or self.tipoOp == "Ban" or self.tipoOp == "Sim":
                    self.errSeman.append(tk + " es " + self.tipoOp + ", no se puede operar, linea " + str(self.linAct))
                    return
                if self.tipoAcum == "" or self.tipoOp == "Dec":
                    self.tipoAcum = self.tipoOp
                self.esperaOperando = 0
            c = c + 1

        if self.esperaOperando == 1:
            self.errSeman.append("operacion incompleta en linea " + str(self.linAct))
            return

        self.comparaTipo(nomV, tipoDest, self.tipoAcum)

    def comparaTipo(self, nomV, tipoDest, tipoVal):
        if tipoDest == tipoVal:
            return
        if tipoDest == "Ent" and tipoVal == "Dec":
            self.errSeman.append(nomV + " es Ent y se le esta poniendo un decimal, se pierde info (linea " + str(self.linAct) + ")")
            return
        if tipoDest == "Dec" and tipoVal == "Ent":
            return  # Revisar que si mostar con .00 si es enteri
        self.errSeman.append("tipos no compatibles: " + nomV + " es " + tipoDest + " y se le quiso poner " + tipoVal + ", linea " + str(self.linAct))

    # ---------------- arboles ----------------

    def arbolSeman(self):
        self.arboles = []
        self.valGuardados = {}
        self.valCad = {} # valores de las cadenas, pa q se arrastren en concat
        self.ind = 0
        self.long = len(self.tokComp)
        while self.ind < self.long:
            tokAct = self.tokComp[self.ind]
            if self.esTipo(tokAct) == 1:
                # declaraciones no llevan arbol
                self.hastaPuntoComa()
                self.ind = self.ind + 1
            elif tokAct == "Entrada":
                self.arbolEntrada()
            elif tokAct == "Salida":
                self.arbolSalida()
            elif self.posVar(tokAct) != -1:
                self.arbolAsig(tokAct)
            else:
                self.ind = self.ind + 1
        return self.arboles

    def arbolEntrada(self):
        # el valor se pide al correr, ya no se sabe cuanto vale
        if self.ind + 1 < self.long:
            nomEnt = self.tokComp[self.ind + 1]
            if nomEnt in self.valGuardados:
                self.valGuardados.pop(nomEnt)
            if nomEnt in self.valCad:
                self.valCad.pop(nomEnt)
        self.hastaPuntoComa()
        self.ind = self.ind + 1

    def arbolSalida(self):
        # solo se grafica si es concatenacion: Salida = "a" + x + "b" ;
        self.ind = self.ind + 1
        if self.ind < self.long and self.tokComp[self.ind] == "=":
            self.ind = self.ind + 1
        inicio = self.ind
        self.hastaPuntoComa()
        der = self.tokComp[inicio:self.ind]
        if '"' in der and '+' in der:
            nodoConcat = self.armaConcat(der, inicio)
            self.arboles.append({"top": "salida", "left": "valor", "right": nodoConcat["right"],
                                 "hijos": [{"top": "Salida"}, {"top": "="}, nodoConcat]})
        self.ind = self.ind + 1

    def arbolAsig(self, nomVar):
        self.ind = self.ind + 1
        if self.ind < self.long and self.tokComp[self.ind] == "=":
            self.ind = self.ind + 1
        inicio = self.ind
        self.hastaPuntoComa()
        der = self.tokComp[inicio:self.ind]
        self.ind = self.ind + 1

        nodoVar = {"top": "nomVar", "left": "valor", "right": nomVar, "hijos": [{"top": nomVar}]}
        nodoIgual = {"top": "="}

        if len(der) == 0:
            return
        if len(der) == 2 and der[0] == '"' and der[1] == '"':
            # cadena sola: nombre = " Fernanda " , no se grafica solo se guarda
            self.valCad[nomVar] = self.textoCadena(inicio)
            return
        if '"' in der and '+' in der:
            nodoConcat = self.armaConcat(der, inicio)
            self.arboles.append({"top": "datoValor", "left": "valor", "right": nodoConcat["right"],
                                 "hijos": [nodoVar, nodoIgual, nodoConcat]})
            self.valCad[nomVar] = nodoConcat["valCad"] # ya junto, sin los +
            return
        if '"' in der or der[0] == "True" or der[0] == "False":
            return

        # operacion aritmetica
        nodoExpr = self.armaExpr(der)
        tipoVarDestino = "Ent"
        if self.posVar(nomVar) != -1:
            tipoVarDestino = self.tipoVar[self.posVar(nomVar)]

        valFinal = nodoExpr["valNum"]
        if valFinal != None and tipoVarDestino == "Ent":
            valFinal = round(valFinal)  # redondear solo al asginar auna var entera

        # solo grafico si hay operador, z = 21 no
        hayOper = 0
        c = 0
        while c < len(der):
            if self.esOper(der[c]) == 1:
                hayOper = 1
            c = c + 1
        if hayOper == 1:
            if valFinal != None:
                textoFinal = self.formatoNum(valFinal)
            else:
                textoFinal = nodoExpr["right"]
            self.arboles.append({"top": "operacion", "left": "valor", "right": textoFinal,
                                 "hijos": [nodoVar, nodoIgual, nodoExpr]})

        if valFinal != None:
            self.valGuardados[nomVar] = valFinal

    def armaExpr(self, der):
        # como en intermedio: primero una lista operando, operador, operando...
        # luego junto * y / , despues + y - , de izq a der
        self.expr = []
        k = 0
        while k < len(der):
            if len(self.expr) % 2 == 0:
                self.expr.append(self.armaOperando(der[k]))
            elif self.esOper(der[k]) == 1:
                self.expr.append(der[k])
            else:
                break # ya no viene operador, lo demas no entra
            k = k + 1
        if len(self.expr) % 2 == 0:
            self.expr.pop(len(self.expr)-1) # quedo un operador suelto al final

        # nivel 2, multiplicaciones y divisiones
        i = 1
        while i < len(self.expr):
            if self.expr[i] == "*" or self.expr[i] == "/":
                nodo = self.juntaTermino(self.expr[i-1], self.expr[i], self.expr[i+1])
                self.expr.pop(i+1)
                self.expr.pop(i)
                self.expr[i-1] = nodo
            else:
                i = i + 2

        # cada pedazo q quedo es un termino
        i = 0
        while i < len(self.expr):
            self.expr[i] = self.envuelve("termino", self.expr[i])
            i = i + 2

        # nivel 1, sumas y restas (ya solo quedan de esas)
        while len(self.expr) > 1:
            nodo = self.juntaExpr(self.expr[0], self.expr[1], self.expr[2])
            self.expr.pop(2)
            self.expr.pop(1)
            self.expr[0] = nodo

        return self.envuelve("expr", self.expr[0])

    def envuelve(self, top, nodo):
        # el nodo de arriba nomas copia lo de su hijo
        return {"top": top, "left": "valor", "right": nodo["right"],
                "valNum": nodo["valNum"], "tipoDat": nodo["tipoDat"], "hijos": [nodo]}

    def juntaTermino(self, izq, operador, der):
        valRes = None
        if izq["valNum"] != None and der["valNum"] != None:
            if operador == "*":
                valRes = izq["valNum"] * der["valNum"]
            elif der["valNum"] != 0:
                valRes = izq["valNum"] / der["valNum"]  # division real, pero se redondea al asginar
        if valRes != None:
            textoRes = self.formatoNum(valRes)
        else:
            textoRes = str(izq["right"]) + operador + str(der["right"])
        return {"top": "termino", "left": "valor", "right": textoRes,
                "valNum": valRes, "tipoDat": self.combinaTipo(izq["tipoDat"], der["tipoDat"]),
                "hijos": [izq, {"top": operador}, der]}

    def juntaExpr(self, izq, operador, der):
        valRes = None
        if izq["valNum"] != None and der["valNum"] != None:
            if operador == "+":
                valRes = izq["valNum"] + der["valNum"]
            else:
                valRes = izq["valNum"] - der["valNum"]
            textoRes = self.formatoNum(valRes)
        else:
            textoRes = str(izq["right"]) + operador + str(der["right"])
        return {"top": "expr", "left": "valor", "right": textoRes,
                "valNum": valRes, "tipoDat": self.combinaTipo(izq["tipoDat"], der["tipoDat"]),
                "hijos": [izq, {"top": operador}, der]}

    def armaOperando(self, tokAct):
        return self.envuelve("operando", self.armaHoja(tokAct))

    def armaHoja(self, tokAct):
        esNumero = 1
        tienePunto = 0
        if len(tokAct) == 0:
            esNumero = 0
        c = 0
        while c < len(tokAct):
            if tokAct[c] == '.':
                tienePunto = tienePunto + 1
            elif tokAct[c] not in self.sinLex.num:
                esNumero = 0
            c = c + 1
        if tienePunto > 1 or tokAct == '.':
            esNumero = 0 # tipo 3.4.5 , si no truena el float

        if esNumero == 1:
            if tienePunto == 1:
                valorNum = float(tokAct)
                tipoDat = "Dec"
            else:
                valorNum = int(tokAct)
                tipoDat = "Ent"
            return {"top": "numero", "left": "valor", "right": tokAct,
                    "valNum": valorNum, "tipoDat": tipoDat, "hijos": [{"top": tokAct}]}

        # si no es numero entonces es una variable
        tipoDat = "Ent"
        if self.posVar(tokAct) != -1:
            tipoDat = self.tipoVar[self.posVar(tokAct)]
        valorNum = None
        textoNodo = tokAct
        if tokAct in self.valGuardados:
            valorNum = self.valGuardados[tokAct]
            textoNodo = self.formatoNum(valorNum)
        return {"top": "nomVar", "left": "valor", "right": textoNodo,
                "valNum": valorNum, "tipoDat": tipoDat, "hijos": [{"top": tokAct}]}

    def combinaTipo(self, tipoIzq, tipoDer):
        if tipoIzq == "Dec" or tipoDer == "Dec":
            return "Dec"
        return "Ent"

    def formatoNum(self, valor):
        entero = int(valor)
        if entero == valor:
            return str(entero)
        return str(valor)

    def textoCadena(self, idxTok):
        # saca lo de adentro de la cadena q abre en tokComp[idxTok]
        # cuento cuantas comillas hay antes en la misma linea pa saber cual cadena es
        lin = self.linComp[idxTok]
        comillas = 0
        c = 0
        while c < idxTok:
            if self.tokComp[c] == '"' and self.linComp[c] == lin:
                comillas = comillas + 1
            c = c + 1
        textos = re.findall(r'"([^"]*)"', self.sinLex.lineas[lin - 1])
        if comillas // 2 < len(textos):
            return textos[comillas // 2]
        return ""

    def armaConcat(self, der, inicio):
        # separo der en elementos: cadena o variable, los + no
        elems = []
        i = 0
        while i < len(der):
            tk = der[i]
            if tk == '"':
                elems.append({"top": "cadena", "left": "valor", "right": self.textoCadena(inicio + i),
                              "hijos": [{"top": '"'}, {"top": '"'}]})
                i = i + 2
            elif tk == "+":
                i = i + 1
            else:
                # si ya se sabe lo q vale la variable pongo su valor, si no su nombre
                valor = tk
                if tk in self.valCad:
                    valor = self.valCad[tk]
                elif tk in self.valGuardados:
                    valor = self.formatoNum(self.valGuardados[tk])
                elems.append({"top": "nomVar", "left": "valor", "right": valor,
                              "hijos": [{"top": tk}]})
                i = i + 1

        if len(elems) == 0:
            return {"top": "concat", "left": "valor", "right": "", "valCad": "", "hijos": []}

        # segun la gramatica de concat
        if len(elems) == 1:
            hijos = [elems[0]]
        elif elems[0]["top"] == "cadena":
            # concat -> cadena + masCat
            hijos = [elems[0], {"top": "+"}, self.armaMasCat(elems[1:])]
        elif elems[1]["top"] == "cadena" and len(elems) == 2:
            # concat -> nomVar + cadena
            hijos = [elems[0], {"top": "+"}, elems[1]]
        elif elems[1]["top"] == "cadena":
            # concat -> nomVar + cadena + masCat
            hijos = [elems[0], {"top": "+"}, elems[1], {"top": "+"}, self.armaMasCat(elems[2:])]
        else:
            hijos = [elems[0], {"top": "+"}, self.armaMasCat(elems[1:])]

        textoRes = ""
        valJunto = "" # lo mismo pero pegado, pa guardarlo
        c = 0
        while c < len(elems):
            if c > 0:
                textoRes = textoRes + "+"
            textoRes = textoRes + elems[c]["right"]
            valJunto = valJunto + elems[c]["right"]
            c = c + 1

        return {"top": "concat", "left": "valor", "right": textoRes, "valCad": valJunto, "hijos": hijos}

    def armaMasCat(self, lista):
        # masCat -> elemCad | elemCad + masCat
        # lo armo de atras pa delante, el ultimo es el masCat mas chiquito
        k = len(lista) - 1
        elem = {"top": "elemCad", "left": "valor", "right": lista[k]["right"], "hijos": [lista[k]]}
        sig = {"top": "masCat", "left": "valor", "right": elem["right"], "hijos": [elem]}
        k = k - 1
        while k >= 0:
            elem = {"top": "elemCad", "left": "valor", "right": lista[k]["right"], "hijos": [lista[k]]}
            sig = {"top": "masCat", "left": "valor", "right": elem["right"] + "+" + sig["right"],
                   "hijos": [elem, {"top": "+"}, sig]}
            k = k - 1
        return sig

class Intermedio: # codigo intermedio, ocupa las tablas del lexico igual q semantico
    def __init__(self, sinLex):
        self.sinLex = sinLex
        self.lineas = sinLex.lineas
        self.tokComp = sinLex.tokComp
        self.linComp = sinLex.linComp
        self.varTipo = sinLex.varTipo
        self.opers = []
        self.limpia()

    def limpia(self):
        # operaciones de la expresion actual, en el orden q se resuelven
        self.oOpe = []
        self.oOp1 = []
        self.oOp2 = []
        # cuadruplos
        self.cuOpe = []
        self.cuOp1 = []
        self.cuOp2 = []
        self.cuAux = []
        # triplos
        self.lidir = []
        self.ope = []
        self.op1 = []
        self.op2 = []
        # codigo P
        self.codP = []
        # polaca, una fila cada q sale un operador
        self.polPila1 = []
        self.polPila2 = []
        self.polCad = []

    def tokeniza(self):
        # busco variable = ... ; en tokComp, igual q en el semantico
        self.opers = []
        self.ind = 0
        self.long = len(self.tokComp)
        while self.ind < self.long:
            tokAct = self.tokComp[self.ind]
            if tokAct in self.varTipo and self.ind + 1 < self.long and self.tokComp[self.ind + 1] == "=":
                nomV = tokAct
                lin = self.linComp[self.ind]
                self.ind = self.ind + 2
                der = []
                while self.ind < self.long and self.tokComp[self.ind] != ";":
                    der.append(self.tokComp[self.ind])
                    self.ind = self.ind + 1
                if self.esAritmetica(der) == 1:
                    self.opers.append([lin, nomV, der])
            self.ind = self.ind + 1
        return self.opers

    def esAritmetica(self, der):
        # solo las q llevan operador, cadenas y True/False no
        ban = 0
        c = 0
        while c < len(der):
            if der[c] == '"' or der[c] == "True" or der[c] == "False":
                return 0
            if self.esOper(der[c]) == 1:
                ban = 1
            c = c + 1
        return ban

    def generaCodigo(self):
        self.limpia()
        self.tokeniza()
        n = 0
        while n < len(self.opers):
            self.nomV = self.opers[n][1]
            self.toks = self.opers[n][2]
            self.sepTablas()
            self.armaOperaciones()
            self.cuadruplos()
            self.trio()
            self.polaca()
            self.armaPCode() # va despues de polaca pq sale de ahi
            n = n + 1

    def sepTablas(self):
        # raya entre expresion y expresion
        self.cuOpe.append("---")
        self.cuOp1.append("---")
        self.cuOp2.append("---")
        self.cuAux.append("---")
        self.lidir.append("---")
        self.ope.append("---")
        self.op1.append("---")
        self.op2.append("---")
        self.codP.append("---")
        self.polPila1.append("---")
        self.polPila2.append("---")
        self.polCad.append("---")

    def esOper(self, tk):
        if tk == "+" or tk == "-" or tk == "*" or tk == "/":
            return 1
        return 0

    def prioridad(self, oper):
        if oper == "*" or oper == "/":
            return 2
        if oper == "+" or oper == "-":
            return 1
        return 0 # el = siempre abajo

    def esAux(self, tk):
        # auxiliares v0, v1.. las variables no llevan numero asi q no se revuelven
        if len(tk) > 1 and tk[0] == "v" and tk[1] in self.sinLex.num:
            return 1
        return 0

    def armaOperaciones(self):
        # copio la expresion y la voy resolviendo, primero * y / y luego + y -
        # de izq a der, la q resuelvo la cambio por su auxiliar
        self.oOpe = []
        self.oOp1 = []
        self.oOp2 = []
        self.expr = []
        c = 0
        while c < len(self.toks):
            self.expr.append(self.toks[c])
            c = c + 1
        nivel = 2
        while nivel > 0:
            i = 0
            while i < len(self.expr):
                if self.esOper(self.expr[i]) == 1 and self.prioridad(self.expr[i]) == nivel:
                    aux = "v" + str(len(self.oOpe))
                    self.oOpe.append(self.expr[i])
                    self.oOp1.append(self.expr[i-1])
                    self.oOp2.append(self.expr[i+1])
                    self.expr.pop(i+1)
                    self.expr.pop(i)
                    self.expr[i-1] = aux
                    # no avanzo i, ahi ya quedo el sig operador
                else:
                    i = i + 1
            nivel = nivel - 1
        self.resFinal = self.expr[0]

    def cuadruplos(self):
        c = 0
        while c < len(self.oOpe):
            self.cuOpe.append(self.oOpe[c])
            self.cuOp1.append(self.oOp1[c])
            self.cuOp2.append(self.oOp2[c])
            self.cuAux.append("v" + str(c))
            c = c + 1
        # asignacion final
        self.cuOpe.append("=")
        self.cuOp1.append(self.resFinal)
        self.cuOp2.append("")
        self.cuAux.append(self.nomV)

    def trio(self):
        c = 0
        while c < len(self.oOpe):
            self.lidir.append("[" + str(c) + "]")
            self.ope.append(self.oOpe[c])
            self.op1.append(self.aDir(self.oOp1[c]))
            self.op2.append(self.aDir(self.oOp2[c]))
            c = c + 1
        self.lidir.append("[" + str(c) + "]")
        self.ope.append("=")
        self.op1.append(self.aDir(self.resFinal))
        self.op2.append(self.nomV)

    def aDir(self, tk):
        # v0 se cambia por [0]
        if self.esAux(tk) == 1:
            return "[" + tk[1:] + "]"
        return tk

    def polaca(self):
        # pila1 operandos y pila2 operadores, lo q ya salio queda como # en pila1
        # pilaTex lleva lo q vale cada cosa de pila1 ya en polaca
        self.pila1 = [self.nomV] # la variable destino hasta abajo
        self.pilaTex = [self.nomV]
        self.pilaVer = [self.nomV] # esta es la q se ve en la tabla
        self.pila2 = ["="]
        i = 0
        while i < len(self.toks):
            tk = self.toks[i]
            if self.esOper(tk) == 1:
                while self.prioridad(self.pila2[len(self.pila2)-1]) >= self.prioridad(tk):
                    self.sacaPolaca()
                self.pila2.append(tk)
            else:
                self.pila1.append(tk)
                self.pilaTex.append(tk)
                self.pilaVer.append(tk)
            i = i + 1
        # vacio lo q quedo, el = sale al ultimo
        while len(self.pila2) > 0:
            self.sacaPolaca()
        self.cadena = self.pilaTex[0]

    def sacaPolaca(self):
        # guardo como estaban las pilas antes de sacar
        self.polPila1.append(self.textoPila(self.pila1))
        self.polPila2.append(self.textoPila(self.pila2))
        oper = self.pila2.pop(len(self.pila2)-1)
        seg = self.pilaTex.pop(len(self.pilaTex)-1) # el de arriba es el segundo
        pri = self.pilaTex.pop(len(self.pilaTex)-1)
        self.pilaTex.append(pri + " " + seg + " " + oper)
        # en la tabla va como salen de la pila, primero el de arriba
        # asi el destino queda al final: 2 5 * x =
        # si los dos ya eran resultados (#) van en el orden q salieron, izq a der
        segV = self.pilaVer.pop(len(self.pilaVer)-1)
        priV = self.pilaVer.pop(len(self.pilaVer)-1)
        if self.pila1[len(self.pila1)-1] == "#" and self.pila1[len(self.pila1)-2] == "#":
            self.pilaVer.append(priV + " " + segV + " " + oper)
        else:
            self.pilaVer.append(segV + " " + priV + " " + oper)
        self.pila1.pop(len(self.pila1)-1)
        self.pila1.pop(len(self.pila1)-1)
        self.pila1.append("#")
        # la cadena es todo lo q ya salio, en orden de abajo pa arriba
        cad = ""
        c = 0
        while c < len(self.pila1):
            if self.pila1[c] == "#":
                if cad != "":
                    cad = cad + " "
                cad = cad + self.pilaVer[c]
            c = c + 1
        self.polCad.append(cad)

    def textoPila(self, pila):
        # la pila sin los #
        texto = ""
        c = 0
        while c < len(pila):
            if pila[c] != "#":
                if texto != "":
                    texto = texto + " "
                texto = texto + pila[c]
            c = c + 1
        return texto

    def armaPCode(self):
        # sale de pilaTex (x ... =) no de la tabla, pa q no se volteen los operandos
        partes = self.cadena.split(" ")
        self.codP.append("lda " + partes[0] + ";")
        c = 1
        while c < len(partes):
            tk = partes[c]
            if tk == "=":
                self.codP.append("sto;")
            elif tk == "+":
                self.codP.append("adi;")
            elif tk == "-":
                self.codP.append("sbi;")
            elif tk == "*":
                self.codP.append("mpi;")
            elif tk == "/":
                self.codP.append("div;")
            else:
                self.cargaOperando(tk)
            c = c + 1

    def cargaOperando(self, tk):
        if tk[0] in self.sinLex.num:
            self.codP.append("ldc " + tk + ";")
        else:
            self.codP.append("lod " + tk + ";")



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