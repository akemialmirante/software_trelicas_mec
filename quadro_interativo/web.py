from mec import processar_trelica
from quadro import quadro_interativo

import streamlit as st
from streamlit_drawable_canvas import st_canvas

import os as os

if 'current_page' not in st.session_state:
    st.session_state.current_page = 'main'
    st.rerun()

def mostrar_graficos(ss):
            
    if(uploaded_files):
        st.success(f"Treliça {arquivo_selecionado} processada com sucesso!")
        
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


if st.session_state.current_page == 'main':
    
    # visuais primários do streamlit
    st.title("🏗️ Análise de Treliças")
        
    st.subheader("Opção 1: Upload de arquivos individuais")
    uploaded_files = st.file_uploader(
        "Escolha arquivos de treliça (.txt)", 
        type=['txt'], 
        accept_multiple_files=True
    )

    st.subheader("Opção 2: Clique abaixo para ter acesso aos inputs em gráfico interativo:")
    if st.button("Comece a projetar!"):
        st.session_state.current_page = "tracker"

   
    # parte do upload do arquivo em si
    if uploaded_files:
        st.write("### Arquivos carregados:")
        
        arquivo_selecionado = st.selectbox(
            "Selecione um arquivo para processar:",
            options=[f.name for f in uploaded_files]
        )
        
        if st.button("Processar Treliça Selecionada"):
            
            # parte de abrir o seletor de arquivo via OS
            arquivo_obj = next(f for f in uploaded_files if f.name == arquivo_selecionado)
            temp_path = f"temp_{arquivo_selecionado}"
            with open(temp_path, "wb") as f:
                f.write(arquivo_obj.getbuffer())
            
            
            proc_trel = processar_trelica(temp_path)
            if proc_trel:
                mostrar_graficos(proc_trel)
                
            os.remove(temp_path)
            
if st.session_state.current_page == "tracker":

    if st.button("← Voltar para Seleção"):
        st.session_state.current_page = 'main'
        st.rerun()
    
    quadro_interativo()