import random
import numpy as np

alpha = 0.9
gamma = 0.8
epsilon = 0.25
epsilon_decay = 0.999
min_epsilon = 0.05
num_episodes = 10000
num_steps = 1000
max_steps = 10000

valA = [0, 1, 2]
valB = [0, 1, 2]
valC = [0, 1, 2]
valD = [0, 1, 2]

valX = [0, 1, 2]
valY = [0, 1, 2]


actions = [0, 1, 2, 3]
# env = gym.make("Snake-v0", render_mode="human")

# Q-table


# def train():
#     for episode in range(num_episodes):
#         state = env.reset()
#         total_reward = 0
#         for step in range(max_steps):
#             if random.uniform(0, 1) < epsilon:
#                 action = env.action_space.sample()
#             else:
#                 action = np.argmax(q_table[state])
            
#             next_state, reward, done, _ = env.step(action)
#             total_reward += reward

#             q_table[state, action] = q_table[state, action] + alpha * (reward + gamma * np.max(q_table[next_state]) - q_table[state, action])
#             state = next_state

#             if done:
#                 break
        
#         epsilon = max(epsilon * epsilon_decay, min_epsilon)



class Player:
    def __init__(self, state, num_states=729,num_actions = 4, alpha=0.0015, gamma=0.65, times=60000, maxMovies = 20, epsilon=0.6, epsilon_decay=0.8, min_epsilon=0.1):
        self.q_table = np.zeros((num_states, num_actions))  # Inicializa a Q-table
        self.roudPoints = 0  # Recompensa acumulada
        self.state = state  # Estado atual
        self.new_state = state  # Novo estado após a ação
        self.alpha = alpha  # Taxa de aprendizado
        self.gamma = gamma  # Fator de desconto
        self.times = times
        self.maxMovies = maxMovies
        self.epsilon = epsilon  # Probabilidade de exploração
        self.epsilon_decay = epsilon_decay  # Decaimento do epsilon
        self.min_epsilon = min_epsilon  # Valor mínimo de epsilon
        # self.load_q_table()
    def plusMovies(self, k):
        self.maxMovies = min(self.maxMovies + k, 1000)
        # print("maxMovies: ", self.maxMovies)


    def play(self, state):
        action = int(np.argmax(self.q_table[state]))
        return action
    def get_action(self, state):
        """ Escolhe uma ação usando uma estratégia epsilon-greedy """

        # state = tuple(state)  # Garante que o estado seja uma tupla

        # # Se o estado não existir na Q-table, inicializa com zeros
        # if state not in self.q_table:
        #     self.q_table[state] = np.zeros(4)

        if random.uniform(0, 1) < self.epsilon:
            action = random.choice([0, 1, 2, 3])  # Exploração (ação aleatória)
        else:
            action = int(np.argmax(self.q_table[state]))

        #decai o epsilon
        self.epsilon = max(self.epsilon * self.epsilon_decay, self.min_epsilon)

        # print(f"🔍 Estado: {state} | Ação escolhida: {action}")  # Debug

        if action not in [0, 1, 2, 3]:
            raise ValueError(f"⚠️ ERRO: Ação inválida {action} gerada!")

        return action
    
    def save_q_table(self, filename='q_table.npy'):
        """Salva a Q-table em um arquivo."""
        np.save(filename, self.q_table)
        print(f"Q-table salva em {filename}.")

    def load_q_table(self, filename='q_table.npy'):
        """Carrega a Q-table de um arquivo."""
        self.q_table = np.load(filename)
        print(f"Q-table carregada de {filename}.")


    def die(self, state, action):
        """ Penaliza ao morrer e reseta o estado """
        self.roudPoints -= 50 # Penalidade por perder
        self.update_q_table(state, action)
        print("points: ", self.roudPoints)
        self.roudPoints = 0

    def plus(self, points):
        """ Recompensa ao comer comida """
        self.roudPoints += points 

    def live(self):
        """ Pequena penalidade por cada movimento """
        self.roudPoints -= 0.1  # Movimentos ineficientes são penalizados

    def update_q_table(self, state, action):
        """ Atualiza a Q-table usando a equação do Q-learning """
        
        reward = self.roudPoints  # Obtém a recompensa acumulada
        self.q_table[state, action] = self.q_table[state, action] + self.alpha * (
            reward + self.gamma * np.max(self.q_table[self.new_state]) - self.q_table[state, action]
        )

    def reset_rewards(self):
        """ Reseta a recompensa acumulada """
        self.roudPoints = 0
    def reset(self, state, action):
        """ Reseta o estado, atualiza a Q-table e prepara um novo episódio """
        self.update_q_table(state, action)  # Atualiza a Q-table antes de resetar
        self.roudPoints = 0  # Zera a recompensa para o próximo episódio
