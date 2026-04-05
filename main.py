import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
import json
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER

# ===== SISTEMA DE SIMULAÇÃO DE DATA =====
MODO_SIMULACAO = True

if MODO_SIMULACAO:
    DATA_SIMULADA = datetime(2026, 4, 8, 10, 0, 0)
    print(f"⚠️ MODO DE SIMULAÇÃO ATIVO!")
    print(f"📅 Data simulada: {DATA_SIMULADA.strftime('%A, %d/%m/%Y %H:%M')}")
    print(f"🎯 Testando comportamento para quarta-feira 10:00\n")
else:
    DATA_SIMULADA = None

def get_datetime_atual():
    if MODO_SIMULACAO and DATA_SIMULADA:
        return DATA_SIMULADA
    return datetime.now()

def data_referencia():
    hoje = get_datetime_atual()
    inicio_semana = hoje - timedelta(days=hoje.weekday())
    return inicio_semana

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

vars_labels_segunda = []
vars_labels_quarta = []
DATA_FILE = "pedidos_salvos.json"

# ============================================================
# PALETA DE CORES — tema escuro refinado
# ============================================================
BG          = "#0f1117"   # fundo principal
SURFACE     = "#181c27"   # cards / seções
SURFACE2    = "#1f2436"   # header de seção
BORDER      = "#252b3b"   # bordas
TEXT        = "#e2e6f0"   # texto principal
MUTED       = "#6b7280"   # texto secundário

ACCENT      = "#4f9cf9"   # azul principal
ACCENT2     = "#7c6af7"   # roxo/violeta
GREEN_OK    = "#22c55e"   # no prazo
GREEN_DARK  = "#16a34a"   # hover ok
RED_LATE    = "#f43f5e"   # atrasado
AMBER       = "#f59e0b"   # pendente / atenção

FONT_TITLE  = ("Segoe UI", 13, "bold")
FONT_NORMAL = ("Segoe UI", 10)
FONT_SMALL  = ("Segoe UI", 9)
FONT_HERO   = ("Segoe UI", 20, "bold")

# ============================================================
# PERSISTÊNCIA (lógica original intacta)
# ============================================================
def carregar_dados():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Erro ao carregar dados: {e}")
            return {}
    return {}

def salvar_dados():
    dados = {
        'selecoes_segunda': {},
        'selecoes_quarta': {},
        'tipo_quarta': opcao_quarta.get(),
        'data_salvamento': get_datetime_atual().strftime("%d/%m/%Y %H:%M:%S"),
        'semana_inicio': data_referencia().strftime("%d/%m/%Y")
    }
    for var, label, pedido in vars_labels_segunda:
        if var.get():
            dados['selecoes_segunda'][pedido] = {
                'marcado': True,
                'cor': label.cget("bg"),
                'data_marcacao': get_datetime_atual().strftime("%d/%m/%Y %H:%M:%S")
            }
        else:
            dados['selecoes_segunda'][pedido] = {'marcado': False}

    for var, label, pedido in vars_labels_quarta:
        if var.get():
            dados['selecoes_quarta'][pedido] = {
                'marcado': True,
                'cor': label.cget("bg"),
                'data_marcacao': get_datetime_atual().strftime("%d/%m/%Y %H:%M:%S")
            }
        else:
            dados['selecoes_quarta'][pedido] = {'marcado': False}

    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Erro ao salvar dados: {e}")

def restaurar_selecoes():
    dados = carregar_dados()
    if not dados:
        return
    semana_atual = data_referencia().strftime("%d/%m/%Y")
    semana_salva = dados.get('semana_inicio', '')
    if semana_salva != semana_atual:
        limpar_checkboxes_sem_salvar()
        salvar_dados()
        return
    if 'tipo_quarta' in dados:
        opcao_quarta.set(dados['tipo_quarta'])
    atualizar_secao_quarta()
    root.after(300, lambda: aplicar_selecoes_salvas(dados))

def aplicar_selecoes_salvas(dados):
    if 'selecoes_segunda' in dados:
        for var, label, pedido in vars_labels_segunda:
            if pedido in dados['selecoes_segunda']:
                info = dados['selecoes_segunda'][pedido]
                var.set(info['marcado'])
                if info['marcado']:
                    label.config(bg=info.get('cor', SURFACE))
    if 'selecoes_quarta' in dados:
        for var, label, pedido in vars_labels_quarta:
            if pedido in dados['selecoes_quarta']:
                info = dados['selecoes_quarta'][pedido]
                var.set(info['marcado'])
                if info['marcado']:
                    label.config(bg=info.get('cor', SURFACE))

# ============================================================
# LÓGICA DE PRAZO (original intacta)
# ============================================================
def verificar_prazo(nome_pedido):
    agora = get_datetime_atual()
    dia   = agora.weekday()
    hora  = agora.hour
    minuto = agora.minute

    if nome_pedido in prazo_segunda:
        if dia < 0 or (dia == 0 and (hora < 8 or (hora == 8 and minuto <= 40))):
            return True
        return False

    if nome_pedido in entregas_internas or nome_pedido in entregas_externas:
        if dia < 2 or (dia == 2 and (hora < 12 or (hora == 12 and minuto <= 40))):
            return True
        return False

    return None

def on_check(var, label, nome_pedido, salvar=True):
    if var.get():
        resultado = verificar_prazo(nome_pedido)
        if resultado is True:
            label.config(bg="#1a3d2b", fg=GREEN_OK)    # verde escuro + texto verde
        elif resultado is False:
            label.config(bg="#3d1a24", fg=RED_LATE)    # vermelho escuro + texto vermelho
        else:
            label.config(bg=SURFACE2, fg=MUTED)
    else:
        label.config(bg=SURFACE, fg=TEXT)
    if salvar:
        salvar_dados()

# ============================================================
# CRIAÇÃO DE SEÇÃO — novo visual
# ============================================================
def criar_secao(titulo, pedidos, master_frame, lista_vars_labels, cor_acento=ACCENT):
    outer = tk.Frame(master_frame, bg=SURFACE, highlightthickness=1,
                     highlightbackground=BORDER, highlightcolor=BORDER)
    outer.pack(fill="x", pady=(0, 12), padx=2)

    # Header da seção
    header = tk.Frame(outer, bg=SURFACE2, height=40)
    header.pack(fill="x")
    header.pack_propagate(False)

    # Barra colorida lateral
    accent_bar = tk.Frame(header, bg=cor_acento, width=4)
    accent_bar.pack(side="left", fill="y")

    tk.Label(header, text=titulo, font=FONT_TITLE,
             bg=SURFACE2, fg=TEXT).pack(side="left", padx=14, pady=8)

    # Grid de itens
    grid_frame = tk.Frame(outer, bg=SURFACE)
    grid_frame.pack(padx=16, pady=12, fill="x")

    colunas = 3
    linha = 0
    coluna = 0

    for pedido in pedidos:
        var = tk.BooleanVar()

        item_frame = tk.Frame(grid_frame, bg=SURFACE, highlightthickness=1,
                              highlightbackground=BORDER, highlightcolor=ACCENT)
        item_frame.grid(row=linha, column=coluna, sticky="ew", padx=5, pady=4)
        grid_frame.columnconfigure(coluna, weight=1)

        cb = tk.Checkbutton(
            item_frame, variable=var,
            bg=SURFACE, activebackground=SURFACE2,
            selectcolor=SURFACE2,
            fg=ACCENT, activeforeground=ACCENT,
            cursor="hand2", relief="flat", bd=0
        )
        cb.pack(side="left", padx=(8, 2), pady=6)

        label = tk.Label(
            item_frame, text=pedido,
            font=FONT_NORMAL, bg=SURFACE, fg=TEXT,
            width=28, anchor="w", padx=4, pady=6
        )
        label.pack(side="left")

        cb.config(command=lambda v=var, l=label, p=pedido: on_check(v, l, p))
        lista_vars_labels.append((var, label, pedido))

        coluna += 1
        if coluna >= colunas:
            coluna = 0
            linha += 1

# ============================================================
# SEÇÃO QUARTA (original intacta, visual atualizado)
# ============================================================
def atualizar_secao_quarta():
    global vars_labels_quarta
    vars_labels_quarta.clear()
    for widget in quarta_frame.winfo_children():
        widget.destroy()

    tipo = opcao_quarta.get()
    if tipo == "internas":
        criar_secao("Entregas Internas  ·  prazo: quarta 12:40",
                    entregas_internas, quarta_frame, vars_labels_quarta, ACCENT2)
    elif tipo == "externas":
        criar_secao("Entregas Externas  ·  prazo: quarta 12:40",
                    entregas_externas, quarta_frame, vars_labels_quarta, AMBER)

def limpar_checkboxes_sem_salvar():
    for var, label, _ in vars_labels_segunda:
        var.set(False)
        label.config(bg=SURFACE, fg=TEXT)
    for var, label, _ in vars_labels_quarta:
        var.set(False)
        label.config(bg=SURFACE, fg=TEXT)

def limpar_selecoes():
    resposta = messagebox.askyesno(
        "Nova Semana",
        "⚠️ Tem certeza que deseja iniciar uma nova semana?\n\n"
        "Todas as seleções atuais serão perdidas!",
        icon='warning'
    )
    if resposta:
        limpar_checkboxes_sem_salvar()
        salvar_dados()
        messagebox.showinfo("Sucesso", "✅ Nova semana iniciada!\nTodos os checkboxes foram limpos.")

# ============================================================
# GERAÇÃO DE PDF (lógica original intacta)
# ============================================================
def gerar_relatorio_pdf():
    arquivo_pdf = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("Arquivos PDF", "*.pdf"), ("Todos os arquivos", "*.*")],
        initialfile=f"relatorio_semanal_{get_datetime_atual().strftime('%d%m%Y_%H%M')}.pdf"
    )
    if not arquivo_pdf:
        return

    inicio = data_referencia()
    fim = inicio + timedelta(days=4)
    periodo_str = f"{inicio.strftime('%d/%m/%Y')} a {fim.strftime('%d/%m/%Y')}"

    pendentes = []
    atrasadas = []

    for var, label, pedido in vars_labels_segunda:
        if not var.get():
            pendentes.append(pedido)
        else:
            if not verificar_prazo(pedido):
                atrasadas.append(pedido)

    for var, label, pedido in vars_labels_quarta:
        if not var.get():
            pendentes.append(pedido)
        else:
            if not verificar_prazo(pedido):
                atrasadas.append(pedido)

    total_selecionados = (len(vars_labels_segunda) + len(vars_labels_quarta)) - len(pendentes)
    total_recebido_no_prazo = total_selecionados - len(atrasadas)

    doc = SimpleDocTemplate(arquivo_pdf, pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)

    styles = getSampleStyleSheet()
    titulo_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'],
                                  fontSize=16, textColor=colors.HexColor('#2c3e50'),
                                  spaceAfter=30, alignment=TA_CENTER)
    subtitulo_style = ParagraphStyle('CustomSubtitle', parent=styles['Heading2'],
                                     fontSize=11, textColor=colors.grey,
                                     spaceAfter=20, alignment=TA_CENTER)
    heading_style = ParagraphStyle('Heading', parent=styles['Heading3'],
                                   fontSize=13, textColor=colors.HexColor('#34495e'),
                                   spaceAfter=12, spaceBefore=20)
    item_style = ParagraphStyle('Item', parent=styles['Normal'],
                                fontSize=10, leftIndent=20,
                                bulletIndent=10, spaceAfter=4)
    normal_style = styles['Normal']

    story = []
    story.append(Paragraph("RELATÓRIO SEMANAL - REQUISIÇÕES", titulo_style))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(f"Período: {periodo_str}", subtitulo_style))
    story.append(Paragraph(f"Data/Hora: {get_datetime_atual().strftime('%d/%m/%Y %H:%M')}", subtitulo_style))

    if MODO_SIMULACAO:
        story.append(Paragraph("⚠️ RELATÓRIO GERADO EM MODO DE SIMULAÇÃO ⚠️",
                                ParagraphStyle('Warning', parent=normal_style,
                                               textColor=colors.red, alignment=TA_CENTER)))

    story.append(Spacer(1, 0.5*cm))

    resumo_data = [
        ['Total de requisições:', str(total_selecionados)],
        ['✅ Recebidas no prazo:', str(total_recebido_no_prazo)],
        ['⚠️ Atrasadas:', str(len(atrasadas))],
        ['📌 Pendentes:', str(len(pendentes))]
    ]
    resumo_table = Table(resumo_data, colWidths=[10*cm, 3*cm])
    resumo_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 11),
        ('TEXTCOLOR', (0,0), (0,-1), colors.HexColor('#2c3e50')),
        ('TEXTCOLOR', (1,0), (1,-1), colors.HexColor('#2980b9')),
        ('ALIGN', (1,0), (1,-1), 'RIGHT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(resumo_table)
    story.append(Spacer(1, 0.5*cm))

    if pendentes:
        story.append(Paragraph("📌 REQUISIÇÕES PENDENTES", heading_style))
        for item in sorted(pendentes):
            story.append(Paragraph(f"• {item}", item_style))
        story.append(Spacer(1, 0.3*cm))
    else:
        story.append(Paragraph("📌 Todas as requisições foram solicitadas!",
                                ParagraphStyle('Success', parent=heading_style,
                                               textColor=colors.green)))

    if atrasadas:
        story.append(Paragraph("⚠️ REQUISIÇÕES ATRASADAS", heading_style))
        for item in sorted(atrasadas):
            story.append(Paragraph(f"• {item}", item_style))
        story.append(Spacer(1, 0.3*cm))
    else:
        story.append(Paragraph("✅ Nenhuma requisição atrasada!",
                                ParagraphStyle('Success', parent=heading_style,
                                               textColor=colors.green)))

    story.append(Spacer(1, 1*cm))
    story.append(Paragraph("Observações:", heading_style))
    story.append(Paragraph("Atenciosamente,", normal_style))
    story.append(Paragraph("Lucas Godoy", normal_style))
    story.append(Paragraph("Auxiliar de almoxarifado", normal_style))

    try:
        doc.build(story)
        messagebox.showinfo("Sucesso", f"✅ PDF gerado com sucesso!\n\n📁 Salvo em:\n{arquivo_pdf}")
    except Exception as e:
        messagebox.showerror("Erro", f"❌ Erro ao gerar PDF:\n{str(e)}")

# ============================================================
# JANELA PRINCIPAL
# ============================================================
root = tk.Tk()
root.title("Controle de Requisições — Almoxarifado")
root.geometry("1140x820")
root.configure(bg=BG)
root.minsize(900, 600)

style = ttk.Style()
style.theme_use('clam')
style.configure("Dark.Vertical.TScrollbar",
                troughcolor=SURFACE, background=BORDER,
                arrowcolor=MUTED, bordercolor=SURFACE,
                lightcolor=SURFACE, darkcolor=SURFACE)
style.map("Dark.Vertical.TScrollbar",
          background=[('active', ACCENT), ('!active', BORDER)])

# ── Scrollable canvas ──────────────────────────────────────
main_container = tk.Frame(root, bg=BG)
main_container.pack(fill="both", expand=True)

canvas = tk.Canvas(main_container, bg=BG, highlightthickness=0)
scrollbar = ttk.Scrollbar(main_container, orient="vertical",
                          command=canvas.yview, style="Dark.Vertical.TScrollbar")
scrollable_frame = tk.Frame(canvas, bg=BG)

MAX_WIDTH = 1100  # largura máxima do conteúdo

def _on_frame_configure(e):
    canvas.configure(scrollregion=canvas.bbox("all"))

def _on_canvas_configure(e):
    w = min(e.width, MAX_WIDTH)
    canvas.itemconfig(canvas_window, width=w)
    x = e.width // 2
    canvas.coords(canvas_window, x, 0)

scrollable_frame.bind("<Configure>", _on_frame_configure)
canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="n")
canvas.bind("<Configure>", _on_canvas_configure)
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# Mousewheel
def _on_mousewheel(event):
    canvas.yview_scroll(int(-1*(event.delta/120)), "units")
canvas.bind_all("<MouseWheel>", _on_mousewheel)

# ── HEADER ─────────────────────────────────────────────────
header_frame = tk.Frame(scrollable_frame, bg="#0d1020", height=80)
header_frame.pack(fill="x")
header_frame.pack_propagate(False)

# Linha decorativa no topo do header (gradiente simulado via múltiplos frames)
stripe = tk.Frame(header_frame, bg=ACCENT, height=3)
stripe.pack(fill="x", side="top")

header_inner = tk.Frame(header_frame, bg="#0d1020")
header_inner.pack(fill="both", expand=True, padx=24)

tk.Label(header_inner,
         text="CONTROLE DE REQUISIÇÕES",
         font=("Segoe UI", 17, "bold"),
         bg="#0d1020", fg=TEXT).pack(side="left", pady=18)

tk.Label(header_inner,
         text="Almoxarifado",
         font=FONT_SMALL,
         bg="#0d1020", fg=MUTED).pack(side="left", padx=(10, 0), pady=22)

# Badge simulação
if MODO_SIMULACAO:
    sim_badge = tk.Label(header_inner,
                         text=f"  ⚠  SIMULAÇÃO: {get_datetime_atual().strftime('%d/%m/%Y %H:%M')}  ",
                         font=FONT_SMALL, bg="#3d1a0a", fg="#f97316",
                         relief="flat", padx=6, pady=2)
    sim_badge.pack(side="right", pady=22)

# ── INFO SEMANA ─────────────────────────────────────────────
info_bar = tk.Frame(scrollable_frame, bg=SURFACE2, height=34)
info_bar.pack(fill="x")
info_bar.pack_propagate(False)

semana_atual = data_referencia()
fim_semana   = semana_atual + timedelta(days=4)
info_text = (f"  📅  Semana:  "
             f"{semana_atual.strftime('%d/%m/%Y')}  →  {fim_semana.strftime('%d/%m/%Y')}")
tk.Label(info_bar, text=info_text, font=FONT_SMALL,
         bg=SURFACE2, fg=MUTED).pack(side="left", pady=6, padx=8)

sep = tk.Frame(scrollable_frame, bg=BORDER, height=1)
sep.pack(fill="x")

# ── CONTEÚDO ─────────────────────────────────────────────────
content = tk.Frame(scrollable_frame, bg=BG)
content.pack(fill="both", expand=True, padx=20, pady=20)

# Seção segunda-feira
criar_secao("Segunda-feira  ·  prazo: 08:40",
            prazo_segunda, content, vars_labels_segunda, ACCENT)

# ── SELETOR DE QUARTA ────────────────────────────────────────
seletor_outer = tk.Frame(content, bg=SURFACE, highlightthickness=1,
                         highlightbackground=BORDER)
seletor_outer.pack(fill="x", pady=(0, 12), padx=2)

seletor_header = tk.Frame(seletor_outer, bg=SURFACE2, height=40)
seletor_header.pack(fill="x")
seletor_header.pack_propagate(False)

accent_bar2 = tk.Frame(seletor_header, bg=ACCENT2, width=4)
accent_bar2.pack(side="left", fill="y")

tk.Label(seletor_header, text="Quarta-feira  ·  tipo de entrega",
         font=FONT_TITLE, bg=SURFACE2, fg=TEXT).pack(side="left", padx=14)

seletor_btns = tk.Frame(seletor_outer, bg=SURFACE)
seletor_btns.pack(pady=10, padx=16, anchor="w")

opcao_quarta = tk.StringVar(value="internas")

def _btn_internas():
    opcao_quarta.set("internas")
    btn_int.config(bg=ACCENT2, fg="white")
    btn_ext.config(bg=SURFACE2, fg=MUTED)
    atualizar_secao_quarta()

def _btn_externas():
    opcao_quarta.set("externas")
    btn_ext.config(bg=AMBER, fg="white")
    btn_int.config(bg=SURFACE2, fg=MUTED)
    atualizar_secao_quarta()

btn_int = tk.Button(seletor_btns, text="Entregas Internas",
                    command=_btn_internas,
                    font=FONT_NORMAL, bg=ACCENT2, fg="white",
                    cursor="hand2", padx=16, pady=6,
                    relief="flat", activebackground=ACCENT2, activeforeground="white",
                    bd=0)
btn_int.pack(side="left", padx=(0, 8))

btn_ext = tk.Button(seletor_btns, text="Entregas Externas",
                    command=_btn_externas,
                    font=FONT_NORMAL, bg=SURFACE2, fg=MUTED,
                    cursor="hand2", padx=16, pady=6,
                    relief="flat", activebackground=SURFACE2, activeforeground=TEXT,
                    bd=0)
btn_ext.pack(side="left")

# Frame dinâmico da quarta
quarta_frame = tk.Frame(content, bg=BG)
quarta_frame.pack(fill="x")

# ── BOTÕES DE AÇÃO ───────────────────────────────────────────
sep2 = tk.Frame(content, bg=BORDER, height=1)
sep2.pack(fill="x", pady=(16, 0))

botoes_frame = tk.Frame(content, bg=BG)
botoes_frame.pack(pady=16, anchor="w")

btn_nova_semana = tk.Button(
    botoes_frame, text="  🔄  Nova Semana",
    command=limpar_selecoes,
    font=FONT_NORMAL,
    bg="#3d2010", fg="#f97316",
    cursor="hand2", padx=18, pady=8,
    relief="flat", bd=0,
    activebackground="#4a2a14", activeforeground="#f97316"
)
btn_nova_semana.pack(side="left", padx=(0, 10))

btn_pdf = tk.Button(
    botoes_frame, text="  📄  Gerar Relatório PDF",
    command=gerar_relatorio_pdf,
    font=FONT_NORMAL,
    bg="#0f2d1a", fg=GREEN_OK,
    cursor="hand2", padx=18, pady=8,
    relief="flat", bd=0,
    activebackground="#163d24", activeforeground=GREEN_OK
)
btn_pdf.pack(side="left")

# ── LEGENDA ──────────────────────────────────────────────────
legenda_outer = tk.Frame(content, bg=SURFACE, highlightthickness=1,
                         highlightbackground=BORDER)
legenda_outer.pack(fill="x", pady=(4, 16), padx=2)

legenda_inner = tk.Frame(legenda_outer, bg=SURFACE)
legenda_inner.pack(padx=16, pady=10, anchor="w")

tk.Label(legenda_inner, text="Legenda", font=("Segoe UI", 9, "bold"),
         bg=SURFACE, fg=MUTED).pack(side="left", padx=(0, 16))

for cor, txt in [(GREEN_OK, "No prazo"), (RED_LATE, "Atrasado"), (BORDER, "Não requisitado")]:
    dot = tk.Frame(legenda_inner, bg=cor, width=12, height=12)
    dot.pack(side="left", padx=(0, 5))
    dot.pack_propagate(False)
    tk.Label(legenda_inner, text=txt, font=FONT_SMALL,
             bg=SURFACE, fg=MUTED).pack(side="left", padx=(0, 18))

# ── RODAPÉ ───────────────────────────────────────────────────
footer = tk.Frame(scrollable_frame, bg=SURFACE2, height=32)
footer.pack(fill="x", side="bottom")
footer.pack_propagate(False)

tk.Label(footer,
         text="Desenvolvido por Lucas Godoy  ·  Auxiliar de Almoxarifado",
         font=FONT_SMALL, bg=SURFACE2, fg=MUTED).pack(side="left", padx=20, pady=6)

# ── INICIALIZAÇÃO ────────────────────────────────────────────
atualizar_secao_quarta()

def on_closing():
    salvar_dados()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)
root.after(500, restaurar_selecoes)
root.mainloop()