import plotly.express as px
import streamlit as st
import pandas as pd

def exibir_estatisticas():
    st.header("📊 Estatísticas da Partida")

    if "history" not in st.session_state or len(st.session_state.history) == 0:
        st.info("Nenhum ponto registrado ainda.")
        return

    df = pd.DataFrame(st.session_state.history)
    st.dataframe(df, hide_index=True, use_container_width=True)
    # Preparar dataframe para as métricas solicitadas

    # Total de pontos por jogador (linhas onde o jogador fez o ponto)
    pontos_por_jogador = df['jogador'].value_counts().rename('total_pontos').reset_index()
    pontos_por_jogador.rename(columns={'index': 'jogador'}, inplace=True)

    # Total de erros causados pelo jogador (Erros e Erros de saque)
    erros = df[df['tipo'].str.contains('Erro', case=False)]
    erros_por_jogador = erros['jogador'].value_counts().rename('total_erros').reset_index()
    erros_por_jogador.rename(columns={'index': 'jogador'}, inplace=True)

    # Total de pontos e erros combinados
    metricas = pontos_por_jogador.merge(erros_por_jogador, on='jogador', how='outer').fillna(0)

    # Erros de saque
    erros_saque = df[df['tipo'].str.contains('Erro de saque', case=False)]
    erros_saque_por_jogador = erros_saque['jogador'].value_counts().rename('erros_saque').reset_index()
    erros_saque_por_jogador.rename(columns={'index': 'jogador'}, inplace=True)

    # Aces (se houver na coluna tipo)
    aces = df[df['tipo'].str.contains('Ace', case=False)]
    aces_por_jogador = aces['jogador'].value_counts().rename('aces').reset_index()
    aces_por_jogador.rename(columns={'index': 'jogador'}, inplace=True)

    # Total de saques
    saques = df[df['tipo'].str.contains('saque', case=False)]
    total_saques_por_jogador = saques['jogador'].value_counts().rename('total_saques').reset_index()
    total_saques_por_jogador.rename(columns={'index': 'jogador'}, inplace=True)

    # Eficiência de saque = Aces/Total de saques e Erros de saque/Total de saques
    saque_stats = total_saques_por_jogador.merge(aces_por_jogador, on='jogador', how='left') \
        .merge(erros_saque_por_jogador, on='jogador', how='left').fillna(0)

    saque_stats['eficiencia_ace'] = saque_stats['aces'] / saque_stats['total_saques']
    saque_stats['eficiencia_erro_saque'] = saque_stats['erros_saque'] / saque_stats['total_saques']

    # Eficiência K1 e K2 (nº de pontos K1 ou K2 / total de pontos do jogador)
    k1 = df[df['fase'].str.contains('K1', case=False)]
    k2 = df[df['fase'].str.contains('K2', case=False)]

    k1_por_jogador = k1['jogador'].value_counts().rename('pontos_k1').reset_index()
    k1_por_jogador.rename(columns={'index': 'jogador'}, inplace=True)
    k2_por_jogador = k2['jogador'].value_counts().rename('pontos_k2').reset_index()
    k2_por_jogador.rename(columns={'index': 'jogador'}, inplace=True)

    eficiencia_k = pontos_por_jogador.merge(k1_por_jogador, on='jogador', how='left') \
        .merge(k2_por_jogador, on='jogador', how='left').fillna(0)

    eficiencia_k['eficiencia_k1'] = eficiencia_k['pontos_k1'] / eficiencia_k['total_pontos']
    eficiencia_k['eficiencia_k2'] = eficiencia_k['pontos_k2'] / eficiencia_k['total_pontos']

    # Juntar tudo
    resultado = metricas.merge(eficiencia_k[['jogador', 'eficiencia_k1', 'eficiencia_k2']], on='jogador', how='left') \
        .merge(saque_stats[['jogador', 'eficiencia_ace', 'eficiencia_erro_saque']], on='jogador', how='left') \
        .fillna(0)
    st.dataframe(resultado, hide_index=True, use_container_width=True)
    # --- Limpeza e garantias ---
    if "tipo" not in df.columns or "jogador" not in df.columns:
        st.warning("Histórico incompleto — não há dados suficientes para gerar estatísticas.")
        return

def novas_estatisticas():
    import pandas as pd
# test = pd.read_csv("beach_volley_20251025_Evando_Arthur_Bassereau_Aye.csv")
test = pd.DataFrame(st.session_state.history)

#test.groupby(['jogador', 'tipo']).size().unstack(fill_value=0)
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
# exibir_estatisticas()

estatistica_selecionada = st.selectbox("Selecione a estatística para visualizar:", 
             options=["Estatísticas por Jogador", "Estatísticas por Time"], 
             key="estatistica_selecionada")
st.markdown(f"## {estatistica_selecionada}")
if estatistica_selecionada == "Estatísticas por Jogador":
    st.dataframe(all_statistics_player, hide_index=True, use_container_width=True)
elif estatistica_selecionada == "Estatísticas por Time":
    st.dataframe(statistics_time, hide_index=True, use_container_width=True)
    # statistics_time[statistics_time['total_saques_adversarios']]
st.dataframe(all_statistics_player, hide_index=True, use_container_width=True)
st.dataframe(statistics_time, hide_index=True, use_container_width=True)