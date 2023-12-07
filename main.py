import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pygame import mixer, USEREVENT


class MusicPlayer:
    def __init__(root, main):
        root.main = main
        root.main.title("Local Stream")
        root.main.geometry("500x400")

        root.current_folder = tk.StringVar()
        root.current_folder.set(
            "No Folder Selected - Supported File : .mp3, .wav .flac"
        )

        root.current_file = tk.StringVar()
        root.current_file.set("No Song Currently Played")

        root.allowed_extensions = [".mp3", ".wav", ".flac"]

        root.repeat_icon = tk.PhotoImage(file="assets/repeat.png")
        root.folder_icon = tk.PhotoImage(file="assets/folder.png")

        root.create_widgets()

        root.paused = False

        root.repeat_mode = True

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

        file_label = tk.Label(root.main, textvariable=root.current_file)
        file_label.pack()

        # Listbox to display the songs
        root.song_listbox = tk.Listbox(
            root.main, selectmode=tk.SINGLE, height=10, width=60
        )
        root.song_listbox.pack(pady=10)
        root.song_listbox.bind("<Double-Button-1>", root.play_selected_music)

        # Play button
        root.play_button = ttk.Button(
            root.main,
            # image=root.play_icon,
            text="Play/Reset",
            compound=tk.LEFT,
            command=root.play_selected_music,
        )
        root.play_button.pack()

        # Pause button
        root.pause_resume_button = ttk.Button(
            root.main,
            # image=root.pause_icon,
            text="Pause",
            compound=tk.LEFT,
            command=root.toggle_pause_resume_music,
        )
        root.pause_resume_button.pack()

        # Stop button
        stop_button = ttk.Button(
            root.main,
            # image=root.stop_icon,
            text="Stop",
            compound=tk.LEFT,
            command=root.stop_music,
        )
        stop_button.pack()

        # Repeat button
        root.repeat_button_toggle = ttk.Button(
            root.main,
            image=root.repeat_icon,
            text="OFF",
            compound=tk.LEFT,
            command=root.toggle_repeat_mode,
        )
        root.repeat_button_toggle.pack()

        # Initialize the mixer
        mixer.init()

    def select_folder(root):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            root.current_folder.set(f"Selected Folder - {folder_selected}")
            root.load_music_files(folder_selected)
            root.update_song_listbox()

    def load_music_files(root, folder_path):
        root.music_files = [
            os.path.join(folder_path, file)
            for file in os.listdir(folder_path)
            if any(file.lower().endswith(ext) for ext in root.allowed_extensions)
        ]

        # Trow error messagebox to remind user to select an appropriate folder
        if not root.music_files:
            root.stop_music()
            root.current_folder.set(
                "No Folder Selected - Supported File : .mp3, .wav .flac"
            )
            messagebox.showinfo(
                "No Audio Files Found",
                "No audio files with allowed extensions found in the selected folder ( .mp3, .wav, .flac )\n\nTry selecting another folder!",
            )

    # Update the listbox content (songs list) with the new folder that user selected
    def update_song_listbox(root):
        root.song_listbox.delete(0, tk.END)
        for music_file in root.music_files:
            root.song_listbox.insert(tk.END, os.path.basename(music_file))
        if root.music_files:
            root.stop_music()
            root.song_listbox.selection_clear(0, tk.END)
            root.song_listbox.selection_set(0)
            root.play_selected_music()

    def play_selected_music(root, event=None):
        root.selected_index = root.song_listbox.curselection()
        if root.selected_index:
            root.selected_music_file = root.music_files[root.selected_index[0]]
            mixer.music.load(root.selected_music_file)
            mixer.music.play()

            def check_end():
                if not root.repeat_mode and mixer.music.get_pos() == -1:
                    # Song ended, play next
                    root.play_selected_music()
                root.main.after(100, check_end)

            check_end()
            root.current_file.set(
                (f"Now Playing - {os.path.basename(root.selected_music_file)}")
            )

    def toggle_pause_resume_music(root):
        if root.paused:
            mixer.music.unpause()
            root.paused = False
            root.pause_resume_button["text"] = "Pause"
            root.current_file.set(
                (f"Now Playing - {os.path.basename(root.selected_music_file)}")
            )
        else:
            mixer.music.pause()
            root.paused = True
            root.pause_resume_button["text"] = "Resume"
            root.current_file.set(
                (f"Paused - {os.path.basename(root.selected_music_file)}")
            )

    def toggle_repeat_mode(root):
        root.repeat_mode = not root.repeat_mode
        if root.repeat_mode:
            root.repeat_button_toggle["text"] = "OFF"
        else:
            root.repeat_button_toggle["text"] = "ON"

    def stop_music(root):
        if mixer.music.get_busy() or mixer.music.pause:
            mixer.music.stop()
            root.song_listbox.selection_clear(0, tk.END)
            root.song_listbox.selection_clear(tk.ACTIVE)
            root.current_file.set("No Song Currently Played")


if __name__ == "__main__":
    root = tk.Tk()
    music_player = MusicPlayer(root)
    root.mainloop()
