from processo import Processo
from collections import deque

def RoundRobin(processos: list[Processo], quantum: int):
    tempo = 0
    filaDeProcessos = deque(processos)
    linhaDoTempo = []

    while filaDeProcessos:
        processo = filaDeProcessos.popleft()
        inicio = tempo
        tempo_executando = min(quantum, processo.tempo_restante)

        tempo += tempo_executando
        processo.tempo_restante -= tempo_executando
        fim = tempo

        linhaDoTempo.append({
            "pid": processo.pid,
            "inicio": inicio,
            "fim": fim
        })

        if processo.tempo_restante == 0:
            processo.termino = fim
            processo.tempo_de_resposta = processo.termino - processo.chegada
            processo.tempo_de_espera = processo.tempo_de_resposta - processo.duracao
        else:
            filaDeProcessos.append(processo)

    return linhaDoTempo, processos

