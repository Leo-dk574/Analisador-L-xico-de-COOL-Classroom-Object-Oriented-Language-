import Lexico

def get_classe_contexto(ambiente):
    curr = ambiente
    while curr is not None:
        if hasattr(curr, "getClasse") and curr.getClasse():
            c = curr.getClasse()
            return c.nome if hasattr(c, "nome") else c
        curr = getattr(curr, "pai", None)
    return "Main"

def eh_subtipo(tipo_A, tipo_B, ambiente=None):
    classe_atual = get_classe_contexto(ambiente)
        
    if tipo_A == "SELF_TYPE": tipo_A = classe_atual
    if tipo_B == "SELF_TYPE": tipo_B = classe_atual
    
    if tipo_A == tipo_B: return True
    if tipo_B == "Object": return True

    # 100% Rigoroso, sem Wildcard/Coringa!
    import Sintatico
    descritor = Sintatico.descritor
    
    atual = descritor.buscarClasse(tipo_A)
    while atual is not None:
        if atual.pai == tipo_B: return True
        if atual.pai is None: break
        atual = descritor.buscarClasse(atual.pai)
        
    return False

def mensagemErro(token, token_esperado):
    print(f"Erro Sintático: Esperado '{token_esperado}' mas recebeu '{token['valor']}' do tipo {token['tipo']}")

def sintaticoExpr(ambiente):
    return ExprAtribuicao(ambiente)

def ExprAtribuicao(ambiente):
    erro, token, tipo_dir = ExprNotLogical(ambiente)
    if erro: return True, token, "Object"

    proximo = Lexico.peek()
    if proximo["valor"] == "<-":
        if token["tipo"] != "ID":
            mensagemErro(token, "ID para atribuição")
            return True, token, "Object"
    
        nome_id = token["valor"]
        
        tipo_id = ambiente.buscarPai(nome_id)
        if tipo_id is None:
            print(f"Erro Semântico: Variável '{nome_id}' não declarada neste escopo.")
            return True, token, "Object"

        Lexico.lexico() 
        erro, token, tipo_expr = sintaticoExpr(ambiente)
        if erro: return True, token, "Object"

        if not eh_subtipo(tipo_expr, tipo_id, ambiente):
            print(f"Erro Semântico: Não é possível atribuir '{tipo_expr}' à variável '{nome_id}' (tipo esperado: '{tipo_id}')")
            return True, token, "Object"

        return False, token, tipo_expr

    return False, token, tipo_dir

def ExprNotLogical(ambiente):
    proximo = Lexico.peek()
    if proximo["valor"] == "not":
        Lexico.lexico() 
        erro, token, tipo_expr = sintaticoExpr(ambiente)
        if erro: return True, token, "Object"
        
        if tipo_expr != "Bool":
            print(f"Erro Semântico: Operador 'not' espera tipo 'Bool', recebeu '{tipo_expr}'")
            return True, token, "Object"
            
        return False, token, "Bool"
    return ExprComparacao(ambiente)

def ExprComparacao(ambiente):
    erro, token, tipo_esq = ExprSomaSub(ambiente)
    if erro: return True, token, "Object"

    proximo = Lexico.peek()
    if proximo["valor"] in ["<", "<=", "="]:
        op = proximo["valor"]
        Lexico.lexico() 
        
        erro, token, tipo_dir = ExprSomaSub(ambiente)
        if erro: return True, token, "Object"

        if op in ["<", "<="]:
            if tipo_esq != "Int" or tipo_dir != "Int":
                print(f"Erro Semântico: Operador '{op}' só pode ser aplicado entre inteiros.")
                return True, token, "Object"
        else: 
            if tipo_esq in ["Int", "Bool", "String"] or tipo_dir in ["Int", "Bool", "String"]:
                if tipo_esq != tipo_dir:
                    print(f"Erro Semântico: Comparação ilícita (tipos básicos estáticos) entre '{tipo_esq}' e '{tipo_dir}'.")
                    return True, token, "Object"

        return False, token, "Bool"

    return False, token, tipo_esq

def ExprSomaSub(ambiente):
    erro, token, tipo_esq = ExprMultDiv(ambiente)
    if erro: return True, token, "Object"

    proximo = Lexico.peek()
    while proximo["valor"] in ["+", "-"]:
        op = proximo["valor"]
        Lexico.lexico() 
        
        erro, token, tipo_dir = ExprMultDiv(ambiente)
        if erro: return True, token, "Object"
        
        if tipo_esq != "Int" or tipo_dir != "Int":
            print(f"Erro Semântico: Operador '{op}' exige operandos 'Int'. Recebeu '{tipo_esq}' e '{tipo_dir}'.")
            return True, token, "Object"
            
        tipo_esq = "Int" 
        proximo = Lexico.peek()

    return False, token, tipo_esq

def ExprMultDiv(ambiente):
    erro, token, tipo_esq = ExprIsvoidNeg(ambiente)
    if erro: return True, token, "Object"

    proximo = Lexico.peek()
    while proximo["valor"] in ["/", "*"]:
        op = proximo["valor"]
        Lexico.lexico() 
        
        erro, token, tipo_dir = ExprIsvoidNeg(ambiente)
        if erro: return True, token, "Object"
        
        if tipo_esq != "Int" or tipo_dir != "Int":
            print(f"Erro Semântico: Operador '{op}' exige operandos 'Int'.")
            return True, token, "Object"
            
        tipo_esq = "Int"
        proximo = Lexico.peek()

    return False, token, tipo_esq

def ExprIsvoidNeg(ambiente):
    proximo = Lexico.peek()
    if proximo["valor"] in ["isvoid", "~"]:
        op = proximo["valor"]
        Lexico.lexico() 
        
        erro, token, tipo_expr = ExprIsvoidNeg(ambiente)
        if erro: return True, token, "Object"
        
        if op == "~":
            if tipo_expr != "Int":
                print(f"Erro Semântico: Negação '~' exige tipo 'Int', recebeu '{tipo_expr}'.")
                return True, token, "Object"
            return False, token, "Int"
        
        if op == "isvoid":
            return False, token, "Bool"

    return ExprDispatch(ambiente)

def ExprDispatch(ambiente):
    erro, token, tipo_alvo = ExprAtomo(ambiente)
    if erro: return True, token, "Object"

    proximo = Lexico.peek()
    while proximo["valor"] in [".", "@", "("]:

        if proximo["valor"] == "@":
            Lexico.lexico() 
            token_type = Lexico.lexico()
            if token_type["tipo"] != "TYPE":
                mensagemErro(token_type, "TYPE")
                return True, token_type, "Object"
            tipo_alvo = token_type["valor"]

            proximo = Lexico.peek()
            if proximo["valor"] != ".":
                mensagemErro(proximo, ".")
                return True, proximo, "Object"

        if proximo["valor"] == ".":
            Lexico.lexico() 
            token_metodo = Lexico.lexico()
            if token_metodo["tipo"] != "ID":
                mensagemErro(token_metodo, "ID do método")
                return True, token_metodo, "Object"

            if Lexico.peek()["valor"] != "(":
                mensagemErro(Lexico.peek(), "(")
                return True, Lexico.peek(), "Object"

            erro, token_erro, tipos_args = validarArgumentosChamada(ambiente)
            if erro: return True, token_erro, "Object"
            
            import Sintatico
            descritor = Sintatico.descritor
            
            classe_real = tipo_alvo
            if tipo_alvo == "SELF_TYPE":
                classe_real = get_classe_contexto(ambiente)
                
            classe_obj = descritor.buscarClasse(classe_real)
            if classe_obj is not None:
                metodo = classe_obj.buscarMetodoPai(token_metodo["valor"], descritor)
                if metodo is not None:
                    if len(metodo.parametros) != len(tipos_args):
                        print(f"Erro Semântico: '{token_metodo['valor']}' requer {len(metodo.parametros)} args, mas recebeu {len(tipos_args)}.")
                        return True, token_metodo, "Object"
                    
                    for i, (t_esp, t_pass) in enumerate(zip(metodo.parametros, tipos_args)):
                        if not eh_subtipo(t_pass, t_esp, ambiente):
                            print(f"Erro Semântico: Arg {i+1} de '{token_metodo['valor']}' deve ser subtipo de '{t_esp}', mas recebeu '{t_pass}'.")
                            return True, token_metodo, "Object"

                    tipo_alvo = classe_real if metodo.tipo == "SELF_TYPE" else metodo.tipo
                else:
                    print(f"Erro Semântico: Método '{token_metodo['valor']}' não existe em '{classe_real}'")
                    return True, token_metodo, "Object"
            else:
                print(f"Erro Semântico: Tentativa de acessar método em classe indefinida '{classe_real}'.")
                return True, token_metodo, "Object"

        if proximo["valor"] == "(":
            erro, token_erro, tipos_args = validarArgumentosChamada(ambiente)
            if erro: return True, token_erro, "Object"
            
            nome_metodo = token["valor"]
            import Sintatico
            descritor = Sintatico.descritor
            classe_real = get_classe_contexto(ambiente)
                
            classe_obj = descritor.buscarClasse(classe_real)
            if classe_obj is not None:
                metodo = classe_obj.buscarMetodoPai(nome_metodo, descritor)
                if metodo is not None:
                    if len(metodo.parametros) != len(tipos_args):
                        print(f"Erro Semântico: '{nome_metodo}' requer {len(metodo.parametros)} args, recebeu {len(tipos_args)}.")
                        return True, token_erro, "Object"
                    
                    for i, (t_esp, t_pass) in enumerate(zip(metodo.parametros, tipos_args)):
                        if not eh_subtipo(t_pass, t_esp, ambiente):
                            print(f"Erro Semântico: Arg {i+1} implícito de '{nome_metodo}' deve ser '{t_esp}', recebeu '{t_pass}'.")
                            return True, token_erro, "Object"

                    tipo_alvo = classe_real if metodo.tipo == "SELF_TYPE" else metodo.tipo
                else:
                    print(f"Erro Semântico: Método implícito '{nome_metodo}' indefinido.")
                    return True, token_erro, "Object"
            else:
                return True, token_erro, "Object"

        proximo = Lexico.peek()
            
    return False, token, tipo_alvo
        
def validarArgumentosChamada(ambiente):
    Lexico.lexico() # Consome "("
    tipos_encontrados = []
    
    if Lexico.peek()["valor"] != ")": 
        while True:
            erro, t_erro, tipo_arg = sintaticoExpr(ambiente) 
            if erro: return True, t_erro, []
            tipos_encontrados.append(tipo_arg)
            
            if Lexico.peek()["valor"] == ",":
                Lexico.lexico() 
            else:
                break 
                
    token = Lexico.lexico()
    if token["valor"] != ")":
        mensagemErro(token, ")")
        return True, token, []
        
    return False, token, tipos_encontrados

def ExprAtomo(ambiente):
    proximo = Lexico.peek()

    if proximo["tipo"] == "ID":
        token = Lexico.lexico()
        nome_id = token["valor"]
        
        if nome_id == "self":
            return False, token, "SELF_TYPE"
            
        tipo_encontrado = ambiente.buscarPai(nome_id)
        if tipo_encontrado is None:
            if Lexico.peek()["valor"] == "(":
                return False, token, "Object" 
            print(f"Erro Semântico: Identificador '{nome_id}' não definido neste escopo.")
            return True, token, "Object"
            
        return False, token, tipo_encontrado

    if proximo["tipo"] == "Numero": return False, Lexico.lexico(), "Int"
    if proximo["tipo"] == "String": return False, Lexico.lexico(), "String"
    if proximo["valor"] in ["true", "false"]: return False, Lexico.lexico(), "Bool"

    if proximo["valor"] == "(":
        Lexico.lexico()  
        erro, token, tipo_expr = sintaticoExpr(ambiente)
        if erro: return True, token, "Object"
        token_fecha = Lexico.lexico()
        if token_fecha["valor"] != ")":
            mensagemErro(token_fecha, ")")
            return True, token_fecha, "Object"
        return False, token_fecha, tipo_expr

    if proximo["valor"] == "if":
        Lexico.lexico() 
        erro, token, tipo_cond = sintaticoExpr(ambiente)
        if erro: return True, token, "Object"
        if tipo_cond != "Bool":
            print(f"Erro Semântico: Condição do 'if' deve ser 'Bool', não '{tipo_cond}'.")
            return True, token, "Object"

        token_then = Lexico.lexico()
        if token_then["valor"] != "then":
            mensagemErro(token_then, "then")
            return True, token_then, "Object"

        erro, token, tipo_then = sintaticoExpr(ambiente)
        if erro: return True, token, "Object"

        token_else = Lexico.lexico()
        if token_else["valor"] != "else":
            mensagemErro(token_else, "else")
            return True, token_else, "Object"

        erro, token, tipo_else = sintaticoExpr(ambiente)
        if erro: return True, token, "Object"

        token_fi = Lexico.lexico()
        if token_fi["valor"] != "fi":
            mensagemErro(token_fi, "fi")
            return True, token_fi, "Object"

        if eh_subtipo(tipo_then, tipo_else, ambiente):
            tipo_retorno = tipo_else
        elif eh_subtipo(tipo_else, tipo_then, ambiente):
            tipo_retorno = tipo_then
        else:
            tipo_retorno = "Object"
            
        return False, token_fi, tipo_retorno

    if proximo["valor"] == "while":
        Lexico.lexico()  
        erro, token, tipo_cond = sintaticoExpr(ambiente)
        if erro: return True, token, "Object"
        if tipo_cond != "Bool":
            print("Erro Semântico: Condição do 'while' deve ser 'Bool'.")
            return True, token, "Object"

        token_loop = Lexico.lexico()
        if token_loop["valor"] != "loop":
            mensagemErro(token_loop, "loop")
            return True, token_loop, "Object"

        erro, token, _ = sintaticoExpr(ambiente)
        if erro: return True, token, "Object"

        token_pool = Lexico.lexico()
        if token_pool["valor"] != "pool":
            mensagemErro(token_pool, "pool")
            return True, token_pool, "Object"
        return False, token_pool, "Object"

    if proximo["valor"] == "{":
        Lexico.lexico()  
        tipo_bloco = "Object"
        while True:
            erro, token, tipo_bloco = sintaticoExpr(ambiente)
            if erro: return True, token, "Object"

            token_pv = Lexico.lexico()
            if token_pv["valor"] != ";":
                mensagemErro(token_pv, ";")
                return True, token_pv, "Object"

            if Lexico.peek()["valor"] == "}":
                break

        token_fecha = Lexico.lexico()
        if token_fecha["valor"] != "}":
            mensagemErro(token_fecha, "}")
            return True, token_fecha, "Object"

        return False, token_fecha, tipo_bloco

    if proximo["valor"] == "new":
        Lexico.lexico()  
        token_type = Lexico.lexico()
        if token_type["tipo"] != "TYPE":
            mensagemErro(token_type, "TYPE")
            return True, token_type, "Object"
            
        tipo = token_type["valor"]
        import Sintatico
        if tipo != "SELF_TYPE" and Sintatico.descritor.buscarClasse(tipo) is None:
            print(f"Erro Semântico: Instanciação de classe indefinida '{tipo}'.")
            return True, token_type, "Object"

        return False, token_type, tipo

    if proximo["valor"] == "let":
        Lexico.lexico() 
        from Semantico.Ambiente import Ambiente
        ambiente_let = Ambiente(ambiente)

        while True:
            token_id = Lexico.lexico()
            if token_id["tipo"] != "ID":
                mensagemErro(token_id, "ID")
                return True, token_id, "Object"

            token_dp = Lexico.lexico()
            if token_dp["valor"] != ":":
                mensagemErro(token_dp, ":")
                return True, token_dp, "Object"

            token_type = Lexico.lexico()
            if token_type["tipo"] != "TYPE":
                mensagemErro(token_type, "TYPE")
                return True, token_type, "Object"

            nome_var = token_id["valor"]
            tipo_var = token_type["valor"]
            
            import Sintatico
            if tipo_var != "SELF_TYPE" and Sintatico.descritor.buscarClasse(tipo_var) is None:
                print(f"Erro Semântico: Tipo indefinido '{tipo_var}' na declaração do let.")
                return True, token_type, "Object"
            
            ambiente_let.addVariavel(nome_var, tipo_var)

            if Lexico.peek()["valor"] == "<-":
                Lexico.lexico()
                erro, token, tipo_inicializacao = sintaticoExpr(ambiente_let)
                if erro: return True, token, "Object"
                
                if not eh_subtipo(tipo_inicializacao, tipo_var, ambiente_let):
                    print(f"Erro Semântico: let '{nome_var}' não pode receber tipo '{tipo_inicializacao}'. Esperado '{tipo_var}'.")
                    return True, token, "Object"

            if Lexico.peek()["valor"] == ",":
                Lexico.lexico()
                continue
            else:
                break

        token_in = Lexico.lexico()
        if token_in["valor"] != "in":
            mensagemErro(token_in, "in")
            return True, token_in, "Object"

        erro, token, tipo_corpo_let = sintaticoExpr(ambiente_let)
        if erro: return True, token, "Object"
        return False, token, tipo_corpo_let

    if proximo["valor"] == "case":
        Lexico.lexico()  
        erro, token, tipo_cond = sintaticoExpr(ambiente)
        if erro: return True, token, "Object"

        token_of = Lexico.lexico()
        if token_of["valor"] != "of":
            mensagemErro(token_of, "of")
            return True, token_of, "Object"

        tipos_ramos = []
        from Semantico.Ambiente import Ambiente
        while True:
            token_id = Lexico.lexico()
            if token_id["tipo"] != "ID":
                mensagemErro(token_id, "ID")
                return True, token_id, "Object"

            token_dp = Lexico.lexico()
            if token_dp["valor"] != ":":
                mensagemErro(token_dp, ":")
                return True, token_dp, "Object"

            token_type = Lexico.lexico()
            if token_type["tipo"] != "TYPE":
                mensagemErro(token_type, "TYPE")
                return True, token_type, "Object"

            token_seta = Lexico.lexico()
            if token_seta["valor"] != "=>":
                mensagemErro(token_seta, "=>")
                return True, token_seta, "Object"

            ambiente_ramo = Ambiente(ambiente)
            ambiente_ramo.addVariavel(token_id["valor"], token_type["valor"])

            erro, token, tipo_ramo = sintaticoExpr(ambiente_ramo)
            if erro: return True, token, "Object"
            tipos_ramos.append(tipo_ramo)

            token_pv = Lexico.lexico()
            if token_pv["valor"] != ";":
                mensagemErro(token_pv, ";")
                return True, token_pv, "Object"

            if Lexico.peek()["valor"] == "esac":
                break

        token_esac = Lexico.lexico()
        if token_esac["valor"] != "esac":
            mensagemErro(token_esac, "esac")
            return True, token_esac, "Object"

        return False, token_esac, tipos_ramos[0] if tipos_ramos else "Object"

    mensagemErro(proximo, "Expressão válida")
    return True, proximo, "Object"