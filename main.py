import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pygame import mixer


class MusicPlayer:
    def __init__(root, main):
        root.main = main
        root.main.title("Local Stream")
        root.main.geometry("500x400")

        root.current_folder = tk.StringVar()
        root.current_folder.set("No folder selected")

        root.allowed_extensions = [".mp3", ".wav", ".flac"]

        # root.play_icon = tk.PhotoImage(file="assets/play.png")
        # root.stop_icon = tk.PhotoImage(file="assets/stop.png")
        root.folder_icon = tk.PhotoImage(file="assets/folder.png")

        root.create_widgets()

    def create_widgets(root):
        # Folder selection button
        folder_button = ttk.Button(
            root.main,
            image=root.folder_icon,
            text="Select Folder",
            compound=tk.LEFT,
            command=root.select_folder,
        )
        folder_button.pack(pady=5)

        # Current folder label
        folder_label = tk.Label(root.main, textvariable=root.current_folder)
        folder_label.pack()

        # Listbox to display the songs
        root.song_listbox = tk.Listbox(
            root.main, selectmode=tk.SINGLE, height=10, width=60
        )
        root.song_listbox.pack(pady=10)
        root.song_listbox.bind("<Double-Button-1>", root.play_selected_music)

        # Play button
        play_button = ttk.Button(
            root.main,
            # image=root.play_icon,
            text="Play",
            compound=tk.LEFT,
            command=root.play_selected_music,
        )
        play_button.pack()

        # Stop button
        stop_button = ttk.Button(
            root.main,
            # image=root.stop_icon,
            text="Stop",
            compound=tk.LEFT,
            command=root.stop_music,
        )
        stop_button.pack()

        # Initialize the mixer
        mixer.init()

    def select_folder(root):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            root.current_folder.set("Selected Folder: " + folder_selected)
            root.load_music_files(folder_selected)
            root.update_song_listbox()

    def load_music_files(root, folder_path):
        root.music_files = [
            os.path.join(folder_path, file)
            for file in os.listdir(folder_path)
            if any(file.lower().endswith(ext) for ext in root.allowed_extensions)
        ]

        if not root.music_files:
            messagebox.showinfo(
                "No Audio Files Found",
                "No audio files with allowed extensions found in the selected folder (.mp3, .wav, .flac)",
            )

    def update_song_listbox(root):
        root.song_listbox.delete(0, tk.END)  # Clear the listbox
        for music_file in root.music_files:
            root.song_listbox.insert(tk.END, os.path.basename(music_file))

    def play_selected_music(root, event=None):
        selected_index = root.song_listbox.curselection()
        if selected_index:
            selected_music_file = root.music_files[selected_index[0]]
            if mixer.music.get_busy():
                mixer.music.stop()
            mixer.music.load(selected_music_file)
            mixer.music.play()

    def stop_music(root):
        if mixer.music.get_busy():
            mixer.music.stop()
            root.song_listbox.selection_clear(0, tk.END)
            root.song_listbox.selection_set(tk.ACTIVE)


if __name__ == "__main__":
    root = tk.Tk()
    music_player = MusicPlayer(root)
    root.mainloop()
