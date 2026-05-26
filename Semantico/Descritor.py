class Metodo:
    def __init__(self, tipo, parametros):
        self.tipo = tipo
        self.parametros = parametros # ex: ['Int']

class Classe:
    def __init__(self, nome, pai=None):
        self.nome = nome
        self.pai = pai # ex: 'Object'
        self.metodos = {} # { nome: Metodo }
        self.atributos = {} # { nome: 'Int' }

    def addAtrib(self, nome, tipo):
        self.atributos[nome] = tipo

    def buscarAtribLocal(self, nome):
        return self.atributos.get(nome)

    def buscarAtribPai(self, nome, tabela_descritores):
        if nome in self.atributos:
            return self.atributos[nome]
        
        if self.pai is not None:
            descritor_pai = tabela_descritores.buscarClasse(self.pai)
            if descritor_pai is not None:
                return descritor_pai.buscarAtribPai(nome, tabela_descritores)
                
        return None

    def addMetodo(self, nome, tipo, parametros):
        self.metodos[nome] = Metodo(tipo, parametros)

    def buscarMetodoLocal(self, nome):
        return self.metodos.get(nome)

    def buscarMetodoPai(self, nome, tabela_descritores):
        if nome in self.metodos:
            return self.metodos[nome]
            
        if self.pai is not None:
            descritor_pai = tabela_descritores.buscarClasse(self.pai)
            if descritor_pai is not None:
                return descritor_pai.buscarMetodoPai(nome, tabela_descritores)
                
        return None

class TabelaDescritores:
    def __init__(self):
        self.classes = {} # { nome: Classe }
        
    def addClasse(self, nome, pai=None):
        self.classes[nome] = Classe(nome, pai)
        return self.classes[nome]
        
    def buscarClasse(self, nome):
        return self.classes.get(nome)