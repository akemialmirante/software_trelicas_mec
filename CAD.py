import streamlit as st
import pandas as pd
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import math

st.title("Mini-CAD de Treliças")

# --- Sidebar para configuração ---
modo = st.sidebar.selectbox("Modo de desenho:", ["nó (point)", "barra (line)", "força (line)"])
cor = st.sidebar.color_picker("Cor do desenho:", "#000000")
espessura = st.sidebar.slider("Espessura:", 1, 10, 2)
realtime = st.sidebar.checkbox("Atualizar em tempo real", True)

# --- Canvas ---
canvas_result = st_canvas(
    stroke_width=espessura,
    stroke_color=cor,
    background_color="#EEE",
    drawing_mode="point" if modo.startswith("nó") else "line",
    update_streamlit=realtime,
    height=400,
    width=600,
    key="canvas",
)

# --- Processamento dos dados desenhados ---
if canvas_result.json_data is not None:
    objs = pd.json_normalize(canvas_result.json_data["objects"])
    st.subheader("Objetos desenhados (JSON)")
    st.dataframe(objs)

    # Interpretação dos objetos
    nodes = []
    barras = []
    for _, row in objs.iterrows():
        typ = row["type"]
        if typ == "circle" or typ == "point":
            nodes.append((row["left"], row["top"]))
        elif typ == "line":
            barras.append(((row["x1"], row["y1"]), (row["x2"], row["y2"])))

    st.write("Nós:", nodes)
    st.write("Barras:", barras)

    # Exemplo de: aplicar força fixa para cada nó (setas simples)
    for idx, (x, y) in enumerate(nodes):
        fx, fy = 20, -20  # exemplo: força para cima e à direita
        st.write(f"Força no nó {idx+1} ({x:.1f}, {y:.1f}): vetor ({fx}, {fy})")
