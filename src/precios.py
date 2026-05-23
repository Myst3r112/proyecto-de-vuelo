from src.digrafo import calcular_distancia_ruta

CLASES_TARIFA = {
    "Standard": {
        "multiplicador": 1.0,
        "detalle": "Tarifa base para viajar ligero.",
    },
    "Premium": {
        "multiplicador": 1.55,
        "detalle": "Mayor comodidad y prioridad en servicios.",
    },
    "Business": {
        "multiplicador": 2.35,
        "detalle": "Experiencia ejecutiva con mayor flexibilidad.",
    },
}

TIPOS_VIAJE = {
    "Solo ida": 1.0,
    "Ida y vuelta": 1.88,
}

IMPUESTO_PORCENTUAL = 0.18
TASA_AEROPUERTO_PERSONA_USD = 30.24
CAMBIO_PEN = 3.42

def formatear_monto(monto, moneda="USD"):
    return f"{moneda} {monto:,.2f}"

def calcular_precio_ruta(digrafo, ruta, *, tipo_viaje, clase, pasajeros):
    distancia_total = calcular_distancia_ruta(digrafo, ruta)
    segmentos = len(ruta) - 1
    escalas = max(0, len(ruta) - 2)
    pasajeros = max(1, int(pasajeros))

    base_por_persona = 42 + (distancia_total * 0.035) + (segmentos * 9) + (escalas * 12)
    subtotal_persona = base_por_persona * TIPOS_VIAJE[tipo_viaje] * CLASES_TARIFA[clase]["multiplicador"]
    impuesto_persona = subtotal_persona * IMPUESTO_PORCENTUAL
    tasa_aeropuerto_persona = TASA_AEROPUERTO_PERSONA_USD
    tasas_persona = impuesto_persona + tasa_aeropuerto_persona
    total_persona_usd = subtotal_persona + tasas_persona
    total_usd = total_persona_usd * pasajeros

    return {
        "ruta": ruta,
        "tipo_viaje": tipo_viaje,
        "clase": clase,
        "pasajeros": pasajeros,
        "distancia_total": distancia_total,
        "segmentos": segmentos,
        "escalas": escalas,
        "subtotal_persona_usd": subtotal_persona,
        "impuesto_porcentual": IMPUESTO_PORCENTUAL,
        "impuesto_persona_usd": impuesto_persona,
        "tasa_aeropuerto_persona_usd": tasa_aeropuerto_persona,
        "tasas_persona_usd": tasas_persona,
        "total_persona_usd": total_persona_usd,
        "total_usd": total_usd,
        "total_pen": total_usd * CAMBIO_PEN,
    }

def calcular_comparacion_tarifas(digrafo, ruta, *, tipo_viaje, pasajeros):
    comparacion = list()

    for clase in CLASES_TARIFA:
        precio = calcular_precio_ruta(
            digrafo,
            ruta,
            tipo_viaje=tipo_viaje,
            clase=clase,
            pasajeros=pasajeros,
        )
        comparacion.append({
            "Clase": clase,
            "Detalle": CLASES_TARIFA[clase]["detalle"],
            "Total USD": formatear_monto(precio["total_usd"], "USD"),
            "Total PEN": formatear_monto(precio["total_pen"], "PEN"),
        })

    return comparacion
