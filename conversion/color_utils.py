import numpy as np

# Stałe dla przestrzeni sRGB i punktu bieli D65
WHITE_POINT_D65 = np.array([0.9505, 1.0000, 1.0891])

def gamma_correction(channel, gamma=2.2):
    
    #Korekcja gamma dla kanału RGB (0-255 → 0.0-1.0). Return wartosc po korekcji gamma zakres 0.0-1.0
    normalized = channel / 255.0
    return np.power(normalized, gamma)

def normalize_rgb(rgb_image):
    
    # Normalizacja i korekcja gamma, arg array z wartosciami 0-255, zwraca 0.0-1.0 po korekcji gamma
    return gamma_correction(rgb_image.astype(np.float64))
