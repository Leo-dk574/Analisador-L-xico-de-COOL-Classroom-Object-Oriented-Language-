import Lexico

def mensagemErro(token, token_esperado):
    print(f"Esperado {token_esperado} mas recebeu um {token["valor"]} do tipo {token["tipo"]} na linha:{Lexico.num_linha}")

def sintaticoExpr():
    erro, token = ExprAtribuicao()
    return erro, token


def ExprAtribuicao():
    erro, token = ExprNotLogical()
    if erro: return True, token

    proximo = Lexico.peek()

    if(proximo["valor"] == "<-"):
        
        if(token["tipo"] != "ID"):
            mensagemErro(token, "ID para atribuição")
            return True, token
    
        token = Lexico.lexico()
        erro, token = sintaticoExpr()
        return erro, token

    return False, token


def ExprNotLogical():
    proximo = Lexico.peek()

    if(proximo["valor"] == "not"):
        token = Lexico.lexico()
        return sintaticoExpr()
    
    return ExprComparacao()

def ExprComparacao():
    erro, token = ExprSomaSub()
    if erro: return True, token

    proximo = Lexico.peek()

    if(proximo["valor"] in ["<", "<=", "="]):
        token = Lexico.lexico()
        
        return ExprSomaSub()

    return False, token

def ExprSomaSub():
    erro, token = ExprMultDiv()
    if erro: return True, token

    proximo = Lexico.peek()

    while(proximo["valor"] in ["+", "-"]):
        token = Lexico.lexico()
        erro, token = ExprMultDiv()
        if erro: return True, token
        proximo = Lexico.peek()

    return False, token


def ExprMultDiv():
    erro, token = ExprIsvoidNeg()
    if erro: return True, token

    proximo = Lexico.peek()

    while(proximo["valor"] in ["/", "*"]):
        token = Lexico.lexico()
        
        erro, token = ExprIsvoidNeg()
        if erro: return True, token
        proximo = Lexico.peek()

    return False, token


def ExprIsvoidNeg():
    proximo = Lexico.peek()

    if(proximo["valor"] in ["isvoid", "~"]):
        token = Lexico.lexico()
        return ExprIsvoidNeg()

    return ExprDispatch()


def ExprDispatch():
    erro, token = ExprAtomo()
    if erro: return True, token

    proximo = Lexico.peek()
    
    # Enquanto houver . ou @, continuamos no loop
    while proximo["valor"] in [".", "@"]:
        # Caso 1: Dispatch Estático (obj@TYPE.id)
        if proximo["valor"] == "@":
            token = Lexico.lexico()
            token = Lexico.lexico()
            if token["tipo"] != "TYPE":
                mensagemErro(token, "TYPE")
                return True, token
            
            # Depois do @, o manual exige um ponto obrigatoriamente
            proximo = Lexico.peek()
            if proximo["valor"] != ".":
                mensagemErro(proximo, ".")
                return True, proximo

        # Caso 2: O Ponto (independente de ter tido @ antes)
        if proximo["valor"] == ".":
            token = Lexico.lexico()
            token = Lexico.lexico()
            if token["tipo"] != "ID":
                mensagemErro(token, "ID do método")
                return True, token
            
            if Lexico.peek()["valor"] != "(":
                mensagemErro(Lexico.peek(), "(")
                return True, Lexico.peek()
            
            erro, token_erro = validarArgumentosChamada()
            if erro: return True, token_erro
            
        proximo = Lexico.peek()
        
    return False, token
        

def validarArgumentosChamada():
    Lexico.lexico() # Consome o "("
    
    if Lexico.peek()["valor"] != ")": # Se não for fechamento imediato, tem expr
        while True:
            erro, _ = ExprAtribuicao() # Valida uma expressão (argumento)
            if erro: return True, _
            
            if Lexico.peek()["valor"] == ",":
                Lexico.lexico() # Consome a vírgula e continua o loop
            else:
                break # Sai do loop se não houver mais vírgulas
                
    token = Lexico.lexico()
    if token["valor"] != ")":
        mensagemErro(token, ")")
        return True, token
        
    return False, token

def ExprAtomo():
    return True, "A"