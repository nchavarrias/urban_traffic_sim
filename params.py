# params.py
def get_arrival_rates(n_arms, sidebar):
    return [sidebar.slider(f"Flujo brazo {i+1} (veh/h)", 50, 1200, 400) for i in range(n_arms)]

def get_sim_time(sidebar):
    return sidebar.slider("Duración simulación (s)", 600, 3600, 1800)
