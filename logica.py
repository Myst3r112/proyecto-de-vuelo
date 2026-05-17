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
import math

### Funciones auxiliares para cargar datos e imagens, y hacer calculos ####
def cargar_imagen(ruta):
    with open(ruta, "rb") as archivo: data = archivo.read()
    return base64.b64encode(data).decode()

def cargar_datos_csv(ruta_csv, *, tipo_dato: str):
    df = pd.read_csv(ruta_csv)
    match tipo_dato:
        case "coordenadas":
            return {
                fila["pais"]: (fila["longitud"], fila["latitud"])
                for _, fila in df.iterrows()
            }
        case "conexiones":
            return [
                (fila["origen"], fila["destino"])
                for _, fila in df.iterrows()
            ]

def interpolar_color(t):
    r = int(46 + (217 - 46) * t)
    g = int(139 + (75 - 139) * t)
    b = int(87 + (75 - 87) * t)

    return [r, g, b]

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
                if matriz_a[i][k] and matriz_b[k][j]:
                    resultado[i][j] = 1
                    break

    return resultado

def formula_haversine(coordenada1, coordenada2):
    longitud1, latitud1 = coordenada1
    longitud2, latitud2 = coordenada2

    radio_tierra = 6371

    latitud1_rad = math.radians(latitud1)
    latitud2_rad = math.radians(latitud2)
    diferencia_latitud = math.radians(latitud2 - latitud1)
    diferencia_longitud = math.radians(longitud2 - longitud1)

    a = (
        math.sin(diferencia_latitud / 2) ** 2
        + math.cos(latitud1_rad) * math.cos(latitud2_rad)
        * math.sin(diferencia_longitud / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return radio_tierra * c

### Variables globales ####
coordenadas_paises = cargar_datos_csv("datos/coordenadas_paises.csv", tipo_dato="coordenadas")
conexiones = cargar_datos_csv("datos/conexiones.csv", tipo_dato="conexiones")
paises = [pais for pais in coordenadas_paises.keys()]
MARGEN_DESVIO = 0.03

### Funcones para contruir y analizar la matriz de conectividad ###
def crear_matriz(dimension) -> np.ndarray:
    matriz = np.zeros((dimension, dimension), dtype=int)

    for origen, destino in conexiones:
        if origen in paises and destino in paises:
            i, j = paises.index(origen), paises.index(destino)
            matriz[i][j] = 1

    return matriz

def validar_origen_destino(origen, destino):
    if origen is None and destino is None: return False, "Selecciona un pais de origen y destino"
    if origen is None: return False, "Selecciona un pais de origen"
    if destino is None: return False, "Selecciona un pais de destino"
    if origen == destino: return False, "No se puede usar el mismo pais como origen y destino"
    return True, ""

def validar_ruta(ruta):
    if len(ruta) != len(set(ruta)): return False, "La ruta no puede repetir paises"
    for pais in ruta:
        if pais not in paises: return False, f"El pais {pais} no existe en la lista"
    return True, ""

def calcular_conectividad(matriz):
    A = np.array(matriz, dtype=int).copy()
    np.fill_diagonal(A, 0)
    A2 = producto_booleano(A, A)
    np.fill_diagonal(A2, 0)
    A3 = producto_booleano(A2, A)
    np.fill_diagonal(A3, 0)
    return A, A2, A3

def analizar_conectividad_matricial(matriz, origen, destino):
    A, A2, A3 = calcular_conectividad(matriz)

    i = paises.index(origen)
    j = paises.index(destino)

    directa = A[i][j] == 1
    una_escala = A2[i][j] == 1
    dos_escalas = A3[i][j] == 1

    return {
        "A": A,
        "directa": directa,
        "una_escala": una_escala,
        "dos_escalas": dos_escalas,
        "hay_conectividad": directa or una_escala or dos_escalas
    }

### Buscar origenes y destinos con conexion
def buscar_rutas(matriz, origen, destino, *, tipo_ruta: str, digrafo=None) -> list:
    rutas = list()
    i, j = paises.index(origen), paises.index(destino)

    match tipo_ruta:
        case "directa":
            if matriz[i][j]:
                ruta = [origen, destino]

                if digrafo is None: rutas.append(ruta)
                else:
                    cumple_margen, _, _ = verificar_margen_desvio(digrafo, ruta)
                    if cumple_margen: rutas.append(ruta)
            pass
        case "una_escala":
            for k, escala1 in enumerate(paises):
                if escala1 in (origen, destino): continue
                if matriz[i][k] and matriz[k][j]:
                    ruta = [origen, escala1, destino]
                    if digrafo is None:rutas.append(ruta)
                    else:
                        cumple_margen, _, _ = verificar_margen_desvio(digrafo, ruta)
                        if cumple_margen: rutas.append(ruta)
            pass
        case "dos_escalas":
            for k, escala1 in enumerate(paises):
                for l, escala2 in enumerate(paises):
                    if len({origen, escala1, escala2, destino}) != 4: continue
                    if matriz[i][k] and matriz[k][l] and matriz[l][j]:
                        ruta = [origen, escala1, escala2, destino]
                        if digrafo is None: rutas.append(ruta)
                        else:
                            cumple_margen, _, _ = verificar_margen_desvio(digrafo, ruta)
                            if cumple_margen: rutas.append(ruta)
            pass
    return rutas

def calcular_origenes_destinos(matriz, *, origen=None, destino=None, digrafo=None) -> list:
    opciones = set()
    A, _, _ = calcular_conectividad(matriz)

    if origen is not None:
        for posible_destino in paises:
            if posible_destino == origen: continue

            rutas = buscar_rutas(A, origen, posible_destino, tipo_ruta="directa", digrafo=digrafo)
            if rutas:
                opciones.add(posible_destino)
                continue

            rutas = buscar_rutas(A, origen, posible_destino, tipo_ruta="una_escala", digrafo=digrafo)
            if rutas:
                opciones.add(posible_destino)
                continue

            rutas = buscar_rutas(A, origen, posible_destino, tipo_ruta="dos_escalas", digrafo=digrafo)
            if rutas:
                opciones.add(posible_destino)

    elif destino is not None:
        for posible_origen in paises:
            if posible_origen == destino: continue

            rutas = buscar_rutas(A, posible_origen, destino, tipo_ruta="directa", digrafo=digrafo)
            if rutas:
                opciones.add(posible_origen)
                continue

            rutas = buscar_rutas(A, posible_origen, destino, tipo_ruta="una_escala", digrafo=digrafo)
            if rutas:
                opciones.add(posible_origen)
                continue

            rutas = buscar_rutas(A, posible_origen, destino, tipo_ruta="dos_escalas", digrafo=digrafo)
            if rutas:
                opciones.add(posible_origen)

    else:
        return list(paises)

    return sorted(list(opciones))

### Funciones para construir y calcular el digrafo interno ###
def construir_digrafo_interno(matriz):
    digrafo = {
        "nodos": dict(),
        "aristas": dict()
    }

    for pais in paises:
        longitud, latitud = coordenadas_paises[pais]
        digrafo["nodos"][pais] = {
            "pais": pais,
            "longitud": longitud,
            "latitud": latitud,
            "color": [77, 77, 77]
        }

    for i, origen in enumerate(paises):
        for j, destino in enumerate(paises):
            if origen == destino: continue

            coordenada_origen = coordenadas_paises[origen]
            coordenada_destino = coordenadas_paises[destino]
            distancia = formula_haversine(coordenada_origen, coordenada_destino)
            digrafo["aristas"][(origen, destino)] = {
                "origen": origen,
                "destino": destino,
                "coordenada_origen": coordenada_origen,
                "coordenada_destino": coordenada_destino,
                "distancia": distancia,
                "existe": matriz[i][j] == 1
            }
    return digrafo

def calcular_distancia_ruta(digrafo, ruta):
    distancia_total = 0
    for i in range(len(ruta) - 1): distancia_total += digrafo["aristas"][(ruta[i], ruta[i + 1])]["distancia"]
    return distancia_total

def verificar_margen_desvio(digrafo, ruta, *, margen: float = MARGEN_DESVIO):
    origen, destino = ruta[0], ruta[-1]
    distancia_directa = digrafo["aristas"][(origen, destino)]["distancia"]
    distancia_total = calcular_distancia_ruta(digrafo, ruta)
    limite = distancia_directa * (1 + margen)
    return distancia_total <= limite, distancia_total, limite

### Funciones para agregar rutas ###
def recorrer_ruta_paises_pares(digrafo, ruta, *, funcion: str):
    nuevas = list()
    for i in range(len(ruta) - 1):
        origen = ruta[i]
        destino = ruta[i + 1]
        arista = digrafo["aristas"][(origen, destino)]
        if funcion == "verificar_existencia" and not arista["existe"]: return False
        if funcion == "agregar_conexiones" and not arista["existe"]: nuevas.append((origen, destino))

    if funcion == "verificar_existencia": return True
    if funcion == "agregar_conexiones": return nuevas

def cargar_recomendaciones(digrafo, origen, destino, *, tipo_ruta: str) -> list:
    recomendaciones = list()
    valido, _ = validar_origen_destino(origen, destino)
    if not valido: return recomendaciones
    for escala1 in paises:
        match tipo_ruta:
            case "una_escala":
                ruta = list([origen, escala1, destino])
                ruta_valida, _ = validar_ruta(ruta)

                if not ruta_valida: continue
                cumple_margen, distancia_total, limite = verificar_margen_desvio(digrafo, ruta)

                if not cumple_margen: continue
                if recorrer_ruta_paises_pares(digrafo, ruta, funcion="verificar_existencia"): continue
                nuevas = recorrer_ruta_paises_pares(digrafo, ruta, funcion="agregar_conexiones")

                if not nuevas: continue

                recomendaciones.append({
                    "escala": escala1,
                    "ruta": ruta,
                    "distancia_total": distancia_total,
                    "limite": limite,
                    "conexiones_nuevas": nuevas
                })
                if len(recomendaciones) == 10: break
            case "dos_escalas":
                for escala2 in paises:
                    ruta = list([origen, escala1, escala2, destino])
                    ruta_valida, _ = validar_ruta(ruta)
                    
                    if not ruta_valida: continue
                    cumple_margen, distancia_total, limite = verificar_margen_desvio(digrafo, ruta)

                    if not cumple_margen: continue
                    if recorrer_ruta_paises_pares(digrafo, ruta, funcion="verificar_existencia"): continue
                    nuevas = recorrer_ruta_paises_pares(digrafo, ruta, funcion="agregar_conexiones")

                    if not nuevas: continue
                    recomendaciones.append({
                        "escala": f"{escala1} -> {escala2}",
                        "ruta": ruta,
                        "distancia_total": distancia_total,
                        "limite": limite,
                        "conexiones_nuevas": nuevas
                    })
                    
                    if len(recomendaciones) == 10: break
    recomendaciones.sort(key=lambda x: x["distancia_total"])
    return recomendaciones

def agregar_rutas_escalas(matriz, digrafo, ruta):
    if len(ruta) not in (3, 4): return False, "La ruta debe tener una o dos escalas"
    valido, mensaje = validar_ruta(ruta)

    if not valido: return False, mensaje
    cumple_margen, _, _ = verificar_margen_desvio(digrafo, ruta)

    if not cumple_margen: return False, "La ruta no cumple con el margen de desvio permitido"
    if recorrer_ruta_paises_pares(digrafo, ruta, funcion="verificar_existencia"): return False, "La ruta ya existe en la matriz de conexiones"
    nuevas_conexiones = recorrer_ruta_paises_pares(digrafo, ruta, funcion="agregar_conexiones")

    for origen, destino in nuevas_conexiones:
        fila = paises.index(origen)
        columna = paises.index(destino)

        matriz[fila][columna] = 1
        digrafo["aristas"][(origen, destino)]["existe"] = True

    texto_ruta = " -> ".join(ruta)
    return True, f"Ruta agregada correctamente: {texto_ruta}"

### Funciones para visualizacion en graphviz ###
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

### Funciones para visualizacion en el mapa ###
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