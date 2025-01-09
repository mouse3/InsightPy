def entropy(file_path : str):
    from math import log2
    from collections import Counter
    # Leer el archivo en modo binario
    with open(file_path, 'rb') as file:
        data = file.read()
    #Full mathematics here
    # Calculates the frecuency of each byte of the data 
    frecuency = Counter(data)
    
    # Calculates the probability of each byte 
    length = len(data)
    probabilities = [frec / length for frec in frecuency.values()]
    
    # Calculates the entropy using the Shannons' formula 
    entropie = -sum(p * log2(p) for p in probabilities)

    ###### Redundancy
    redundancy = 1 - entropie/(log2(255)) #255 possible symbols(on a byte)
    return entropie, redundancy