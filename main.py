import random
import numpy as np



class Player:
    def __init__(self, state, num_states=729,num_actions = 4, alpha=0.06, gamma=0.65, times=65000, maxMovies = 20, epsilon=0.5, epsilon_decay=0.95, min_epsilon=0.1):
        self.q_table = np.random.uniform(low=-1, high=1, size=(num_states, num_actions))
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
        
    def plusMovies(self, k):
        self.maxMovies = min(self.maxMovies + k, 1000)
        # print("maxMovies: ", self.maxMovies)
    # Q-table carregada de q_table.npy.
    # 🐍 Tamanho médio da cobra: 4.62
    # 🏃‍♂️ Média de movimentos: 77.02
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
        self.roudPoints -= 10 # Penalidade por perder
        self.update_q_table(state, action)
        print("points: ", self.roudPoints)
        self.roudPoints = 0

    def plus(self, points):
        """ Recompensa ao comer comida """
        self.roudPoints += points 

    def live(self):
        """ Pequena penalidade por cada movimento """
        self.roudPoints -= 1  # Movimentos ineficientes são penalizados

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