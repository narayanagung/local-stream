import os
import time

from tkinter import *
from tkinter import filedialog, messagebox, ttk
from pygame import mixer

from mutagen.mp3 import MP3
from mutagen.wave import WAVE
from mutagen.flac import FLAC


class MusicPlayer:
    ## INITIALIZE ##
    def __init__(self, main):
        self.main = main
        self.main.title("Local Stream")
        self.main.geometry("600x600")

        # Label
        self.current_folder = StringVar()
        self.current_folder.set(
            "No Folder Selected - Supported File : .mp3, .wav .flac"
        )

        self.current_file = StringVar()
        self.current_file.set("No Song Currently Played")

        self.tips = StringVar()

        # Listbox frame
        self.scroll_frame = Frame(self.main, width=50)
        self.scrollbar = Scrollbar(self.scroll_frame, orient=VERTICAL, width=20)
        # Listbox to display the songs
        self.song_listbox = Listbox(
            self.scroll_frame,
            yscrollcommand=self.scrollbar.set,
            activestyle="none",
        )
        self.scrollbar.config(command=self.song_listbox.yview)

        # Assets
        self.folder_icon = PhotoImage(file="assets/folder.png")

        # Key bind
        self.song_listbox.bind("<Double-Button-1>", self.play_selected_music)
        self.song_listbox.bind("<space>", self.toggle_pause_resume_music)
        self.song_listbox.bind("<Return>", self.play_selected_music)
        self.song_listbox.bind("<Up>", self.play_previous_music)
        self.song_listbox.bind("<Down>", self.play_next_music)

        self.allowed_extensions = [".mp3", ".wav", ".flac"]

        self.paused = False
        self.repeat_mode = False
        self.loop_mode = True
        self.song_length = 0

        self.create_widgets()

    ## FUNCTION ##
    # Widget #
    def create_widgets(self):
        # Folder selection button
        folder_button = ttk.Button(
            self.main,
            image=self.folder_icon,
            text="Select Folder",
            compound=LEFT,
            command=self.select_folder,
        )

        # Info Label
        folder_label = Label(self.main, textvariable=self.current_folder)
        file_label = Label(self.main, textvariable=self.current_file)
        tip_label = Label(self.main, textvariable=self.tips)
        self.status_bar = Label(self.main, text="")

        # Repeat button
        self.repeat_button_toggle = ttk.Button(
            self.main,
            # image=self.repeat_icon,
            text="Repeat - Off",
            compound=LEFT,
            command=self.toggle_repeat_mode,
        )

        # Previous button
        self.previous_button = ttk.Button(
            self.main,
            # image=self.previous_icon,
            text="Previous",
            compound=LEFT,
            command=self.play_previous_music,
        )

        # Pause/Resume button
        self.pause_resume_button = ttk.Button(
            self.main,
            # image=self.pause_resume_icon,
            text="Pause",
            compound=LEFT,
            command=self.toggle_pause_resume_music,
        )

        # Next button
        self.next_button = ttk.Button(
            self.main,
            # image=self.next_icon,
            text="Next",
            compound=LEFT,
            command=self.play_next_music,
        )

        # Loop button
        self.loop_button_toggle = ttk.Button(
            self.main,
            # image=self.loop_icon,
            text="Loop - All",
            compound=LEFT,
            command=self.toggle_loop_mode,
        )

        ## GUI ##
        # Header
        folder_button.pack(padx=5, pady=5)
        folder_label.pack(padx=5, pady=5)
        file_label.pack(padx=5, pady=5)
        tip_label.pack(padx=5, pady=5)

        # List Box
        self.scroll_frame.pack()
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.song_listbox.pack(
            pady=15, ipadx=180, ipady=30, side=LEFT, fill=BOTH, expand=True
        )

        # Media Info
        self.status_bar.pack(padx=5, pady=5)

        # Media player button
        self.repeat_button_toggle.pack(padx=5, pady=5)
        self.previous_button.pack(padx=5, pady=5)
        self.pause_resume_button.pack(padx=5, pady=5)
        self.next_button.pack(padx=5, pady=5)
        self.loop_button_toggle.pack(padx=5, pady=5)

        # Initialize the mixer
        mixer.init()

    # List Box & Media Control #
    # Folder selection using filedialog
    def select_folder(self):
        self.folder_selected = filedialog.askdirectory()
        self.current_folder.set(f"Selected Folder - {self.folder_selected}")
        self.load_music_files(self.folder_selected)
        self.update_song_listbox()

    def load_music_files(self, folder_path):
        self.music_files = [
            os.path.join(folder_path, file)
            for file in os.listdir(folder_path)
            if any(file.lower().endswith(ext) for ext in self.allowed_extensions)
        ]

        # Trow error messagebox to remind user to select an appropriate folder
        if not self.music_files:
            self.stop_music()
            self.current_folder.set(
                "Selected folder are not valid - Supported File : .mp3, .wav .flac"
            )
            self.tips.set(
                "Tip : Make sure to have at least 1 audio file in your selected folder"
            )
            messagebox.showinfo(
                "No Audio Files Found",
                "No audio files with allowed extensions found in the selected folder ( .mp3, .wav, .flac )\n\nTry selecting another folder!",
            )

    # Update the listbox content (songs list) with the new folder that user selected
    def update_song_listbox(self):
        self.song_listbox.delete(0, END)
        for music_file in self.music_files:
            self.song_listbox.insert(END, os.path.basename(music_file))

        self.stop_music()
        self.song_listbox.selection_clear(0, END)
        self.song_listbox.selection_set(0)
        self.play_selected_music()

        self.tips.set(
            "Tip : You can also Double click with the cursor to play any song in the list"
        )

        self.song_listbox.focus_set()

    # Interupt current song to play the next/previous song
    def play_next_music(self, event=None):
        self.current_index = self.song_listbox.curselection()
        self.next_index = (self.current_index[0] + 1) % len(self.music_files)
        self.navigate()

    def loop_music_once(self):
        self.current_index = self.song_listbox.curselection()
        self.next_index = (self.current_index[0] + 1) % len(self.music_files)
        self.navigate()
        if self.next_index == 0:
            self.stop_music()
            messagebox.showinfo(
                "Music Stoped",
                "You have reached the end of the playlist\n\nGood night 🤗",
            )

    def play_previous_music(self, event=None):
        self.current_index = self.song_listbox.curselection()
        self.next_index = (self.current_index[0] - 1) % len(self.music_files)
        self.navigate()

    def navigate(self):
        self.next_song = self.music_files[self.next_index]
        self.song_listbox.selection_clear(0, END)
        self.song_listbox.selection_set(self.next_index)
        mixer.music.load(self.next_song)
        mixer.music.play()

        self.current_file.set((f"Now Playing - {os.path.basename(self.next_song)}"))
        self.paused = False
        self.pause_resume_button["text"] = "Pause"

    # Play selected music in listbox, also bind to double clicking
    def play_selected_music(self, event=None):
        self.selected_index = self.song_listbox.curselection()
        self.selected_music_file = self.music_files[self.selected_index[0]]
        self.song_listbox.selection_clear(0, END)
        self.song_listbox.selection_set(self.selected_index)
        mixer.music.load(self.selected_music_file)
        mixer.music.play()

        self.current_file.set(
            (f"Now Playing - {os.path.basename(self.selected_music_file)}")
        )
        self.paused = False
        self.pause_resume_button["text"] = "Pause"

        self.play_time()

        # Check if song end, repeat for eternity
        def check_repeat():
            if self.repeat_mode and mixer.music.get_pos() == -1:
                self.play_selected_music()
            self.main.after(100, check_repeat)

        check_repeat()

        # Loop the entire song list or only once and stop
        def check_loop():
            if self.loop_mode and not mixer.music.get_busy() and not self.paused:
                self.play_next_music()
            if not self.loop_mode and not mixer.music.get_busy() and not self.paused:
                self.loop_music_once()
            self.main.after(100, check_loop)

        check_loop()

    def toggle_pause_resume_music(self, event=None):
        if self.paused:
            mixer.music.unpause()
            self.paused = False
            self.pause_resume_button["text"] = "Pause"
        else:
            mixer.music.pause()
            self.paused = True
            self.pause_resume_button["text"] = "Resume"

    def toggle_repeat_mode(self):
        self.repeat_mode = not self.repeat_mode
        if self.repeat_mode:
            self.repeat_button_toggle["text"] = "Repeat - On"
        else:
            self.repeat_button_toggle["text"] = "Repeat - Off"

    def toggle_loop_mode(self):
        self.loop_mode = not self.loop_mode
        if self.loop_mode:
            self.loop_button_toggle["text"] = "Loop - All"
        else:
            self.loop_button_toggle["text"] = "Loop - Once"

    def stop_music(self):
        # if mixer.music.get_busy() or mixer.music.pause:
        mixer.music.stop()
        self.song_listbox.selection_clear(0, END)
        self.song_listbox.selection_clear(ACTIVE)

        self.current_file.set("No Song Currently Played")
        self.paused = False
        self.pause_resume_button["text"] = "Pause"
        self.status_bar.config(text="")

    # Song Length & Time Control #
    def play_time(self):
        # Get the song length with Mutagen (.mp3, .wav, .flac)
        def time_mp3():
            song_mut_mp3 = MP3(self.selected_music_file)
            self.song_length = song_mut_mp3.info.length

        def time_wav():
            song_mut_wav = WAVE(self.selected_music_file)
            self.song_length = song_mut_wav.info.length

        def time_flac():
            song_mut_flac = FLAC(self.selected_music_file)
            self.song_length = song_mut_flac.info.length

        # Current song time
        current_time = mixer.music.get_pos() / 1000
        convert_current_time = time.strftime("%H:%M:%S", time.gmtime(current_time))

        self.selected_index = self.song_listbox.curselection()
        self.selected_music_file = self.music_files[self.selected_index[0]]

        # Checking the appropriate extention
        if self.selected_music_file.lower().endswith(".mp3"):
            time_mp3()
        elif self.selected_music_file.lower().endswith(".wav"):
            time_wav()
        elif self.selected_music_file.lower().endswith(".flac"):
            time_flac()
        else:
            pass

        # Song length
        convert_song_length = time.strftime("%H:%M:%S", time.gmtime(self.song_length))

        # Visualize current time and song length
        self.status_bar.config(text=f"{convert_current_time} - {convert_song_length}")
        self.status_bar.after(100, self.play_time)


if __name__ == "__main__":
    root = Tk()
    music_player = MusicPlayer(root)
    root.mainloop()
