import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import datetime # Potrzebne do generowania unikalnych nazw plików

from gui.display_area import DisplayArea
from gui.language_manager import LanguageManager
from conversion.converters import rgb_to_xyz, rgb_to_cmyk, colorize_channel
from image_processing.image_loader import load_image, array_to_pil, save_image

class MainWindow(tk.Tk):
    
    def __init__(self):
        super().__init__()
        
        self.lang = LanguageManager()
        self.title(self.lang.get('window_title'))
        self.geometry("1400x800")
        
        self.current_image = None
        self.current_image_path = None
        self.converted_channels = None
        
        # Zmienne do obsługi statusu (żeby działało tłumaczenie po zmianie języka)
        self.current_status_key = 'status_ready'
        self.current_status_params = {}
        
        self.images_folder = os.path.join(os.path.expanduser("~"), "Documents", "images")
        self.convert_folder = os.path.join(os.path.expanduser("~"), "Documents", "convert")
        
        os.makedirs(self.images_folder, exist_ok=True)
        os.makedirs(self.convert_folder, exist_ok=True)
        
        self.create_widgets()
    
    def create_widgets(self):
        control_frame = ttk.Frame(self, padding=10)
        control_frame.pack(side='top', fill='x')
        
        self.load_button = ttk.Button(control_frame, text=self.lang.get('load_button'), command=self.load_image)
        self.load_button.pack(side='left', padx=5)
        
        self.mode_var = tk.StringVar(value="XYZ")
        self.mode_combo = ttk.Combobox(control_frame, textvariable=self.mode_var, values=["XYZ", "CMYK"], state="readonly", width=10)
        self.mode_combo.pack(side='left', padx=5)
        
        self.convert_button = ttk.Button(control_frame, text=self.lang.get('convert_button'), command=self.convert_image)
        self.convert_button.pack(side='left', padx=5)
        
        self.save_button = ttk.Button(control_frame, text=self.lang.get('save_button'), command=self.save_results)
        self.save_button.pack(side='left', padx=5)
        
        self.lang_frame = ttk.LabelFrame(control_frame, text=self.lang.get('language_frame'), padding=5)
        self.lang_frame.pack(side='right', padx=5)
        
        self.flag_button = tk.Button(
            self.lang_frame,
            text=self.lang.get_flag_emoji() + " " + self.lang.current_language,
            font=('Arial', 12),
            command=self.toggle_language
        )
        self.flag_button.pack()
        
        self.status_label = ttk.Label(self, text=self.lang.get('status_ready'), foreground="green")
        self.status_label.pack(side='top', fill='x', padx=10)
        
        self.display_area = DisplayArea(self, self.lang)
        self.display_area.pack(side='top', fill='both', expand=True, padx=10, pady=10)
    
    def update_status(self, key, color="black", **kwargs):
        """
        Inteligentna aktualizacja statusu.
        Zapamiętuje klucz i parametry, żeby móc przetłumaczyć tekst przy zmianie języka.
        """
        self.current_status_key = key
        self.current_status_params = kwargs
        
        # Pobierz tekst w aktualnym języku
        text = self.lang.get(key, **kwargs)
        
        # Jeśli kluczem jest 'status_loaded', dodajemy nazwę pliku ręcznie, bo to specyficzny przypadek
        if key == 'status_loaded' and 'filename' in kwargs:
            text = f"{self.lang.get('status_loaded')} {kwargs['filename']}"
            
        self.status_label.config(text=text, foreground=color)

    def toggle_language(self):
        new_lang = 'EN' if self.lang.current_language == 'PL' else 'PL'
        self.lang.set_language(new_lang)
        self.refresh_ui()
    
    def refresh_ui(self):
        self.title(self.lang.get('window_title'))
        self.load_button.config(text=self.lang.get('load_button'))
        self.save_button.config(text=self.lang.get('save_button'))
        self.convert_button.config(text=self.lang.get('convert_button'))
        self.lang_frame.config(text=self.lang.get('language_frame'))
        self.flag_button.config(text=self.lang.get_flag_emoji() + " " + self.lang.current_language)
        
        # Odświeżamy status używając zapamiętanego klucza
        # Zachowujemy kolor (pobieramy go z obecnego labela)
        current_color = self.status_label.cget("foreground")
        self.update_status(self.current_status_key, color=current_color, **self.current_status_params)
        
        self.display_area.refresh_labels()
    
    def load_image(self):
        path = filedialog.askopenfilename()
        if not path: return
        
        try:
            self.current_image = load_image(path)
            self.current_image_path = path
            self.converted_channels = None
            
            pil_img = array_to_pil(self.current_image)
            self.display_area.show_preview(pil_img)
            
            # Używamy nowej metody update_status
            filename = os.path.basename(path)
            self.update_status('status_loaded', color="green", filename=filename)
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.update_status('status_error_load', color="red")

    def convert_image(self):
        if self.current_image is None:
            messagebox.showwarning(self.lang.get('dialog_warning'), self.lang.get('warning_no_image'))
            return
            
        mode = self.mode_var.get()
        pil_original = array_to_pil(self.current_image)
        
        self.update_status('status_converting', color="blue")
        self.update() # Wymuś odświeżenie GUI
        
        try:
            if mode == "XYZ":
                xyz = rgb_to_xyz(self.current_image)
                # Używamy 'Y_XYZ' dla luminancji (zielony)
                img_x = array_to_pil(colorize_channel(xyz[:,:,0], 'X'))
                img_y = array_to_pil(colorize_channel(xyz[:,:,1], 'Y_XYZ')) 
                img_z = array_to_pil(colorize_channel(xyz[:,:,2], 'Z'))
                
                self.converted_channels = {'X': img_x, 'Y': img_y, 'Z': img_z, 'RGB': pil_original}
                self.display_area.setup_layout_xyz(pil_original, img_x, img_y, img_z)
                
            elif mode == "CMYK":
                cmyk = rgb_to_cmyk(self.current_image)
                # Używamy 'Yellow' dla żółtego (żółty)
                img_c = array_to_pil(colorize_channel(cmyk[:,:,0], 'C'))
                img_m = array_to_pil(colorize_channel(cmyk[:,:,1], 'M'))
                img_y = array_to_pil(colorize_channel(cmyk[:,:,2], 'Yellow')) 
                img_k = array_to_pil(colorize_channel(cmyk[:,:,3], 'K'))
                
                self.converted_channels = {'C': img_c, 'M': img_m, 'Y': img_y, 'K': img_k, 'RGB': pil_original}
                self.display_area.setup_layout_cmyk(pil_original, img_c, img_m, img_y, img_k)

            self.update_status('status_converted', color="green")
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
            print(e)
            self.update_status('status_error_convert', color="red")

    def save_results(self):
        if not self.converted_channels:
            return
        
        base_name = os.path.splitext(os.path.basename(self.current_image_path))[0]
        
        # --- NOWOŚĆ: Dodajemy znacznik czasu do nazwy plików ---
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        # Np. nazwa pliku: image_X_20231027_153022.png
        
        saved_count = 0
        for name, img in self.converted_channels.items():
            if name == 'RGB': continue
            
            filename = f"{base_name}_{name}_{timestamp}.png"
            path = os.path.join(self.convert_folder, filename)
            img.save(path)
            saved_count += 1
            
        messagebox.showinfo(
            self.lang.get('dialog_success'), 
            self.lang.get('success_saved', count=saved_count, path=self.convert_folder, files="")
        )
        self.update_status('status_saved', color="green")