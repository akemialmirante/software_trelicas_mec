import os
import streamlit as st
import pandas as pd
from anastruct import SystemElements

EPSILON = 0.000001


# --- Função para ler arquivo de treliça ---
def ler_trelica(arquivo):
    with open(arquivo, "r") as f:
        linhas = [linha.strip() for linha in f.readlines() if linha.strip()]

    n, m = map(int, linhas[0].split(";"))

    nos = []
    coordenadas = []
    for i in range(1, n + 1):
        partes = linhas[i].split(";")
        nos.append(partes[0])
        coordenadas.append([float(partes[1]), float(partes[2])])

    matriz = []
    for i in range(n + 1, n + 1 + n):
        matriz.append(list(map(int, linhas[i].split(";"))))

    forcas = []
    for i in range(n + 1 + n, n + 1 + n + n):
        Px, Py = map(float, linhas[i].split(";"))
        forcas.append((Px, Py))

    vinculos = []
    for i in range(n + 1 + n + n, n + 1 + n + n + n):
        vinculos.append(linhas[i])

    return n, m, nos, coordenadas, matriz, forcas, vinculos


# --- Função para processar arquivo .txt de treliça ---
def processar_arquivo(caminho_completo):
    n, m, nos, coords, matriz, forcas, vinculos = ler_trelica(caminho_completo)

    ss = SystemElements()
    # Elementos
    for i in range(n):
        for j in range(i + 1, n):
            if matriz[i][j] == 1:
                ss.add_truss_element(location=[coords[i], coords[j]])
    # Vínculos
    for i, v in enumerate(vinculos):
        if v == "P":
            ss.add_support_hinged(node_id=i + 1)
        elif v == "X":
            ss.add_support_roll(node_id=i + 1, direction=2)
        elif v == "Y":
            ss.add_support_roll(node_id=i + 1, direction=1)
    # Forças
    for i, (Fx, Fy) in enumerate(forcas):
        if Fx != 0 or Fy != 0:
            ss.point_load(node_id=i + 1, Fx=Fx, Fy=Fy)

    ss.solve()
    return ss


# --- Streamlit App ---
st.title("🏗️ Análise de Treliças")
st.write("Selecione uma pasta ou carregue arquivos de treliça (.txt) para análise")

# Opção 1: Upload de arquivos
st.subheader("📂 Upload de arquivos")
uploaded_files = st.file_uploader(
    "Escolha arquivos de treliça (.txt)",
    type=['txt'],
    accept_multiple_files=True
)

# # Opção 2: Caminho da pasta
# st.subheader("📁 Caminho da pasta")
# pasta_path = st.text_input("Digite o caminho da pasta com arquivos de treliça:")


# --- Função auxiliar para mostrar resultados ---
def mostrar_resultados(ss):
    st.success("✅ Treliça processada com sucesso!")

    # Mostrar gráficos
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

# --- Processamento ---
if uploaded_files:
    arquivo_selecionado = st.selectbox(
        "Selecione um arquivo para processar:",
        options=[f.name for f in uploaded_files]
    )

    if st.button("Processar Treliça Selecionada"):
        temp_path = f"temp_{arquivo_selecionado}"
        arquivo_obj = next(f for f in uploaded_files if f.name == arquivo_selecionado)
        with open(temp_path, "wb") as f:
            f.write(arquivo_obj.getbuffer())

        ss = processar_arquivo(temp_path)
        mostrar_resultados(ss)

        os.remove(temp_path)

# elif pasta_path and os.path.exists(pasta_path):
#     arquivos = [f for f in os.listdir(pasta_path) if f.endswith(".txt")]
#     if arquivos:
#         arquivo_selecionado = st.selectbox(
#             "Selecione um arquivo para processar:",
#             options=arquivos
#         )

#         if st.button("Processar Treliça da Pasta"):
#             caminho_completo = os.path.join(pasta_path, arquivo_selecionado)
#             ss = processar_arquivo(caminho_completo)
#             mostrar_resultados(ss)
#     else:
#         st.warning("Nenhum arquivo .txt encontrado na pasta especificada.")

# elif pasta_path:
#     st.error("Caminho da pasta não existe ou é inválido.")
