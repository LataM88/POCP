import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

class DisplayArea(ttk.Frame):
    
    def __init__(self, parent, language_manager):
        super().__init__(parent)
        self.lang = language_manager
        self.panels = {}       
        self.panel_frames = {} 
        self.status_placeholder = None
        
        self.setup_empty()

    def clear_widgets(self):
        """Usuwa wszystkie elementy z obszaru wyświetlania."""
        for widget in self.winfo_children():
            widget.destroy()
        self.panels.clear()
        self.panel_frames.clear()
        self.status_placeholder = None

    def setup_empty(self):
        self.clear_widgets()
        self.status_placeholder = ttk.Label(
            self, 
            text=self.lang.get('status_ready'),
            font=('Arial', 12)
        )
        self.status_placeholder.pack(expand=True)

    def show_preview(self, pil_image):
        self.clear_widgets()
        
        frame = ttk.LabelFrame(self, text=self.lang.get('original_panel'), padding=5)
        frame.pack(expand=True, fill='both', padx=50, pady=50)
        
        img_label = tk.Label(frame, bg='#f0f0f0')
        img_label.pack(expand=True, fill='both')
        
        self.panels['RGB'] = img_label
        self.panel_frames['RGB'] = {'frame': frame, 'title_key': 'original_panel'}
        
        self._update_image('RGB', pil_image)

    def create_panel(self, parent, key, title_key, row, col, rowspan=1, columnspan=1):
        title = self.lang.get(title_key)
        frame = ttk.LabelFrame(parent, text=title, padding=5)
        frame.grid(row=row, column=col, rowspan=rowspan, columnspan=columnspan, 
                   padx=5, pady=5, sticky='nsew')
        
        img_label = tk.Label(frame, bg='#f0f0f0', text=self.lang.get('empty_panel'))
        img_label.pack(expand=True, fill='both')
        
        self.panels[key] = img_label
        self.panel_frames[key] = {'frame': frame, 'title_key': title_key}
        return img_label

    def setup_layout_xyz(self, original_img, x_img, y_img, z_img):
        """Układ dla XYZ: Idealnie równa siatka 2x2."""
        self.clear_widgets()
        self.update_idletasks() # Ważne: przelicz wymiary okna przed rysowaniem
        
        # Obliczamy jeden wspólny rozmiar dla wszystkich 4 ćwiartek
        # Dzielimy szerokość/wysokość okna na 2 i odejmujemy marginesy
        win_w = self.winfo_width()
        win_h = self.winfo_height()
        if win_w < 100: win_w = 800 # Zabezpieczenie
        if win_h < 100: win_h = 600
        
        target_size = (win_w // 2 - 30, win_h // 2 - 40)

        # Ustawiamy "uniform", żeby kolumny były sztywno równe
        self.columnconfigure(0, weight=1, uniform='xyz_cols')
        self.columnconfigure(1, weight=1, uniform='xyz_cols')
        self.rowconfigure(0, weight=1, uniform='xyz_rows')
        self.rowconfigure(1, weight=1, uniform='xyz_rows')
        
        self.create_panel(self, 'RGB', 'original_panel', 0, 0)
        self.create_panel(self, 'X', 'ch_x', 0, 1)
        self.create_panel(self, 'Y', 'ch_y', 1, 0)
        self.create_panel(self, 'Z', 'ch_z', 1, 1)
        
        # Przekazujemy explicit_size, żeby wszystkie miały ten sam wymiar
        self._update_image('RGB', original_img, explicit_size=target_size)
        self._update_image('X', x_img, explicit_size=target_size)
        self._update_image('Y', y_img, explicit_size=target_size)
        self._update_image('Z', z_img, explicit_size=target_size)

    def setup_layout_cmyk(self, original_img, c_img, m_img, y_img, k_img):
        """Układ dla CMYK: Lewa (duża) + Prawa (4 małe równe)."""
        self.clear_widgets()
        self.update_idletasks()
        
        win_w = self.winfo_width()
        win_h = self.winfo_height()
        if win_w < 100: win_w = 1000
        if win_h < 100: win_h = 600

        # Kontenery
        left_container = ttk.Frame(self)
        left_container.pack(side='left', fill='both', expand=True, padx=5)
        
        right_container = ttk.Frame(self)
        right_container.pack(side='right', fill='both', expand=True, padx=5)
        
        # --- LEWA STRONA (RGB) ---
        rgb_frame = ttk.LabelFrame(left_container, text=self.lang.get('original_panel'), padding=5)
        rgb_frame.pack(fill='both', expand=True, padx=5, pady=5)
        rgb_label = tk.Label(rgb_frame, bg='#f0f0f0')
        rgb_label.pack(fill='both', expand=True)
        
        self.panels['RGB'] = rgb_label
        self.panel_frames['RGB'] = {'frame': rgb_frame, 'title_key': 'original_panel'}
        
        # Rozmiar dla dużego po lewej
        left_size = (win_w // 2 - 40, win_h - 60)
        self._update_image('RGB', original_img, explicit_size=left_size)

        # --- PRAWA STRONA (CMYK - Siatka 2x2) ---
        # Wymuszamy równość kolumn i wierszy
        right_container.columnconfigure(0, weight=1, uniform='cmyk_cols')
        right_container.columnconfigure(1, weight=1, uniform='cmyk_cols')
        right_container.rowconfigure(0, weight=1, uniform='cmyk_rows')
        right_container.rowconfigure(1, weight=1, uniform='cmyk_rows')
        
        self.create_panel(right_container, 'C', 'ch_cyan', 0, 0)
        self.create_panel(right_container, 'M', 'ch_magenta', 0, 1)
        self.create_panel(right_container, 'Y', 'ch_yellow', 1, 0)
        self.create_panel(right_container, 'K', 'ch_black', 1, 1)
        
        # Obliczamy rozmiar dla małych kafelków (połowa prawej strony)
        small_w = (win_w // 2) // 2 - 30
        small_h = (win_h) // 2 - 40
        small_size = (small_w, small_h)

        self._update_image('C', c_img, explicit_size=small_size)
        self._update_image('M', m_img, explicit_size=small_size)
        self._update_image('Y', y_img, explicit_size=small_size)
        self._update_image('K', k_img, explicit_size=small_size)

    def _update_image(self, key, pil_image, explicit_size=None):
        """
        Aktualizuje obraz w panelu.
        explicit_size: (width, height) - jeśli podane, wymusza konkretny rozmiar,
        zamiast zgadywać na podstawie wielkości widgetu.
        """
        if key not in self.panels: return
        
        if explicit_size:
            target_w, target_h = explicit_size
        else:
            # Fallback do starej metody (dla podglądu/preview)
            self.update_idletasks()
            target_w = self.panels[key].winfo_width()
            target_h = self.panels[key].winfo_height()
            if target_w < 50: target_w = 300
            if target_h < 50: target_h = 300
        
        # Upewniamy się, że wartości są dodatnie
        target_w = max(50, int(target_w))
        target_h = max(50, int(target_h))

        img_copy = pil_image.copy()
        
        # Używamy thumbnail, który zachowuje proporcje
        img_copy.thumbnail((target_w, target_h), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(img_copy)
        
        self.panels[key].config(image=photo, text='')
        self.panels[key].image = photo

    def refresh_labels(self):
        if self.status_placeholder and self.status_placeholder.winfo_exists():
            self.status_placeholder.config(text=self.lang.get('status_ready'))
            
        for key, data in self.panel_frames.items():
            new_text = self.lang.get(data['title_key'])
            data['frame'].config(text=new_text)

    def setup_layout_lab(self, original_img, l_img, a_img, b_img):
        """Układ dla LAB: Idealnie równa siatka 2x2."""
        self.clear_widgets()
        self.update_idletasks()
        
        # Obliczamy jeden wspólny rozmiar dla wszystkich 4 ćwiartek
        win_w = self.winfo_width()
        win_h = self.winfo_height()
        if win_w < 100: win_w = 800
        if win_h < 100: win_h = 600
        
        target_size = (win_w // 2 - 30, win_h // 2 - 40)

        # Ustawiamy "uniform", żeby kolumny były sztywno równe
        self.columnconfigure(0, weight=1, uniform='lab_cols')
        self.columnconfigure(1, weight=1, uniform='lab_cols')
        self.rowconfigure(0, weight=1, uniform='lab_rows')
        self.rowconfigure(1, weight=1, uniform='lab_rows')
        
        self.create_panel(self, 'RGB', 'original_panel', 0, 0)
        self.create_panel(self, 'L', 'ch_l', 0, 1)
        self.create_panel(self, 'a', 'ch_a', 1, 0)
        self.create_panel(self, 'b', 'ch_b', 1, 1)
        
        self._update_image('RGB', original_img, explicit_size=target_size)
        self._update_image('L', l_img, explicit_size=target_size)
        self._update_image('a', a_img, explicit_size=target_size)
        self._update_image('b', b_img, explicit_size=target_size)

    def setup_layout_hsl(self, original_img, h_img, s_img, l_img):
        """Układ dla HSL: Siatka 2x2."""
        self.clear_widgets()
        self.update_idletasks()
        
        win_w = self.winfo_width(); win_h = self.winfo_height()
        if win_w < 100: win_w = 800
        if win_h < 100: win_h = 600
        target_size = (win_w // 2 - 30, win_h // 2 - 40)

        self.columnconfigure(0, weight=1, uniform='hsl_cols')
        self.columnconfigure(1, weight=1, uniform='hsl_cols')
        self.rowconfigure(0, weight=1, uniform='hsl_rows')
        self.rowconfigure(1, weight=1, uniform='hsl_rows')
        
        self.create_panel(self, 'RGB', 'original_panel', 0, 0)
        self.create_panel(self, 'H', 'ch_h', 0, 1)
        self.create_panel(self, 'S', 'ch_s', 1, 0)
        self.create_panel(self, 'L', 'ch_l_hsl', 1, 1)
        
        self._update_image('RGB', original_img, explicit_size=target_size)
        self._update_image('H', h_img, explicit_size=target_size)
        self._update_image('S', s_img, explicit_size=target_size)
        self._update_image('L', l_img, explicit_size=target_size)

    def setup_layout_luv(self, original_img, l_img, u_img, v_img):
        """Układ dla LUV: Siatka 2x2."""
        self.clear_widgets()
        self.update_idletasks()
        
        win_w = self.winfo_width(); win_h = self.winfo_height()
        if win_w < 100: win_w = 800
        if win_h < 100: win_h = 600
        target_size = (win_w // 2 - 30, win_h // 2 - 40)

        self.columnconfigure(0, weight=1, uniform='luv_cols')
        self.columnconfigure(1, weight=1, uniform='luv_cols')
        self.rowconfigure(0, weight=1, uniform='luv_rows')
        self.rowconfigure(1, weight=1, uniform='luv_rows')
        
        self.create_panel(self, 'RGB', 'original_panel', 0, 0)
        self.create_panel(self, 'L', 'ch_l_luv', 0, 1)
        self.create_panel(self, 'u', 'ch_u', 1, 0)
        self.create_panel(self, 'v', 'ch_v', 1, 1)
        
        self._update_image('RGB', original_img, explicit_size=target_size)
        self._update_image('L', l_img, explicit_size=target_size)
        self._update_image('u', u_img, explicit_size=target_size)
        self._update_image('v', v_img, explicit_size=target_size)

    def setup_layout_ycbcr(self, original_img, y_img, cb_img, cr_img):
        """Układ dla YCbCr: Siatka 2x2."""
        self.clear_widgets()
        self.update_idletasks()
        
        win_w = self.winfo_width(); win_h = self.winfo_height()
        if win_w < 100: win_w = 800
        if win_h < 100: win_h = 600
        target_size = (win_w // 2 - 30, win_h // 2 - 40)

        self.columnconfigure(0, weight=1, uniform='ycbcr_cols')
        self.columnconfigure(1, weight=1, uniform='ycbcr_cols')
        self.rowconfigure(0, weight=1, uniform='ycbcr_rows')
        self.rowconfigure(1, weight=1, uniform='ycbcr_rows')
        
        self.create_panel(self, 'RGB', 'original_panel', 0, 0)
        self.create_panel(self, 'Y', 'ch_y_ycbcr', 0, 1)
        self.create_panel(self, 'Cb', 'ch_cb', 1, 0)
        self.create_panel(self, 'Cr', 'ch_cr', 1, 1)
        
        self._update_image('RGB', original_img, explicit_size=target_size)
        self._update_image('Y', y_img, explicit_size=target_size)
        self._update_image('Cb', cb_img, explicit_size=target_size)
        self._update_image('Cr', cr_img, explicit_size=target_size)