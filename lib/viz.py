"""Visualizaciones del Taller 4.

Mezcla Plotly (gráficas estadísticas) y pyvis (red interactiva embebida en HTML).
Paleta consistente con la app del Grupo B.
"""

from __future__ import annotations

import math
from collections import Counter

import networkx as nx
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from pyvis.network import Network


COLOR_POR_TIPO = {
    "banco": "#1f77b4",        # azul
    "urbanizadora": "#d62728", # rojo
    "familia": "#ff7f0e",      # naranja
    "individuo": "#7f7f7f",    # gris
}

COLOR_OBSERVADA = "#1f77b4"
COLOR_BA = "#d62728"
COLOR_ER = "#7f7f7f"


def red_pyvis(
    G: nx.DiGraph,
    color_por: str = "tipo",
    altura: int = 600,
    mostrar_label_desde_grado: int = 8,
    nodos_destacados: set | None = None,
    layout_precomputado: bool = True,
    escala_layout: float = 1200.0,
) -> str:
    """HTML interactivo de la red (pyvis/vis.js).

    Con `layout_precomputado=True` (default), el layout se calcula en Python
    con `nx.spring_layout` y se pasa fijo a pyvis con físicas desactivadas.
    Esto evita que el navegador haga la simulación cliente — crítico para
    N > 200 nodos.
    """
    net = Network(
        height=f"{altura}px",
        width="100%",
        bgcolor="#ffffff",
        font_color="#222",
        notebook=False,
        directed=True,
        cdn_resources="remote",
    )

    grados = {n: G.in_degree(n) + G.out_degree(n) for n in G.nodes}
    g_max = max(grados.values()) if grados else 1

    pos = None
    if layout_precomputado:
        try:
            n_nodos = G.number_of_nodes()
            pos = nx.spring_layout(
                G,
                seed=42,
                k=3.0 / (n_nodos ** 0.5),
                iterations=200,
            )
        except Exception:
            pos = None

    destacados_int = {int(x) for x in (nodos_destacados or set())}
    for n, attrs in G.nodes(data=True):
        nid = int(n)
        tipo = attrs.get("tipo", "individuo")
        nombre = attrs.get("nombre", str(n))
        d = int(grados[n])
        color = COLOR_POR_TIPO.get(tipo, "#888")
        if nid in destacados_int:
            color = "#9b59b6"
        label = nombre if d >= mostrar_label_desde_grado else " "
        node_kwargs = dict(
            label=label,
            title=f"<b>{nombre}</b><br>tipo: {tipo}<br>grado: {d} (in={int(G.in_degree(n))}, out={int(G.out_degree(n))})",
            size=float(6 + (d / max(1, g_max)) * 25),
            color=color,
            borderWidth=1,
            font={"size": 12, "face": "Inter, Arial"},
        )
        if pos is not None and n in pos:
            x, y = pos[n]
            node_kwargs["x"] = float(x * escala_layout)
            node_kwargs["y"] = float(-y * escala_layout)
            node_kwargs["physics"] = False
        net.add_node(nid, **node_kwargs)

    pesos = [d.get("peso", 1) for _, _, d in G.edges(data=True)]
    if pesos:
        log_pesos = np.log10(np.clip(pesos, 1, None))
        p_min, p_max = float(np.min(log_pesos)), float(np.max(log_pesos))
    else:
        p_min, p_max = 0, 1

    for u, v, data in G.edges(data=True):
        peso = float(data.get("peso", 1))
        lp = math.log10(max(peso, 1))
        ancho = float(0.3 + (lp - p_min) / max(0.01, p_max - p_min) * 3)
        net.add_edge(
            int(u),
            int(v),
            title=f"valor: ${peso:,.0f}",
            width=ancho,
            color={"color": "#bbb", "opacity": 0.5},
            arrows="to",
        )

    if layout_precomputado and pos is not None:
        net.toggle_physics(False)
        opciones = """
        {
          "physics": {
            "enabled": false,
            "stabilization": {"enabled": false, "iterations": 0, "fit": false}
          },
          "interaction": {
            "hover": true, "tooltipDelay": 100, "navigationButtons": true,
            "dragNodes": true, "zoomView": true, "dragView": true
          },
          "nodes": {"shape": "dot", "scaling": {"min": 4, "max": 35}},
          "edges": {"smooth": {"enabled": false}},
          "layout": {"improvedLayout": false}
        }
        """
    else:
        opciones = """
        {
          "physics": {
            "solver": "barnesHut",
            "barnesHut": {
              "gravitationalConstant": -2500,
              "centralGravity": 0.2,
              "springLength": 100,
              "springConstant": 0.04,
              "damping": 0.4,
              "avoidOverlap": 0.6
            },
            "stabilization": {"enabled": true, "iterations": 150}
          },
          "interaction": {
            "hover": true, "tooltipDelay": 100, "navigationButtons": true,
            "dragNodes": true
          },
          "nodes": {"shape": "dot", "scaling": {"min": 4, "max": 35}},
          "edges": {"smooth": {"enabled": true, "type": "continuous"}}
        }
        """
    net.set_options(opciones)
    return net.generate_html(notebook=False)


def hist_grado(grados, k_promedio: float | None = None) -> go.Figure:
    fig = go.Figure()
    arr = np.asarray(list(grados), dtype=float)
    n_bins = min(40, int(arr.max()) + 1) if len(arr) else 10
    fig.add_trace(
        go.Histogram(
            x=arr,
            nbinsx=n_bins,
            marker_color=COLOR_OBSERVADA,
            opacity=0.85,
        )
    )
    if k_promedio is not None:
        fig.add_vline(
            x=k_promedio,
            line_dash="dash",
            line_color="red",
            annotation_text=f"⟨k⟩ = {k_promedio:.2f}",
            annotation_position="top right",
        )
    fig.update_layout(
        xaxis_title="Grado k",
        yaxis_title="Número de nodos",
        margin=dict(b=10, l=10, r=10, t=20),
        height=380,
    )
    return fig


def hist_betweenness(valores) -> go.Figure:
    """Histograma genérico para valores de betweenness (floats en [0, 1])."""
    arr = np.asarray(list(valores), dtype=float)
    fig = go.Figure()
    fig.add_trace(
        go.Histogram(
            x=arr,
            nbinsx=40,
            marker_color=COLOR_OBSERVADA,
            opacity=0.85,
        )
    )
    fig.update_layout(
        xaxis_title="Betweenness (normalizada)",
        yaxis_title="Número de nodos",
        margin=dict(b=10, l=10, r=10, t=20),
        height=340,
    )
    return fig


def degree_dist_loglog(
    df: pd.DataFrame, gamma: float | None = None, intercepto: float | None = None
) -> go.Figure:
    fig = go.Figure()
    df_pos = df[df["k"] > 0].copy()
    fig.add_trace(
        go.Scatter(
            x=df_pos["k"],
            y=df_pos["p_k"],
            mode="markers",
            marker=dict(size=8, color=COLOR_OBSERVADA),
            name="Observada",
        )
    )
    if gamma is not None and intercepto is not None and len(df_pos) >= 2:
        ks = np.linspace(df_pos["k"].min(), df_pos["k"].max(), 50)
        ps = 10 ** (intercepto - gamma * np.log10(ks))
        fig.add_trace(
            go.Scatter(
                x=ks,
                y=ps,
                mode="lines",
                line=dict(color="red", dash="dash"),
                name=f"Ajuste γ = {gamma:.2f}",
            )
        )
    fig.update_xaxes(type="log", title="k (log)")
    fig.update_yaxes(type="log", title="p_k (log)")
    fig.update_layout(
        legend=dict(orientation="h", y=-0.2),
        margin=dict(b=10, l=10, r=10, t=20),
        height=400,
    )
    return fig


def hist_componentes(tamanos: list[int]) -> go.Figure:
    conteo = Counter(tamanos)
    df = pd.DataFrame(sorted(conteo.items()), columns=["tamano", "n_componentes"])
    fig = go.Figure(
        go.Bar(
            x=df["tamano"].astype(str),
            y=df["n_componentes"],
            marker_color=COLOR_OBSERVADA,
        )
    )
    fig.update_layout(
        xaxis_title="Tamaño del componente (nodos)",
        yaxis_title="Número de componentes con ese tamaño",
        margin=dict(b=10, l=10, r=10, t=20),
        height=340,
    )
    return fig


def subgrafo_top3_html(G: nx.DiGraph, top3: list[int], altura: int = 480) -> str:
    H = G.to_undirected()
    nodos = set(top3)
    for n in top3:
        nodos.update(H.neighbors(n))
    sub = G.subgraph(nodos).copy()
    return red_pyvis(
        sub,
        altura=altura,
        mostrar_label_desde_grado=0,
        nodos_destacados=set(top3),
    )


def comparacion_modelos_loglog(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    color_map = {
        "Observada": COLOR_OBSERVADA,
        "ER (mismo L)": COLOR_ER,
    }
    estilos = {"Observada": "markers", "ER (mismo L)": "markers"}
    for modelo in df["modelo"].unique():
        sub = df[(df["modelo"] == modelo) & (df["k"] > 0)]
        color = color_map.get(modelo, COLOR_BA)
        fig.add_trace(
            go.Scatter(
                x=sub["k"],
                y=sub["p_k"],
                mode=estilos.get(modelo, "markers"),
                marker=dict(size=7, color=color),
                name=modelo,
            )
        )
    fig.update_xaxes(type="log", title="k (log)")
    fig.update_yaxes(type="log", title="p_k (log)")
    fig.update_layout(
        legend=dict(orientation="h", y=-0.2),
        margin=dict(b=10, l=10, r=10, t=20),
        height=450,
    )
    return fig


def hist_pesos(pesos: list[float]) -> go.Figure:
    fig = go.Figure()
    pos = [p for p in pesos if p > 0]
    fig.add_trace(
        go.Histogram(
            x=np.log10(pos),
            nbinsx=40,
            marker_color=COLOR_OBSERVADA,
            opacity=0.85,
        )
    )
    fig.update_layout(
        xaxis_title="log₁₀(peso) [pesos colombianos]",
        yaxis_title="Número de transacciones",
        margin=dict(b=10, l=10, r=10, t=20),
        height=340,
    )
    return fig


def bar_clustering(C_obs: float, C_er: float, C_promedio_local: float) -> go.Figure:
    fig = go.Figure(
        go.Bar(
            x=["C_global observado", "C_global ER (referencia)", "⟨C_i⟩ local promedio"],
            y=[C_obs, C_er, C_promedio_local],
            marker_color=[COLOR_OBSERVADA, COLOR_ER, "#ff7f0e"],
        )
    )
    fig.update_layout(
        yaxis_title="Coeficiente de clustering",
        margin=dict(b=10, l=10, r=10, t=20),
        height=340,
    )
    return fig
