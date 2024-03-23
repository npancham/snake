import numpy as np
import pygame
import sys
from snake import Game
from snake_solver import Solver


class Button:
    def __init__(self, text, font, center_x, center_y, text_color, background_color, on_click):
        self.center_x = center_x
        self.center_y = center_y
        self.on_click = on_click

        text_surface = font.render(text, True, text_color)
        self.surface = pygame.Surface((SCREEN_WIDTH * 0.75, font.size(text)[1] * 2))
        self.surface.fill(background_color)
        self.size = self.surface.get_size()
        self.surface.blit(text_surface, text_surface.get_rect(center=(self.size[0] / 2, self.size[1] / 2)))

    def render(self):
        screen.blit(self.surface, self.surface.get_rect(center=(self.center_x, self.center_y)))


def main_menu():
    play_button = Button("\u2022 Play", font_48, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 3, WHITE, BLACK, play)
    solve_button = Button("\u2022 Watch AI play", font_48, SCREEN_WIDTH / 2, SCREEN_HEIGHT * 2 / 3, WHITE, BLACK, solve)

    running = True

    while running:
        screen.fill(BLACK)
        play_button.render()
        solve_button.render()

        if mouse_is_at_button(play_button):
            draw_hover_effect(play_button)
        elif mouse_is_at_button(solve_button):
            draw_hover_effect(solve_button)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if mouse_is_at_button(play_button):
                    play_button.on_click()
                elif mouse_is_at_button(solve_button):
                    solve_button.on_click()

        pygame.display.flip()


def play():
    game = Game(N_ROWS, N_COLUMNS)

    running = True

    while running:

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    game.snake_go_north()
                elif event.key == pygame.K_RIGHT:
                    game.snake_go_east()
                elif event.key == pygame.K_DOWN:
                    game.snake_go_south()
                elif event.key == pygame.K_LEFT:
                    game.snake_go_west()

            # Did the user click the window close button?
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        if not game.update():
            running = False

        screen.fill(empty_cell_color)
        draw_grid()
        draw_snake(game.get_snake_head_coordinates(), game.get_snake_body_coordinates())
        draw_food(game.get_food_coordinates())
        draw_walls()
        render_score(game.get_score())

        pygame.display.flip()

        clock.tick(SNAKE_SPEED)

    game_over(game.get_score())


def solve():
    solver = Solver(N_ROWS, N_COLUMNS)

    running = True

    while running:

        for event in pygame.event.get():
            # Did the user click the window close button?
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        if not solver.solve():
            running = False

        screen.fill(empty_cell_color)
        draw_grid()
        draw_snake(solver.get_snake_head_coordinates(), solver.get_snake_body_coordinates())
        draw_food(solver.get_food_coordinates())
        draw_walls()
        render_score(solver.get_score())

        pygame.display.flip()

        clock.tick(SNAKE_SPEED)

    game_over(solver.get_score())


def game_over(score):
    transparent_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    transparent_overlay.fill(BLACK)
    transparent_overlay.set_alpha(192)
    screen.blit(transparent_overlay, (0, 0))

    rendered_game_over = font_48.render("Game Over!", True, WHITE)
    rendered_score = font_36.render(f"Score: {score}", True, WHITE)

    screen.blit(rendered_game_over, rendered_game_over.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT * 1 / 3)))
    screen.blit(rendered_score, rendered_score.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT * 2 / 3)))

    pygame.display.flip()

    time_at_game_over = pygame.time.get_ticks()

    running = True

    while running:
        for event in pygame.event.get():
            # Did the user click the window close button?
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        current_time = pygame.time.get_ticks()

        # Show the game over screen for 5 seconds before moving on
        if current_time - time_at_game_over > 5000:
            running = False


def mouse_is_at_button(button):
    return button.center_y - button.size[1] / 2 <= pygame.mouse.get_pos()[1] <= button.center_y + button.size[1] / 2


def draw_hover_effect(button):
    rect = pygame.Rect(button.center_x - button.size[0] / 2, button.center_y - button.size[1] / 2, button.size[0], button.size[1])
    pygame.draw.rect(screen, button_hover_color, rect, 5, 10)


def array_to_screen_coordinates(coordinates_in_array):
    # As each cell drawn on the screen is larger than 1 pixel, this function converts the array coordinates of a cell to
    # the top left pixel coordinates corresponding to that cell on the screen
    coordinates_on_screen = coordinates_in_array * CELL_SIZE + CELL_SIZE
    return coordinates_on_screen


def draw_outer_filled_square(coordinates_on_screen, color):
    rect = pygame.Rect(coordinates_on_screen[0], coordinates_on_screen[1], CELL_SIZE, CELL_SIZE)
    pygame.draw.rect(screen, color, rect, 0)


def draw_inner_filled_square(coordinates_on_screen, color):
    rect = pygame.Rect(coordinates_on_screen[0] + CELL_BORDER, coordinates_on_screen[1] + CELL_BORDER, CELL_SIZE - 2 * CELL_BORDER, CELL_SIZE - 2 * CELL_BORDER)
    pygame.draw.rect(screen, color, rect, 0)


def draw_open_square(coordinates_on_screen, color):
    rect = pygame.Rect(coordinates_on_screen[0], coordinates_on_screen[1], CELL_SIZE, CELL_SIZE)
    pygame.draw.rect(screen, color, rect, CELL_BORDER)


def draw_snake(snake_head_coordinates, snake_body_coordinates):
    coordinates_on_screen = array_to_screen_coordinates(snake_head_coordinates)
    draw_inner_filled_square(coordinates_on_screen, snake_color)

    for coordinates in snake_body_coordinates:
        coordinates_on_screen = array_to_screen_coordinates(coordinates)
        draw_inner_filled_square(coordinates_on_screen, snake_color)


def draw_food(food_coordinates):
    coordinates_on_screen = array_to_screen_coordinates(food_coordinates)
    draw_inner_filled_square(coordinates_on_screen, food_color)


def draw_walls():
    for i in range(-1, N_ROWS + 1):
        coordinates_on_screen = array_to_screen_coordinates(np.array([-1, i]))
        draw_outer_filled_square(coordinates_on_screen, wall_color)

        coordinates_on_screen = array_to_screen_coordinates(np.array([N_ROWS, i]))
        draw_outer_filled_square(coordinates_on_screen, wall_color)

    for j in range(-1, N_COLUMNS + 1):
        coordinates_on_screen = array_to_screen_coordinates(np.array([j, -1]))
        draw_outer_filled_square(coordinates_on_screen, wall_color)

        coordinates_on_screen = array_to_screen_coordinates(np.array([j, N_COLUMNS]))
        draw_outer_filled_square(coordinates_on_screen, wall_color)


def draw_grid():
    for i in range(N_ROWS):
        for j in range(N_COLUMNS):
            coordinates_on_screen = array_to_screen_coordinates(np.array([j, i]))
            draw_open_square(coordinates_on_screen, WHITE)


def render_score(score):
    rendered_score = font_24.render(f"Score: {score}", True, WHITE, BLACK)
    screen.blit(rendered_score, (CELL_SIZE, CELL_SIZE - rendered_score.get_size()[1]))


BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

N_ROWS = 20
N_COLUMNS = 20

CELL_SIZE = 20
CELL_BORDER = 1

SCREEN_WIDTH = (N_COLUMNS + 2) * CELL_SIZE
SCREEN_HEIGHT = (N_ROWS + 2) * CELL_SIZE

SNAKE_SPEED = 10

empty_cell_color = BLACK
grid_line_color = WHITE
wall_color = BLACK
snake_color = GREEN
food_color = RED
button_hover_color = YELLOW

pygame.init()

pygame.display.set_caption("Snake")

clock = pygame.time.Clock()

screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])

font_48 = pygame.font.SysFont("Sys", 48)
font_36 = pygame.font.SysFont("Sys", 36)
font_24 = pygame.font.SysFont("Sys", 24)

main_menu()
