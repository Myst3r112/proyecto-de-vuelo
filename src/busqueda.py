import numpy as np
from src.digrafo import verificar_margen_desvio, recorrer_ruta_paises_pares
from src.data import *

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

def buscar_rutas(matriz, origen, destino, *, tipo_ruta: str, digrafo=None) -> list:
    rutas = list()
    i, j = paises.index(origen), paises.index(destino)

    matriz = np.array(matriz, dtype=int)
    n = matriz.shape[0]
    posibles_escalas = [np.flatnonzero(matriz[row]).tolist() for row in range(n)]

    match tipo_ruta:
        case "directa":
            if matriz[i, j]:
                ruta = [origen, destino]
                if digrafo is None: rutas.append(ruta)
                else:
                    cumple_margen, _, _ = verificar_margen_desvio(digrafo, ruta)
                    if cumple_margen: rutas.append(ruta)
            pass
        case "una_escala":
            for k in posibles_escalas[i]:
                if k in (i, j): continue
                if matriz[k, j]:
                    ruta = [origen, paises[k], destino]
                    if digrafo is None: rutas.append(ruta)
                    else:
                        cumple_margen, _, _ = verificar_margen_desvio(digrafo, ruta)
                        if cumple_margen: rutas.append(ruta)
            pass                        
        case "dos_escalas":
            for k in posibles_escalas[i]:
                if k in (i, j): continue
                for l in posibles_escalas[k]:
                    if l in (i, k, j): continue
                    if matriz[l, j]:
                        ruta = [origen, paises[k], paises[l], destino]
                        if digrafo is None: rutas.append(ruta)
                        else:
                            cumple_margen, _, _ = verificar_margen_desvio(digrafo, ruta)
                            if cumple_margen: rutas.append(ruta)
            pass
    return rutas

def cargar_recomendaciones(digrafo, origen, destino, *, tipo_ruta: str) -> list:
    recomendaciones = list()
    valido, _ = validar_origen_destino(origen, destino)
    if not valido: return recomendaciones

    for escala_A in paises:
        match tipo_ruta:
            case "directa":
                ruta = list([origen, destino])
                if len(set(ruta)) != 2 : continue
                if digrafo["aristas"][(origen, destino)]["existe"]: continue
                _, distancia_total, limite = verificar_margen_desvio(digrafo, ruta)

                recomendaciones.append({
                    "mostrar": f"{origen} -> {destino}",
                    "ruta": ruta,
                    "distancia_total": distancia_total,
                    "limite": limite,
                    "conexiones_nuevas": [(origen, destino)]
                })
                break

            case "una_escala":
                ruta = list([origen, escala_A, destino])
                ruta_valida, _ = validar_ruta(ruta)

                if not ruta_valida: continue
                cumple_margen, distancia_total, limite = verificar_margen_desvio(digrafo, ruta)

                if not cumple_margen: continue
                if recorrer_ruta_paises_pares(digrafo, ruta, funcion="verificar_existencia"): continue
                nuevas = recorrer_ruta_paises_pares(digrafo, ruta, funcion="agregar_conexiones")

                if not nuevas: continue

                recomendaciones.append({
                    "mostrar": escala_A,
                    "ruta": ruta,
                    "distancia_total": distancia_total,
                    "limite": limite,
                    "conexiones_nuevas": nuevas
                })
                pass

            case "dos_escalas":
                for escala_B in paises:
                    ruta = list([origen, escala_A, escala_B, destino])
                    ruta_valida, _ = validar_ruta(ruta)
                    
                    if not ruta_valida: continue
                    cumple_margen, distancia_total, limite = verificar_margen_desvio(digrafo, ruta)

                    if not cumple_margen: continue
                    if recorrer_ruta_paises_pares(digrafo, ruta, funcion="verificar_existencia"): continue
                    nuevas = recorrer_ruta_paises_pares(digrafo, ruta, funcion="agregar_conexiones")

                    if not nuevas: continue
                    recomendaciones.append({
                        "mostrar": f"{escala_A} -> {escala_B}",
                        "ruta": ruta,
                        "distancia_total": distancia_total,
                        "limite": limite,
                        "conexiones_nuevas": nuevas
                    })
                pass

    recomendaciones.sort(key=lambda x: x["distancia_total"])
    return recomendaciones[:10]

def agregar_conexiones(matriz, digrafo, ruta):
    valido, mensaje = validar_ruta(ruta)

    if not valido: return False, mensaje
    cumple_margen, _, _ = verificar_margen_desvio(digrafo, ruta)

    if not cumple_margen: return False, "La ruta no cumple con el margen de desvio permitido"
    if recorrer_ruta_paises_pares(digrafo, ruta, funcion="verificar_existencia"): return False, "La ruta ya existe en la matriz de conexiones"
    nuevas_conexiones = recorrer_ruta_paises_pares(digrafo, ruta, funcion="agregar_conexiones")

    for origen, destino in nuevas_conexiones:
        fila = paises.index(origen)
        columna = paises.index(destino)

        matriz[fila, columna] = 1
        matriz[columna, fila] = 1
        digrafo["aristas"][(origen, destino)]["existe"] = True
        digrafo["aristas"][(destino, origen)]["existe"] = True

    texto_ruta = " -> ".join(ruta)
    return True, f"Ruta agregada correctamente: {texto_ruta}"

