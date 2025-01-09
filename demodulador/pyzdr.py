import numpy as np
import matplotlib.pyplot as plt
import soundfile as sf
from scipy.io import wavfile
from scipy.signal import hilbert, find_peaks

class PSKSignalProcessor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.sample_rate = None
        self.signal = None
        self.duration = None
        self.channel_1 = None
        self.channel_2 = None

    def load_signal(self):
        data, self.sample_rate = sf.read(self.file_path)
        if len(data.shape) == 1:  # Mono signal
            data = np.stack((data, data), axis=-1)
        self.signal = data
        self.channel_1 = data[:, 0]
        self.channel_2 = data[:, 1]
        self.duration = len(data) / self.sample_rate

    def plot_waveform(self):
        time = np.linspace(0, self.duration, len(self.signal))
        plt.figure(figsize=(15, 6))
        plt.plot(time, self.channel_1, label='Channel 1')
        plt.plot(time, self.channel_2, label='Channel 2')
        plt.xlabel('Time [s]')
        plt.ylabel('Amplitude')
        plt.title('Waveform of the Signal')
        plt.legend()
        plt.grid()
        plt.show()

    def plot_fft(self):
        fft_data_1 = np.fft.fft(self.channel_1)
        fft_data_2 = np.fft.fft(self.channel_2)
        freqs = np.fft.fftfreq(len(self.signal), 1 / self.sample_rate)
        plt.figure(figsize=(15, 6))
        plt.plot(freqs, np.abs(fft_data_1), label='Channel 1')
        plt.plot(freqs, np.abs(fft_data_2), label='Channel 2')
        plt.xlabel('Frequency [Hz]')
        plt.ylabel('Magnitude')
        plt.title('FFT of the Signal')
        plt.legend()
        plt.grid()
        plt.show()

    def plot_spectrogram(self):
        plt.figure(figsize=(15, 6))
        plt.specgram(self.channel_1, NFFT=1024, Fs=self.sample_rate, noverlap=512, cmap='inferno')
        plt.title('Spectrogram - Channel 1')
        plt.xlabel('Time [s]')
        plt.ylabel('Frequency [Hz]')
        plt.colorbar(label='Intensity [dB]')
        plt.show()

    def process_psk(self, output_file):
        demodulator = PSKDemodulator(self.file_path, frecuencia_portadora=1000, tasa_de_símbolos=100)
        demodulator.procesar(output_file)

    def run(self, output_file):
        self.load_signal()
        self.plot_waveform()
        self.plot_fft()
        self.plot_spectrogram()
        self.process_psk(output_file)

class PSKDemodulator:
    def __init__(self, wav_file, frecuencia_portadora, tasa_de_símbolos):
        self.wav_file = wav_file
        self.frecuencia_portadora = frecuencia_portadora
        self.tasa_de_símbolos = tasa_de_símbolos
        self.tasa_de_muestreo = None
        self.señal = None
        self.coordenadas = None

    def cargar_señal(self):
        self.tasa_de_muestreo, self.señal = wavfile.read(self.wav_file)
        if len(self.señal.shape) > 1:
            self.señal = np.mean(self.señal, axis=1)

    def demodular(self):
        T_symbol = 1 / self.tasa_de_símbolos
        N_samples = int(self.tasa_de_muestreo * T_symbol)
        t = np.arange(N_samples) / self.tasa_de_muestreo

        señal_coseno = np.cos(2 * np.pi * self.frecuencia_portadora * t)
        señal_seno = np.sin(2 * np.pi * self.frecuencia_portadora * t)

        bloques = np.array_split(self.señal, len(self.señal) // N_samples)

        self.coordenadas = []
        for bloque in bloques:
            if len(bloque) < N_samples:
                continue

            I = np.sum(bloque * señal_coseno) / N_samples
            Q = np.sum(bloque * señal_seno) / N_samples

            simbolo_complejo = I + 1j * Q
            self.coordenadas.append(simbolo_complejo)

    @staticmethod
    def ideal_points_PSK(M):
        from numpy import pi, cos, sin
        return [cos((2 * pi * k) / M) + 1j * sin((2 * pi * k) / M) for k in range(M)]

    def calcular_errores_por_modulación(self):
        posibles_modulaciones = [1, 2, 4, 8, 16]
        errores_por_modulación = {}

        for M in posibles_modulaciones:
            puntos_ideales = self.ideal_points_PSK(M)
            error_acumulado = 0
            for z in self.coordenadas:
                distancias_cuadradas = [abs(z - z_0)**2 for z_0 in puntos_ideales]
                error_acumulado += min(distancias_cuadradas)

            errores_por_modulación[M] = error_acumulado

        return errores_por_modulación

    def asignar_bits(self, puntos_ideales, M):
        bits_por_símbolo = int(np.log2(M))
        mapa_bits = {p: format(i, f'0{bits_por_símbolo}b') for i, p in enumerate(puntos_ideales)}

        bits = []
        for z in self.coordenadas:
            punto_cercano = min(puntos_ideales, key=lambda z_0: abs(z - z_0))
            bits.extend(map(int, mapa_bits[punto_cercano]))
        return bits

    @staticmethod
    def guardar_bits(bits, archivo_salida):
        with open(archivo_salida, 'wb') as f:
            byte_array = bytearray(int(''.join(map(str, bits[i:i+8])), 2) for i in range(0, len(bits), 8))
            f.write(byte_array)

    def procesar(self, archivo_bin):
        self.cargar_señal()
        self.demodular()

        errores_por_modulación = self.calcular_errores_por_modulación()
        mejor_modulación = min(errores_por_modulación, key=errores_por_modulación.get)
        puntos_ideales = self.ideal_points_PSK(mejor_modulación)

        bits = self.asignar_bits(puntos_ideales, mejor_modulación)
        self.guardar_bits(bits, archivo_bin)

        print("Errores acumulados por modulación:")
        for M, error in errores_por_modulación.items():
            print(f"{M}-PSK: {error:.7f}")
        print(f"\nModulación detectada: {mejor_modulación}-PSK")
        print(f"Bits demodulados guardados en: {archivo_bin}")



"""
import sys

if len(sys.argv) < 2:
    print("Usage: python script.py [file_path]")
    sys.exit(1)

file_path = sys.argv[1]
output_file = file_path.replace('.wav', '_output.bin')

processor = PSKSignalProcessor(file_path)
processor.run(output_file)
"""
