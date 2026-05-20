# Taller 4 — Conceptos básicos en la red de transacciones inmobiliarias

App Streamlit para el curso *Introducción a la Complejidad 2026-I* (Universidad del Valle).

Cubre los 9 ejercicios técnico-conceptuales sobre redes (grado promedio, distribución de grado, centralidades de grado e intermediación, conexa/no conexa, clustering local y global, dirigida/ponderada, vinculación preferencial) sobre una **red simulada** de ~500 actores y ~1000 transacciones, calibrada estructuralmente a la Notaría 2 de Cali (1938–1943).

Pensada como complemento del Taller 4 cuando los datos ampliados del Grupo B (red inmobiliaria) aún no están listos.

## Correr localmente

```bash
# Crear venv con Python 3.11+ (no usar el 3.9 del sistema)
/opt/homebrew/bin/python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Ejecutar
streamlit run streamlit_app.py
```

La app abre en http://localhost:8501.

## Estructura

```
app/
├── streamlit_app.py         # Entry point
├── lib/
│   ├── simulacion.py        # Genera la red sintética (BA modificado con tipos)
│   ├── metricas.py          # 9 funciones de cálculo
│   ├── teoria.py            # Textos y fórmulas LaTeX
│   ├── viz.py               # Plotly + pyvis
│   └── storage.py           # Persistencia a Google Sheets / CSV local
├── data/nombres.json        # Pool de apellidos caleños, bancos, urbanizadoras
└── .streamlit/
    ├── config.toml          # Tema
    └── secrets.toml         # (no checked in) credenciales Google
```

## Persistencia

Por defecto las respuestas se guardan en `respuestas_local.csv`.

**Recomendación: reutilizar el mismo sheet del Grupo B, pero en una pestaña distinta.**
El service account ya tiene permisos sobre ese documento; basta con apuntar a una
pestaña nueva (`taller4`) y la app la crea automáticamente la primera vez que
un estudiante envíe una respuesta.

Para configurar:
1. Tomar la URL del sheet que ya usa la app del Grupo B (`3. Inmobilliario/`).
2. Crear `.streamlit/secrets.toml`:

```toml
[gcp_service_account]
# ... contenido del JSON del service account (mismo que Grupo B) ...

[sheets]
url = "https://docs.google.com/spreadsheets/d/<MISMO_ID_QUE_GRUPO_B>/edit"
worksheet = "taller4"   # ⚠️ DEBE ser distinto a "respuestas" (que usa Grupo B)
```

> ⚠️ **No** pongas `worksheet = "respuestas"`: el esquema de columnas de este taller (17 columnas) es distinto al del Grupo B (18 columnas) y se sobrescribirían mutuamente.

La primera vez que la app escriba, `gspread` detecta que la pestaña `taller4`
no existe y la crea con el encabezado correcto (ver `lib/storage.py:_abrir_hoja`).

## Deploy en Streamlit Cloud

1. Subir a un repo `Rodato/complejidad-taller4-conceptos`.
2. En https://share.streamlit.io crear nueva app apuntando al repo.
3. En "Secrets" pegar el contenido de `secrets.toml`.

## Calibración de la red simulada

La red se genera con un mecanismo BA modificado:

- **13 hubs iniciales** (bancos + urbanizadoras) con conexiones débiles entre sí.
- **487 nodos restantes** (familias notables + individuos) llegan secuencialmente.
- Cada nuevo nodo emite **m=2** aristas con vinculación preferencial sesgada (bancos/urbanizadoras atraen 3× más).
- **6%** de los nodos llegan aislados (genera componentes desconectados).
- **15%** de probabilidad de cerrar triángulo después de cada arista (genera clustering local).
- Pesos lognormal: media e⁸ ≈ 3000 pesos (transacciones entre individuos), e¹⁰ ≈ 22000 pesos (bancos/urbanizadoras).

Semilla por defecto: 42. El botón "Regenerar" produce variaciones manteniendo la estructura.
