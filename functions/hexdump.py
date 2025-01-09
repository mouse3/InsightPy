def hexdump(file_path: str) -> str:
    output = []
    with open(file_path, 'rb') as f:
        offset = 0
        while chunk := f.read(16):
            # Muestra el offset
            line = f"{offset:08x}  "

            # Muestra los bytes en formato hexadecimal
            hex_bytes = ' '.join(f"{byte:02x}" for byte in chunk)
            line += f"{hex_bytes:<48} "

            # Muestra los caracteres imprimibles (o '.' si no es imprimible)
            ascii_rep = ''.join(chr(byte) if 32 <= byte <= 126 else '.' for byte in chunk)
            line += f"|{ascii_rep}|"

            output.append(line)
            offset += len(chunk)
    
    return '\n'.join(output)