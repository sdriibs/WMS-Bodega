def calcular_rutas(conteo_para_motor, num_vehiculos):
    """
    Algoritmo Greedy a prueba de balas.
    Recibe: {'SANTIAGO': 40, 'PAC': 20} y el número de vehículos.
    """
    if not conteo_para_motor or num_vehiculos <= 0:
        return []

    # 1. Crear las "cajas" (vehículos) vacías
    rutas = [{'id': i+1, 'comunas': [], 'total': 0} for i in range(num_vehiculos)]
    
    # 2. Ordenar las comunas de la más pesada a la más liviana
    comunas_ordenadas = sorted(conteo_para_motor.items(), key=lambda x: x[1], reverse=True)
    
    # 3. Reparto equitativo (Greedy)
    for comuna, cantidad in comunas_ordenadas:
        # Encontrar el vehículo que tiene MENOS carga en este momento
        ruta_mas_vacia = min(rutas, key=lambda r: r['total'])
        
        # Asignarle la comuna
        ruta_mas_vacia['comunas'].append(comuna)
        ruta_mas_vacia['total'] += cantidad
        
    # 4. Limpiar: Retornar solo las rutas que sí tienen carga (por si sobran camiones)
    rutas_utiles = [r for r in rutas if r['total'] > 0]
    
    return rutas_utiles
