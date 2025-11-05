class LanguageManager:
    
    def __init__(self):
        self.current_language = 'PL'
        
        self.translations = {
            'PL': {
                'window_title': 'Konwersja RGB → CIE XYZ',
                'load_button': 'Wczytaj',
                'save_button': 'Zapisz',
                'convert_button': 'Przekształć',
                'language_frame': 'Język',
                'original_panel': 'RGB (Oryginalny)',
                'status_ready': 'Gotowy do pracy',
                'status_loaded': 'Wczytano:',
                'status_converting': 'Konwersja...',
                'status_converted': 'Konwersja do XYZ zakończona!',
                'status_saved': 'Zapisano pomyślnie',
                'status_error_load': 'Błąd wczytywania',
                'status_error_convert': 'Błąd konwersji',
                'status_error_save': 'Błąd zapisu',
                'status_no_image': 'Brak obrazu',
                'empty_panel': 'Pusty',
                'waiting_panel': 'Oczekuje na konwersję',
                'warning_no_image': 'Najpierw wczytaj obraz!',
                'warning_no_conversion': 'Najpierw wykonaj konwersję!',
                'warning_no_source': 'Brak informacji o źródłowym obrazie!',
                'warning_folder_not_exists': 'Folder nie istnieje:\n{path}\n\nUtwórz folder \'images\' w Dokumentach.',
                'success_saved': 'Zapisano {count} plików do:\n{path}\n\n{files}',
                'error_load': 'Nie udało się wczytać obrazu:\n{error}',
                'error_convert': 'Błąd podczas konwersji:\n{error}',
                'error_save': 'Nie udało się zapisać plików:\n{error}',
                'dialog_warning': 'Uwaga',
                'dialog_success': 'Sukces',
                'dialog_error': 'Błąd',
                'dialog_select_image': 'Wybierz obraz',
                'dialog_all_images': 'Wszystkie obrazy',
                'dialog_all_files': 'Wszystkie pliki',
            },
            'EN': {
                'window_title': 'RGB → CIE XYZ Conversion',
                'load_button': 'Load',
                'save_button': 'Save',
                'convert_button': 'Convert',
                'language_frame': 'Language',
                'original_panel': 'RGB (Original)',
                'status_ready': 'Ready to work',
                'status_loaded': 'Loaded:',
                'status_converting': 'Converting...',
                'status_converted': 'Conversion to XYZ completed!',
                'status_saved': 'Saved successfully',
                'status_error_load': 'Loading error',
                'status_error_convert': 'Conversion error',
                'status_error_save': 'Save error',
                'status_no_image': 'No image',
                'empty_panel': 'Empty',
                'waiting_panel': 'Waiting for conversion',
                'warning_no_image': 'Please load an image first!',
                'warning_no_conversion': 'Please perform conversion first!',
                'warning_no_source': 'No source image information!',
                'warning_folder_not_exists': 'Folder does not exist:\n{path}\n\nCreate \'images\' folder in Documents.',
                'success_saved': 'Saved {count} files to:\n{path}\n\n{files}',
                'error_load': 'Failed to load image:\n{error}',
                'error_convert': 'Error during conversion:\n{error}',
                'error_save': 'Failed to save files:\n{error}',
                'dialog_warning': 'Warning',
                'dialog_success': 'Success',
                'dialog_error': 'Error',
                'dialog_select_image': 'Select image',
                'dialog_all_images': 'All images',
                'dialog_all_files': 'All files',
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
        flags = {
            'PL': '🇵🇱',
            'EN': '🇬🇧'
        }
        return flags.get(self.current_language, '🌐')
