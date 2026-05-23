from data import * 
from utils import formula_haversine

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
                "existe": bool(matriz[i][j] == 1)
            }
    return digrafo

def calcular_distancia_ruta(digrafo, ruta):
    distancia_total = 0
    for i in range(len(ruta) - 1): 
        distancia_total += digrafo["aristas"][(ruta[i], ruta[i + 1])]["distancia"]
    return distancia_total

def verificar_margen_desvio(digrafo, ruta, *, margen: float = MARGEN_DESVIO):
    origen, destino = ruta[0], ruta[-1]
    distancia_directa = digrafo["aristas"][(origen, destino)]["distancia"]
    distancia_total = calcular_distancia_ruta(digrafo, ruta)
    limite = distancia_directa * (1 + margen)

    if distancia_total > limite:
        return False, distancia_total, limite

    for i in range(len(ruta) - 1):
        actual = ruta[i]
        siguiente = ruta[i + 1]

        distancia_actual_destino = digrafo["aristas"][(actual, destino)]["distancia"]
        distancia_siguiente_destino = 0 if siguiente == destino else digrafo["aristas"][(siguiente, destino)]["distancia"]

        if distancia_siguiente_destino >= distancia_actual_destino:
            return False, distancia_total, limite

    for escala in ruta[1:-1]:
        distancia_con_escala = (
            digrafo["aristas"][(origen, escala)]["distancia"] +
            digrafo["aristas"][(escala, destino)]["distancia"]
        )

        if distancia_con_escala > limite:
            return False, distancia_total, limite

    return True, distancia_total, limite

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

