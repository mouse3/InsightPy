def lsb(image_path : str):
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