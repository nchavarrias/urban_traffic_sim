import simpy
import numpy as np

def simulate_intersection(env, intersection, arrivals, sim_time, out, log=None):
    n_arms = intersection.n_arms
    colas = [[] for _ in range(n_arms)]  # listas con tiempos de llegada de vehículos en cola
    demoras = [[] for _ in range(n_arms)]  # tiempos de espera reales de vehículos que pasaron
    max_cola = [0] * n_arms
    t = 0
    capacidad_por_segundo = 0.5  # ejemplo: 1800 veh/h = 0.5 veh/s capacidad de paso

    if log is not None:
        log.append(f"Simulación iniciada: tiempo={sim_time}s, ciclo_total={sum(p.green_time for p in intersection.phases)}s")
        for i, lam in enumerate(arrivals):
            log.append(f"Brazo {i+1}: flujo de llegada = {lam} veh/h")

    while t < sim_time:
        # Llegadas
        for idx, lam in enumerate(arrivals):
            p_llegada = lam / 3600
            if np.random.rand() < p_llegada:
                colas[idx].append(t)
                if log is not None:
                    log.append(f"{t}s: Vehículo LLEGÓ en Brazo {idx+1}, cola actual={len(colas[idx])}")

        # Fases semafóricas
        for phase in intersection.phases:
            verde = phase.green_time
            brazos_activos = phase.arms_active
            for seg in range(verde):
                for brazo in brazos_activos:
                    if len(colas[brazo]) > 0:
                        if np.random.rand() < capacidad_por_segundo:
                            tiempo_llegada = colas[brazo].pop(0)
                            demora_veh = t - tiempo_llegada
                            demoras[brazo].append(demora_veh)
                            if log is not None:
                                log.append(f"{t}s: Vehículo ATENDIDO en Brazo {brazo+1}, demora={demora_veh:.1f}s, cola restante={len(colas[brazo])}")
                # Actualizar máximo de la cola por brazo
                for i in range(n_arms):
                    max_cola[i] = max(max_cola[i], len(colas[i]))
                yield env.timeout(1)
                t += 1

        # Log estado de colas cada 60s
        if log is not None and t % 60 == 0:
            estado_colas = ", ".join([f"B{i+1}: {len(cola)}" for i, cola in enumerate(colas)])
            log.append(f"{t}s: Estado colas: {estado_colas}")

    # Resultados
    out['demora_prom'] = [np.mean(d) if d else 0 for d in demoras]
    out['cola_max'] = max_cola
    out['atendidos'] = [len(d) for d in demoras]

    if log is not None:
        log.append("Simulación finalizada.")
        log.append(f"Demoras promedio: {out['demora_prom']}")
        log.append(f"Colas máximas: {out['cola_max']}")
        log.append(f"Vehículos atendidos: {out['atendidos']}")
