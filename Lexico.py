global num_linha
num_linha = 1

global f

global c
c = ' '

global prox_token
prox_token = None

def arquivoOpen(nome):
    global f
    f = open(nome)


def tipador(palavra):
    print(palavra)
    token = {
        "tipo": "Tipo",
        "valor": palavra
    }
    if(palavra == "Fim do Arquivo"):
        token["tipo"] = "EOF"
        return token
    if(palavra[0]=='\"'):
        token["tipo"] = "String"
    if(palavra.isdecimal()):
        token["tipo"] = "Numero"
    if(palavra in ["+","-","<","<=","=>","<-","*","/","~","="]):
        token["tipo"] = "Operador"
    if(palavra in "{}();:~+-*/=.,@"):
        token["tipo"] = "Delimitador"
    if(palavra.lower() in ["class","inherits","if","then","fi","while","loop","pool","let","in","case","of","esac","new","isvoid","not","true","false"]):
        token["tipo"] = "PR"
        token["valor"] = token["valor"].lower()
    if(palavra[0].isupper()):
        token["tipo"] = "TYPE"
    if(token["tipo"] == "Tipo"):
        token["tipo"] = "ID"
    return token

# PR, Class, String, Numero, Operador, Variavel, Delimitator


def lexico():
    global prox_token
    if prox_token is not None:
        token = prox_token
        prox_token = None
        return token

    global c
    global f
    global num_linha
    palavra = ""
    lemos_aspas = False
    comentario = False
    comentario_linha = False
    while(True):
        if c == '\n':
            if comentario_linha:
                comentario_linha = False
            num_linha += 1
        if c in "{}();:~+-*/=.,@" and not lemos_aspas and (not comentario and not comentario_linha):
            if c == '=':
                aux2 = f.read(1)
                if aux2 == '>':
                    c = c+aux2
                else:
                    f.seek(f.tell()-1,0)

            aux = c
            c = ' '
            return tipador(aux)
        else:
            c = f.read(1)
            if not c: 
                return tipador("Fim do Arquivo")
            if c in '(-' or (c == '*' and comentario):
                aux = f.read(1)
                if aux in '*-' or (aux == ')' and comentario):
                    if c == '-' and aux == '-':
                        comentario_linha = True
                    else:
                        comentario = not comentario
                    c = ' '
                    aux = ' '
                else:
                    f.seek(f.tell()-1,0)
            if c == '<':
                aux = f.read(1)
                if aux == '-' or aux == '=':
                    if palavra != '':
                        f.seek(f.tell()-2,0)
                        return tipador(palavra)
                    else:
                        return tipador(c+aux)
                else:
                    if palavra != '':
                        f.seek(f.tell()-2,0)
                        return tipador(palavra)
                    else:
                        f.seek(f.tell()-1,0)
                        return tipador(c)
            if not comentario and not comentario_linha:
                if c == '"':
                    lemos_aspas = not lemos_aspas
                if c not in " '\t''\n'{}();:~+-*/=.,@" or lemos_aspas:
                    palavra += c
                else:
                    if palavra != "":
                        return tipador(palavra)
                

def peek():
    global prox_token
    if prox_token is None:
        prox_token = lexico()
    return prox_token