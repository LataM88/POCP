import numpy as np
from conversion.color_utils import normalize_rgb, WHITE_POINT_D65

# Macierz transformacji sRGB → XYZ (punkt bieli D65)
SRGB_TO_XYZ_MATRIX = np.array([
    [0.41242, 0.35759, 0.18046],
    [0.21266, 0.71517, 0.07218],
    [0.01933, 0.11919, 0.95044]
])

def rgb_to_xyz(rgb_image):
    #Konwertuje obraz RGB (0-255) do przestrzeni kolorów CIE XYZ.
    rgb_linear = normalize_rgb(rgb_image)
    
    # Reshape dla mnożenia macierzowego
    h, w, _ = rgb_linear.shape
    rgb_reshaped = rgb_linear.reshape(-1, 3)
    
    # Transformacja macierzowa: XYZ = RGB * M^T
    xyz_reshaped = rgb_reshaped @ SRGB_TO_XYZ_MATRIX.T
    
    # Powrót do kształtu obrazu
    xyz_image = xyz_reshaped.reshape(h, w, 3)
    
    return xyz_image

def xyz_channels_to_display(xyz_image):
    #Konwertuje kanały XYZ do postaci wizualizacji (0-255).Normalizuje każdy kanał osobno dla lepszej widoczności.
    
    display_channels = []
    
    for i in range(3):
        channel = xyz_image[:, :, i]        #Normalizacja kanału do zakresu 0-255
        
        min_val = channel.min()
        max_val = channel.max()
        
        if max_val - min_val > 0:
            normalized = (channel - min_val) / (max_val - min_val) * 255
        else:
            normalized = np.zeros_like(channel)
        
        display_channels.append(normalized.astype(np.uint8))
    
    return display_channels
