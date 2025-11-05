from PIL import Image
import numpy as np

def load_image(file_path):
    img = Image.open(file_path)
    
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    return np.array(img)

def save_image(image_array, file_path):

    image_array = np.clip(image_array, 0, 255).astype(np.uint8)
    
    img = Image.fromarray(image_array)
    img.save(file_path)
    print(f"Zapisano: {file_path}")

def array_to_pil(image_array):
  
    image_array = np.clip(image_array, 0, 255).astype(np.uint8)
    
    return Image.fromarray(image_array)
