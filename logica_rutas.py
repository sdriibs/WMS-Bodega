import math

MAPA_SANTIAGO = {
    'SANTIAGO': (0, 0), 'ESTACION CENTRAL': (-2, -1), 'QUINTA NORMAL': (-2, 1),
    'INDEPENDENCIA': (0, 2), 'RECOLETA': (1, 2), 'SAN MIGUEL': (0, -3),
    'PAC': (-1, -3), 'SAN JOAQUIN': (2, -3), 'PROVIDENCIA': (3, 0),
    'ÑUÑOA': (4, -1), 'LA REINA': (6, 0), 'LAS CONDES': (6, 3),
    'VITACURA': (5, 5), 'LO BARNECHEA': (8, 6), 'CONCHALI': (0, 4),
    'HUECHURABA': (1, 6), 'RENCA': (-3, 4), 'QUILICURA': (-2, 8),
    'CERRO NAVIA': (-4, 3), 'LO PRADO': (-3, 1), 'PUDAHUEL': (-6, 2),
    'CERRILLOS': (-3, -5), 'MAIPU': (-6, -7), 'LO ESPEJO': (-1, -6),
    'LA CISTERNA': (0, -6), 'SAN RAMON': (1, -7), 'LA GRANJA': (2, -7),
    'EL BOSQUE': (0, -9), 'LA FLORIDA': (4, -6), 'SAN BERNARDO': (-1, -12),
    'COLINA': (0, 15), 'LAMPA': (-6, 12), 'PUENTE ALTO': (5, -11)
}

def calcular_distancia(comuna1, comuna2):
    x1, y1 = MAPA_SANTIAGO[comuna1]
    x2, y2 = MAPA_SANTIAGO[comuna2]
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def sugerir_vehiculo(cantidad):
    if cantidad == 0: return "Sin Carga"
    elif cantidad <= 35: return "Moto (1 Viaje)"
    elif cantidad <= 60: return "Auto / Furgón"
    else: return "Alta Carga (Forzar Doble Moto o Auto)"

def generar_rutas_dinamicas(conteo_ruteo, num_choferes):
    pendientes = {comuna: cant for comuna, cant in conteo_ruteo.items() if cant > 0}
    if not pendientes or num_choferes <= 0: return []

    total_paquetes = sum(pendientes.values())
    promedio_ideal = math.ceil(total_paquetes / num_choferes)
    limite_vehiculo = 60 
    rutas_armadas = []

    for i in range(num_choferes):
        if not pendientes: break

        comuna_ancla = max(pendientes, key=pendientes.get)
        ruta_actual = {
            'chofer_id': i + 1, 'comunas': [comuna_ancla],
            'desglose': {comuna_ancla: pendientes[comuna_ancla]},
            'total_paquetes': pendientes[comuna_ancla]
        }
        del pendientes[comuna_ancla]
        punto_actual = comuna_ancla

        while pendientes and ruta_actual['total_paquetes'] < promedio_ideal:
            vecino_cercano = min(pendientes.keys(), key=lambda k: calcular_distancia(punto_actual, k))
            paquetes_vecino = pendientes[vecino_cercano]

            if ruta_actual['total_paquetes'] + paquetes_vecino > limite_vehiculo: break 

            ruta_actual['comunas'].append(vecino_cercano)
            ruta_actual['desglose'][vecino_cercano] = paquetes_vecino
            ruta_actual['total_paquetes'] += paquetes_vecino
            punto_actual = vecino_cercano 
            del pendientes[vecino_cercano]

        ruta_actual['vehiculo'] = sugerir_vehiculo(ruta_actual['total_paquetes'])
        rutas_armadas.append(ruta_actual)

    if pendientes:
        ruta_rebalse = {
            'chofer_id': "EXTRA", 'comunas': list(pendientes.keys()),
            'desglose': pendientes, 'total_paquetes': sum(pendientes.values()),
            'vehiculo': "REBALSE - Faltan Choferes"
        }
        rutas_armadas.append(ruta_rebalse)

    return rutas_armadas