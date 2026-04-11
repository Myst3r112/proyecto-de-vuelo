import streamlit as st
import pandas as pd
from logica import *

st.set_page_config(
    page_title="Rutas Aéreas",
    page_icon="🛩️",
    layout="wide"
)

st.markdown("""
    <style>
    button {
        transition: all 0.2s ease;
    }
    button:hover {
        transform: scale(1.02);
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    div[data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
    }
    </style>
    """, 
    unsafe_allow_html=True
)

fondo = cargar_imagen("imagen/fondo.png")

st.markdown(f"""
    <div style="
        background-image: 
            linear-gradient(rgba(15,23,42,0.7), rgba(30,64,175,0.7)),
            url('data:image/png;base64,{fondo}');
        background-size: cover;
        background-position: center;
        padding: 28px;
        border-radius: 18px;
        color: white;
        margin-bottom: 18px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.25);
    ">
        <h1 style="margin: 0; font-size: 32px;">🛩️ Sistema de Rutas Aéreas</h1>
        <p style="margin: 8px 0 0 0; font-size: 16px;">
            Proyecto de Matemática Discreta: análisis de rutas mediante matrices de conectividad y grafos.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

if "matriz" not in st.session_state:
    st.session_state.matriz = generar_matriz_aleatoria(len(paises), probabilidad=0.2)

if "resultado_busqueda" not in st.session_state:
    st.session_state.resultado_busqueda = None

if "ruta_seleccionada" not in st.session_state:
    st.session_state.ruta_seleccionada = None

col_main, col_panel = st.columns([2.2, 1], gap="large")

with col_main:
    tab1, tab2, tab3 = st.tabs([
        "🔎 Buscar rutas",
        "➕ Agregar ruta",
        "📶 Matriz de conectividad"
    ])

    with tab1:
        st.subheader("Buscar rutas entre países")

        c1, c2 = st.columns(2)
        with c1:
            origen = st.selectbox("País de origen", paises)
        with c2:
            destino = st.selectbox("País de destino", paises)

        if st.button("Buscar rutas", use_container_width=True):
            valido, mensaje = validar_origen_destino(origen, destino)

            if not valido:
                st.warning(mensaje)
                st.session_state.resultado_busqueda = None
                st.session_state.ruta_seleccionada = None
            else:
                A, A2, A3 = calcular_conectividad(st.session_state.matriz)

                st.session_state.resultado_busqueda = {
                    "directas": rutas_directas(A, origen, destino),
                    "una": rutas_una_escala(A, origen, destino),
                    "dos": rutas_dos_escalas(A, origen, destino),
                    "A2_valor": A2[paises.index(origen)][paises.index(destino)],
                    "A3_valor": A3[paises.index(origen)][paises.index(destino)],
                }

        resultado = st.session_state.resultado_busqueda

        if resultado:
            st.divider()
            st.subheader("Resultados de la búsqueda")

            d1, d2, d3 = st.columns(3)
            with d1:
                st.metric("Directas", len(resultado["directas"]))
            with d2:
                st.metric("Con 1 escala", len(resultado["una"]))
            with d3:
                st.metric("Con 2 escalas", len(resultado["dos"]))

            st.caption(
                f"A² entre origen y destino: {resultado['A2_valor']} | "
                f"A³ entre origen y destino: {resultado['A3_valor']}"
            )

            if resultado["directas"]:
                st.markdown("### ✈️ Rutas directas")
                for i, ruta in enumerate(resultado["directas"]):
                    texto = " → ".join(ruta)
                    if st.button(texto, key=f"dir_{i}", use_container_width=True):
                        st.session_state.ruta_seleccionada = ruta

            if resultado["una"]:
                st.markdown("### 🛫 Rutas con 1 escala")
                for i, ruta in enumerate(resultado["una"]):
                    texto = " → ".join(ruta)
                    if st.button(texto, key=f"una_{i}", use_container_width=True):
                        st.session_state.ruta_seleccionada = ruta

            if resultado["dos"]:
                st.markdown("### 🛬 Rutas con 2 escalas")
                for i, ruta in enumerate(resultado["dos"]):
                    texto = " → ".join(ruta)
                    if st.button(texto, key=f"dos_{i}", use_container_width=True):
                        st.session_state.ruta_seleccionada = ruta

            if not (resultado["directas"] or resultado["una"] or resultado["dos"]):
                st.info("No se encontraron rutas entre los países seleccionados.")

    with tab2:
        st.subheader("Agregar nueva ruta aérea")

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

        if st.button("Agregar ruta", use_container_width=True):
            agregado = agregar_ruta(st.session_state.matriz, origen_nuevo, destino_nuevo)

            if agregado:
                st.success("Ruta agregada correctamente.")
                st.session_state.resultado_busqueda = None
                st.session_state.ruta_seleccionada = None
            else:
                st.warning("No se pudo agregar la ruta. Puede ser inválida o ya existir.")

    with tab3:
        st.subheader("Matriz de conectividad de vuelos directos")

        df_matriz = pd.DataFrame(
            st.session_state.matriz,
            index=paises,
            columns=paises
        )

        st.dataframe(df_matriz, use_container_width=True)

with col_panel:
    st.subheader("🧭 Visualización de la ruta")
    st.caption("🟢 Origen   🔵 Escala   🔴 Destino")

    if st.session_state.ruta_seleccionada:
        st.markdown(f"**Ruta seleccionada:** {' → '.join(st.session_state.ruta_seleccionada)}")
        espacio_izq, centro, espacio_der = st.columns([1, 1, 1])
        with centro:
            dibujar_grafo(st.session_state.ruta_seleccionada, st)
    else:
        st.markdown("""
            <div style="
                background: linear-gradient(90deg, #0f172a, #1e40af);
                padding: 14px;
                border-radius: 12px;
                text-align: center;
                font-weight: 600;
                color: white;
            ">
                ✈️ Selecciona una ruta para visualizar el grafo
            </div>
        """, unsafe_allow_html=True)

    st.divider()

    coordenadas = cargar_coordenadas("datos/coordenadas_paises.csv")

    st.subheader("🌍 Mapa interactivo")

    if st.session_state.ruta_seleccionada:
        dibujar_mapa(st.session_state.ruta_seleccionada, st, coordenadas)
    else:
        st.markdown("""
            <div style="
                background: linear-gradient(90deg, #0f172a, #1e40af);
                padding: 14px;
                border-radius: 12px;
                text-align: center;
                font-weight: 600;
                color: white;
            ">
                ✈️ Selecciona una ruta para visualizar el mapa
            </div>
        """, unsafe_allow_html=True)
