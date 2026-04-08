import numpy as np
import random
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
    

def crear_matriz():
    return np.zeros((len(paises),len(paises)), dtype=int)    

def agregar_ruta(matriz, origen, destino):
    valido, _ = validar_origen_destino(origen, destino)
    if not valido:
        return False

    i = indice_paises[origen]
    j = indice_paises[destino]

    if matriz[i][j] == 1:
        return False

    matriz[i][j] = 1
    return True

def generar_matriz_aleatoria(n, probabilidad=0.3):
    m = np.zeros((n, n), dtype=int)
    
    for i in range(n):
        for j in range(n):
            if i != j:  # evitar país consigo mismo
                if random.random() < probabilidad:
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