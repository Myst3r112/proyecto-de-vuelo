import pandas as pd
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

coordenadas_paises = cargar_datos_csv("datos/coordenadas_paises.csv", tipo_dato="coordenadas")
conexiones = cargar_datos_csv("datos/conexiones.csv", tipo_dato="conexiones")
paises = [pais for pais in coordenadas_paises.keys()]
MARGEN_DESVIO = 0.35
