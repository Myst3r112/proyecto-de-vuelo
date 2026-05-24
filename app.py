from datetime import datetime
import pandas as pd
import streamlit as st
from src.utils import cargar_imagen
from src.data import paises
from src.matriz import (
    crear_matriz, 
    calcular_origenes_destinos,
    analizar_conectividad_matricial
)
from src.digrafo import construir_digrafo_interno
from src.busqueda import (
    buscar_rutas,
    validar_origen_destino,
    cargar_recomendaciones,
    agregar_conexiones
    
)
from src.precios import (
    CLASES_TARIFA,
    calcular_comparacion_tarifas,
    calcular_precio_ruta,
    formatear_monto
)
from src.visualizacion import dibujar_mapa, dibujar_grafo
st.set_page_config(
    page_title='Terra Airline',
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
        div[data-testid="stDialog"] div[role="dialog"] {
            width: min(760px, calc(100vw - 32px));
        }
        div[data-testid="stHorizontalBlock"]:has(.encabezado-vuelos) {
            background-size: cover;
            background-position: center;
            padding: 28px;
            border-radius: 18px;
            color: white;
            margin-bottom: 18px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.25);
        }
        div[data-testid="stHorizontalBlock"]:has(.encabezado-vuelos) div[data-testid="stVerticalBlock"] {
            gap: 0.35rem;
        }
        div[data-testid="stHorizontalBlock"]:has(.encabezado-vuelos) .stButton {
            display: flex;
            justify-content: flex-end;
        }
        div[data-testid="stHorizontalBlock"]:has(.encabezado-vuelos) .stButton button {
            width: min(190px, 100%);
            border: 1px solid rgba(255,255,255,0.68);
            background: rgba(255,255,255,0.16);
            color: white;
            font-weight: 700;
            backdrop-filter: blur(6px);
        }
        div[data-testid="stHorizontalBlock"]:has(.encabezado-vuelos) .stCaptionContainer {
            color: rgba(255,255,255,0.88);
            text-align: right;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

def mostrar_encabezado():
    fondo = cargar_imagen("imagen/fondo.png")
    modo_actual = st.session_state.modo_app
    modo_siguiente = "Admin" if modo_actual == "Usuario" else "Usuario"

    st.markdown(
        f"""
        <style>
        div[data-testid="stHorizontalBlock"]:has(.encabezado-vuelos) {{
            background-image:
                linear-gradient(rgba(15,23,42,0.7), rgba(30,64,175,0.7)),
                url("data:image/png;base64,{fondo}");
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

    titulo, selector = st.columns([4, 1.25], vertical_alignment="center")

    with titulo:
        st.markdown(
            """
            <div class="encabezado-vuelos">
                <h1 style="margin: 0; font-size: 32px;">
                    🛩️ Aerolineas Terra 🛩️
                </h1>
                <p style="margin: 8px 0 0 0; font-size: 16px;">
                    Proyecto de Matemática Discreta: análisis de rutas mediante matrices de conectividad y grafos.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with selector:
        if st.button(f"Cambiar a {modo_siguiente}", use_container_width=True):
            st.session_state.modo_app = modo_siguiente
            limpiar_busqueda()
            st.rerun()
        st.caption(f"Modo actual: {modo_actual}")

def inicializar_estado():
    if "matriz" not in st.session_state: st.session_state.matriz = crear_matriz(len(paises))
    if "resultado_busqueda" not in st.session_state: st.session_state.resultado_busqueda = None
    if "ruta_seleccionada" not in st.session_state: st.session_state.ruta_seleccionada = None
    if "origen_busqueda" not in st.session_state: st.session_state.origen_busqueda = None
    if "destino_busqueda" not in st.session_state: st.session_state.destino_busqueda = None
    if "mensaje_agregar" not in st.session_state: st.session_state.mensaje_agregar = None
    if "digrafo_interno" not in st.session_state: st.session_state.digrafo_interno = construir_digrafo_interno(st.session_state.matriz)
    if "tarifa_confirmada" not in st.session_state: st.session_state.tarifa_confirmada = None
    if "modo_app" not in st.session_state: st.session_state.modo_app = "Usuario"
    if "historial_compras" not in st.session_state: st.session_state.historial_compras = list()

def limpiar_busqueda():
    st.session_state.resultado_busqueda = None
    st.session_state.ruta_seleccionada = None
    st.session_state.tarifa_confirmada = None

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

def registrar_compra(precio):
    compra = {
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "ruta": " → ".join(precio["ruta"]),
        "tipo_viaje": precio["tipo_viaje"],
        "clase": precio["clase"],
        "pasajeros": precio["pasajeros"],
        "subtotal_persona_usd": precio["subtotal_persona_usd"],
        "impuesto_persona_usd": precio["impuesto_persona_usd"],
        "tasa_aeropuerto_persona_usd": precio["tasa_aeropuerto_persona_usd"],
        "total_persona_usd": precio["total_persona_usd"],
        "total_usd": precio["total_usd"],
        "total_pen": precio["total_pen"],
    }

    st.session_state.historial_compras.append(compra)
    st.session_state.tarifa_confirmada = compra

def mostrar_historial_compras():
    st.subheader("Historial de compras")

    historial = st.session_state.historial_compras

    if not historial:
        st.info("Aún no hay compras registradas en esta sesión.")
        return

    total_usd = sum(compra["total_usd"] for compra in historial)
    total_pasajeros = sum(compra["pasajeros"] for compra in historial)

    dato1, dato2, dato3 = st.columns(3)

    with dato1:
        st.metric("Compras", len(historial))
    with dato2:
        st.metric("Pasajeros", total_pasajeros)
    with dato3:
        st.metric("Total comprado", formatear_monto(total_usd, "USD"))

    filas = []

    for compra in reversed(historial):
        filas.append({
            "Fecha": compra["fecha"],
            "Ruta": compra["ruta"],
            "Viaje": compra["tipo_viaje"],
            "Clase": compra["clase"],
            "Pasajeros": compra["pasajeros"],
            "Por pasajero": formatear_monto(compra["total_persona_usd"], "USD"),
            "Total USD": formatear_monto(compra["total_usd"], "USD"),
            "Total PEN": formatear_monto(compra["total_pen"], "PEN"),
        })

    st.dataframe(pd.DataFrame(filas), use_container_width=True, hide_index=True)

    with st.expander("Ver desglose de tasas por pasajero"):
        detalle = []

        for compra in reversed(historial):
            detalle.append({
                "Fecha": compra["fecha"],
                "Ruta": compra["ruta"],
                "Subtotal": formatear_monto(compra["subtotal_persona_usd"], "USD"),
                "Impuesto 18%": formatear_monto(compra["impuesto_persona_usd"], "USD"),
                "Tasa aeropuerto fija": formatear_monto(compra["tasa_aeropuerto_persona_usd"], "USD"),
                "Total por pasajero": formatear_monto(compra["total_persona_usd"], "USD"),
            })

        st.dataframe(pd.DataFrame(detalle), use_container_width=True, hide_index=True)

    if st.button("Vaciar historial", use_container_width=True):
        st.session_state.historial_compras = list()
        st.session_state.tarifa_confirmada = None
        st.rerun()

def mostrar_tarjetas_rutas(titulo, rutas, digrafo_interno):
    if not rutas: return
    st.markdown(titulo)

    for i, ruta in enumerate(rutas):
        texto = " → ".join(ruta)
        precio_desde = calcular_precio_ruta(
            digrafo_interno,
            ruta,
            tipo_viaje="Solo ida",
            clase="Standard",
            pasajeros=1,
        )

        with st.container(border=True):
            boton_visualizar, boton_elegir, detalle_ruta = st.columns([1, 1, 3.2], vertical_alignment="center")

            with boton_visualizar:
                if st.button("Visualizar ruta", use_container_width=True, key=f"visualizar_busqueda_{titulo}_{i}"):
                    st.session_state.ruta_seleccionada = ruta

            with boton_elegir:
                if st.button("Elegir ruta", use_container_width=True, key=f"elegir_busqueda_{titulo}_{i}"):
                    st.session_state.ruta_seleccionada = ruta
                    mostrar_contenido_cotizacion(ruta, digrafo_interno)

            with detalle_ruta:
                st.markdown(f"**{texto}**")
                st.caption(
                    f"{len(ruta) - 1} tramo(s) | "
                    f"{precio_desde['distancia_total']:.0f} km | "
                    f"desde {formatear_monto(precio_desde['total_usd'], 'USD')}"
                )

def mostrar_resultados(resultado, digrafo_interno):
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

    mostrar_tarjetas_rutas("### ✈️ Rutas directas", resultado["directas"], digrafo_interno)
    mostrar_tarjetas_rutas("### 🛫 Rutas con 1 escala", resultado["una_escala"], digrafo_interno)
    mostrar_tarjetas_rutas("### 🛬 Rutas con 2 escalas", resultado["dos_escalas"], digrafo_interno)

    if not (resultado["directas"] or resultado["una_escala"] or resultado["dos_escalas"]): 
        st.info("La matriz detectó conectividad, pero no se encontraron rutas válidas sin repetir países.")

@st.dialog("Elegir ruta y tarifa")
def mostrar_contenido_cotizacion(ruta, digrafo_interno):
    texto_ruta = " → ".join(ruta)
    st.markdown(f"**Ruta seleccionada:** {texto_ruta}")

    tipo_viaje, pasajeros = st.columns([1.4, 1], vertical_alignment="bottom")

    with tipo_viaje:
        seleccion_viaje = st.radio(
            "Tipo de viaje",
            ["Solo ida", "Ida y vuelta"],
            horizontal=True,
            key="cotizacion_tipo_viaje"
        )

    with pasajeros:
        cantidad_pasajeros = st.number_input(
            "Pasajeros",
            min_value=1,
            max_value=9,
            value=1,
            step=1,
            key="cotizacion_pasajeros"
        )

    clase = st.radio(
        "Clase",
        list(CLASES_TARIFA.keys()),
        horizontal=True,
        key="cotizacion_clase"
    )

    precio = calcular_precio_ruta(
        digrafo_interno,
        ruta,
        tipo_viaje=seleccion_viaje,
        clase=clase,
        pasajeros=cantidad_pasajeros,
    )

    total, por_persona, distancia = st.columns(3)

    with total:
        st.metric("Total", formatear_monto(precio["total_usd"], "USD"))
        st.caption(formatear_monto(precio["total_pen"], "PEN"))

    with por_persona:
        st.metric("Por pasajero", formatear_monto(precio["total_persona_usd"], "USD"))
        st.caption(
            f"Impuesto 18%: {formatear_monto(precio['impuesto_persona_usd'], 'USD')} | "
            f"Tasa fija: {formatear_monto(precio['tasa_aeropuerto_persona_usd'], 'USD')}"
        )

    with distancia:
        st.metric("Distancia", f"{precio['distancia_total']:.0f} km")
        st.caption(f"{precio['segmentos']} tramo(s), {precio['escalas']} escala(s)")

    st.table(
        pd.DataFrame(calcular_comparacion_tarifas(
            digrafo_interno,
            ruta,
            tipo_viaje=seleccion_viaje,
            pasajeros=cantidad_pasajeros,
        ))
    )

    confirmar, cerrar = st.columns(2)
    with confirmar:
        if st.button("Comprar boleto", use_container_width=True):
            registrar_compra(precio)
            st.rerun()

    with cerrar:
        if st.button("Cerrar", use_container_width=True):
            st.rerun()

def mostrar_recomendaciones(recomendaciones, digrafo_interno):
    if not recomendaciones:
        st.info("No se encontraron rutas disponibles para agregar con las opciones seleccionadas")
        return

    st.markdown("### Recomendaciones disponibles")

    columnas = st.columns(2)

    for i, recomendacion in enumerate(recomendaciones):
        ruta = recomendacion["ruta"]
        mostrar = recomendacion["mostrar"]
        distancia_total = recomendacion["distancia_total"]
        limite = recomendacion["limite"]

        with columnas[i % 2]:
            with st.container(border=True):
                st.markdown(f"**{mostrar}**")
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
                        agregado, mensaje = agregar_conexiones(st.session_state.matriz, digrafo_interno, ruta)

                        st.session_state.mensaje_agregar = mensaje

                        if agregado:
                            st.session_state.ruta_seleccionada = ruta
                            st.session_state.resultado_busqueda = None

                        st.rerun()

def main(): 
    aplicar_estilos()
    inicializar_estado()
    mostrar_encabezado()
    digrafo_interno = st.session_state.digrafo_interno
    es_admin = st.session_state.modo_app == "Admin"
    
    columna_main, columna_panel = st.columns([2.2, 1], gap="large")
    with columna_main:
        if es_admin:
            tabla1, tabla2= st.tabs([
                "➕ Agregar ruta",
                "📶 Matriz de conectividad"
            ])
        else:
            tabla1, tabla2 = st.tabs(["🔎 Buscar rutas", "🧾 Historial"])
        
        if not es_admin:
            with tabla1:
                st.subheader("Buscar rutas entre países")
    
                origen_actual = st.session_state.get("origen_busqueda")
                destino_actual = st.session_state.get("destino_busqueda")
    
                if destino_actual is not None: 
                    opciones_origen = calcular_origenes_destinos(
                        st.session_state.matriz, 
                        destino=destino_actual,
                        digrafo=digrafo_interno
                        )
                else: opciones_origen = paises
    
                if origen_actual is not None: 
                    opciones_destino = calcular_origenes_destinos(
                        st.session_state.matriz, 
                        origen=origen_actual,
                        digrafo=digrafo_interno
                        )
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
                            "directas": buscar_rutas(
                                analisis["A"],
                                origen,
                                destino,
                                tipo_ruta="directa",
                                digrafo=digrafo_interno
                            ),
                            "una_escala": buscar_rutas(
                                analisis["A"],
                                origen,
                                destino,
                                tipo_ruta="una_escala",
                                digrafo=digrafo_interno
                            ),
                            "dos_escalas": buscar_rutas(
                                analisis["A"],
                                origen,
                                destino,
                                tipo_ruta="dos_escalas",
                                digrafo=digrafo_interno
                            )
                        }
                        st.session_state.ruta_seleccionada = None
                        st.session_state.tarifa_confirmada = None
    
                if st.session_state.tarifa_confirmada:
                    tarifa = st.session_state.tarifa_confirmada
                    st.success(
                        "Compra registrada: "
                        f"{tarifa['ruta']} | "
                        f"{tarifa['tipo_viaje']} | "
                        f"{tarifa['clase']} | "
                        f"{tarifa['pasajeros']} pasajero(s) | "
                        f"{formatear_monto(tarifa['total_usd'], 'USD')}"
                    )
    
                if st.session_state.resultado_busqueda: mostrar_resultados(st.session_state.resultado_busqueda, digrafo_interno)

            with tabla2:
                mostrar_historial_compras()

        if es_admin:
            with tabla1:
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
                    ["Directa", "Con 1 escala", "Con 2 escalas"],
                    horizontal=True
                )

                if tipo_visual == "Directa": tipo_ruta_agregar = "directa"
                if tipo_visual == "Con 1 escala": tipo_ruta_agregar = "una_escala"
                if tipo_visual == "Con 2 escalas": tipo_ruta_agregar = "dos_escalas"

                valido, mensaje = validar_origen_destino(origen_nuevo, destino_nuevo)

                if not valido:
                    st.warning(mensaje)
                else:
                    recomendaciones = cargar_recomendaciones(digrafo_interno, origen_nuevo, destino_nuevo, tipo_ruta=tipo_ruta_agregar)
                    mostrar_recomendaciones(recomendaciones, digrafo_interno)

            with tabla2:
                st.subheader("Matriz de conectividad de vuelos")

                df_matriz = pd.DataFrame(
                    st.session_state.matriz,
                    index=paises,
                    columns=paises
                )

                st.dataframe(df_matriz, use_container_width=True)
                
                st.divider()
                st.subheader("Mapa con digrafo dirigido")
                dibujar_mapa(st, digrafo=st.session_state.digrafo_interno)

    with columna_panel:
        st.subheader("🧭 Visualización de la ruta")
        st.caption("🟢 Origen   🔵 Escala   🔴 Destino")

        if st.session_state.ruta_seleccionada:
            st.markdown(f"**Ruta seleccionada:** {' → '.join(st.session_state.ruta_seleccionada)}")

            _, centro, _ = st.columns(3)

            with centro:
                dibujar_grafo(st.session_state.ruta_seleccionada, st)
        else:
            mostrar_mensaje_panel("✈️ Selecciona una ruta para visualizar el grafo")

        st.divider()
        st.subheader("🌍 Mapa interactivo")

        if st.session_state.ruta_seleccionada: dibujar_mapa(st, ruta=st.session_state.ruta_seleccionada)
        else: mostrar_mensaje_panel("✈️ Selecciona una ruta para visualizar el mapa")

if __name__ == "__main__":
    main()
