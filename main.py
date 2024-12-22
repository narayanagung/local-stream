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
        self.main.geometry("600x700")

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
        # self.song_listbox.bind("<Return>", self.play_selected_music)

        self.allowed_extensions = [".mp3", ".wav", ".flac"]
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
            width=250,
        )

        # Info Label
        folder_label = Label(self.main, textvariable=self.current_folder)
        file_label = Label(self.main, textvariable=self.current_file)
        tip_label = Label(self.main, textvariable=self.tips)
        self.time_bar = Label(self.main, text="")

        # Pause/Resume button
        self.pause_resume_button = ttk.Button(
            self.main,
            # image=self.pause_resume_icon,
            text="Pause",
            compound=LEFT,
            command=lambda: self.toggle_pause_resume_music(paused),
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
        self.time_bar.pack(padx=5, pady=5)

        # Progress bar
        self.progress_bar = ttk.Scale(  # Creates the progress bar
            self.main,
            orient=HORIZONTAL,
            length=400,
            from_=0,
            to=100,
            command=self.seek_music,  # Calls seek_music when user interacts
        )

        self.user_interacting = False  # Tracks if the user is manually seeking
        self.progress_bar.bind("<ButtonPress-1>", self.on_progress_bar_interact)
        self.progress_bar.bind("<ButtonRelease-1>", self.on_progress_bar_release)

        self.scroll_frame.pack()
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.song_listbox.pack(
            pady=15, ipadx=180, ipady=30, side=LEFT, fill=BOTH, expand=True
        )

        self.progress_bar.pack(padx=5, pady=10)  # Packs the progress bar in the GUI

        # Media player button pack
        self.pause_resume_button.pack(padx=5, pady=5)

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
            # self.stop_music()
            self.current_folder.set(
                "Selected folder are not valid - Supported File : .mp3, .wav, .flac,"
            )
            self.tips.set(
                "Tip : Make sure to have at least 1 audio file in your selected folder"
            )
            messagebox.showinfo(
                "No Audio Files Found",
                "No audio files with allowed extensions found in the selected folder ( .mp3, .wav, .flac )\n\nTry selecting another folder!",
            )

    def on_progress_bar_interact(self, event=None):
        self.user_interacting = True  # User starts interacting, mute the audio
        mixer.music.set_volume(0)

    def on_progress_bar_release(self, event=None):
        self.user_interacting = False  # User stops interacting, restore the audio
        mixer.music.set_volume(1)

    def seek_music(self, event=None):
        mixer.music.load(self.selected_music_file)  # Reload the song
        mixer.music.play(start=int(self.progress_bar.get()))

    # Update the listbox content (songs list) with the new folder that user selected
    def update_song_listbox(self):
        self.song_listbox.delete(0, END)
        for music_file in self.music_files:
            self.song_listbox.insert(END, os.path.basename(music_file))

        # self.stop_music()
        self.song_listbox.selection_clear(0, END)
        self.song_listbox.selection_set(0)
        self.play_selected_music()

        self.tips.set(
            "Tip : You can also Double click with the cursor to play any song in the list"
        )

        self.song_listbox.focus_set()

    # Play selected music in listbox, also bind to double clicking
    def play_selected_music(self, event=None):
        global stopped
        stopped = False
        self.selected_index = self.song_listbox.curselection()
        self.selected_music_file = self.music_files[self.selected_index[0]]
        self.song_listbox.selection_clear(0, END)
        self.song_listbox.selection_set(self.selected_index)

        mixer.music.load(self.selected_music_file)
        mixer.music.play()

        self.current_file.set(
            (f"Now Playing - {os.path.basename(self.selected_music_file)}")
        )

        self.progress_bar.config(value=0)
        self.play_time()

    # Pause n resume
    global paused
    paused = False

    def toggle_pause_resume_music(self, is_paused):
        global paused
        paused = is_paused

        if paused:
            mixer.music.unpause()
            paused = False
            self.pause_resume_button["text"] = "Pause"
        else:
            mixer.music.pause()
            paused = True
            self.pause_resume_button["text"] = "Resume"

    global stopped
    stopped = False

    def stop_music(self):
        mixer.music.stop()
        self.song_listbox.selection_clear(0, END)
        self.song_listbox.selection_clear(ACTIVE)
        self.progress_bar.config(value=0)

        self.current_file.set("No Song Currently Played")
        # self.paused = False
        self.pause_resume_button["text"] = "Pause"
        self.status_bar.config(text="")

        global stopped
        stopped = True

    # Song Length & Time Control #
    def play_time(self):
        if stopped:
            return

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

        # Checking the appropriate extention
        if self.selected_music_file.lower().endswith(".mp3"):
            time_mp3()
        elif self.selected_music_file.lower().endswith(".wav"):
            time_wav()
        elif self.selected_music_file.lower().endswith(".flac"):
            time_flac()

        # Current song position
        current_time = mixer.music.get_pos() / 1000
        convert_current_time = time.strftime("%H:%M:%S", time.gmtime(current_time))

        self.selected_index = self.song_listbox.curselection()
        self.selected_music_file = self.music_files[self.selected_index[0]]

        # Song length
        convert_song_length = time.strftime("%H:%M:%S", time.gmtime(self.song_length))

        # Plus 1 to match the song
        current_time += 1

        if int(self.progress_bar.get()) == int(self.song_length):
            self.time_bar.config(text=f"{convert_song_length} - {convert_song_length}")
        elif paused:
            pass
        elif int(self.progress_bar.get()) == int(current_time):
            # Slider is not moved
            self.progress_bar_position = int(self.song_length)
            self.progress_bar.config(
                to=self.progress_bar_position, value=int(current_time)
            )
        else:
            # User interact with the slider
            self.progress_bar_position = int(self.song_length)
            self.progress_bar.config(
                to=self.progress_bar_position, value=int(self.progress_bar.get())
            )
            convert_current_time = time.strftime(
                "%H:%M:%S", time.gmtime(int(self.progress_bar.get()))
            )
            self.time_bar.config(text=f"{convert_current_time} - {convert_song_length}")
            self.next_time = int(self.progress_bar.get()) + 1
            self.progress_bar.config(value=self.next_time)

            self.time_bar.after(1000, self.play_time)


if __name__ == "__main__":
    root = Tk()
    music_player = MusicPlayer(root)
    root.mainloop()
