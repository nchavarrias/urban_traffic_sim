import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

def draw_intersection(n_arms=4, phases=None, active_phase=None):
    """
    Dibuja un diagrama esquemático del cruce con n brazos.
    Colorea los brazos activos en la fase (si se indica active_phase).
    """
    fig, ax = plt.subplots(figsize=(4, 4))
    angles = np.linspace(0, 2 * np.pi, n_arms, endpoint=False)
    for idx, angle in enumerate(angles):
        x = [0, np.cos(angle)]
        y = [0, np.sin(angle)]
        color = "tab:blue"
        # Destaca brazos de la fase activa
        if active_phase is not None and idx in active_phase.arms_active:
            color = "tab:red"
        ax.plot(x, y, lw=12, color=color, solid_capstyle="round")
        # Marca los números de brazo
        ax.text(1.25 * np.cos(angle), 1.25 * np.sin(angle), f"B{idx + 1}", ha="center", va="center", fontsize=14)
    ax.set_xlim(-1.6, 1.6)
    ax.set_ylim(-1.6, 1.6)
    ax.axis("off")
    plt.tight_layout()
    st.pyplot(fig)

def plot_bar_metric(df, col, title):
    st.bar_chart(df.set_index("Brazo")[col])
    st.markdown(f"**{title}**")

def summary_stats(series):
    return {
        "Media": round(series.mean(), 2),
        "Máximo": int(series.max()),
        "Mínimo": int(series.min()),
        "Desv. típica": round(series.std(), 2)
    }

def show_stats(df):
    st.markdown("### Resumen Estadístico")
    for col in ["Demora promedio (s)", "Cola máxima", "Atendidos", "Saturación"]:
        if col in df.columns:
            stats = summary_stats(df[col])
            st.markdown(f"#### {col}")
            for k, v in stats.items():
                st.write(f"- {k}: {v}")

def executive_summary_and_advice(df, segundos_verde, intersection, ciclo):
    """
    Genera recomendaciones precisas y cuantificadas para mejorar la operación del cruce,
    priorizando brazos/fases saturadas y con problemas críticos.
    """

    # Umbrales parametrizables
    umbral_saturacion_alta = 0.85
    incremento_verde = 10  # segundos a aumentar en verde cuando se recomienda
    incremento_ciclo = 10  # segundos a aumentar en ciclo cuando se recomienda

    # Identificar brazos/fases problemáticas
    brazos_saturados = []
    fases_a_mejorar = set()
    for i, sat in enumerate(df["Saturación"]):
        if sat >= umbral_saturacion_alta:
            brazos_saturados.append((i, sat))
            # Asociar brazo con fase(s)
            for j, phase in enumerate(intersection.phases):
                if i in phase.arms_active:
                    fases_a_mejorar.add(j)

    # Identificar brazo con mayor demora
    idx_brazo_demora = df["Demora promedio (s)"].idxmax()
    brazo_mayor_demora = df.loc[idx_brazo_demora, "Brazo"]
    demora_max = df.loc[idx_brazo_demora, "Demora promedio (s)"]

    consejo = ""

    # Caso 1: Hay saturación alta (prioridad principal)
    if brazos_saturados:
        fases_str = ", ".join([f"'{intersection.phases[j].name}'" for j in fases_a_mejorar])
        consejo += f"Brazo(s) saturado(s): "
        consejo += ", ".join([f"Brazo {b+1} (S={sat:.2f})" for b, sat in brazos_saturados]) + ". "
        consejo += f"Recomiendo aumentar el tiempo verde en fase(s) {fases_str} en {incremento_verde} segundos "
        consejo += f"y extender el ciclo total a {ciclo + incremento_ciclo} segundos."

    # Caso 2: Sin saturación pero con demora muy alta
    elif demora_max > 1200:  # más de 20 minutos demora alta
        # Buscar fase que atiende ese brazo
        fases_demora = [j for j, phase in enumerate(intersection.phases) if idx_brazo_demora in phase.arms_active]
        if fases_demora:
            f = intersection.phases[fases_demora[0]]
            tiempo_actual = segundos_verde[fases_demora[0]]
            consejo += (f"Brazo con mayor demora ({demora_max:.0f}s) es {brazo_mayor_demora}. "
                        f"Sube {incremento_verde} segundos el verde en fase '{f.name}' (actualmente {tiempo_actual}s) "
                        "o considera aumentar el ciclo.")
        else:
            consejo += f"Brazo con mayor demora ({demora_max:.0f}s) es {brazo_mayor_demora}, revisa tiempos verdes."

    # Caso 3: Sin problemas graves
    else:
        consejo += "El cruce opera bien. Puedes probar a reducir ligeramente el ciclo para mejorar la fluidez."

    return consejo

def detailed_problem_description(df, segundos_verde, intersection, ciclo):
    """
    Devuelve una descripción clara de los brazos con mayores problemas,
    explicando por qué son problemáticos usando métricas relevantes.
    """
    # Identificar brazos con peor demora, cola y porcentaje atendido
    brazo_peor_demora = df.iloc[df["Demora promedio (s)"].idxmax()]
    brazo_peor_cola = df.iloc[df["Cola máxima"].idxmax()]
    brazo_menor_atendidos = df.iloc[df["Atendidos"].idxmin()]

    texto = f"### Análisis detallado de problemas por brazo\n\n"

    # Descripción demora
    texto += (f"- **{brazo_peor_demora['Brazo']}** tiene la mayor demora promedio "
              f"({brazo_peor_demora['Demora promedio (s)']:.1f} s), indicando que los vehículos "
              "esperan mucho antes de cruzar.\n")

    # Buscar fase responsable (que abre ese brazo)
    idx_fase_demora = None
    for i, phase in enumerate(intersection.phases):
        if int(brazo_peor_demora['Brazo'].split()[-1]) - 1 in phase.arms_active:
            idx_fase_demora = i
            break
    tiempo_verde_demora = segundos_verde[idx_fase_demora] if idx_fase_demora is not None else 0
    texto += (f"  Esto puede ser por un tiempo verde reducido en la fase "
              f"\"{intersection.phases[idx_fase_demora].name}\" ({tiempo_verde_demora}s).\n\n")

    # Descripción cola máxima
    texto += (f"- **{brazo_peor_cola['Brazo']}** presenta la cola máxima de "
              f"{brazo_peor_cola['Cola máxima']} vehículos, lo que sugiere congestión considerable "
              "y posibilidad de bloqueo upstream.\n\n")

    # Descripción vehículos atendidos
    texto += (f"- **{brazo_menor_atendidos['Brazo']}** tiene el menor número de vehículos "
              f"servidos ({brazo_menor_atendidos['Atendidos']} veh.), lo que puede indicar saturación "
              "o insuficiente tiempo verde asignado.\n\n")

    texto += ("Recomendación: Revisa los tiempos verdes asignados a las fases relacionadas con estos "
              "brazos para mejorar el flujo y reducir demoras.\n")

    # Información sobre el ciclo total
    texto += f"\nEl ciclo total del cruce es de {ciclo} segundos."

    return texto

def assign_verde_por_brazo(intersection, segundos_verde):
    """
    Suma para cada brazo el tiempo verde total acumulado según las fases que lo atienden.
    """
    n_brazos = intersection.n_arms
    tiempo_verde_brazo = [0] * n_brazos
    for i, phase in enumerate(intersection.phases):
        for brazo in phase.arms_active:
            tiempo_verde_brazo[brazo] += segundos_verde[i]
    return tiempo_verde_brazo
