class LanguageManager:
    
    def __init__(self):
        self.current_language = 'PL'
        
        self.translations = {
            'PL': {
                'window_title': 'Konwersja RGB → CIE XYZ / CMYK',
                'load_button': 'Wczytaj',
                'save_button': 'Zapisz',
                'convert_button': 'Przekształć',
                'language_frame': 'Język',
                'original_panel': 'Oryginał (RGB)',
                'status_ready': 'Gotowy do pracy',
                'status_loaded': 'Wczytano:',
                'status_converting': 'Konwersja...',
                'status_converted': 'Konwersja zakończona!',
                'status_saved': 'Zapisano pomyślnie',
                'status_error_load': 'Błąd wczytywania',
                'status_error_convert': 'Błąd konwersji',
                'status_error_save': 'Błąd zapisu',
                'status_no_image': 'Brak obrazu',
                'empty_panel': 'Pusty',
                'waiting_panel': 'Oczekuje...',
                'warning_no_image': 'Najpierw wczytaj obraz!',
                'warning_no_conversion': 'Najpierw wykonaj konwersję!',
                'warning_no_source': 'Brak informacji o źródłowym obrazie!',
                'success_saved': 'Zapisano pliki do:\n{path}',
                'error_load': 'Nie udało się wczytać obrazu:\n{error}',
                'error_convert': 'Błąd podczas konwersji:\n{error}',
                'error_save': 'Nie udało się zapisać plików:\n{error}',
                'dialog_warning': 'Uwaga',
                'dialog_success': 'Sukces',
                'dialog_error': 'Błąd',
                'dialog_select_image': 'Wybierz obraz',
                # Nazwy kanałów
                'ch_cyan': 'Cyjan (C)',
                'ch_magenta': 'Magenta (M)',
                'ch_yellow': 'Żółty (Y)',
                'ch_black': 'Czarny (K)',
                'ch_x': 'Kanał X',
                'ch_y': 'Kanał Y',
                'ch_z': 'Kanał Z',
                'ch_l': 'Jasność (L*)',
                'ch_a': 'Zielony-Czerwony (a*)',
                'ch_b': 'Niebieski-Żółty (b*)',
                'grayscale_view': 'Widok w skali szarości',
                'ch_h': 'Barwa (H)',
                'ch_s': 'Nasycenie (S)',
                'ch_l_hsl': 'Jasność (L)',

                # YCbCr
                'ch_y_ycbcr': 'Luminancja (Y)',
                'ch_cb': 'Różnica Niebieska (Cb)',
                'ch_cr': 'Różnica Czerwona (Cr)',

            },
            'EN': {
                'window_title': 'RGB → CIE XYZ / CMYK Conversion',
                'load_button': 'Load',
                'save_button': 'Save',
                'convert_button': 'Convert',
                'language_frame': 'Language',
                'original_panel': 'Original (RGB)',
                'status_ready': 'Ready to work',
                'status_loaded': 'Loaded:',
                'status_converting': 'Converting...',
                'status_converted': 'Conversion completed!',
                'status_saved': 'Saved successfully',
                'status_error_load': 'Loading error',
                'status_error_convert': 'Conversion error',
                'status_error_save': 'Save error',
                'status_no_image': 'No image',
                'empty_panel': 'Empty',
                'waiting_panel': 'Waiting...',
                'warning_no_image': 'Please load an image first!',
                'warning_no_conversion': 'Please perform conversion first!',
                'warning_no_source': 'No source image information!',
                'success_saved': 'Saved files to:\n{path}',
                'error_load': 'Failed to load image:\n{error}',
                'error_convert': 'Error during conversion:\n{error}',
                'error_save': 'Failed to save files:\n{error}',
                'dialog_warning': 'Warning',
                'dialog_success': 'Success',
                'dialog_error': 'Error',
                'dialog_select_image': 'Select image',
                # Channel names
                'ch_cyan': 'Cyan (C)',
                'ch_magenta': 'Magenta (M)',
                'ch_yellow': 'Yellow (Y)',
                'ch_black': 'Black (K)',
                'ch_x': 'Channel X',
                'ch_y': 'Channel Y',
                'ch_z': 'Channel Z',
                'ch_l': 'Lightness (L*)',
                'ch_a': 'Green-Red (a*)',
                'ch_b': 'Blue-Yellow (b*)',
                'grayscale_view': 'Grayscale View',
                'ch_h': 'Hue (H)',
                'ch_s': 'Saturation (S)',
                'ch_l_hsl': 'Lightness (L)',

                'ch_y_ycbcr': 'Luminance (Y)',
                'ch_cb': 'Blue Difference (Cb)',
                'ch_cr': 'Red Difference (Cr)',

            }
        }
    
    def set_language(self, language_code):
        if language_code in self.translations:
            self.current_language = language_code
    
    def get(self, key, **kwargs):
        text = self.translations[self.current_language].get(key, key)
        if kwargs:
            try:
                text = text.format(**kwargs)
            except KeyError:
                pass
        return text
    
    def get_flag_emoji(self):
        return '🇵🇱' if self.current_language == 'PL' else '🇬🇧'