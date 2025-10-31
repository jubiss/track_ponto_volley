import streamlit as st
import pandas as pd


test = pd.DataFrame(st.session_state.history)
st.dataframe(test, hide_index=True, use_container_width=True)
# test = pd.read_csv("beach_volley_20251025_Evando_Arthur_Bassereau_Aye.csv")
time_1 = test[test['time'] == 'time1']['jogador'].unique()
time_2 = test[test['time'] == 'time2']['jogador'].unique()

def estatisticas_jogador(test):
    total_erros = test[test['tipo'].isin(['Erro de saque', 'Erro'])].groupby(['jogador', 'time']).agg(total_erros = ('jogador', 'count')).reset_index()
    total_pontos = test[~test['tipo'].isin(['Erro de saque', 'Erro'])].groupby(['jogador', 'time']).agg(total_pontos = ('jogador', 'count')).reset_index()
    # perc_fases = test[test['fase'].notnull()].groupby(['jogador', 'time', 'fase']).agg(total_fases = ('jogador', 'count')).reset_index()
    total_saques = test.groupby(['sacador']).agg(total_saques = ('jogador', 'count')).reset_index().rename(columns={'sacador': 'jogador'})
    fundamentos_pontos = test.pivot_table(index=['jogador', 'time'], columns='tipo', aggfunc='size', fill_value=0).reset_index()
    fase_ponto = test.pivot_table(index=['jogador', 'time'], columns='fase', aggfunc='size', fill_value=0).reset_index()
    all_statistics_player = total_erros.merge(total_pontos, how='outer', on=['jogador', 'time']).merge(total_saques, how='outer', on=['jogador']).merge(fase_ponto, how='outer', on=['jogador', 'time']).merge(fundamentos_pontos, how='outer', on=['jogador', 'time']).fillna(0)
    all_statistics_player['percentual_erro_saques'] = all_statistics_player['Erro de saque'] / all_statistics_player['total_saques'] * 100
    all_statistics_player['percentual_ace'] = all_statistics_player['Ace'] / all_statistics_player['total_saques'] * 100
    return all_statistics_player

def estatisticas_time(test):
    total_erros = test[test['tipo'].isin(['Erro de saque', 'Erro'])].groupby(['time']).agg(total_erros = ('jogador', 'count')).reset_index()
    total_pontos = test[~test['tipo'].isin(['Erro de saque', 'Erro'])].groupby(['time']).agg(total_pontos = ('jogador', 'count')).reset_index()
    # perc_fases = test[test['fase'].notnull()].groupby(['jogador', 'time', 'fase']).agg(total_fases = ('jogador', 'count')).reset_index()
    total_saques = test.groupby(['time']).agg(total_saques = ('jogador', 'count')).reset_index().rename(columns={'sacador': 'jogador'})
    fundamentos_pontos = test.pivot_table(index=[ 'time'], columns='tipo', aggfunc='size', fill_value=0).reset_index()
    fase_ponto = test.pivot_table(index=[ 'time'], columns='fase', aggfunc='size', fill_value=0).reset_index()
    all_statistics = total_erros\
        .merge(total_pontos, how='outer', on=['time'])\
        .merge(total_saques, how='outer', on=['time'])\
        .merge(fase_ponto, how='outer', on=['time'])\
        .merge(fundamentos_pontos, how='outer', on=['time']).fillna(0)
    total_saque_pontos_time1 = all_statistics[all_statistics['time'] == 'time1'][['total_saques', 'total_pontos']].rename(
        columns={'total_saques': 'total_saques_adversario', 'total_pontos': 'total_pontos_adversario'})
    total_saque_pontos_time1['time'] = 'time2'
    total_saque_pontos_time2 = all_statistics[all_statistics['time'] == 'time2'][['total_saques', 'total_pontos']].rename(
        columns={'total_saques': 'total_saques_adversario', 'total_pontos': 'total_pontos_adversario'})
    total_saque_pontos_time2['time'] = 'time1'
    total_ponto_adversario = pd.concat([total_saque_pontos_time1, total_saque_pontos_time2], ignore_index=True)
    all_statistics = all_statistics.merge(total_ponto_adversario, how='left', on='time')
    return all_statistics
all_statistics_player = estatisticas_jogador(test)
all_statistics_player['percentual_erro_saques'] = all_statistics_player['Erro de saque'] / all_statistics_player['total_saques'] * 100
all_statistics_player['percentual_ace'] = all_statistics_player['Ace'] / all_statistics_player['total_saques'] * 100

statistics_time = estatisticas_time(test)
statistics_time['percentual_k1_geral'] = statistics_time['K1 (side-out)'] / statistics_time['total_saques_adversario'] * 100
statistics_time['percentual_k2_geral'] = statistics_time['K2 (com saque)'] / statistics_time['total_saques'] * 100
statistics_time['percentual_k1_ponto'] = statistics_time['K1 (side-out)'] / statistics_time['total_pontos'] * 100
statistics_time['percentual_k2_ponto'] = statistics_time['K2 (com saque)'] / statistics_time['total_pontos'] * 100

all_statistics_player = all_statistics_player.rename(columns={'jogador': 'Atleta'})

df = pd.DataFrame(dados)
st.dataframe(test)
st.dataframe(all_statistics_player)
st.dataframe(statistics_time)
# ===== CSS customizado =====
st.markdown("""
<style>
.header-box {
    display: flex;
    justify-content: space-between;
    background: linear-gradient(90deg, #444, #6a6);
    color: white;
    border-radius: 10px;
    padding: 0.6rem 1rem;
    font-weight: bold;
    font-size: 1.2rem;
}
.tab-menu {
    display: flex;
    justify-content: space-around;
    background: linear-gradient(90deg, #d4ff4f, #3efec9);
    padding: 0.5rem;
    border-radius: 8px;
    margin-top: 0.5rem;
    font-weight: bold;
}
.tab-menu div {
    padding: 0.3rem 0.8rem;
    border-radius: 6px;
    cursor: pointer;
}
.tab-active {
    background: #47ff5f;
    box-shadow: 0 0 6px #222;
}
.table-container {
    background: white;
    border-radius: 10px;
    box-shadow: 0 0 6px rgba(0,0,0,0.2);
    padding: 0.5rem;
    margin-top: 0.5rem;
}
th {
    background-color: #008060 !important;
    color: white !important;
    text-align: center !important;
}
td {
    text-align: center !important;
}
</style>
""", unsafe_allow_html=True)

# ===== Cabeçalho =====
col1, col2 = st.columns(2)
col1, col2 = st.columns(2)

# Define qual time está selecionado (exemplo inicial)
if "time_selected" not in st.session_state:
    st.session_state.time_selected = "time1"

col1, col2 = st.columns(2)

# Define cores diferentes para cada botão e destaca o selecionado
cor_time1 = "#16a085"# if st.session_state.time_selected == "time1" else "#555"
cor_time2 = "#16a085"# if st.session_state.time_selected == "time2" else "#555"

# CSS atualizado
st.markdown(f"""
<style>
div[data-testid="stButton"] button {{
    width: 100%;
    height: 60px;
    font-size: 1.1rem;
    font-weight: bold;
    border-radius: 10px;
    color: white;
    border: none;
    transition: 0.2s;
}}
div[data-testid="stButton"]:nth-child(1) button {{
    background: linear-gradient(90deg, #333, {cor_time1});
}}
div[data-testid="stButton"]:nth-child(2) button {{
    background: linear-gradient(90deg, #333, {cor_time2});
}}
div[data-testid="stButton"] button:hover {{
    transform: scale(1.02);
    box-shadow: 0 0 8px #f888;
}}
</style>
""", unsafe_allow_html=True)

# Botões
with col1:
    if st.button(f"🏐 {' e '.join(time_1)}", key="btn_time1"):
        st.session_state.time_selected = "time1"

with col2:
    if st.button(f"{' e '.join(time_2)}", key="btn_time2"):
        st.session_state.time_selected = "time2"

# ===== Tabs de fundamentos =====
abas = ["Pontuação", "Ataque", "Bloqueio", "Saque", "Recepção", "Defesa"]
selected_tab = st.segmented_control("Escolha a estatística:", abas, default="Pontuação")

# ===== Tabela =====
st.markdown('<div class="table-container">', unsafe_allow_html=True)
st.markdown(f"### 🟢 {selected_tab}")

if selected_tab == "Pontuação":
    pontuacao = all_statistics_player[['Atleta', 'time', 'total_pontos', 'Ataque', 'Bloqueio', 'Ace']].copy()
    pontuacao = pontuacao[pontuacao['time'] == st.session_state.time_selected].rename(columns={'total_pontos': 'Pontos', 'Ataque': 'Ataque', 'Bloqueio': 'Bloqueio', 'Ace': 'Saque'})
    st.dataframe(pontuacao.drop(columns=['time']), hide_index=True)

elif selected_tab == "Ataque":
    ataque = all_statistics_player[['Atleta', 'time', 'Ataque']].copy()
    ataque = ataque[ataque['time'] == st.session_state.time_selected]
    st.dataframe(ataque.drop(columns=['time']), hide_index=True)

elif selected_tab == "Bloqueio":
    bloqueio = all_statistics_player[['Atleta', 'time', 'Bloqueio']].copy()
    bloqueio = bloqueio[bloqueio['time'] == st.session_state.time_selected]
    st.dataframe(bloqueio.drop(columns=['time']), hide_index=True)
elif selected_tab == "Saque":
    saque = all_statistics_player[['Atleta', 'time', 'Ace', 'Erro de saque', 'total_saques', 'percentual_ace', 'percentual_erro_saques']].copy()
    saque = saque[saque['time'] == st.session_state.time_selected].rename(columns={
        'Ace': 'Aces',
        'Erro de saque': 'Erros de Saque',
        'total_saques': 'Total de Saques',
        'percentual_ace': '% Aces',
        'percentual_erro_saques': '% Erros de Saque'
    })
    saque['Neutro'] = saque['Total de Saques'] - (saque['Aces'] + saque['Erros de Saque'])
    st.dataframe(
        saque[['Atleta', 'Aces', 'Neutro', 'Erros de Saque', 'Total de Saques', '% Aces', '% Erros de Saque']],
        hide_index=True)
st.markdown("</div>", unsafe_allow_html=True)
