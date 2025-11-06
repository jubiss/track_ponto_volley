"""
TODO: 
- Estatísticas do jogo
- Regras automáticas de finalização de set 
- Adicionar progressão de jogadas em um jogo (Saque, passe, levantamento, ataque, bloqueio) 
- Persistência entre sessões 
- Outras formas de registrar as informações (Usando reconhecimento de voz)
"""
import streamlit as st
from datetime import datetime
import pandas as pd

def importar_historico(uploaded_file):
    try:
        df = pd.read_csv(uploaded_file)

        # Garantir colunas essenciais
        colunas_esperadas = {"set", "time", "jogador", "tipo"}
        if not colunas_esperadas.issubset(set(df.columns)):
            st.error("❌ Arquivo inválido — faltam colunas obrigatórias (set, time, jogador, tipo).")
            return

        # Converte dataframe para lista de dicionários
        st.session_state.history = df.to_dict(orient="records")

        # Recalcular placares por set
        st.session_state.set_scores = {}
        for _, row in df.iterrows():
            set_num = int(row["set"])
            time = row["time"]

            if set_num not in st.session_state.set_scores:
                st.session_state.set_scores[set_num] = {"time1": 0, "time2": 0}

            if time in st.session_state.set_scores[set_num]:
                st.session_state.set_scores[set_num][time] += 1

        # Recalcula placar total
        st.session_state.scores["time1"] = sum(v["time1"] for v in st.session_state.set_scores.values())
        st.session_state.scores["time2"] = sum(v["time2"] for v in st.session_state.set_scores.values())

        st.session_state.current_set = max(st.session_state.set_scores.keys())
        st.success("✅ Histórico importado com sucesso!")
        st.toast("Histórico carregado — placares recalculados.")
        st.rerun()

    except Exception as e:
        st.error(f"Erro ao importar histórico: {e}")


def mark_point(player, time, other_time, tipo_ponto, player_session, sacador=None, fase=None, time_saque=None):
    set_num = st.session_state.current_set
    if ((tipo_ponto == "Erro Ataque") or (tipo_ponto == "Erro de saque") or (tipo_ponto == "Falta") or (tipo_ponto == "Erro") or
    (tipo_ponto == "Erro Bloqueio") or (tipo_ponto == "Erro defesa")):
        st.session_state.scores[other_time] += 1
        st.session_state.set_scores[set_num][other_time] += 1
    else:
        st.session_state.scores[player] += 1
        st.session_state.scores[time] += 1
        st.session_state.set_scores[set_num][time] += 1
    st.session_state.history.append({
        "hora": datetime.now().strftime("%H:%M:%S"),
        "jogador": player_session,
        "tipo": tipo_ponto,
        "time": time,
        "set": set_num,
        "sacador": sacador,
        "fase": fase,
        "time_saque": time_saque
    })

def atualizar_sacador(jogador_que_pontuou, time_finalizador, tipo_ponto):
    """
    Atualiza automaticamente o próximo sacador de acordo com o jogador que pontuou e o tipo de ponto.
    """
    sacadores = st.session_state.sacadores
    time_sacando = st.session_state.time_sacando

    # 🔹 Caso 1: Ace — mesmo jogador continua sacando
    if tipo_ponto == "Ace":
        st.session_state.time_sacando = time_finalizador
        for t, lista in sacadores.items():
            if jogador_que_pontuou in lista:
                st.session_state.sacador_index[t] = lista.index(jogador_que_pontuou)
        return

    # 🔹 Caso 2: Erro de saque — troca para o outro time e alterna sacador
    if (tipo_ponto == "Erro de saque") or (tipo_ponto == "Erro Ataque"):
        proximo_time = "time2" if time_finalizador == "time1" else "time1"
        st.session_state.time_sacando = proximo_time
        st.session_state.sacador_index[proximo_time] = 1 - st.session_state.sacador_index[proximo_time]
        return

    # 🔹 Caso 3: Ponto comum (ataque, bloqueio, erro adversário)
    if time_finalizador == time_sacando:
        # Time manteve o saque → mesmo jogador continua
        return
    else:
        # Time ganhou o ponto e vai sacar → alterna o jogador do time
        st.session_state.time_sacando = time_finalizador
        st.session_state.sacador_index[time_finalizador] = 1 - st.session_state.sacador_index[time_finalizador]


def point_selection(selecao_ponto):
    # tipos_de_ponto = ["Ace", "Ataque", "Erro", "Bloqueio", "Erro de saque"]

    # Sacador sugerido automaticamente
    # time_sacando = st.session_state.time_sacando
    # indice = st.session_state.sacador_index[time_sacando]
    # sacador_sugerido = st.session_state.sacadores[time_sacando][indice]    
    tipos_de_ponto = ["Ataque", "Erro Ataque", "Bloqueio", "Falta", "Erro", "Erro Bloqueio", "Erro defesa"]
    # Selecionar quem sacou o ponto atual
    c1, c2, c3 = st.columns([4, 1, 1])
    sacador = c1.radio(
        "Quem sacou este ponto?",
        [st.session_state.player1, st.session_state.player2, st.session_state.player3, st.session_state.player4],
        horizontal=True,
        index=1,
        key="sacador_atual"
    )
    if sacador == st.session_state.player1 or sacador == st.session_state.player2:
        time_saque = "time1"
    elif sacador == st.session_state.player3 or sacador == st.session_state.player4:
        time_saque = "time2"

    if c2.button("Acerto de saque (Ace)"):
        fase = "K0"
        if sacador == st.session_state.player1:
            mark_point(
                player='player1', time='time1', other_time='time2', tipo_ponto='Ace', player_session=sacador, sacador=sacador, fase=fase,
                time_saque=time_saque)
        if sacador == st.session_state.player2:
            mark_point(
                player='player2', time='time1', other_time='time2', tipo_ponto='Ace', player_session=sacador, sacador=sacador, fase=fase,
                time_saque=time_saque)
        if sacador == st.session_state.player3:
            mark_point(
                player='player3', time='time2', other_time='time1', tipo_ponto='Ace', player_session=sacador, sacador=sacador, fase=fase,
                time_saque=time_saque)
        if sacador == st.session_state.player4:
            mark_point(
                player='player4', time='time2', other_time='time1', tipo_ponto='Ace', player_session=sacador, sacador=sacador, fase=fase,
                time_saque=time_saque)

    if c3.button("Erro de saque"):
        fase = "K0"
        if sacador == st.session_state.player1:
            mark_point(
                player='player1', time='time1', other_time='time2', tipo_ponto='Erro de saque', player_session=sacador, sacador=sacador, 
                fase=fase, time_saque=time_saque)
        if sacador == st.session_state.player2:
            mark_point(
                player='player2', time='time1', other_time='time2', tipo_ponto='Erro de saque', player_session=sacador, sacador=sacador, 
                fase=fase, time_saque=time_saque)
        if sacador == st.session_state.player3:
            mark_point(
                player='player3', time='time2', other_time='time1', tipo_ponto='Erro de saque', player_session=sacador, sacador=sacador, 
                fase=fase, time_saque=time_saque)
        if sacador == st.session_state.player4:
            mark_point(
                player='player4', time='time2', other_time='time1', tipo_ponto='Erro de saque', player_session=sacador, sacador=sacador, 
                fase=fase, time_saque=time_saque)

    # Selecionar fase da jogada
    fase = st.radio(
        "Fase da jogada:",
        ["K1 (side-out)", "K2 (com saque)", "Outro"],
        horizontal=True,
        key="fase_jogada"
    )
    if selecao_ponto == 'Selectionbox':
        # Selecionar quem sacou o ponto atual

        # 🔹 Modo atual com selectbox
        tipo_ponto = st.selectbox(
            "Tipo de ponto",
            tipos_de_ponto,
            key="tipo_ponto"
        )

        c1, c2, c3, c4 = st.columns(4)
        if c1.button(f"🏐 {st.session_state.player1}"):
            mark_point(player="player1", time="time1", other_time="time2", tipo_ponto=tipo_ponto, player_session=st.session_state.player1, sacador=sacador, fase=fase)
        if c2.button(f"🏐 {st.session_state.player2}"):
            mark_point(player="player2", time="time1", other_time="time2", tipo_ponto=tipo_ponto, player_session=st.session_state.player2, sacador=sacador, fase=fase)
        if c3.button(f"🏐 {st.session_state.player3}"):
            mark_point(player="player3", time="time2", other_time="time1", tipo_ponto=tipo_ponto, player_session=st.session_state.player3, sacador=sacador, fase=fase)
        if c4.button(f"🏐 {st.session_state.player4}"):
            mark_point(player="player4", time="time2", other_time="time1", tipo_ponto=tipo_ponto, player_session=st.session_state.player4, sacador=sacador, fase=fase)

    else:
        # 🔴 Novo modo de botões duplos (ponto e erro)
        st.markdown("### Registro rápido de pontos e erros")

        # Cores personalizadas por tipo
        tipo_cores = {
            "Ace": "#2ecc71",            # verde
            "Ataque": "#27ae60",         # verde escuro
            "Bloqueio": "#9b59b6",       # roxo
            "Erro de ataque": "#e74c3c",           # vermelho
            "Falta": "#f39c12",          # laranja
            "Erro de saque": "#c0392b"   # vermelho escuro
        }

        # Estilos CSS para diferenciar botões
        st.markdown("""
            <style>
            .block-container {
                padding-top: 0.5rem;
                padding-bottom: 0rem;
            }
            div[data-testid="stVerticalBlock"] {
                gap: 0.4rem !important;
            }
            div[data-testid="stButton"] > button {
                width: 100%;
                height: 46px !important;
                font-weight: 600;
                border-radius: 10px;
                margin-bottom: 4px !important;
            }
            </style>
        """, unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        jogadores = [
            ("player1", "time1", "time2", st.session_state.player1, col1),
            ("player2", "time1", "time2", st.session_state.player2, col2),
            ("player3", "time2", "time1", st.session_state.player3, col3),
            ("player4", "time2", "time1", st.session_state.player4, col4)
        ]
        for player_key, time, other_time, nome, col in jogadores:
            with col:
                st.markdown(f"**{nome}**")
                # Botão verde = ponto positivo
            for tipo in tipos_de_ponto:
                # cor = tipo_cores[tipo]
                # button_html = f"""
                #     <button style="background-color:{cor};
                #                     width:100%;
                #                     height:46px;
                #                     border:none;
                #                     border-radius:10px;
                #                     font-weight:600;
                #                     margin-bottom:4px;
                #                     cursor:pointer;">
                #         {tipo}
                #     </button>
                # """
                # Usar st.markdown com HTML + JS para detectar cliques
                # Simula um botão real com JavaScript postMessage
                clicked = col.button(tipo, key=f"{nome}_{tipo}", use_container_width=True)
                if clicked:
                    mark_point(player_key, time, other_time, tipo, nome, sacador=sacador, fase=fase, time_saque=time_saque)

def check_set_end():
    set_num = st.session_state.current_set
    scores = st.session_state.set_scores[set_num]
    limit = 15 if set_num == 3 else 21
    diff = abs(scores["time1"] - scores["time2"])

    # Condição para sugerir o fim do set
    if (scores["time1"] >= limit or scores["time2"] >= limit) and diff >= 2:
        winner = "Time 1" if scores["time1"] > scores["time2"] else "Time 2"
        st.warning(
            f"🏁 O **set {set_num}** parece ter terminado!\n\n"
            f"{winner} está vencendo por **{scores['time1']} x {scores['time2']}**.\n"
            "Deseja encerrar o set agora?"
        )
        # Botão de confirmação
        col1, col2 = st.columns(2)
        if col1.button("✅ Encerrar Set"):
            st.session_state.current_set += 1
            st.session_state.set_scores[st.session_state.current_set] = {"time1": 0, "time2": 0}
            st.success(f"Set {set_num} encerrado. Novo set iniciado!")
            st.rerun()
        if col2.button("❌ Continuar jogando"):
            st.info("Set continuará até decisão manual.")

st.set_page_config(page_title="Beach Volleyball Score", layout="centered")

st.title("🏐 Beach Volleyball Tracker")

uploaded_file = st.sidebar.file_uploader(
    "Importar histórico (CSV)",
    type=["csv"],
    help="Selecione um arquivo CSV exportado anteriormente."
)

if uploaded_file is not None:
    if st.sidebar.button("📥 Carregar histórico"):
        importar_historico(uploaded_file)

# Configuração inicial
if "game_started" not in st.session_state:
    st.session_state.game_started = False
    st.session_state.scores = {"player1": 0, "player2": 0, "player3": 0, "player4": 0, "time1": 0, "time2": 0}
    st.session_state.current_set = 1
    st.session_state.set_scores = {1: {"time1": 0, "time2": 0}}
    st.session_state.history = []
if not st.session_state.game_started:
    st.subheader("Defina os jogadores")
    c1, c2 = st.columns(2)
    player1 = c1.text_input("Jogador 1", "Jogador A")
    player2 = c2.text_input("Jogador 2", "Jogador B")
    player3 = c1.text_input("Jogador 3", "Jogador C")
    player4 = c2.text_input("Jogador 4", "Jogador D")

    if st.button("Iniciar Jogo"):
        st.session_state.player1 = player1
        st.session_state.player2 = player2
        st.session_state.player3 = player3
        st.session_state.player4 = player4
        st.session_state.scores = {"player1": 0, "player2": 0, "player3": 0, "player4": 0, "time1": 0, "time2": 0}
        st.session_state.current_set = 1
        st.session_state.set_scores = {1: {"time1": 0, "time2": 0}}
        st.session_state.history = []
        st.session_state.sacadores = {
        "time1": [st.session_state.player1, st.session_state.player2],
        "time2": [st.session_state.player3, st.session_state.player4],
        }
        st.session_state.sacador_index = {
        "time1": 0,  # Começa com o primeiro jogador do time 1
        "time2": 0,  # Começa com o primeiro jogador do time 2
    }
        st.session_state.game_started = True
        st.session_state.time_sacando = "time1"
        st.rerun()

else:
    st.header(f"Set {st.session_state.current_set}")
    st.header(f"{st.session_state.player1}, {st.session_state.player2} vs {st.session_state.player3}, {st.session_state.player4}")
    st.subheader("Registrar Ponto")


    selecao_ponto = st.selectbox(
        "Como marcar os pontos",
        ['Botão', 'Selectionbox'],
        key="selecao_ponto_method"
    )
    point_selection(selecao_ponto=selecao_ponto)

    # if selecao_ponto == 'selectionbox':
    #     # Selecionar tipo de ponto
    #     tipo_ponto = st.selectbox(
    #         "Tipo de ponto",
    #         tipos_de_ponto,
    #         key="tipo_ponto"
    #     )
    #     c1, c2, c3, c4 = st.columns(4)
    #     if c1.button(f"🏐 {st.session_state.player1}"):
    #         mark_point(player="player1", time="time1", other_time="time2", tipo_ponto=tipo_ponto, player_session=st.session_state.player1)    
    #     if c2.button(f"🏐 {st.session_state.player2}"):
    #         mark_point(player="player2", time="time1", other_time="time2", tipo_ponto=tipo_ponto, player_session=st.session_state.player2)
    #     if c3.button(f"🏐 {st.session_state.player3}"):
    #         mark_point(player="player3", time="time2", other_time="time1", tipo_ponto=tipo_ponto, player_session=st.session_state.player3)
    #     if c4.button(f"🏐 {st.session_state.player4}"):
    #         mark_point(player="player4", time="time2", other_time="time1", tipo_ponto=tipo_ponto, player_session=st.session_state.player4)

    col1, col2 = st.columns(2)
    col1.metric(f"{st.session_state.player1}, {st.session_state.player2}", st.session_state.scores["time1"])
    col2.metric(f"{st.session_state.player3}, {st.session_state.player4}", st.session_state.scores["time2"])


    # Exibir placares dos sets
    st.write("### 🧮 Placar por Set")
    for set_num, s in st.session_state.set_scores.items():
        st.write(f"**Set {set_num}:** {s['time1']} x {s['time2']}")

    check_set_end()

    if st.button("↩️ Desfazer último ponto"):
        if st.session_state.history:
            last = st.session_state.history.pop()  # remove o último ponto
            set_num = last["set"]
            player = [k for k, v in st.session_state.items() if isinstance(v, str) and v == last["jogador"]]
            
            if player:
                player_key = player[0]
                time_key = last["time"].lower().replace(" ", "")
                # diminui pontuação
                if st.session_state.scores[player_key] > 0:
                    st.session_state.scores[player_key] -= 1
                if st.session_state.scores[time_key] > 0:
                    st.session_state.scores[time_key] -= 1
                if st.session_state.set_scores[set_num][time_key] > 0:
                    st.session_state.set_scores[set_num][time_key] -= 1
            st.success(f"Último ponto removido ({last['jogador']} - {last['tipo']} - Set {set_num})")
            st.rerun()
        else:
            st.warning("Nenhum ponto para desfazer.")
    st.divider()

    # Finalizar set atual
    if st.button("🏁 Finalizar Set"):
        st.session_state.current_set += 1
        st.session_state.set_scores[st.session_state.current_set] = {"time1": 0, "time2": 0}
        st.success(f"Set {st.session_state.current_set - 1} finalizado. Novo set iniciado!")
        st.rerun()

    st.subheader("📜 Histórico de pontos")

    if st.session_state.history:
        #df = pd.DataFrame(st.session_state.history)
        df = pd.DataFrame(st.session_state.history)
        # st.dataframe(df[::-1], hide_index=True, use_container_width=True)
        edited_df = st.data_editor(df, hide_index=True, use_container_width=True)
        if st.button("Recalcular placar"):
            # Recalcula tudo com base no histórico editado
            st.session_state.scores = {k: 0 for k in st.session_state.scores.keys()}
            for _, row in edited_df.iterrows():
                player = [k for k, v in st.session_state.items() if isinstance(v, str) and v == row["jogador"]]
                if player:
                    player_key = player[0]
                    time_key = row["time"].lower().replace(" ", "")
                    st.session_state.scores[player_key] += 1
                    st.session_state.scores[time_key] += 1
         
         
            st.session_state.history = edited_df.to_dict("records")
            st.success("Placar recalculado com base no histórico (por set)!")
            st.rerun()
        
        csv = df.to_csv(index=False).encode("utf-8")
        nome_arquivo = f"beach_volley_{datetime.now().strftime('%Y%m%d')}_{st.session_state.player1}_{st.session_state.player2}_{st.session_state.player3}_{st.session_state.player4}.csv"
# {datetime.now().strftime('%Y%m%d')}_{st.session_state.player1}_{st.session_state.player2}_{st.session_state.player3}_{st.session_state.player4}
        st.download_button(
            label="💾 Exportar histórico em CSV",
            data=csv,
            file_name=nome_arquivo,
            mime="text/csv",
            use_container_width=True
        )
    # 👉 Adicione aqui o botão de exportar CSV 👇
    else:
        st.info("Nenhum ponto registrado ainda.")

    if st.button("🔄 Reiniciar Jogo"):
        st.session_state.game_started = False
        st.rerun()
