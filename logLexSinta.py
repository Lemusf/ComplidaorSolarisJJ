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
        self.tipoVar=[] # Agg para semantico tipo Dato
        self.varTipo= [] # Agg semantico variable 
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
                    if ban == 0:
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
            linea = self.lineas[self.nLinea - 1]
            variables = linea.split(maxsplit=1)[1].replace(";", "").split(",")

            for variable in variables:
                variable = variable.strip()
                self.varTipo.append(variable)
                self.tipoVar.append(token)

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
        while self.edcad==0:
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
                                lista.append("un operador (+, -, *, /)")
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
        self.tipoVar=sinLex.tipoVar # Agg para semantico tipo Dato
        self.varTipo= sinLex.varTipo # Agg semantico variable 
        self.pasos = []
        self.nomVarConVal = []
        self.valVarConVal = []
        # Hay qu4 agregar listas para los tipos de varuables y hay que agregar lo de los 
        # operadores
        # TU en tu def recuerda poner la tabla fija JUAN

    def analiSeman(self):
        self.errSeman = []
        self.ind = 0
        self.long = len(self.tokComp)

        self.checaDuplic()

        while self.ind < self.long:
            self.tokAct = self.tokComp[self.ind]
            self.linAct = self.linComp[self.ind]

            if self.tokAct == "Begin" or self.tokAct == "End":
                self.ind = self.ind + 1
                continue

            if self.tokAct == "&&":
                self.ind = self.ind + 1
                continue

            if self.tokAct == "Ent" or self.tokAct == "Dec" or self.tokAct == "Ban" or self.tokAct == "Sim" or self.tokAct == "Sen":
                # 
                while self.tokComp[self.ind] != ";":
                    self.ind = self.ind + 1
                self.ind = self.ind + 1
                continue

            if self.tokAct == "Entrada":
                self.ind = self.ind + 1
                self.nomV = self.tokComp[self.ind]
                self.decVarBus(self.nomV)   # solo revisa que la variable exista
                # lo de las comillas se ignora, no hay ejecución, no se valida tipo
                while self.ind < self.long and self.tokComp[self.ind] != ";":
                    self.ind = self.ind + 1
                self.ind = self.ind + 1
                continue

            if self.tokAct == "Salida":
                self.ind = self.ind + 1
                if self.tokComp[self.ind] == "=":
                    self.ind = self.ind + 1
                if self.tokComp[self.ind] == '"':
                    self.ind = self.ind + 2
                if self.ind < self.long and self.tokComp[self.ind] == ",":
                    self.ind = self.ind + 1
                    self.decVarBus(self.tokComp[self.ind])
                    self.ind = self.ind + 1
                elif self.ind < self.long and self.tokComp[self.ind] == "+":
                    inicio = self.ind
                    while self.ind < self.long and self.tokComp[self.ind] != ";":
                        self.ind = self.ind + 1
                    self.checaVarsConcat(self.tokComp[inicio:self.ind])
                while self.ind < self.long and self.tokComp[self.ind] != ";":
                    self.ind = self.ind + 1
                self.ind = self.ind + 1
                continue

            self.esVar = 0
            c = 0
            while c < len(self.varTipo):
                if self.varTipo[c] == self.tokAct:
                    self.esVar = 1
                c = c + 1

            if self.esVar == 1:
                self.nomV = self.tokAct
                self.pos = 0
                c = 0
                while c < len(self.varTipo):
                    if self.varTipo[c] == self.nomV:
                        self.pos = c
                    c = c + 1
                self.tipoDest = self.tipoVar[self.pos]
                self.ind = self.ind + 1
                if self.tokComp[self.ind] == "=":
                    self.ind = self.ind + 1
                self.inicio = self.ind
                while self.tokComp[self.ind] != ";":
                    self.ind = self.ind + 1
                self.der = self.tokComp[self.inicio:self.ind]
                self.revisaAsig(self.nomV, self.tipoDest, self.der)
                self.guardaValorSiSeSabe(self.nomV, self.der)
                self.ind = self.ind + 1
                continue

            self.pareceVar = 1
            if len(self.tokAct) == 0:
                self.pareceVar = 0
            c = 0
            while c < len(self.tokAct):
                if self.tokAct[c] not in self.sinLex.let:
                    self.pareceVar = 0
                c = c + 1

            if self.pareceVar == 1:
                self.errSeman.append("la variable " + self.tokAct + " no fue declarada, linea " + str(self.linAct))
                while self.ind < self.long and self.tokComp[self.ind] != ";":
                    self.ind = self.ind + 1
                self.ind = self.ind + 1
                continue

            self.ind = self.ind + 1

        return self.errSeman

    def guardaValorSiSeSabe(self, nomV, der):
        if len(der) != 1:
            return
        tok = der[0]
        if self.esCero(tok) == 1:
            yaEsta = -1
            c = 0
            while c < len(self.nomVarConVal):
                if self.nomVarConVal[c] == nomV:
                    yaEsta = c
                c = c + 1
            if yaEsta != -1:
                self.valVarConVal[yaEsta] = 0
            else:
                self.nomVarConVal.append(nomV)
                self.valVarConVal.append(0)
        else:
            c = 0
            while c < len(self.nomVarConVal):
                if self.nomVarConVal[c] == nomV:
                    self.valVarConVal[c] = -999
                c = c + 1

    def valorVarEsCero(self, nomV):
        c = 0
        while c < len(self.nomVarConVal):
            if self.nomVarConVal[c] == nomV and self.valVarConVal[c] == 0:
                return 1
            c = c + 1
        return 0

    def checaDuplic(self):
        self.yaVistas = []
        c = 0
        while c < len(self.varTipo):
            nomV = self.varTipo[c]
            rep = 0
            d = 0
            while d < len(self.yaVistas):
                if self.yaVistas[d] == nomV:
                    rep = 1
                d = d + 1
            if rep == 1:
                self.linDup = self.buscaLineaDup(nomV, c)
                self.errSeman.append("la variable " + nomV + " ya habia sido declarada antes, linea " + str(self.linDup))
            else:
                self.yaVistas.append(nomV)
            c = c + 1

    def buscaLineaDup(self, nomV, posEnVarTipo):
        vistoTok = 0
        i = 0
        while i < len(self.tokComp):
            if self.tokComp[i] == nomV:
                vistoTok = vistoTok + 1
                if vistoTok == posEnVarTipo + 1:
                    return self.linComp[i]
            i = i + 1
        return self.linComp[len(self.linComp) - 1]

    def decVarBus(self, nomV):
        self.enc = 0
        c = 0
        while c < len(self.varTipo):
            if self.varTipo[c] == nomV:
                self.enc = 1
            c = c + 1
        if self.enc == 0:
            self.errSeman.append("Error, variable " + nomV + " no declarada (linea " + str(self.linAct) + ")")

    def checaVarsConcat(self, lista):
        c = 0
        while c < len(lista):
            tk = lista[c]
            if tk != '"' and tk != '+':
                self.decVarBus(tk)
            c = c + 1

    def tipoTok(self, token):
        self.pos2 = -1
        c = 0
        while c < len(self.varTipo):
            if self.varTipo[c] == token:
                self.pos2 = c
            c = c + 1
        if self.pos2 != -1:
            return self.tipoVar[self.pos2]

        self.esNum = 1
        self.tienePunto = 0
        c = 0
        while c < len(token):
            car = token[c]
            if car == '.':
                self.tienePunto = 1
            elif car not in self.sinLex.num:
                self.esNum = 0
            c = c + 1
        if self.esNum == 1 and len(token) > 0:
            if self.tienePunto == 1:
                return "Dec"
            return "Ent"

        self.esLetra = 1
        c = 0
        while c < len(token):
            if token[c] not in self.sinLex.let:
                self.esLetra = 0
            c = c + 1
        if self.esLetra == 1 and len(token) > 0:
            self.errSeman.append(token + " no fue declarada y se uso en linea " + str(self.linAct))
            return "error"

        print("token raro en operacion: ", token)  # esto casi no deberia pasar pero por si las dudas
        self.errSeman.append("token invalido " + token + " en linea " + str(self.linAct))
        return "error"

    def esCero(self, token):
        if len(token) == 0:
            return 0
        c = 0
        while c < len(token):
            car = token[c]
            if car != '0' and car != '.':
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
            self.checaVarsConcat(der)
            return

        if der[0] == "True" or der[0] == "False":
            if tipoDest != "Ban":
                self.errSeman.append("no se puede meter un booleano en " + nomV + " (" + tipoDest + "), linea " + str(self.linAct))
            return

        if len(der) == 1:
            self.tipoVal = self.tipoTok(der[0])
            if self.tipoVal == "error":
                return
            self.comparaTipo(nomV, tipoDest, self.tipoVal)
            return

        # aqui ya es operacion con opSuma/opMul
        self.tipoAcum = ""
        self.esperaOperando = 1
        self.opAnt = ""
        c = 0
        while c < len(der):
            tk = der[c]
            if self.esperaOperando == 1:
                if self.opAnt == "/":
                    if self.esCero(tk) == 1:
                        self.errSeman.append("division entre cero en la asignacion de " + nomV + ", linea " + str(self.linAct))
                        return
                    if self.valorVarEsCero(tk) == 1:
                        self.errSeman.append("division entre " + tk + " que vale 0, en la asignacion de " + nomV + ", linea " + str(self.linAct))
                        return
                self.tipoOp = self.tipoTok(tk)
                if self.tipoOp == "error":
                    return
                if self.tipoOp == "Sen" or self.tipoOp == "Ban" or self.tipoOp == "Sim":
                    self.errSeman.append(tk + " es " + self.tipoOp + ", no se puede operar, linea " + str(self.linAct))
                    return
                if self.tipoAcum == "":
                    self.tipoAcum = self.tipoOp
                if self.tipoOp == "Dec":
                    self.tipoAcum = "Dec"
                self.esperaOperando = 0
            else:
                if tk != "+" and tk != "-" and tk != "*" and tk != "/":
                    self.errSeman.append("faltó operador antes de " + tk + ", linea " + str(self.linAct))
                    return
                self.opAnt = tk
                self.esperaOperando = 1
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

    def arbolSeman(self):
        self.arboles = []
        self.valGuardados = {}
        ind = 0
        largo = len(self.tokComp)
        while ind < largo:
            tokAct = self.tokComp[ind]

            # Para ignoarar las declaraciones, mas de una variable en una linea
            if tokAct == "Ent" or tokAct == "Dec" or tokAct == "Ban" or tokAct == "Sim" or tokAct == "Sen":
                while ind < largo and self.tokComp[ind] != ";":
                    ind = ind + 1
                ind = ind + 1
                continue

            # Salida con concatenacion: Salida = "a" + x + "b";
            if tokAct == "Salida":
                ind = ind + 1
                if ind < largo and self.tokComp[ind] == "=":
                    ind = ind + 1
                inicio = ind
                while ind < largo and self.tokComp[ind] != ";":
                    ind = ind + 1
                der = self.tokComp[inicio:ind]
                if '"' in der and '+' in der:
                    nodoConcat = self.armaConcat(der, inicio)
                    nodoSal = {"top": "salida", "left": "valor", "right": nodoConcat["right"],
                               "hijos": [{"top": "Salida"}, {"top": "="}, nodoConcat]}
                    self.arboles.append(nodoSal)
                ind = ind + 1
                continue

            esVarDec = 0
            c = 0
            while c < len(self.varTipo):
                if self.varTipo[c] == tokAct:
                    esVarDec = 1
                    break
                c = c + 1

            if esVarDec == 1:
                nomVar = tokAct
                ind = ind + 1
                if ind < largo and self.tokComp[ind] == "=":
                    ind = ind + 1
                inicio = ind
                while ind < largo and self.tokComp[ind] != ";":
                    ind = ind + 1
                der = self.tokComp[inicio:ind]

                nodoVar = {"top": "nomVar", "left": "valor", "right": nomVar,
                           "hijos": [{"top": nomVar}]}
                nodoIgual = {"top": "="}

                # Asignacion con concatenacion: x = "a" + y;
                if len(der) > 0 and '"' in der and '+' in der:
                    nodoConcat = self.armaConcat(der, inicio)
                    nodoDato = {"top": "datoValor", "left": "valor", "right": nodoConcat["right"],
                                "hijos": [nodoVar, nodoIgual, nodoConcat]}
                    self.arboles.append(nodoDato)

                # Asignacion aritmetica (como ya la tenias)
                elif len(der) > 0 and '"' not in der and der[0] != "True" and der[0] != "False":
                    self.posDer = 0
                    self.tokDer = der
                    nodoExpr = self.armaExpr()

                    # buscar el tipo declarado de la variable final o a la que se le asigna
                    tipoVarDestino = "Ent"
                    c = 0
                    while c < len(self.varTipo):
                        if self.varTipo[c] == nomVar:
                            tipoVarDestino = self.tipoVar[c]
                        c = c + 1

                    valFinal = nodoExpr["valNum"]
                    if valFinal != None and tipoVarDestino == "Ent":
                        valFinal = round(valFinal)  # redondear solo al asginar auna var entera

                    nodoOper = {"top": "operacion", "left": "valor",
                                "right": self.formatoNum(valFinal) if valFinal != None else nodoExpr["right"],
                                "hijos": [nodoVar, nodoIgual, nodoExpr]}
                    self.arboles.append(nodoOper)

                    if valFinal != None:
                        self.valGuardados[nomVar] = valFinal

                ind = ind + 1
                continue

            ind = ind + 1

        return self.arboles

    def armaExpr(self):
        izq = self.armaTermino()

        while self.posDer < len(self.tokDer) and (self.tokDer[self.posDer] == "+" or self.tokDer[self.posDer] == "-"):
            operador = self.tokDer[self.posDer]
            self.posDer = self.posDer + 1
            der = self.armaTermino()

            tipoRes = self.combinaTipo(izq["tipoDat"], der["tipoDat"])

            if izq["valNum"] != None and der["valNum"] != None:
                if operador == "+":
                    valRes = izq["valNum"] + der["valNum"]
                else:
                    valRes = izq["valNum"] - der["valNum"]
                textoRes = self.formatoNum(valRes)
            else:
                valRes = None
                textoRes = str(izq["right"]) + operador + str(der["right"])

            izq = {"top": "expr", "left": "valor", "right": textoRes,
                   "valNum": valRes, "tipoDat": tipoRes,
                   "hijos": [izq, {"top": operador}, der]}

        return {"top": "expr", "left": "valor", "right": izq["right"],
                "valNum": izq["valNum"], "tipoDat": izq["tipoDat"], "hijos": [izq]}

    def armaTermino(self):
        izq = self.armaOperando()

        while self.posDer < len(self.tokDer) and (self.tokDer[self.posDer] == "*" or self.tokDer[self.posDer] == "/"):
            operador = self.tokDer[self.posDer]
            self.posDer = self.posDer + 1
            der = self.armaOperando()

            tipoRes = self.combinaTipo(izq["tipoDat"], der["tipoDat"])
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

            izq = {"top": "termino", "left": "valor", "right": textoRes,
                   "valNum": valRes, "tipoDat": tipoRes,
                   "hijos": [izq, {"top": operador}, der]}

        return {"top": "termino", "left": "valor", "right": izq["right"],
                "valNum": izq["valNum"], "tipoDat": izq["tipoDat"], "hijos": [izq]}

    def armaOperando(self):
        tokAct = self.tokDer[self.posDer]
        self.posDer = self.posDer + 1
        hoja = self.armaHoja(tokAct)
        return {"top": "operando", "left": "valor", "right": hoja["right"],
                "valNum": hoja["valNum"], "tipoDat": hoja["tipoDat"], "hijos": [hoja]}

    def armaHoja(self, tokAct):
        esNumero = 1
        if len(tokAct) == 0:
            esNumero = 0
        c = 0
        while c < len(tokAct):
            car = tokAct[c]
            if car not in self.sinLex.num and car != '.':
                esNumero = 0
            c = c + 1

        if esNumero == 1:
            tienePunto = 0
            c = 0
            while c < len(tokAct):
                if tokAct[c] == '.':
                    tienePunto = 1
                c = c + 1

            if tienePunto == 1:
                valorNum = float(tokAct)
                tipoDat = "Dec"
            else:
                valorNum = int(tokAct)
                tipoDat = "Ent"

            return {"top": "numero", "left": "valor", "right": tokAct,
                    "valNum": valorNum, "tipoDat": tipoDat,
                    "hijos": [{"top": tokAct}]}

        # si no es numero entonces es una variable
        tipoDat = "Ent"
        c = 0
        while c < len(self.varTipo):
            if self.varTipo[c] == tokAct:
                tipoDat = self.tipoVar[c]
            c = c + 1

        valorNum = None
        if tokAct in self.valGuardados:
            valorNum = self.valGuardados[tokAct]

        if valorNum == None:
            textoNodo = tokAct
        else:
            textoNodo = self.formatoNum(valorNum)

        return {"top": "nomVar", "left": "valor", "right": textoNodo,
                "valNum": valorNum, "tipoDat": tipoDat,
                "hijos": [{"top": tokAct}]}

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
        # saca el contenido de la cadena cuya comilla de apertura esta en tokComp[idxTok]
        lin = self.linComp[idxTok]
        comillas = 0
        c = 0
        while c < idxTok:
            if self.tokComp[c] == '"' and self.linComp[c] == lin:
                comillas = comillas + 1
            c = c + 1
        pos = comillas // 2
        textos = re.findall(r'"([^"]*)"', self.sinLex.lineas[lin - 1])
        if pos < len(textos):
            return textos[pos]
        return ""

    def armaConcat(self, der, inicio):
        # separa der en elementos: cadena o variable
        elems = []
        i = 0
        while i < len(der):
            tk = der[i]
            if tk == '"':
                texto = self.textoCadena(inicio + i)
                elems.append({"top": "cadena", "left": "valor", "right": texto,
                              "hijos": [{"top": '"'}, {"top": '"'}]})
                i = i + 2
            elif tk == "+":
                i = i + 1
            else:
                elems.append({"top": "nomVar", "left": "valor", "right": tk,
                              "hijos": [{"top": tk}]})
                i = i + 1

        if len(elems) == 0:
            return {"top": "concat", "left": "valor", "right": "", "hijos": []}

        e0 = elems[0]
        resto = elems[1:]

        if len(resto) == 0:
            hijos = [e0]
        elif e0["top"] == "cadena":
            # concat -> cadena + masCat
            hijos = [e0, {"top": "+"}, self.armaMasCat(resto)]
        elif resto[0]["top"] == "cadena" and len(resto) == 1:
            # concat -> nomVar + cadena
            hijos = [e0, {"top": "+"}, resto[0]]
        elif resto[0]["top"] == "cadena":
            # concat -> nomVar + cadena + masCat
            hijos = [e0, {"top": "+"}, resto[0], {"top": "+"}, self.armaMasCat(resto[1:])]
        else:
            hijos = [e0, {"top": "+"}, self.armaMasCat(resto)]

        textoRes = ""
        c = 0
        while c < len(elems):
            if c > 0:
                textoRes = textoRes + "+"
            textoRes = textoRes + elems[c]["right"]
            c = c + 1

        return {"top": "concat", "left": "valor", "right": textoRes, "hijos": hijos}

    def armaMasCat(self, lista):
        elem = {"top": "elemCad", "left": "valor", "right": lista[0]["right"],
                "hijos": [lista[0]]}
        if len(lista) == 1:
            return {"top": "masCat", "left": "valor", "right": elem["right"], "hijos": [elem]}
        sig = self.armaMasCat(lista[1:])
        return {"top": "masCat", "left": "valor", "right": elem["right"] + "+" + sig["right"],
                "hijos": [elem, {"top": "+"}, sig]}

class Intermedio:
    def __init__(self, sinLex):
        self.sinLex = sinLex
        self.lineas = sinLex.lineas
        self.varTipo = sinLex.varTipo
        self.opers = []     

    def tokeniza(self):
        self.opers = []
        n = 0
        while n < len(self.lineas):
            linea = self.lineas[n]
            pos = linea.find('&&')
            if pos != -1:
                linea = linea[:pos]         
            sents = linea.split(';')
            s = 0
            while s < len(sents):
                sent = sents[s]
                if '=' in sent:
                    partes = sent.split('=', 1)
                    nomV = partes[0].strip()
                    der = partes[1].strip()
                    if nomV in self.varTipo and self.esAritmetica(der) == 1:
                        self.opers.append([n + 1, nomV, self.tokenizaOp(der)])
                s = s + 1
            n = n + 1
        return self.opers

    def esAritmetica(self, der):
        if '"' in der:
            return 0
        if der == "True" or der == "False":
            return 0
        c = 0
        while c < len(der):
            if der[c] == '+' or der[c] == '-' or der[c] == '*' or der[c] == '/':
                return 1
            c = c + 1
        return 0

    def tokenizaOp(self, texto):
        toks = []
        i = 0
        while i < len(texto):
            car = texto[i]
            if car.isspace():
                i = i + 1
            elif car == '+' or car == '-' or car == '*' or car == '/':
                toks.append(car)
                i = i + 1
            else:
                j = i
                while j < len(texto) and (texto[j].isalnum() or texto[j] == '.'):
                    j = j + 1
                if j == i:
                    toks.append(car)         
                    i = i + 1
                else:
                    toks.append(texto[i:j])
                    i = j
        return toks
    def trio(self):
        self.lidir=[]
        self.ope=[]
        self.op1=[]
        self.op2=[]
        
class Intermedio:
    def __init__(self, sinLex):
        self.sinLex = sinLex
        self.lineas = sinLex.lineas
        self.varTipo = sinLex.varTipo
        self.opers = []
        # operaciones de la expresion q estoy procesando (en orden de evaluacion)
        self.oOpe = []
        self.oOp1 = []
        self.oOp2 = []
        # cuadruplos
        self.cuOpe = []
        self.cuOp1 = []
        self.cuOp2 = []
        self.cuAux = []
        # triplos (las listas q ya tenia en trio)
        self.lidir = []
        self.ope = []
        self.op1 = []
        self.op2 = []
        # codigo P
        self.codP = []
        # notacion polaca, una fila cada vez q se saca un operador
        self.polPila1 = []
        self.polPila2 = []
        self.polCad = []

    def tokeniza(self):
        self.opers = []
        n = 0
        while n < len(self.lineas):
            linea = self.lineas[n]
            pos = linea.find('&&')
            if pos != -1:
                linea = linea[:pos]         
            sents = linea.split(';')
            s = 0
            while s < len(sents):
                sent = sents[s]
                if '=' in sent:
                    partes = sent.split('=', 1)
                    nomV = partes[0].strip()
                    der = partes[1].strip()
                    if nomV in self.varTipo and self.esAritmetica(der) == 1:
                        self.opers.append([n + 1, nomV, self.tokenizaOp(der)])
                s = s + 1
            n = n + 1
        return self.opers

    def esAritmetica(self, der):
        if '"' in der:
            return 0
        if der == "True" or der == "False":
            return 0
        c = 0
        while c < len(der):
            if der[c] == '+' or der[c] == '-' or der[c] == '*' or der[c] == '/':
                return 1
            c = c + 1
        return 0

    def tokenizaOp(self, texto):
        toks = []
        i = 0
        while i < len(texto):
            car = texto[i]
            if car.isspace():
                i = i + 1
            elif car == '+' or car == '-' or car == '*' or car == '/':
                toks.append(car)
                i = i + 1
            else:
                j = i
                while j < len(texto) and (texto[j].isalnum() or texto[j] == '.'):
                    j = j + 1
                if j == i:
                    toks.append(car)         
                    i = i + 1
                else:
                    toks.append(texto[i:j])
                    i = j
        return toks

    def generaCodigo(self):
        # aqui junto todo, cada expresion pasa por las 4 representaciones
        self.tokeniza()
        n = 0
        while n < len(self.opers):
            self.nomV = self.opers[n][1]
            self.toks = self.opers[n][2]
            self.sepTablas()
            self.armaOperaciones()
            self.cuadruplos()
            self.trio()
            self.armaPCode()
            self.polaca()
            n = n + 1

    def sepTablas(self):
        # una raya entre expresion y expresion
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
        return 0   # el = va hasta abajo de la pila

    def esAux(self, tk):
        # los auxiliares son v0, v1... las variables no llevan numeros asi q no se confunden
        if len(tk) > 1 and tk[0] == "v" and tk[1] in self.sinLex.num:
            return 1
        return 0

    def armaOperaciones(self):
        # pila de operandos y pila de operadores, si el de arriba tiene prioridad
        # mayor o igual al q llega, sale primero (asi sale de izquierda a derecha)
        self.oOpe = []
        self.oOp1 = []
        self.oOp2 = []
        self.pilaOp = []
        self.pilaOr = []
        i = 0
        while i < len(self.toks):
            tk = self.toks[i]
            if self.esOper(tk) == 1:
                while len(self.pilaOr) > 0 and self.prioridad(self.pilaOr[len(self.pilaOr)-1]) >= self.prioridad(tk):
                    self.sacaOperacion()
                self.pilaOr.append(tk)
            else:
                self.pilaOp.append(tk)
            i = i + 1
        while len(self.pilaOr) > 0:
            self.sacaOperacion()
        # lo unico q queda en la pila es el resultado final
        self.resFinal = self.pilaOp[len(self.pilaOp)-1]

    def sacaOperacion(self):
        oper = self.pilaOr.pop(len(self.pilaOr)-1)
        seg = self.pilaOp.pop(len(self.pilaOp)-1)    # el de arriba es el segundo operando
        pri = self.pilaOp.pop(len(self.pilaOp)-1)
        aux = "v" + str(len(self.oOpe))
        self.oOpe.append(oper)
        self.oOp1.append(pri)
        self.oOp2.append(seg)
        self.pilaOp.append(aux)    # el resultado se vuelve a meter como auxiliar

    def cuadruplos(self):
        c = 0
        while c < len(self.oOpe):
            self.cuOpe.append(self.oOpe[c])
            self.cuOp1.append(self.oOp1[c])
            self.cuOp2.append(self.oOp2[c])
            self.cuAux.append("v" + str(c))
            c = c + 1
        # la asignacion final
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
        # si es un auxiliar (v0) lo cambio por su direccion ([0])
        if self.esAux(tk) == 1:
            return "[" + tk[1:] + "]"
        return tk

    def armaPCode(self):
        self.codP.append("lda " + self.nomV + ";")
        c = 0
        while c < len(self.oOpe):
            self.cargaOperando(self.oOp1[c])
            self.cargaOperando(self.oOp2[c])
            if self.oOpe[c] == "+":
                self.codP.append("adi;")
            elif self.oOpe[c] == "-":
                self.codP.append("sbi;")
            elif self.oOpe[c] == "*":
                self.codP.append("mpi;")
            else:
                self.codP.append("div;")
            c = c + 1
        self.codP.append("sto;")

    def cargaOperando(self, tk):
        # los auxiliares ya estan en la pila, solo cargo variables y constantes
        if self.esAux(tk) == 1:
            return
        if tk[0] in self.sinLex.num:
            self.codP.append("ldc " + tk + ";")
        else:
            self.codP.append("lod " + tk + ";")

    def polaca(self):
        # pila1 = operandos, pila2 = operadores, la cadena es lo q se va sacando
        self.pila1 = [self.nomV]     # la variable destino va hasta abajo
        self.pila2 = ["="]
        self.cadena = ""
        i = 0
        while i < len(self.toks):
            tk = self.toks[i]
            if self.esOper(tk) == 1:
                # el = tiene prioridad 0 asi q nunca sale aqui
                while self.prioridad(self.pila2[len(self.pila2)-1]) >= self.prioridad(tk):
                    self.sacaPolaca()
                self.pila2.append(tk)
            else:
                self.pila1.append(tk)
            i = i + 1
        # al final se vacian las pilas, el = sale hasta el ultimo
        while len(self.pila2) > 0:
            self.sacaPolaca()

    def sacaPolaca(self):
        # primero guardo como estan las pilas antes de sacar
        self.polPila1.append(self.textoPila(self.pila1))
        self.polPila2.append(self.textoPila(self.pila2))
        oper = self.pila2.pop(len(self.pila2)-1)
        texto = ""
        # el operador saca sus dos operandos (el de arriba primero)
        # el # es un resultado q ya salio antes, ese no se vuelve a escribir
        k = 0
        while k < 2:
            tk = self.pila1.pop(len(self.pila1)-1)
            if tk != "#":
                texto = texto + tk + " "
            k = k + 1
        texto = texto + oper + " "
        self.pila1.append("#")
        self.cadena = self.cadena + texto
        self.polCad.append(self.cadena.strip())

    def textoPila(self, pila):
        # para mostrar la pila sin los #
        texto = ""
        c = 0
        while c < len(pila):
            if pila[c] != "#":
                if texto != "":
                    texto = texto + " "
                texto = texto + pila[c]
            c = c + 1
        return texto