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

        if choice_tipo == 'Entrada':
            query_tipo_entrada = """SELECT tipo_entrada_saida_id, tipo_entrada_saida_nome
                                        FROM entradasaida
                                        WHERE tipo_entrada_saida_id IN (5, 1, 2)"""
            df_tipo_entrada = conn.carregar_dados(query_tipo_entrada)
            df_tipo_entrada['tipo_entrada_saida_nome'] = df_tipo_entrada['tipo_entrada_saida_nome'].replace({'nota_fiscal': 'Nota Fiscal', 'balanco': 'Balanço', 'devolucao': 'Devolução'})
            tipo_entrada_dict = dict(zip(df_tipo_entrada['tipo_entrada_saida_nome'], df_tipo_entrada['tipo_entrada_saida_id'])) 
            choice_tipo_entrada = st.selectbox('Selecione o tipo de entrada:', options=df_tipo_entrada['tipo_entrada_saida_nome'])

            item_id = df_item_classe.loc[df_item_classe['nome'] == choice_item, 'id_item'].values[0]
            tipo_mov_id = tipo_dict[choice_tipo]

            if choice_tipo_entrada == 'Nota Fiscal':
                numero_nota = st.number_input('Digite o numero da nota:', min_value=0)
                choice_qtde = st.number_input('Digite a quantidade:', min_value=0)
                tipo_entrada_saida_id = tipo_entrada_dict[choice_tipo_entrada]

                if st.button('Adicionar/Retirar'):

                    if choice_item and choice_qtde > 0 and choice_tipo and numero_nota:
                        query_add_nota = f"""BEGIN
                                                INSERT INTO informacoes (tipo_entrada_saida_id, numero_nota) 
                                                VALUES ({tipo_entrada_saida_id}, {numero_nota});
                                                SELECT SCOPE_IDENTITY() AS informacoes_id;
                                            END"""
                        informacoes_id = conn.inserir_dados(query_add_nota, retornar_id=True)   

                        if informacoes_id:
                            query_add_mov = f"""INSERT INTO moviestoque (id_item, tipo_mov_id, quantidade, tipo_entrada_saida_id, informacoes_id) 
                                                VALUES ({item_id}, {tipo_mov_id}, {choice_qtde}, {tipo_entrada_saida_id}, {informacoes_id})"""
                            conn.inserir_dados(query_add_mov)
                            st.success('Estoque Atualizado')
                        else:
                            st.error("Erro ao capturar o ID gerado para 'informacoes")
                    else:
                        st.error('Preencha todos os campos necessários!')

            elif choice_tipo_entrada == 'Balanço':
                choice_qtde = st.number_input('Digite a quantidade:', min_value=0) 
                tipo_entrada_saida_id = tipo_entrada_dict[choice_tipo_entrada]

                if st.button('Adicionar/Retirar'):

                    if choice_item and choice_qtde > 0 and choice_tipo:
                        query_add_balanco = f"""BEGIN
                                                INSERT INTO informacoes (tipo_entrada_saida_id) 
                                                VALUES ({tipo_entrada_saida_id});
                                                SELECT SCOPE_IDENTITY() AS informacoes_id;
                                            END"""
                        informacoes_id = conn.inserir_dados(query_add_balanco, retornar_id=True) 

                        if informacoes_id:
                            query_add_mov = f"""INSERT INTO moviestoque (id_item, tipo_mov_id, quantidade, tipo_entrada_saida_id, informacoes_id) 
                                                VALUES ({item_id}, {tipo_mov_id}, {choice_qtde}, {tipo_entrada_saida_id}, {informacoes_id})"""
                            conn.inserir_dados(query_add_mov)
                            st.success('Estoque Atualizado')
                        else:
                            st.error("Erro ao capturar o ID gerado para 'informacoes")
                    else:
                        st.error('Preencha todos os campos necessários!')        

            elif choice_tipo_entrada == 'Devolução':
                devolucao_obs = st.text_input('Observação:')
                choice_qtde = st.number_input('Digite a quantidade:', min_value=0)         
                tipo_entrada_saida_id = tipo_entrada_dict[choice_tipo_entrada]

                if st.button('Adicionar/Retirar'):

                    if choice_item and choice_qtde > 0 and choice_tipo and devolucao_obs:
                        query_add_obs = f"""BEGIN
                                                INSERT INTO informacoes (tipo_entrada_saida_id, devolucao_obs) 
                                                VALUES ({tipo_entrada_saida_id}, '{devolucao_obs}');
                                                SELECT SCOPE_IDENTITY() AS informacoes_id;
                                            END"""
                        informacoes_id = conn.inserir_dados(query_add_obs, retornar_id=True)     
                        
                        if informacoes_id:
                            query_add_mov = f"""INSERT INTO moviestoque (id_item, tipo_mov_id, quantidade, tipo_entrada_saida_id, informacoes_id)
                                                VALUES ({item_id}, {tipo_mov_id}, {choice_qtde}, {tipo_entrada_saida_id}, {informacoes_id})"""
                            conn.inserir_dados(query_add_mov)
                            st.success('Estoque Atualizado')
                        else:
                            st.error("Erro ao capturar o ID gerado para 'informacoes")
                    else:
                        st.error('Preencha todos os campos necessários!')   
        else:
            query_tipo_saida = """SELECT tipo_entrada_saida_id, tipo_entrada_saida_nome
                                        FROM entradasaida
                                        WHERE tipo_entrada_saida_id != 5"""
            df_tipo_saida = conn.carregar_dados(query_tipo_saida)
            df_tipo_saida['tipo_entrada_saida_nome'] = df_tipo_saida['tipo_entrada_saida_nome'].replace({'balanco': 'Balanço', 'devolucao': 'Devolução', 'paciente': 'Paciente', 'perda': 'Perda'})
            tipo_saida_dict = dict(zip(df_tipo_saida['tipo_entrada_saida_nome'], df_tipo_saida['tipo_entrada_saida_id'])) 
            choice_tipo_saida = st.selectbox('Selecione o tipo de entrada:', options=df_tipo_saida['tipo_entrada_saida_nome'])

            item_id = df_item_classe.loc[df_item_classe['nome'] == choice_item, 'id_item'].values[0]
            tipo_mov_id = tipo_dict[choice_tipo]

            if choice_tipo_saida == 'Balanço':
                choice_qtde = st.number_input('Digite a quantidade:', min_value=0) 
                tipo_entrada_saida_id = tipo_saida_dict[choice_tipo_saida]

                if st.button('Adicionar/Retirar'):

                    if choice_item and choice_qtde > 0 and choice_tipo:
                        query_add_balanco = f"""BEGIN
                                                INSERT INTO informacoes (tipo_entrada_saida_id) 
                                                VALUES ({tipo_entrada_saida_id});
                                                SELECT SCOPE_IDENTITY() AS informacoes_id;
                                            END"""
                        informacoes_id = conn.inserir_dados(query_add_balanco, retornar_id=True) 

                        if informacoes_id:
                            query_add_mov = f"""INSERT INTO moviestoque (id_item, tipo_mov_id, quantidade, tipo_entrada_saida_id, informacoes_id) 
                                                VALUES ({item_id}, {tipo_mov_id}, {choice_qtde}, {tipo_entrada_saida_id}, {informacoes_id})"""
                            conn.inserir_dados(query_add_mov)
                            st.success('Estoque Atualizado')
                        else:
                            st.error("Erro ao capturar o ID gerado para 'informacoes")
                    else:
                        st.error('Preencha todos os campos necessários!') 

            elif choice_tipo_saida == 'Devolução':
                devolucao_obs = st.text_input('Observação:')
                choice_qtde = st.number_input('Digite a quantidade:', min_value=0)         
                tipo_entrada_saida_id = tipo_saida_dict[choice_tipo_saida]

                if st.button('Adicionar/Retirar'):

                    if choice_item and choice_qtde > 0 and choice_tipo and devolucao_obs:
                        query_add_obs = f"""BEGIN
                                                INSERT INTO informacoes (tipo_entrada_saida_id, devolucao_obs) 
                                                VALUES ({tipo_entrada_saida_id}, '{devolucao_obs}');
                                                SELECT SCOPE_IDENTITY() AS informacoes_id;
                                            END"""
                        informacoes_id = conn.inserir_dados(query_add_obs, retornar_id=True)     
                        
                        if informacoes_id:
                            query_add_mov = f"""INSERT INTO moviestoque (id_item, tipo_mov_id, quantidade, tipo_entrada_saida_id, informacoes_id)
                                                VALUES ({item_id}, {tipo_mov_id}, {choice_qtde}, {tipo_entrada_saida_id}, {informacoes_id})"""
                            conn.inserir_dados(query_add_mov)
                            st.success('Estoque Atualizado')
                        else:
                            st.error("Erro ao capturar o ID gerado para 'informacoes")
                    else:
                        st.error('Preencha todos os campos necessários!')

            elif choice_tipo_saida == 'Paciente':
                paciente_nome = st.text_input('Digite o nome do paciente:')
                choice_qtde = st.number_input('Digite a quantidade:', min_value=0)         
                tipo_entrada_saida_id = tipo_saida_dict[choice_tipo_saida]

                if st.button('Adicionar/Retirar'):

                    if choice_item and choice_qtde > 0 and choice_tipo and paciente_nome:
                        query_add_obs = f"""BEGIN
                                                INSERT INTO informacoes (tipo_entrada_saida_id, paciente_nome) 
                                                VALUES ({tipo_entrada_saida_id}, '{paciente_nome}');
                                                SELECT SCOPE_IDENTITY() AS informacoes_id;
                                            END"""
                        informacoes_id = conn.inserir_dados(query_add_obs, retornar_id=True)     
                        
                        if informacoes_id:
                            query_add_mov = f"""INSERT INTO moviestoque (id_item, tipo_mov_id, quantidade, tipo_entrada_saida_id, informacoes_id)
                                                VALUES ({item_id}, {tipo_mov_id}, {choice_qtde}, {tipo_entrada_saida_id}, {informacoes_id})"""
                            conn.inserir_dados(query_add_mov)
                            st.success('Estoque Atualizado')
                        else:
                            st.error("Erro ao capturar o ID gerado para 'informacoes")
                    else:
                        st.error('Preencha todos os campos necessários!')
            
            elif choice_tipo_saida == 'Perda':
                motivo_perda = st.text_input('Digite o motivo da perda:')
                choice_qtde = st.number_input('Digite a quantidade:', min_value=0)         
                tipo_entrada_saida_id = tipo_saida_dict[choice_tipo_saida]   

                if st.button('Adicionar/Retirar'):

                    if choice_item and choice_qtde > 0 and choice_tipo and motivo_perda:
                        query_add_obs = f"""BEGIN
                                                INSERT INTO informacoes (tipo_entrada_saida_id, motivo_perda) 
                                                VALUES ({tipo_entrada_saida_id}, '{motivo_perda}');
                                                SELECT SCOPE_IDENTITY() AS informacoes_id;
                                            END"""
                        informacoes_id = conn.inserir_dados(query_add_obs, retornar_id=True)     
                        
                        if informacoes_id:
                            query_add_mov = f"""INSERT INTO moviestoque (id_item, tipo_mov_id, quantidade, tipo_entrada_saida_id, informacoes_id)
                                                VALUES ({item_id}, {tipo_mov_id}, {choice_qtde}, {tipo_entrada_saida_id}, {informacoes_id})"""
                            conn.inserir_dados(query_add_mov)
                            st.success('Estoque Atualizado')
                        else:
                            st.error("Erro ao capturar o ID gerado para 'informacoes")
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

        if choice_tipo == 'Entrada':
            query_tipo_entrada = """SELECT tipo_entrada_saida_id, tipo_entrada_saida_nome
                                        FROM entradasaida
                                        WHERE tipo_entrada_saida_id IN (5, 1, 2)"""
            df_tipo_entrada = conn.carregar_dados(query_tipo_entrada)
            df_tipo_entrada['tipo_entrada_saida_nome'] = df_tipo_entrada['tipo_entrada_saida_nome'].replace({'nota_fiscal': 'Nota Fiscal', 'balanco': 'Balanço', 'devolucao': 'Devolução'})
            tipo_entrada_dict = dict(zip(df_tipo_entrada['tipo_entrada_saida_nome'], df_tipo_entrada['tipo_entrada_saida_id'])) 
            choice_tipo_entrada = st.selectbox('Selecione o tipo de entrada:', options=df_tipo_entrada['tipo_entrada_saida_nome'])

            item_id = df_item_material.loc[df_item_material['nome'] == choice_item, 'id_item'].values[0]
            tipo_mov_id = tipo_dict[choice_tipo]

            if choice_tipo_entrada == 'Nota Fiscal':
                numero_nota = st.number_input('Digite o numero da nota:', min_value=0)
                choice_qtde = st.number_input('Digite a quantidade:', min_value=0)
                tipo_entrada_saida_id = tipo_entrada_dict[choice_tipo_entrada]

                if st.button('Adicionar/Retirar'):

                    if choice_item and choice_qtde > 0 and choice_tipo and numero_nota:
                        query_add_nota = f"""BEGIN
                                                INSERT INTO informacoes (tipo_entrada_saida_id, numero_nota) 
                                                VALUES ({tipo_entrada_saida_id}, {numero_nota});
                                                SELECT SCOPE_IDENTITY() AS informacoes_id;
                                            END"""
                        informacoes_id = conn.inserir_dados(query_add_nota, retornar_id=True)   

                        if informacoes_id:
                            query_add_mov = f"""INSERT INTO moviestoque (id_item, tipo_mov_id, quantidade, tipo_entrada_saida_id, informacoes_id) 
                                                VALUES ({item_id}, {tipo_mov_id}, {choice_qtde}, {tipo_entrada_saida_id}, {informacoes_id})"""
                            conn.inserir_dados(query_add_mov)
                            st.success('Estoque Atualizado')
                        else:
                            st.error("Erro ao capturar o ID gerado para 'informacoes")
                    else:
                        st.error('Preencha todos os campos necessários!')

            elif choice_tipo_entrada == 'Balanço':
                choice_qtde = st.number_input('Digite a quantidade:', min_value=0) 
                tipo_entrada_saida_id = tipo_entrada_dict[choice_tipo_entrada]

                if st.button('Adicionar/Retirar'):

                    if choice_item and choice_qtde > 0 and choice_tipo:
                        query_add_balanco = f"""BEGIN
                                                INSERT INTO informacoes (tipo_entrada_saida_id) 
                                                VALUES ({tipo_entrada_saida_id});
                                                SELECT SCOPE_IDENTITY() AS informacoes_id;
                                            END"""
                        informacoes_id = conn.inserir_dados(query_add_balanco, retornar_id=True) 

                        if informacoes_id:
                            query_add_mov = f"""INSERT INTO moviestoque (id_item, tipo_mov_id, quantidade, tipo_entrada_saida_id, informacoes_id) 
                                                VALUES ({item_id}, {tipo_mov_id}, {choice_qtde}, {tipo_entrada_saida_id}, {informacoes_id})"""
                            conn.inserir_dados(query_add_mov)
                            st.success('Estoque Atualizado')
                        else:
                            st.error("Erro ao capturar o ID gerado para 'informacoes")
                    else:
                        st.error('Preencha todos os campos necessários!')        

            elif choice_tipo_entrada == 'Devolução':
                devolucao_obs = st.text_input('Observação:')
                choice_qtde = st.number_input('Digite a quantidade:', min_value=0)         
                tipo_entrada_saida_id = tipo_entrada_dict[choice_tipo_entrada]

                if st.button('Adicionar/Retirar'):

                    if choice_item and choice_qtde > 0 and choice_tipo and devolucao_obs:
                        query_add_obs = f"""BEGIN
                                                INSERT INTO informacoes (tipo_entrada_saida_id, devolucao_obs) 
                                                VALUES ({tipo_entrada_saida_id}, '{devolucao_obs}');
                                                SELECT SCOPE_IDENTITY() AS informacoes_id;
                                            END"""
                        informacoes_id = conn.inserir_dados(query_add_obs, retornar_id=True)     
                        
                        if informacoes_id:
                            query_add_mov = f"""INSERT INTO moviestoque (id_item, tipo_mov_id, quantidade, tipo_entrada_saida_id, informacoes_id)
                                                VALUES ({item_id}, {tipo_mov_id}, {choice_qtde}, {tipo_entrada_saida_id}, {informacoes_id})"""
                            conn.inserir_dados(query_add_mov)
                            st.success('Estoque Atualizado')
                        else:
                            st.error("Erro ao capturar o ID gerado para 'informacoes")
                    else:
                        st.error('Preencha todos os campos necessários!')   
        else:
            query_tipo_saida = """SELECT tipo_entrada_saida_id, tipo_entrada_saida_nome
                                        FROM entradasaida
                                        WHERE tipo_entrada_saida_id != 5"""
            df_tipo_saida = conn.carregar_dados(query_tipo_saida)
            df_tipo_saida['tipo_entrada_saida_nome'] = df_tipo_saida['tipo_entrada_saida_nome'].replace({'balanco': 'Balanço', 'devolucao': 'Devolução', 'paciente': 'Paciente', 'perda': 'Perda'})
            tipo_saida_dict = dict(zip(df_tipo_saida['tipo_entrada_saida_nome'], df_tipo_saida['tipo_entrada_saida_id'])) 
            choice_tipo_saida = st.selectbox('Selecione o tipo de entrada:', options=df_tipo_saida['tipo_entrada_saida_nome'])

            item_id = df_item_material.loc[df_item_material['nome'] == choice_item, 'id_item'].values[0]
            tipo_mov_id = tipo_dict[choice_tipo]

            if choice_tipo_saida == 'Balanço':
                choice_qtde = st.number_input('Digite a quantidade:', min_value=0) 
                tipo_entrada_saida_id = tipo_saida_dict[choice_tipo_saida]

                if st.button('Adicionar/Retirar'):

                    if choice_item and choice_qtde > 0 and choice_tipo:
                        query_add_balanco = f"""BEGIN
                                                INSERT INTO informacoes (tipo_entrada_saida_id) 
                                                VALUES ({tipo_entrada_saida_id});
                                                SELECT SCOPE_IDENTITY() AS informacoes_id;
                                            END"""
                        informacoes_id = conn.inserir_dados(query_add_balanco, retornar_id=True) 

                        if informacoes_id:
                            query_add_mov = f"""INSERT INTO moviestoque (id_item, tipo_mov_id, quantidade, tipo_entrada_saida_id, informacoes_id) 
                                                VALUES ({item_id}, {tipo_mov_id}, {choice_qtde}, {tipo_entrada_saida_id}, {informacoes_id})"""
                            conn.inserir_dados(query_add_mov)
                            st.success('Estoque Atualizado')
                        else:
                            st.error("Erro ao capturar o ID gerado para 'informacoes")
                    else:
                        st.error('Preencha todos os campos necessários!') 

            elif choice_tipo_saida == 'Devolução':
                devolucao_obs = st.text_input('Observação:')
                choice_qtde = st.number_input('Digite a quantidade:', min_value=0)         
                tipo_entrada_saida_id = tipo_saida_dict[choice_tipo_saida]

                if st.button('Adicionar/Retirar'):

                    if choice_item and choice_qtde > 0 and choice_tipo and devolucao_obs:
                        query_add_obs = f"""BEGIN
                                                INSERT INTO informacoes (tipo_entrada_saida_id, devolucao_obs) 
                                                VALUES ({tipo_entrada_saida_id}, '{devolucao_obs}');
                                                SELECT SCOPE_IDENTITY() AS informacoes_id;
                                            END"""
                        informacoes_id = conn.inserir_dados(query_add_obs, retornar_id=True)     
                        
                        if informacoes_id:
                            query_add_mov = f"""INSERT INTO moviestoque (id_item, tipo_mov_id, quantidade, tipo_entrada_saida_id, informacoes_id)
                                                VALUES ({item_id}, {tipo_mov_id}, {choice_qtde}, {tipo_entrada_saida_id}, {informacoes_id})"""
                            conn.inserir_dados(query_add_mov)
                            st.success('Estoque Atualizado')
                        else:
                            st.error("Erro ao capturar o ID gerado para 'informacoes")
                    else:
                        st.error('Preencha todos os campos necessários!')

            elif choice_tipo_saida == 'Paciente':
                paciente_nome = st.text_input('Digite o nome do paciente:')
                choice_qtde = st.number_input('Digite a quantidade:', min_value=0)         
                tipo_entrada_saida_id = tipo_saida_dict[choice_tipo_saida]

                if st.button('Adicionar/Retirar'):

                    if choice_item and choice_qtde > 0 and choice_tipo and paciente_nome:
                        query_add_obs = f"""BEGIN
                                                INSERT INTO informacoes (tipo_entrada_saida_id, paciente_nome) 
                                                VALUES ({tipo_entrada_saida_id}, '{paciente_nome}');
                                                SELECT SCOPE_IDENTITY() AS informacoes_id;
                                            END"""
                        informacoes_id = conn.inserir_dados(query_add_obs, retornar_id=True)     
                        
                        if informacoes_id:
                            query_add_mov = f"""INSERT INTO moviestoque (id_item, tipo_mov_id, quantidade, tipo_entrada_saida_id, informacoes_id)
                                                VALUES ({item_id}, {tipo_mov_id}, {choice_qtde}, {tipo_entrada_saida_id}, {informacoes_id})"""
                            conn.inserir_dados(query_add_mov)
                            st.success('Estoque Atualizado')
                        else:
                            st.error("Erro ao capturar o ID gerado para 'informacoes")
                    else:
                        st.error('Preencha todos os campos necessários!')
            
            elif choice_tipo_saida == 'Perda':
                motivo_perda = st.text_input('Digite o motivo da perda:')
                choice_qtde = st.number_input('Digite a quantidade:', min_value=0)         
                tipo_entrada_saida_id = tipo_saida_dict[choice_tipo_saida]   

                if st.button('Adicionar/Retirar'):

                    if choice_item and choice_qtde > 0 and choice_tipo and motivo_perda:
                        query_add_obs = f"""BEGIN
                                                INSERT INTO informacoes (tipo_entrada_saida_id, motivo_perda) 
                                                VALUES ({tipo_entrada_saida_id}, '{motivo_perda}');
                                                SELECT SCOPE_IDENTITY() AS informacoes_id;
                                            END"""
                        informacoes_id = conn.inserir_dados(query_add_obs, retornar_id=True)     
                        
                        if informacoes_id:
                            query_add_mov = f"""INSERT INTO moviestoque (id_item, tipo_mov_id, quantidade, tipo_entrada_saida_id, informacoes_id)
                                                VALUES ({item_id}, {tipo_mov_id}, {choice_qtde}, {tipo_entrada_saida_id}, {informacoes_id})"""
                            conn.inserir_dados(query_add_mov)
                            st.success('Estoque Atualizado')
                        else:
                            st.error("Erro ao capturar o ID gerado para 'informacoes")
                    else:
                        st.error('Preencha todos os campos necessários!')                           





