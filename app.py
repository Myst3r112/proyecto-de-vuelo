import streamlit as st
import pandas as pd
from logica import *
from graphviz import Digraph

def dibujar_grafo(ruta):
    dot = Digraph()

    dot.attr(rankdir='TB')
    dot.attr('node', shape='circle', style='filled', color='lightblue')

    for pais in ruta:
        dot.node(pais)

    for i in range(len(ruta) - 1):
        dot.edge(ruta[i], ruta[i+1])

    st.sidebar.graphviz_chart(dot)

st.set_page_config(
    page_title="Rutas Aereas",
    page_icon="🛩️",
    layout="centered"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins&display=swap');

html, body, [class*="css"]  {
    font-family: 'Poppins', sans-serif;
}
</style>
""", unsafe_allow_html=True)

st.title("🛩️ Sistema de Rutas Aereas - Matemática Discreta")
st.write("Encuentra rutas entre países")

if "matriz" not in st.session_state:
    st.session_state.matriz = crear_matriz()

if "resultado_busqueda" not in st.session_state:
    st.session_state.resultado_busqueda = None

if "ruta_seleccionada" not in st.session_state:
    st.session_state.ruta_seleccionada = None

st.subheader("🔎 Buscar rutas")

col1, col2 = st.columns(2)
with col1:
    origen = st.selectbox("País de Origen", paises)
with col2:
    destino = st.selectbox("País de Destino", paises)

if st.button("Buscar rutas"):
    valido, mensaje = validar_origen_destino(origen, destino)

    if not valido:
        st.warning(mensaje)
        st.session_state.resultado_busqueda = None
    else:
        A, A2, A3 = calcular_conectividad(st.session_state.matriz)

        st.session_state.resultado_busqueda = {
            "directas": rutas_directas(A, origen, destino),
            "una": rutas_una_escala(A, origen, destino),
            "dos": rutas_dos_escalas(A, origen, destino)
        }

        st.session_state.ruta_seleccionada = None

resultado = st.session_state.resultado_busqueda

if resultado:
    st.subheader("Resultados")

    if resultado["directas"]:
        st.write("✈️ Directo:")
        for i, r in enumerate(resultado["directas"]):
            if st.button(f"Ruta directa {i+1}", key=f"dir_{i}"):
                st.session_state.ruta_seleccionada = r

    if resultado["una"]:
        st.write("🛫 1 escala:")
        for i, r in enumerate(resultado["una"]):
            if st.button(f"Ruta {i+1} (1 escala)", key=f"una_{i}"):
                st.session_state.ruta_seleccionada = r

    if resultado["dos"]:
        st.write("🛬 2 escalas:")
        for i, r in enumerate(resultado["dos"]):
            if st.button(f"Ruta {i+1} (2 escalas)", key=f"dos_{i}"):
                st.session_state.ruta_seleccionada = r

    if not (resultado["directas"] or resultado["una"] or resultado["dos"]):
        st.error("No hay rutas disponibles")

if st.session_state.ruta_seleccionada:
    st.sidebar.subheader("🧭 Ruta seleccionada")
    dibujar_grafo(st.session_state.ruta_seleccionada)

st.sidebar.subheader("🌍 Mapa de ruta")
st.sidebar.info("Aquí irá el mapa mundi (próximamente)")

st.subheader("➕ Agregar nueva ruta")

col1, col2, col3 = st.columns(3)

with col1:
    origen_nuevo = st.selectbox("Origen", paises, key="origen_nuevo")

with col2:
    col2_1, col2_2, col2_3 = st.columns([1,2,1])
    with col2_2:
        st.write("")
        st.write("")
        st.image("imagen/flecha.png", width=80)

with col3:
    destino_nuevo = st.selectbox("Destino", paises, key="destino_nuevo")

if st.button("Agregar ruta"):
    agregado = agregar_ruta(st.session_state.matriz, origen_nuevo, destino_nuevo)

    if agregado:
        st.success("Ruta agregada correctamente")
    else:
        st.warning("No se pudo agregar la ruta")

st.subheader("📶 Matriz de Conectividad")

st.dataframe(
    pd.DataFrame(
        st.session_state.matriz,
        index=paises,
        columns=paises
    )
)