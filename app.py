import pandas as pd
import streamlit as st
from logica import (
    cargar_imagen,
    cargar_datos_csv,
    paises,
    crear_matriz,
    validar_origen_destino,
    agregar_ruta,
    analizar_conectividad_matricial,
    calcular_destinos,
    rutas_directas,
    rutas_una_escala,
    rutas_dos_escalas,
    dibujar_grafo,
    dibujar_mapa
)

st.set_page_config(
    page_title="Rutas Aéreas",
    page_icon="🛩️",
    layout="wide"
)

def aplicar_estilos():
    st.markdown(
        """
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

def mostrar_encabezado():
    fondo = cargar_imagen("imagen/fondo.png")
    st.markdown(
        f"""
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

def inicializar_estado():
    if "matriz" not in st.session_state:
        st.session_state.matriz = crear_matriz(len(paises))

    if "resultado_busqueda" not in st.session_state:
        st.session_state.resultado_busqueda = None

    if "ruta_seleccionada" not in st.session_state:
        st.session_state.ruta_seleccionada = None

def limpiar_busqueda():
    st.session_state.resultado_busqueda = None
    st.session_state.ruta_seleccionada = None

def mostrar_mensaje_panel(texto):
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(90deg, #0f172a, #1e40af);
            padding: 14px;
            border-radius: 12px;
            text-align: center;
            font-weight: 600;
            color: white;
        ">
            {texto}
        </div>
        """,
        unsafe_allow_html=True
    )

def mostrar_botones_rutas(titulo, rutas):
    if not rutas: return

    st.markdown(titulo)
    for _, ruta in enumerate(rutas):
        texto = " → ".join(ruta)

        if st.button(texto, use_container_width=True):
            st.session_state.ruta_seleccionada = ruta

def mostrar_resultados(resultado):
    analisis = resultado["analisis"]

    st.divider()
    st.subheader("Resultados de la búsqueda")

    dato1, dato2, dato3 = st.columns(3)

    with dato1: st.metric("Directas", len(resultado["directas"]))
    with dato2: st.metric("Con 1 escala", len(resultado["una_escala"]))
    with dato3: st.metric("Con 2 escalas", len(resultado["dos_escalas"]))

    st.caption(
        "Se encontraron"
        f" {len(resultado['directas'])} rutas directas | "
        f" {len(resultado['una_escala'])} rutas con 1 escala | "
        f" {len(resultado['dos_escalas'])} rutas con 2 escalas"
    )

    if not analisis["hay_conectividad"]:
        st.info("No se encontraron rutas disponibles entre estos países hasta 2 escalas.")
        return

    mostrar_botones_rutas("### ✈️ Rutas directas", resultado["directas"])
    mostrar_botones_rutas("### 🛫 Rutas con 1 escala", resultado["una_escala"])
    mostrar_botones_rutas("### 🛬 Rutas con 2 escalas", resultado["dos_escalas"])

    if not (resultado["directas"] or resultado["una_escala"] or resultado["dos_escalas"]):
        st.info("La matriz detectó conectividad, pero no se encontraron rutas válidas sin repetir países.")

def main():
    aplicar_estilos()
    mostrar_encabezado()
    inicializar_estado()

    columna_main, columna_panel = st.columns([2.2, 1], gap="large")

    with columna_main:
        tabla1, tabla2, tabla3 = st.tabs([
            "🔎 Buscar rutas",
            "➕ Agregar ruta",
            "📶 Matriz de conectividad"
        ])

        with tabla1:
            st.subheader("Buscar rutas entre países")

            bloque1, bloque2 = st.columns(2)
            with bloque1: origen = st.selectbox("País de origen", paises)

            destinos_disponibles = calcular_destinos(st.session_state.matriz, origen)

            with bloque2: destino = st.selectbox("País de destino", destinos_disponibles)

            if st.button("Buscar rutas", use_container_width=True):
                valido, mensaje = validar_origen_destino(origen, destino)

                if not valido:
                    st.warning(mensaje)
                    limpiar_busqueda()
                else:
                    analisis = analizar_conectividad_matricial(st.session_state.matriz, origen, destino)
                    st.session_state.resultado_busqueda = {
                        "analisis": analisis,
                        "directas": rutas_directas(analisis["A"], origen, destino),
                        "una_escala": rutas_una_escala(analisis["A"], origen, destino),
                        "dos_escalas": rutas_dos_escalas(analisis["A"], origen, destino),
                    }
                    st.session_state.ruta_seleccionada = None

            if st.session_state.resultado_busqueda:
                mostrar_resultados(st.session_state.resultado_busqueda)

        with tabla2:
            st.subheader("Agregar nueva ruta aérea")

            bloque1, bloque2, bloque3 = st.columns([3, 1, 3])

            with bloque1: origen_nuevo = st.selectbox("Origen", paises)

            with bloque2:
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

            with bloque3: destino_nuevo = st.selectbox("Destino", paises)

            if st.button("Agregar ruta", use_container_width=True):
                agregado = agregar_ruta(st.session_state.matriz, origen_nuevo, destino_nuevo)

                if agregado:
                    st.success("Ruta agregada correctamente.")
                    limpiar_busqueda()
                else: st.warning("No se pudo agregar la ruta, ya existe")

        with tabla3:
            st.subheader("Matriz de conectividad de vuelos directos")

            df_matriz = pd.DataFrame(
                st.session_state.matriz,
                index=paises,
                columns=paises
            )
            
            st.dataframe(df_matriz, use_container_width=True)


    with columna_panel:
        st.subheader("🧭 Visualización de la ruta")
        st.caption("🟢 Origen   🔵 Escala   🔴 Destino")

        if st.session_state.ruta_seleccionada:
            st.markdown(
                f"**Ruta seleccionada:** "
                f"{' → '.join(st.session_state.ruta_seleccionada)}"
            )

            _, centro, _ = st.columns(3)
            with centro: dibujar_grafo(st.session_state.ruta_seleccionada, st)
        else: mostrar_mensaje_panel("✈️ Selecciona una ruta para visualizar el grafo")

        st.divider()
        st.subheader("🌍 Mapa interactivo")

        coordenadas = cargar_datos_csv("datos/coordenadas_paises.csv", tipo_dato='coordenadas')
        if st.session_state.ruta_seleccionada: dibujar_mapa(st.session_state.ruta_seleccionada, st, coordenadas)
        else: mostrar_mensaje_panel("✈️ Selecciona una ruta para visualizar el mapa")

if __name__ == "__main__":
    main()