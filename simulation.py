import simpy
import numpy as np

def simulate_intersection(env, intersection, arrivals, sim_time, out):
    n_arms = intersection.n_arms
    colas = [0] * n_arms
    espera = [[] for _ in range(n_arms)]
    t = 0

    # Capacidad máxima estimada: 1800 veh/h → 0.5 veh/s como tasa de paso efectiva
    capacidad_por_segundo = 0.5  # vehículos por segundo

    while t < sim_time:
        # Llegadas de vehículos por brazo simuladas como probabilidad por segundo
        for idx, lam in enumerate(arrivals):
            p_llegada = lam / 3600  # probabilidad llegada en 1 segundo
            if np.random.rand() < p_llegada:
                colas[idx] += 1

        # Secuencia de fases semafóricas
        for phase in intersection.phases:
            verde = phase.green_time
            brazos_activados = phase.arms_active
            for seg in range(verde):
                # Atender colas de brazos activos en esta fase, respetando capacidad
                for brazo in brazos_activados:
                    if colas[brazo] > 0:
                        # Permitir paso según tasa capacidad por segundo
                        if np.random.rand() < capacidad_por_segundo:
                            espera[brazo].append(t)
                            colas[brazo] -= 1
                yield env.timeout(1)
                t += 1

    # Calcular métricas de demora promedio, cola máxima, y vehículos atendidos
    out['demora_prom'] = []
    out['cola_max'] = []
    out['atendidos'] = []
    for brazo_espera in espera:
        if len(brazo_espera) == 0:
            out['demora_prom'].append(0)
            out['cola_max'].append(0)
            out['atendidos'].append(0)
        else:
            out['demora_prom'].append(np.mean(brazo_espera))
            out['cola_max'].append(max(brazo_espera) - min(brazo_espera))
            out['atendidos'].append(len(brazo_espera))
