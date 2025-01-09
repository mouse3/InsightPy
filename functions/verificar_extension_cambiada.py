def verificar_extension_cambiada(ruta_directorio : str):
    from os import path, walk
    import exiftool
    cant_archivos_modif = 0
    with exiftool.ExifTool() as et:
        for carpeta_raiz, subcarpetas, archivos in walk(ruta_directorio):
            for archivo in archivos:
                ruta_completa = path.join(carpeta_raiz, archivo)
                
                # Ignorar ciertos archivos como los de 'exiftool_files'
                if 'exiftool_files' in ruta_completa:
                    continue  
                
                # Obtener la extensión del archivo actual
                extension_actual = path.splitext(archivo)[-1].lower().replace('.', '')
                
                try:
                    # Usar get_metadata en lugar de get_metadata_batch
                    metadata = et.get_metadata(ruta_completa)
                    
                    # Verificar si los metadatos contienen el tipo de archivo
                    if metadata:
                        tipo_archivo = metadata.get('File:FileTypeExtension', '').lower()
                        if extension_actual != tipo_archivo:
                            cant_archivos_modif += 1
                            print(f"El archivo '{ruta_completa}' tiene la extensión '.{extension_actual}' pero en los metadatos aparece como '.{tipo_archivo}'")
                except Exception as e:
                    print(f"No se pudieron obtener metadatos para '{ruta_completa}': {e}")
                    continue
        return cant_archivos_modif