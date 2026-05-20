# CLAUDE.md — App Taller 4 (Conceptos básicos de redes)

## Qué es esto

App Streamlit pedagógica para el **Taller 4** del curso *Introducción a la Complejidad 2026-I* (Universidad del Valle). Cubre los 9 ejercicios técnico-conceptuales sobre medidas básicas de redes (⟨k⟩, p_k, centralidad de grado, betweenness, conexa/no conexa, clustering local y global, dirigida/ponderada, vinculación preferencial) **sobre una red simulada** de ~500 actores calibrada estructuralmente a la Notaría 2 de Cali (1938–1943).

- **Por qué simulada:** el dataset ampliado del Grupo B (inmobiliario) no estaba listo cuando se diseñó el taller. La simulación reproduce la estructura del Notaría 2 pero a mayor escala para que la cola de la distribución de grado sea visible.
- **Audiencia:** transversal a los grupos A/B/C — no se diferencia por grupo en la app (decisión deliberada; ver decisiones más abajo).

## Quick start (local)

```bash
# Python 3.11+ (NO usar /usr/bin/python3 de macOS)
/opt/homebrew/bin/python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

streamlit run streamlit_app.py
```

Sin `secrets.toml`, las respuestas se guardan en `respuestas_local.csv` (gitignoreado).

## Arquitectura

```
streamlit_app.py            # Entry point: sidebar + 10 tabs (1 explora red + 9 ej + cierre)
lib/
  simulacion.py             # generar_red(seed, n_total) → nx.DiGraph
  metricas.py               # 9 funciones, una por ejercicio
  teoria.py                 # Textos LaTeX (USAR raw strings r"""...""")
  viz.py                    # Plotly + pyvis
  storage.py                # Google Sheets / CSV local
data/nombres.json           # Apellidos caleños, bancos, urbanizadoras
.streamlit/
  config.toml               # Tema
  secrets.toml              # gitignoreado — usar secrets.example.toml como plantilla
```

## Decisiones clave (no revertir sin avisar)

- **No hay selector de grupo A/B/C.** El taller es transversal; la pestaña final "Para tu proyecto" muestra un único set de preguntas genéricas que funciona para cualquier red del proyecto del estudiante.
- **No hay control de semilla en la UI.** La red usa `SEMILLA_FIJA = 42` siempre. Quitarlo del sidebar fue intencional — exponerlo confundía más de lo que aportaba; el valor pedagógico de cambiar la semilla lo demuestra el docente en clase modificando el código directamente si quiere.
- **Red dirigida y ponderada desde el inicio** (vendedor → comprador, peso = valor en pesos). Las medidas que requieren no-dirigida convierten explícitamente en cada función (`H = G.to_undirected()`).
- **`tab_red` (pestaña 0) usa Plotly, NO pyvis.** Pyvis con N=500 sigue mostrando movimiento residual aunque se deshabilite `physics`, `stabilization` e `improvedLayout`. Plotly es 100% estático. El subgrafo del Ejercicio 6 (N pequeño) sigue usando pyvis porque ahí no hay problema.

## Pitfalls aprendidos

- **scipy es obligatorio en `requirements.txt`.** `nx.spring_layout` cambia internamente a matriz sparse cuando N ≥ 500 y requiere scipy. Localmente puede que ya esté por transitividad (pandas/streamlit); en Streamlit Cloud (Python 3.14 minimal) no está.
- **Strings con LaTeX → `r"""..."""`.** Python 3.14 emite `SyntaxWarning` (y eventualmente `SyntaxError`) por secuencias `\s`, `\g`, `\gamma`, `\sim`, `\geq`, `\gg` en strings normales. Todos los `EJn_INTRO`, `EJn_INTERPRETACION`, `EJn_NOTA_BARABASI` que contienen LaTeX están marcados como raw.
- **`st.html` ≠ `components.html`.** `st.html` no ejecuta JavaScript embebido. Para HTML con scripts (pyvis, vis.js), usar `streamlit.components.v1.html(html, height=H)`. El deprecation warning (`components.v1.html` se removerá 2026-06-01) es prematuro; el reemplazo recomendado `st.iframe` requiere URL, no acepta HTML inline con scripts.
- **IDs de nodos a pyvis deben ser Python `int`, no `numpy.int64`.** JSON encoder de Jinja falla. Forzar `int(n)` y `float(...)` en `red_pyvis`.
- **Streamlit Cloud auto-deploya en cada push a `main`.** Push → ~1–2 min → app actualizada. Si las dependencias cambian, agrega ~30 s más (scipy es el más grande).

## Persistencia (Google Sheets)

- Misma sheet que el Grupo B (la del Notaría 2 detective), **pestaña distinta**: `taller4`.
- Service account: `detective-redes@complejidad-496215.iam.gserviceaccount.com` (ya tiene permisos sobre esa sheet).
- La pestaña `taller4` se crea **automáticamente** la primera vez que un estudiante envía una respuesta (`lib/storage.py:_abrir_hoja`). Header con 16 columnas (`timestamp, nombre, codigo, companeros, resp_red, resp_ej1..ej9, resp_proyecto, timestamp_final`).
- Default del worksheet en `storage.py` es `"taller4"` — si alguien omite ese campo en `secrets.toml`, no rompe el sheet del Grupo B.

## Deploy

- **Repo:** `Rodato/complejidad-taller4-conceptos` (público).
- **URL:** https://complejidad-taller4-conceptos.streamlit.app
- **Secrets:** mismas keys que Grupo B (`[gcp_service_account]` y `[sheets]`). Cambiar solo `worksheet = "taller4"`.

## Convenciones de estilo

- Todo el contenido en español (texto, comments, log messages).
- Identificadores de función en inglés (`generar_red` está OK, `m.grado_promedio` también) o español; mantener consistencia dentro de cada módulo.
- Strings de Sheets/storage: NO incluir `grupo` ni `semilla` en el esquema (intencionalmente removidos).
- Paleta de colores por tipo de actor en `viz.py:COLOR_POR_TIPO`. No cambiar sin actualizar la leyenda en `tab_red`.

## Calibración de la red simulada

`lib/simulacion.py:generar_red(seed=42, n_total=500)`:
- 13 hubs iniciales: 8 bancos + 5 urbanizadoras, conectados entre sí con probabilidad 0.25.
- 487 nodos restantes (≈80 familias notables, ≈407 individuos) llegan secuencialmente.
- Cada nuevo nodo emite `m=2` aristas con vinculación preferencial sesgada (bancos/urbanizadoras atraen 3× más).
- 6% probabilidad de llegar aislado → componentes desconectados (~22 isolates).
- 15% probabilidad de cerrar triángulo → clustering local realista (~0.04 global, 4× sobre ER).
- Pesos lognormal: μ=8 (transacciones entre individuos, ~$3k) o μ=10 (involucran bancos/urbanizadoras, ~$22k), σ=1.2.

Salida esperada con seed=42:
- N=500, L≈1062
- ⟨k⟩ ≈ 4.24 (no dirigida)
- 23 componentes débilmente conectados (1 gigante de 478 + 22 isolates)
- γ_observado ≈ 1.11, clustering global ≈ 0.037 (vs ER ≈ 0.009)

## Para hacer commits/push

```bash
git add -A
git commit -m "..."
git push origin main
```

Streamlit Cloud detecta el push y rebuilea solo. **No** crear branches secundarios sin avisar — el deploy apunta a `main`.

## Autoría

App escrita por **Daniel Otero** sobre el diseño del Taller 4 hecho por **Boris Salazar**. El crédito en la app es simplemente "Boris Salazar y Daniel Otero" (sin etiquetas de docente/autor).
