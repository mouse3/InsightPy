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