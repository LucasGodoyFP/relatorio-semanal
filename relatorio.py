import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta
import json
import os

# --- Listas de pedidos por categoria ---
prazo_segunda = sorted([
    "balcao resultados", "laudos", "sg matriz", "rec infantil", "coleta infantil", "vacina",
    "rec raio x", "rec medicina nuclear", "semanal nto", "refeitorio", "cafeteria", "faturamento",
    "seg do trabalho", "adm nto", "planilha med nuclear", "planilha raio x", "planilha usg",
    "rec usg", "rec central", "volta colher", "medicos cafe", "coleta central", "sg olinda"
])

entregas_internas = sorted([
    "saul elkind", "ibipora", "santa terezinha", "endo", "araucaria", "upa cambe", "ubs cambe",
    "santos dumont", "palhano"
])

entregas_externas = sorted([
    "rolandia", "arapongas", "araucaria", "santa terezinha", "upa cambe", "ubs cambe",
    "santo amaro", "cambe", "provita"
])

# Variáveis globais para controlar checkboxes e labels
vars_labels_segunda = []
vars_labels_quarta = []

# Arquivo para salvar os dados
DATA_FILE = "pedidos_salvos.json"

# Função para carregar dados salvos
def carregar_dados():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Erro ao carregar dados: {e}")
            return {}
    return {}

# Função para salvar dados
def salvar_dados():
    dados = {
        'selecoes_segunda': {},
        'selecoes_quarta': {},
        'tipo_quarta': opcao_quarta.get(),
        'data_salvamento': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        'semana_inicio': data_referencia().strftime("%d/%m/%Y")  # Salva a semana atual
    }
    
    # Salvar seleções da segunda
    for var, label, pedido in vars_labels_segunda:
        if var.get():
            # Salva se está marcado e qual cor tinha
            bg_color = label.cget("bg")
            dados['selecoes_segunda'][pedido] = {
                'marcado': True,
                'cor': bg_color,
                'data_marcacao': datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            }
        else:
            dados['selecoes_segunda'][pedido] = {'marcado': False}
    
    # Salvar seleções da quarta
    for var, label, pedido in vars_labels_quarta:
        if var.get():
            bg_color = label.cget("bg")
            dados['selecoes_quarta'][pedido] = {
                'marcado': True,
                'cor': bg_color,
                'data_marcacao': datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            }
        else:
            dados['selecoes_quarta'][pedido] = {'marcado': False}
    
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
        print(f"Dados salvos com sucesso em {DATA_FILE}!")
    except Exception as e:
        print(f"Erro ao salvar dados: {e}")

# Função para restaurar seleções salvas
def restaurar_selecoes():
    dados = carregar_dados()
    if not dados:
        print("Nenhum dado salvo encontrado. Iniciando com seleções limpas.")
        return
    
    print("Carregando dados salvos...")
    
    # Verificar se os dados salvos são da mesma semana
    semana_atual = data_referencia().strftime("%d/%m/%Y")
    semana_salva = dados.get('semana_inicio', '')
    
    if semana_salva != semana_atual:
        print(f"Dados de semana diferente! Salva: {semana_salva}, Atual: {semana_atual}")
        print("Limpando dados da semana passada automaticamente...")
        # Limpa os checkboxes na interface
        limpar_checkboxes_sem_salvar()
        # Atualiza a semana nos dados salvos
        salvar_dados()
        return
    
    # Restaurar tipo da quarta
    if 'tipo_quarta' in dados:
        opcao_quarta.set(dados['tipo_quarta'])
        print(f"Tipo da quarta restaurado: {dados['tipo_quarta']}")
    
    # Atualizar a seção da quarta
    atualizar_secao_quarta()
    
    # Aguardar a interface ser atualizada antes de aplicar as seleções
    root.after(300, lambda: aplicar_selecoes_salvas(dados))

def aplicar_selecoes_salvas(dados):
    print("Aplicando seleções salvas...")
    
    # Restaurar seleções da segunda
    if 'selecoes_segunda' in dados:
        contador_segunda = 0
        for var, label, pedido in vars_labels_segunda:
            if pedido in dados['selecoes_segunda']:
                info = dados['selecoes_segunda'][pedido]
                var.set(info['marcado'])
                if info['marcado']:
                    # Restaura a cor salva
                    cor_salva = info.get('cor', 'SystemButtonFace')
                    label.config(bg=cor_salva)
                    contador_segunda += 1
        print(f"Segunda: {contador_segunda} seleções restauradas")
    
    # Restaurar seleções da quarta
    if 'selecoes_quarta' in dados:
        contador_quarta = 0
        for var, label, pedido in vars_labels_quarta:
            if pedido in dados['selecoes_quarta']:
                info = dados['selecoes_quarta'][pedido]
                var.set(info['marcado'])
                if info['marcado']:
                    # Restaura a cor salva
                    cor_salva = info.get('cor', 'SystemButtonFace')
                    label.config(bg=cor_salva)
                    contador_quarta += 1
        print(f"Quarta: {contador_quarta} seleções restauradas")
    
    print("Carregamento concluído!")

# Função para simular data atual para o relatório
def data_referencia():
    hoje = datetime.now()
    inicio_semana = hoje - timedelta(days=hoje.weekday())
    return inicio_semana

# --- Verifica se o pedido está dentro do prazo ---
def verificar_prazo(nome_pedido):
    agora = datetime.now()
    dia = agora.weekday()
    hora = agora.hour
    minuto = agora.minute

    if nome_pedido in prazo_segunda:
        # Prazo até segunda 08:40
        if dia < 0 or (dia == 0 and (hora < 8 or (hora == 8 and minuto <= 40))):
            return True
        return False

    if nome_pedido in entregas_internas or nome_pedido in entregas_externas:
        # Prazo até quarta 12:40
        if dia < 2 or (dia == 2 and (hora < 12 or (hora == 12 and minuto <= 40))):
            return True
        return False

    return None

# --- Callback ao marcar checkbox ---
def on_check(var, label, nome_pedido, salvar=True):
    if var.get():
        resultado = verificar_prazo(nome_pedido)
        if resultado is True:
            label.config(bg="lightgreen")
        elif resultado is False:
            label.config(bg="tomato")
        else:
            label.config(bg="gray")
    else:
        label.config(bg="SystemButtonFace")
    
    # Salva automaticamente após cada alteração
    if salvar:
        salvar_dados()

# --- Criação de seções ---
def criar_secao(titulo, pedidos, master_frame, lista_vars_labels):
    tk.Label(master_frame, text=titulo, font=("Arial", 12, "bold")).pack(anchor="w", pady=(15, 5))

    grid_frame = tk.Frame(master_frame)
    grid_frame.pack()

    colunas = 3
    linha = 0
    coluna = 0

    for pedido in pedidos:
        var = tk.BooleanVar()

        container = tk.Frame(grid_frame)
        container.grid(row=linha, column=coluna, sticky="w", padx=10, pady=4)

        checkbox = tk.Checkbutton(container, variable=var)
        checkbox.pack(side="left")

        label = tk.Label(container, text=pedido, width=30, anchor="w")
        label.pack(side="left")

        checkbox.config(command=lambda v=var, l=label, p=pedido: on_check(v, l, p))

        lista_vars_labels.append((var, label, pedido))

        coluna += 1
        if coluna >= colunas:
            coluna = 0
            linha += 1

# --- Atualiza a seção dinâmica de quarta-feira ---
def atualizar_secao_quarta():
    global vars_labels_quarta
    vars_labels_quarta.clear()

    for widget in quarta_frame.winfo_children():
        widget.destroy()

    tipo = opcao_quarta.get()
    if tipo == "internas":
        criar_secao("📦 Requisições que têm que estar prontas até quarta 12:40 (ENTREGAS INTERNAS)", entregas_internas, quarta_frame, vars_labels_quarta)
    elif tipo == "externas":
        criar_secao("📦 Requisições que têm que estar prontas até quarta 12:40 (ENTREGAS EXTERNAS)", entregas_externas, quarta_frame, vars_labels_quarta)

# --- Limpa checkboxes sem salvar (para uso interno) ---
def limpar_checkboxes_sem_salvar():
    for var, label, _ in vars_labels_segunda:
        var.set(False)
        label.config(bg="SystemButtonFace")

    for var, label, _ in vars_labels_quarta:
        var.set(False)
        label.config(bg="SystemButtonFace")

# --- Limpa todas as seleções ---
def limpar_selecoes():
    resposta = messagebox.askyesno("Limpar Seleções", 
        "Tem certeza que deseja limpar TODOS os checkboxes marcados?\n\nIsso iniciará uma nova semana.")
    
    if resposta:
        limpar_checkboxes_sem_salvar()
        salvar_dados()
        print("Todas as seleções foram limpas! Nova semana iniciada.")
        messagebox.showinfo("Nova Semana", "Todos os checkboxes foram limpos e uma nova semana foi iniciada!")

# --- Gera relatório semanal ---
def gerar_relatorio():
    inicio = data_referencia()
    fim = inicio + timedelta(days=4)

    periodo_str = f"{inicio.strftime('%d/%m/%Y')} a {fim.strftime('%d/%m/%Y')}"

    selecionados = []
    nao_selecionados = []

    for var, label, pedido in vars_labels_segunda:
        if var.get():
            selecionados.append(pedido)
        else:
            nao_selecionados.append(pedido)

    for var, label, pedido in vars_labels_quarta:
        if var.get():
            selecionados.append(pedido)
        else:
            nao_selecionados.append(pedido)

    # Para o relatório, consideramos sexta às 12:40 como prazo máximo
    data_referencia_rel = inicio + timedelta(days=4, hours=12, minutes=40)

    urgentes = []
    atrasados = []

    for pedido in selecionados:
        dentro_prazo = verificar_prazo(pedido)
        if dentro_prazo:
            urgentes.append(pedido)
        else:
            atrasados.append(pedido)

    texto = []
    texto.append("📋 Relatório Semanal – Requisições e Recebimentos")
    texto.append(f"Período: {periodo_str}\n")
    texto.append(f"✅ Requisições - Total: {len(selecionados)} de {len(prazo_segunda) + len(entregas_internas) + len(entregas_externas)}")
    texto.append(f"Urgentes: {len(urgentes)}")
    texto.append(f"Sem Requisições:\n")

    for item in sorted(nao_selecionados):
        texto.append(f"🟠 {item}")
    texto.append("\nSolicitadas atrasadas:\n")
    for item in sorted(atrasados):
        texto.append(f"🟡 {item}")
    texto.append("\nRequisições urgentes:\n")
    for item in sorted(urgentes):
        texto.append(f"🔴 {item}")
    texto.append("\n📦 Recebimentos")
    texto.append(f"Total: {len(selecionados)} de {len(prazo_segunda) + len(entregas_internas) + len(entregas_externas)}")
    texto.append("\nPendências:\n\n")
    texto.append("Observações:")
    texto.append("Atenciosamente,")
    texto.append("Lucas Godoy")
    texto.append("Auxiliar de almoxarifado")

    rel_window = tk.Toplevel(root)
    rel_window.title("Relatório Semanal")
    txt_rel = tk.Text(rel_window, width=80, height=30)
    txt_rel.pack(padx=10, pady=10)
    txt_rel.insert("1.0", "\n".join(texto))
    txt_rel.config(state="disabled")

# --- Interface principal ---
root = tk.Tk()
root.title("Verificação de Pedidos - Com Salvamento Automático")
root.geometry("950x700")

# Adicionar tratamento para fechar a janela
def on_closing():
    print("Fechando aplicação...")
    salvar_dados()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)

main_frame = tk.Frame(root)
main_frame.pack(padx=20, pady=20, fill="both", expand=True)

# Título principal
tk.Label(main_frame, text="Sistema de Verificação de Pedidos (Salvamento Automático)", font=("Arial", 16)).pack(pady=(0, 20))

# Seção fixa: Segunda 08:40
criar_secao("📦 Requisições que têm que estar prontas até segunda 08:40", prazo_segunda, main_frame, vars_labels_segunda)

# Seletor de tipo de entrega (quarta-feira)
opcao_quarta = tk.StringVar(value="internas")

seletor_frame = tk.Frame(main_frame)
seletor_frame.pack(pady=15)

tk.Label(seletor_frame, text="Visualizar requisições de quarta-feira: ", font=("Arial", 12)).pack(side="left", padx=(0, 10))

tk.Radiobutton(seletor_frame, text="Entregas Internas", variable=opcao_quarta, value="internas", command=atualizar_secao_quarta).pack(side="left")
tk.Radiobutton(seletor_frame, text="Entregas Externas", variable=opcao_quarta, value="externas", command=atualizar_secao_quarta).pack(side="left")

# Botões para limpar seleções e gerar relatório
botoes_frame = tk.Frame(main_frame)
botoes_frame.pack(pady=10)

botao_limpar = tk.Button(botoes_frame, text="Nova Semana / Limpar Tudo", command=limpar_selecoes, bg="orange", fg="black", font=("Arial", 12, "bold"))
botao_limpar.pack(side="left", padx=10)

botao_relatorio = tk.Button(botoes_frame, text="Gerar Relatório", command=gerar_relatorio, bg="lightblue", fg="black", font=("Arial", 12, "bold"))
botao_relatorio.pack(side="left", padx=10)

botao_salvar = tk.Button(botoes_frame, text="Salvar Agora", command=salvar_dados, bg="lightgreen", fg="black", font=("Arial", 12, "bold"))
botao_salvar.pack(side="left", padx=10)

# Frame que será atualizado com base na escolha
quarta_frame = tk.Frame(main_frame)
quarta_frame.pack()

# Inicializa com internas
atualizar_secao_quarta()

# Carregar dados salvos ao iniciar
print("Iniciando aplicação...")
root.after(500, restaurar_selecoes)

root.mainloop()