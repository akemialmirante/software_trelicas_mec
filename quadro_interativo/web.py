from mec import processar_trelica

import streamlit as st
import os
import pandas as pd
import math

EPSILON = 0.00001

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# === inicializações únicas no session_state ===
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'main'

# Guarda o objeto processado (AnaStruct ou similar)
if 'processed_truss' not in st.session_state:
    st.session_state.processed_truss = None

# Propriedades finais confirmadas (copiadas apenas ao confirmar)
if 'E_barras' not in st.session_state:
    st.session_state.E_barras = {}

if 'd_barras' not in st.session_state:
    st.session_state.d_barras = {}

if 'trelica_confirmada' not in st.session_state:
    st.session_state.trelica_confirmada = False


def init_edit_keys_if_needed(ss):
    """Inicializa chaves temporárias E_edit_i / d_edit_i apenas se não existirem.
       Deve ser chamada sempre que um novo 'ss' (trelica) for carregado/alterado."""
    try:
        num_elementos = max(ss.element_map)
    except Exception:
        return

    for i in range(1, num_elementos + 1):
        keyE = f"E_edit_{i}"
        keyD = f"d_edit_{i}"
        if keyE not in st.session_state:
            st.session_state[keyE] = 210e6
        if keyD not in st.session_state:
            st.session_state[keyD] = 0.05


def mostrar_graficos(ss):
    st.success("Treliça processada com sucesso!")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Estrutura")
        fig_structure = ss.show_structure(show=False)
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

    num_nos = max(ss.node_map)

    # Reações
    reacoes = []
    for node_id in range(1, num_nos + 1):
        r = ss.get_node_results_system(node_id=node_id)
        if abs(r["Fx"]) < EPSILON:
            r["Fx"] = 0
        if abs(r["Fy"]) < EPSILON:
            r["Fy"] = 0
        r["Fx"] = round(r["Fx"], 2)
        r["Fy"] = round(r["Fy"], 2)
        reacoes.append({
            "Nó": node_id,
            "Rx": -r["Fx"],
            "Ry": -r["Fy"],
        })
    
    df_reacoes = pd.DataFrame(reacoes)
    st.write("**Reações de Apoio**")
    st.dataframe(df_reacoes, width='stretch')
 


def props_barra(ss):

    st.write("**Defina Propriedades das Barras (edite e confirme)**")

    # inicializa chaves temporárias caso necessário (só uma vez por trelica carregada)
    init_edit_keys_if_needed(ss)

    num_elementos = max(ss.element_map)

    # Renderiza inputs para edição (essenciais: keys "E_edit_i" e "d_edit_i")
    for element_id in range(1, num_elementos + 1):
        keyE = f"E_edit_{element_id}"
        keyD = f"d_edit_{element_id}"

        colE, cold = st.columns(2)
        
        with colE:
            # não atribuir ao session_state diretamente — o widget grava por si
            st.number_input(
                f"Módulo de Elasticidade (Barra {element_id}) [Pa]",
                min_value=1.0,
                value=st.session_state.get(keyE, 210e6),
                step=1e6,
                format="%.2e",
                key=keyE
            )


        with cold:
            st.number_input(
                        f"Diâmetro da Barra {element_id} [m]",
                        min_value=0.001,
                        value=st.session_state.get(keyD, 0.05),
                        step=0.01,
                        format="%.3f",
                        key=keyD
            )



    # Botão que confirma as propriedades (só então salva em E_barras/d_barras)
    if st.button("✅ Confirmar propriedades das barras"):
        
        E_final = {}
        d_final = {}

        for element_id in range(1, num_elementos + 1):
            E_final[element_id] = st.session_state[f"E_edit_{element_id}"]
            d_final[element_id] = st.session_state[f"d_edit_{element_id}"]

        st.session_state.E_barras = E_final
        st.session_state.d_barras = d_final
        st.session_state.trelica_confirmada = True
        st.success("Propriedades confirmadas — calculando deformações...")

    # Exibe tabela de deformações apenas se confirmado
    if st.session_state.trelica_confirmada:
        elementos = []
        for element_id in range(1, num_elementos + 1):
            e = ss.get_element_results(element_id=element_id)
            axial = e["Nmax"]
            L = e["length"]

            E = st.session_state.E_barras[element_id]
            d = st.session_state.d_barras[element_id]

            A = math.pi * (d**2) / 4.0
            epsilon = axial / (E * A) if E * A != 0 else float('nan')
            delta_L = epsilon * L

            elementos.append({
                "Elemento": element_id,
                "Força axial [N]": round(axial, 2),
                "Comprimento [m]": round(L, 3),
                "Área [m²]": round(A, 6),
                "Deformação ε": f"{epsilon:.3e}",
                "Alongamento ΔL [m]": f"{delta_L:.3e}",
                "Ângulo [rad]": round(e["alpha"], 3)
            })

        df_elementos = pd.DataFrame(elementos)
        st.write("**Elementos com Deformações e Alongamentos**")
        st.dataframe(df_elementos, width='stretch')

        st.subheader("Gráfico Deslocamento:")
        fig_disp = ss.show_displacement(show = False)
        st.pyplot(fig_disp)

    else:
        st.info("Altere as propriedades e clique em 'Confirmar propriedades das barras' para ver deformações e alongamentos.")


   

# ===================== fluxo principal da app =====================

if st.session_state.current_page == 'main':
    
    st.title("🏗️ Análise de Treliças")

    st.subheader("Opção 1: Upload de arquivos individuais")
    uploaded_files = st.file_uploader(
        "Escolha arquivos de treliça (.txt)",
        type=['txt'],
        accept_multiple_files=True,
        key="op1"
    )

    # parte do upload do arquivo em si
    if uploaded_files:
        st.write("### Arquivos carregados:")
        arquivo_selecionado = st.selectbox(
            "Selecione um arquivo para processar:",
            options=[f.name for f in uploaded_files]
        )

        if st.button("Processar Treliça Selecionada", key="processar"):
            arquivo_obj = next(f for f in uploaded_files if f.name == arquivo_selecionado)
            temp_path = f"temp_{arquivo_selecionado}"
            with open(temp_path, "wb") as f:
                f.write(arquivo_obj.getbuffer())

            proc_trel = processar_trelica(temp_path)
            if proc_trel:
                st.session_state.processed_truss = proc_trel
                # inicializa chaves de edição agora que a trelica foi carregada
                init_edit_keys_if_needed(proc_trel)
                st.session_state.trelica_confirmada = False  # força nova confirmação
                st.success(f"Treliça '{arquivo_selecionado}' processada.")
            os.remove(temp_path)


    st.subheader("Opção 2: Quadro com graduação:")
    if st.button("Clique aqui para desenhar!", key="desenhar"):
        st.session_state.current_page = "grid"

    
    # **IMPORTANTE**: mostramos os gráficos sempre que tivermos uma trelica processada
    if st.session_state.processed_truss is not None:
        mostrar_graficos(st.session_state.processed_truss)
        props_barra(st.session_state.processed_truss)



# grid page
if st.session_state.current_page == "grid":
    if st.button("← Voltar para Seleção", key="voltar"):
        st.session_state.current_page = 'main'

    with open(os.path.join(BASE_DIR, "teste_html.html"), "r", encoding="utf-8") as f:
        html_code = f.read()

    st.components.v1.html(html_code, height=600)
