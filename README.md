
A forensic tool made-in Python with general purposes. All the functions that can be used are specified in the Usage 

### Releases in the 4.0 version:
1. User Interface made in`tkinter`
2. Added the "clear" button, that clears the console.
3. Optimizated code
###
1. When the `analyze sniffed` function is used, it prints a `Error: unsupported operand type(s) for +: 'NoneType' and 'str'` error but it still working, it's not a problem at all.
### **Usage**:
```
-h                                                          Shows this text messagge

--ext-changed [directory]                                   Verifies if the extension of a file in a directory was changed

--entropy [file path]                                       Analises the entropy and the redundancy of a file, This may detect some anti-forensic measure

--lsb [file path]                                           Decode a ocult message of a image

--hash [file path] [hash type]                              Calculates the hash of a specified file, default: MD5

--strings [directory] [min_length]                          Prints the strings on a file only if the strings are larger than the min_lenght

--hexdump [file path]                                       Prints the hexdump of a file (the hex information and translated to ASCII utf-8 )

--analyze-sniffed [file path] [output file name] [mode]     Prints the connections that have been made based on sniffing a .pcap file and its variants,

                                                            and also prints the number of requests between one IP and another, smth like:

                                                                192.168.0.1 <-> 192.168.0.4 85 requests X MB/s

                                                                192.168.0.2 <-> 192.168.0.5 66 requests X MB/s

                                                                192.168.0.3 <-> 192.168.0.6 2 requests X MB/s

                                                            if mode is 1 -> Outputs a map created in folium with the .html extension

                                                            if mode is 2-> Outputs an image

--analyze-log [file path]                                   It represents the ADB logcat logs of an Android device on a 3-dimensional coordinate axis.

                                                                X-axis: Unix time(ms)

                                                                Y-axis: PID

                                                                Z-axis: Importance (Info, warning, error and fatal)

                                                            Export the data using: adb logcat *:VIWEF > file.txt

--analyze-image [nº] [nombre del mapa a guardar.html]       nº = 1, Prints any possible editions in a image

                                                            nº = 2, Creates a .html map in which saves the geo-locations of the images

                                                            si nº = 3, Do both things

--trace-map [tracert path] [map file name]                  Shows the path of a icmp from a "tracert -4 -h 30 example.com > output.txt" command,

                                                                example.com: the path of the domain that you want to visualize

                                                                output.txt: The file name, this file has the output of the comand saved in it

                                                            if you dont write the [map file name], it would save the map in a file whose name is "tracert_map.html"

                                                                Note that the location of each point(node) of the visualized path is extracted by ipinfo.io, it uses IP GeoLocation.

--wav-analysis [wav file path]                              Shows the two-dimensional(

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
```
![image](https://github.com/user-attachments/assets/06744da0-e3d4-46df-bb50-6a6fe3da9d68)

### **Libraries imports**:
You can install all of this dependencies using
```
pip install -r requirements.txt
```
Look at the `requirements.txt` file for more details about the dependencies needed

The estimated size of all the files is around 100 MB.
#### **Be careful with:**
You shouldn't modify the`.zip` file because that's the module functions and its hard to repair it. So, you just need to modify and make changes in the `.py` file. The code is completely commented in Spanish, but i'll fix it as soon as possible

#### ***Help from the community:***
By the way, this repository is open to implement functions in the code (Like a new function, optimisation or something like that) by a **Pull Request**
