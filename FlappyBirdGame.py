import random
import pygame
import sys


# Game initialisations
pygame.init()
screen = pygame.display.set_mode((576, 1024))
pygame.display.set_caption("Flappy Bird Game")
clock = pygame.time.Clock()
game_font = pygame.font.Font('04B_19.TTF', 40)
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
pygame.time.set_timer(SPAWN_PIPE, 2000)


# Pipe class that contains both top and bottom pipe
class Pipe:
    def __init__(self):
        self.pipe_height = random.choice(pipe_heights)
        self.pipe_bottom = pipe_surface.get_rect(midtop=(700, self.pipe_height))
        self.pipe_top = pipe_surface.get_rect(midbottom=(700, self.pipe_height - 200))

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
                return True
        return False

    def check_bound(self):
        if self.bird_rect.centery >= 900:
            return True
        if self.bird_rect.centery <= 0:
            return True

    def add_score(self, pipe):
        if self.bird_rect.centerx > pipe.get_centerX() > self.bird_rect.centerx - 10:
            self.score += 1

    def get_score(self):
        return self.score

    def draw_bird(self):
        self.rotate_bird()
        self.bird_movement += gravity
        self.bird_rect.centery += self.bird_movement
        screen.blit(self.bird_rotate, self.bird_rect)


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


def score_display(bird):
    score = bird.get_score()
    score_surface = game_font.render(str(int(score)), True, (255, 255, 255))
    score_rect = score_surface.get_rect(center=(288, 100))
    screen.blit(score_surface, score_rect)


def run_game():
    global game_over, pipe_list

    # Initialise new bird
    bird = Bird()

    # Game logic
    while not game_over:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bird.jump()

            if event.type == SPAWN_PIPE:
                # add pipes to game
                pipe_list.append(Pipe())

            if event.type == BIRD_FRAME:
                bird.animate_bird()

        screen.blit(background_surface, (0, 0))
        pipe_list = move_pipes(pipe_list)

        # drawing components
        bird.draw_bird()
        draw_pipes(pipe_list)
        draw_floor()

        # check game behaviours
        game_over = bird.check_collide(pipe_list) or bird.check_bound()
        delete_pipes(pipe_list)

        if pipe_list:
            # Checks if it passed first pipe
            bird.add_score(pipe_list[0])

        # display scores
        score_display(bird)
        pygame.display.update()
        clock.tick(120)

    pygame.quit()


if __name__ == "__main__":
    run_game()
