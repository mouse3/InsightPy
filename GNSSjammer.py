import threading
import numpy as np
import hackrf
import random
import time
import matplotlib.pyplot as plt

class Main:
    def __init__(self):
        self.FRECUENCIAS = {
            "GPS": {"L1": 1575.42e6, "L2": 1227.60e6, "L5": 1176.45e6},
            "GLONASS": {"L1": 1602e6, "L2": 1246e6, "L3": 1246e6},
            "BeiDou": {"B1": 1561.098e6, "B2": 1207.140e6, "B3": 1268.52e6},
            "Galileo": {"E1": 1575.42e6, "E5a": 1176.45e6, "E5b": 1207.14e6, "E6": 1278.75e6},
        }

    def menu(self):
        while True:
            try:
                print("\nSeleccione una opción:")
                print("1: GPS Jammer")
                print("2: GLONASS Jammer")
                print("3: BeiDou Jammer")
                print("4: Galileo Jammer")
                print("5: Emitir todas las señales")
                print("6: Ver espectrograma de señal")
                print("7: Salir")
                entrada = int(input("Seleccione una opción: "))

                if entrada == 1:
                    self.GPSjammer()
                elif entrada == 2:
                    self.GLONASSjammer()
                elif entrada == 3:
                    self.BeiDoujammer()
                elif entrada == 4:
                    self.Galileojammer()
                elif entrada == 5:
                    self.All()
                elif entrada == 6:
                    self.plot_spectrogram()
                elif entrada == 7:
                    print("Saliendo del programa.")
                    break
                else:
                    print("Opción inválida. Intente nuevamente.")
            except ValueError:
                print("Entrada inválida. Por favor, ingrese un número.")
            except Exception as e:
                print(f"Error inesperado: {e}")

    def plot_spectrogram(self, frecuencia: float = 1575.42e6, duracion: float = 0.5, tasa_muestreo: float = 10e6):
        try:
            tiempo = np.arange(0, duracion, 1/tasa_muestreo)
            onda_senoidal = np.sin(2 * np.pi * frecuencia * tiempo)
            amplitudes_aleatorias = [random.uniform(0.1, 1.0) for _ in range(len(onda_senoidal))]
            onda_modulada = onda_senoidal * amplitudes_aleatorias

            plt.figure(figsize=(10, 6))
            plt.specgram(onda_modulada, NFFT=1024, Fs=tasa_muestreo, noverlap=512, scale='dB')
            plt.title(f"Espectrograma de la señal a {frecuencia / 1e6} MHz")
            plt.xlabel('Tiempo [s]')
            plt.ylabel('Frecuencia [Hz]')
            plt.colorbar(label='Intensidad [dB]')
            plt.show()
        except Exception as e:
            print(f"Error al generar el espectrograma: {e}")

    def All(self):
        hilos = []
        sistemas = ['GPS', 'GLONASS', 'BeiDou', 'Galileo']
        for sistema in sistemas:
            hilo = threading.Thread(target=self.transmitir_frecuencias, args=(sistema,))
            hilos.append(hilo)
            hilo.start()
        for hilo in hilos:
            hilo.join()
        print("Transmisión de todas las señales finalizada.")

    def transmitir_frecuencias(self, sistema: str):
        try:
            for frecuencia in self.FRECUENCIAS[sistema].values():
                self.transmitir_senal(frecuencia)
        except Exception as e:
            print(f"Error transmitiendo frecuencias para {sistema}: {e}")

    def transmitir_senal(self, frecuencia: float, duracion: float = 0.5, tasa_muestreo: float = 10e6, frecuencia_hackrf: float = 900000000, ganancia: int = 20):
        try:
            dev = hackrf.HackRF()
            dev.setup()
            dev.set_freq(frecuencia_hackrf)
            dev.set_sample_rate(tasa_muestreo)
            dev.set_lna_gain(16)
            dev.set_vga_gain(ganancia)

            tiempo = np.arange(0, duracion, 1/tasa_muestreo)
            onda_senoidal = np.sin(2 * np.pi * frecuencia * tiempo)
            amplitudes_aleatorias = [random.uniform(0.1, 1.0) for _ in range(len(onda_senoidal))]
            onda_modulada = onda_senoidal * amplitudes_aleatorias
            onda_final = np.int8(onda_modulada * 127 + 128)

            dev.start_tx(onda_final)
            print(f"Transmisión de la frecuencia {frecuencia} Hz finalizada.")
        except KeyboardInterrupt:
            print("Transmisión interrumpida por el usuario.")
        except Exception as e:
            print(f"Error en la transmisión de la frecuencia {frecuencia}: {e}")
        finally:
            try:
                dev.stop_tx()
                dev.close()
            except:
                pass

    def GPSjammer(self):
        self.transmitir_frecuencias('GPS')

    def GLONASSjammer(self):
        self.transmitir_frecuencias('GLONASS')

    def BeiDoujammer(self):
        self.transmitir_frecuencias('BeiDou')

    def Galileojammer(self):
        self.transmitir_frecuencias('Galileo')

if __name__ == "__main__":
    objeto = Main()
    objeto.menu()
