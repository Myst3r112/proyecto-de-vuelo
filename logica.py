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
paises = [pais for pais in coordenadas_paises.keys()]

def crear_matriz(dimension) -> np.ndarray:
    matriz = np.zeros((dimension, dimension), dtype=int)

    for origen, destino in conexiones:
        i = paises.index(origen)
        j = paises.index(destino)
        matriz[i][j] = 1

    return matriz

def validar_origen_destino(origen, destino):
    if origen is None and destino is None: return False, "Selecciona un pais de origen y destino"
    if origen == destino: return False, "No se puede usar el mismo pais como origen y destino"
    if origen is None: return False, "Selecciona un país de origen"
    if destino is None: return False, "Selecciona un pais de destino"
    return True, ""

def validar_ruta(ruta):
    if len(ruta) != len(set(ruta)): return False, "La ruta no puede repetir paises"
    
    for pais in ruta:
        if pais not in paises: return False, f"El país {pais} no existe en la lista"

    return True, ""





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
        "directa" :directa,
        "una_escala" : una_escala,
        "dos_escalas" : dos_escalas,
        "hay_conectividad" : directa or una_escala or dos_escalas
    }   

def calcular_origenes_destinos(matriz, *, origen=None, destino=None) -> list:
    opciones = list()
    
    for _, pais in enumerate(paises):
        if pais == origen: continue

        if origen is not None: buscar_conexion = analizar_conectividad_matricial(matriz, origen, pais)
        if destino is not None: buscar_conexion = analizar_conectividad_matricial(matriz, pais, destino)

        if buscar_conexion["hay_conectividad"]: opciones.append(pais)
    
    return opciones

def buscar_rutas(matriz, origen, destino, *, tipo_ruta: str) -> list:
    rutas = []
    i = paises.index(origen)
    j = paises.index(destino)
    if tipo_ruta == "directa":
        if matriz[i][j]: rutas.append([origen, destino])
    else:
        for k, escala1 in enumerate(paises):
            if tipo_ruta == "una_escala":
                if escala1 in (origen, destino): continue
                if matriz[i][k] and matriz[k][j]: rutas.append([origen, escala1, destino])
            if tipo_ruta == "dos_escalas":
                for l, escala2 in enumerate(paises):
                    if len({origen, escala1, escala2, destino}) != 4: continue
                    if matriz[i][k] and matriz[k][l] and matriz[l][j]: rutas.append([origen, escala1, escala2, destino])
    
    return rutas

def formula_haversine(coordenada1, coordenada2):
    longitud1, latitud1 = coordenada1
    longitud2, latitud2 = coordenada2

    ratio_tierra  = 6371

    latitud1_rad = math.radians(latitud1)
    latitud2_rad = math.radians(latitud2)
    diferencia_latitud = math.radians(latitud2 - latitud1)
    diferencia_longitud = math.radians(longitud2 - longitud1)

    a = (
        math.sin(diferencia_latitud / 2) ** 2
        + math.cos(latitud1_rad) * math.cos(latitud2_rad) 
        * math.sin(diferencia_longitud / 2) ** 2
    )

    c = (
        2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    )

    return ratio_tierra * c

def distancia_entre_paises(pais1, pais2):
    coordenadas1 = coordenadas_paises[pais1]
    coordenadas2 = coordenadas_paises[pais2]

    return formula_haversine(coordenadas1, coordenadas2)

def distancia_ruta(ruta):
    distancia_total = 0
    for i in range(len(ruta) - 1):
        distancia_total += distancia_entre_paises(ruta[i], ruta[i + 1])
    return distancia_total

def verificar_margen_desvio(ruta, *, margen: float = 0.03):
    origen, destino = ruta[0], ruta[-1]

    distancia_directa = distancia_entre_paises(origen, destino)
    distancia_total = distancia_ruta(ruta)

    limite = distancia_directa * (1 + margen)

    return distancia_total <= limite, distancia_total, limite

def verificar_existencia_ruta(matriz, ruta):
    for i in range(len(ruta) - 1):
        origen, destino = ruta[i], ruta[i + 1]

        fila = paises.index(origen)
        columna = paises.index(destino)
        
        if matriz[fila][columna] == 0: return False
    return True

def conexiones_para_agregar(matriz, ruta):
    nuevas = list()

    for i in range(len(ruta) - 1):
        origen, destino = ruta[i], ruta[i + 1]

        fila = paises.index(origen)
        columna = paises.index(destino)

        if matriz[fila][columna] == 0: nuevas.append((origen, destino))
        
    return nuevas

def cargar_recomendaciones(matriz, origen, destino, *, tipo_ruta: str) -> list:    
    recomendaciones = list()
    valido, _ = validar_origen_destino(origen, destino)
    if not valido: return recomendaciones

    for escala1 in paises:
        if tipo_ruta == "una_escala":
            ruta = [origen, escala1, destino]
            ruta_valida, _ = validar_ruta(ruta)
            if not ruta_valida: continue

            cumple_margen, distancia_total, limite = verificar_margen_desvio(ruta)
            if not cumple_margen: continue
            if verificar_existencia_ruta(matriz, ruta): continue

            nuevas = conexiones_para_agregar(matriz, ruta)
            if not nuevas: continue

            recomendaciones.append({
                "escala": escala1,
                "ruta": ruta,
                "distancia_total": distancia_total,
                "limite": limite,
                "conexiones_nuevas": nuevas
            })
        if tipo_ruta == "dos_escalas":
            for escala2 in paises:
                ruta = [origen, escala1, escala2, destino]
                ruta_valida, _ = validar_ruta(ruta)
                if not ruta_valida: continue

                cumple_margen, distancia_total, limite = verificar_margen_desvio(ruta)
                if not cumple_margen: continue
                if verificar_existencia_ruta(matriz, ruta): continue
                nuevas = conexiones_para_agregar(matriz, ruta)
                if not nuevas: continue
                recomendaciones.append({
                    "escala": f"{escala1} -> {escala2}",
                    "ruta": ruta,
                    "distancia_total": distancia_total,
                    "limite": limite,
                    "conexiones_nuevas": nuevas
                })

    recomendaciones.sort(key=lambda x: x["distancia_total"])
    return recomendaciones                

def agregar_rutas_escalas(matriz, ruta):
    if len(ruta) not in (3, 4): return False, "La ruta debe tener una o dos escalas"
    valido, mensaje = validar_ruta(ruta)
    if not valido: return False, mensaje
    cumple_margen, _, _ = verificar_margen_desvio(ruta)
    if not cumple_margen: return False, "La ruta no cumple con el margen de desvio permitido"
    if verificar_existencia_ruta(matriz, ruta): return False, "La ruta ya existe en la matriz de conexiones"
    nuevas_conexiones = conexiones_para_agregar(matriz, ruta)
    for origen, destino in nuevas_conexiones:
        fila = paises.index(origen)
        columna = paises.index(destino)

        matriz[fila][columna] = 1
    
    texto_ruta = " -> ".join(ruta)

    return True, f"Ruta agregada correctamente: {texto_ruta}"







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

def interpolar_color(t):
    r = int(46 + (217 - 46) * t)
    g = int(139 + (75 - 139) * t)
    b = int(87 + (75 - 87) * t)
    return [r, g, b]

def calcular_angulo_flecha(coordenada_origen, coordenada_destino):
    longitud1, latitud1 = coordenada_origen
    longitud2, latitud2 = coordenada_destino

    angulo = math.degrees(math.atan2(latitud2 - latitud1, longitud2 - longitud1))
    return angulo

def calcular_punto_intermedio(coordenada_origen, coordenada_destino, proporcion):
    longitud1, latitud1 = coordenada_origen
    longitud2, latitud2 = coordenada_destino

    longitud = longitud1 + (longitud2 - longitud1) * proporcion
    latitud = latitud1 + (latitud2 - latitud1) * proporcion

    return longitud, latitud

def construir_digrafo_georeferenciado(matriz, coordenadas):
    nodos = []
    aristas = []
    flechas = []

    for pais in paises:
        longitud, latitud = coordenadas[pais]

        nodos.append({
            "pais": pais,
            "longitud": longitud,
            "latitud": latitud,
            "color": [77, 77, 77]
        })

    pares_procesados = set()

    for i, origen in enumerate(paises):
        for j, destino in enumerate(paises):
            if i == j: continue
            if matriz[i][j] == 0: continue

            par = frozenset([origen, destino])
            if par in pares_procesados: continue

            pares_procesados.add(par)

            existe_ida = matriz[i][j] == 1
            existe_vuelta = matriz[j][i] == 1

            coordenada_origen = coordenadas[origen]
            coordenada_destino = coordenadas[destino]

            distancia = distancia_entre_paises(origen, destino)

            if existe_ida and existe_vuelta:
                tramo = f"{origen} → {destino}<br>{destino} → {origen}"
                tipo = "ida_vuelta"
            else:
                tramo = f"{origen} → {destino}"
                tipo = "ida"

            aristas.append({
                "from": coordenada_origen,
                "to": coordenada_destino,
                "origen": origen,
                "destino": destino,
                "tramo": tramo,
                "distancia": f"{distancia:.0f} km",
                "tipo": tipo,
                "color": [180, 180, 180]
            })

            if existe_ida:
                longitud_flecha, latitud_flecha = calcular_punto_intermedio(
                    coordenada_origen,
                    coordenada_destino,
                    0.65
                )

                flechas.append({
                    "flecha": "➤",
                    "longitud": longitud_flecha,
                    "latitud": latitud_flecha,
                    "angulo": calcular_angulo_flecha(coordenada_origen, coordenada_destino),
                    "color": [255, 255, 255],
                    "tramo": f"{origen} → {destino}",
                    "distancia": f"{distancia:.0f} km"
                })

            if existe_vuelta:
                longitud_flecha, latitud_flecha = calcular_punto_intermedio(
                    coordenada_destino,
                    coordenada_origen,
                    0.65
                )

                flechas.append({
                    "flecha": "➤",
                    "longitud": longitud_flecha,
                    "latitud": latitud_flecha,
                    "angulo": calcular_angulo_flecha(coordenada_destino, coordenada_origen),
                    "color": [255, 255, 255],
                    "tramo": f"{destino} → {origen}",
                    "distancia": f"{distancia:.0f} km"
                })

    return nodos, aristas, flechas

def dibujar_mapa_digrafo_interno(matriz, contenedor, coordenadas):
    nodos, aristas, flechas = construir_digrafo_georeferenciado(matriz, coordenadas)

    capa_aristas = pdk.Layer(
        "LineLayer",
        data=aristas,
        get_source_position="from",
        get_target_position="to",
        get_color="color",
        get_width=3,
        pickable=True
    )
    capa_nodos = pdk.Layer(
        "ScatterplotLayer",
        data=nodos,
        get_position="[longitud, latitud]",
        get_fill_color="color",
        get_radius=900,
        pickable=False
    )
    capa_flechas = pdk.Layer(
        "TextLayer",
        data=flechas,
        get_position="[longitud, latitud]",
        get_text="flecha",
        get_color="color",
        get_size=24,
        get_angle="angulo",
        get_text_anchor='"middle"',
        get_alignment_baseline='"center"',
        pickable=True
    )
    capa_nombres = pdk.Layer(
        "TextLayer",
        data=nodos,
        get_position="[longitud, latitud]",
        get_text="pais",
        get_color=[255, 255, 255],
        get_size=18,
        get_pixel_offset=[0, -22],
        get_text_anchor='"middle"',
        get_alignment_baseline='"center"',
        pickable=False
    )
    capas = [
        capa_aristas,
        capa_nodos,
        capa_flechas,
        capa_nombres
    ]

    latitudes = [coordenadas[pais][1] for pais in paises]
    longitudes = [coordenadas[pais][0] for pais in paises]

    vista = pdk.ViewState(
        latitude=sum(latitudes) / len(latitudes),
        longitude=sum(longitudes) / len(longitudes),
        zoom=2.4
    )
    mapa = pdk.Deck(
        layers=capas,
        initial_view_state=vista,
        map_style="dark",
        tooltip={
            "html": """
                <b>{tramo}</b><br/>
                Distancia: {distancia}
            """,
            "style": {
                "color": "white"
            }
        }
    )

    contenedor.pydeck_chart(mapa, height=550)

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
        }
    )

    contenedor.pydeck_chart(mapa, height=500)
