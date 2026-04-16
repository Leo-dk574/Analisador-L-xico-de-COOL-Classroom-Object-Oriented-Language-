import Lexico

def mensagemErro(token, token_esperado):
    print(f"Esperado {token_esperado} mas recebeu um {token["valor"]} do tipo {token["tipo"]} na linha:{Lexico.num_linha}")

def sintaticoExpr():
    print("Entrou no Expr")
    chaves = 1
    token = {
        "tipo": "",
        "valor": ""
    }
    while(token["tipo"] != "EOF"):
        token = Lexico.lexico()
        if(token["valor"] == '{'):
            chaves = chaves + 1
        if(token["valor"] == '}'):
            chaves = chaves - 1
        if(chaves == 0):
            return False, token


def sintaticoFormal():
    print("Entrou no Formal")
    token = {
        "tipo": "",
        "valor": ""
    }
    first_formal = True
    token = Lexico.lexico()
    while(token["valor"] not in ")"):
        if(first_formal):
            if(token["tipo"] == "ID"):
                token = Lexico.lexico()
                if(token["valor"] == ":"):
                    token = Lexico.lexico()
                    if(token["tipo"] == "TYPE"):
                        token = Lexico.lexico()
                        first_formal = False
                    else:
                        mensagemErro(token, "TYPE")
                        return True, token
                else:
                    mensagemErro(token, ":")
                    return True, token
            else:
                mensagemErro(token, "ID")
                return True, token
        else:
            token = Lexico.lexico()
            if(token["valor"] == ","):
                token = Lexico.lexico()         
                if(token["tipo"] == "ID"):
                    token = Lexico.lexico()
                    if(token["valor"] == ":"):
                        token = Lexico.lexico()
                        if(token["tipo"] == "TYPE"):
                            token = Lexico.lexico()
                        else:
                            mensagemErro(token, "TYPE")
                            return True, token
                    else:
                        mensagemErro(token, ":")
                        return True, token
                else:
                    mensagemErro(token, "ID")
                    return True, token
            else:
                mensagemErro(token, ",")
                return True, token
    if(token["valor"] == ")"):
        return False, token
    else:
        return True, token


def sintaticoFeature(token):
    print("Entrou no Feature")
    if(token["tipo"] == "ID"):
        token = Lexico.lexico()
        if(token["valor"] == "("):
            erro, token = sintaticoFormal()
            if(not erro):
                token = Lexico.lexico()
                if(token["valor"] == ":"):
                    token = Lexico.lexico()
                    if(token["tipo"] == "TYPE"):
                        token = Lexico.lexico()
                        if(token["valor"] == "{"):
                            erro, token = sintaticoExpr();
                            if(not erro):
                                if(token["valor"] == '}'): #mudar para }
                                    return False, token
                                else:
                                    mensagemErro(token, "}")
                                    return True, token
                            else:
                                return True, token
                        else:
                            return True, token
                    else:
                        return True, token
                else:
                    return True, token
            else:
                return True, token
        else:
            return True, token, "("
    else:
        return True, token, "ID"
    

def sintaticoClass():
    print("Entrou na Class")
    token = {
        "tipo":"",
        "valor":""
    }
    token = Lexico.lexico()
    if(token["valor"] == "class"):
        token = Lexico.lexico()
        if(token["tipo"] == "TYPE"):
            token = Lexico.lexico()
            if(token["valor"] == "inherits"):
                token = Lexico.lexico()
                if(token["tipo"] == "TYPE"):
                    token = Lexico.lexico()
                else:
                    mensagemErro(token, "TYPE")
                    return False
            if(token["valor"] == '{'):
                token = Lexico.lexico()
                while(token["valor"] not in "}"):
                    erro, token = sintaticoFeature(token);
                    if(not erro):
                        token = Lexico.lexico()
                        if(token["valor"] == ";"):
                            token = Lexico.lexico()
                        else:
                            mensagemErro(token, ";")
                            return False
                    else:
                        return False
                if(token["valor"] == '}'):
                    return True
                mensagemErro(token, '}')
                return False
            mensagemErro(token, "{")
            return False
        else:
            mensagemErro(token, "TYPE")
            return False
    else:
        mensagemErro(token, "class")
        return False

def sintaticoProgram():
    print("Entrou no Program")
    token = {
        "tipo":"",
        "valor":""
    }
    while(token["tipo"] != "EOF"):
        if(not sintaticoClass()):
            print(f"Erro na Class")
            break
        print("Terminou Class")
        token = Lexico.lexico()
        if(token["valor"] != ';' and token["tipo"] != "EOF"):
            print(f"Esperado ; mas encontrou {token["valor"]} na linha:{Lexico.num_linha}")
            break
        

def sintatico():
    token = {
        "tipo": "",
        "valor": ""
    }
    while(token["tipo"] != "EOF"):
        token = Lexico.lexico()
        print(f"{token["valor"]}   {token["tipo"]}   n:{Lexico.num_linha}")
