def trazar_mapa(rutas_imagenes : str, nombre_mapa_guardar="mapa.html"):
    import exiftool
    from folium import Map, Marker, PolyLine
    from datetime import datetime
    datos_imagenes = []
    with exiftool.ExifTool() as et:
        for ruta in rutas_imagenes:
            metadatos = et.get_metadata_batch(ruta)
            gps_latitude = metadatos.get("EXIF:GPSLatitude")
            gps_longitude = metadatos.get("EXIF:GPSLongitude")
            gps_latitude_ref = metadatos.get("EXIF:GPSLatitudeRef")
            gps_longitude_ref = metadatos.get("EXIF:GPSLongitudeRef")
            fecha_hora = metadatos.get("EXIF:DateTimeOriginal") or metadatos.get("EXIF:CreateDate")
            if gps_latitude and gps_longitude and fecha_hora:
                lat = gps_latitude if gps_latitude_ref == "N" else -gps_latitude
                lon = gps_longitude if gps_longitude_ref == "E" else -gps_longitude
                fecha_hora = datetime.strptime(fecha_hora, "%Y:%m:%d %H:%M:%S")
                datos_imagenes.append({"ruta": ruta, "latitud": lat, "longitud": lon, "fecha_hora": fecha_hora})
    datos_imagenes.sort(key=lambda x: x["fecha_hora"])
    if datos_imagenes:
        inicio = datos_imagenes[0]
        mapa = Map(location=[inicio["latitud"], inicio["longitud"]], zoom_start=12)
        puntos = [[dato["latitud"], dato["longitud"]] for dato in datos_imagenes]
        for punto in puntos:
            Marker(punto, popup=f"{punto}").add_to(mapa)
        PolyLine(puntos, color="blue", weight=2.5, opacity=1).add_to(mapa)
        mapa.save(nombre_mapa_guardar)
        print(f"Mapa guardado como {nombre_mapa_guardar}")
    else:
        print("No se encontraron datos de GPS para trazar en el mapa.")