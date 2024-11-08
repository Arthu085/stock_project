import streamlit as st
from services import conn


st.set_page_config(page_title='Estoque - Saldo',
                    layout="wide")

st.title('Consultar Movimentações de Estoque')

query_item = """SELECT id_item, nome FROM item"""
df_item = conn.carregar_dados(query_item)

choice_item = st.selectbox('Selecione o item:', options=df_item['nome'].tolist())
item_id = df_item.loc[df_item['nome'] == choice_item, 'id_item'].values[0]

col1, col2 = st.columns(2)
with col1:
    data1 = st.date_input('Selecione a primeira data:', format="DD/MM/YYYY")
with col2:
    data2 = st.date_input('Selecione a segunda data:', format="DD/MM/YYYY")

data1_str = data1.strftime('%Y-%m-%d') if data1 else ''
data2_str = data2.strftime('%Y-%m-%d') if data2 else ''


if st.button('Pesquisar'):

    query_search_movi = f"""SELECT e.nome, 
            a.quantidade, 
            FORMAT(a.data_movi, 'dd/MM/yyyy') AS data_formatada, 
            b.tipo_entrada_saida_nome, 
            c.numero_nota, 
            c.devolucao_obs, 
            c.paciente_nome, 
            c.motivo_perda, 
            d.tipo FROM moviestoque a
	INNER JOIN entradasaida b
		ON a.tipo_entrada_saida_id = b.tipo_entrada_saida_id
	INNER JOIN informacoes c
		ON a.informacoes_id = c.informacoes_id
	INNER JOIN tipomov d
		ON a.tipo_mov_id = d.tipo_mov_id
	INNER JOIN item e
		ON a.id_item = e.id_item
	WHERE e.id_item = ('{item_id}')
        AND CONVERT(DATE, a.data_movi) BETWEEN '{data1_str}' AND '{data2_str}'"""
    
    df_query_search_movi = conn.carregar_dados(query_search_movi)
    st.write(df_query_search_movi)
