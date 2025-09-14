from mec import processar_trelica
from quadro import quadro_interativo

import streamlit as st
import os as os
import pandas as pd

EPSILON = 0.00001

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # se quiser rodar o quadro html em vez do quadro

if 'current_page' not in st.session_state:
    st.session_state.current_page = 'main'
    #st.rerun()

def mostrar_graficos(ss):
            
    #if(uploaded_files):
        st.success(f"Treliça processada com sucesso!")
        
        col1, col2, col3 = st.columns(3)
                
        with col1:
            st.subheader("Estrutura")   
            fig_structure = ss.show_structure(show = False)
            st.pyplot(fig_structure)
            
        with col2:
            st.subheader("Forças de Reação")
            fig_reaction = ss.show_reaction_force(show=False)
            st.pyplot(fig_reaction)
            
            
        with col3:
            st.subheader("Forças Axiais")
            fig_axial = ss.show_axial_force(show=False)
            st.pyplot(fig_axial)

        # ---- Tabelas ----
        st.subheader("📊 Resultados Numéricos")

        # Descobrir quantos nós e barras existem
        num_nos = max(ss.node_map)
        num_elementos = max(ss.element_map)

        # Reações
        reacoes = []
        for node_id in range(1, num_nos + 1):
            r = ss.get_node_results_system(node_id=node_id)
            if(abs(r["Fx"]) < EPSILON):
                r["Fx"] = 0
            if(abs(r["Fy"]) < EPSILON):
                r["Fy"] = 0
            r["Fx"] = round(r["Fx"], 2) # Quem quiser fazer ficar em 2 algarismos significativos tá convidado
            r["Fy"] = round(r["Fy"], 2)
            reacoes.append({
                "Nó": node_id,
                "Rx": -r["Fx"], # ele acaba invertendo o sentido
                "Ry": -r["Fy"],
            })
        df_reacoes = pd.DataFrame(reacoes)
        st.write("**Reações de Apoio**")
        st.dataframe(df_reacoes, use_container_width=True)

        # Elementos

        elementos = []
        for element_id in range(1, num_elementos + 1):
            e = ss.get_element_results(element_id=element_id)
            axial = (e["Nmax"])
            elementos.append({
                "Elemento": element_id,
                "Força axial": round(axial, 2),
                "Tamanho da barra": round(e["length"], 2),
                "Ângulo em relação ao eixo X": round(e["alpha"], 2)
            })
        df_elementos = pd.DataFrame(elementos)
        st.write("**Elementos**")
        st.dataframe(df_elementos, use_container_width=True)

    
if st.session_state.current_page == 'main':
    
    # visuais primários do streamlit
    st.title("🏗️ Análise de Treliças")
        
    st.subheader("Opção 1: Upload de arquivos individuais")
    uploaded_files = st.file_uploader(
        "Escolha arquivos de treliça (.txt)", 
        type=['txt'], 
        accept_multiple_files=True,
        key="op1"
    )

    # st.subheader("Opção 2: Clique abaixo para ter acesso aos inputs em gráfico interativo:")
    # if st.button("Comece a projetar!"):
    #     st.session_state.current_page = "tracker"

    st.subheader("Opção 2: Quadro com graduação:")
    if st.button("Clique aqui para desenhar!", key="desenhar"):
        st.session_state.current_page = "grid"
   
    # parte do upload do arquivo em si
    if uploaded_files:
        st.write("### Arquivos carregados:")
        
        arquivo_selecionado = st.selectbox(
            "Selecione um arquivo para processar:",
            options=[f.name for f in uploaded_files]
        )
        
        if st.button("Processar Treliça Selecionada", key="processar"):
            
            # parte de abrir o seletor de arquivo via OS
            arquivo_obj = next(f for f in uploaded_files if f.name == arquivo_selecionado)
            temp_path = f"temp_{arquivo_selecionado}"
            with open(temp_path, "wb") as f:
                f.write(arquivo_obj.getbuffer())
            
            
            proc_trel = processar_trelica(temp_path)
            if proc_trel:
                st.session_state.processed_truss = proc_trel
                st.session_state.selected_file = arquivo_selecionado
            os.remove(temp_path)


            if 'processed_truss' in st.session_state and st.session_state.processed_truss:
                mostrar_graficos(st.session_state.processed_truss)
                
                
# if st.session_state.current_page == "tracker":

#     if st.button("← Voltar para Seleção", key="voltar"):
#         st.session_state.current_page = 'main'
#         #st.rerun()
    
#     #temp = quadro_interativo()
#     #mostrar_graficos(temp)
    
#     quadro_interativo()
#     if 'processed_truss' in st.session_state and st.session_state.processed_truss is not None:
#         mostrar_graficos(st.session_state.processed_truss)
if st.session_state.current_page == "grid":
    
    if st.button("← Voltar para Seleção", key="voltar"):
        st.session_state.current_page = 'main'
        #st.rerun()
        
    with open(os.path.join(BASE_DIR, "teste_html.html"), "r", encoding="utf-8") as f:
       html_code = f.read()
      
    st.components.v1.html(html_code, height=600)
    