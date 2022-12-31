import json

import pygame
import pygame_gui

from game import loader
from game.data import Data

class SoundManager:
    instance = None

    def __init__(self, manager, width, height):
        self.manager = manager
        self.width, self.height = width, height
        self.sounds = [
            pygame.mixer.Sound(loader.filepath("sound_files/ButtonSoundTrimmed.wav")),
            pygame.mixer.Sound(
                loader.filepath("sound_files/NewsPaperMusicTrimmed.wav")
            ),
        ]
        pygame.mixer.music.load(loader.filepath("sound_files/RepeatMusic.mp3"))
        self.slidesDisplayed = False
        pygame.mixer.music.set_volume(Data.instance.musicVolume)

        self.displayVolumeButton()
        self.playMusic()
        pygame.mixer.music.set_volume(Data.instance.musicVolume * Data.instance.masterVolume)
        for i in self.sounds:
            pygame.mixer.Sound.set_volume(i, Data.instance.masterVolume)

        SoundManager.instance = self

    def displayVolumeSlides(self):
        self.musicSlide = pygame_gui.elements.UIHorizontalSlider(
            pygame.Rect(self.width - 150, self.height - 20, 140, 15),
            Data.instance.musicVolume,
            [0, 0.5],
            self.manager,
        )
        self.masterSoundSlide = pygame_gui.elements.UIHorizontalSlider(
            pygame.Rect(self.width - 150, self.height - 80, 140, 15),
            Data.instance.masterVolume,
            [0, 1],
            self.manager,
        )
        self.musicSlideText = pygame_gui.elements.UITextBox(
            manager=self.manager,
            relative_rect=pygame.Rect(self.width - 150, self.height - 60, 140, 40),
            html_text="Music Volume",
        )
        self.masterSoundSlideText = pygame_gui.elements.UITextBox(
            manager=self.manager,
            relative_rect=pygame.Rect(self.width - 150, self.height - 120, 140, 40),
            html_text="Master Volume",
        )
        self.volumeButton.kill()
        self.volumeButton = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(self.width - 70, self.height - 160, 60, 30),
            text="volume",
            manager=self.manager,
        )
        self.slidesDisplayed = True

    def killVolumeSlides(self):
        self.musicSlide.kill()
        self.masterSoundSlide.kill()
        self.musicSlideText.kill()
        self.masterSoundSlideText.kill()
        self.volumeButton.kill()
        self.slidesDisplayed = False

    def displayVolumeButton(self):
        self.volumeButton = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(self.width - 70, self.height - 40, 60, 30),
            text="volume",
            manager=self.manager,
        )

    def playMusic(self):
        pygame.mixer.music.play(-1)

    def updateVolume(self):
        Data.instance.musicVolume = self.musicSlide.get_current_value()
        Data.instance.masterVolume = self.masterSoundSlide.get_current_value()
        pygame.mixer.music.set_volume(Data.instance.musicVolume * Data.instance.masterVolume)
        for i in self.sounds:
            pygame.mixer.Sound.set_volume(i, Data.instance.masterVolume)

    def playButtonSound(self):
        pygame.mixer.Sound.play(self.sounds[0])

    def playNewspaperSound(self):
        pygame.mixer.Sound.play(self.sounds[1])

    def process_events(self, event):
        if self.slidesDisplayed:
            self.updateVolume()

        if event.type == pygame.USEREVENT:
            if event.user_type == "ui_button_pressed":
                self.playButtonSound()

                if event.ui_element == self.volumeButton:
                    if self.slidesDisplayed:
                        self.killVolumeSlides()
                        self.displayVolumeButton()
                    else:
                        self.displayVolumeSlides()
