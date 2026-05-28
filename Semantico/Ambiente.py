class Ambiente:
    def __init__(self, pai=None, classe=None):
        self.variaveis = {} # { nome: tipo }
        self.pai = pai
        self.classe = classe

    def getClasse(self):
        # Se este ambiente conhece a classe, retorna ela
        if self.classe is not None:
            return self.classe
        # Se não conhece, mas tem um pai, pergunta ao pai!
        if self.pai is not None:
            return self.pai.getClasse()
        return None

    def addVariavel(self, nome, tipo):
        self.variaveis[nome] = tipo
        
    def buscarLocal(self, nome):
        return self.variaveis.get(nome)
        
    def buscarPai(self, nome):
        if nome in self.variaveis:
            return self.variaveis[nome]
        if self.pai is not None:
            return self.pai.buscarPai(nome)
        return None