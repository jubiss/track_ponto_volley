import streamlit as st
import pandas as pd

if "lance" not in st.session_state:
    st.session_state.players = ["player1", "player2"]
    st.session_state.jogador_atual_index = 0
    st.session_state.history = pd.DataFrame(columns=["Complexo", "Etapa", "Acao", "Qualidade", "Jogador", "Lance", "Ponto"])
    st.session_state.lance = 0
    st.session_state.complexo_atual = "k1_fase1"
    st.session_state.acao_registrada = False
    st.session_state.ponto = 0

st.dataframe(st.session_state.history)
qualidade_list = ["A", "B", "Erro"]
# Fase 2 Complexo K1
opcoes_fase_2_k1 = ["Levantamento", "jump-set", "free-ball"]
# Fase 3 Complexo K1
tipos_de_ataque = ["Ataque paralela", "Ataque Diagonal", "Lobby", "Tesoura", "Croc", "free-ball"]
def erro_update():
    st.session_state.complexo_atual = "k1_fase1"
    st.session_state.ponto += 1

def update_registro(fase, acao, qualidade):    
    if st.session_state.complexo_atual == "k1_fase1":
        complexo = "K1"
        fase = "Fase1"
        acao = "Passe"
    if st.session_state.complexo_atual == "k1_fase2":
        complexo = "K1"
        fase = "Fase2"
        acao = st.session_state.acao_registrada
    registro = pd.DataFrame(
        [[complexo, fase, acao, qualidade, st.session_state.players[st.session_state.jogador_atual_index], 
            st.session_state.lance, st.session_state.ponto]]
        , columns=st.session_state.history.columns
        )        
    st.session_state.history = pd.concat([st.session_state.history, registro])
    st.session_state.lance += 1
    st.session_state.jogador_atual_index = 1-st.session_state.jogador_atual_index
    if qualidade == "Erro":
        erro_update()

@st.fragment
def exibir_k1_fase_1():
    with st.container():
        st.title("Registro de ações")
        col = st.columns(2)
        for i in range(len(st.session_state.players)):
            col[i].markdown(st.session_state.players[i])
            for qualidade in qualidade_list:
                if col[i].button(f"Passe {qualidade}", key=f"{qualidade}-{st.session_state.players[i]}"):
                    st.session_state.jogador_atual_index = i
                    update_registro(fase="Fase1", acao="Passe", qualidade=qualidade)
                    st.session_state.complexo_atual = "k1_fase2"
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
                    registro = pd.DataFrame(
                        [["K1", "Fase2", st.session_state.acao_registrada, qualidade, jogador, 
                            st.session_state.lance]]
                        , columns=st.session_state.history.columns
                        )
                    st.session_state.history = pd.concat([st.session_state.history, registro])
                    st.session_state.lance += 1
                    if qualidade == "Erro":
                        erro_update()
                    st.session_state.jogador_atual = st.session_state.players[1-st.session_state.jogador_atual_index]
                    st.session_state.complexo_atual = "k1_fase3"
                    st.rerun()

if st.session_state.complexo_atual == "k1_fase1":
    exibir_k1_fase_1()
if st.session_state.complexo_atual == "k1_fase2":
    exibir_k1_fase_2()