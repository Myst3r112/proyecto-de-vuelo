import base64
import math

def cargar_imagen(ruta):
    with open(ruta, "rb") as archivo: data = archivo.read()
    return base64.b64encode(data).decode()

def interpolar_color(t):
    r = int(46 + (217 - 46) * t)
    g = int(139 + (75 - 139) * t)
    b = int(87 + (75 - 87) * t)

    return [r, g, b]

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
