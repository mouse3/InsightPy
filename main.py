from tkinter import Tk, Label, Frame, StringVar, Button, Text, Entry, END, filedialog, ttk, messagebox
from time import strftime
import declaraciones
from pcap_2_image import pcap_to_image
from pcap_2_map import pcap_to_folium_map
import os

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

def extract_strings(file_path: str, min_length: int):
    """
    Extracts strings from the given file that are at least min_length characters long.
    
    :param file_path: Path to the file to be processed.
    :param min_length: Minimum length of strings to be extracted.
    :return: List of extracted strings.
    """
    import re
    
    # Define the regular expression pattern to match printable characters
    pattern = rb'[\x20-\x7E]{' + str(min_length).encode() + rb',}'
    
    # Read the binary data from the file
    with open(file_path, 'rb') as f:
        data = f.read()
    
    # Find all matching strings using the regex pattern
    strings = re.findall(pattern, data)
    
    # Decode the binary strings to ASCII
    decoded_strings = [s.decode('ascii') for s in strings]
    
    return decoded_strings

def verificar_extension_cambiada(directory_path: str):
    """
    Verifies if the extension of files in a directory have been changed.
    
    :param directory_path: Path to the directory to be checked.
    :return: List of files with changed extensions.
    """
    original_extensions = {
        '.jpg': 'ffd8ff',
        '.png': '89504e47',
        '.gif': '47494638',
        '.pdf': '25504446',
        '.zip': '504b0304',
        # Add more file signatures as needed
    }
    
    changed_files = []
    
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            with open(file_path, 'rb') as f:
                file_header = f.read(4).hex()
                for ext, signature in original_extensions.items():
                    if file_header.startswith(signature) and not file.endswith(ext):
                        changed_files.append(file_path)
    
    return changed_files

class MyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Forensic Analysis Tool")
        
        # Frame for time label
        self.time_label = Label(root, text="", font=("Helvetica", 16))
        self.time_label.grid(row=0, column=1, padx=10, pady=10)
        self.update_time()

        # Frame for options selection
        option_frame = Frame(root)
        option_frame.grid(row=1, column=0, padx=10, pady=10, sticky='n')
        Label(option_frame, text="Options Menu").grid(row=0, column=0)

        # Dropdown for function selection
        self.function_var = StringVar(value="Select Function")
        function_dropdown = ttk.Combobox(option_frame, textvariable=self.function_var)
        function_dropdown['values'] = [
            "Show Help", "Analyze Entropy", "Decode LSB", "Calculate Hash", 
            "Hex Dump", "Analyze Sniffed", "Analyze Log", "Trace Map", 
            "WAV Analysis", "Extract Strings", "Verify Extension Change"
        ]
        function_dropdown.grid(row=1, column=0, pady=2, sticky='ew')
        function_dropdown.bind("<<ComboboxSelected>>", self.update_inputs)

        # Frame for dynamic inputs
        self.input_frame = Frame(root)
        self.input_frame.grid(row=1, column=1, padx=10, pady=10)

        # Submit button
        submit_button = Button(root, text="Run Function", command=self.run_selected_function)
        submit_button.grid(row=2, column=1, padx=10, pady=10)

        # Clear button
        clear_button = Button(root, text="Clear Console", command=self.clear_console)
        clear_button.grid(row=2, column=0, padx=10, pady=10)

        # Console output
        self.console = Text(root, height=40, width=180)
        self.console.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

    def update_time(self):
        current_time = strftime('%H:%M:%S')
        self.time_label.config(text=current_time)
        self.root.after(1000, self.update_time)

    def show_help(self):
        self.console.insert(END, menu + "\n")

    def update_inputs(self, event=None):
        # Clear previous inputs
        for widget in self.input_frame.winfo_children():
            widget.destroy()

        # Get selected function
        selected_function = self.function_var.get()

        # Configure inputs based on function
        if selected_function == "Show Help":
            Label(self.input_frame, text="No inputs required for Help").grid(row=0, column=0)
        elif selected_function in ["Analyze Entropy", "Decode LSB", "Hex Dump", "WAV Analysis"]:
            self.create_file_selector("File Path:", file_type='file')
        elif selected_function == "Calculate Hash":
            self.create_file_selector("File Path:", file_type='file')
            Label(self.input_frame, text="Hash Type:").grid(row=1, column=0)
            self.hash_type_var = StringVar()
            hash_dropdown = ttk.Combobox(self.input_frame, textvariable=self.hash_type_var)
            hash_dropdown['values'] = ['md5', 'sha1', 'sha224', 'sha256', 'sha384', 'sha512']
            hash_dropdown.grid(row=1, column=1)
        elif selected_function == "Analyze Sniffed":
            self.create_file_selector("File Path:", file_type='file')
            Label(self.input_frame, text="Output File Name:").grid(row=1, column=0)
            self.output_file_entry = Entry(self.input_frame, width=50)
            self.output_file_entry.grid(row=1, column=1)
            Label(self.input_frame, text="Mode:").grid(row=2, column=0)
            self.mode_var = StringVar(value="Select Mode")
            mode_dropdown = ttk.Combobox(self.input_frame, textvariable=self.mode_var)
            mode_dropdown['values'] = ["1 - Outputs an Image file", "2 - Outputs a html Map"]
            mode_dropdown.grid(row=2, column=1)
        elif selected_function == "Trace Map":
            self.create_file_selector("Tracert Path:", file_type='file')
            Label(self.input_frame, text="Map File Name:").grid(row=1, column=0)
            self.map_file_entry = Entry(self.input_frame, width=50)
            self.map_file_entry.grid(row=1, column=1)
        elif selected_function == "Extract Strings":
            self.create_file_selector("File Path:", file_type='file')
            Label(self.input_frame, text="Minimum String Length:").grid(row=1, column=0)
            self.min_length_entry = Entry(self.input_frame, width=50)
            self.min_length_entry.grid(row=1, column=1)
        elif selected_function == "Verify Extension Change":
            self.create_file_selector("Directory Path:", file_type='directory')

    def create_file_selector(self, label_text, file_type='file'):
        """ Helper function to create file/directory selector buttons. """
        Label(self.input_frame, text=label_text).grid(row=0, column=0)
        self.file_path_var = StringVar()
        file_entry = Entry(self.input_frame, textvariable=self.file_path_var, width=50)
        file_entry.grid(row=0, column=1)
        if file_type == 'file':
            file_button = Button(self.input_frame, text="Browse", command=self.select_file)
        else:
            file_button = Button(self.input_frame, text="Browse", command=self.select_directory)
        file_button.grid(row=0, column=2)

    def select_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.file_path_var.set(file_path)

    def select_directory(self):
        directory_path = filedialog.askdirectory()
        if directory_path:
            self.file_path_var.set(directory_path)

    def clear_console(self):
        self.console.delete(1.0, END)

    def run_selected_function(self):
        selected_function = self.function_var.get()
        try:
            if selected_function == "Show Help":
                self.show_help()
            elif selected_function == "Analyze Entropy":
                file_path = self.file_path_var.get()
                self.console.insert(END, declaraciones.entropy(file_path) + "\n")
            elif selected_function == "Decode LSB":
                file_path = self.file_path_var.get()
                self.console.insert(END, declaraciones.extract_lsb_message(file_path) + "\n")
            elif selected_function == "Calculate Hash":
                file_path = self.file_path_var.get()
                hash_type = self.hash_type_var.get()
                self.console.insert(END, declaraciones.calculate_hash(file_path, hash_type) + "\n")
            elif selected_function == "Hex Dump":
                file_path = self.file_path_var.get()
                self.console.insert(END, declaraciones.hexdump(file_path) + "\n")
            elif selected_function == "Analyze Sniffed":
                file_path = self.file_path_var.get()
                output_file = self.output_file_entry.get()
                mode = self.mode_var.get().split()[0]
                if mode == "1":
                    pcap_to_image(file_path, output_file)
                elif mode == "2":
                    pcap_to_folium_map(file_path, output_file)
                self.console.insert(END, "Analysis complete. Output saved to: " + output_file + "\n")
            elif selected_function == "Analyze Log":
                file_path = self.file_path_var.get()
                self.console.insert(END, declaraciones.adblog(file_path) + "\n")
            elif selected_function == "Trace Map":
                file_path = self.file_path_var.get()
                map_file = self.map_file_entry.get() or "tracert_map.html"
                self.console.insert(END, declaraciones.traceroute(file_path, map_file) + "\n")
            elif selected_function == "WAV Analysis":
                file_path = self.file_path_var.get()
                self.console.insert(END, declaraciones.wav_analysis(file_path) + "\n")
            elif selected_function == "Extract Strings":
                file_path = self.file_path_var.get()
                min_length = int(self.min_length_entry.get())
                strings = extract_strings(file_path, min_length)
                for string in strings:
                    self.console.insert(END, string + "\n")
            elif selected_function == "Verify Extension Change":
                directory_path = self.file_path_var.get()
                changed_files = verificar_extension_cambiada(directory_path)
                if changed_files:
                    self.console.insert(END, "Files with changed extensions:\n")
                    for file in changed_files:
                        self.console.insert(END, file + "\n")
                else:
                    self.console.insert(END, "No files with changed extensions found.\n")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.console.insert(END, "Error: " + str(e) + "\n")

if __name__ == "__main__":
    root = Tk()
    app = MyApp(root)
    root.mainloop()
