def detectar_edicion_imagen(ruta_imagen : str):
    import exiftool
    from json import loads
    indicadores_edicion = {"Software": None, "CreateDate": None, "ModifyDate": None}
    
    with exiftool.ExifTool() as et:
        try:
            # Execute ExifTool command to retrieve metadata
            metadata_json = et.execute(b"-j", ruta_imagen.encode('utf-8'))
            metadata_list = loads(metadata_json)
            metadatos = metadata_list[0] if metadata_list else {}

            software = metadatos.get("Software")
            create_date = metadatos.get("CreateDate")
            modify_date = metadatos.get("ModifyDate")
            
            if software:
                indicadores_edicion["Software"] = software
            if create_date and modify_date and create_date != modify_date:
                indicadores_edicion["CreateDate"] = create_date
                indicadores_edicion["ModifyDate"] = modify_date

            edicion_detectada = any(indicadores_edicion.values())
            if edicion_detectada:
                print("Posible edición detectada:")
                print(indicadores_edicion)
            else:
                print("No se detectaron indicios claros de edición en la imagen.")
                
            return edicion_detectada, indicadores_edicion
            
        except Exception as e:
            print(f"Error obteniendo metadatos: {e}")
            return False, indicadores_edicion