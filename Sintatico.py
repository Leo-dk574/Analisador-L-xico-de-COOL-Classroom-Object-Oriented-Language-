import Lexico
from SintaticoExpr import mensagemErro
import SintaticoExpr

from Semantico.Descritor import TabelaDescritores
from Semantico.Ambiente import Ambiente

descritor = TabelaDescritores()

def iniciarDescritor():
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

def sintaticoFormal():
    print("Entrou no Formal")
    parametros = {}

    token = Lexico.lexico()

    if(token["valor"] == ")"):
        return False, token, parametros
    
    while True:
        if(token["tipo"] != "ID"):
            mensagemErro(token, "ID")
            return True, token, parametros
        
        nome = token["valor"]
        if nome in parametros:
            print(f"Parâmetro {nome} duplicado na assinatura do metodo")
            return True, token, parametros

        token = Lexico.lexico()
        if(token["valor"] != ":"):
            mensagemErro(token, ":")
            return True, token, parametros

        token = Lexico.lexico()
        if(token["tipo"] != "TYPE"):
            mensagemErro(token, "TYPE")
            return True, token, parametros
        
        tipo = token["valor"]
        parametros[nome] = tipo

        token = Lexico.lexico()
        if(token["valor"] == ")"):
            return False, token, parametros
        
        if(token["valor"] == ","):
            token = Lexico.lexico()
        else:
            mensagemErro(token, ", ou )")
            return True, token, parametros


def sintaticoFeature(token, ambienteClasse, Classe):
    print("Entrou no Feature")
    
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
        
        tipo = token["valor"]
        #tipo_expr = tipo #variavel usada apenas para testar o código durante a transição do refactor do código. Ainda não implementado as mudanças no SintaticoExpr

        if Classe.buscarMetodoLocal(nomeFeature) is not None:
            print(f"Método {nomeFeature} redefinido na classe f{Classe.nome}")
            return True, token
            
        metodoPai = Classe.buscarMetodoPai(nomeFeature, descritor)
        if metodoPai is not None:
            if metodoPai.tipo != tipo or metodoPai.parametros != list(parametros.values()):
                print(f"Override ilegal do método '{nomeFeature}'. Assinatura não bate com o pai")
                return True, token

        Classe.addMetodo(nomeFeature, tipo, list(parametros.values()))

        token = Lexico.lexico()
        if token["valor"] != "{":
            mensagemErro(token, "{")
            return True, token

        ambiente = Ambiente(ambienteClasse)
        for nome_param, tipo_param in parametros.items():
            ambiente.addVariavel(nome_param, tipo_param)

        erro, token, tipo_expr = SintaticoExpr.sintaticoExpr(ambiente)
        if erro: return True, token

        if not SintaticoExpr.eh_subtipo(tipo_expr, tipo, ambiente):
            print(f"Método '{nomeFeature}' deveria retornar um subtipo de '{tipo}', mas o corpo retornou '{tipo_expr}'")
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
        
        tipo = token["valor"]

        if Classe.buscarAtribLocal(nomeFeature) is not None:
            print(f"Atributo {nomeFeature} já definido na classe {Classe.nome}")
            return True, token

        if Classe.buscarAtribPai(nomeFeature, descritor) is not None:
            print(f"Atributo '{nomeFeature}' não pode ser sobrescrito da classe pai.")
            return True, token
            
        Classe.addAtrib(nomeFeature, tipo)
        ambienteClasse.addVariavel(nomeFeature, tipo)
        tipo_expr = tipo

        if Lexico.peek()["valor"] == "<-":
            Lexico.lexico()
            erro, token, tipo_expr = SintaticoExpr.sintaticoExpr(ambienteClasse)
            if erro: return True, token
        
        if not SintaticoExpr.eh_subtipo(tipo_expr, tipo, ambienteClasse):
            print(f"Método '{nomeFeature}' deveria retornar um subtipo de '{tipo}', mas o corpo retornou '{tipo_expr}'")
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
    print("Entrou na Class")
    
    if token["valor"] != "class":
        mensagemErro(token, "class")
        return True
    
    token = Lexico.lexico()
    if token["tipo"] != "TYPE":
        mensagemErro(token, "TYPE")
        return True
    
    nomeClasse = token["valor"]
    nomePai = 'Object'
    if descritor.buscarClasse(nomeClasse) is not None:
        print(f"Classe {nomeClasse} já foi definida")
        return True

    token = Lexico.lexico()
    if token["valor"] == "inherits":
        
        token = Lexico.lexico()
        if token["tipo"] != "TYPE":
            mensagemErro(token, "TYPE")
            return True

        nomePai = token["valor"]
        if descritor.buscarClasse(nomePai) is None:
            print(f"Classe pai {nomePai} não foi definida")
            return True

        token = Lexico.lexico()
    
    novaClasse = descritor.addClasse(nomeClasse, nomePai)
    ambiente = Ambiente(ambientePai, novaClasse)
    
    descritorPai = descritor.buscarClasse(nomePai)
    for nome, tipo in descritorPai.atributos.items():
        ambiente.addVariavel(nome, tipo)

    if token["valor"] != "{":
        mensagemErro(token, "{")
        return True
    
    token = Lexico.lexico()
    while(token["valor"] != "}"):
        erro, token = sintaticoFeature(token, ambiente, novaClasse)
        
        if(erro):
            return True
        
        if token["valor"] != ";":
            mensagemErro(token, ";")
            return True
        token = Lexico.lexico()
    return False



def sintaticoProgram():
    print("Entrou no Program")
    iniciarDescritor()
    ambiente_global = Ambiente(None)

    token = Lexico.lexico()
    while(token["tipo"] != "EOF"):
        erro = sintaticoClass(token, ambiente_global)

        if(erro):
            break

        token = Lexico.lexico()
        if token["valor"] != ";":
            mensagemErro(token, ";")
            break
        token = Lexico.lexico()