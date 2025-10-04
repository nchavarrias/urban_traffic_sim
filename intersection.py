# intersection.py
class Intersection:
    def __init__(self, n_arms, phases):
        self.n_arms = n_arms
        self.phases = phases  # Lista de Phase objects

class Phase:
    def __init__(self, name, green_time, arms_active):
        self.name = name
        self.green_time = green_time    # segundos
        self.arms_active = arms_active  # [i, j, k] brazos en verde

# Ejemplo de modelos de cruce:

def model_plus(n_arms):
    # Cruce "X"/"+" típico: 4 brazos emparejados por fases ortogonales
    # Fase 1: Norte-Sur; Fase 2: Este-Oeste
    phases = [
        Phase("Norte-Sur", 30, [0, 2]),
        Phase("Este-Oeste", 30, [1, 3])
    ]
    return Intersection(n_arms, phases)

def model_tee():
    # Cruce en "T": 3 brazos con fases adaptadas
    phases = [
        Phase("Principal", 35, [0, 1]),      # Principal y lateral derecha
        Phase("Lateral", 25, [2])            # Lateral solo
    ]
    return Intersection(3, phases)

def model_star():
    # Cruce tipo estrella: 5-6 brazos
    n_arms = 5
    phases = [
        Phase("Norte", 15, [0]),
        Phase("Este", 15, [1]),
        Phase("Sur", 15, [2]),
        Phase("Oeste",15, [3]),
        Phase("Centro",15, [4])
    ]
    return Intersection(n_arms, phases)
