def extraer_informacion_imagen(ruta_imagen : str, mode : int, nombre_mapa_guardar=None):
    from detectar_edicion_imagen import detectar_edicion_imagen
    from trazar_mapa import trazar_mapa
    if mode == 1:
        detectar_edicion_imagen(ruta_imagen)
    elif mode == 2:
        trazar_mapa([ruta_imagen], nombre_mapa_guardar)
    elif mode == 3:
        detectar_edicion_imagen(ruta_imagen)
        trazar_mapa([ruta_imagen], nombre_mapa_guardar)
    else:
        print("Error: Modo no válido. Consulte -h para la lista de comandos.")
