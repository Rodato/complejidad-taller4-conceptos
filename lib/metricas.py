"""Cálculo de las medidas del Taller 4.

Una función por ejercicio. Todas reciben un nx.DiGraph y devuelven datos
estructurados (dict, DataFrame) listos para mostrar en Streamlit.
"""

from __future__ import annotations

import math
from collections import Counter

import networkx as nx
import numpy as np
import pandas as pd


# ---------- Ejercicio 1: Grado promedio ⟨k⟩ ----------

def grado_promedio(G: nx.DiGraph) -> dict:
    N = G.number_of_nodes()
    L = G.number_of_edges()
    H = G.to_undirected()
    grados_no_dir = [d for _, d in H.degree()]
    k_no_dir = sum(grados_no_dir) / N if N else 0.0
    k_in = L / N if N else 0.0
    k_out = L / N if N else 0.0
    return {
        "N": N,
        "L": L,
        "k_promedio_no_dirigida": k_no_dir,
        "k_in_promedio": k_in,
        "k_out_promedio": k_out,
        "densidad": nx.density(G),
        "k_max_no_dir": max(grados_no_dir) if grados_no_dir else 0,
    }


# ---------- Ejercicio 2: Distribución de grado p_k ----------

def distribucion_grado(G: nx.DiGraph) -> dict:
    H = G.to_undirected()
    grados = [d for _, d in H.degree()]
    N = len(grados)
    conteo = Counter(grados)
    df = (
        pd.DataFrame(
            [(k, c, c / N) for k, c in sorted(conteo.items())],
            columns=["k", "conteo", "p_k"],
        )
        .assign(log_k=lambda d: np.log10(d["k"].replace(0, np.nan)))
        .assign(log_pk=lambda d: np.log10(d["p_k"]))
    )

    # Ajuste lineal en log-log sobre k >= 1 con p_k > 0
    df_fit = df.dropna(subset=["log_k", "log_pk"])
    df_fit = df_fit[df_fit["k"] > 0]
    gamma = None
    intercepto = None
    if len(df_fit) >= 3:
        coefs = np.polyfit(df_fit["log_k"], df_fit["log_pk"], 1)
        gamma = -coefs[0]
        intercepto = coefs[1]

    return {
        "df": df,
        "gamma_estimado": gamma,
        "intercepto_loglog": intercepto,
        "grados": grados,
    }


# ---------- Ejercicio 3: Centralidad de grado ----------

def centralidad_grado(G: nx.DiGraph, top: int = 10) -> pd.DataFrame:
    N = G.number_of_nodes()
    normalizador = (N - 1) if N > 1 else 1
    filas = []
    for n, attrs in G.nodes(data=True):
        kin = G.in_degree(n)
        kout = G.out_degree(n)
        ktot = kin + kout
        filas.append(
            {
                "nodo": n,
                "nombre": attrs.get("nombre", str(n)),
                "tipo": attrs.get("tipo", "?"),
                "grado_in": kin,
                "grado_out": kout,
                "grado_total": ktot,
                "C_grado_norm": ktot / (2 * normalizador),
            }
        )
    df = pd.DataFrame(filas).sort_values("grado_total", ascending=False).reset_index(drop=True)
    return df.head(top)


# ---------- Ejercicio 4: Centralidad por intermediación en el componente gigante ----------

def betweenness_componente_gigante(G: nx.DiGraph, top: int = 10) -> dict:
    H = G.to_undirected()
    if H.number_of_nodes() == 0:
        return {"df": pd.DataFrame(), "nodos_gigante": set(), "tamano": 0}
    componentes = list(nx.connected_components(H))
    componentes.sort(key=len, reverse=True)
    nodos_gigante = componentes[0]
    sub = H.subgraph(nodos_gigante).copy()
    bet = nx.betweenness_centrality(sub, normalized=True)
    filas = []
    for n, b in bet.items():
        attrs = G.nodes[n]
        filas.append(
            {
                "nodo": n,
                "nombre": attrs.get("nombre", str(n)),
                "tipo": attrs.get("tipo", "?"),
                "betweenness": b,
                "grado_total": G.in_degree(n) + G.out_degree(n),
            }
        )
    df = pd.DataFrame(filas).sort_values("betweenness", ascending=False).reset_index(drop=True)
    return {
        "df_top": df.head(top),
        "df_completo": df,
        "nodos_gigante": nodos_gigante,
        "tamano": len(nodos_gigante),
        "betweenness_dict": bet,
    }


# ---------- Ejercicio 5: Conexa o no conexa ----------

def componentes(G: nx.DiGraph) -> dict:
    H = G.to_undirected()
    comp_w = list(nx.weakly_connected_components(G))
    comp_s = list(nx.strongly_connected_components(G))
    tamanos_w = sorted([len(c) for c in comp_w], reverse=True)
    tamanos_s = sorted([len(c) for c in comp_s], reverse=True)
    return {
        "n_weakly": len(comp_w),
        "n_strongly": len(comp_s),
        "tamanos_weakly": tamanos_w,
        "tamanos_strongly": tamanos_s,
        "es_conexa_debil": len(comp_w) == 1,
        "es_conexa_fuerte": len(comp_s) == 1,
        "n_aislados": sum(1 for t in tamanos_w if t == 1),
        "tamano_gigante": tamanos_w[0] if tamanos_w else 0,
    }


# ---------- Ejercicio 6: Coeficiente de clustering local para los 3 más conectados ----------

def clustering_local_top3(G: nx.DiGraph) -> dict:
    H = G.to_undirected()
    grados = sorted(H.degree(), key=lambda x: x[1], reverse=True)
    top3 = [n for n, _ in grados[:3]]
    C_local = nx.clustering(H)
    filas = []
    for n in top3:
        vecinos = set(H.neighbors(n))
        filas.append(
            {
                "nodo": n,
                "nombre": G.nodes[n].get("nombre", str(n)),
                "tipo": G.nodes[n].get("tipo", "?"),
                "grado": H.degree(n),
                "C_local": C_local[n],
                "vecinos": vecinos,
            }
        )
    pares_conectados = []
    for i in range(len(top3)):
        for j in range(i + 1, len(top3)):
            a, b = top3[i], top3[j]
            conectados = H.has_edge(a, b)
            vecinos_comunes = set(H.neighbors(a)) & set(H.neighbors(b))
            pares_conectados.append(
                {
                    "par": (G.nodes[a].get("nombre", str(a)), G.nodes[b].get("nombre", str(b))),
                    "conectados": conectados,
                    "vecinos_comunes": len(vecinos_comunes),
                }
            )
    df_top = pd.DataFrame(
        [{k: v for k, v in f.items() if k != "vecinos"} for f in filas]
    )
    return {
        "df": df_top,
        "filas_top3": filas,
        "pares": pares_conectados,
        "C_local_dict": C_local,
    }


# ---------- Ejercicio 7: Coeficiente de clustering global ----------

def _contar_triangulos_y_triples(H: nx.Graph) -> tuple[int, int]:
    """Cuenta triángulos y triples conectados (caminos de longitud 2)."""
    triangulos = sum(nx.triangles(H).values()) // 3
    triples = 0
    for n in H.nodes:
        k = H.degree(n)
        triples += k * (k - 1) // 2
    return triangulos, triples


def clustering_global(G: nx.DiGraph, n_repeticiones_er: int = 5) -> dict:
    H = G.to_undirected()
    N = H.number_of_nodes()
    L = H.number_of_edges()
    triangulos, triples = _contar_triangulos_y_triples(H)
    C_formula = (3 * triangulos / triples) if triples > 0 else 0.0
    C_nx = nx.transitivity(H)
    C_promedio_local = nx.average_clustering(H)

    Cs_er = []
    for s in range(n_repeticiones_er):
        ER = nx.gnm_random_graph(N, L, seed=1000 + s)
        Cs_er.append(nx.transitivity(ER))
    C_er_promedio = float(np.mean(Cs_er)) if Cs_er else 0.0

    return {
        "triangulos": triangulos,
        "triples_conectados": triples,
        "C_global_formula": C_formula,
        "C_global_nx": C_nx,
        "C_promedio_local": C_promedio_local,
        "C_global_ER_referencia": C_er_promedio,
        "ratio_observado_vs_ER": (C_nx / C_er_promedio) if C_er_promedio > 0 else None,
    }


# ---------- Ejercicio 8: Dirigida/no dirigida, ponderada/no ponderada ----------

def direccion_y_peso(G: nx.DiGraph, top: int = 10) -> dict:
    filas = []
    for u, v, data in G.edges(data=True):
        filas.append(
            {
                "vendedor": G.nodes[u].get("nombre", str(u)),
                "comprador": G.nodes[v].get("nombre", str(v)),
                "peso": data.get("peso", 0.0),
            }
        )
    df_trans = pd.DataFrame(filas).sort_values("peso", ascending=False).reset_index(drop=True)
    asimetria = []
    for n, attrs in G.nodes(data=True):
        kin = G.in_degree(n)
        kout = G.out_degree(n)
        if kin + kout == 0:
            continue
        asimetria.append(
            {
                "nombre": attrs.get("nombre", str(n)),
                "tipo": attrs.get("tipo", "?"),
                "grado_in": kin,
                "grado_out": kout,
                "asimetria": kout - kin,
            }
        )
    df_asim = pd.DataFrame(asimetria).sort_values("asimetria", key=abs, ascending=False).reset_index(drop=True)
    pesos = [d.get("peso", 0.0) for _, _, d in G.edges(data=True)]
    return {
        "df_top_transacciones": df_trans.head(top),
        "df_asimetria_top": df_asim.head(top),
        "total_ponderado": float(sum(pesos)),
        "peso_promedio": float(np.mean(pesos)) if pesos else 0.0,
        "peso_mediano": float(np.median(pesos)) if pesos else 0.0,
        "n_aristas": G.number_of_edges(),
    }


# ---------- Ejercicio 9: Vinculación preferencial ----------

def vinculacion_preferencial(G: nx.DiGraph) -> dict:
    H = G.to_undirected()
    N = H.number_of_nodes()
    L = H.number_of_edges()

    grados_emp = [d for _, d in H.degree()]

    m = max(1, round(L / N)) if N > 0 else 1
    BA = nx.barabasi_albert_graph(N, m, seed=42)
    grados_ba = [d for _, d in BA.degree()]

    ER = nx.gnm_random_graph(N, L, seed=42)
    grados_er = [d for _, d in ER.degree()]

    def _dist(grados):
        c = Counter(grados)
        total = len(grados)
        return pd.DataFrame(
            [(k, n, n / total) for k, n in sorted(c.items())],
            columns=["k", "conteo", "p_k"],
        )

    df_emp = _dist(grados_emp).assign(modelo="Observada")
    df_ba = _dist(grados_ba).assign(modelo="BA (m=%d)" % m)
    df_er = _dist(grados_er).assign(modelo="ER (mismo L)")
    df = pd.concat([df_emp, df_ba, df_er], ignore_index=True)

    def _gamma(grados):
        c = Counter(grados)
        if not c:
            return None
        ks = np.array(sorted(c.keys()))
        ks = ks[ks > 0]
        if len(ks) < 3:
            return None
        ps = np.array([c[k] / len(grados) for k in ks])
        ps = ps[ps > 0]
        ks = ks[: len(ps)]
        return -float(np.polyfit(np.log10(ks), np.log10(ps), 1)[0])

    return {
        "df_comparacion": df,
        "gamma_observado": _gamma(grados_emp),
        "gamma_ba": _gamma(grados_ba),
        "gamma_er": _gamma(grados_er),
        "m_usado_ba": m,
    }
