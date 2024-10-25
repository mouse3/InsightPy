menu = """  
-h                                                          Shows this text messagge
    
--ext-changed [directory]                                   Verifies if the extension of a file in a directory was changed
    
--entropy [file path]                                       Analises the entropy and the redundancy of a file, This may detect some anti-forensic measure
    
--lsb [file path]                                           Decode a ocult message of a image
    
--hash [file path] [hash type]                              Calculates the hash of a specified file, default: MD5
    
--strings [directory] [min_length]                          Prints the strings on a file only if the strings are larger than the min_lenght
    
--hexdump [file path]                                       Prints the hexdump of a file (the hex information and translated to ASCII utf-8 )
    
--analyze-sniffed [file path] [output file name] [mode]     Prints the connections that have been made based on sniffing a .pcap file and its variants, 
                                                            and also prints the number of requests between one IP and another, smth like:
                                                                192.168.0.1 <-> 192.168.0.4 85 requests X MB/s
                                                                192.168.0.2 <-> 192.168.0.5 66 requests X MB/s
                                                                192.168.0.3 <-> 192.168.0.6 2 requests X MB/s
                                                            if mode is 1 -> Outputs a map created in folium with the .html extension
                                                            if mode is 2-> Outputs an image
    
--analyze-log [file path]                                   It represents the ADB logcat logs of an Android device on a 3-dimensional coordinate axis. 
                                                                X-axis: Unix time(ms)
                                                                Y-axis: PID
                                                                Z-axis: Importance (Info, warning, error and fatal)
                                                            Export the data using: adb logcat *:VIWEF > file.txt
    
--analyze-image [nº] [nombre del mapa a guardar.html]       nº = 1, Prints any possible editions in a image
                                                            nº = 2, Creates a .html map in which saves the geo-locations of the images
                                                            si nº = 3, Do both things
    
--trace-map [tracert path] [map file name]                  Shows the path of a icmp from a "tracert -4 -h 30 example.com > output.txt" command, 
                                                                example.com: the path of the domain that you want to visualize
                                                                output.txt: The file name, this file has the output of the comand saved in it
    
                                                            if you dont write the [map file name], it would save the map in a file whose name is "tracert_map.html"
                                                                Note that the location of each point(node) of the visualized path is extracted by ipinfo.io, it uses IP GeoLocation.
    
--wav-analysis [wav file path]                              Shows the two-dimensional(
                                                                                    X- Time(s)
                                                                                    Y- Amplitude) a
                                                            and three-dimensional(
                                                                                    X-Time(s)
                                                                                    Y-Frecuency(Hz)
                                                                                    Z-Intensity(dB)) 
                                                            graph representing the audio of a .wav file
                                                            Additionaly:
                                                                It shows the constellation diagram(that helps you to know if it's phase modulated).
                                                                And the fourier transform(To know if it is frecuency modulated) 
                                                            The intensity is calculated using the log10 of watts + 1e-18, this is done to avoid any calculation problems  

"""


"""
from os import path, walk, getcwd
import exiftool
from sys import argv



if __name__ == '__main__':
    if len(argv) > 1:
        if argv[1] == '-h':
            print(menu)
        elif argv[1] == '--ext-changed':
            ruta_directorio = argv[2] if len(argv) >= 3 else getcwd()
            cant_archivos_modif = verificar_extension_cambiada(ruta_directorio)
            print("Cantidad de archivos modificados: ", cant_archivos_modif)
        elif argv[1] == '--entropy':
            file_path = argv[2]
            entropie, redundancy = entropy(file_path)
            print(f'The entropy of the file is {entropie:.6f} bit by byte')
            print(f"The redundancy of the file is {redundancy:.6f}")
            if entropie == 0:
                print("The entropy level is so low")
            elif 0 < entropie <= 2:
                print("The entropy level is Low")
            elif 2 < entropie <= 4:
                print("The entropy level is Low-medium")
            elif 4 < entropie <= 6:
                print("The entropy level is Medium")
            elif 6 < entropie <= 7.5:
                print("The entropy level is Medium-high")
            elif 7.5 < entropie < 8:
                print("The entropy level is high, Is so possible that there was applied a forensic evasion technique.")
            elif entropie >= 8:
                print("The entropy level i high af. This is imposible")
        elif argv[1] == '--lsb':
            if len(argv) > 1:
                image_path = argv[2]
                text = extract_lsb_message(image_path)
                print("Ocult message:" + text)
        elif argv[1] == '--strings':
            if len(argv) == 4:
                file_path = argv[2]
                n_string = argv[3]
                strings = extract_strings(file_path, n_string)
                for string in strings:
                    print(string)
            else: 
                print("Error: Parámetros insuficientes. Consulte -h para la lista de comandos.")
        elif argv[1] == '--hash':
            print("hashlib supports: sha1, sha224, sha256, sha384, sha512, sha3_224 \nsha3_256, sha3_384, sha3_512, shake128, shake256, blake2b, blake2s and md5 \n")
            if len(argv) == 4:
                file_path = argv[2]
                algorithm = argv[3]
                file_hash = calculate_hash(file_path, algorithm)
            elif len(argv) == 3:
                file_path = argv[2]
                algorithm = "sha1"
                file_hash = calculate_hash(file_path, algorithm)
            else:
                print("Error: Parámetros insuficientes. Consulte -h para la lista de comandos.")
            print(f"The hash {algorithm.upper()} of the file is: {file_hash}")
        elif argv[1] == '--analyze-log':
            from log_viewer import procesar_logs
            if len(argv) == 3:
                directory = argv[2] if len(argv) >= 3 else getcwd()
                procesar_logs(directory)
        elif argv[1] == '--hexdump':
            if len(argv) == 3:
                directory = argv[2] if len(argv) >= 3 else getcwd()
                hexdump(directory)
        elif argv[1] == '--analyze-image':
            if len(argv) >= 4:
                ruta_imagen = argv[3]
                mode = int(argv[2])
                nombre_mapa_guardar = argv[4] if len(argv) > 4 else "mapa.html"
                extraer_informacion_imagen(ruta_imagen, mode, nombre_mapa_guardar)
            else:
                print("Error: Parámetros insuficientes. Consulte -h para la lista de comandos.")
        elif argv[1] == '--trace-map':
            from traceroute import traceroute
            if len(argv)  >= 3:
                archivo_traceado = argv[2] 
                nombre_mapa_guardar = argv[3] if len(argv) > 3 else "tracert_map.html"
                traceroute(archivo_traceado, nombre_mapa_guardar)
        elif argv[1] == '--wav-analysis':
            from wav_analysis import wav_analysis
            if len(argv) == 3:
                wav_file = argv[2] if len(argv) >= 3 else getcwd()
                wav_analysis(wav_file)
        elif argv[1] == '--analyze-sniffed':
            from pcap import pcap_to_image
            pcap_file = argv[2]
            output_image = argv[3]
            pcap_to_image(pcap_file, output_image)
        else:
            print("Comando no reconocido. Use '-h' para ver la lista de comandos.")
    else:
        print(menu)
"""

"""
Hay que cambiar la clase, de tal manera que:
    Se pueda meter inputs(agregando un Label de texto o smth like that) para que las funciones pues funcionen(XD)
    O, mejor dicho; poder pasarle los inputs necesarios a las funciones para que cumplan con su objetivo

Funcion tochisima:
    Que se pueda elegir un archivo a través de un gestor de archivos(https://kivy.org/doc/stable/api-kivy.uix.filechooser.html)
"""





from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.uix.filechooser import FileChooserListView
from datetime import datetime
import declaraciones


# Funciones globales correspondientes a cada opción
def show_help():
    print(menu) 

def ext_changed(directory): 
    print(f"Verifying if the extension of files in {directory} was changed")
    salida = declaraciones.verificar_extension_cambiada(directory)
    print(salida)
    print(salida)

def analyze_entropy(file_path):
    print(f"Analyzing the entropy of {file_path}")
    salida = declaraciones.entropy(file_path)
    print(salida)

def decode_lsb(file_path):
    print(f"Decoding hidden message in {file_path}")
    salida = declaraciones.extract_lsb_message(file_path)
    print(salida)

def calculate_hash(file_path, hash_type):
    if hash_type == '':
        hash_type = 'md5'
    print(f"Calculating {hash_type} hash for {file_path}")
    salida = declaraciones.calculate_hash(file_path, hash_type)
    print(salida)

def extract_strings(directory, min_length):
    print(f"Extracting strings from {directory} with a minimum length of {min_length}")
    salida = declaraciones.extract_strings(directory, min_length)
    print(salida)

def hexdump(file_path):
    print(f"Printing hexdump of {file_path}")
    salida = declaraciones.hexdump(file_path)
    print(salida)

def analyze_sniffed(file_path, output_name, mode):
    if mode == 1: #mapa
        from pcap_2_map import pcap_to_folium_map
        pcap_to_folium_map(file_path, output_name)
    elif mode == 2: #imagen
        from pcap_2_image import pcap_to_image
        print(f"Analyzing connections in {file_path} and saving results to {output_name}")
        salida = pcap_to_image(file_path, output_name)
        print(salida)

def analyze_log(file_path):
    from log_viewer import procesar_logs
    print(f"Analyzing ADB logcat logs from {file_path} in 3D coordinates")
    procesar_logs(file_path)

def tracert_map(tracert_path, map_file='tracert_map.html'):
    import traceroute
    print(f"Tracing route based on {tracert_path} and saving to {map_file}")
    traceroute.traceroute(tracert_path, map_file)

def wav_analysis(wav_file):
    from wav_analysis import wav_analysis
    print(f"Analyzing .wav file: {wav_file}")


# Función para abrir la ventana de selección de archivo
def open_filechooser(callback):
    layout = BoxLayout(orientation='vertical')
    filechooser = FileChooserListView()
    layout.add_widget(filechooser)

    # Botón para seleccionar archivo
    select_button = Button(text="Seleccionar")
    layout.add_widget(select_button)

    popup = Popup(title="Seleccionar archivo", content=layout, size_hint=(0.9, 0.9))

    def on_file_select(instance):
        selected_file = filechooser.selection and filechooser.selection[0]
        if selected_file:
            callback(selected_file)  # Llama a la función correspondiente con el archivo seleccionado
            popup.dismiss()

    select_button.bind(on_release=on_file_select)
    popup.open()


class MyApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical', size_hint=(None, None), width=300, height=400)
        layout.pos_hint = {'center_x': 0.5, 'center_y': 0.5}

        self.time_label = Label(text=self.get_time(), font_size=24)
        layout.add_widget(self.time_label)
        Clock.schedule_interval(self.update_time, 1)

        dropdown = DropDown()

        # Botones de opciones con la ventana de selección de archivo

        option_entropy = Button(text='--entropy', size_hint_y=None, height=44)
        option_entropy.bind(on_release=lambda btn: open_filechooser(analyze_entropy))
        dropdown.add_widget(option_entropy)

        option_lsb = Button(text='--lsb', size_hint_y=None, height=44)
        option_lsb.bind(on_release=lambda btn: open_filechooser(decode_lsb))
        dropdown.add_widget(option_lsb)

        option_hash = Button(text='--hash', size_hint_y=None, height=44)
        option_hash.bind(on_release=lambda btn: open_filechooser(lambda path: calculate_hash(path, "md5")))
        dropdown.add_widget(option_hash)

        option_hexdump = Button(text='--hexdump', size_hint_y=None, height=44)
        option_hexdump.bind(on_release=lambda btn: open_filechooser(hexdump))
        dropdown.add_widget(option_hexdump)

        option_sniffed = Button(text='--analyze-sniffed', size_hint_y=None, height=44)
        option_sniffed.bind(on_release=lambda btn: open_filechooser(lambda path: analyze_sniffed(path, "output_image")))
        dropdown.add_widget(option_sniffed)

        option_log = Button(text='--analyze-log', size_hint_y=None, height=44)
        option_log.bind(on_release=lambda btn: open_filechooser(analyze_log))
        dropdown.add_widget(option_log)

        option_trace = Button(text='--trace-map', size_hint_y=None, height=44)
        option_trace.bind(on_release=lambda btn: open_filechooser(tracert_map))
        dropdown.add_widget(option_trace)

        option_wav = Button(text='--wav-analysis', size_hint_y=None, height=44)
        option_wav.bind(on_release=lambda btn: open_filechooser(wav_analysis))
        dropdown.add_widget(option_wav)

        mainbutton = Button(text='Mostrar Opciones', size_hint=(None, None), height=44, width=200)
        mainbutton.bind(on_release=dropdown.open)
        layout.add_widget(mainbutton)

        return layout

    def get_time(self):
        return datetime.now().strftime('%H:%M:%S')

    def update_time(self, dt):
        self.time_label.text = self.get_time()

if __name__ == '__main__':
    MyApp().run()
