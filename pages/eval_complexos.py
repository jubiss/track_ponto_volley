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

st.set_page_config(page_title="Avaliador de Complexos", layout="centered")

st.title("🏐 Vôlei de Praia Avaliador de Complexos")

# uploaded_file = st.sidebar.file_uploader(
#     "Importar histórico (CSV)",
#     type=["csv"],
#     help="Selecione um arquivo CSV exportado anteriormente."
# )
# 
# if uploaded_file is not None:
#     if st.sidebar.button("📥 Carregar histórico"):
#         importar_historico(uploaded_file)

# Configuração inicial
if "game_started" not in st.session_state:
    st.session_state.game_started = False
    st.session_state.current_set = 1
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
        # TODO Trocar string "player1" por variável player1, fazer mudanças em todas as partes de código que utilizam .scores
        # Lógica K0 , Ações positivas, negativas e continuidade
        dataframe_ponto_erro_continuidade = pd.DataFrame(data=[0,0,0], index=["Ações Positivas", "Ações Negativas", "Continuidade"], columns=[player1])

        st.session_state.k0 = {player1: [0,0,0], player2: [0,0,0], player3: [0,0,0], player4: [0,0,0]}
        st.session_state.k1 = {player1: [0,0,0], player2: [0,0,0], player3: [0,0,0], player4: [0,0,0]}
        st.session_state.k2 = {player1: [0,0,0], player2: [0,0,0], player3: [0,0,0], player4: [0,0,0]}
        st.session_state.current_set = 1
        st.session_state.game_started = True
        # st.rerun()

else:
    st.header(f"Set {st.session_state.current_set}")
    st.header(f"{st.session_state.player1}, {st.session_state.player2} vs {st.session_state.player3}, {st.session_state.player4}")
    st.subheader("Registrar Ponto")


    selecao_ponto = st.selectbox(
        "Como marcar os pontos",
        ['Botão', 'Selectionbox'],
        key="selecao_ponto_method"
    )

    c1, c2, c3, c4 = st.columns(4)



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

    # col1, col2 = st.columns(2)
    # col1.metric(f"{st.session_state.player1}, {st.session_state.player2}", st.session_state.scores["time1"])
    # col2.metric(f"{st.session_state.player3}, {st.session_state.player4}", st.session_state.scores["time2"])
    dataframe_ponto_erro_continuidade = pd.DataFrame(data=[[0,0,0]], index=[st.session_state.player1], columns=["Ações Positivas", "Ações Negativas", "Continuidade"])
    
    if dataframe_ponto_erro_continuidade_player1 in locals():
        pass
    else:
        dataframe_ponto_erro_continuidade_player1 = dataframe_ponto_erro_continuidade.copy(deep=True)
    C0, c1, c2, c3, c4, c5, c6 = st.columns(7)
    if c1.button("+", key="p+"):
        dataframe_ponto_erro_continuidade_player1["Ações Positivas"] += 1
    if c2.button("-P", key="p-"):
        dataframe_ponto_erro_continuidade_player1["Ações Positivas"] -= 1
    if c3.button("+N"):
        dataframe_ponto_erro_continuidade_player1["Ações Negativas"] += 1
    if c4.button("-N"):
        dataframe_ponto_erro_continuidade_player1["Ações Negativas"] -= 1
    if c5.button("+C"):
        dataframe_ponto_erro_continuidade_player1["Continuidade"] += 1
    if c6.button("-C"):
        dataframe_ponto_erro_continuidade_player1["Continuidade"] -= 1

    st.dataframe(dataframe_ponto_erro_continuidade_player1, use_container_width=True)


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
