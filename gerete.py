
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def generate_training_graphs(training_csv, test_csv, training_stats_npy, test_stats_npy, state_distribution_csv):
    # Carregar dados do treinamento
    train_df = pd.read_csv(training_csv)
    train_stats = np.load(training_stats_npy, allow_pickle=True).item()
    
    # Carregar dados de teste
    test_df = pd.read_csv(test_csv)
    test_stats = np.load(test_stats_npy, allow_pickle=True).item()
    
    # Carregar distribuição de estados
    state_df = pd.read_csv(state_distribution_csv)
    
    # Criar gráfico de distribuição de pontuação no treinamento
    plt.figure(figsize=(10, 5))
    plt.hist(train_df['Pontuação'], bins=20, alpha=0.7, color='blue', label='Treinamento')
    plt.xlabel('Pontuação')
    plt.ylabel('Frequência')
    plt.title('Distribuição de Pontuações no Treinamento')
    plt.legend()
    plt.savefig('training_score_distribution.png')
    plt.close()
    
    # Criar gráfico de número de movimentos
    plt.figure(figsize=(10, 5))
    plt.hist(train_df['Movimentos'], bins=20, alpha=0.7, color='green', label='Treinamento')
    plt.xlabel('Movimentos')
    plt.ylabel('Frequência')
    plt.title('Distribuição de Movimentos no Treinamento')
    plt.legend()
    plt.savefig('training_moves_distribution.png')
    plt.close()
    
    # Criar gráfico de distribuição de estados
    plt.figure(figsize=(12, 6))
    plt.bar(state_df['Estado'], state_df['Frequencia'], color='purple')
    plt.xlabel('Estado')
    plt.ylabel('Frequência')
    plt.title('Distribuição de Estados Encontrados pelo Agente')
    plt.xticks(rotation=90)
    plt.savefig('state_distribution.png')
    plt.close()
    
    # Comparação de estatísticas gerais
    labels = ['Média Pontos', 'Média Movimentos']
    training_means = [train_stats['Media_Pontos'], train_stats['Media_Movimentos']]
    test_means = [test_stats['Media_Pontos'], test_stats['Media_Movimentos']]
    
    x = np.arange(len(labels))
    width = 0.35  # Largura das barras
    
    fig, ax = plt.subplots(figsize=(8, 6))
    rects1 = ax.bar(x - width/2, training_means, width, label='Treinamento', color='blue')
    rects2 = ax.bar(x + width/2, test_means, width, label='Teste', color='red')
    
    ax.set_xlabel('Métrica')
    ax.set_ylabel('Valores')
    ax.set_title('Comparação entre Treinamento e Teste')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()
    
    plt.savefig('training_vs_test_comparison.png')
    plt.close()
    
    print("📊 Gráficos gerados e salvos!")
