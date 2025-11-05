import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

class DisplayArea(ttk.Frame):
    
    def __init__(self, parent, language_manager):
        super().__init__(parent)
        self.lang = language_manager
        self.panels = {}
        self.panel_frames = {}
        self.create_display_panels()
    
    def create_display_panels(self):
        
        panel_keys = ['RGB', 'X', 'Y', 'Z']
        panel_labels = [
            self.lang.get('original_panel'),
            'X',
            'Y',
            'Z'
        ]
        
        for i, (key, label) in enumerate(zip(panel_keys, panel_labels)):
            frame = ttk.LabelFrame(self, text=label, padding=10)
            frame.grid(row=0, column=i, padx=5, pady=5, sticky='nsew')
            
            img_label = tk.Label(
                frame, 
                bg='white', 
                width=30, 
                height=20, 
                text=self.lang.get('empty_panel')
            )
            img_label.pack(expand=True, fill='both')
            
            self.panels[key] = img_label
            self.panel_frames[key] = frame
        
        for i in range(4):
            self.columnconfigure(i, weight=1)
        self.rowconfigure(0, weight=1)
    
    def refresh_labels(self):
        self.panel_frames['RGB'].config(text=self.lang.get('original_panel'))
    
    def update_panel(self, panel_name, pil_image):
        if panel_name not in self.panels:
            return
        
        img_copy = pil_image.copy()
        img_copy.thumbnail((300, 300), Image.Resampling.LANCZOS)
        
        photo = ImageTk.PhotoImage(img_copy)
        
        self.panels[panel_name].config(image=photo, text='')
        self.panels[panel_name].image = photo
    
    def clear_panels(self):
        for label in self.panels.values():
            label.config(image='', text=self.lang.get('empty_panel'))
            label.image = None
