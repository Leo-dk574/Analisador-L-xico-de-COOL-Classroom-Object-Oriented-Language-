import Lexico
import SintaticoExpr

from Semantico.Descritor import TabelaDescritores
from Semantico.Ambiente import Ambiente

descritor = TabelaDescritores()
PASSO = 1

def iniciarDescritor():
    descritor.classes = {}
    classeObject = descritor.addClasse("Object", None)
    classeObject.addMetodo("abort", "Object", [])
    classeObject.addMetodo("type_name", "String", [])
    classeObject.addMetodo("copy", "SELF_TYPE", [])

    classeIO = descritor.addClasse("IO", "Object")
    classeIO.addMetodo("out_string", "SELF_TYPE", ["String"])
    classeIO.addMetodo("out_int", "SELF_TYPE", ["Int"])
    classeIO.addMetodo("in_string", "String", [])
    classeIO.addMetodo("in_int", "Int", [])

    descritor.addClasse("Int", "Object")
    descritor.addClasse("Bool", "Object")

    classeString = descritor.addClasse("String", "Object")
    classeString.addMetodo("length", "Int", [])
    classeString.addMetodo("concat", "String", ["String"])
    classeString.addMetodo("substr", "String", ["Int", "Int"])

def mensagemErro(token, token_esperado):
    linha = getattr(Lexico, "num_linha", "?")
    print(f"Erro Sintático (Linha {linha}): Esperado '{token_esperado}' mas recebeu '{token['valor']}' do tipo '{token['tipo']}'")

def sintaticoFormal():
    parametros = {}
    token = Lexico.lexico()
    if token["valor"] == ")": return False, token, parametros
    
    while True:
        if token["tipo"] != "ID":
            mensagemErro(token, "ID")
            return True, token, parametros
        nome = token["valor"]
        if nome == "self":
            print(f"Erro Semântico: 'self' não pode ser usado como nome de parâmetro.")
            return True, token, parametros
        if nome in parametros:
            print(f"Erro Semântico: Parâmetro '{nome}' duplicado.")
            return True, token, parametros

        token = Lexico.lexico()
        if token["valor"] != ":":
            mensagemErro(token, ":")
            return True, token, parametros

        token = Lexico.lexico()
        if token["tipo"] != "TYPE":
            mensagemErro(token, "TYPE")
            return True, token, parametros
        tipo = token["valor"]
        if tipo == "SELF_TYPE":
            print(f"Erro Semântico: Parâmetro '{nome}' não pode ter o tipo SELF_TYPE.")
            return True, token, parametros
            
        parametros[nome] = tipo

        token = Lexico.lexico()
        if token["valor"] == ")": return False, token, parametros
        if token["valor"] == ",":
            token = Lexico.lexico()
        else:
            mensagemErro(token, ", ou )")
            return True, token, parametros

def sintaticoFeature(token, ambienteClasse, Classe):
    global PASSO
    if token["tipo"] != "ID":
        mensagemErro(token, "ID")
        return True, token
    
    nomeFeature = token["valor"]
    token = Lexico.lexico()
    
    if token["valor"] == "(": 
        erro, token, parametros = sintaticoFormal()
        if erro: return True, token
        
        token = Lexico.lexico()
        if token["valor"] != ":":
            mensagemErro(token, ":")
            return True, token
            
        token = Lexico.lexico()
        if token["tipo"] != "TYPE":
            mensagemErro(token, "TYPE")
            return True, token
        tipo_retorno = token["valor"]

        if PASSO == 1:
            if Classe.buscarMetodoLocal(nomeFeature) is not None:
                print(f"Erro Semântico: Método '{nomeFeature}' já declarado.")
                return True, token
            Classe.addMetodo(nomeFeature, tipo_retorno, list(parametros.values()))
            
            token = Lexico.lexico()
            if token["valor"] != "{":
                mensagemErro(token, "{")
                return True, token
                
            profundidade = 1
            while profundidade > 0:
                token = Lexico.lexico()
                if token["tipo"] == "EOF": return True, token
                if token["valor"] == "{": profundidade += 1
                elif token["valor"] == "}": profundidade -= 1
                
            token = Lexico.lexico() 
            if token["valor"] != ";":
                mensagemErro(token, ";")
                return True, token
            return False, token
            
        else:
            token = Lexico.lexico() 
            ambiente = Ambiente(ambienteClasse)
            for nome_param, tipo_param in parametros.items():
                ambiente.addVariavel(nome_param, tipo_param)

            erro, token, tipo_expr = SintaticoExpr.sintaticoExpr(ambiente)
            if erro: return True, token

            if not SintaticoExpr.eh_subtipo(tipo_expr, tipo_retorno, ambiente):
                print(f"Erro Semântico: Método '{nomeFeature}' retornou '{tipo_expr}', mas prometeu um subtipo de '{tipo_retorno}'.")
                return True, token

            token = Lexico.lexico() 
            if token["valor"] != "}":
                mensagemErro(token, "}")
                return True, token
            
            token = Lexico.lexico()
            if token["valor"] != ";":
                mensagemErro(token, ";")
                return True, token

            return False, token

    elif token["valor"] == ":": 
        token = Lexico.lexico()
        if token["tipo"] != "TYPE":
            mensagemErro(token, "TYPE")
            return True, token
        tipo_atributo = token["valor"]

        if PASSO == 1:
            if Classe.buscarAtribLocal(nomeFeature) is not None:
                print(f"Erro Semântico: Atributo '{nomeFeature}' já definido.")
                return True, token
            Classe.addAtrib(nomeFeature, tipo_atributo)

            if Lexico.peek()["valor"] == "<-":
                Lexico.lexico() 
                chaves = 0
                while True:
                    proximo = Lexico.peek()
                    if proximo["tipo"] == "EOF": break
                    if proximo["valor"] == "{": chaves += 1
                    elif proximo["valor"] == "}": chaves -= 1
                    elif proximo["valor"] == ";" and chaves == 0:
                        break
                    Lexico.lexico()
            token = Lexico.lexico() 
            if token["valor"] != ";":
                mensagemErro(token, ";")
                return True, token
            return False, token
            
        else: 
            if nomeFeature == "self":
                print(f"Erro Semântico: 'self' não pode ser nome de atributo.")
                return True, token
            
            if Classe.pai and descritor.buscarClasse(Classe.pai):
                if descritor.buscarClasse(Classe.pai).buscarAtribPai(nomeFeature, descritor):
                    print(f"Erro Semântico: Atributo herdado '{nomeFeature}' não pode ser redefinido.")
                    return True, token

            tipo_expr = tipo_atributo
            if Lexico.peek()["valor"] == "<-":
                Lexico.lexico()
                erro, token, tipo_expr = SintaticoExpr.sintaticoExpr(ambienteClasse)
                if erro: return True, token

            if not SintaticoExpr.eh_subtipo(tipo_expr, tipo_atributo, ambienteClasse):
                print(f"Erro Semântico: Atributo '{nomeFeature}' de tipo '{tipo_atributo}' recebeu inicialização inválida '{tipo_expr}'.")
                return True, token
            
            token = Lexico.lexico()
            if token["valor"] != ";":
                mensagemErro(token, ";")
                return True, token
            return False, token
    else:
        mensagemErro(token, "( ou :")
        return True, token

def sintaticoClass(token, ambientePai):
    global PASSO
    if token["valor"] != "class":
        mensagemErro(token, "class")
        return True

    token = Lexico.lexico()
    if token["tipo"] != "TYPE":
        mensagemErro(token, "TYPE")
        return True
    nomeClasse = token["valor"]
    
    if PASSO == 1 and nomeClasse in ["Object", "IO", "Int", "Bool", "String", "SELF_TYPE"]:
        print(f"Erro Semântico: Classe básica '{nomeClasse}' não pode ser redefinida.")
        return True

    token = Lexico.lexico()
    nomePai = "Object"
    if token["valor"] == "inherits":
        token = Lexico.lexico()
        if token["tipo"] != "TYPE":
            mensagemErro(token, "TYPE")
            return True
        nomePai = token["valor"]
        if PASSO == 1 and nomePai in ["Int", "Bool", "String", "SELF_TYPE"]:
            print(f"Erro Semântico: Não é permitido herdar de '{nomePai}'.")
            return True
        token = Lexico.lexico()

    if PASSO == 1:
        if descritor.buscarClasse(nomeClasse) is not None:
            print(f"Erro Semântico: Classe '{nomeClasse}' redefinida.")
            return True
        novaClasse = descritor.addClasse(nomeClasse, nomePai)
    else:
        novaClasse = descritor.buscarClasse(nomeClasse)

    ambiente = Ambiente(ambientePai, novaClasse)
    ambiente.addVariavel("self", "SELF_TYPE")

    if PASSO == 2:
        atual = descritor.buscarClasse(nomePai)
        caminho = []
        while atual is not None:
            caminho.insert(0, atual)
            atual = descritor.buscarClasse(atual.pai) if atual.pai else None
        
        for c in caminho:
            for n, t in c.atributos.items():
                ambiente.addVariavel(n, t)
        
        for n, t in novaClasse.atributos.items():
            ambiente.addVariavel(n, t)

    if token["valor"] != "{":
        mensagemErro(token, "{")
        return True
    
    token = Lexico.lexico()
    while token["valor"] != "}":
        erro, token = sintaticoFeature(token, ambiente, novaClasse)
        if erro: return True
        
        if token["valor"] != ";":
            mensagemErro(token, ";")
            return True
        token = Lexico.lexico()
    return False

def sintaticoProgram():
    global PASSO
    print("\n[INFO] Construindo Árvore de Classes (Passagem 1)...")
    
    PASSO = 1
    iniciarDescritor()
    ambiente_global = Ambiente(None)
    
    token = Lexico.lexico()
    erro = False
    while token["tipo"] != "EOF":
        erro = sintaticoClass(token, ambiente_global)
        if erro: break
        token = Lexico.lexico()
        if token["valor"] != ";":
            mensagemErro(token, ";")
            erro = True
            break
        token = Lexico.lexico()
        
    if erro:
        print("[ERRO] Compilação abortada na Passagem 1.")
        return True

    # Validações estruturais obrigatórias
    for nome_classe, classe_obj in descritor.classes.items():
        if nome_classe in ["Object", "IO", "Int", "Bool", "String"]: continue
        if descritor.buscarClasse(classe_obj.pai) is None:
            print(f"Erro Semântico: Classe '{nome_classe}' herda da classe indefinida '{classe_obj.pai}'.")
            return True
        visitados = set()
        atual = classe_obj
        while atual is not None:
            if atual.nome in visitados:
                print(f"Erro Semântico: Ciclo de herança detectado em '{atual.nome}'.")
                return True
            visitados.add(atual.nome)
            atual = descritor.buscarClasse(atual.pai)

    classe_main = descritor.buscarClasse("Main")
    if not classe_main:
        print("Erro Semântico: A classe 'Main' não foi definida.")
        return True
    if not classe_main.buscarMetodoLocal("main"):
        print("Erro Semântico: O método 'main' não foi definido na classe 'Main'.")
        return True

    print("[INFO] Validando Tipagem Semântica e Escopos (Passagem 2)...")
    PASSO = 2
    
    # === REBOBINAR O ARQUIVO ===
    Lexico.f.seek(0)
    Lexico.c = Lexico.f.read(1)
    Lexico.num_linha = 1
    if hasattr(Lexico, 'prox_token'):
        Lexico.prox_token = None
    
    token = Lexico.lexico()
    while token["tipo"] != "EOF":
        erro = sintaticoClass(token, ambiente_global)
        if erro: break
        token = Lexico.lexico()
        if token["valor"] != ";":
            mensagemErro(token, ";")
            erro = True
            break
        token = Lexico.lexico()
        
    if erro:
        print("[ERRO] Falha de validação semântica/sintática detectada na Passagem 2.")
        return True
        
    print("\n>>> SUCESSO! O código é 100% Válido em COOL <<<")
    return False