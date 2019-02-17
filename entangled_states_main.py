#!/usr/bin/env python
"""
Demonstrates various entangled states
"""

import os, pygame
from pygame.locals import *
from pygame.compat import geterror
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit import execute
from qiskit import BasicAer
from qiskit.tools.visualization import plot_state_qsphere
from qiskit.tools.visualization import plot_histogram

# Bell state type constants
PHI_PLUS = 0
PHI_MINUS = 1
PSI_PLUS = 2
PSI_MINUS = 3

WINDOW_SIZE = 600, 600

WHITE = 255, 255, 255
BLACK = 0, 0, 0


if not pygame.font: print ('Warning, fonts disabled')
if not pygame.mixer: print ('Warning, sound disabled')

main_dir = os.path.split(os.path.abspath(__file__))[0]
data_dir = os.path.join(main_dir, 'data')


def load_image(name, colorkey=None):
    fullname = os.path.join(data_dir, name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error:
        print ('Cannot load image:', fullname)
        raise SystemExit(str(geterror()))
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image, image.get_rect()


def load_sound(name):
    class NoneSound:
        def play(self): pass
    if not pygame.mixer or not pygame.mixer.get_init():
        return NoneSound()
    fullname = os.path.join(data_dir, name)
    try:
        sound = pygame.mixer.Sound(fullname)
    except pygame.error:
        print ('Cannot load sound: %s' % fullname)
        raise SystemExit(str(geterror()))
    return sound


def create_bell_circuit(bell_state_type):
    qr = QuantumRegister(2, 'q')
    qc = QuantumCircuit(qr)

    # Insert X gates according to type of Bell state
    if bell_state_type == PHI_MINUS or bell_state_type == PSI_MINUS:
        qc.x(qr[0])
    if bell_state_type == PSI_PLUS or bell_state_type == PSI_MINUS:
        qc.x(qr[1])

    qc.h(qr[0])
    qc.cx(qr[0], qr[1])
    return qc



class CircuitDiagram(pygame.sprite.Sprite):
    """Displays a circuit diagram"""
    def __init__(self, circuit):
        pygame.sprite.Sprite.__init__(self)

        circuit_drawing = circuit.draw(output='mpl')

        # TODO: Create a save_fig method that works cross-platform
        #       and has exception handling
        circuit_drawing.savefig("data/bell_circuit.png")

        self.image, self.rect = load_image('bell_circuit.png', -1)

    def update(self):
        # Nothing yet
        a = 1


def main():
    pygame.init()
    screen = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption('Entangled States')

    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill(WHITE)

    # TODO: Put things on background?

    screen.blit(background, (0, 0))
    pygame.display.flip()

    # Prepare objects
    clock = pygame.time.Clock()
    circuit = create_bell_circuit(PHI_PLUS)
    circuit_diagram = CircuitDiagram(circuit)
    allsprites = pygame.sprite.RenderPlain(circuit_diagram)


#Main Loop
    going = True
    while going:
        clock.tick(60)

        # Handle Input Events
        for event in pygame.event.get():
            if event.type == QUIT:
                going = False
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                going = False

        allsprites.update()

        #Draw Everything
        screen.blit(background, (0, 0))
        allsprites.draw(screen)
        pygame.display.flip()

    pygame.quit()

#Game Over


#this calls the 'main' function when this script is executed
if __name__ == '__main__':
    main()