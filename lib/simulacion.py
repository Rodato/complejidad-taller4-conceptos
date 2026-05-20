"""Simulación de una red de transacciones inmobiliarias calibrada a Notaría 2 (Cali, 1938-1943).

Genera un DiGraph dirigido y ponderado (vendedor → comprador, peso = valor en pesos)
usando un mecanismo de Barabási–Albert modificado con cuatro tipos de actor:
bancos, urbanizadoras, familias notables e individuos comunes.

El resultado tiene:
- Distribución de grado heavy-tailed (apta para mostrar leyes de potencia).
- Varios componentes débilmente conectados (incluye nodos aislados).
- Triángulos suficientes para clustering local no trivial.
- Pesos lognormal en órdenes de magnitud de pesos colombianos de la época.
"""

from __future__ import annotations

import json
from pathlib import Path

import networkx as nx
import numpy as np


_NOMBRES_PATH = Path(__file__).parent.parent / "data" / "nombres.json"


def _cargar_nombres() -> dict:
    with _NOMBRES_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def _muestrear_preferencial(
    rng: np.random.Generator,
    candidatos: list[int],
    pesos: np.ndarray,
    k: int,
) -> list[int]:
    """Muestrea k candidatos sin reemplazo con probabilidad proporcional a pesos."""
    if k >= len(candidatos):
        return list(candidatos)
    pesos = pesos.astype(float)
    if pesos.sum() <= 0:
        pesos = np.ones_like(pesos)
    prob = pesos / pesos.sum()
    elegidos = rng.choice(candidatos, size=k, replace=False, p=prob)
    return list(elegidos)


def generar_red(seed: int = 42, n_total: int = 500) -> nx.DiGraph:
    """Genera una red dirigida y ponderada de transacciones inmobiliarias.

    Parámetros
    ----------
    seed : int
        Semilla para reproducibilidad.
    n_total : int
        Número total de nodos en la red final.

    Devuelve
    --------
    nx.DiGraph
        Red con atributos en nodos (`tipo`, `nombre`) y aristas (`peso`).
    """
    rng = np.random.default_rng(seed)
    nombres = _cargar_nombres()

    G = nx.DiGraph()

    bancos = nombres["bancos"]
    urbanizadoras = nombres["urbanizadoras"]
    hubs_iniciales = bancos + urbanizadoras
    n_hubs = len(hubs_iniciales)

    for i, nombre in enumerate(bancos):
        G.add_node(i, tipo="banco", nombre=nombre)
    for j, nombre in enumerate(urbanizadoras):
        G.add_node(len(bancos) + j, tipo="urbanizadora", nombre=nombre)

    for i in range(n_hubs):
        for j in range(i + 1, n_hubs):
            if rng.random() < 0.25:
                origen, destino = (i, j) if rng.random() < 0.5 else (j, i)
                peso = float(rng.lognormal(mean=9.0, sigma=1.0))
                G.add_edge(origen, destino, peso=peso)

    n_restantes = n_total - n_hubs
    n_familias = max(1, int(0.16 * n_restantes))
    n_individuos = n_restantes - n_familias

    tipos_llegada = ["familia"] * n_familias + ["individuo"] * n_individuos
    rng.shuffle(tipos_llegada)

    apellidos_familias = nombres["familias_notables"]
    apellidos_comunes = nombres["apellidos_comunes"]
    nombres_h = nombres["nombres_hombres"]
    nombres_m = nombres["nombres_mujeres"]

    contador_familia = {a: 0 for a in apellidos_familias}

    p_aislado = 0.06
    p_triangulo = 0.15
    m = 2

    for idx, tipo in enumerate(tipos_llegada):
        nodo_id = n_hubs + idx

        if tipo == "familia":
            apellido = apellidos_familias[rng.integers(0, len(apellidos_familias))]
            contador_familia[apellido] += 1
            nombre_pila = (
                nombres_h[rng.integers(0, len(nombres_h))]
                if rng.random() < 0.6
                else nombres_m[rng.integers(0, len(nombres_m))]
            )
            nombre = f"{nombre_pila} {apellido}"
        else:
            apellido = apellidos_comunes[rng.integers(0, len(apellidos_comunes))]
            nombre_pila = (
                nombres_h[rng.integers(0, len(nombres_h))]
                if rng.random() < 0.5
                else nombres_m[rng.integers(0, len(nombres_m))]
            )
            nombre = f"{nombre_pila} {apellido}"

        G.add_node(nodo_id, tipo=tipo, nombre=nombre)

        if rng.random() < p_aislado:
            continue

        candidatos = [n for n in G.nodes if n != nodo_id]
        if not candidatos:
            continue

        grados = np.array([G.degree(n) + 1 for n in candidatos], dtype=float)
        sesgo_tipo = np.array(
            [
                3.0 if G.nodes[n]["tipo"] in ("banco", "urbanizadora") else 1.0
                for n in candidatos
            ],
            dtype=float,
        )
        pesos_atrac = grados * sesgo_tipo

        m_real = min(m, len(candidatos))
        destinos = _muestrear_preferencial(rng, candidatos, pesos_atrac, m_real)

        for destino in destinos:
            es_vendedor = rng.random() < 0.5
            origen, dest = (nodo_id, destino) if es_vendedor else (destino, nodo_id)
            mu_peso = (
                10.0 if G.nodes[origen]["tipo"] in ("banco", "urbanizadora") else 8.0
            )
            peso = float(rng.lognormal(mean=mu_peso, sigma=1.2))
            G.add_edge(origen, dest, peso=peso)

            if rng.random() < p_triangulo:
                vecinos_destino = list(set(G.predecessors(destino)) | set(G.successors(destino)))
                vecinos_destino = [v for v in vecinos_destino if v != nodo_id and not G.has_edge(nodo_id, v) and not G.has_edge(v, nodo_id)]
                if vecinos_destino:
                    tercero = vecinos_destino[rng.integers(0, len(vecinos_destino))]
                    es_vendedor3 = rng.random() < 0.5
                    o3, d3 = (nodo_id, tercero) if es_vendedor3 else (tercero, nodo_id)
                    peso3 = float(rng.lognormal(mean=8.0, sigma=1.0))
                    G.add_edge(o3, d3, peso=peso3)

    return G


def resumen(G: nx.DiGraph) -> dict:
    """Resumen rápido de la red. Útil para validación visual."""
    no_dirigida = G.to_undirected()
    componentes_w = list(nx.weakly_connected_components(G))
    componentes_w.sort(key=len, reverse=True)
    return {
        "N": G.number_of_nodes(),
        "L": G.number_of_edges(),
        "k_promedio": 2 * G.number_of_edges() / G.number_of_nodes(),
        "densidad": nx.density(G),
        "n_componentes_weakly": len(componentes_w),
        "tamano_gigante": len(componentes_w[0]) if componentes_w else 0,
        "n_aislados": sum(1 for c in componentes_w if len(c) == 1),
        "clustering_global_no_dir": nx.transitivity(no_dirigida),
        "tipos": {
            t: sum(1 for _, d in G.nodes(data=True) if d["tipo"] == t)
            for t in ("banco", "urbanizadora", "familia", "individuo")
        },
    }


if __name__ == "__main__":
    G = generar_red()
    info = resumen(G)
    for k, v in info.items():
        print(f"{k}: {v}")
