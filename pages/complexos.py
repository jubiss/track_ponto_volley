import streamlit as st
import pandas as pd
from dataclasses import dataclass

@dataclass
class Jogador():
    nome: str
    id_user: str
    pontos: int
    erros: int

@dataclass
class Time():
    id: str
    nome: str
    jogadores: list[Jogador]
    pontos: int
    erros: int

@dataclass
class Jogo():
    id: str
    link_video_jogo : str|None = None
    ponto_time_1 : int = 0
    ponto_time2 : int = 0
    set_jogo : int = 1
    sacador_atual : Jogador|None = None
    time_sacando : Time|None = None

@dataclass
class Acao():
    jogador: Jogador
    complexo: 
    

if "lance" not in st.session_state:
    st.session_state.players = ["player1", "player2"]
    st.session_state.jogador_atual_index = 0
    st.session_state.history = pd.DataFrame(columns=["Complexo", "Etapa", "Acao", "Qualidade", "Jogador", "Lance", "Ponto"])
    st.session_state.lance = 0
    st.session_state.complexo_atual = "K1_fase1"
    st.session_state.acao_registrada = False
    st.session_state.ponto = 0

qualidade_list = ["Ponto", "A", "B", "Erro"]

opcoes_fase_1_k1 = ["Passe", "free-ball", "Largada"]

opcoes_passagem_de_bola = ["free-ball", "Ataque no Meio", "Ataque na paralela", "Ataque na Diagonal", "Lobby", "Croc", "Tesoura", "Largada"]
# Fase 2 Complexo K1
opcoes_fase_2_k1 = ["Levantamento", "jump-set"]
# Fase 3 Complexo K1
opcoes_fase_3_k1 = opcoes_passagem_de_bola
def check_fim_ponto(qualidade):
    if ((st.session_state.complexo_atual == "K1_fase3") or (qualidade == "Ponto")
            or (qualidade == "Erro")):
        st.session_state.lance = 0
        st.session_state.ponto += 1
        st.session_state.complexo_atual = "K1_fase1"
    else:
        if (st.session_state.complexo_atual == "K1_fase2"):
            st.session_state.complexo_atual = "K1_fase3"
        elif (st.session_state.complexo_atual == "K1_fase1"):
            st.session_state.complexo_atual = "K1_fase2"

        st.session_state.lance += 1

def update_registro(fase, acao, qualidade):    
    complexo = "K1"
    if complexo == "K1":
        registro = pd.DataFrame(
            [[complexo, fase, acao, qualidade, 
            st.session_state.players[st.session_state.jogador_atual_index], 
            st.session_state.lance, st.session_state.ponto]]
            , columns=st.session_state.history.columns
            )        
        st.session_state.history = pd.concat([st.session_state.history, registro])
        st.session_state.jogador_atual_index = 1-st.session_state.jogador_atual_index
        check_fim_ponto(qualidade)


@st.fragment
def exibir_k1_fase_1():
    with st.container():
        st.title("Registro de ações")
        st.markdown(st.session_state.complexo_atual)
        col = st.columns(2)
        for i in range(len(st.session_state.players)):
            col[i].markdown(st.session_state.players[i])
            for qualidade in qualidade_list:
                if col[i].button(f"Passe {qualidade}", key=f"{qualidade}-{st.session_state.players[i]}"):
                    st.session_state.jogador_atual_index = i
                    update_registro(fase="Fase1", acao="Passe", qualidade=qualidade)
                    # st.session_state.complexo_atual = "k1_fase2"
                    st.rerun()
@st.fragment
def exibir_k1_fase_2():
    with st.container():
        st.title("Registro de ações")
        jogador = st.session_state.players[st.session_state.jogador_atual_index]
        st.markdown(jogador)
        col = st.columns(2)
        for opcoes in opcoes_fase_2_k1:
            if st.session_state.acao_registrada == opcoes:
                type="primary"
            else:
                type="secondary"
            if col[0].button(f"{opcoes}", key=f"{opcoes}-{jogador}", type=type):
                st.session_state.acao_registrada = opcoes
                st.rerun()
        if st.session_state.acao_registrada != False:
            for qualidade in qualidade_list:
                if col[1].button(f"{qualidade}", key=f"fase2-{qualidade}"):
                    update_registro(fase="Fase2", acao=st.session_state.acao_registrada, qualidade=qualidade)
                    # st.session_state.complexo_atual = "k1_fase3"
                    st.rerun()

@st.fragment
def exibir_k1_fase_3():
    with st.container():
        st.title("Registro de ações")
        jogador = st.session_state.players[st.session_state.jogador_atual_index]
        st.markdown(jogador)
        col = st.columns(2)
        for opcoes in opcoes_fase_3_k1:
            if st.session_state.acao_registrada == opcoes:
                type="primary"
            else:
                type="secondary"
            if col[0].button(f"{opcoes}", key=f"{opcoes}-{jogador}", type=type):
                st.session_state.acao_registrada = opcoes
                st.rerun()
        if st.session_state.acao_registrada != False:
            for qualidade in qualidade_list:
                if col[1].button(f"{qualidade}", key=f"fase3-{qualidade}"):
                    update_registro(fase="Fase3", acao=st.session_state.acao_registrada, qualidade=qualidade)
                    # st.session_state.complexo_atual = "K1_fase1"
                    st.rerun()

if st.session_state.complexo_atual == "K1_fase1":
    exibir_k1_fase_1()
if st.session_state.complexo_atual == "K1_fase2":
    exibir_k1_fase_2()
if st.session_state.complexo_atual == "K1_fase3":
    exibir_k1_fase_3()
    
# st.dataframe(st.session_state.history)
import plotly.graph_objects as go

def donut_recepcoes(df):
    """
    Cria um donut chart a partir de um DataFrame com:
    - df['player']
    - df['total_recepcoes']
    Cada linha é um jogador.
    Return:
        fig (plotly.graph_objs._figure.Figure)
    """

    # Valores
    players = df["Jogador"].tolist()
    recepcoes = df["total_recepcoes"].tolist()
    # Total
    total = sum(recepcoes)
    # Porcentagens
    porcentagens = [(r / total) * 100 for r in recepcoes]
    # Donut chart
    fig = go.Figure(
        data=[
            go.Pie(
                labels=players,
                values=recepcoes,
                hole=0.55,
                textinfo="label+percent",
                hovertemplate="<b>%{label}</b><br>Recepções: %{value}<extra></extra>",
                marker=dict(
                    colors=["#2563eb", "#10b981", "#f59e0b", "#ef4444"]  # suporta + jogadores
                )
            )
        ]
    )
    # Layout clean
    fig.update_layout(
        title_text="Receptions by Player",
        margin=dict(l=20, r=20, t=40, b=20),
        height=350,
        showlegend=True
    )

    return fig

if len(st.session_state.history) > 0:
    df = st.session_state.history
    df_passe = df[df['Acao'] == 'Passe']
    total_recepcoes = len(df_passe)
    df_passe_agg = df_passe.groupby(['Jogador']).agg(total_recepcoes=("Jogador", "count")).reset_index()
    df_passe_agg['total_recepcoes_jogo'] = total_recepcoes
    df_passe_agg['razao_recepcoes'] = df_passe_agg['total_recepcoes']/df_passe_agg['total_recepcoes_jogo']*100
    if len(df_passe_agg) == 1:
        jogador_com_recepcao = df_passe_agg.loc[0, 'Jogador']
        jogador_sem_recepcao = "player2" if jogador_com_recepcao == "player1" else "player1"   
        df_passe_agg.loc[1,::] = [jogador_sem_recepcao, 0, 0, 0]

    fig = donut_recepcoes(df_passe_agg)
    st.plotly_chart(fig)

    st.dataframe(st.session_state.history)