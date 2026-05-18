from graphviz import Digraph
import pydeck as pdk
from utils import interpolar_color 
from data import *
def dibujar_grafo(ruta, contenedor):
    dot = Digraph()
    dot.attr(rankdir="TB")
    dot.attr(ranksep="0.8")
    dot.attr("edge", color="#7A7A7A", penwidth="1.8", arrowsize="0.7")

    for i, pais in enumerate(ruta):
        nombre_nodo = f"n{i}"
        if i == 0: color = "#2E8B57"
        elif i == len(ruta) - 1: color = "#D94B4B"
        else: color = "#4DA6FF"
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
            color="#7A7A7A"
        )
    for i in range(len(ruta) - 1): dot.edge(f"n{i}", f"n{i + 1}")
    contenedor.graphviz_chart(dot)

def construir_datos_digrafo_interno(digrafo):
    nodos = list(digrafo["nodos"].values())
    aristas, pares_procesados = list(), set()

    for (origen, destino), arista in digrafo["aristas"].items():
        if not arista["existe"]: continue
        par = frozenset([origen, destino])

        if par in pares_procesados: continue
        pares_procesados.add(par)
        arista_vuelta = digrafo["aristas"].get((destino, origen))
        existe_vuelta = arista_vuelta is not None and arista_vuelta["existe"]

        if existe_vuelta:
            tramo = f"{origen} → {destino}<br>{destino} → {origen}"
            tipo = "ida_vuelta"
        else:
            tramo = f"{origen} → {destino}"
            tipo = "ida"

        aristas.append({
            "from": arista["coordenada_origen"],
            "to": arista["coordenada_destino"],
            "origen": origen,
            "destino": destino,
            "tramo": tramo,
            "distancia": f"{arista['distancia']:.0f} km",
            "tipo": tipo,
            "color": [180, 180, 180]
        })

    return nodos, aristas

def construir_datos_ruta(ruta):
    nodos, aristas, colores_nodos = list(), list(), list()
    distancia = len(ruta)
    for i in range(distancia):
        t = 0 if distancia == 1 else i / (distancia - 1)
        colores_nodos.append(interpolar_color(t))

    for i, pais in enumerate(ruta):
        longitud, latitud = coordenadas_paises[pais]
        nodos.append({
            "pais": pais,
            "longitud": longitud,
            "latitud": latitud,
            "color": colores_nodos[i]
        })

    for j in range(distancia - 1):
        origen = coordenadas_paises[ruta[j]]
        destino = coordenadas_paises[ruta[j + 1]]

        aristas.append({
            "from": origen,
            "to": destino,
            "source_color": colores_nodos[j],
            "target_color": colores_nodos[j + 1]
        })
    
    return nodos, aristas

def dibujar_mapa(contenedor, *, ruta=None, digrafo=None):
    if digrafo is not None:
        nodos, aristas = construir_datos_digrafo_interno(digrafo)
        tooltip_html = "<b>{tramo}</b><br/>Distancia: {distancia}"
        radio_nodo=900
        nodo_pickable=False
        
        capa_lineas = pdk.Layer(
           "LineLayer",
           data=aristas,
           get_source_position="from",
           get_target_position="to",
           get_color="color",
           get_width=4,
           pickable=True
        )
    if ruta is not None:
        nodos, aristas = construir_datos_ruta(ruta)
        tooltip_html = "<b>{pais}</b>"
        radio_nodo=20000
        nodo_pickable=True
        
        capa_lineas = pdk.Layer(
            "ArcLayer",
            data=aristas,
            get_source_position="from",
            get_target_position="to",
            get_source_color="source_color",
            get_target_color="target_color",
            get_width=4,
            pickable=False
        )

    capa_puntos = pdk.Layer(
        "ScatterplotLayer",
        data=nodos,
        get_position="[longitud, latitud]",
        get_fill_color="color",
        get_radius=radio_nodo,
        pickable=nodo_pickable
    )
    latitudes = [nodo["latitud"] for nodo in nodos]
    longitudes = [nodo["longitud"] for nodo in nodos]

    vista = pdk.ViewState(
        latitude = sum(latitudes) / len(latitudes),
        longitude = sum(longitudes) / len(longitudes),
        zoom = 2
    )

    mapa = pdk.Deck(
        layers=[capa_lineas, capa_puntos],
        initial_view_state=vista,
        map_style="dark",
        tooltip={
            "html": tooltip_html,
            "style": {
                "color": "white"
            }
        }
    )
    contenedor.pydeck_chart(mapa, height=500)