import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import datetime # Potrzebne do generowania unikalnych nazw plików

from gui.display_area import DisplayArea
from gui.language_manager import LanguageManager
from conversion.converters import rgb_to_xyz, rgb_to_cmyk, rgb_to_lab, rgb_to_hsl, rgb_to_ycbcr, colorize_channel
from image_processing.image_loader import load_image, array_to_pil, save_image

class MainWindow(tk.Tk):
    
    def __init__(self):
        super().__init__()
        
        self.lang = LanguageManager()
        self.title(self.lang.get('window_title'))
        # Maksymalizacja okna dla lepszej widoczności przy dużym skalowaniu (np. 225%)
        self.state('zoomed') 
        
        self.current_image = None
        self.current_image_path = None
        
        # Przechowuje gotowe obrazy PIL do wyświetlenia/zapisu (np. pokolorowane lub szare)
        self.converted_channels = None
        
        # Przechowuje SUROWE dane kanałów (numpy arrays) do ponownego generowania widoku
        # Format: {'mode': 'CMYK', 'channels': {'C': array, 'M': array...}, 'rgb': array}
        self.raw_converted_data = None
        
        # Zmienne do obsługi statusu (żeby działało tłumaczenie po zmianie języka)
        self.current_status_key = 'status_ready'
        self.current_status_params = {}
        
        # Ustalanie ścieżek względem głównego folderu projektu (gdzie jest main.py)
        # gui/main_window.py -> gui/ -> .. (project root)
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        self.images_folder = os.path.join(project_root, "zdjecia")
        self.convert_folder = os.path.join(project_root, "zapisane")
        
        os.makedirs(self.images_folder, exist_ok=True)
        os.makedirs(self.convert_folder, exist_ok=True)
        
        self.create_widgets()
    
    def create_widgets(self):
        control_frame = ttk.Frame(self, padding=10)
        control_frame.pack(side='top', fill='x')
        
        self.load_button = ttk.Button(control_frame, text=self.lang.get('load_button'), command=self.load_image)
        self.load_button.pack(side='left', padx=5)
        
        self.mode_var = tk.StringVar(value="XYZ")
        # Zmiana: Przywrócenie XYZ/LUV
        self.mode_combo = ttk.Combobox(control_frame, textvariable=self.mode_var, values=["XYZ", "CMYK", "LAB", "HSL", "YCbCr"], state="readonly", width=10)
        self.mode_combo.pack(side='left', padx=5)
        
        # Checkbox dla trybu szarości
        self.grayscale_var = tk.BooleanVar(value=False)
        self.grayscale_check = ttk.Checkbutton(control_frame, text=self.lang.get('grayscale_view'), variable=self.grayscale_var, command=self.update_view_mode)
        self.grayscale_check.pack(side='left', padx=5)
        
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
        self.grayscale_check.config(text=self.lang.get('grayscale_view')) # Update text
        self.lang_frame.config(text=self.lang.get('language_frame'))
        self.flag_button.config(text=self.lang.get_flag_emoji() + " " + self.lang.current_language)
        
        # Odświeżamy status używając zapamiętanego klucza
        # Zachowujemy kolor (pobieramy go z obecnego labela)
        current_color = self.status_label.cget("foreground")
        self.update_status(self.current_status_key, color=current_color, **self.current_status_params)
        
        self.display_area.refresh_labels()
    
    def load_image(self):
        path = filedialog.askopenfilename(initialdir=self.images_folder)
        if not path: return
        
        try:
            self.current_image = load_image(path)
            self.current_image_path = path
            self.converted_channels = None
            self.raw_converted_data = None # Reset raw data
            
            pil_img = array_to_pil(self.current_image)
            self.display_area.show_preview(pil_img)
            
            # Używamy nowej metody update_status
            filename = os.path.basename(path)
            self.update_status('status_loaded', color="green", filename=filename)
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.update_status('status_error_load', color="red")

    def update_view_mode(self):
        """Callback dla checkboxa Grayscale - odświeża widok bez ponownej konwersji."""
        if self.raw_converted_data:
            self.refresh_display_images()

    def convert_image(self):
        if self.current_image is None:
            messagebox.showwarning(self.lang.get('dialog_warning'), self.lang.get('warning_no_image'))
            return
            
        mode = self.mode_var.get()
        pil_original = array_to_pil(self.current_image)
        
        self.update_status('status_converting', color="blue")
        self.update() # Wymuś odświeżenie GUI
        
        try:
            # 1. Konwersja matematyczna
            raw_channels = {}
            
            if mode == "XYZ":
                xyz = rgb_to_xyz(self.current_image)
                raw_channels = {'X': xyz[:,:,0], 'Y': xyz[:,:,1], 'Z': xyz[:,:,2]}
                
            elif mode == "CMYK":
                cmyk = rgb_to_cmyk(self.current_image)
                raw_channels = {'C': cmyk[:,:,0], 'M': cmyk[:,:,1], 'Y': cmyk[:,:,2], 'K': cmyk[:,:,3]}
            
            elif mode == "LAB":
                lab = rgb_to_lab(self.current_image)
                raw_channels = {'L': lab[:,:,0], 'a': lab[:,:,1], 'b': lab[:,:,2]}

            elif mode == "HSL":
                hsl = rgb_to_hsl(self.current_image)
                raw_channels = {'H': hsl[:,:,0], 'S': hsl[:,:,1], 'L': hsl[:,:,2]}



            elif mode == "YCbCr":
                ycbcr = rgb_to_ycbcr(self.current_image)
                raw_channels = {'Y': ycbcr[:,:,0], 'Cb': ycbcr[:,:,1], 'Cr': ycbcr[:,:,2]}

            # Zapisz dane surowe, żeby móc przełączać widok
            self.raw_converted_data = {
                'mode': mode,
                'channels': raw_channels,
                'rgb': self.current_image
            }
            
            # 2. Generowanie obrazków i wyświetlanie
            self.refresh_display_images()

            self.update_status('status_converted', color="green")
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
            import traceback
            traceback.print_exc()
            self.update_status('status_error_convert', color="red")

    def refresh_display_images(self):
        """Generuje obrazy PIL na podstawie raw_converted_data i aktualnych ustawień (np. grayscale)."""
        if not self.raw_converted_data:
            return

        mode = self.raw_converted_data['mode']
        channels_data = self.raw_converted_data['channels']
        original_rgb = self.raw_converted_data['rgb']
        
        is_grayscale = self.grayscale_var.get()
        
        pil_original = array_to_pil(original_rgb)
        pil_channels = {}
        
        # Helper map
        channel_type_map = {
            'X': 'X', 'Y': 'Y_XYZ', 'Z': 'Z',
            'C': 'C', 'M': 'M',  'K': 'K', # Yellow handled below
            'L': 'L', 'a': 'a', 'b': 'b',
            'H': 'H', 'S': 'S',
            'Y_ycbcr': 'Y_ycbcr', 'Cb': 'Cb', 'Cr': 'Cr'
        }
        
        generated_imgs = {}
        
        for key, data in channels_data.items():
            ctype = key
            
            # Special handling for ambiguous keys
            if mode == 'CMYK' and key == 'Y': ctype = 'Yellow'
            elif mode == 'XYZ' and key == 'Y': ctype = 'Y_XYZ'
            elif mode == 'YCbCr' and key == 'Y': ctype = 'Y_ycbcr'
            elif mode == 'HSL' and key == 'L': ctype = 'L_hsl'
            elif key in channel_type_map: ctype = channel_type_map[key]
            
            res_array = colorize_channel(data, ctype, grayscale=is_grayscale)
            generated_imgs[key] = array_to_pil(res_array)
        
        self.converted_channels = generated_imgs
        self.converted_channels['RGB'] = pil_original
        
        # Wywołanie layoutu
        if mode == "XYZ":
             self.display_area.setup_layout_xyz(pil_original, generated_imgs['X'], generated_imgs['Y'], generated_imgs['Z'])
        elif mode == "CMYK":
            self.display_area.setup_layout_cmyk(pil_original, generated_imgs['C'], generated_imgs['M'], generated_imgs['Y'], generated_imgs['K'])
        elif mode == "LAB":
            self.display_area.setup_layout_lab(pil_original, generated_imgs['L'], generated_imgs['a'], generated_imgs['b'])
        elif mode == "HSL":
            self.display_area.setup_layout_hsl(pil_original, generated_imgs['H'], generated_imgs['S'], generated_imgs['L'])

        elif mode == "YCbCr":
            self.display_area.setup_layout_ycbcr(pil_original, generated_imgs['Y'], generated_imgs['Cb'], generated_imgs['Cr'])

    def save_results(self):
        if not self.converted_channels:
            return
        
        base_name = os.path.splitext(os.path.basename(self.current_image_path))[0]
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        saved_count = 0
        for name, img in self.converted_channels.items():
            if name == 'RGB': continue
            
            # Add '_gray' suffix if in grayscale mode
            suffix = ""
            if self.grayscale_var.get():
                suffix = "_gray"
                
            filename = f"{base_name}_{name}{suffix}_{timestamp}.png"
            path = os.path.join(self.convert_folder, filename)
            img.save(path)
            saved_count += 1
            
        messagebox.showinfo(
            self.lang.get('dialog_success'), 
            self.lang.get('success_saved', count=saved_count, path=self.convert_folder, files="")
        )
        self.update_status('status_saved', color="green")