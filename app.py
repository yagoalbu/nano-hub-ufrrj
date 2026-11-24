from datetime import date, datetime, time
from pathlib import Path
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from supabase import create_client
from datetime import date, datetime, time
from zoneinfo import ZoneInfo

st.set_page_config(
    page_title="NaNo Hub | UFRRJ",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------- Identidade visual NaNo & UFRRJ ----------
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap');
:root { --nano-blue:#0879A8; --nano-blue-dark:#075477; --nano-orange:#F28C00; --nano-ink:#172B3A; }
html, body, [class*="css"] { font-family:'DM Sans',sans-serif; }
.stApp { background:#F4F7FA; color:var(--nano-ink); }

/* Botão nativo de abrir/fechar sidebar destacado */
[data-testid="collapsedControl"] {
    background: #075477 !important;
    color: #FFFFFF !important;
    border-radius: 10px !important;
    margin: 10px 0 0 12px !important;
    padding: 4px 8px !important;
    box-shadow: 0 4px 12px rgba(7, 84, 119, 0.25) !important;
}
[data-testid="collapsedControl"] svg { fill: #FFFFFF !important; }

/* Sidebar e Botões de Navegação Reais (Sem bolinhas!) */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #06354E 0%, #075477 100%);
    border-right: 1px solid rgba(255, 255, 255, 0.1);
}
[data-testid="stSidebar"] * { color: #F5FAFD !important; }

[data-testid="stSidebar"] .stButton > button {
    width: 100% !important;
    justify-content: flex-start !important;
    text-align: left !important;
    padding: 0.65rem 0.95rem !important;
    border-radius: 11px !important;
    background: rgba(255, 255, 255, 0.06) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    color: #E6F2F8 !important;
    font-weight: 500 !important;
    font-size: 0.95rem !important;
    transition: all 0.2s ease !important;
    box-shadow: none !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255, 255, 255, 0.15) !important;
    border-color: rgba(255, 255, 255, 0.25) !important;
    transform: translateX(4px);
}
/* Botão da página ativa (type="primary" dentro da sidebar) */
[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: linear-gradient(90deg, rgba(242, 140, 0, 0.32) 0%, rgba(255, 255, 255, 0.16) 100%) !important;
    border: 1px solid rgba(242, 140, 0, 0.65) !important;
    border-left: 5px solid #F28C00 !important;
    color: #FFFFFF !important;
    font-weight: 700 !important;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.2) !important;
}

/* Botão customizado de abrir menu no topo da tela */
.menu-trigger-wrap button {
    background: #FFFFFF !important;
    color: #075477 !important;
    border: 1px solid #D5E1EA !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    padding: 0.45rem 1rem !important;
    box-shadow: 0 2px 8px rgba(18, 54, 75, 0.06) !important;
}
.menu-trigger-wrap button:hover {
    border-color: #0879A8 !important;
    background: #EEF6FA !important;
}

.block-container { max-width:1480px; padding-top:1.4rem; padding-bottom:3rem; }
h1,h2,h3 { color:#12364B; letter-spacing:-.03em; }
div[data-testid="stMetric"] { background:white; border:1px solid #E2EAF0; border-radius:15px; padding:16px 18px; box-shadow:0 3px 14px rgba(18,54,75,.04); }
div[data-testid="stMetricLabel"] { color:#627789; font-weight:600; }
div[data-testid="stMetricValue"] { color:#075477; }
.stButton > button[kind="primary"], .stFormSubmitButton > button { background:#0879A8; border:0; border-radius:9px; color:white; font-weight:700; }
.stButton > button[kind="primary"]:hover, .stFormSubmitButton > button:hover { background:#075477; color:white; }
.stButton > button { border-radius:9px; }
[data-testid="stTabs"] button[aria-selected="true"] { color:#0879A8; border-bottom-color:#F28C00; }
.nano-hero { background:linear-gradient(115deg,#064D70 0%,#0879A8 72%,#1596B8 100%); color:white; padding:26px 30px; border-radius:18px; margin-bottom:22px; box-shadow:0 9px 26px rgba(7,84,119,.15); }
.nano-hero h1 { color:white; margin:0; font-size:30px; }
.nano-hero p { color:#D9EDF5; margin:6px 0 0 0; }
.section-kicker { color:#F28C00; text-transform:uppercase; font-size:11px; font-weight:800; letter-spacing:.13em; }
.panel { background:white; border:1px solid #E2EAF0; border-radius:15px; padding:18px 20px; margin-bottom:12px; }
.small-muted { color:#718596; font-size:13px; }
.orange-line { height:4px; width:46px; background:#F28C00; border-radius:8px; margin:9px 0 15px; }
</style>
""",
    unsafe_allow_html=True,
)

ROOT = Path(__file__).parent
LOGO = ROOT / "assets" / "logo_nano_ufrrj.png"

# ---------- Controle de Acesso (Senha Única do Laboratório) ----------
if "autenticado" not in st.session_state:
  st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
  _, col_login, _ = st.columns([1.2, 1.6, 1.2])
  with col_login:
    st.write("")
    st.write("")
    with st.container(border=True):
      if LOGO.exists():
        st.image(str(LOGO), use_container_width=True)
      st.markdown(
          "<h2 style='text-align:center; margin-bottom:2px;'>NaNo Hub</h2>",
          unsafe_allow_html=True,
      )
      st.markdown(
          "<p style='text-align:center; color:#627789; font-size:14px;"
          " margin-bottom:18px;'>Acesso restrito à equipe do laboratório •"
          " UFRRJ</p>",
          unsafe_allow_html=True,
      )

      with st.form("form_login_lab"):
        senha_digitada = st.text_input(
            "Senha de acesso do laboratório",
            type="password",
            placeholder="Digite o código de acesso",
        )
        entrar = st.form_submit_button(
            "Entrar no Painel", type="primary", use_container_width=True
        )

        if entrar:
          senha_correta = st.secrets.get("LAB_PASSWORD", "nano2026")
          if senha_digitada == senha_correta:
            st.session_state["autenticado"] = True
            st.rerun()
          else:
            st.error("Senha incorreta. Verifique com a coordenação do NaNo.")
  st.stop()


@st.cache_resource
def get_supabase():
  url = st.secrets.get("SUPABASE_URL", "")
  key = st.secrets.get("SUPABASE_KEY", "")
  if not url or not key:
    return None
  return create_client(url, key)


db = get_supabase()


def rows(table, order=None, descending=False):
  if db is None:
    return []
  q = db.table(table).select("*")
  if order:
    q = q.order(order, desc=descending)
  return q.execute().data or []


def insert(table, payload):
  if db is None:
    raise RuntimeError("Configure o Supabase em .streamlit/secrets.toml.")
  return db.table(table).insert(payload).execute()


def delete(table, record_id):
  if db is None:
    raise RuntimeError("Supabase não configurado.")
  return db.table(table).delete().eq("id", record_id).execute()


def update(table, record_id, payload):
  if db is None:
    raise RuntimeError("Supabase não configurado.")
  return db.table(table).update(payload).eq("id", record_id).execute()


def safe_date(value):
  try:
    return date.fromisoformat(str(value)[:10])
  except Exception:
    return None


def page_header(kicker, title, subtitle):
  st.markdown(
      f'<div class="section-kicker">{kicker}</div><h1>{title}</h1><p'
      f' class="small-muted">{subtitle}</p><div class="orange-line"></div>',
      unsafe_allow_html=True,
  )


def show_table(data, columns=None):
  if not data:
    st.info("Ainda não há registros cadastrados.")
    return
  df = pd.DataFrame(data)
  if columns:
    df = df[[c for c in columns if c in df.columns]]
  st.dataframe(df, use_container_width=True, hide_index=True)


def delete_widget(table, records, label_fn, key):
  if not records:
    return
  with st.expander("⚙️ Gerenciar / excluir registros"):
    opts = {label_fn(r): r["id"] for r in records if r.get("id") is not None}
    if opts:
      chosen = st.selectbox(
          "Selecione o registro", list(opts), key=f"{key}_sel"
      )
      if st.button("Excluir registro", key=f"{key}_del"):
        try:
          delete(table, opts[chosen])
          st.success("Registro excluído.")
          st.rerun()
        except Exception as e:
          st.error(f"Não foi possível excluir: {e}")


if db is None:
  with st.sidebar:
    if LOGO.exists():
      st.image(str(LOGO), use_container_width=True)
    st.markdown("### NaNo Hub")
    st.caption("UFRRJ • Gestão laboratorial")
  st.markdown(
      '<div class="nano-hero"><div class="section-kicker">NaNo &'
      " UFRRJ</div><h1>Seu laboratório, conectado.</h1><p>Organização de"
      " pessoas, equipamentos, materiais e conhecimento"
      " científico.</p></div>",
      unsafe_allow_html=True,
  )
  st.warning(
      "O aplicativo está pronto, mas ainda precisa da conexão com o Supabase."
  )
  st.markdown(
      "**Para conectar:** crie `.streamlit/secrets.toml` a partir do arquivo"
      " `secrets.toml.example` e informe a URL e a chave do seu projeto"
      " Supabase."
  )
  st.code(
      'SUPABASE_URL = "https://SEU-PROJETO.supabase.co"\nSUPABASE_KEY ='
      ' "SUA_CHAVE_ANON"',
      language="toml",
  )
  st.stop()

# Dados carregados para os indicadores e páginas
try:
  researchers = rows("pesquisadores", "nome")
  equipment = rows("equipamentos", "nome")
  reservations = rows("reservas_equipamentos", "data_uso")
  inventory = rows("estoque_insumos", "nome")
  projects = rows("projetos", "created_at", True)
  notices = rows("mural_avisos", "id", True)
  experiments = rows("experimentos", "data_experimento", True)
  documents = rows("biblioteca", "created_at", True)
except Exception as e:
  st.error(f"Falha ao consultar o banco de dados: {e}")
  st.info("Confira se o SQL de criação das tabelas foi executado no Supabase.")
  st.stop()

today = date.today()
today_res = [r for r in reservations if safe_date(r.get("data_uso")) == today]
low_stock = [
    i
    for i in inventory
    if i.get("quantidade_minima") is not None
    and float(i.get("quantidade_atual") or 0)
    <= float(i["quantidade_minima"])
]

# Controle da página ativa na sessão
if "pagina_ativa" not in st.session_state:
  st.session_state["pagina_ativa"] = "Visão geral"

# ---------- Barra Superior com Botão de Menu ----------
top_col1, top_col2 = st.columns([1.4, 8.6])
with top_col1:
  st.markdown('<div class="menu-trigger-wrap">', unsafe_allow_html=True)
  if st.button("☰ Menu", key="btn_toggle_sidebar", use_container_width=True):
    components.html(
        """
            <script>
            const doc = window.parent.document;
            const btn = doc.querySelector('[data-testid="collapsedControl"] button') 
                     || doc.querySelector('[data-testid="stSidebarCollapseButton"] button')
                     || doc.querySelector('button[aria-label*="sidebar" i]')
                     || doc.querySelector('button[aria-label*="navigation" i]');
            if (btn) btn.click();
            </script>
            """,
        height=0,
        width=0,
    )
  st.markdown("</div>", unsafe_allow_html=True)

# ---------- Menu Lateral Único (Botões Modernos sem Emojis) ----------
NAV_ITEMS = [
    "Visão geral",
    "Pesquisadores",
    "Escala e agenda",
    "Equipamentos",
    "Estoque",
    "Projetos",
    "Caderno experimental",
    "Biblioteca científica",
    "Mural de avisos",
]

with st.sidebar:
  if LOGO.exists():
    st.image(str(LOGO), use_container_width=True)
  st.markdown("### NaNo Hub")
  st.caption("Plataforma de gestão • UFRRJ")
  st.markdown("---")

  for nome_pag in NAV_ITEMS:
    ativo = st.session_state["pagina_ativa"] == nome_pag
    if st.button(
        nome_pag,
        key=f"nav_btn_{nome_pag}",
        type="primary" if ativo else "secondary",
        use_container_width=True,
    ):
      st.session_state["pagina_ativa"] = nome_pag
      st.rerun()

  st.divider()
  st.caption(f"📅 {today.strftime('%d/%m/%Y')}")
  st.caption("NaNo & UFRRJ")

menu = st.session_state["pagina_ativa"]

# ---------- Visão geral ----------

if menu == "Visão geral":
    hora_atual = datetime.now(ZoneInfo("America/Sao_Paulo")).hour
    if 5 <= hora_atual < 12:
        saudacao = "Bom dia"
    elif 12 <= hora_atual < 18:
        saudacao = "Boa tarde"
    else:
        saudacao = "Boa noite"

    st.markdown(
        f'<div class="nano-hero"><div class="section-kicker">Painel'
        f" operacional</div><h1>{saudacao}, equipe NaNo.</h1><p>Acompanhe a"
        f" rotina do laboratório em um só lugar.</p></div>",
        unsafe_allow_html=True,
    )
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Pesquisadores", len(researchers), help="Pessoas cadastradas")
    c2.metric("Reservas hoje", len(today_res), help="Uso de equipamentos na data de hoje")
    c3.metric("Equipamentos", len(equipment))
    c4.metric("Alertas de estoque", len(low_stock), delta="Atenção" if low_stock else "Tudo em ordem", delta_color="inverse" if low_stock else "normal")
    left,right = st.columns([1.15, .85])
    with left:
        st.subheader("Agenda de hoje")
        if today_res:
            for r in today_res:
                st.markdown(f'<div class="panel"><b>🔬 {r.get("equipamento_nome") or r.get("equipamento") or "Equipamento"}</b><br><span class="small-muted">{r.get("hora_inicio","")}–{r.get("hora_fim","")} • {r.get("pesquisador","")}</span></div>', unsafe_allow_html=True)
        else: st.info("Nenhuma reserva registrada para hoje.")
        st.subheader("Projetos recentes")
        for p in projects[:4]:
            st.markdown(f'<div class="panel"><b>{p.get("titulo","Projeto sem título")}</b><br><span class="small-muted">{p.get("responsavel","")} • {p.get("status","Em andamento")}</span></div>', unsafe_allow_html=True)
    with right:
        st.subheader("Atenção ao estoque")
        if low_stock:
            for item in low_stock[:6]:
                st.warning(f"{item.get('nome')} — {item.get('quantidade_atual')} {item.get('unidade','')} (mínimo: {item.get('quantidade_minima')})")
        else: st.success("Nenhum item abaixo do estoque mínimo.")
        st.subheader("Avisos recentes")
        if notices:
            for n in notices[:4]:
                st.markdown(f'<div class="panel"><b>{n.get("categoria","Aviso")}</b><br>{n.get("mensagem","")}<br><span class="small-muted">Por {n.get("autor","")}</span></div>', unsafe_allow_html=True)
        else: st.info("O mural está vazio.")
    st.subheader("Panorama de utilização")
    if reservations:
        df = pd.DataFrame(reservations)
        if "equipamento" in df.columns:
            st.bar_chart(df["equipamento"].value_counts(), color="#0879A8")
    else: st.caption("Os gráficos serão preenchidos conforme as reservas forem cadastradas.")

# ---------- Pesquisadores ----------
elif menu == "Pesquisadores":
    page_header("Equipe", "Pesquisadores", "Cadastro e organização das pessoas vinculadas ao laboratório.")
    with st.expander("＋ Cadastrar pesquisador", expanded=False):
        with st.form("new_researcher"):
            a,b = st.columns(2)
            nome = a.text_input("Nome completo *")
            email = b.text_input("E-mail")
            vinculo = a.selectbox("Vínculo", ["Iniciação científica", "Iniciação tecnológica", "Mestrado", "Doutorado", "Pós-doutorado", "Docente", "Técnico", "Outro"])
            projeto = b.text_input("Projeto / linha de pesquisa")
            ativo = st.selectbox("Situação", ["Ativo", "Afastado", "Concluído"])
            submitted = st.form_submit_button("Salvar pesquisador", type="primary")
            if submitted:
                if not nome.strip(): st.error("Informe o nome.")
                else:
                    try: insert("pesquisadores", {"nome":nome.strip(),"email":email.strip(),"vinculo":vinculo,"projeto":projeto.strip(),"situacao":ativo}); st.success("Pesquisador cadastrado."); st.rerun()
                    except Exception as e: st.error(str(e))
    show_table(researchers, ["nome","email","vinculo","projeto","situacao"])
    delete_widget("pesquisadores", researchers, lambda r:f'{r.get("nome")} • {r.get("vinculo","")}', "researcher")

# ---------- Escala e agenda ----------
elif menu == "Escala e agenda":
  page_header(
      "Planejamento",
      "Escala e agenda",
      "Organize a presença da equipe e as reservas de equipamentos.",
  )
  tab1, tab2 = st.tabs(["Escala semanal", "Reservas"])
  with tab1:
    days = [
        "Segunda-feira",
        "Terça-feira",
        "Quarta-feira",
        "Quinta-feira",
        "Sexta-feira",
    ]
    with st.expander("＋ Adicionar à escala"):
      with st.form("new_shift"):
        a, b = st.columns(2)
        who = a.selectbox(
            "Pesquisador",
            [r["nome"] for r in researchers]
            or ["Cadastre pesquisadores primeiro"],
        )
        selected_days = b.multiselect(
            "Dias da semana (selecione um ou mais)",
            days,
            placeholder="Ex: Segunda-feira, Quarta-feira, Quinta-feira",
        )
        shift = a.selectbox(
            "Turno",
            ["Manhã (08h–12h)", "Tarde (13h–17h)", "Integral (08h–17h)"],
        )
        activity = b.text_input("Atividade / bancada")
        if st.form_submit_button("Adicionar escala", type="primary"):
          if not selected_days:
            st.error("Selecione pelo menos um dia da semana.")
          elif who == "Cadastre pesquisadores primeiro":
            st.error("Cadastre os pesquisadores antes de montar a escala.")
          else:
            try:
              for d_sel in selected_days:
                insert(
                    "escala_laboratorio",
                    {
                        "pesquisador": who,
                        "dia_semana": d_sel,
                        "turno": shift,
                        "atividade": activity,
                    },
                )
              st.success(f"Escala adicionada para {', '.join(selected_days)}.")
              st.rerun()
            except Exception as e:
              st.error(str(e))
    shifts = rows("escala_laboratorio")
    cols = st.columns(5)
    for idx, d in enumerate(days):
      with cols[idx]:
        st.markdown(f"**{d.replace('-feira','')}**")
        for s in [x for x in shifts if x.get("dia_semana") == d]:
          st.markdown(
              f'<div class="panel"><b>{s.get("pesquisador")}</b><br><span'
              f' class="small-muted">{s.get("turno","")}</span><br><span'
              f' class="small-muted">{s.get("atividade","")}</span></div>',
              unsafe_allow_html=True,
          )
    delete_widget(
        "escala_laboratorio",
        shifts,
        lambda r: (
            f'{r.get("pesquisador")} • {r.get("dia_semana")} • {r.get("turno")}'
        ),
        "shift",
    )
  with tab2:
    st.subheader("Reservar equipamento")
    equip_names = [e["nome"] for e in equipment]
    with st.form("new_reservation"):
      a, b = st.columns(2)
      person = a.selectbox(
          "Responsável",
          [r["nome"] for r in researchers] or ["Pesquisador não cadastrado"],
      )
      eq = b.selectbox(
          "Equipamento", equip_names or ["Cadastre equipamentos primeiro"]
      )
      d = a.date_input("Data de uso", min_value=today)
      note = b.text_input("Objetivo / observação")
      x, y = st.columns(2)
      start = x.time_input("Início", value=time(9, 0))
      end = y.time_input("Término", value=time(12, 0))
      if st.form_submit_button("Solicitar reserva", type="primary"):
        if end <= start:
          st.error("O término deve ser posterior ao início.")
        elif not equip_names:
          st.error("Cadastre equipamentos antes de reservar.")
        else:
          collision = any(
              r.get("equipamento") == eq
              and safe_date(r.get("data_uso")) == d
              and str(r.get("hora_inicio", "")) < end.strftime("%H:%M:%S")
              and str(r.get("hora_fim", "")) > start.strftime("%H:%M:%S")
              for r in reservations
          )
          if collision:
            st.error(
                "Já existe uma reserva sobreposta para esse equipamento."
                " Atualize a página e tente outro horário."
            )
          else:
            try:
              insert(
                  "reservas_equipamentos",
                  {
                      "pesquisador": person,
                      "equipamento": eq,
                      "data_uso": d.isoformat(),
                      "hora_inicio": start.strftime("%H:%M"),
                      "hora_fim": end.strftime("%H:%M"),
                      "observacao": note,
                  },
              )
              st.success("Reserva registrada.")
              st.rerun()
            except Exception as e:
              st.error(str(e))
    show_table(
        reservations,
        [
            "data_uso",
            "hora_inicio",
            "hora_fim",
            "equipamento",
            "pesquisador",
            "observacao",
        ],
    )
    delete_widget(
        "reservas_equipamentos",
        reservations,
        lambda r: (
            f'{r.get("data_uso")} • {r.get("equipamento")} •'
            f' {r.get("pesquisador")}'
        ),
        "reservation",
    )

# ---------- Equipamentos ----------
elif menu == "Equipamentos":
    page_header("Infraestrutura", "Equipamentos", "Cadastro, disponibilidade e acompanhamento da infraestrutura.")
    with st.expander("＋ Cadastrar equipamento"):
        with st.form("new_equipment"):
            a,b = st.columns(2)
            name = a.text_input("Nome do equipamento *")
            category = b.selectbox("Categoria", ["Impressão 3D","Eletroquímica","Preparação de amostras","Caracterização","Armazenamento","Outro"])
            location = a.text_input("Localização / bancada")
            status = b.selectbox("Status", ["Disponível","Em manutenção","Indisponível"])
            details = st.text_area("Descrição / observações")
            if st.form_submit_button("Salvar equipamento", type="primary"):
                if not name.strip(): st.error("Informe o nome.")
                else:
                    try: insert("equipamentos", {"nome":name.strip(),"categoria":category,"localizacao":location,"status":status,"descricao":details}); st.success("Equipamento cadastrado."); st.rerun()
                    except Exception as e: st.error(str(e))
    show_table(equipment, ["nome","categoria","localizacao","status","descricao"])
    delete_widget("equipamentos", equipment, lambda r:f'{r.get("nome")} • {r.get("localizacao","")}', "equipment")

# ---------- Estoque ----------
elif menu == "Estoque":
    page_header("Materiais", "Estoque de reagentes e insumos", "Acompanhe quantidades, validade e níveis mínimos.")
    with st.expander("＋ Cadastrar item no estoque"):
        with st.form("new_stock"):
            a,b,c = st.columns(3)
            name = a.text_input("Nome do reagente / insumo *")
            category = b.selectbox("Categoria", ["Reagente","Solvente","Consumível","Peça","Filamento","Outro"])
            unit = c.selectbox("Unidade", ["g","kg","mg","mL","L","unidade","frasco","rolo"])
            qty = a.number_input("Quantidade atual", min_value=0.0, step=1.0)
            minimum = b.number_input("Estoque mínimo", min_value=0.0, step=1.0)
            expiry = c.date_input("Validade (opcional)", value=None)
            lot = a.text_input("Lote")
            supplier = b.text_input("Fornecedor")
            location = c.text_input("Local de armazenamento")
            if st.form_submit_button("Salvar item", type="primary"):
                if not name.strip(): st.error("Informe o nome.")
                else:
                    payload={"nome":name.strip(),"categoria":category,"unidade":unit,"quantidade_atual":qty,"quantidade_minima":minimum,"lote":lot,"fornecedor":supplier,"localizacao":location}
                    if expiry: payload["validade"]=expiry.isoformat()
                    try: insert("estoque_insumos",payload); st.success("Item cadastrado."); st.rerun()
                    except Exception as e: st.error(str(e))
    if low_stock:
        st.warning(f"{len(low_stock)} item(ns) no nível mínimo ou abaixo dele.")
    show_table(inventory, ["nome","categoria","quantidade_atual","unidade","quantidade_minima","validade","lote","localizacao"])
    delete_widget("estoque_insumos", inventory, lambda r:f'{r.get("nome")} • lote {r.get("lote","—")}', "stock")

# ---------- Projetos ----------
elif menu == "Projetos":
    page_header("Pesquisa", "Projetos", "Centralize informações, responsáveis e andamento das pesquisas.")
    with st.expander("＋ Criar projeto"):
        with st.form("new_project"):
            title = st.text_input("Título do projeto *")
            a,b = st.columns(2)
            lead = a.text_input("Responsável")
            funding = b.text_input("Agência / financiamento")
            status = a.selectbox("Status", ["Planejamento","Em andamento","Em análise","Concluído","Pausado"])
            start_date = b.date_input("Data de início")
            summary = st.text_area("Resumo / objetivo")
            if st.form_submit_button("Criar projeto", type="primary"):
                if not title.strip(): st.error("Informe o título.")
                else:
                    try: insert("projetos", {"titulo":title.strip(),"responsavel":lead,"financiamento":funding,"status":status,"data_inicio":start_date.isoformat(),"resumo":summary}); st.success("Projeto criado."); st.rerun()
                    except Exception as e: st.error(str(e))
    show_table(projects, ["titulo","responsavel","financiamento","status","data_inicio","resumo"])
    delete_widget("projetos", projects, lambda r:r.get("titulo","Projeto"), "project")

# ---------- Caderno experimental ----------
elif menu == "Caderno experimental":
    page_header("Registro científico", "Caderno experimental", "Documente procedimentos, parâmetros e resultados com rastreabilidade.")
    with st.expander("＋ Registrar experimento", expanded=True):
        with st.form("new_experiment"):
            title = st.text_input("Nome do experimento *")
            a,b = st.columns(2)
            project_opts = [p["titulo"] for p in projects]
            project = a.selectbox("Projeto relacionado", ["Não vinculado"] + project_opts)
            researcher = b.selectbox("Responsável", [r["nome"] for r in researchers] or ["Não cadastrado"])
            exp_date = a.date_input("Data do experimento")
            stage = b.selectbox("Etapa", ["Planejamento","Preparação","Execução","Análise","Concluído"])
            materials = st.text_area("Materiais, reagentes e formulação")
            method = st.text_area("Procedimento experimental")
            results = st.text_area("Resultados e observações")
            if st.form_submit_button("Salvar registro", type="primary"):
                if not title.strip(): st.error("Informe o nome do experimento.")
                else:
                    try: insert("experimentos", {"titulo":title,"projeto":project,"responsavel":researcher,"data_experimento":exp_date.isoformat(),"etapa":stage,"materiais":materials,"procedimento":method,"resultados":results}); st.success("Experimento registrado."); st.rerun()
                    except Exception as e: st.error(str(e))
    show_table(experiments, ["data_experimento","titulo","projeto","responsavel","etapa","resultados"])
    delete_widget("experimentos", experiments, lambda r:f'{r.get("data_experimento")} • {r.get("titulo")}', "experiment")

# ---------- Biblioteca ----------
elif menu == "Biblioteca científica":
    page_header("Conhecimento", "Biblioteca científica", "Organize artigos, protocolos, manuais e documentos do laboratório.")
    with st.expander("＋ Cadastrar referência / documento"):
        with st.form("new_document"):
            title = st.text_input("Título *")
            a,b = st.columns(2)
            kind = a.selectbox("Tipo", ["Artigo científico","Protocolo","FISPQ","Manual de equipamento","Relatório","Outro"])
            category = b.text_input("Categoria / projeto")
            author = a.text_input("Autor / responsável")
            url = b.text_input("Link do arquivo (URL)")
            notes = st.text_area("Notas")
            if st.form_submit_button("Adicionar à biblioteca", type="primary"):
                if not title.strip(): st.error("Informe o título.")
                else:
                    try: insert("biblioteca", {"titulo":title,"tipo":kind,"categoria":category,"autor":author,"url":url,"observacoes":notes}); st.success("Documento cadastrado."); st.rerun()
                    except Exception as e: st.error(str(e))
    show_table(documents, ["titulo","tipo","categoria","autor","url","observacoes"])
    delete_widget("biblioteca", documents, lambda r:f'{r.get("titulo")} • {r.get("tipo")}', "document")

# ---------- Mural ----------
elif menu == "Mural de avisos":
    page_header("Comunicação", "Mural de avisos", "Compartilhe comunicados, alertas de manutenção e informações importantes.")
    with st.expander("＋ Publicar aviso", expanded=True):
        with st.form("new_notice"):
            a,b = st.columns(2)
            author = a.text_input("Autor")
            category = b.selectbox("Categoria", ["Comunicado geral","Manutenção","Estoque / insumos","Segurança","Evento"])
            message = st.text_area("Mensagem *")
            if st.form_submit_button("Publicar aviso", type="primary"):
                if not message.strip(): st.error("Escreva uma mensagem.")
                else:
                    try: insert("mural_avisos", {"autor":author or "Equipe NaNo","categoria":category,"tipo":category,"mensagem":message}); st.success("Aviso publicado."); st.rerun()
                    except Exception as e: st.error(str(e))
    for n in notices:
        with st.container(border=True):
            st.markdown(f"**{n.get('categoria') or n.get('tipo','Aviso')}** · {n.get('autor','Equipe NaNo')}")
            st.write(n.get("mensagem",""))
            if st.button("Excluir aviso", key=f"notice_{n.get('id')}"):
                try: delete("mural_avisos",n["id"]); st.rerun()
                except Exception as e: st.error(str(e))

st.divider()
st.caption("NaNo Hub • UFRRJ | Plataforma interna de apoio à gestão e à pesquisa. Confirme os registros e protocolos no laboratório antes de utilizá-los.")
