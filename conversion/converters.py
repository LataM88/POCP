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

    return output

def rgb_to_hsl(rgb_image):
    """Konwertuje obraz RGB (0-255) do HSL (H: 0-360, S: 0-1, L: 0-1)."""
    # Normalizacja do 0-1
    img = rgb_image.astype(float) / 255.0
    
    r = img[..., 0]
    g = img[..., 1]
    b = img[..., 2]
    
    max_c = np.max(img, axis=2)
    min_c = np.min(img, axis=2)
    delta = max_c - min_c
    
    L = (max_c + min_c) / 2.0
    
    S = np.zeros_like(L)
    # S = delta / (1 - |2L - 1|)  dla L != 0,1
    # Uważamy na dzielenie przez zero
    mask_l = (L > 0) & (L < 1)
    S[mask_l] = delta[mask_l] / (1 - np.abs(2 * L[mask_l] - 1))
    
    H = np.zeros_like(L)
    # H calculation
    mask_delta = delta > 0
    
    # r is max
    mask_r = mask_delta & (max_c == r)
    H[mask_r] = ((g[mask_r] - b[mask_r]) / delta[mask_r]) % 6
    
    # g is max
    mask_g = mask_delta & (max_c == g)
    H[mask_g] = ((b[mask_g] - r[mask_g]) / delta[mask_g]) + 2
    
    # b is max
    mask_b = mask_delta & (max_c == b)
    H[mask_b] = ((r[mask_b] - g[mask_b]) / delta[mask_b]) + 4
    
    H = H * 60.0
    H[H < 0] += 360.0
    
    return np.dstack((H, S, L))



def rgb_to_ycbcr(rgb_image):
    """Konwertuje RGB do YCbCr (standard JPEG/JFIF)."""
    # Y  =  0.299*R + 0.587*G + 0.114*B
    # Cb = -0.1687*R - 0.3313*G + 0.5*B + 128
    # Cr =  0.5*R - 0.4187*G - 0.0813*B + 128
    
    img = rgb_image.astype(float)
    R = img[..., 0]
    G = img[..., 1]
    B = img[..., 2]
    
    Y = 0.299 * R + 0.587 * G + 0.114 * B
    Cb = -0.168736 * R - 0.331264 * G + 0.5 * B + 128
    Cr = 0.5 * R - 0.418688 * G - 0.081312 * B + 128
    
    return np.dstack((Y, Cb, Cr))



def colorize_channel(channel_data, channel_type, grayscale=False):
    """
    Tworzy wizualizację kanału w kolorze lub skali szarości.
    """
    h, w = channel_data.shape

    # -- Special handling for conversion previews (raw Lab/XYZ/RGB) --
    if isinstance(channel_type, str) and channel_type.endswith('_rgb'):
        if channel_type == 'L_rgb':
            L = channel_data.copy()
            if L.max() <= 1.01: L = L * 100.0
            return lab_to_rgb(np.dstack((L, np.zeros_like(L), np.zeros_like(L))))
        return colorize_channel(channel_data, channel_type.replace('_rgb', ''), grayscale)

    norm = (channel_data - channel_data.min()) / (channel_data.max() - channel_data.min() + 1e-10)
    val = (norm * 255).astype(np.uint8)
    
    # Jeśli tryb szarości -> zwracamy po prostu intensywność
    if grayscale:
        return np.dstack((val, val, val))

    inv_val = 255 - val 
    output = np.zeros((h, w, 3), dtype=np.uint8)

    # --- PRZESTRZEŃ RGB (Decomposition) ---
    if channel_type == 'R':
        output[..., 0] = val
    elif channel_type == 'G':
        output[..., 1] = val
    elif channel_type == 'B':
        output[..., 2] = val
        
    # --- PRZESTRZEŃ XYZ ---
    elif channel_type == 'X':
        output[..., 0] = val
    elif channel_type == 'Y_XYZ': 
        output[..., 1] = val
    elif channel_type == 'Z': 
        output[..., 2] = val
        
    # --- PRZESTRZEŃ CMYK ---
    elif channel_type == 'C':
        output[..., 0] = inv_val; output[..., 1] = 255; output[..., 2] = 255
    elif channel_type == 'M':
        output[..., 0] = 255; output[..., 1] = inv_val; output[..., 2] = 255
    elif channel_type == 'Yellow':
        output[..., 0] = 255; output[..., 1] = 255; output[..., 2] = inv_val
    elif channel_type == 'K':
        output[..., 0] = inv_val; output[..., 1] = inv_val; output[..., 2] = inv_val

    # --- PRZESTRZEŃ LAB / LUV ---
    elif channel_type in ['L', 'L_hsl']: # Jasność - szary
        output[..., 0] = val; output[..., 1] = val; output[..., 2] = val
    
    elif channel_type == 'a': # Lab a* (Green-Red)
        output[..., 0] = (norm * 255).astype(np.uint8) 
        output[..., 1] = ((1 - norm) * 255).astype(np.uint8)
        output[..., 2] = 128
        
    elif channel_type == 'b': # Lab b* (Blue-Yellow)
        output[..., 0] = (norm * 255).astype(np.uint8)
        output[..., 1] = (norm * 255).astype(np.uint8) 
        output[..., 2] = ((1 - norm) * 255).astype(np.uint8)

    # --- PRZESTRZEŃ HSL ---
    elif channel_type == 'H': # Hue
        # Vectorized HSV->RGB for visualization
        h_ = norm * 6.0
        x = (1 - np.abs(h_ % 2 - 1))
        
        r_ = np.zeros_like(h_); g_ = np.zeros_like(h_); b_ = np.zeros_like(h_)
        
        mask = (h_ < 1); r_[mask]=1; g_[mask]=x[mask]
        mask = (h_ >= 1) & (h_ < 2); r_[mask]=x[mask]; g_[mask]=1
        mask = (h_ >= 2) & (h_ < 3); g_[mask]=1; b_[mask]=x[mask]
        mask = (h_ >= 3) & (h_ < 4); g_[mask]=x[mask]; b_[mask]=1
        mask = (h_ >= 4) & (h_ < 5); r_[mask]=x[mask]; b_[mask]=1
        mask = (h_ >= 5); r_[mask]=1; b_[mask]=x[mask]
        
        output[..., 0] = (r_ * 255).astype(np.uint8)
        output[..., 1] = (g_ * 255).astype(np.uint8)
        output[..., 2] = (b_ * 255).astype(np.uint8)

    elif channel_type == 'S': # Saturation
        # Standardowa wizualizacja nasycenia (skala szarości)
        output[..., 0] = val
        output[..., 1] = val
        output[..., 2] = val
        
    


    # --- PRZESTRZEŃ YCbCr ---
    elif channel_type == 'Y_ycbcr': # Luminancja - grayscale
        output[..., 0] = val; output[..., 1] = val; output[..., 2] = val

    elif channel_type == 'Cb': # (Blue-Yellowish difference)
        # Low Cb = Yellow/Green, High Cb = Blue
        # Approximation for visualization:
        # Map 0..255 Cb to Blue-Yellow
        output[..., 0] = ((1-norm) * 255).astype(np.uint8)
        output[..., 1] = ((1-norm) * 255).astype(np.uint8)
        output[..., 2] = (norm * 255).astype(np.uint8)

    elif channel_type == 'Cr': # (Red-Greenish difference)
        # Low Cr = Green/Cyan, High Cr = Red
        output[..., 0] = (norm * 255).astype(np.uint8)
        output[..., 1] = ((1-norm) * 255).astype(np.uint8)
        output[..., 2] = ((1-norm) * 255).astype(np.uint8)
        
    return output