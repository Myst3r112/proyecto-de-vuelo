import pandas as pd
import streamlit as st
from logica import *

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
            <h1 style="margin: 0; font-size: 32px;">
                🛩️ Aero Skibidis 🛩️
            </h1>
            <p style="margin: 8px 0 0 0; font-size: 16px;">
                Proyecto de Matemática Discreta: análisis de rutas mediante matrices de conectividad y grafos.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

def inicializar_estado():
    if "matriz" not in st.session_state: st.session_state.matriz = crear_matriz(len(paises))
    if "resultado_busqueda" not in st.session_state: st.session_state.resultado_busqueda = None
    if "ruta_seleccionada" not in st.session_state: st.session_state.ruta_seleccionada = None
    if "origen_busqueda" not in st.session_state: st.session_state.origen_busqueda = None
    if "destino_busqueda" not in st.session_state: st.session_state.destino_busqueda = None
    if "mensaje_agregar" not in st.session_state: st.session_state.mensaje_agregar = None

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
    for i, ruta in enumerate(rutas):
        texto = " → ".join(ruta)
        if st.button(texto, use_container_width=True, key=f"ruta_{titulo}_{i}_{texto}"):
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
        "Se encontraron ->"
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

def mostrar_recomendaciones(recomendaciones, digrafo_interno):
    if not recomendaciones:
        st.info("No se encontraron rutas disponibles para agregar con las opciones seleccionadas")
        return
    st.markdown("### Recomendaciones disponibles")

    columnas = st.columns(2)
    for i, recomendacion in enumerate(recomendaciones):
        ruta = recomendacion["ruta"]
        escala = recomendacion["escala"]
        distancia_total = recomendacion["distancia_total"]
        limite = recomendacion["limite"]

        with columnas[i % 2]:
            with st.container(border=True):
                st.markdown(f"**{escala}**")
                st.caption(f"Ruta: {' → '.join(ruta)}")
                st.caption(f"Distancia: {distancia_total:.0f} km / Límite: {limite:.0f} km")

                boton1, boton2 = st.columns(2)
                with boton1:
                    if st.button("Visualizar ruta", use_container_width=True, key=f"visualizar_{i}_{'_'.join(ruta)}"):
                        st.session_state.ruta_seleccionada = ruta
                        st.session_state.resultado_busqueda = None
                        st.rerun()

                with boton2:
                    if st.button("Agregar ruta", use_container_width=True, key=f"agregar_{i}_{'_'.join(ruta)}"):
                        agregado, mensaje = agregar_rutas_escalas(st.session_state.matriz, digrafo_interno, ruta)

                        st.session_state.mensaje_agregar = mensaje

                        if agregado:
                            st.session_state.ruta_seleccionada = ruta
                            st.session_state.resultado_busqueda = None
                        st.rerun()

def main():
    aplicar_estilos()
    mostrar_encabezado()
    inicializar_estado()

    digrafo_interno = construir_digrafo_interno(st.session_state.matriz)

    columna_main, columna_panel = st.columns([2.2, 1], gap="large")

    with columna_main:
        tabla1, tabla2, tabla3 = st.tabs([
            "🔎 Buscar rutas",
            "➕ Agregar ruta",
            "📶 Matriz de conectividad"
        ])

        with tabla1:
            st.subheader("Buscar rutas entre países")
            
            origen_actual = st.session_state.get("origen_busqueda")
            destino_actual = st.session_state.get("destino_busqueda")

            if destino_actual is not None: opciones_origen = calcular_origenes_destinos(st.session_state.matriz, sdestino=destino_actual)
            else: opciones_origen = paises
            
            if origen_actual is not None: opciones_destino = calcular_origenes_destinos(st.session_state.matriz, origen=origen_actual)
            else: opciones_destino = paises

            bloque1, bloque2 = st.columns(2)
            with bloque1:
                origen = st.selectbox(
                    "País de origen",
                    opciones_origen,
                    index=None,
                    placeholder="Ingrese un origen",
                    key="origen_busqueda"
                )
            with bloque2:
                destino = st.selectbox(
                    "País de destino",
                    opciones_destino,
                    index=None,
                    placeholder="Ingrese un destino",
                    key="destino_busqueda"
                )
            
            if st.button("Buscar rutas", use_container_width=True):
                valido, mensaje = validar_origen_destino(origen, destino)

                if not valido:
                    st.warning(mensaje)
                    limpiar_busqueda()
                else:
                    analisis = analizar_conectividad_matricial(st.session_state.matriz, origen, destino)
                    
                    st.session_state.resultado_busqueda = {
                        "analisis": analisis,
                        "directas": buscar_rutas(analisis["A"], origen, destino, stipo_ruta="directa"),
                        "una_escala": buscar_rutas(analisis["A"], origen, destino, tipo_ruta="una_escala"),
                        "dos_escalas": buscar_rutas(analisis["A"], origen, destino, tipo_ruta="dos_escalas")
                    }
                    st.session_state.ruta_seleccionada = None

            if st.session_state.resultado_busqueda: mostrar_resultados(st.session_state.resultado_busqueda)

        with tabla2:
            st.subheader("Agregar nueva ruta aérea con escala")

            if st.session_state.mensaje_agregar:
                st.info(st.session_state.mensaje_agregar)
                st.session_state.mensaje_agregar = None
            
            bloque1, bloque2 = st.columns(2)
            with bloque1:
                origen_nuevo = st.selectbox(
                    "Origen",
                    paises,
                    index=None,
                    placeholder="Ingrese un origen",
                    key="origen_nuevo"
                )

            with bloque2:
                destino_nuevo = st.selectbox(
                    "Destino",
                    paises,
                    index=None,
                    placeholder="Ingrese un destino",
                    key="destino_nuevo"
                )
            
            tipo_visual = st.radio(
                "Tipo de ruta que desea agregar",
                ["Con 1 escala", "Con 2 escalas"],
                horizontal=True
            )

            if tipo_visual == "Con 1 escala": tipo_ruta_agregar = "una_escala"
            if tipo_visual == "Con 2 escalas": tipo_ruta_agregar = "dos_escalas"

            valido, mensaje = validar_origen_destino(origen_nuevo, destino_nuevo)
            if not valido: st.warning(mensaje)
            else:
                recomendaciones = cargar_recomendaciones(digrafo_interno, origen_nuevo, destino_nuevo, tipo_ruta=tipo_ruta_agregar)
                mostrar_recomendaciones(recomendaciones, digrafo_interno)

        with tabla3:
            st.subheader("Matriz de conectividad de vuelos directos")

            df_matriz = pd.DataFrame(
                st.session_state.matriz,
                index=paises,
                columns=paises
            )

            st.dataframe(df_matriz, use_container_width=True)

            st.divider()
            st.subheader("Dígrafo dirigido interno del sistema (Por ahora se ve solo pa verificar aña)")

            dibujar_mapa_digrafo_interno(digrafo_interno, st)

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

        if st.session_state.ruta_seleccionada: dibujar_mapa(st.session_state.ruta_seleccionada, st, coordenadas_paises)
        else: mostrar_mensaje_panel("✈️ Selecciona una ruta para visualizar el mapa")


if __name__ == "__main__":
    main()