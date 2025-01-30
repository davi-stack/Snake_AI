import pygame
import random

# Inicializa o Pygame
pygame.init()

# Configurações do jogo
WIDTH, HEIGHT = 400, 400
GRID_SIZE = 20
SNAKE_COLOR = (0, 255, 0)
FOOD_COLOR = (255, 0, 0)
BG_COLOR = (0, 0, 0)
SPEED = 100  # Velocidade do jogo (ms)

# Criação da tela
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Direções
directions = {
    "UP": (0, -1),
    "DOWN": (0, 1),
    "LEFT": (-1, 0),
    "RIGHT": (1, 0)
}

class SnakeGame:
    def __init__(self):
        self.snake = [(5, 5)]  # Posição inicial
        self.food = self.spawn_food()
        self.direction = "RIGHT"
        self.running = True

    def spawn_food(self):
        while True:
            food_pos = (random.randint(0, WIDTH // GRID_SIZE - 1), random.randint(0, HEIGHT // GRID_SIZE - 1))
            if food_pos not in self.snake:
                return food_pos

    def move(self):
        head_x, head_y = self.snake[0]
        dx, dy = directions[self.direction]
        new_head = (head_x + dx, head_y + dy)

        # Verifica colisões
        if new_head in self.snake or not (0 <= new_head[0] < WIDTH // GRID_SIZE and 0 <= new_head[1] < HEIGHT // GRID_SIZE):
            self.running = False
            return

        # Adiciona nova cabeça
        self.snake.insert(0, new_head)

        # Se a comida for comida, gera nova, senão remove a cauda
        if new_head == self.food:
            self.food = self.spawn_food()
        else:
            self.snake.pop()

    def draw(self):
        screen.fill(BG_COLOR)

        # Desenha a cobra
        for segment in self.snake:
            pygame.draw.rect(screen, SNAKE_COLOR, (segment[0] * GRID_SIZE, segment[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))

        # Desenha a comida
        pygame.draw.rect(screen, FOOD_COLOR, (self.food[0] * GRID_SIZE, self.food[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))

        pygame.display.flip()

    def get_state(self):
        """ Retorna o estado do jogo (para treinar a IA depois) """
        return {
            "snake": self.snake,
            "food": self.food,
            "direction": self.direction
        }

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP and self.direction != "DOWN":
                        self.direction = "UP"
                    elif event.key == pygame.K_DOWN and self.direction != "UP":
                        self.direction = "DOWN"
                    elif event.key == pygame.K_LEFT and self.direction != "RIGHT":
                        self.direction = "LEFT"
                    elif event.key == pygame.K_RIGHT and self.direction != "LEFT":
                        self.direction = "RIGHT"

            self.move()
            self.draw()
            pygame.time.delay(SPEED)

        pygame.quit()

if __name__ == "__main__":
    game = SnakeGame()
    game.run()
