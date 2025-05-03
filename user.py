class User:

    def __init__(self, cpf, nome, sexo, nasc):
        self.cpf = cpf
        self.nome = nome
        self.sexo = sexo
        self.nasc = nasc

    def toDict(self):
        return {
            'cpf': self.cpf,
            'nome': self.nome,
            'sexo': self.sexo,
            'nasc': self.nasc
        }