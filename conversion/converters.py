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

def xyz_to_lab(xyz_image):
    """Konwertuje obraz XYZ do CIE L*a*b."""
    # Normalizujemy względem białego punktu D65
    xyz_norm = xyz_image / WHITE_POINT_D65
    
    # Funkcja f(t) dla Lab
    delta = 6/29  # ~0.206
    delta_sq = delta ** 2
    delta_cubed = delta ** 3
    
    def f_func(t):
        result = np.zeros_like(t)
        mask1 = t > delta_cubed
        mask2 = ~mask1
        result[mask1] = np.cbrt(t[mask1])
        result[mask2] = t[mask2] / (3 * delta_sq) + 4/29
        return result
    
    f_xyz = f_func(xyz_norm)
    
    # Obliczamy L*, a*, b*
    L = 116 * f_xyz[:,:,1] - 16
    a = 500 * (f_xyz[:,:,0] - f_xyz[:,:,1])
    b = 200 * (f_xyz[:,:,1] - f_xyz[:,:,2])
    
    lab = np.dstack((L, a, b))
    return lab

def rgb_to_lab(rgb_image):
    """Konwertuje obraz RGB (0-255) bezpośrednio do CIE L*a*b."""
    xyz = rgb_to_xyz(rgb_image)
    return xyz_to_lab(xyz)


def lab_to_xyz(lab_image):
    """Konwertuje obraz CIE L*a*b do XYZ (zakłada punkt bieli D65).
    lab_image: HxWx3 (L in [0,100], a and b in their usual ranges)
    """
    L = lab_image[:, :, 0]
    a = lab_image[:, :, 1]
    b = lab_image[:, :, 2]

    # Odwrotność funkcji f
    fy = (L + 16.0) / 116.0
    fx = fy + (a / 500.0)
    fz = fy - (b / 200.0)

    delta = 6.0 / 29.0
    delta_cubed = delta ** 3

    def inv_f(f):
        result = np.zeros_like(f)
        mask = f > delta
        # dla f > delta: t = f^3
        result[mask] = f[mask] ** 3
        # dla f <= delta: t = 3*delta^2*(f - 4/29)
        result[~mask] = 3 * (delta ** 2) * (f[~mask] - 4.0 / 29.0)
        return result

    xr = inv_f(fx)
    yr = inv_f(fy)
    zr = inv_f(fz)

    # Pomnóż przez punkt bieli
    X = xr * WHITE_POINT_D65[0]
    Y = yr * WHITE_POINT_D65[1]
    Z = zr * WHITE_POINT_D65[2]

    return np.dstack((X, Y, Z))


def xyz_to_rgb(xyz_image):
    """Konwertuje obraz XYZ do sRGB (0-255) z klipowaniem i odwrotną kompresją gamma.
    Zakładamy punkt bieli D65 i macierz SRGB_TO_XYZ_MATRIX używaną wyżej.
    """
    # Odwróć macierz konwersji (XYZ -> linear RGB)
    M_inv = np.linalg.inv(SRGB_TO_XYZ_MATRIX)
    h, w, _ = xyz_image.shape
    xyz_reshaped = xyz_image.reshape(-1, 3)
    rgb_linear = xyz_reshaped @ M_inv.T

    # Kompresja sRGB (linear -> srgb)
    def linear_to_srgb(chan):
        a = 0.055
        threshold = 0.0031308
        srgb = np.where(chan <= threshold, 12.92 * chan, (1 + a) * np.power(np.clip(chan, 0, None), 1.0 / 2.4) - a)
        return srgb

    srgb = linear_to_srgb(rgb_linear)
    srgb = np.clip(srgb, 0.0, 1.0)
    srgb8 = (srgb.reshape(h, w, 3) * 255.0).astype(np.uint8)
    return srgb8


def lab_to_rgb(lab_image):
    """Konwertuje obraz Lab (L in 0..100) do uint8 RGB 0-255."""
    xyz = lab_to_xyz(lab_image)
    return xyz_to_rgb(xyz)

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
                  lub 'L', 'a', 'b' (Lab)
    """
    h, w = channel_data.shape

    # --- RZECZYWISTA WIZUALIZACJA LAB → RGB ---
    # Jeśli prosimy o '*_rgb', to traktujemy channel_data jako wartości Lab (surowe)
    # i konstruujemy obraz Lab, po czym konwertujemy go prawidłowo do sRGB.
    if isinstance(channel_type, str) and channel_type.endswith('_rgb'):
        # Nie stosujemy normalizacji tutaj - oczekujemy wartości w skali Lab
        if channel_type == 'L_rgb':
            L = channel_data.astype(np.float64)
            # Dopasuj skalę jeśli L w 0..1
            if L.max() <= 1.01:
                L = L * 100.0
            lab_img = np.dstack((L, np.zeros_like(L), np.zeros_like(L)))
            return lab_to_rgb(lab_img)

        if channel_type == 'a_rgb':
            a = channel_data.astype(np.float64)
            # Jeśli dane są znormalizowane 0..1 -> mapuj na [-128,128]
            if a.max() <= 1.01 and a.min() >= -1e-9:
                a = (a - 0.5) * 2.0 * 128.0
            L = np.full_like(a, 50.0)
            b = np.zeros_like(a)
            lab_img = np.dstack((L, a, b))
            return lab_to_rgb(lab_img)

        if channel_type == 'b_rgb':
            b = channel_data.astype(np.float64)
            if b.max() <= 1.01 and b.min() >= -1e-9:
                b = (b - 0.5) * 2.0 * 128.0
            L = np.full_like(b, 50.0)
            a = np.zeros_like(b)
            lab_img = np.dstack((L, a, b))
            return lab_to_rgb(lab_img)

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

    # --- PRZESTRZEŃ LAB (Perceptualna) ---
    elif channel_type == 'L': # Lightness (jasność) - wyświetlamy jako szarość
        output[..., 0] = val
        output[..., 1] = val
        output[..., 2] = val
    
    elif channel_type == 'a': # a* (zielony←→czerwony) - negatywne=zielony, pozytywne=czerwony
        # Normalizujemy tak, że środek (128) = 0
        # Wartości < 128 = zielony, > 128 = czerwony
        output[..., 0] = (norm * 255).astype(np.uint8)  # czerwony
        output[..., 1] = ((1 - norm) * 255).astype(np.uint8)  # Zielony
        output[..., 2] = 128  # Neutralnie
    
    elif channel_type == 'b': # b* (niebieski←→żółty) - negatywne=niebieski, pozytywne=żółty
        # Wartości < 128 = niebieski, > 128 = żółty
        output[..., 0] = (norm * 255).astype(np.uint8)  # Żółty
        output[..., 1] = (norm * 255).astype(np.uint8)  # Żółty
        output[..., 2] = ((1 - norm) * 255).astype(np.uint8)  # Niebieski
        
    return output