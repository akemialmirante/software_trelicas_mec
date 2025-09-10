from mec import processar_trelica
from quadro import *

import streamlit as st

import os as os

if 'current_page' not in st.session_state:
    st.session_state.current_page = 'main'
    st.rerun()

def pegar_detalhes(ss):
    
    resultados = []
    for i in range(len(canvas_to_file_format.no)):
        resultados.append(ss.get_element_results(i))
        
        
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
                st.session_state.processed_truss = proc_trel
                st.session_state.selected_file = arquivo_selecionado
            os.remove(temp_path)


            if 'processed_truss' in st.session_state and st.session_state.processed_truss:
                mostrar_graficos(st.session_state.processed_truss)
                
            if st.button("Gerar relatório"):
                st.session_state.current_page = "relatorio"
                st.rerun()
                        
                        
if st.session_state.current_page == "relatorio":
    with st.spinner("Processando..."):
                        
        import datetime
        hour = datetime.datetime.now().hour
                        
        os.makedirs(f"relatorios{hour}", exist_ok=True)
                            
        relatorio = f"relatorio.txt"
        with open("relatorio.txt", "w") as f:
            st.write("gozei")
                                
            f.write(f"{len(canvas_to_file_format.no)}")
            f.write(f"{pegar_detalhes(proc_trel)}")
                                
            f_struct = st.session_state.processed_truss.show_structure(show=False)
            f_struct.savefig(f"relatorios{hour}/estrutura.png", dpi=300, bbox_inches='tight')
            f_react = proc_trel.show_reaction_force(show=False)
            f_react.savefig(f"relatorios{hour}/f_reacao.png", dpi=300, bbox_inches='tight')
            f_ax = proc_trel.show_axial_force(show=False)
            f_react.savefig(f"relatorios{hour}/f_axiais.png", dpi=300, bbox_inches='tight')
                
            f.write(f"{pegar_detalhes(st.session_state.processed_truss)}")
            
    os.rename("relatorio.txt", "relatorio_{hour}.txt")
    st.session_state.current_page = "main"
    
    
if st.session_state.current_page == "tracker":

    if st.button("← Voltar para Seleção"):
        st.session_state.current_page = 'main'
        st.rerun()
    
    quadro_interativo()
    
    