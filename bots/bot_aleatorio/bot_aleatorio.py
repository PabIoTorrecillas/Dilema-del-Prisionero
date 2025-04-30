import random

rewards = {
    ('cooperar', 'cooperar'): (1, 1),  
    ('traicionar', 'cooperar'): (0, 10),  
    ('cooperar', 'traicionar'): (10, 0),    
    ('traicionar', 'traicionar'): (5, 5)        
}

def prisionero_1_estrategia():
    return random.choice(['cooperar', 'traicionar'])

def prisionero_2_estrategia():
    return random.choice(['cooperar', 'traicionar'])

def dilema_del_prisionero_rondas(n_rondas=10):
    prisionero_1_total = 0
    prisionero_2_total = 0

    for ronda in range(1, n_rondas + 1):
        prisionero_1_decision = prisionero_1_estrategia()
        prisionero_2_decision = prisionero_2_estrategia()

        resultado = rewards[(prisionero_1_decision, prisionero_2_decision)]
        
        prisionero_1_total += resultado[0]
        prisionero_2_total += resultado[1]

        print(f"Ronda {ronda}:")
        print(f"Jugador 1 ha decidido: {prisionero_1_decision}")
        print(f"Jugador 2 ha decidido: {prisionero_2_decision}")
        print(f"Resultado: Jugador 1 recibe {resultado[0]} monedas. Jugador 2 recibe {resultado[1]} monedas.")
        print("--------------------------------------------------")

    print(f"Resultado final después de {n_rondas} rondas:")
    print(f"Jugador 1 ha recibido un total de {prisionero_1_total} monedas.")
    print(f"Jugador 2 ha recibido un total de {prisionero_2_total} monedas.")

if __name__ == "__main__":
    dilema_del_prisionero_rondas()
