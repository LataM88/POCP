import numpy as np
from conversion.color_utils import normalize_rgb, WHITE_POINT_D65

# Macierz transformacji sRGB → XYZ (D65)
SRGB_TO_XYZ_MATRIX = np.array([
    [0.41242, 0.35759, 0.18046],
    [0.21266, 0.71517, 0.07218],
    [0.01933, 0.11919, 0.95044]
])

def rgb_to_xyz(rgb_image):
    """Konwertuje obraz RGB (0-255) do XYZ."""
    rgb_linear = normalize_rgb(rgb_image)
    h, w, _ = rgb_linear.shape
    rgb_reshaped = rgb_linear.reshape(-1, 3)
    xyz_reshaped = rgb_reshaped @ SRGB_TO_XYZ_MATRIX.T
    return xyz_reshaped.reshape(h, w, 3)

def rgb_to_cmyk(rgb_image):
    """Konwertuje obraz RGB (0-255) do CMYK (0-100)."""
    rgb = rgb_image.astype(float) / 255.0
    K = 1 - np.max(rgb, axis=2)
    C = (1 - rgb[..., 0] - K) / (1 - K + 1e-10)
    M = (1 - rgb[..., 1] - K) / (1 - K + 1e-10)
    Y = (1 - rgb[..., 2] - K) / (1 - K + 1e-10)
    cmyk = np.dstack((C, M, Y, K))
    return np.clip(cmyk, 0, 1)

def colorize_channel(channel_data, channel_type):
    """
    Tworzy wizualizację kanału w kolorze.
    channel_type: 'X', 'Y_XYZ', 'Z' (addytywne) lub 'C', 'M', 'Yellow', 'K' (substraktywne)
    """
    h, w = channel_data.shape
    norm = (channel_data - channel_data.min()) / (channel_data.max() - channel_data.min() + 1e-10)
    
    output = np.zeros((h, w, 3), dtype=np.uint8)
    val = (norm * 255).astype(np.uint8)
    inv_val = 255 - val 

    # --- PRZESTRZEŃ XYZ (Addytywna - świecenie) ---
    if channel_type == 'X': # Pseudo-Red
        output[..., 0] = val
    
    elif channel_type == 'Y_XYZ': # LUMINANCJA (XYZ) - To jest "jasność", oko widzi ją najbardziej jako zieleń
        output[..., 1] = val
        
    elif channel_type == 'Z': # Pseudo-Blue
        output[..., 2] = val
        
    # --- PRZESTRZEŃ CMYK (Substraktywna - tusz) ---
    elif channel_type == 'C': # Cyan
        output[..., 0] = inv_val
        output[..., 1] = 255
        output[..., 2] = 255
    elif channel_type == 'M': # Magenta
        output[..., 0] = 255
        output[..., 1] = inv_val
        output[..., 2] = 255
        
    # TUTAJA BYŁ BŁĄD: Wcześniej 'Y' łapało się wyżej jako Y_XYZ (zielony)
    elif channel_type == 'Yellow': # Żółty (CMYK)
        output[..., 0] = 255
        output[..., 1] = 255
        output[..., 2] = inv_val # B jest zabierane
        
    elif channel_type == 'K': # Black
        output[..., 0] = inv_val
        output[..., 1] = inv_val
        output[..., 2] = inv_val
        
    return output