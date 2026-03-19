# Mapa basico de conexiones radiales
GRAFO_AVENIDAS = {
    'SANTIAGO': ['ESTACION CENTRAL', 'QUINTA NORMAL', 'INDEPENDENCIA', 'RECOLETA', 'SAN MIGUEL', 'PAC', 'PROVIDENCIA', 'ÑUÑOA'],
    'PROVIDENCIA': ['SANTIAGO', 'ÑUÑOA', 'LAS CONDES', 'RECOLETA'],
    'ÑUÑOA': ['SANTIAGO', 'PROVIDENCIA', 'MACUL', 'LA REINA', 'PEÑALOLEN'],
    'MACUL': ['ÑUÑOA', 'LA FLORIDA', 'SAN JOAQUIN', 'PEÑALOLEN'],
    'PEÑALOLEN': ['ÑUÑOA', 'MACUL', 'LA FLORIDA', 'LA REINA'],
    'LA FLORIDA': ['PUENTE ALTO', 'MACUL', 'PEÑALOLEN', 'LA GRANJA', 'SAN RAMON'],
    'SAN JOAQUIN': ['SAN MIGUEL', 'MACUL', 'SANTIAGO', 'LA GRANJA'],
    'SAN MIGUEL': ['SANTIAGO', 'PAC', 'SAN JOAQUIN', 'LA CISTERNA', 'SAN RAMON'],
    'ESTACION CENTRAL': ['SANTIAGO', 'QUINTA NORMAL', 'LO PRADO', 'CERRILLOS', 'PAC'],
    'QUINTA NORMAL': ['SANTIAGO', 'ESTACION CENTRAL', 'LO PRADO', 'CERRO NAVIA', 'RENCA'],
    'LO PRADO': ['QUINTA NORMAL', 'ESTACION CENTRAL', 'PUDAHUEL', 'CERRO NAVIA'],
    'CERRO NAVIA': ['QUINTA NORMAL', 'LO PRADO', 'PUDAHUEL', 'RENCA'],
    'PUDAHUEL': ['LO PRADO', 'CERRO NAVIA', 'MAIPU', 'CERRILLOS', 'ESTACION CENTRAL', 'LAMPA'],
    'MAIPU': ['CERRILLOS', 'ESTACION CENTRAL', 'PUDAHUEL'],
    'CERRILLOS': ['MAIPU', 'ESTACION CENTRAL', 'PAC', 'LO ESPEJO'],
    'PAC': ['SANTIAGO', 'ESTACION CENTRAL', 'CERRILLOS', 'LO ESPEJO', 'SAN MIGUEL'],
    'LO ESPEJO': ['PAC', 'CERRILLOS', 'LA CISTERNA', 'SAN BERNARDO'],
    'LA CISTERNA': ['SAN MIGUEL', 'EL BOSQUE', 'SAN RAMON', 'LO ESPEJO', 'SAN BERNARDO'],
    'SAN RAMON': ['LA CISTERNA', 'SAN MIGUEL', 'LA GRANJA', 'LA FLORIDA', 'EL BOSQUE'],
    'LA GRANJA': ['SAN RAMON', 'SAN JOAQUIN', 'LA FLORIDA', 'MACUL'],
    'EL BOSQUE': ['LA CISTERNA', 'SAN BERNARDO', 'SAN RAMON'],
    'SAN BERNARDO': ['EL BOSQUE', 'LO ESPEJO', 'LA CISTERNA'],
    'PUENTE ALTO': ['LA FLORIDA'],
    'RECOLETA': ['SANTIAGO', 'INDEPENDENCIA', 'CONCHALI', 'HUECHURABA', 'PROVIDENCIA'],
    'INDEPENDENCIA': ['SANTIAGO', 'RECOLETA', 'CONCHALI', 'RENCA'],
    'CONCHALI': ['RECOLETA', 'INDEPENDENCIA', 'HUECHURABA', 'QUILICURA', 'RENCA'],
    'HUECHURABA': ['CONCHALI', 'RECOLETA', 'VITACURA', 'QUILICURA'],
    'RENCA': ['INDEPENDENCIA', 'CONCHALI', 'QUILICURA', 'CERRO NAVIA', 'QUINTA NORMAL'],
    'QUILICURA': ['RENCA', 'CONCHALI', 'HUECHURABA', 'LAMPA', 'COLINA'],
    'COLINA': ['QUILICURA', 'LAMPA'],
    'LAMPA': ['QUILICURA', 'COLINA', 'PUDAHUEL'],
    'LAS CONDES': ['PROVIDENCIA', 'VITACURA', 'LA REINA', 'LO BARNECHEA'],
    'VITACURA': ['LAS CONDES', 'LO BARNECHEA', 'PROVIDENCIA', 'HUECHURABA'],
    'LO BARNECHEA': ['LAS CONDES', 'VITACURA'],
    'LA REINA': ['ÑUÑOA', 'PEÑALOLEN', 'LAS CONDES']
}

def normalizar_y_filtrar(datos_crudos):
    alias = {
        "PEDRO AGUIRRE CERDA": "PAC",
        "P.A.C.": "PAC",
        "STGO": "SANTIAGO",
        "SANTIAGO CENTRO": "SANTIAGO",
        "ÑUÑOA": "NUNOA",
        "PEÑALOLEN": "PENALOLEN",
    }
    
    limpios = {}
    for comuna, cantidad in datos_crudos.items():
        if cantidad <= 0:
            continue
            
        nombre_upper = str(comuna).strip().upper()
        nombre_final = alias.get(nombre_upper, nombre_upper)
        
        limpios[nombre_final] = limpios.get(nombre_final, 0) + cantidad
        
    return limpios

def calcular_rutas(datos_bd, num_conductores):
    paquetes = normalizar_y_filtrar(datos_bd)
    if not paquetes:
        return []

    # Ordenar de mayor a menor para definir núcleos
    ordenado = sorted(paquetes.items(), key=lambda x: x[1], reverse=True)
    rutas = []
    asignadas = set()

    # Asignar Núcleos
    limite = min(num_conductores, len(ordenado))
    for i in range(limite):
        nucleo = ordenado[i][0]
        rutas.append({
            "id": i + 1,
            "nucleo": nucleo,
            "comunas": [nucleo],
            "total": paquetes[nucleo]
        })
        asignadas.add(nucleo)

    # Regla inamovible: Quilicura arrastra Lampa y Colina
    for ruta in rutas:
        if "QUILICURA" in ruta["comunas"]:
            for amarre in ["LAMPA", "COLINA"]:
                if amarre in paquetes and amarre not in asignadas:
                    ruta["comunas"].append(amarre)
                    ruta["total"] += paquetes[amarre]
                    asignadas.add(amarre)

    # Absorción radial (Gravedad)
    for comuna, cantidad in paquetes.items():
        if comuna in asignadas:
            continue

        vecinos = GRAFO_AVENIDAS.get(comuna, [])
        ruta_asignada = None

        # Buscar si algún vecino ya está en una ruta
        for ruta in rutas:
            if any(c in vecinos for c in ruta["comunas"]):
                ruta_asignada = ruta
                break

        # Si no tiene conexión, se va a la ruta con menos carga
        if not ruta_asignada:
            ruta_asignada = min(rutas, key=lambda x: x["total"])

        ruta_asignada["comunas"].append(comuna)
        ruta_asignada["total"] += cantidad
        asignadas.add(comuna)

    return rutas