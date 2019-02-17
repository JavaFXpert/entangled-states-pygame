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
NUM_BELL_STATES = 4

DEFAULT_NUM_SHOTS = 100

WINDOW_SIZE = 1500, 1200

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


class HBox(pygame.sprite.RenderPlain):
    """Arranges sprites horizontally"""
    def __init__(self, xpos, ypos, *sprites):
        pygame.sprite.RenderPlain.__init__(self, sprites)
        self.xpos = xpos
        self.ypos = ypos
        self.arrange()

    def arrange(self):
        next_xpos = self.xpos
        next_ypos = self.ypos
        sprite_list = self.sprites()
        for sprite in sprite_list:
            sprite.rect.left = next_xpos
            sprite.rect.top = next_ypos
            next_xpos += sprite.rect.width

class VBox(pygame.sprite.RenderPlain):
    """Arranges sprites vertically"""
    def __init__(self, xpos, ypos, *sprites):
        pygame.sprite.RenderPlain.__init__(self, sprites)
        self.xpos = xpos
        self.ypos = ypos
        self.arrange()

    def arrange(self):
        next_xpos = self.xpos
        next_ypos = self.ypos
        sprite_list = self.sprites()
        for sprite in sprite_list:
            sprite.rect.left = next_xpos
            sprite.rect.top = next_ypos
            next_ypos += sprite.rect.height

class CircuitDiagram(pygame.sprite.Sprite):
    """Displays a circuit diagram"""
    def __init__(self, circuit):
        pygame.sprite.Sprite.__init__(self)
        self.image = None
        self.rect = None
        self.set_circuit(circuit)

    # def update(self):
    #     # Nothing yet
    #     a = 1

    def set_circuit(self, circuit):
        circuit_drawing = circuit.draw(output='mpl')

        # TODO: Create a save_fig method that works cross-platform
        #       and has exception handling
        circuit_drawing.savefig("data/bell_circuit.png")

        self.image, self.rect = load_image('bell_circuit.png', -1)


class QSphere(pygame.sprite.Sprite):
    """Displays a qsphere"""
    def __init__(self, circuit):
        pygame.sprite.Sprite.__init__(self)
        self.image = None
        self.rect = None
        self.set_circuit(circuit)

    # def update(self):
    #     # Nothing yet
    #     a = 1

    def set_circuit(self, circuit):
        backend_sv_sim = BasicAer.get_backend('statevector_simulator')
        job_sim = execute(circuit, backend_sv_sim)
        result_sim = job_sim.result()

        quantum_state = result_sim.get_statevector(circuit, decimals=3)
        qsphere = plot_state_qsphere(quantum_state)
        qsphere.savefig("data/bell_qsphere.png")

        self.image, self.rect = load_image('bell_qsphere.png', -1)
        self.rect.inflate_ip(-100, -100)

class MeasurementsHistogram(pygame.sprite.Sprite):
    """Displays a histogram with measurements"""
    def __init__(self, circuit, num_shots=DEFAULT_NUM_SHOTS):
        pygame.sprite.Sprite.__init__(self)
        self.image = None
        self.rect = None
        self.set_circuit(circuit, num_shots)

    # def update(self):
    #     # Nothing yet
    #     a = 1

    def set_circuit(self, circuit, num_shots=DEFAULT_NUM_SHOTS):
        backend_sim = BasicAer.get_backend('qasm_simulator')
        qr = QuantumRegister(circuit.width(), 'q')
        cr = ClassicalRegister(circuit.width(), 'c')
        meas_circ = QuantumCircuit(qr, cr)
        meas_circ.barrier(qr)
        meas_circ.measure(qr, cr)
        complete_circuit = circuit + meas_circ

        job_sim = execute(complete_circuit, backend_sim, shots=num_shots)

        result_sim = job_sim.result()

        counts = result_sim.get_counts(complete_circuit)
        print(counts)

        histogram = plot_histogram(counts)
        histogram.savefig("data/bell_histogram.png")

        self.image, self.rect = load_image('bell_histogram.png', -1)


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

    cur_bell_state = PHI_PLUS

    # Prepare objects
    clock = pygame.time.Clock()
    circuit = create_bell_circuit(cur_bell_state)

    circuit_diagram = CircuitDiagram(circuit)
    histogram = MeasurementsHistogram(circuit)
    qsphere = QSphere(circuit)

    top_sprites = HBox(0, 0, circuit_diagram)
    bottom_sprites = HBox(0, 200, qsphere, histogram)

    # top_sprites = VBox(0, 0, circuit_diagram)
    # bottom_sprites = VBox(300, 0, qsphere, histogram)

    # Main Loop
    going = True
    while going:
        clock.tick(60)

        # Handle Input Events
        for event in pygame.event.get():
            if event.type == QUIT:
                going = False
            elif event.type == KEYDOWN:
                index_increment = 0
                if event.key == K_ESCAPE:
                    going = False
                elif event.key == K_RIGHT or event.key == K_DOWN:
                    index_increment = 1
                elif event.key == K_LEFT or event.key == K_UP:
                    index_increment = -1
                if index_increment != 0:
                    cur_bell_state  = (cur_bell_state + index_increment) % NUM_BELL_STATES

                    circuit = create_bell_circuit(cur_bell_state)

                    circuit_diagram.set_circuit(circuit)
                    qsphere.set_circuit(circuit)
                    histogram.set_circuit(circuit)

                    top_sprites.arrange()
                    bottom_sprites.arrange()

        # top_sprites.update()
        # bottom_sprites.update()

        #Draw Everything
        screen.blit(background, (0, 0))
        top_sprites.draw(screen)
        bottom_sprites.draw(screen)
        pygame.display.flip()

    pygame.quit()

#Game Over


#this calls the 'main' function when this script is executed
if __name__ == '__main__':
    main()