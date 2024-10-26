from tkinter import Tk, Label, Frame, StringVar, Button, Text, Entry, END
from tkinter import filedialog, ttk, messagebox
from time import strftime
import declaraciones
from pcap_2_image import pcap_to_image
from pcap_2_map import pcap_to_folium_map

menu = """  
-h: Shows this help message

--ext-changed [directory]: Verifies if the extension of a file in a directory was changed

--entropy [file path]: Analyzes the entropy of a file to detect anti-forensic measures

--lsb [file path]: Decodes a hidden message from an image

--hash [file path] [hash type]: Calculates the hash of a specified file (default: MD5)

--strings [directory] [min_length]: Extracts strings in a file with length >= min_length

--hexdump [file path]: Displays the hex dump of a file

--analyze-sniffed [file path] [output file] [mode]: Analyzes a .pcap file to output network connections

--analyze-log [file path]: Visualizes Android device logs in 3D

--trace-map [tracert path] [map file]: Shows the path of an ICMP from a 'tracert' command

--wav-analysis [wav file path]: Analyzes and displays audio data of a .wav file

"""

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
            "Hex Dump", "Analyze Sniffed", "Analyze Log", "Trace Map", "WAV Analysis"
        ]
        function_dropdown.grid(row=1, column=0, pady=2, sticky='ew')
        function_dropdown.bind("<<ComboboxSelected>>", self.update_inputs)

        # Frame for dynamic inputs
        self.input_frame = Frame(root)
        self.input_frame.grid(row=1, column=1, padx=10, pady=10)

        # Submit button
        submit_button = Button(root, text="Run Function", command=self.run_selected_function)
        submit_button.grid(row=2, column=1, padx=10, pady=10)

        # Console output
        self.console = Text(root, height=20, width=80)
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
                hash_type = self.hash_type_var.get() or "md5"
                self.console.insert(END, declaraciones.calculate_hash(file_path, hash_type) + "\n")
            elif selected_function == "Hex Dump":
                file_path = self.file_path_var.get()
                self.console.insert(END, declaraciones.hexdump(file_path) + "\n")
            elif selected_function == "Analyze Sniffed":
                file_path = self.file_path_var.get()
                output_file = self.output_file_entry.get()
                mode = self.mode_var.get()
                if mode.startswith("1"):
                    self.console.insert(END, pcap_to_image(file_path, output_file) + "\n")
                elif mode.startswith("2"):
                    self.console.insert(END, pcap_to_folium_map(file_path, output_file) + "\n")
                else:
                    messagebox.showerror("Error", "Invalid mode selected.")
            elif selected_function == "Trace Map":
                file_path = self.file_path_var.get()
                map_file = self.map_file_entry.get() or "tracert_map.html"
                self.console.insert(END, declaraciones.traceroute(file_path, map_file) + "\n")
            elif selected_function == "WAV Analysis":
                file_path = self.file_path_var.get()
                self.console.insert(END, declaraciones.wav_analysis(file_path) + "\n")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.console.insert(END, "Error: " + str(e) + "\n")

if __name__ == "__main__":
    root = Tk()
    app = MyApp(root)
    root.mainloop()
