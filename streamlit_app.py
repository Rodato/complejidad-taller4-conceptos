"""Taller 4 — Conceptos básicos en la red de transacciones inmobiliarias.

App Streamlit para Universidad del Valle, curso Introducción a la Complejidad 2026-I.
Cubre los 9 ejercicios técnico-conceptuales sobre una red simulada de ~500
actores, calibrada a la Notaría 2 de Cali (1938–1943).
"""

from __future__ import annotations

import streamlit as st
import streamlit.components.v1 as components

from lib import metricas as m
from lib import teoria as t
from lib import viz as v
from lib.simulacion import generar_red, resumen
from lib.storage import (
    crear_fila_estudiante,
    guardar_respuesta,
    modo_almacenamiento,
)


st.set_page_config(
    page_title="Taller 4 — Conceptos básicos de redes",
    page_icon="🕸️",
    layout="wide",
)


@st.cache_data(show_spinner="Generando red simulada...")
def _red_cacheada(seed: int, n_total: int):
    G = generar_red(seed=seed, n_total=n_total)
    return G


SEMILLA_FIJA = 42
N_TOTAL_FIJO = 500


def _init_state():
    defaults = {
        "nombre": "",
        "codigo": "",
        "companeros": "",
        "row_index": None,
        "identificado": False,
        "destino_storage": modo_almacenamiento(),
    }
    for k, val in defaults.items():
        st.session_state.setdefault(k, val)


def sidebar_identificacion():
    st.sidebar.header("Identificación")
    st.session_state["nombre"] = st.sidebar.text_input(
        "Tu nombre completo", value=st.session_state["nombre"]
    )
    st.session_state["codigo"] = st.sidebar.text_input(
        "Código (carnet)", value=st.session_state["codigo"]
    )
    st.session_state["companeros"] = st.sidebar.text_area(
        "Compañeros de equipo (opcional)",
        value=st.session_state["companeros"],
        height=80,
    )

    if not st.session_state["identificado"]:
        if st.sidebar.button("Empezar el taller", type="primary"):
            if not st.session_state["nombre"].strip():
                st.sidebar.error("Escribe tu nombre antes de empezar.")
            else:
                ok, err, destino, row = crear_fila_estudiante(
                    {
                        "nombre": st.session_state["nombre"],
                        "codigo": st.session_state["codigo"],
                        "companeros": st.session_state["companeros"],
                    }
                )
                if ok or row is not None:
                    st.session_state["row_index"] = row
                    st.session_state["identificado"] = True
                    st.session_state["destino_storage"] = destino
                    st.sidebar.success(f"Registrado ({destino}). ¡Sigue con los ejercicios!")
                if err:
                    st.sidebar.warning(err)
    else:
        st.sidebar.success(
            f"✓ Identificado como {st.session_state['nombre']}"
        )

    st.sidebar.divider()
    st.sidebar.caption(
        f"💾 Modo de guardado: **{st.session_state['destino_storage']}**"
        + ("" if st.session_state['destino_storage'] == 'sheets' else " (sin credenciales Sheets)")
    )


def _bloque_respuesta(ejercicio: str, label: str = "Tu interpretación") -> None:
    """Renderiza un text_area + botón Guardar para un ejercicio dado."""
    if not st.session_state["identificado"]:
        st.info("👈 Identifícate en la barra lateral para poder guardar tus respuestas.")
        return
    key = f"resp_{ejercicio}"
    texto = st.text_area(label, key=key, height=140, placeholder="Escribe aquí tu interpretación...")
    if st.button(f"Guardar respuesta — {ejercicio}", key=f"btn_{ejercicio}"):
        if not texto.strip():
            st.warning("Escribe algo antes de guardar.")
            return
        ok, err, destino = guardar_respuesta(
            st.session_state["row_index"], ejercicio, texto
        )
        if ok:
            st.success(f"Guardado en {destino}.")
        else:
            st.warning(f"Falló: {err}")


# ===================== TABS =====================

def tab_ej1(G):
    st.markdown(f"### Ejercicio 1 — {t.EJ1_ENUNCIADO}")
    st.markdown(t.EJ1_INTRO)
    st.latex(t.EJ1_FORMULA)
    st.markdown(t.EJ1_INTRO_DIR)
    st.latex(t.EJ1_FORMULA_DIR)

    r = m.grado_promedio(G)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("N (nodos)", r["N"])
    col2.metric("L (aristas)", r["L"])
    col3.metric("⟨k⟩ no dirigida", f"{r['k_promedio_no_dirigida']:.2f}")
    col4.metric("⟨k_in⟩ = ⟨k_out⟩", f"{r['k_in_promedio']:.2f}")

    st.markdown(f"- **Densidad** (fracción de aristas posibles realizadas): `{r['densidad']:.4f}`")
    st.markdown(f"- **k máximo** observado: `{r['k_max_no_dir']}`")

    st.divider()
    st.subheader("Histograma de grado")
    H = G.to_undirected()
    grados = [d for _, d in H.degree()]
    st.plotly_chart(v.hist_grado(grados, r["k_promedio_no_dirigida"]), width="stretch")

    st.divider()
    st.markdown(t.EJ1_INTERPRETACION)
    _bloque_respuesta("ej1")


def tab_ej2(G):
    st.markdown(f"### Ejercicio 2 — {t.EJ2_ENUNCIADO}")
    st.markdown(t.EJ2_INTRO)
    st.latex(t.EJ2_FORMULA)

    r = m.distribucion_grado(G)
    col1, col2 = st.columns(2)
    if r["gamma_estimado"] is not None:
        col1.metric("γ estimado (pendiente log-log)", f"{r['gamma_estimado']:.2f}")
    col2.metric("Grado máximo", int(r["df"]["k"].max()))

    st.subheader("Distribución observada")
    st.dataframe(r["df"][["k", "conteo", "p_k"]].head(20), width="stretch")

    st.subheader("Log-log con ajuste γ")
    st.plotly_chart(
        v.degree_dist_loglog(r["df"], r["gamma_estimado"], r["intercepto_loglog"]),
        width="stretch",
    )

    st.divider()
    st.markdown(t.EJ2_INTERPRETACION)
    _bloque_respuesta("ej2")


def tab_ej3(G):
    st.markdown(f"### Ejercicio 3 — {t.EJ3_ENUNCIADO}")
    st.markdown(t.EJ3_INTRO)
    st.latex(t.EJ3_FORMULA)

    df = m.centralidad_grado(G, top=10)
    st.subheader("Top 10 actores por grado total")
    st.dataframe(
        df[["nombre", "tipo", "grado_in", "grado_out", "grado_total", "C_grado_norm"]],
        width="stretch",
    )

    st.divider()
    st.markdown(t.EJ3_INTERPRETACION)
    _bloque_respuesta("ej3")


def tab_ej4(G):
    st.markdown(f"### Ejercicio 4 — {t.EJ4_ENUNCIADO}")
    st.markdown(t.EJ4_INTRO)
    st.latex(t.EJ4_FORMULA)

    with st.spinner("Calculando betweenness (puede tardar unos segundos)..."):
        r = m.betweenness_componente_gigante(G, top=10)

    col1, col2 = st.columns(2)
    col1.metric("Tamaño componente gigante", r["tamano"])
    col2.metric("Fracción del total", f"{r['tamano'] / G.number_of_nodes():.0%}")

    st.subheader("Top 10 por betweenness (intermediación)")
    st.dataframe(
        r["df_top"][["nombre", "tipo", "betweenness", "grado_total"]],
        width="stretch",
    )

    st.subheader("Distribución completa de betweenness")
    st.plotly_chart(
        v.hist_betweenness(r["df_completo"]["betweenness"].values),
        width="stretch",
    )

    st.divider()
    st.markdown(t.EJ4_INTERPRETACION)
    _bloque_respuesta("ej4")


def tab_ej5(G):
    st.markdown(f"### Ejercicio 5 — {t.EJ5_ENUNCIADO}")
    st.markdown(t.EJ5_INTRO)

    r = m.componentes(G)
    col1, col2, col3 = st.columns(3)
    col1.metric("# componentes débiles", r["n_weakly"])
    col2.metric("# componentes fuertes", r["n_strongly"])
    col3.metric("# nodos aislados", r["n_aislados"])

    veredicto = "**no conexa**" if not r["es_conexa_debil"] else "**conexa**"
    st.markdown(
        f"La red es {veredicto} (débilmente). "
        f"El componente gigante tiene **{r['tamano_gigante']}** nodos "
        f"({r['tamano_gigante'] / G.number_of_nodes():.0%} del total)."
    )

    st.subheader("Distribución de tamaños de componente (débilmente conectados)")
    st.plotly_chart(v.hist_componentes(r["tamanos_weakly"]), width="stretch")

    st.divider()
    st.markdown(t.EJ5_INTERPRETACION)
    _bloque_respuesta("ej5")


def tab_ej6(G):
    st.markdown(f"### Ejercicio 6 — {t.EJ6_ENUNCIADO}")
    st.markdown(t.EJ6_INTRO)
    st.latex(t.EJ6_FORMULA)

    r = m.clustering_local_top3(G)
    st.subheader("Los 3 nodos más conectados (grado total)")
    st.dataframe(r["df"], width="stretch")

    st.subheader("¿Están conectados entre sí?")
    for par in r["pares"]:
        a, b = par["par"]
        estado = "✅ conectados directamente" if par["conectados"] else "❌ no conectados directamente"
        st.markdown(
            f"- **{a}** ↔ **{b}**: {estado} · vecinos comunes: **{par['vecinos_comunes']}**"
        )

    st.subheader("Subgrafo: los 3 más conectados y sus vecinos")
    top3_ids = [fila["nodo"] for fila in r["filas_top3"]]
    html = v.subgrafo_top3_html(G, top3_ids, altura=500)
    components.html(html, height=520, scrolling=False)

    st.divider()
    st.markdown(t.EJ6_INTERPRETACION)
    _bloque_respuesta("ej6")


def tab_ej7(G):
    st.markdown(f"### Ejercicio 7 — {t.EJ7_ENUNCIADO}")
    st.markdown(t.EJ7_INTRO)
    st.latex(t.EJ7_FORMULA)

    st.warning(t.EJ7_NOTA_BARABASI)

    r = m.clustering_global(G)
    col1, col2, col3 = st.columns(3)
    col1.metric("# triángulos", r["triangulos"])
    col2.metric("# triples conectados", f"{r['triples_conectados']:,}")
    col3.metric("C_global (fórmula)", f"{r['C_global_formula']:.4f}")

    col4, col5, col6 = st.columns(3)
    col4.metric("C_global (NetworkX)", f"{r['C_global_nx']:.4f}")
    col5.metric("⟨C_i⟩ local promedio", f"{r['C_promedio_local']:.4f}")
    col6.metric("C_global ER referencia", f"{r['C_global_ER_referencia']:.4f}")

    if r["ratio_observado_vs_ER"] is not None:
        st.markdown(
            f"**La red observada tiene ~{r['ratio_observado_vs_ER']:.1f}× más clustering "
            f"que un Erdős–Rényi del mismo tamaño.** "
            f"Eso es la firma de fuerzas sociales que cierran triángulos."
        )

    st.plotly_chart(
        v.bar_clustering(
            r["C_global_nx"], r["C_global_ER_referencia"], r["C_promedio_local"]
        ),
        width="stretch",
    )

    st.divider()
    st.markdown(t.EJ7_INTERPRETACION)
    _bloque_respuesta("ej7")


def tab_ej8(G):
    st.markdown(f"### Ejercicio 8 — {t.EJ8_ENUNCIADO}")
    st.markdown(t.EJ8_INTRO)

    r = m.direccion_y_peso(G)
    col1, col2, col3 = st.columns(3)
    col1.metric("# transacciones", r["n_aristas"])
    col2.metric("Peso mediano", f"${r['peso_mediano']:,.0f}")
    col3.metric("Total ponderado", f"${r['total_ponderado']:,.0f}")

    st.subheader("Top 10 transacciones por valor")
    st.dataframe(
        r["df_top_transacciones"].style.format({"peso": "${:,.0f}"}),
        width="stretch",
    )

    st.subheader("Actores con mayor asimetría in-out")
    st.dataframe(
        r["df_asimetria_top"][["nombre", "tipo", "grado_in", "grado_out", "asimetria"]],
        width="stretch",
    )

    st.subheader("Distribución del logaritmo del peso")
    pesos = [d["peso"] for _, _, d in G.edges(data=True)]
    st.plotly_chart(v.hist_pesos(pesos), width="stretch")

    st.divider()
    st.markdown(t.EJ8_INTERPRETACION)
    _bloque_respuesta("ej8")


def tab_ej9(G):
    st.markdown(f"### Ejercicio 9 — {t.EJ9_ENUNCIADO}")
    st.markdown(t.EJ9_INTRO)
    st.latex(t.EJ9_FORMULA)

    r = m.vinculacion_preferencial(G)
    col1, col2, col3 = st.columns(3)
    col1.metric("γ observado", f"{r['gamma_observado']:.2f}" if r["gamma_observado"] else "—")
    col2.metric(f"γ BA (m={r['m_usado_ba']})", f"{r['gamma_ba']:.2f}" if r["gamma_ba"] else "—")
    col3.metric("γ ER", f"{r['gamma_er']:.2f}" if r["gamma_er"] else "—")

    st.subheader("Comparación log-log: observada vs BA vs ER")
    st.plotly_chart(v.comparacion_modelos_loglog(r["df_comparacion"]), width="stretch")

    st.markdown("""
    **Interpretación rápida:** si la curva observada se parece a la de **BA**
    (cola heavy-tailed, pendiente negativa marcada) y es muy distinta de la
    de **ER** (pico estrecho, sin cola), entonces la hipótesis de vinculación
    preferencial tiene sustento empírico.
    """)

    st.divider()
    st.markdown(t.EJ9_INTERPRETACION)
    _bloque_respuesta("ej9")


def tab_red(G):
    st.markdown("### 🕸️ Explora la red")
    st.markdown(
        "Antes de calcular cualquier medida, **mira la red**. "
        "Esta es la base sobre la que harás los 9 ejercicios."
    )
    col1, col2, col3, col4 = st.columns(4)
    col1.markdown("🔵 **Bancos**")
    col2.markdown("🔴 **Urbanizadoras**")
    col3.markdown("🟠 **Familias notables**")
    col4.markdown("⚪ **Individuos**")
    st.caption(
        "Arrastra los nodos para moverlos · Acerca con la rueda del mouse · "
        "Pasa el cursor sobre un nodo para ver su nombre, tipo y grado · "
        "El tamaño del nodo es proporcional a su grado total · "
        "El grosor de la arista es proporcional al valor (en log) de la transacción"
    )
    html = v.red_pyvis(G, altura=650, mostrar_label_desde_grado=10)
    components.html(html, height=680, scrolling=False)

    st.divider()
    st.markdown("### Observa y anota")
    st.markdown(
        "Estas preguntas te ayudan a desarrollar **intuición** antes de calcular formalmente "
        "las medidas en los 9 ejercicios. Tu respuesta queda guardada y la podrás "
        "comparar con los resultados cuando termines:"
    )
    st.markdown(
        "- ¿Hay nodos muy grandes? ¿De qué tipo son?\n"
        "- ¿Ves grupos de nodos separados del resto?\n"
        "- ¿Las aristas son uniformes o hay unas mucho más gruesas que otras?\n"
        "- Si tuvieras que adivinar quién intermedia más entre actores, ¿por dónde apostarías?"
    )
    _bloque_respuesta("red", label="Lo que observo (en mis palabras)")


def tab_proyecto():
    st.markdown(t.PROYECTO_INTRO)
    st.divider()
    _bloque_respuesta("proyecto", label="Tu cierre")


# ===================== MAIN =====================

def main():
    _init_state()
    sidebar_identificacion()

    st.title("Taller 4 — Conceptos básicos en la red de transacciones inmobiliarias")
    st.caption(
        "Universidad del Valle · Introducción a la Complejidad 2026-I · "
        "Boris Salazar y Daniel Otero"
    )
    st.markdown(t.INTRO_GENERAL)

    G = _red_cacheada(SEMILLA_FIJA, N_TOTAL_FIJO)
    info = resumen(G)

    with st.expander("📋 Ficha de la red simulada", expanded=False):
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Nodos", info["N"])
        col2.metric("Aristas", info["L"])
        col3.metric("Componentes débiles", info["n_componentes_weakly"])
        col4.metric("Aislados", info["n_aislados"])
        st.markdown(
            f"**Tipos de actor:** "
            + ", ".join(f"{k}: {v}" for k, v in info["tipos"].items())
        )

    tabs = st.tabs(
        [
            "🕸️ La red",
            "1. ⟨k⟩",
            "2. p_k",
            "3. C. grado",
            "4. C. intermediación",
            "5. ¿Conexa?",
            "6. Clustering local",
            "7. Clustering global",
            "8. Dirigida/Ponderada",
            "9. Vinc. preferencial",
            "🎯 Para tu proyecto",
        ]
    )
    with tabs[0]:
        tab_red(G)
    with tabs[1]:
        tab_ej1(G)
    with tabs[2]:
        tab_ej2(G)
    with tabs[3]:
        tab_ej3(G)
    with tabs[4]:
        tab_ej4(G)
    with tabs[5]:
        tab_ej5(G)
    with tabs[6]:
        tab_ej6(G)
    with tabs[7]:
        tab_ej7(G)
    with tabs[8]:
        tab_ej8(G)
    with tabs[9]:
        tab_ej9(G)
    with tabs[10]:
        tab_proyecto()


if __name__ == "__main__":
    main()
