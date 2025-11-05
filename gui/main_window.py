import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image
import numpy as np
import os

from gui.display_area import DisplayArea
from gui.language_manager import LanguageManager
from conversion.rgb_to_xyz import rgb_to_xyz, xyz_channels_to_display
from image_processing.image_loader import load_image, array_to_pil, save_image

class MainWindow(tk.Tk):
    
    def __init__(self):
        super().__init__()
        
        self.lang = LanguageManager()
        self.title(self.lang.get('window_title'))
        self.geometry("1400x750")
        
        self.current_image = None
        self.current_image_path = None
        self.converted_channels = None
        
        self.images_folder = os.path.join(os.path.expanduser("~"), "Documents", "images")
        self.convert_folder = os.path.join(os.path.expanduser("~"), "Documents", "convert")
        
        os.makedirs(self.images_folder, exist_ok=True)
        os.makedirs(self.convert_folder, exist_ok=True)
        
        self.create_widgets()
    
    def create_widgets(self):
        
        # Górny panel kontrolny
        control_frame = ttk.Frame(self, padding=10)
        control_frame.pack(side='top', fill='x')
        
        # Przyciski
        self.load_button = ttk.Button(
            control_frame,
            text=self.lang.get('load_button'),
            command=self.load_image
        )
        self.load_button.pack(side='left', padx=5)
        
        self.save_button = ttk.Button(
            control_frame,
            text=self.lang.get('save_button'),
            command=self.save_results
        )
        self.save_button.pack(side='left', padx=5)
        
        self.convert_button = ttk.Button(
            control_frame,
            text=self.lang.get('convert_button'),
            command=self.convert_image
        )
        self.convert_button.pack(side='left', padx=5)
        
        # Przełącznik języka
        self.lang_frame = ttk.LabelFrame(
            control_frame, 
            text=self.lang.get('language_frame'), 
            padding=5
        )
        self.lang_frame.pack(side='right', padx=5)
        
        self.flag_button = tk.Button(
            self.lang_frame,
            text=self.lang.get_flag_emoji() + " " + self.lang.current_language,
            font=('Arial', 14),
            command=self.toggle_language,
            relief='raised',
            cursor='hand2'
        )
        self.flag_button.pack()
        
        # Status bar
        status_frame = ttk.Frame(self, padding=5)
        status_frame.pack(side='top', fill='x')
        
        self.status_label = ttk.Label(
            status_frame, 
            text=self.lang.get('status_ready'), 
            foreground="green"
        )
        self.status_label.pack(side='left', padx=10)
        
        # Obszar wyświetlania
        self.display_area = DisplayArea(self, self.lang)
        self.display_area.pack(side='top', fill='both', expand=True, padx=10, pady=10)
    
    def toggle_language(self):
        if self.lang.current_language == 'PL':
            self.lang.set_language('EN')
        else:
            self.lang.set_language('PL')
        
        self.refresh_ui()
    
    def refresh_ui(self):
        self.title(self.lang.get('window_title'))
        self.load_button.config(text=self.lang.get('load_button'))
        self.save_button.config(text=self.lang.get('save_button'))
        self.convert_button.config(text=self.lang.get('convert_button'))
        self.flag_button.config(
            text=self.lang.get_flag_emoji() + " " + self.lang.current_language
        )
        self.lang_frame.config(text=self.lang.get('language_frame'))
        self.status_label.config(text=self.lang.get('status_ready'))
        self.display_area.refresh_labels()
    
    def load_image(self):
        if not os.path.exists(self.images_folder):
            messagebox.showwarning(
                self.lang.get('dialog_warning'), 
                self.lang.get('warning_folder_not_exists', path=self.images_folder)
            )
            initial_dir = os.path.expanduser("~")
        else:
            initial_dir = self.images_folder
        
        file_path = filedialog.askopenfilename(
            title=self.lang.get('dialog_select_image'),
            initialdir=initial_dir,
            filetypes=[
                (self.lang.get('dialog_all_images'), "*.png *.jpg *.jpeg *.bmp *.tiff"),
                ("PNG", "*.png"),
                ("JPEG", "*.jpg *.jpeg"),
                ("BMP", "*.bmp"),
                (self.lang.get('dialog_all_files'), "*.*")
            ]
        )
        
        if not file_path:
            return
        
        try:
            self.current_image = load_image(file_path)
            self.current_image_path = file_path
            self.converted_channels = None
            
            pil_img = array_to_pil(self.current_image)
            self.display_area.update_panel('RGB', pil_img)
            
            for panel in ['X', 'Y', 'Z']:
                self.display_area.panels[panel].config(
                    image='', 
                    text=self.lang.get('waiting_panel')
                )
                self.display_area.panels[panel].image = None
            
            self.status_label.config(
                text=f"{self.lang.get('status_loaded')} {os.path.basename(file_path)}", 
                foreground="green"
            )
            
        except Exception as e:
            messagebox.showerror(
                self.lang.get('dialog_error'), 
                self.lang.get('error_load', error=str(e))
            )
            self.status_label.config(
                text=self.lang.get('status_error_load'), 
                foreground="red"
            )
    
    def convert_image(self):
        # Konwertuje załadowany obraz RGB na CIE XYZ
        if self.current_image is None:
            messagebox.showwarning(
                self.lang.get('dialog_warning'), 
                self.lang.get('warning_no_image')
            )
            self.status_label.config(
                text=self.lang.get('status_no_image'), 
                foreground="orange"
            )
            return
        
        try:
            self.status_label.config(
                text=self.lang.get('status_converting'), 
                foreground="blue"
            )
            self.update()
            
            # Konwersja RGB → XYZ
            xyz_image = rgb_to_xyz(self.current_image)
            channels = xyz_channels_to_display(xyz_image)
            
            self.converted_channels = {
                'X': channels[0],
                'Y': channels[1],
                'Z': channels[2]
            }
            
            panel_names = ['X', 'Y', 'Z']
            
            for panel, channel in zip(panel_names, channels):
                pil_img = array_to_pil(channel)
                self.display_area.update_panel(panel, pil_img)
            
            self.status_label.config(
                text=self.lang.get('status_converted'), 
                foreground="green"
            )
            
        except Exception as e:
            messagebox.showerror(
                self.lang.get('dialog_error'), 
                self.lang.get('error_convert', error=str(e))
            )
            self.status_label.config(
                text=self.lang.get('status_error_convert'), 
                foreground="red"
            )
    
    def save_results(self):
        """Zapisuje wyniki konwersji."""
        if self.converted_channels is None:
            messagebox.showwarning(
                self.lang.get('dialog_warning'), 
                self.lang.get('warning_no_conversion')
            )
            return
        
        if self.current_image_path is None:
            messagebox.showwarning(
                self.lang.get('dialog_warning'), 
                self.lang.get('warning_no_source')
            )
            return
        
        try:
            os.makedirs(self.convert_folder, exist_ok=True)
            
            base_name = os.path.splitext(os.path.basename(self.current_image_path))[0]
            saved_files = []
            
            # Zapisz kanały X, Y, Z
            for channel_name in ['X', 'Y', 'Z']:
                filename = f"{base_name}_{channel_name}.png"
                filepath = os.path.join(self.convert_folder, filename)
                save_image(self.converted_channels[channel_name], filepath)
                saved_files.append(filename)
            
            # Zapisz oryginalny RGB
            rgb_filename = f"{base_name}_RGB_original.png"
            rgb_filepath = os.path.join(self.convert_folder, rgb_filename)
            save_image(self.current_image, rgb_filepath)
            saved_files.append(rgb_filename)
            
            messagebox.showinfo(
                self.lang.get('dialog_success'), 
                self.lang.get('success_saved', 
                    count=len(saved_files),
                    path=self.convert_folder,
                    files="\n".join(saved_files)
                )
            )
            
            self.status_label.config(
                text=self.lang.get('status_saved'), 
                foreground="green"
            )
            
        except Exception as e:
            messagebox.showerror(
                self.lang.get('dialog_error'), 
                self.lang.get('error_save', error=str(e))
            )
            self.status_label.config(
                text=self.lang.get('status_error_save'), 
                foreground="red"
            )
