import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from pygame import mixer
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC
import io
import os

class MusicPlayer(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Music Player")
        self.geometry("400x300")

        self.song_list = []
        self.current_song = None
        self.paused_pos = 0  # Initialize paused position

        self.create_widgets()

    def create_widgets(self):
        # Load the image and resize it
        image_path = "music.jpg"  # Replace with the path to your image
        self.background_image = Image.open(image_path)
        self.background_image = self.background_image.resize((400, 300))  # Resize to fit the window
        self.background_photo = ImageTk.PhotoImage(self.background_image)
        
        # Set the background image
        self.background_label = tk.Label(self, image=self.background_photo)
        self.background_label.alt = "Background image showing music notes"
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Labels
        self.lbl_title = tk.Label(self, text="Music Player", font=("Arial", 18))
        self.lbl_title.pack(pady=10)

        self.lbl_song_info = tk.Label(self, text="", font=("Arial", 12))
        self.lbl_song_info.pack(pady=5)

        # Buttons
        self.btn_load_playlist = tk.Button(self, text="Load Music", command=self.load_playlist)
        self.btn_load_playlist.pack()

        self.btn_play_pause = tk.Button(self, text="Play/Pause", command=self.play_pause)
        self.btn_play_pause.pack()

        self.btn_stop = tk.Button(self, text="Stop", command=self.stop)
        self.btn_stop.pack()

        self.btn_exit = tk.Button(self, text="Exit", command=self.exit_app)
        self.btn_exit.pack()

        # Volume Control
        self.volume_var = tk.StringVar()
        self.volume_entry = tk.Entry(self, textvariable=self.volume_var, font=("Arial", 12), width=10)
        self.volume_entry.pack()

        self.scale_volume = tk.Scale(self, from_=0, to=100, orient=tk.HORIZONTAL, command=self.set_volume, showvalue=False)
        self.scale_volume.set(50)  # Default volume
        self.scale_volume.pack()

        self.volume_var.set(str(self.scale_volume.get()))  # Set initial volume value

        # Bind the <Return> event to the volume entry
        self.volume_entry.bind("<Return>", self.update_volume_from_entry)

        # Bind root window event to hide cursor when clicking outside volume entry
        self.bind("<Button-1>", self.hide_cursor)

        # Button to open the album artwork window
        self.btn_open_artwork = tk.Button(self, text="Show Album Artwork", command=self.open_album_art_window)
        self.btn_open_artwork.pack(pady=5)

    def open_album_art_window(self):
        if self.current_song:
            try:
                audio = MP3(self.current_song, ID3=ID3)
                tags = audio.tags
                if "APIC:" in tags:
                    # Get the embedded image (APIC frame)
                    artwork = tags["APIC:"].data
                    image = Image.open(io.BytesIO(artwork))
                    
                    # Display image in a new window
                    artwork_window = tk.Toplevel(self)
                    artwork_window.title("Embedded Album Artwork")
                    img = ImageTk.PhotoImage(image)
                    label = tk.Label(artwork_window, image=img, text="Album Artwork", compound=tk.TOP)
                    label.image = img
                    label.pack()
                else:
                    messagebox.showinfo("Info", "No embedded artwork found in the selected MP3 file.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open album artwork window: {str(e)}")
        else:
            messagebox.showinfo("Info", "No song loaded.")

    def hide_cursor(self, event):
        if event.widget != self.volume_entry:
            self.volume_entry.icursor("end")

    def load_playlist(self):
        if mixer.music.get_busy():
            # Ask the user if they want to stop the music before loading a new song
            if messagebox.askyesno("Stop Music", "Music is currently playing. Do you want to stop it before loading a new song?"):
                self.stop()  # Stop the music if the user chooses to do so
            else:
                return  # If the user chooses not to stop the music, return without loading a new song

        file_path = filedialog.askopenfilename(filetypes=[("MP3 Files", "*.mp3")])
        if file_path:
            if self.is_valid_mp3(file_path):
                self.current_song = file_path
                filename = os.path.basename(file_path)
                self.lbl_song_info.config(text=f"Loaded: {filename}")
            else:
                # Invalid MP3 file
                messagebox.showerror("Error", "Invalid MP3 file selected.")

    def is_valid_mp3(self, file_path):
        return file_path.lower().endswith(".mp3") and os.path.isfile(file_path)

    def play_pause(self):
        if not mixer.get_init():
            mixer.init()
        if not self.current_song:
            return
        if mixer.music.get_busy():
            if mixer.music.get_pos() > 0:
                mixer.music.pause()
                self.paused_pos = mixer.music.get_pos()  # Store current position
            else:
                mixer.music.unpause()
        elif self.current_song:
            if self.paused_pos is not None:
                if mixer.music.get_pos() > 0:
                    mixer.music.unpause()
                else:
                    mixer.music.load(self.current_song)
                    mixer.music.play(start=self.paused_pos)  # Start from paused position
                    filename = os.path.basename(self.current_song)  # Extract just the filename
                    self.lbl_song_info.config(text=f"Now playing: {filename}")
                    self.paused_pos = None
            else:
                mixer.music.load(self.current_song)
                mixer.music.play()
                filename = os.path.basename(self.current_song)  # Extract just the filename
                self.lbl_song_info.config(text=f"Now playing: {filename}")
        self.btn_play_pause.config(text="Play/Pause")



    def stop(self):
        if mixer.music.get_busy():
            mixer.music.stop()
            self.current_song = None
            self.lbl_song_info.config(text="Playback stopped")
            self.btn_play_pause.config(text="Play/Pause")

    def set_volume(self, volume):
        volume = int(volume)
        self.volume_var.set(str(volume))  # Update volume text box
        if not mixer.get_init():
            mixer.init()
        mixer.music.set_volume(volume / 100)

    def update_volume_from_entry(self, event):
        try:
            volume = int(self.volume_var.get())
            if 0 <= volume <= 100:
                self.scale_volume.set(volume)  # Update the slider
                self.set_volume(volume)  # Update the volume
            else:
                messagebox.showerror("Error", "Volume must be between 0 and 100.")
        except ValueError:
            messagebox.showerror("Error", "Invalid volume value.")

    def exit_app(self):
        if mixer.music.get_busy():
            mixer.music.stop()
        mixer.quit()
        self.destroy()

if __name__ == "__main__":
    app = MusicPlayer()
    app.mainloop()
