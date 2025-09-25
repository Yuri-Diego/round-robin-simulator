class Processo:
    def __init__(self, pid, chegada: int, duracao: int ):
        self.pid = pid
        self.chegada = chegada
        self.duracao, self.tempo_restante = duracao, duracao
        self.termino = None
        self.tempo_de_resposta = 0
        self.tempo_de_espera = 0