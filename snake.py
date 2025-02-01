import pygame
import random
import numpy as np
from main import Player
import pandas as pd
from collections import defaultdict
from gerete import generate_training_graphs
# Inicializa o Pygame
pygame.init()

# Configurações do jogo
WIDTH, HEIGHT = 800, 800
GRID_SIZE = 20
SNAKE_COLOR = (0, 255, 0)
FOOD_COLOR = (255, 0, 0)
BG_COLOR = (0, 0, 0)
SPEED = 60 # Velocidade do jogo (ms)

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
        all_scores = []  # Lista para armazenar pontuações
        all_moves = []   # Lista para armazenar número de movimentos
        self.data = []   # Lista para armazenar dados detalhados
        state_distribution = defaultdict(int)  # Distribuição de estados
        train_data = []  # Armazena informações de cada treino

        while self.running and train < player.times:
            moves = 0
            score = 0
            while self.running and moves < max_moves:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                        break
                state = self.get_state()
                opposite_directions = {
                    'UP': 'DOWN', 'DOWN': 'UP',
                    'LEFT': 'RIGHT', 'RIGHT': 'LEFT'
                }
                state_distribution[state] += 1  # Contabiliza o estado
                action = player.get_action(state)
                if dic_action[action] == opposite_directions[self.direction]:
                    player.roudPoints -= 0.5  # Aplica uma penalidade alta para desencorajar a ação
                
                self.direction = dic_action[action]
                #trata o caso de ação inválida, a cobra não pode voltar para trás
                
                
                size = len(self.snake)
                self.move()
                
                if size < len(self.snake):
                    player.plus(10)  # Recompensa ao comer
                
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
                    all_scores.append(score)
                    all_moves.append(moves)
                    
                    train_data.append({
                        'Treino': train + 1,
                        'Pontuação': score,
                        'Movimentos': moves,
                        'Mortes': self.death_count,
                        'Epsilon': player.epsilon
                    })
                    
                    player.die(last_state, last_action)
                    train += 1
                    break
            
            player.reset_rewards()
        
        # Converter para NumPy para análise
        self.data = np.array(self.data)
        
        # Criar DataFrame Pandas para salvar CSV
        df = pd.DataFrame(self.data, columns=['Mortes', 'Movimentos', 'Pontuação', 'Última Ação'])
        df.to_csv(f'training_data_{player.times}.csv', index=False)
        
        # Salvar estatísticas gerais
        stats = {
            'Media_Pontos': np.mean(all_scores) if all_scores else 0,
            'Media_Movimentos': np.mean(all_moves) if all_moves else 0,
            'Total_Mortes': self.death_count
        }
        np.save(f'training_stats_{player.times}.npy', stats)
        print("📊 Estatísticas gerais:", stats)
        
        # Salvar distribuição de estados
        state_df = pd.DataFrame(list(state_distribution.items()), columns=['Estado', 'Frequencia'])
        state_df.to_csv(f'state_distribution_{player.times}.csv', index=False)
        
        # Salvar dados de cada treino
        train_df = pd.DataFrame(train_data)
        train_df.to_csv(f'training_session_{player.times}.csv', index=False)
        
        player.save_q_table()
        pygame.quit()
    def bot_play(self, player):
        """Executa o bot para testar o modelo e coleta estatísticas."""
        test_scores = []
        test_moves = []
        test_data = []
        self.lives = 20  # Definir um número fixo de vidas para os testes
        
        while self.lives >= 0:
            moves = 0
            score = 0
            while self.running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                state = self.get_state()
                action = player.play(state)
                self.direction = dic_action[action]
                self.move()
                if self.die:
                    # self.lives -= 1
                    self.die = False
                    break
                moves += 1
                score = len(self.snake) - (moves*0.1)
                self.draw()
                pygame.time.delay(SPEED)
            self.lives -= 1
            test_scores.append(score)
            test_moves.append(moves)
            test_data.append({'Score': score, 'Movimentos': moves, 'Vidas Restantes': self.lives})
            
        pygame.quit()
        
        # Salvar estatísticas de teste
        test_df = pd.DataFrame(test_data)
        test_df.to_csv('test_results.csv', index=False)
        np.save('test_stats.npy', {'Media_Pontos': np.mean(test_scores), 'Media_Movimentos': np.mean(test_moves)})
        print("📊 Estatísticas de Teste Salvas.")

    def move(self):
        head_x, head_y = self.snake[0]
        dx, dy = directions[self.direction]
        new_head = (head_x + dx, head_y + dy)

        # Verifica colisões
        if  not (0 <= new_head[0] < WIDTH // GRID_SIZE and 0 <= new_head[1] < HEIGHT // GRID_SIZE):
            self.reinit()
            self.die = True
            return False

        if new_head in self.snake[1:]:
            self.reinit()
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

        #ver se a calda está perto
        #se a calda estiver perto, a direita, mudar c para 0, se estiver a esquerda mudar a para 0, se estiver em cima mudar b para 0, se estiver em baixo mudar d para 0
        dir = [self.snake[0][0] + 1, self.snake[0][1]]
        esq = [self.snake[0][0] - 1, self.snake[0][1]]
        cima = [self.snake[0][0], self.snake[0][1] - 1]
        baixo = [self.snake[0][0], self.snake[0][1] + 1]

        if dir in self.snake:
            c = 0
        if esq in self.snake:
            a = 0
        if cima in self.snake:
            b = 0
        if baixo in self.snake:
            d = 0

        
        
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
    player.load_q_table()
    game.bot_play(player)
    # generate_training_graphs('training_data_40000.csv', 'test_results.csv', 'training_stats_40000.npy', 'test_stats.npy', 'state_distribution_40000.csv')
    # game.auto_move(player)
