import streamlit as st
from datetime import datetime
import pandas as pd

def mark_point(player, time, other_time, tipo_ponto, player_session):    
    set_num = st.session_state.current_set
    if tipo_ponto == "Erro":
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
        "set": set_num
    })
st.set_page_config(page_title="Beach Volleyball Score", layout="centered")

st.title("🏐 Beach Volleyball Tracker")

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
        st.session_state.game_started = True
        st.rerun()

else:
    st.header(f"Set {st.session_state.current_set}")
    st.header(f"{st.session_state.player1}, {st.session_state.player2} vs {st.session_state.player3}, {st.session_state.player4}")
    st.subheader("Registrar Ponto")

    # Selecionar tipo de ponto
    tipo_ponto = st.selectbox(
        "Tipo de ponto",
        ["Ace", "Ataque", "Erro", "Bloqueio", "Outro"],
        key="tipo_ponto"
    )
    c1, c2, c3, c4 = st.columns(4)
    if c1.button(f"🏐 +1 {st.session_state.player1}"):
        mark_point(player="player1", time="time1", other_time="time2", tipo_ponto=tipo_ponto, player_session=st.session_state.player1)    
    if c2.button(f"🏐 +1 {st.session_state.player2}"):
        mark_point(player="player2", time="time1", other_time="time2", tipo_ponto=tipo_ponto, player_session=st.session_state.player2)
    if c3.button(f"🏐 +1 {st.session_state.player3}"):
        mark_point(player="player3", time="time2", other_time="time1", tipo_ponto=tipo_ponto, player_session=st.session_state.player3)
    if c4.button(f"🏐 +1 {st.session_state.player4}"):
        mark_point(player="player4", time="time2", other_time="time1", tipo_ponto=tipo_ponto, player_session=st.session_state.player4)

    col1, col2 = st.columns(2)
    col1.metric(f"{st.session_state.player1}, {st.session_state.player2}", st.session_state.scores["time1"])
    col2.metric(f"{st.session_state.player3}, {st.session_state.player4}", st.session_state.scores["time2"])


    # Exibir placares dos sets
    st.write("### 🧮 Placar por Set")
    for set_num, s in st.session_state.set_scores.items():
        st.write(f"**Set {set_num}:** {s['time1']} x {s['time2']}")

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
