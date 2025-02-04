import pygame
import random
import numpy as np
from main import Player
import pandas as pd
from collections import defaultdict
from gerete import generate_training_graphs
from pygame import font
# Inicializa o Pygame
pygame.init()

# Configurações do jogo
WIDTH, HEIGHT = 800, 800
GRID_SIZE = 20
SNAKE_COLOR = (0, 255, 0)
FOOD_COLOR = (255, 0, 0)
BG_COLOR = (0, 0, 0)
SPEED = 45 # Velocidade do jogo (ms)

# Criação da tela
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
dic_action = {
    0: "UP",
    1: "DOWN",
    2: "LEFT",
    3: "RIGHT"
}
# Direções
directions = {
    "UP": (0, -1),
    "DOWN": (0, 1),
    "LEFT": (-1, 0),
    "RIGHT": (1, 0)
}

class SnakeGame:
    def __init__(self):
        #inicia snake em um lugar aleatório do mapa
        self.snake = [(random.randint(0, WIDTH // GRID_SIZE - 1), random.randint(0, HEIGHT // GRID_SIZE - 1))]
        self.die = False
        self.food = self.set_foods(1)
        self.direction = "RIGHT"
        self.running = True
        self.points = 0
        self.data = []  # Dados coletados
        self.i =0
        self.lives = 10
        self.death_count = 0
    def reinit(self):
        self.snake = [(random.randint(0, WIDTH // GRID_SIZE - 1), random.randint(0, HEIGHT // GRID_SIZE - 1))]
        if random.randint(0, 10) <= 3:
            n = random.randint(1, 4)
            if n==1:
                self.snake = [(0, 0)]
            elif n==2:
                self.snake = [(0, 800)]
            elif n==3:
                self.snake = [(800, 0)]
            else:
                self.snake = [(800, 800)]
        
        self.food = self.set_foods(1)
        self.direction = "RIGHT"
        self.running = True
        self.points = 0
        self.lives -= 1
    def spawn_food(self, food_num):
        while True:
            food_pos = (random.randint(0, WIDTH // GRID_SIZE - 1), random.randint(0, HEIGHT // GRID_SIZE - 1))
            if food_pos not in self.snake:
                return food_pos
    
    def set_foods(self, food_num):
        self.food = []
        if len(self.snake) < 3:
            #gera comida em porição aleatória perto da cabeça
            head_x, head_y = self.snake[0]

            for i in range(food_num):
                fat_x = random.randint(-2, 2)
                fat_y = random.randint(-2, 2)
                self.food.append((head_x + fat_x, head_y + fat_y))
        else:
            for i in range(food_num):
                self.food.append(self.spawn_food(food_num))
        return self.food
    def auto_move(self, player, max_moves=5000):
        """Executa os movimentos do agente, coleta dados e salva estatísticas."""
        self.death_count = 0  # Reinicia contagem de mortes
        train = 0
        
        state_distribution = defaultdict(int)  # Distribuição de estados
        
        while self.running and train < player.times:
            moves = 0
            score = 0
            self.reinit()
            
            while self.running and moves < max_moves:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                        break
                state = self.get_state()
                
                state_distribution[state] += 1  # Contabiliza o estado
                action = player.get_action(state)
                self.direction = dic_action[action]
                #trata o caso de ação inválida, a cobra não pode voltar para trás
                
                
                size = len(self.snake)
                
                self.move()
                if train < 15:
                    self.draw()
                    pygame.time.delay(SPEED)
                
                if train > player.times - 10:
                    self.draw()
                    pygame.time.delay(SPEED)
                if size < len(self.snake):
                    player.plus(10)  # Recompensa ao comer
                    player.plusMovies(2)
                
                player.live()  # Penalidade por movimento
                moves += 1
                score = player.roudPoints
                
                if len(self.snake) > 2:
                    player.plusMovies(min(len(self.snake), 10))
                
                if not self.running or moves >= 50 or len(self.snake) > 15:
                    self.death_count += 1
                    last_state = state
                    last_action = action
                    
                    self.data.append([self.death_count, moves, score, last_action])
                   
                    
                    player.die(last_state, last_action)
                    train += 1
                    break
            
            player.reset_rewards()
        
        
        
        player.save_q_table()
        # pygame.quit()
    
    def bot_play(self, player):
        """Executa o bot para testar o modelo e coleta estatísticas."""
        test_scores = []
        test_moves = []
        test_data = []
        self.lives = 20  # Definir um número fixo de vidas para os testes
        plays = 0  # Contador de jogadas
        dic = []
        
        pygame.font.init()  # Inicializa o módulo de fontes
        font = pygame.font.SysFont('Arial', 24)  # Fonte para exibir o placar

        while  plays < 15:
            moves = 0
            score = 0
            size = 0
            self.die = False
            while self.running and not self.die and moves < 500:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                
                state = self.get_state()
                action = player.play(state)
                self.direction = dic_action[action]
                size = len(self.snake)
                self.move()
                
                if self.die:
                    self.lives -= 1  # Reduzir vidas quando a cobra morre
                    self.die = False
                    break
                
                moves += 1
                score = len(self.snake) - (moves * 0.1)

                # Desenha o jogo
                self.draw()
                # # Exibe o tamanho da cobra no canto da tela
               
                pygame.time.delay(SPEED)
            
            # Coleta de dados após cada jogo
            dic.append([size, moves])
            test_scores.append(score)
            test_moves.append(moves)
            test_data.append([plays, score, moves, size])
            
            plays += 1

        soma = 0 
        nums = 0
        soma_moves = 0
        for elm in dic:
            nums+=1
            soma += elm[0]
            soma_moves += elm[1]
        print(f"🐍 Tamanho médio da cobra: {soma / nums:.2f}"
              f"\n🏃‍♂️ Média de movimentos: {soma_moves / nums:.2f}")
        print(dic)
        pygame.quit()

    def move(self):
        head_x, head_y = self.snake[0]
        dx, dy = directions[self.direction]
        new_head = (head_x + dx, head_y + dy)

        # Verifica colisões
        if  not (0 <= new_head[0] < WIDTH // GRID_SIZE and 0 <= new_head[1] < HEIGHT // GRID_SIZE):
            self.reinit()
            self.die = True
            self.death_count += 1
            return False

        
        # Adiciona nova cabeça
        self.snake.insert(0, new_head)

        # Se a comida for comida, gera nova, senão remove a cauda
        if new_head in self.food:
            self.points += 10
            self.food = self.set_foods(1)
        else:
            self.snake.pop()
        return True
    def draw(self):
        print(self.i)
        self.i+=1
        screen.fill(BG_COLOR)

        # Desenha a cobra
        for segment in self.snake:
            pygame.draw.rect(screen, SNAKE_COLOR, (segment[0] * GRID_SIZE, segment[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))

        # Desenha a comida
        for food in self.food:
            pygame.draw.rect(screen, FOOD_COLOR, (food[0] * GRID_SIZE, food[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))

        pygame.display.flip()

    def get_state(self):
        #se a distância da cabeça até limite a direita for 0, então 1, se for maior que 0 e menor que 3 1, se não 2
        head_x, head_y = self.snake[0]
        a = 0 if head_y == 0 else 1 if 0 < head_y < 3 else 2
        b = 0 if head_x == 0 else 1 if 0 < head_x < 3 else 2
        c = 0 if head_y == 800 else 1 if 798 < head_y < 800 else 2
        d = 0 if head_x == 800 else 1 if 798 < head_x < 800 else 2


        
        
        #checa qual comida mais próxima
        food = self.food[0]
        x = 0 if head_x == food[0] else 1 if head_x < food[0] else 2
        y = 0 if head_y == food[1] else 1 if head_y < food[1] else 2
        base = 3
        state = [a, b, c, d, x, y]
        index = sum(state[i] * (base ** i) for i in range(len(state)))
        return index

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
    player = Player(game.get_state())
    game.auto_move(player)
    player.load_q_table()
    game.bot_play(player)