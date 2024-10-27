import streamlit as st
from services import conn

st.set_page_config(page_title='Estoque - Entrada/Saída',
                    layout="wide")

st.title('Entrada e Saída de Estoque')

query_tipomov = "SELECT tipo_mov_id, tipo FROM tipomov"
df_tipomov = conn.carregar_dados(query_tipomov)

df_tipomov['tipo'] = df_tipomov['tipo'].replace({'entrada': 'Entrada', 'saida': 'Saída'})
tipo_dict = dict(zip(df_tipomov['tipo'], df_tipomov['tipo_mov_id']))  

query_categoria = "SELECT categoria_id, nome FROM categoria"
df_categoria = conn.carregar_dados(query_categoria)
df_categoria['nome'] = df_categoria['nome'].replace({'classe': 'Classe', 'material': 'Material'})

query_classes = """
SELECT a.id_classe, a.nome_classe 
FROM classes a 
LEFT JOIN categoria b 
ON a.categoria_id = b.categoria_id
"""
df_classes = conn.carregar_dados(query_classes)

query_material = """SELECT a.id_material, a.nome_material 
FROM material a 
LEFT JOIN categoria b 
ON a.categoria_id = b.categoria_id"""
df_material = conn.carregar_dados(query_material)
df_material['nome_material'] = df_material['nome_material'].replace({'material_paciente': 'Material Paciente'})

choice_categoria = st.selectbox('Selecione a categoria:', options=df_categoria['nome'])

if choice_categoria == 'Classe':
    choice_classes = st.selectbox('Selecione a classe:', options=df_classes['nome_classe'])
    if choice_classes:
        query_item_classe = f"""SELECT a.id_item, a.nome, b.nome_classe FROM item a
        INNER JOIN classes b
        ON a.id_classe = b.id_classe
        WHERE nome_classe = ('{choice_classes}')"""
        df_item_classe = conn.carregar_dados(query_item_classe)
        choice_item = st.selectbox('Selecione o item:', options=df_item_classe['nome'])
        choice_tipo = st.selectbox('Selecione o tipo de movimentação:', options=df_tipomov['tipo'])
        choice_qtde = st.number_input('Digite a quantidade:', min_value=0)

        item_id = df_item_classe.loc[df_item_classe['nome'] == choice_item, 'id_item'].values[0]
        tipo_mov_id = tipo_dict[choice_tipo]

        if st.button('Adicionar/Retirar'):
            if choice_item and choice_qtde > 0 and choice_tipo:
                try:
                    query_add_mov = f"INSERT INTO moviestoque (id_item, tipo_mov_id, quantidade) VALUES ({item_id}, {tipo_mov_id}, {choice_qtde})"
                    conn.inserir_dados(query_add_mov)
                    st.success('Estoque Atualizado')
                except Exception as e:
                    if "Estoque insuficiente para saída." in str(e):
                        st.error('Erro: Estoque insuficiente para a saída desejada!')
                    else:
                        st.error(f'Ocorreu um erro ao adicionar a movimentação: {str(e)}')
            else:
                st.error('Preencha todos os campos necessários!')

else:
    choice_material = st.selectbox('Selecione o material:', options=df_material['nome_material'])
    if choice_material:
        query_item_material = """SELECT a.id_item, a.nome, b.nome_material FROM item a
        INNER JOIN material b
        ON a.id_material = b.id_material"""
        df_item_material = conn.carregar_dados(query_item_material)
        choice_item = st.selectbox('Selecione o item:', options=df_item_material['nome'])
        choice_tipo = st.selectbox('Selecione o tipo de movimentação:', options=df_tipomov['tipo'])
        choice_qtde = st.number_input('Digite a quantidade:', min_value=0)

        item_id = df_item_material.loc[df_item_material['nome'] == choice_item, 'id_item'].values[0]
        tipo_mov_id = tipo_dict[choice_tipo]
        
        if st.button('Adicionar/Retirar'):
            if choice_item and choice_qtde > 0 and choice_tipo:
                try:
                    query_add_mov = f"INSERT INTO moviestoque (id_item, tipo_mov_id, quantidade) VALUES ({item_id}, {tipo_mov_id}, {choice_qtde})"
                    conn.inserir_dados(query_add_mov)
                    st.success('Estoque Atualizado')
                except Exception as e:
                    if "Estoque insuficiente para saída." in str(e):
                        st.error('Erro: Estoque insuficiente para a saída desejada!')
                    else:
                        st.error(f'Ocorreu um erro ao adicionar a movimentação: {str(e)}')
            else:
                st.error('Preencha todos os campos necessários!')




