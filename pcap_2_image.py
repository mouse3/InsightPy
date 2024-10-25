def pcap_to_image(pcap_file, output_image):
    from pyshark import FileCapture
    import matplotlib.pyplot as plt
    from networkx import Graph, spring_layout, draw_networkx_edges, draw_networkx_labels, draw_networkx_nodes
    import socket
    def format_size(size_bytes):
        #Convierte el tamaño en bytes a KB, MB o GB según sea necesario
        if size_bytes < 1024:
            return f"{size_bytes} Bytes"
        elif size_bytes < 1024 ** 2:
            return f"{size_bytes / 1024:.2f} KB"
        elif size_bytes < 1024 ** 3:
           return f"{size_bytes / (1024 ** 2):.2f} MB"
        else:
           return f"{size_bytes / (1024 ** 3):.2f} GB"

    try:
        # Cargar el archivo pcap usando pyshark
        cap = FileCapture(pcap_file, display_filter="ip")
    except Exception as e:
        print(f"An error has occurred when reading the PCAP file: {e}")
        return

    # Crear un grafo
    G = Graph()
    connection_count = {}
    connection_bytes = {}

    # Extraer IPs y agregar conexiones al grafo
    for packet in cap:
        try:
            src_ip = packet.ip.src
            dst_ip = packet.ip.dst
            packet_size = int(packet.length)  # Tamaño del paquete en bytes

            # Resolver dominio si no es una IP local
            for ip in [src_ip, dst_ip]:
                if not ip.startswith(("192", "255", "224")):
                    try:
                        domain_name = socket.gethostbyaddr(ip)[0]
                        ip = f"{ip}/{domain_name}"
                    except socket.herror:
                        pass

            # Añadir arista al grafo
            G.add_edge(src_ip, dst_ip)
            connection = (src_ip, dst_ip)
            connection_count[connection] = connection_count.get(connection, 0) + 1
            connection_bytes[connection] = connection_bytes.get(connection, 0) + packet_size

        except AttributeError:
            # Saltar paquetes que no contienen información IP
            continue

    # Ordenar y mostrar conexiones
    sorted_connections = sorted(
        connection_count.keys(),
        key=lambda conn: (connection_bytes[conn], connection_count[conn]),
        reverse=True
    )
    output = [
        f"{src} <-> {dst} {connection_count[(src, dst)]} requests, {format_size(connection_bytes[(src, dst)])}" 
        for src, dst in sorted_connections
    ]

    # Imprimir conexiones en la consola
    for line in output:
        print(line)

    # Dibujar el grafo
    plt.figure(figsize=(12, 8))
    pos = spring_layout(G)
    node_sizes = [G.degree(n) * 100 for n in G.nodes()]
    draw_networkx_nodes(G, pos, node_size=node_sizes, node_color='lightblue')
    edges_color = ['red' if edge == sorted_connections[0] else 'lightgray' for edge in G.edges()]
    draw_networkx_edges(G, pos, width=1.0, alpha=0.5, edge_color=edges_color)
    draw_networkx_labels(G, pos, font_size=10)

    # Guardar imagen
    plt.title('Connections IPs')
    plt.axis('off')
    plt.savefig(output_image + ".png", format='PNG')
    plt.close()

    return f"The connection with the most requests is {sorted_connections[0][0]} <-> {sorted_connections[0][1]} with {connection_count[sorted_connections[0]]} requests."
