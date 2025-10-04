import streamlit as st
import simpy
import numpy as np
import pandas as pd
from intersection import model_plus, model_tee, model_star
from simulation import simulate_intersection
from params import get_arrival_rates, get_sim_time
from utils import (
    draw_intersection, 
    plot_bar_metric, 
    show_stats, 
    executive_summary_and_advice,
    detailed_problem_description
)

# --- SELECCIÓN DE MODELO DE CRUCE ---
st.title("Simulador de Tráfico Urbano por Cruce Multi-Fase")
modelo = st.sidebar.selectbox("Modelo de cruce", ["X / +", "T", "Estrella"])
if modelo == "X / +":
    intersection = model_plus(4)
elif modelo == "T":
    intersection = model_tee()
elif modelo == "Estrella":
    intersection = model_star()

n_arms = intersection.n_arms
n_fases = len(intersection.phases)

# --- CONFIGURACIÓN DE CICLO Y VERDES ---
ciclo = st.sidebar.slider("Ciclo semafórico total (s)", 20, 180, 90)
st.sidebar.markdown("##### Proporción de verde por fase (%)")
verdes = []
proporcion_total = 0
for idx, phase in enumerate(intersection.phases):
    value = st.sidebar.slider(
        f"{phase.name} (%)", 0, 100, int(100 / n_fases), key=f"v_{idx}"
    )
    verdes.append(value)
    proporcion_total += value

if proporcion_total > 100:
    st.sidebar.error(f"¡La suma de proporciones supera el 100% ({proporcion_total}%)!")
else:
    st.sidebar.success(f"Suma total: {proporcion_total}%")

# Asignar segundos reales a cada fase
segundos_verde = [int(ciclo * verde / 100) for verde in verdes]
for idx, phase in enumerate(intersection.phases):
    phase.green_time = segundos_verde[idx]
    st.sidebar.markdown(f"**{phase.name}**: {verdes[idx]}% → {segundos_verde[idx]}s")

# --- CONFIGURACIÓN DE FLUJOS POR BRAZO ---
llegadas = [st.sidebar.slider(f"Flujo brazo {i+1} (veh/h)", 50, 1200, 400) for i in range(n_arms)]

# --- DIAGRAMA DEL CRUCE ---
st.markdown("### Esquema del cruce y fases")
selected_fase = st.selectbox(
    "Visualiza o resalta la fase:", 
    range(n_fases),
    format_func=lambda i: intersection.phases[i].name
)
draw_intersection(
    n_arms=intersection.n_arms,
    phases=intersection.phases,
    active_phase=intersection.phases[selected_fase]
)

st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("### Configuración actual del cruce")
for idx, phase in enumerate(intersection.phases):
    acc = ', '.join([f"Brazo {i+1}" for i in phase.arms_active])
    st.markdown(f"- **{phase.name}**: {segundos_verde[idx]}s (<span style='color:red'>{acc}</span>)", unsafe_allow_html=True)

# --- DURACIÓN DE SIMULACIÓN Y BOTÓN ---
sim_time = st.slider("Duración de simulación total (s)", 600, 3600, 1800)
resultados = {}

# --- EJECUCIÓN DE SIMULACIÓN ---
if st.button("Ejecutar simulación", disabled=(proporcion_total > 100)):
    env = simpy.Environment()
    env.process(simulate_intersection(env, intersection, llegadas, sim_time, resultados))
    env.run()
    df = pd.DataFrame({
        "Brazo": [f"Brazo {i+1}" for i in range(n_arms)],
        "Demora promedio (s)": resultados['demora_prom'],
        "Cola máxima": resultados['cola_max'],
        "Atendidos": resultados['atendidos']
    })
    st.markdown("### Métricas por brazo")
    st.dataframe(df)
    plot_bar_metric(df, "Demora promedio (s)", "Demora media por brazo")
    plot_bar_metric(df, "Cola máxima", "Cola máxima por brazo")
    plot_bar_metric(df, "Atendidos", "Vehículos atendidos por brazo")
    show_stats(df)

    consejo = executive_summary_and_advice(df, segundos_verde, intersection, ciclo)
    st.markdown(f"### Consejo ejecutivo")
    st.info(consejo)

    descripcion_problemas = detailed_problem_description(df, segundos_verde, intersection, ciclo)
    st.markdown(descripcion_problemas)

else:
    st.info("Ajusta los parámetros y pulsa 'Ejecutar simulación' para ver resultados. No puedes simular si la suma de verdes supera el 100%.")

st.markdown("---")
st.markdown("Desarrollado para simulaciones de cruces urbanos. Modifica el modelo, el ciclo y los verdes para experimentar con diferentes estrategias semafóricas.")
