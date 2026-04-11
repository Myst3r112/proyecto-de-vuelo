import numpy as np
import random
import base64
import pandas as pd
import pydeck as pdk
from graphviz import Digraph

paises = [
    "Perú", "Chile", "Argentina", "Brasil",
    "Colombia", "México", "Ecuador", "Bolivia",
    "Paraguay", "Uruguay", "Panamá", "Costa Rica"
]

indice_paises = {pais: idx for idx, pais in enumerate(paises)}

def validar_origen_destino(origen, destino):
    if origen == destino:
        return False, "No se puede usar el mismo país"
    elif origen not in indice_paises:
        return False, "Origen no válido"
    elif destino not in indice_paises:
        return False, "Destino no válido"
    return True, ""
    
def agregar_ruta(matriz, origen, destino):
    valido, _ = validar_origen_destino(origen, destino)
    if not valido:
        return False

    i = indice_paises[origen]
    j = indice_paises[destino]

    if matriz[i][j] == 1:
        return False

    matriz[i][j] = 1
    matriz[j][i] = 1
    return True

def generar_matriz_aleatoria(n, probabilidad=0.25):
    m = np.zeros((n, n), dtype=int)

    for i in range(n):
        for j in range(i + 1, n):
            if random.random() <= probabilidad:
                m[i][j] = 1
                m[j][i] = 1

    return m

def calcular_conectividad(matriz):
    A = matriz
    A2 = np.dot(A, A)
    A3 = np.dot(A2, A)
    
    return A, A2, A3

def hay_conexion(matriz_k, origen, destino):
    valido, _ = validar_origen_destino(origen, destino)
    if not valido:
        return False

    i = indice_paises[origen]
    j = indice_paises[destino]
    return matriz_k[i][j] > 0

def rutas_directas(A, origen, destino):
    if hay_conexion(A, origen, destino):
        return [[origen, destino]]
    return []

def rutas_una_escala(A, origen, destino):
    rutas = []
    i = indice_paises[origen]
    j = indice_paises[destino]

    for k in range(len(paises)):
        escala = paises[k]

        if escala != origen and escala != destino:
            if A[i][k] > 0 and A[k][j] > 0:
                rutas.append([origen, escala, destino])

    return rutas

def rutas_dos_escalas(A, origen, destino):
    rutas = []
    i = indice_paises[origen]
    j = indice_paises[destino]

    for k in range(len(paises)):
        for l in range(len(paises)):

            escala1 = paises[k]
            escala2 = paises[l]

            if len({origen, escala1, escala2, destino}) < 4:
                continue

            if A[i][k] > 0 and A[k][l] > 0 and A[l][j] > 0:
                rutas.append([origen, escala1, escala2, destino])

    return rutas

def dibujar_grafo(ruta, contenedor):
    dot = Digraph()

    dot.attr(rankdir="TB")

    dot.attr(ranksep="0.6")
    dot.attr(nodesep="0.4")

    dot.attr("edge", color="#7A7A7A", penwidth="1.8", arrowsize="0.5")

    for i, pais in enumerate(ruta):
        nombre_nodo = f"n{i}"

        if i == 0:
            color = "#2E8B57"
        elif i == len(ruta) - 1:
            color = "#D94B4B"
        else:
            color = "#4DA6FF"

        dot.node(
            nombre_nodo,
            label="",
            xlabel=pais,
            shape="circle",
            width="0.35",
            height="0.35",
            fixedsize="true",
            style="filled",
            fillcolor=color,
            color=color,
            fontname="Helvetica"
        )

    for i in range(len(ruta) - 1):
        dot.edge(f"n{i}", f"n{i+1}")

    contenedor.graphviz_chart(dot)

def cargar_imagen(ruta):
    with open(ruta, "rb") as f:
        data = f.read()
        return base64.b64encode(data).decode()
    
def cargar_coordenadas(ruta_csv):
    df = pd.read_csv(ruta_csv)

    return {
        fila["pais"]: (fila["longitud"], fila["latitud"])
        for _, fila in df.iterrows()
    }
 
def interpolar_color(t):
    """
    t va de 0 a 1
    0 = verde, 1 = rojo
    """
    r = int(46 + (217 - 46) * t)
    g = int(139 + (75 - 139) * t)
    b = int(87 + (75 - 87) * t)
    return [r, g, b]

def dibujar_mapa(ruta, contenedor, coordenadas):
    lineas = []
    puntos = []

    n = len(ruta)

    colores_nodos = []
    if n == 1:
        colores_nodos = [[46, 139, 87]]
    else:
        for i in range(n):
            t = i / (n - 1)
            colores_nodos.append(interpolar_color(t))

    # Puntos del mapa
    for i, pais in enumerate(ruta):
        lon, lat = coordenadas[pais]
        puntos.append({
            "pais": pais,
            "lon": lon,
            "lat": lat,
            "color": colores_nodos[i]
        })

    # Tramos con degradado continuo por segmentos
    for i in range(n - 1):
        origen = coordenadas[ruta[i]]
        destino = coordenadas[ruta[i + 1]]

        lineas.append({
            "from": origen,
            "to": destino,
            "source_color": colores_nodos[i],
            "target_color": colores_nodos[i + 1]
        })

    capa_lineas = pdk.Layer(
        "ArcLayer",
        data=lineas,
        get_source_position="from",
        get_target_position="to",
        get_source_color="source_color",
        get_target_color="target_color",
        get_width=4,
    )

    capa_puntos = pdk.Layer(
        "ScatterplotLayer",
        data=puntos,
        get_position='[lon, lat]',
        get_fill_color='color',
        get_radius=100000,
        pickable=True,
    )

    lats = [coordenadas[p][1] for p in ruta]
    lons = [coordenadas[p][0] for p in ruta]

    lat_centro = sum(lats) / len(lats)
    lon_centro = sum(lons) / len(lons)

    vista = pdk.ViewState(
        latitude=lat_centro,
        longitude=lon_centro,
        zoom=4
    )

    mapa = pdk.Deck(
        layers=[capa_lineas, capa_puntos],
        initial_view_state=vista,
        map_style="light",
        tooltip={
        "html": "<b>{pais}</b>",
        "style": {"color": "white"}
}
    )

    contenedor.pydeck_chart(mapa, height=400)