# simulation.py
import simpy
import numpy as np

def simulate_intersection(env, intersection, arrivals, sim_time, out):
    n_arms = intersection.n_arms
    colas = [0]*n_arms
    espera = [[] for _ in range(n_arms)]
    t = 0
    while t < sim_time:
        # Llegadas
        for idx, lam in enumerate(arrivals):
            if np.random.rand() < lam/3600:
                colas[idx] += 1
        # Fases secuenciales
        for phase in intersection.phases:
            for sec in range(phase.green_time):
                for arm in phase.arms_active:
                    if colas[arm] > 0:
                        espera[arm].append(t)
                        colas[arm] -= 1
                yield env.timeout(1)
                t += 1
    out['demora_prom'] = [np.mean(x) if x else 0 for x in espera]
    out['atendidos'] = [len(x) for x in espera]
    out['cola_max'] = [max([t-i for i in x]) if x else 0 for x in espera]

