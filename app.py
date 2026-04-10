import streamlit as st
import pandas as pd
from logica import *

st.set_page_config(
    page_title="Rutas Aereas",
    page_icon="🛩️",
    layout="wide"
)

st.title("🛩️ Sistema de Rutas Aéreas - Matemática Discreta")

if "matriz" not in st.session_state:
    st.session_state.matriz = generar_matriz_aleatoria(len(paises), probabilidad = 0.1)

if "resultado_busqueda" not in st.session_state:
    st.session_state.resultado_busqueda = None

if "ruta_seleccionada" not in st.session_state:
    st.session_state.ruta_seleccionada = None

col_main, col_panel = st.columns([2.2, 1], gap="large")

with col_main:
    st.subheader("🔎 Buscar rutas")

    c1, c2 = st.columns(2)
    with c1:
        origen = st.selectbox("País de origen", paises)
    with c2:
        destino = st.selectbox("País de destino", paises)

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
                "dos": rutas_dos_escalas(A, origen, destino),
            }

    resultado = st.session_state.resultado_busqueda

    if resultado:
        st.subheader("Resultados")

        if resultado["directas"]:
            st.write("✈️ Directo")
            for i, r in enumerate(resultado["directas"]):
                if st.button(f"Ruta directa {i+1}", key=f"dir_{i}"):
                    st.session_state.ruta_seleccionada = r

        if resultado["una"]:
            st.write("🛫 1 escala")
            for i, r in enumerate(resultado["una"]):
                if st.button(f"Ruta {i+1} (1 escala)", key=f"una_{i}"):
                    st.session_state.ruta_seleccionada = r

        if resultado["dos"]:
            st.write("🛬 2 escalas")
            for i, r in enumerate(resultado["dos"]):
                if st.button(f"Ruta {i+1} (2 escalas)", key=f"dos_{i}"):
                    st.session_state.ruta_seleccionada = r
        
        if not (resultado["directas"] or resultado["una"] or resultado["dos"]):
            st.info("No se encontraron rutas entre los países seleccionados.")    

    st.subheader("➕ Agregar nueva ruta")
    a1, a2, a3 = st.columns([3, 1, 3])

    with a1:
        origen_nuevo = st.selectbox("Origen", paises, key="origen_nuevo")
    with a2:
        flecha = cargar_imagen("imagen/flecha.png")

        st.markdown(
            f"""
            <div style="
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100%;
                margin-top: 38px;
            ">
                <img src="data:image/png;base64,{flecha}" width="70">
            </div>
            """,
            unsafe_allow_html=True
        )
    with a3:
        destino_nuevo = st.selectbox("Destino", paises, key="destino_nuevo")

    if st.button("Agregar ruta"):
        agregado = agregar_ruta(st.session_state.matriz, origen_nuevo, destino_nuevo)

        if agregado:
            st.success("Ruta agregada correctamente")
            st.session_state.resultado_busqueda = None
            st.session_state.ruta_seleccionada= None

        else:
            st.warning("No se pudo agregar la ruta")

    st.subheader("📶 Matriz de conectividad")
    st.dataframe(
        pd.DataFrame(
            st.session_state.matriz,
            index=paises,
            columns=paises
        )
    )

with col_panel:
    st.subheader("Ruta seleccionada")
    if st.session_state.ruta_seleccionada:
        dibujar_grafo(st.session_state.ruta_seleccionada, st)
    else:
        st.info("Selecciona una ruta para ver el grafo.")

    st.subheader("Mapa interactivo")
    st.info("Aquí irá el mapa mundi.")