# main.py
import streamlit as st
import simpy
from intersection import model_plus, model_tee, model_star
from simulation import simulate_intersection
from params import get_arrival_rates, get_sim_time
import pandas as pd

# Selección de modelo
modelo = st.sidebar.selectbox("Modelo de cruce", ["X / +", "T", "Estrella"])
if modelo == "X / +":
    intersection = model_plus(4)
elif modelo == "T":
    intersection = model_tee()
elif modelo == "Estrella":
    intersection = model_star()

# Parámetros de entrada
arrivals = get_arrival_rates(intersection.n_arms, st.sidebar)
sim_time = get_sim_time(st.sidebar)

# Simulación
resultados = {}
if st.button("Simular"):
    env = simpy.Environment()
    env.process(simulate_intersection(env, intersection, arrivals, sim_time, resultados))
    env.run()
    df = pd.DataFrame({
        "Brazo": [f"Brazo {i+1}" for i in range(intersection.n_arms)],
        "Demora promedio (s)": resultados['demora_prom'],
        "Cola máxima": resultados['cola_max'],
        "Atendidos": resultados['atendidos']
    })
    st.dataframe(df)
    st.bar_chart(df.set_index("Brazo")["Demora promedio (s)"])
    st.bar_chart(df.set_index("Brazo")["Cola máxima"])
    st.bar_chart(df.set_index("Brazo")["Atendidos"])
    # Puedes añadir gráficos de evolución temporal, animaciones, etc.

st.markdown("Selecciona distintas configuraciones, tiempos y tasas de llegada para explorar el impacto en demoras y uso de la intersección.")
