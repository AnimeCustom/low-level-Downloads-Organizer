import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import shutil
from pathlib import Path
import json

class DownloadOrganizerUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Downloads Organizer")
        self.root.geometry("450x500")
        
        self.downloads_dir = Path.home() / "Downloads"
        
        # Sicherer Speicherort für die Config-Datei in Windows AppData
        config_dir = Path.home() / "AppData" / "Local" / "DownloadsOrganizer"
        config_dir.mkdir(parents=True, exist_ok=True) # Erstellt den Ordner automatisch, falls er fehlt
        self.config_path = config_dir / "organizer_config.json"
        
        # Standardordner und Mapping
        self.available_folders = ["Bilder", "Dokumente", "Videos", "Installationsdateien", "Ignorieren"]
        self.extension_mapping = {}
        self.comboboxes = {}
        
        self.load_config()
        self.found_extensions = self.scan_extensions()
        
        self.build_ui()

    def load_config(self):
        """Lädt die gespeicherten Zuordnungen und Ordner aus einer JSON-Datei."""
        if self.config_path.exists():
            with open(self.config_path, "r") as f:
                data = json.load(f)
                self.extension_mapping = data.get("mapping", {})
                loaded_folders = data.get("folders", [])
                for folder in loaded_folders:
                    if folder not in self.available_folders:
                        self.available_folders.append(folder)

    def save_config(self):
        """Speichert die aktuellen Zuordnungen und Ordner."""
        # Aktualisiere Mapping aus den UI-Elementen
        for ext, box in self.comboboxes.items():
            self.extension_mapping[ext] = box.get()
            
        data = {
            "mapping": self.extension_mapping,
            "folders": self.available_folders
        }
        with open(self.config_path, "w") as f:
            json.dump(data, f)

    def scan_extensions(self):
        """Findet alle Dateiendungen, die aktuell im Downloads-Ordner liegen."""
        extensions = set()
        for item in self.downloads_dir.iterdir():
            if item.is_file() and item.suffix and item.name.lower() not in ["desktop.ini", "organizer_config.json"]:
                extensions.add(item.suffix.lower())
        return sorted(list(extensions))

    def build_ui(self):
        """Baut das User Interface zusammen."""
        # Top Frame für Buttons
        top_frame = tk.Frame(self.root, pady=10)
        top_frame.pack(fill="x")
        
        tk.Button(top_frame, text="+ Neuen Ordner hinzufügen", command=self.add_folder).pack(side="left", padx=10)
        tk.Button(top_frame, text="▶ Aufräumen starten", command=self.run_sorting, bg="#4CAF50", fg="white").pack(side="right", padx=10)
        
        # Scrollbarer Bereich für die Endungen
        canvas = tk.Canvas(self.root)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")
        
        # UI-Zeilen für jede gefundene Endung generieren
        tk.Label(scrollable_frame, text="Gefundene Dateiendungen", font=("Arial", 12, "bold")).grid(row=0, column=0, pady=10, sticky="w")
        
        if not self.found_extensions:
            tk.Label(scrollable_frame, text="Keine Dateien zum Aufräumen gefunden.").grid(row=1, column=0, sticky="w")
            return

        for i, ext in enumerate(self.found_extensions, start=1):
            tk.Label(scrollable_frame, text=ext, width=15, anchor="w").grid(row=i, column=0, pady=5)
            
            box = ttk.Combobox(scrollable_frame, values=self.available_folders, state="readonly", width=25)
            # Vorherige Auswahl setzen oder "Ignorieren" als Standard
            box.set(self.extension_mapping.get(ext, "Ignorieren"))
            box.grid(row=i, column=1, pady=5)
            
            self.comboboxes[ext] = box

    def add_folder(self):
        """Lässt den Nutzer einen neuen Zielordner definieren."""
        new_folder = simpledialog.askstring("Neuer Ordner", "Name des neuen Ordners:")
        if new_folder and new_folder not in self.available_folders:
            self.available_folders.append(new_folder)
            # Alle Dropdowns aktualisieren
            for box in self.comboboxes.values():
                box["values"] = self.available_folders

    def run_sorting(self):
        """Verschiebt die Dateien basierend auf den UI-Einstellungen."""
        self.save_config()
        moved_count = 0
        
        for item in self.downloads_dir.iterdir():
            if item.is_file() and item.suffix and item.name.lower() not in ["desktop.ini", "organizer_config.json"]:
                ext = item.suffix.lower()
                target_folder = self.extension_mapping.get(ext, "Ignorieren")
                
                # Datei verschieben, wenn nicht auf "Ignorieren" gesetzt
                if target_folder != "Ignorieren" and target_folder in self.available_folders:
                    target_path = self.downloads_dir / target_folder
                    target_path.mkdir(exist_ok=True) # Erstellt den Ordner, falls er nicht existiert
                    
                    try:
                        shutil.move(str(item), str(target_path / item.name))
                        moved_count += 1
                    except Exception as e:
                        print(f"Fehler bei {item.name}: {e}")
                        
        messagebox.showinfo("Erfolg", f"Aufräumen beendet!\n{moved_count} Dateien wurden verschoben.")
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = DownloadOrganizerUI(root)
    root.mainloop()