import pygame

import pygame_gui

class Sound:
    def __init__(self, manager, width, height):
        self.manager = manager
        self.width = width
        self.height = height
        self.sounds = [pygame.mixer.Sound("data/ButtonSound.wav"), pygame.mixer.Sound("data/NewsPaperMusic.wav")]
        pygame.mixer.music.load("data/RepeatMusic.mp3")
        pygame.mixer.music.set_volume(.5)
        self.slidesDisplayed = False
        
    def displayVolumeSlides(self):
        self.musicSlide = pygame_gui.elements.ui_horizontal_slider.UIHorizontalSlider(
            pygame.Rect(self.width - 150, self.height - 20, 140, 15),
            .5, [0,.5], self.manager, None, None, None)
        self.masterSoundSlide = pygame_gui.elements.ui_horizontal_slider.UIHorizontalSlider(
            pygame.Rect(self.width - 150, self.height - 80, 140, 15),
            1, [0,1], self.manager, None, None, None)
        self.musicSlideText = pygame_gui.elements.ui_text_box.UITextBox(
            manager=self.manager,
            relative_rect=pygame.Rect(self.width - 150, self.height - 60, 140, 40),
            html_text="Music Volume",)
        self.masterSoundSlideText = pygame_gui.elements.ui_text_box.UITextBox(
            manager=self.manager,
            relative_rect=pygame.Rect(self.width - 150, self.height - 120, 140, 40),
            html_text="Master Volume")
        self.volumeButton.kill()
        self.volumeButton = pygame_gui.elements.ui_button.UIButton(
            relative_rect=pygame.Rect(self.width - 70, self.height - 160, 60, 30),
            text="volume",
            manager=self.manager)
        self.slidesDisplayed = True

    def killVolumeSlides(self):
        self.musicSlide.kill()
        self.masterSoundSlide.kill()
        self.musicSlideText.kill()
        self.masterSoundSlideText.kill()
        self.volumeButton.kill()
        self.slidesDisplayed = False

    def displayVolumeButton(self):
        self.volumeButton = pygame_gui.elements.ui_button.UIButton(
            relative_rect=pygame.Rect(self.width - 70, self.height - 40, 60, 30),
            text="volume",
            manager=self.manager)
            
        
    def playMusic(self):
        pygame.mixer.music.play(-1)

    def updateVolume(self):
        musicVolume = self.masterSoundSlide.get_current_value()*self.musicSlide.get_current_value()
        pygame.mixer.music.set_volume(musicVolume)
        masterVolume = self.masterSoundSlide.get_current_value()
        for i in self.sounds:
            pygame.mixer.Sound.set_volume(i, masterVolume)

    def playButtonSound(self):
        pygame.mixer.Sound.play(self.sounds[0])

    def playNewspaperSound(self):
        pygame.mixer.Sound.play(self.sounds[1])
