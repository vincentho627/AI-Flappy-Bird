import random
import neat
import pygame
import sys


# Game initialisations
pygame.init()
screen = pygame.display.set_mode((576, 1024))
pygame.display.set_caption("AI Flappy Bird")
clock = pygame.time.Clock()
game_font = pygame.font.Font('Font.TTF', 40)
game_over = False
gravity = 0.7

# Background initialisations
background_surface = pygame.transform.scale2x(pygame.image.load('assets/background-day.png').convert_alpha())

# Floor initialisations
floor_surface = pygame.transform.scale2x(pygame.image.load('assets/base.png').convert())
floor_x_pos = 0

# Bird initialisations
bird_down_flap = pygame.transform.scale2x(pygame.image.load('assets/yellowbird-downflap.png').convert_alpha())
bird_mid_flap = pygame.transform.scale2x(pygame.image.load('assets/yellowbird-midflap.png').convert_alpha())
bird_up_flap = pygame.transform.scale2x(pygame.image.load('assets/yellowbird-upflap.png').convert_alpha())
bird_frames = [bird_up_flap, bird_mid_flap, bird_down_flap]
BIRD_FRAME = pygame.USEREVENT + 1

# Pipes initialisations
pipe_surface = pygame.transform.scale2x(pygame.image.load('assets/pipe-green.png').convert_alpha())
pipe_heights = [300, 400, 500, 600, 700, 800]
SPAWN_PIPE = pygame.USEREVENT
pipe_list = []

# Set events
pygame.time.set_timer(BIRD_FRAME, 150)
# Time dependent on speeds of pipe
pygame.time.set_timer(SPAWN_PIPE, 2000)


# Pipe class that contains both top and bottom pipe
class Pipe:
    def __init__(self):
        self.pipe_height = random.choice(pipe_heights)
        self.pipe_bottom = pipe_surface.get_rect(midtop=(600, self.pipe_height))
        self.pipe_top = pipe_surface.get_rect(midbottom=(600, self.pipe_height - 200))

    def get_pipe(self):
        return self.pipe_bottom, self.pipe_top

    def move_pipe(self):
        self.pipe_bottom.centerx -= 5
        self.pipe_top.centerx -= 5

    def passed_screen(self):
        return self.pipe_top.right <= 0

    def draw_pipe(self):
        screen.blit(pipe_surface, self.pipe_bottom)
        flip_pipe = pygame.transform.flip(pipe_surface, False, True)
        screen.blit(flip_pipe, self.pipe_top)

    def get_centerX(self):
        return self.pipe_top.centerx


# Bird class contains scores and all functions and checks
class Bird:
    def __init__(self):
        self.score = 0
        self.bird_index = 0
        self.bird_surface = bird_frames[self.bird_index]
        self.bird_rect = self.bird_surface.get_rect(center=(100, 512))
        self.bird_movement = 0
        self.bird_rotate = pygame.transform.rotozoom(self.bird_surface, self.bird_movement * -1.5, 1)
        self.alive = True

    def rotate_bird(self):
        self.bird_rotate = pygame.transform.rotozoom(self.bird_surface, self.bird_movement * -1.5, 1)

    def jump(self):
        if self.bird_rect.centery >= -5:
            self.bird_movement = 0
            self.bird_movement -= 10

    def update_index(self):
        if self.bird_index < 2:
            self.bird_index += 1
        else:
            self.bird_index = 0

    def animate_bird(self):
        self.update_index()
        self.bird_surface = bird_frames[self.bird_index]
        self.bird_rect = self.bird_surface.get_rect(center=(100, self.bird_rect.centery))

    def check_collide(self, pipes):
        for pipe in pipes:
            pipe1, pipe2 = pipe.get_pipe()
            if self.bird_rect.colliderect(pipe1) or self.bird_rect.colliderect(pipe2):
                self.alive = False
                return True
        return False

    def check_bound(self):
        if self.bird_rect.centery >= 900:
            self.alive = False
            return True
        if self.bird_rect.centery <= 0:
            self.alive = False
            return True

    def add_score(self, pipe):
        # Set range dependent on speed of pipe
        if self.bird_rect.centerx > pipe.get_centerX() > self.bird_rect.centerx - 10:
            self.score += 1

    def get_score(self):
        return self.score

    def is_alive(self):
        return self.alive

    def draw_bird(self):
        self.rotate_bird()
        self.bird_movement += gravity
        self.bird_rect.centery += self.bird_movement
        screen.blit(self.bird_rotate, self.bird_rect)

    def get_reward(self):
        if self.is_alive():
            return 1 + self.get_score()
        else:
            return -50

    def get_data(self, pipe):
        if pipe:
            bottom, top = pipe.get_pipe()
            distance_top = abs(self.bird_rect.centery - top.bottom)
            distance_bot = abs(self.bird_rect.centery - bottom.top)
            return self.bird_rect.centery, distance_bot, distance_top
        return self.bird_rect.centery, abs(self.bird_rect.centery - 400), abs(self.bird_rect.centery - 600)


# Non class functions dealing with public variables
def move_pipes(pipes):
    for pipe in pipes:
        pipe.move_pipe()
    return pipes


def delete_pipes(pipes):
    for pipe in pipes:
        if pipe.passed_screen():
            pipes.remove(pipe)
        else:
            break


def draw_pipes(pipes):
    for pipe in pipes:
        pipe.draw_pipe()


def draw_floor():
    global floor_x_pos
    if floor_x_pos <= -576:
        floor_x_pos = 0
    floor_x_pos -= 1
    screen.blit(floor_surface, (floor_x_pos, 900))
    screen.blit(floor_surface, (floor_x_pos + 576, 900))


def score_display(bird_list):
    score = max(map(lambda x: x.get_score(), bird_list))
    score_surface = game_font.render(str(int(score)), True, (255, 255, 255))
    score_rect = score_surface.get_rect(center=(288, 100))
    screen.blit(score_surface, score_rect)


def restart_game():
    global pipe_list
    pipe_list = []
    pygame.time.set_timer(BIRD_FRAME, 150)
    pygame.time.set_timer(SPAWN_PIPE, 2000)


def run_game(genomes, config):
    global game_over, pipe_list

    # Initialise new bird
    # bird = Bird()
    # bird_list.append(bird)
    nets = []
    bird_list = []
    # Initialise list with a pipe to start process
    pipe_list = [Pipe()]

    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        g.fitness = 0

        bird_list.append(Bird())

    # Game logic
    while True:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == SPAWN_PIPE:
                # add pipes to game
                pipe_list.append(Pipe())

        # Input data into networks
        for index, bird in enumerate(bird_list):
            if pipe_list:
                output = nets[index].activate(bird.get_data(pipe_list[-1]))
            else:
                output = nets[index].activate(bird.get_data(None))
            i = output.index(max(output))
            # getting output of either 0 or 1 since only 2 outputs
            if i == 0:
                bird.jump()
            else:
                pass

        remain_birds = 0
        for index, bird in enumerate(bird_list):
            # give award if bird still alive, reward calculated by staying alive and how many pipes passed
            if bird.is_alive():
                remain_birds += 1
                bird.animate_bird()
                genomes[index][1].fitness += bird.get_reward()

        # Move onto next generation
        if remain_birds == 0:
            break

        screen.blit(background_surface, (0, 0))
        pipe_list = move_pipes(pipe_list)

        # drawing components
        for index, bird in enumerate(bird_list):
            if bird.is_alive():
                bird.draw_bird()
                if bird.check_bound() or bird.check_collide(pipe_list):
                    genomes[index][1].fitness += bird.get_reward()

                if pipe_list:
                    # Checks if it passed first pipe
                    bird.add_score(pipe_list[-1])

        draw_pipes(pipe_list)
        draw_floor()

        # check game behaviours
        delete_pipes(pipe_list)

        # display scores
        score_display(bird_list)
        pygame.display.update()
        clock.tick(120)

    restart_game()


if __name__ == "__main__":
    config_path = './config-feedforward.txt'
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet,
                                neat.DefaultStagnation, config_path)

    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    p.run(run_game, 1000)
