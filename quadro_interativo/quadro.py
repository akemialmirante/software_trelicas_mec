import streamlit as st
from streamlit_drawable_canvas import st_canvas

import numpy as np
import tempfile
import os

from mec import processar_trelica

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def extrair_quadro(canvas_result):
    """Nós & Conexões vindos do quadro"""
    
    if not canvas_result.json_data or not canvas_result.json_data.get("objects"):   # se não tem nada no quadro, retorna nada...
        return None, None, None, None
    
    objects = canvas_result.json_data["objects"]
    
    nos = []
    conexoes = []
    forcas = []
    suportes = []
    
    for obj in objects:
        if obj["type"] == "circle":  # nós = circulos
            
            nos.append({
                "id": len(nos),
                "x": obj["left"] + obj["radius"],
                "y": obj["top"] + obj["radius"],
                "radius": obj["radius"]
            })
            
        elif obj["type"] == "line":\
            
            x1_abs = obj["left"] + obj["x1"]
            y1_abs = obj["top"] + obj["y1"]
            x2_abs = obj["left"] + obj["x2"]
            y2_abs = obj["top"] + obj["y2"]

            conexoes.append({
            "x1": x1_abs,
            "y1": y1_abs,
            "x2": x2_abs,
            "y2": y2_abs
            })
            
        """  elif obj["type"] == "line":  # conexoes = linhas entre nós
            
            conexoes.append({
                "x1": obj["x1"],
                "y1": obj["y1"], 
                "x2": obj["x2"],
                "y2": obj["y2"]
            }) 
        """
            
    return nos, conexoes, forcas, suportes


def find_node_connections(nodes, connections, tolerance=20):
    """criar a matriz de conexão baseado na existência de 2 nós mais próximos à conexão."""


    n = len(nodes)
    connectivity_matrix = [[0 for _ in range(n)] for _ in range(n)]
    
    for connection in connections:
        
        start_node = None
        end_node = None
        
        for i, node in enumerate(nodes):
            
            # checar distância entre a posição (x,y)conexão e (x,y)nó
            dist_start = np.sqrt((connection["x1"] - node["x"])**2 + (connection["y1"] - node["y"])**2)
            if dist_start <= tolerance:
                start_node = i
            
            # a mesma coisa para outro nó
            dist_end = np.sqrt((connection["x2"] - node["x"])**2 + (connection["y2"] - node["y"])**2)
            if dist_end <= tolerance:
                end_node = i
        
        # se estiver na lógica de que estão em posições diferentes porém unem os polos da conexão, são armazenados
        if start_node is not None and end_node is not None and start_node != end_node:
            connectivity_matrix[start_node][end_node] = 1
            connectivity_matrix[end_node][start_node] = 1
    
    return connectivity_matrix


def canvas_to_file_format(nos, conexoes, forces_input=None, supports_input=None):
    """tradutor     dados.quadro -> dados.arquivo   para o ler_arquivo()"""
    
    if not nos:
        return None
    
    n = len(nos)
    connectivity_matrix = find_node_connections(nos, conexoes)
    
    # Calcular nº conexões
    m = sum(sum(row[i+1:]) for i, row in enumerate(connectivity_matrix))
    
    
    file_lines = [] # linhas do texto
    
    # linha 1: n;m 
    file_lines.append(f"{n};{m}")
    
    # linha 2 até n+1: nós (nome;x;y)
    for i, node in enumerate(nos):
        file_lines.append(f"N{i+1};{node['x']:.1f};{node['y']:.1f}")
    
    # linha n+2 até 2n+1: matriz de conexões
    for row in connectivity_matrix:
        file_lines.append(";".join(map(str, row)))
    
    
    # linha 2n+2 até 3n+1: forças (Fx;Fy)
    for i in range(n):
        if forces_input and i < len(forces_input):
            fx, fy = forces_input[i]
            file_lines.append(f"{fx};{fy}")
        else:
            file_lines.append("0;0")  # default: força = 0
    
    
    # linhas 3n+2 até 4n+1: suportes
    for i in range(n):
        if supports_input and i < len(supports_input):
            file_lines.append(supports_input[i])
        else:
            file_lines.append("L")  # default: livre
    
    return "\n".join(file_lines)


def processar_trelica_quadro(canvas_result, forces_data=None, supports_data=None):
    """processo completo de pegar do quadro, passar para a id dos nós e conexões, depois pro txt."""
    
    
    nos, conexoes, forcas, suportes = extrair_quadro(canvas_result)
    
    if not nos:
        return None
    
    # passando pro formato do txt
    file_content = canvas_to_file_format(nos, conexoes, forces_data, supports_data)
    
    if not file_content:
        return None
    
    # temp_file.txt para processamento
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
        temp_file.write(file_content)
        temp_path = temp_file.name
    
    try:
        result = processar_trelica(temp_path)   # hora de processar usando a função já existente. o try vem da necessidade criada por um except la no mec.
        return result
    
    finally:
        if os.path.exists(temp_path):           # apaga-se o arquivo temporário
            os.remove(temp_path)


def quadro_interativo():
    """Quadro interativo que transforma seu desenho em solução.""" 
    
    # nesse momento quando atribui-se um novo título para a janela, a sessão muda completamente.
    
    st.title("🎨 Quadro Interativo")
    
    st.write("""               
    **Instruções:**
    1. Circle -> criar nós
    2. Line -> criar conexões
    3. Insira as forças abaixo
    4. Clique em "Análise da Estrutura" para começar
    """) 
    
    drawing_mode = st.selectbox(
        "Modo de Desenho:",
        ["circle", "line"]
    )
    
    st.markdown("""
    <style>
    canvas {
        background-image: 
            linear-gradient(rgba(200,200,200,0.3) 1px, transparent 1px),
            linear-gradient(90deg, rgba(200,200,200,0.3) 1px, transparent 1px);
        background-size: 25px 25px !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # config do quadro
    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",
        stroke_width=3,
        stroke_color="#000",
        background_color="#FFF",
        background_image=None,
        update_streamlit=True,
        height=400,
        width=600,
        drawing_mode=drawing_mode,
        key="truss_canvas",
    )
    
    # Show extracted data
    if canvas_result.json_data:
        nodes, connections, forces, supports = extrair_quadro(canvas_result)
        
        if nodes:
            st.write(f"**Detectados:** {len(nodes)} nós, {len(connections)} conexões")
            
            # detalhes de nós
            with st.expander("Detalhes dos nós:"):
                for i, node in enumerate(nodes):
                    st.write(f"Nó {i+1}: ({node['x']:.1f}, {node['y']:.1f})")
            
            
            # input de forças
            st.subheader("⚡ Forças")
            forces_data = []
            cols = st.columns(min(len(nodes), 4))
            
            for i, node in enumerate(nodes):
                with cols[i % 4]:
                    
                    st.write(f"**Nó {i+1}**")
                    fx = st.number_input(f"Fx", key=f"fx_{i}", value=0.0, step=0.1)
                    fy = st.number_input(f"Fy", key=f"fy_{i}", value=0.0, step=0.1)
                    forces_data.append((fx, fy))
            
            
            # input de suportes
            st.subheader("🔗 Suportes")
            supports_data = []
            cols = st.columns(min(len(nodes), 4))
            
            for i, node in enumerate(nodes):
                with cols[i % 4]:
                    support_type = st.selectbox(
                        f"No {i+1}",
                        ["L", "P", "X", "Y"],
                        key=f"support_{i}",
                        help="L=Livre, P=Fixo, X=Rolete, Y=Apoio Lateral"
                    )
                    supports_data.append(support_type)
            
            
            # botão para análise
            if st.button("🔍 Análise de Estutura", type="primary"):
                with st.spinner("Processando..."):
                    processed_truss = processar_trelica_quadro(
                        canvas_result, 
                        forces_data, 
                        supports_data
                    )
                    
                    if processed_truss:
                        st.session_state.processed_truss = processed_truss
                        return processed_truss
                    else:
                        st.error("Análise falhou! Desenhe melhor da próxima vez... 😏")
            
            
            with st.expander("🔍 TXT gerado (Debug)"):
                file_content = canvas_to_file_format(nodes, connections, forces_data, supports_data)
                st.code(file_content, language="text")
    
    else:
        st.info("Comece a desenhar para ver informações sobre nós e conexões!")

if __name__ == "__main__":
    quadro_interativo()