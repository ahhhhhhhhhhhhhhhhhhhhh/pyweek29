'''Game main module.

Contains the entry point used by the run_game.py script.

Feel free to put all your game code here, or in other modules in this "game"
package.
'''

import pygame

from game import loader

def main():
    print("Hello from your game's main()")
    print(loader.load('sample.txt').read())

    width, height = [1280, 720]
    bgcolor = (230,30,70)

    pygame.init()

    screen = pygame.display.set_mode([width,height])
    clock = pygame.time.Clock()

    while True:
        clock.tick(60)
        
        screen.fill(bgcolor)
        
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit


    
