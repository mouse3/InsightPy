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
    
--wav-analysis [Full wav file path]                         Shows the two-dimensional(
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
--modulation-detector [Full wav file path]
                                                            Analyze and process a full wav-recorded signal 

"""

import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout,
    QComboBox, QPushButton, QWidget, QLineEdit, QTextEdit, QRadioButton,
    QButtonGroup, QFileDialog
)
# Importar todas las funciones desde los archivos correspondientes
from functions.calculate_hash import calculate_hash
from functions.detectar_edicion_imagen import detectar_edicion_imagen
from functions.entropy import entropy
from functions.extract_lsb_message import extract_lsb_message
from functions.extract_strings import extract_strings
from functions.extraer_informacion_imagen import extraer_informacion_imagen
from functions.hexdump import hexdump
from functions.trazar_mapa import trazar_mapa
from functions.verificar_extension_cambiada import verificar_extension_cambiada
from functions.analyze_log import procesar_logs as analyze_log 
from functions.wav_analysis import wav_analysis
from demodulador import pyzdr
import subprocess


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Forensic Analysis Tool")
        self.resize(920, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Main layout
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Console log
        self.console_log = QTextEdit(self)
        self.console_log.setReadOnly(True)
        self.console_log.setPlaceholderText("Console log")
        self.layout.addWidget(self.console_log)

        # Function selection
        self.function_label = QLabel("Select Function:")
        self.layout.addWidget(self.function_label)
        self.function_combobox = QComboBox()
        self.function_combobox.addItems([
            "--ext-changed", "--entropy", "--lsb", "--hash", "--strings",
            "--hexdump", "--analyze-sniffed", "--analyze-log",
            "--analyze-image", "--trace-map", "--wav-analysis", "--modulation-detector"
        ])
        self.layout.addWidget(self.function_combobox)

        # Input fields
        self.input_layout = QVBoxLayout()
        self.input_fields = []
        self.layout.addLayout(self.input_layout)

        # Add execute button
        self.execute_button = QPushButton("Execute")
        self.execute_button.clicked.connect(self.execute_function)
        self.layout.addWidget(self.execute_button)

        # Update input fields based on function selection
        self.function_combobox.currentTextChanged.connect(self.update_inputs)
        self.update_inputs(self.function_combobox.currentText())

    def update_inputs(self, function_name):
        # Clear previous inputs
        for field in self.input_fields:
            self.input_layout.removeWidget(field)
            field.deleteLater()
        self.input_fields.clear()

        # Add inputs based on the function selected
        if function_name == "--ext-changed":
            self.add_file_input("Select Directory", folder=True)
        elif function_name in ["--entropy", "--lsb", "--hexdump", "--analyze-log", "--wav-analysis", "--modulation-detector"]:
            self.add_file_input("Select File")
        elif function_name == "--hash":
            self.add_file_input("Select File")
            self.add_text_input("Hash Type")
        elif function_name == "--strings":
            self.add_file_input("Select Directory", folder=True)
            self.add_text_input("Min Length")
        elif function_name == "--analyze-sniffed":
            self.add_file_input("Select File")
            self.add_text_input("Output File Name")
            self.add_text_input("Mode (1=HTML, 2=Image)")
        elif function_name == "--analyze-image":
            self.add_text_input("Mode (1=Edit Detection, 2=Geolocation, 3=Both)")
            self.add_text_input("Output Map Name")
        elif function_name == "--trace-map":
            self.add_file_input("Tracert File Path")
            self.add_text_input("Map File Name")

    def add_file_input(self, placeholder, folder=False):
        layout = QHBoxLayout()
        line_edit = QLineEdit()
        line_edit.setPlaceholderText(placeholder)
        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(lambda: self.browse_file(line_edit, folder))
        layout.addWidget(line_edit)
        layout.addWidget(browse_button)
        self.input_layout.addLayout(layout)
        self.input_fields.append(line_edit)

    def add_text_input(self, placeholder):
        line_edit = QLineEdit()
        line_edit.setPlaceholderText(placeholder)
        self.input_layout.addWidget(line_edit)
        self.input_fields.append(line_edit)

    def browse_file(self, line_edit, folder):
        options = QFileDialog.Options()
        if folder:
            file_path = QFileDialog.getExistingDirectory(self, "Select Directory", options=options)
        else:
            file_path, _ = QFileDialog.getOpenFileName(self, "Select File", "", "All Files (*)", options=options)
        if file_path:
            line_edit.setText(file_path)

    def execute_function(self, function_name):
        # Limpiar widgets existentes en el layout de entrada
        for i in reversed(range(self.input_layout.count())):
            widget_to_remove = self.input_layout.itemAt(i).widget()
            if widget_to_remove is not None:
                widget_to_remove.deleteLater()
                self.input_layout.removeWidget(widget_to_remove)

        # Limpiar lista de campos
        self.input_fields.clear()

        # Añadir nuevos inputs según la función seleccionada
        if function_name == "--ext-changed":
            self.add_file_input("Select Directory", folder=True)
        elif function_name in ["--entropy", "--lsb", "--hexdump", "--analyze-log", "--wav-analysis", "--modulation-detector"]:
            self.add_file_input("Select File")
        elif function_name == "--hash":
            self.add_file_input("Select File")
            self.add_text_input("Hash Type")
        elif function_name == "--strings":
            self.add_file_input("Select Directory", folder=True)
            self.add_text_input("Min Length")
        elif function_name == "--analyze-sniffed":
            self.add_file_input("Select File")
            self.add_text_input("Output File Name")
            self.add_text_input("Mode (1=HTML, 2=Image)")
        elif function_name == "--analyze-image":
            self.add_text_input("Mode (1=Edit Detection, 2=Geolocation, 3=Both)")
            self.add_text_input("Output Map Name")
        elif function_name == "--trace-map":
            self.add_file_input("Tracert File Path")
            self.add_text_input("Map File º")



app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())