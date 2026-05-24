import numpy as np
from src.data import *
from src.busqueda import buscar_rutas

def crear_matriz(dimension) -> np.ndarray:
    matriz = np.zeros((dimension, dimension), dtype=int)
    
    for origen, destino in conexiones:
        if origen in paises and destino in paises:
            i, j = paises.index(origen), paises.index(destino)
            matriz[i, j] = 1
            matriz[j, i] = 1

    return matriz

def producto_booleano(matriz_a, matriz_b):
    matriz_a = np.array(matriz_a, dtype=int)
    matriz_b = np.array(matriz_b, dtype=int)

    producto = matriz_a.dot(matriz_b)
    return (producto > 0).astype(int)

def calcular_conectividad(matriz):
    A = np.array(matriz, dtype=int)
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

    directa = A[i, j] == 1
    una_escala = A2[i, j] == 1
    dos_escalas = A3[i, j] == 1

    return {
        "A": A,
        "directa": directa,
        "una_escala": una_escala,
        "dos_escalas": dos_escalas,
        "hay_conectividad": directa or una_escala or dos_escalas
    }

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
    else: return list(paises)
    return sorted(list(opciones))
