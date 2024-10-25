def pcap_to_folium_map(pcap_file, output_map):
    from folium import Map, PolyLine, CircleMarker
    from scapy.all import rdpcap, IP
    from requests import get
    from ipaddress import ip_address
    # Coordenadas para áreas específicas
    atlantic_coords = (25.0, -45.0)  # Centro aproximado del Atlántico Norte
    local_network_bounds = {
        "lat_min": 20.0,
        "lat_max": 40.0,
        "lon_min": -60.0,
        "lon_max": -30.0,
    }


    # Función para convertir bytes a una unidad de medida legible
    def format_data_size(bytes_count):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_count < 1024:
                return f"{bytes_count:.2f} {unit}"
            bytes_count /= 1024
        return f"{bytes_count:.2f} PB"

    # Generar cuadrícula ordenada y espaciada para IPs locales basadas en la frecuencia de conexión
    def generate_ordered_coords_in_rectangle(bounds, rank, total):
        grid_size = int(total**0.5) + 1
        row = rank // grid_size
        col = rank % grid_size

        lat_spacing = (bounds["lat_max"] - bounds["lat_min"]) / grid_size
        lon_spacing = (bounds["lon_max"] - bounds["lon_min"]) / grid_size

        lat = bounds["lat_min"] + (row * lat_spacing)
        lon = bounds["lon_min"] + (col * lon_spacing)
        return lat, lon

    # Determinar si una IP es privada
    def is_private_ip(ip):
        return ip_address(ip).is_private

    # Obtener ubicación de IP pública usando un servicio de geolocalización o ubicación predeterminada
    def get_ip_location(ip, rank, total_private_ips):
        if is_private_ip(ip):
            return generate_ordered_coords_in_rectangle(local_network_bounds, rank, total_private_ips)
        else:
            try:
                response = get(f"https://ipinfo.io/{ip}/json")
                data = response.json()
                loc = data.get("loc", None)
                if loc:
                    lat, lon = map(float, loc.split(","))
                    return lat, lon
            except:
                pass
        return atlantic_coords

    # Función principal para procesar PCAP y crear el mapa en Folium
        try:
            packets = rdpcap(pcap_file)
        except Exception as e:
            print(f"An error occurred when reading the PCAP file: {e}")
            return

        # Crear un mapa de Folium
        m = Map(location=[20, 0], zoom_start=2)

        # Diccionarios para almacenar ubicaciones de IPs y conexiones
        ip_locations = {}
        connection_count = {}
        connection_data_size = {}  # Tamaño de datos transmitidos en cada conexión
        private_ip_ranking = {}

        # Extraer IPs, contar conexiones y sumar tamaños de datos
        for packet in packets:
            if IP in packet:
                src_ip = packet[IP].src
                dst_ip = packet[IP].dst

                # Contar las conexiones y sumar el tamaño de datos transmitidos
                connection = (src_ip, dst_ip)
                connection_count[connection] = connection_count.get(connection, 0) + 1
                connection_data_size[connection] = connection_data_size.get(connection, 0) + len(packet)
                private_ip_ranking[src_ip] = private_ip_ranking.get(src_ip, 0) + 1
                private_ip_ranking[dst_ip] = private_ip_ranking.get(dst_ip, 0) + 1

        # Ordenar IPs privadas y asignar ubicaciones
        ranked_private_ips = {ip: rank for rank, ip in enumerate(
            sorted((ip for ip in private_ip_ranking if is_private_ip(ip)), key=lambda x: -private_ip_ranking[x]))}

        for packet in packets:
            if IP in packet:
                src_ip = packet[IP].src
                dst_ip = packet[IP].dst

                if src_ip not in ip_locations:
                    ip_locations[src_ip] = get_ip_location(src_ip, ranked_private_ips.get(src_ip, 0), len(ranked_private_ips))
                if dst_ip not in ip_locations:
                    ip_locations[dst_ip] = get_ip_location(dst_ip, ranked_private_ips.get(dst_ip, 0), len(ranked_private_ips))

        # Encontrar la conexión más frecuente
        max_connection = max(connection_count, key=connection_count.get)
        max_count = connection_count[max_connection]

        print(f"The connection with the most requests is {max_connection[0]} <-> {max_connection[1]} with {max_count} requests.\n")

        # Crear nodos y líneas en el mapa
        node_request_count = {}
        for (src, dst), count in connection_count.items():
            node_request_count[src] = node_request_count.get(src, 0) + count
            node_request_count[dst] = node_request_count.get(dst, 0) + count

            # Obtener coordenadas de origen y destino
            src_coords = ip_locations[src]
            dst_coords = ip_locations[dst]

            # Color de la conexión más frecuente
            line_color = 'red' if (src, dst) == max_connection else 'blue'

            # Convertir tamaño de datos a una unidad de medida adecuada
            data_size = format_data_size(connection_data_size[(src, dst)])

            # Añadir línea para la conexión con el tamaño de datos en el tooltip
            PolyLine(
                locations=[src_coords, dst_coords],
                color=line_color,
                weight=2,
                tooltip=f"{src} <-> {dst} ({count} requests, total: {data_size})"
            ).add_to(m)

        # Añadir nodos de hosts al mapa
        for ip, coords in ip_locations.items():
            request_count = node_request_count.get(ip, 1)

            CircleMarker(
                location=coords,
                radius=5 + (request_count / 5000),
                color='green',
                fill=True,
                fill_opacity=0.6,
                tooltip=f"Host: {ip}\nRequests: {request_count}"
            ).add_to(m)

        # Guardar el mapa en un archivo HTML
        m.save(output_map + ".html")
        print(f"Map saved as {output_map}.html")