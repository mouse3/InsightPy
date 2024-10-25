"""
from os import path, walk, getcwd
import exiftool
from folium import Map, Marker, PolyLine
from datetime import datetime
from sys import argv
from math import log2
from collections import Counter
import hashlib
from json import loads
from PIL import Image
from re import findall
from pytsk3 import Img_Info, FS_Info, TSK_FS_META_TYPE_REG, TSK_FS_META_FLAG_UNALLOC
from log_viewer import procesar_logs
from traceroute import traceroute
"""

def hexdump(file_path : str):
    with open(file_path, 'rb') as f:
        offset = 0
        while chunk := f.read(16):
            # Muestra el offset
            print(f"{offset:08x}  ", end='')

            # Muestra los bytes en formato hexadecimal
            hex_bytes = ' '.join(f"{byte:02x}" for byte in chunk)
            print(f"{hex_bytes:<48}", end=' ')

            # Muestra los caracteres imprimibles (o '.' si no es imprimible)
            ascii_rep = ''.join(chr(byte) if 32 <= byte <= 126 else '.' for byte in chunk)
            print(f"|{ascii_rep}|")

            offset += len(chunk)

def extract_strings(file_path : str, min_length : int):
    from re import findall
    """
    Extrae y devuelve todas las cadenas de texto legibles de un archivo binario.

    :param file_path: Ruta del archivo a analizar.
    :param min_length: Longitud mínima de las cadenas a extraer (por defecto es 4).
    :return: Una lista de cadenas legibles encontradas en el archivo.
    """
    # Convertir min_length a entero por si llega como string
    min_length = int(min_length)

    with open(file_path, "rb") as f:
        data = f.read()

    # Utiliza una expresión regular para encontrar secuencias de caracteres legibles
    pattern = rb'[\x20-\x7E]{%d,}' % min_length
    strings = findall(pattern, data)
    return [s.decode("utf-8", errors="ignore") for s in strings]

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

def extract_lsb_message(image_path : str):
    from PIL import Image
    # Cargar la imagen
    image = Image.open(image_path)
    pixels = list(image.getdata())
    
    # Vamos a almacenar los bits del mensaje oculto
    hidden_bits = []
    
    for pixel in pixels:
        for color in pixel[:3]:  # Sólo RGB, ignorar el canal alfa si existe
            hidden_bits.append(color & 1)  # Extrae el bit menos significativo
    
    # Agrupar los bits en bytes (8 bits cada uno)
    hidden_message = ""
    for i in range(0, len(hidden_bits), 8):
        byte = hidden_bits[i:i+8]
        # Convertir de bits a un caracter (ASCII)
        hidden_message += chr(int("".join(map(str, byte)), 2))
    
    # Eliminar cualquier relleno nulo al final del mensaje
    hidden_message = hidden_message.split('\x00', 1)[0]
    
    return hidden_message


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

def extraer_informacion_imagen(ruta_imagen : str, mode : int, nombre_mapa_guardar=None):
    if mode == 1:
        detectar_edicion_imagen(ruta_imagen)
    elif mode == 2:
        trazar_mapa([ruta_imagen], nombre_mapa_guardar)
    elif mode == 3:
        detectar_edicion_imagen(ruta_imagen)
        trazar_mapa([ruta_imagen], nombre_mapa_guardar)
    else:
        print("Error: Modo no válido. Consulte -h para la lista de comandos.")

def entropy(file_path : str):
    from math import log2
    from collections import Counter
    # Leer el archivo en modo binario
    with open(file_path, 'rb') as file:
        data = file.read()
    #Full mathematics here
    # Calculates the frecuency of each byte of the data 
    frecuency = Counter(data)
    
    # Calculates the probability of each byte 
    length = len(data)
    probabilities = [frec / length for frec in frecuency.values()]
    
    # Calculates the entropy using the Shannons' formula 
    entropie = -sum(p * log2(p) for p in probabilities)

    ###### Redundancy
    redundancy = 1 - entropie/(log2(255)) #255 possible symbols(on a byte)
    return entropie, redundancy


def calculate_hash(file_path :str, algorithm : str):
    import hashlib
    if algorithm == '':
        algorithm = 'md5'
    # Initialize the hash object
    hash_func = getattr(hashlib, algorithm)()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            hash_func.update(chunk)
    return hash_func.hexdigest()
