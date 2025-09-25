import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.cm as cm

from processo import Processo
from round_robin import RoundRobin


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Round Robin Simulator")
        
        # Filas
        self.processos = []       # entrada
        self.finalizados = []     # terminados

        # Estrutura principal
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=2)
        self.root.columnconfigure(1, weight=3)

        # Frame esquerdo (inputs + tabela + métricas)
        left_frame = tk.Frame(root, padx=10, pady=10)
        left_frame.grid(row=0, column=0, sticky="nsew")

        # Frame direito (gráfico)
        right_frame = tk.Frame(root, padx=10, pady=10)
        right_frame.grid(row=0, column=1, sticky="nsew")

        # ==== Inputs e Botões ====
        input_frame = tk.Frame(left_frame)
        input_frame.pack(fill=tk.X, pady=5)

        tk.Label(input_frame, text="PID:").grid(row=0, column=0, padx=5)
        self.pid_entry = tk.Entry(input_frame, width=8)
        self.pid_entry.grid(row=0, column=1, padx=5)

        tk.Label(input_frame, text="Duração:").grid(row=0, column=2, padx=5)
        self.duracao_entry = tk.Entry(input_frame, width=8)
        self.duracao_entry.grid(row=0, column=3, padx=5)

        tk.Button(input_frame, text="Adicionar Processo", command=self.adicionar_processo).grid(
            row=0, column=4, padx=10
        )

        tk.Label(input_frame, text="Quantum:").grid(row=0, column=5, padx=5)
        self.quantum_entry = tk.Entry(input_frame, width=8)
        self.quantum_entry.grid(row=0, column=6, padx=5)

        tk.Button(input_frame, text="Executar RR", command=self.executar_rr).grid(
            row=0, column=7, padx=10
        )

        # Feedback lateral com duas listas (entrada e finalizados)
        self.feedback_frame = tk.LabelFrame(input_frame, text="📋 Fila de Processos")
        self.feedback_frame.grid(row=0, column=8, padx=15, sticky="ns")

        lists_frame = tk.Frame(self.feedback_frame)
        lists_frame.pack(fill=tk.BOTH, expand=True)

        entrada_frame = tk.Frame(lists_frame)
        entrada_frame.grid(row=0, column=0, padx=5, sticky="n")
        tk.Label(entrada_frame, text="Entrada").pack()
        self.feedback_list = tk.Listbox(entrada_frame, height=6, width=25)
        self.feedback_list.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

        finalizados_frame = tk.Frame(lists_frame)
        finalizados_frame.grid(row=0, column=1, padx=5, sticky="n")
        tk.Label(finalizados_frame, text="Finalizados").pack()
        self.finished_list = tk.Listbox(finalizados_frame, height=6, width=25, fg="green")
        self.finished_list.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

        # ==== Tabela de Processos ====
        self.tree = ttk.Treeview(
            left_frame,
            columns=("pid", "chegada", "duracao", "termino", "resposta", "espera"),
            show="headings",
            height=15
        )
        self.tree.pack(fill=tk.BOTH, expand=True, pady=10)

        for col in ("pid", "chegada", "duracao", "termino", "resposta", "espera"):
            self.tree.heading(col, text=col.capitalize())
            self.tree.column(col, anchor="center")

        # ==== Labels de métricas (médias) ====
        metrics_frame = tk.Frame(left_frame)
        metrics_frame.pack(fill=tk.X, pady=5)
        tk.Label(metrics_frame, text="Média de Tempo de Resposta:").grid(row=0, column=0, padx=5, sticky="w")
        self.avg_response_label = tk.Label(metrics_frame, text="0")
        self.avg_response_label.grid(row=0, column=1, padx=5, sticky="w")

        tk.Label(metrics_frame, text="Média de Tempo de Espera:").grid(row=1, column=0, padx=5, sticky="w")
        self.avg_wait_label = tk.Label(metrics_frame, text="0")
        self.avg_wait_label.grid(row=1, column=1, padx=5, sticky="w")

        # ==== Gráfico ====
        self.fig, self.ax = plt.subplots(figsize=(5, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=right_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def adicionar_processo(self):
        pid = self.pid_entry.get()
        duracao = self.duracao_entry.get()
        if not pid or not duracao:
            messagebox.showwarning("Erro", "Preencha todos os campos")
            return
        try:
            duracao = int(duracao)
        except ValueError:
            messagebox.showerror("Erro", "Duração deve ser número inteiro")
            return

        processo = Processo(pid, chegada=len(self.processos), duracao=duracao)
        self.processos.append(processo)
        self.feedback_list.insert(tk.END, f"{processo.pid} (Burst: {processo.duracao})")

        self.pid_entry.delete(0, tk.END)
        self.duracao_entry.delete(0, tk.END)

    def executar_rr(self):
        if not self.processos:
            messagebox.showwarning("Erro", "Nenhum processo na fila de entrada")
            return
        quantum = self.quantum_entry.get()
        if not quantum:
            messagebox.showwarning("Erro", "Defina o quantum")
            return
        try:
            quantum = int(quantum)
        except ValueError:
            messagebox.showerror("Erro", "Quantum deve ser um número inteiro")
            return

        # Resetar estado
        for idx, p in enumerate(self.processos):
            p.chegada = idx
            p.tempo_restante = p.duracao
            p.termino = None
            p.tempo_de_resposta = 0
            p.tempo_de_espera = 0

        # Rodar Round Robin
        linhaDoTempo, terminados = RoundRobin(self.processos, quantum)
        self.finalizados.extend(terminados)
        self.processos = []

        # Atualizar listas de feedback
        self.feedback_list.delete(0, tk.END)
        self.finished_list.delete(0, tk.END)
        for p in self.finalizados:
            self.finished_list.insert(tk.END, f"{p.pid} ✔")

        # Atualizar tabela
        for item in self.tree.get_children():
            self.tree.delete(item)
        for p in self.finalizados:
            self.tree.insert(
                "", "end",
                values=(p.pid, p.chegada, p.duracao, p.termino, p.tempo_de_resposta, p.tempo_de_espera)
            )

        # Calcular médias
        n = len(self.finalizados)
        avg_resposta = sum(p.tempo_de_resposta for p in self.finalizados) / n if n else 0
        avg_espera = sum(p.tempo_de_espera for p in self.finalizados) / n if n else 0
        self.avg_response_label.config(text=f"{avg_resposta:.2f}")
        self.avg_wait_label.config(text=f"{avg_espera:.2f}")

        # Definir cores
        pids = [p.pid for p in terminados]
        cmap = cm.get_cmap("tab20", len(pids))
        color_map = {pid: cmap(i) for i, pid in enumerate(pids)}

        # Plotar gráfico
        self.ax.clear()
        for task in linhaDoTempo:
            self.ax.barh(
                task["pid"],
                task["fim"] - task["inicio"],
                left=task["inicio"],
                color=color_map[task["pid"]],
                edgecolor="black"
            )

        self.ax.set_xlabel("Tempo")
        self.ax.set_ylabel("Processos")
        self.ax.set_title("Escalonamento Round Robin")

        handles = [plt.Rectangle((0, 0), 1, 1, color=color_map[pid]) for pid in pids]
        self.ax.legend(handles, pids, title="Processos", loc="upper center",
                       bbox_to_anchor=(0.5, -0.15), ncol=min(len(pids), 5), frameon=False)
        self.fig.subplots_adjust(bottom=0.25)
        self.canvas.draw()
