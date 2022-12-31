import json

import pygame
import pygame_gui

from game import loader


class SoundManager:
    instance = None

    def __init__(self, manager, width, height):
        self.manager = manager
        self.width, self.height = width, height
        self.sounds = [
            pygame.mixer.Sound(loader.filepath("sound_files/ButtonSoundTrimmed.wav")),
            pygame.mixer.Sound(loader.filepath("sound_files/NewsPaperMusicTrimmed.wav")),
        ]
        pygame.mixer.music.load(loader.filepath("sound_files/RepeatMusic.mp3"))
        self.sliders_displayed = False
        self.load_volume()
        pygame.mixer.music.set_volume(self.music_volume)

        self.create_volume_button()
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(self.music_volume * self.master_volume)
        for sound in self.sounds:
            sound.set_volume(self.master_volume)

        SoundManager.instance = self

    def create_volume_sliders(self):
        self.music_volume_slider = pygame_gui.elements.UIHorizontalSlider(
            pygame.Rect(self.width - 150, self.height - 20, 140, 15),
            self.music_volume,
            [0, 0.5],
            self.manager,
        )
        self.master_volume_slider = pygame_gui.elements.UIHorizontalSlider(
            pygame.Rect(self.width - 150, self.height - 80, 140, 15),
            self.master_volume,
            [0, 1],
            self.manager,
        )
        self.music_volume_text = pygame_gui.elements.UITextBox(
            manager=self.manager,
            relative_rect=pygame.Rect(self.width - 150, self.height - 60, 140, 40),
            html_text="Music Volume",
        )
        self.master_volume_text = pygame_gui.elements.UITextBox(
            manager=self.manager,
            relative_rect=pygame.Rect(self.width - 150, self.height - 120, 140, 40),
            html_text="Master Volume",
        )
        self.volume_button.kill()
        self.volume_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(self.width - 70, self.height - 160, 60, 30),
            text="volume",
            manager=self.manager,
        )
        self.sliders_displayed = True

    def kill_volume_sliders(self):
        self.music_volume_slider.kill()
        self.master_volume_slider.kill()
        self.music_volume_text.kill()
        self.master_volume_text.kill()
        self.volume_button.kill()
        self.sliders_displayed = False

    def create_volume_button(self):
        self.volume_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(self.width - 70, self.height - 40, 60, 30),
            text="volume",
            manager=self.manager,
        )

    def update_volume(self):
        self.music_volume = self.music_volume_slider.get_current_value()
        self.master_volume = self.master_volume_slider.get_current_value()
        pygame.mixer.music.set_volume(self.music_volume * self.master_volume)
        self.save_volume()
        for sound in self.sounds:
            sound.set_volume(self.master_volume)

    def play_button_sound(self):
        self.sounds[0].play()

    def play_newspaper_sound(self):
        self.sounds[1].play()

    def save_volume(self):
        data = {
            "Volume": {
                "masterVolume": self.master_volume,
                "musicVolume": self.music_volume,
            }
        }
        with open(loader.filepath("persistence.json"), "w") as write_file:
            json.dump(data, write_file)

    def load_volume(self):
        with open(loader.filepath("persistence.json"), "r") as read_file:
            data = json.load(read_file)
            self.master_volume = data["Volume"]["masterVolume"]
            self.music_volume = data["Volume"]["musicVolume"]

    def process_events(self, event):
        if self.sliders_displayed:
            self.update_volume()

        if event.type == pygame.USEREVENT:
            if event.user_type == "ui_button_pressed":
                self.play_button_sound()

                if event.ui_element == self.volume_button:
                    if self.sliders_displayed:
                        self.kill_volume_sliders()
                        self.create_volume_button()
                    else:
                        self.create_volume_sliders()
