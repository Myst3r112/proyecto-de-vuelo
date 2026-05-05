'''
Para poder usar este programa debe instalar las librerias requeridas, ingrese este comando en la consola:
pip install -r requirements.txt

Una vez instalado los modulos, para ejecutar el programa solo coloque en consola:
streamlit run app.py

Recuerde utilizar el mismo interprete de Pyhon con el que se instalaron las librerias para evitar
errores de modulos no encontrados
'Ctrl + Shift + P' y seleccionar 'select interpreter' para verificar o corregir este error de modulo
'''
import numpy as np
import base64
import pandas as pd
import pydeck as pdk
from graphviz import Digraph

def cargar_imagen(ruta):
    with open(ruta, "rb") as archivo:
        data = archivo.read()
    return base64.b64encode(data).decode()

def cargar_datos_csv(ruta_csv, *, tipo_dato: str):
    df = pd.read_csv(ruta_csv)
    if tipo_dato == 'coordenadas':
        return {
            fila['pais']: (fila['longitud'], fila['latitud'])
            for _, fila in df.iterrows()
        }
    elif tipo_dato == 'conexiones':
        return [
            (fila["origen"], fila["destino"])
            for _, fila in df.iterrows()
        ]

coordenadas_paises = cargar_datos_csv("datos/coordenadas_paises.csv", tipo_dato='coordenadas')
conexiones = cargar_datos_csv("datos/conexiones.csv", tipo_dato='conexiones')

paises = [ i for i in coordenadas_paises.keys()]

def crear_matriz(dimension):
    matriz = np.zeros((dimension, dimension), dtype=int)

    for origen, destino  in conexiones:
        i = paises.index(origen)
        j = paises.index(destino)

        matriz[i][j] = 1

    return matriz

def validar_origen_destino(origen, destino):
    if origen == destino:
        return False, "No se puede usar el mismo pais como origen y destino"
    return True, ""

def agregar_ruta(matriz, origen, destino):
    valido, i = validar_origen_destino(origen, destino)
    if not valido: return False

    i = paises.index(origen)
    j = paises.index(destino)
    if matriz[i][j] == 1: return False

    matriz[i][j] = 1
    matriz[j][i] = 1
    return True



def producto_booleano(matriz_a, matriz_b):
    matriz_a = np.array(matriz_a, dtype=int)
    matriz_b = np.array(matriz_b, dtype=int)

    filas = matriz_a.shape[0]
    columnas = matriz_b.shape[1]
    intermedios = matriz_a.shape[1]

    resultado = np.zeros((filas, columnas), dtype=int)

    for i in range(filas):
        for j in range(columnas):
            for k in range(intermedios):
                if matriz_a[i][k] == 1 and matriz_b[k][j] == 1:
                    resultado[i][j] = 1
                    break
    return resultado

def calcular_conectividad(matriz):
    A = np.array(matriz, dtype=int).copy()
    np.fill_diagonal(A,0)
    A2 = producto_booleano(A, A)
    np.fill_diagonal(A2,0)
    A3 = producto_booleano(A2, A)
    np.fill_diagonal(A3,0)

    return A, A2 , A3

def analizar_conectividad_matricial(matriz, origen, destino):
    A, A2, A3 = calcular_conectividad(matriz)

    i = paises.index(origen)
    j = paises.index(destino)

    directa = A[i][j] == 1
    una_escala = A2[i][j] == 1
    dos_escalas = A3[i][j] == 1

    return {
        "A" : A,
        "A2" : A2,
        "A3" : A3,
        "directa" :directa,
        "una_escala" : una_escala,
        "dos_escalas" : dos_escalas,
        "hay_conectividad" : directa or una_escala or dos_escalas
    }   

def calcular_destinos(matriz, origen):
    i = paises.index(origen)
    destinos = list()
    
    for j, pais in enumerate(paises):
        if matriz[i][j] == 1:
            destinos.append(pais)
    
    return destinos




def rutas_directas(matriz, origen, destino):
    i = paises.index(origen)
    j = paises.index(destino)

    if matriz[i][j] == 1: return[[origen, destino]]
    return []

def rutas_una_escala(matriz, origen, destino):
    rutas = []
    i = paises.index(origen)
    j = paises.index(destino)

    for k, escala in enumerate(paises):
        if escala in (origen, destino): continue
        if matriz[i][k] == 1 and matriz[k][j] == 1:
            rutas.append([origen, escala, destino])
    
    return rutas
    
def rutas_dos_escalas(matriz, origen, destino):
    rutas = []
    i = paises.index(origen)
    j = paises.index(destino)

    for k, escala1 in enumerate(paises):
        for l, escala2 in enumerate(paises):
            if len({origen, escala1, escala2, destino}) != 4: continue
            if matriz[i][k] == 1 and matriz[k][l] == 1 and matriz[l][j] == 1:
                rutas.append([origen, escala1, escala2, destino])
    
    return rutas



def dibujar_grafo(ruta, contenedor):
    dot = Digraph()
    dot.attr(rankdir="TB")
    dot.attr(ranksep="0.6")
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
            color="#7A7A7A"
        )

    for i in range(len(ruta) - 1):
        dot.edge(f"n{i}", f"n{i + 1}")

    contenedor.graphviz_chart(dot)

def interpolar_color(t):
    r = int(46 + (217 - 46) * t)
    g = int(139 + (75 - 139) * t)
    b = int(87 + (75 - 87) * t)
    return [r, g, b]

def dibujar_mapa(ruta, contenedor, coordenadas):
    lineas = []
    puntos = []
    distancia = len(ruta)

    colores_nodos = []
    for i in range(distancia):
        t = 0 if distancia == 1 else i / (distancia - 1)
        colores_nodos.append(interpolar_color(t))
    
    for i, pais in enumerate(ruta):
        longitud, latitud = coordenadas[pais]
        puntos.append({
            "pais": pais,
            "longitud": longitud,
            "latitud": latitud,
            "color": colores_nodos[i]
        })

    for j in range(distancia - 1):
        origen = coordenadas[ruta[j]]
        destino = coordenadas[ruta[j + 1]]

        lineas.append({
            "from": origen,
            "to": destino,
            "source_color": colores_nodos[j],
            "target_color": colores_nodos[j + 1]
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
        get_position="[longitud, latitud]",
        get_fill_color="color",
        get_radius=100000,
        pickable=True,
    )

    latitudes = [coordenadas[pais][1] for pais in ruta]
    longitudes = [coordenadas[pais][0] for pais in ruta]

    vista = pdk.ViewState(
        latitude = sum(latitudes) / len(latitudes),
        longitude = sum(longitudes) / len(longitudes),
        zoom = 3
    )

    mapa = pdk.Deck(
        layers=[capa_lineas, capa_puntos],
        initial_view_state=vista,
        map_style="dark",
        tooltip={
            "html": "<b>{pais}</b>",
            "style": {"color": "white"}
        }\
    )

    contenedor.pydeck_chart(mapa, height=500)
    