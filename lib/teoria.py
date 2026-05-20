"""Textos y fórmulas LaTeX del Taller 4.

Separar contenido de lógica facilita que Daniel edite los enunciados
sin tocar el código. Cada ejercicio tiene:
- ENUNCIADO: la pregunta tal cual del documento original.
- FORMULA: LaTeX para st.latex().
- INTRO: explicación breve antes del cálculo.
- INTERPRETACION: pista o pregunta interpretativa.
"""

INTRO_GENERAL = """
## Taller 4 — Conceptos básicos en la red de transacciones inmobiliarias

Este taller te lleva paso a paso por las **medidas fundamentales** de una red.
Todos los cálculos se hacen sobre una red **simulada** de ~500 actores y ~1000
transacciones inmobiliarias, **calibrada** estructuralmente a la Notaría 2 de
Cali (1938–1943) pero con tamaño suficiente para apreciar leyes de potencia.

> La red es **dirigida** (vendedor → comprador) y **ponderada** (peso = valor
> de la transacción en pesos colombianos). Algunas medidas requieren proyectarla
> a su versión no dirigida — eso lo veremos explícitamente cuando aplique.

**Cómo usar la app:**
1. En la barra lateral, completa tu identificación (nombre, código, grupo).
2. Recorre los **9 ejercicios** en orden (las pestañas en la parte superior).
3. En cada ejercicio, después de mirar los resultados, escribe tu **interpretación**
   y oprime *Guardar*. Tus respuestas se guardan automáticamente.
4. La última pestaña ("Para tu proyecto") conecta lo aprendido con la red que
   tu grupo (A, B o C) está construyendo.
"""

# --- Ejercicio 1 ---
EJ1_ENUNCIADO = "Encuentre el **Grado Promedio** ⟨k⟩ de la red de transacciones inmobiliarias."
EJ1_FORMULA = r"\langle k \rangle = \frac{1}{N}\sum_{i=1}^{N} k_i = \frac{2L}{N}"
EJ1_FORMULA_DIR = r"\langle k^{in} \rangle = \langle k^{out} \rangle = \frac{L}{N}"
EJ1_INTRO = """
El **grado** de un nodo es el número de vínculos que tiene. El **grado promedio**
⟨k⟩ resume con un solo número la conectividad típica de la red.

En una red **no dirigida** de $N$ nodos y $L$ aristas:
"""
EJ1_INTRO_DIR = """
En una red **dirigida**, cada arista contribuye una unidad al grado de entrada
($k^{in}$) y una al de salida ($k^{out}$):
"""
EJ1_INTERPRETACION = """
**Para pensar:** el promedio ⟨k⟩ esconde la heterogeneidad. ¿Crees que la
mayoría de actores en una red de transacciones inmobiliarias tienen un grado
cercano al promedio, o hay unos pocos con muchísimos más vínculos que el resto?
"""

# --- Ejercicio 2 ---
EJ2_ENUNCIADO = "Encuentre la **distribución de grado** $p_k$ de la misma red."
EJ2_FORMULA = r"p_k = \frac{N_k}{N}"
EJ2_INTRO = """
La distribución de grado $p_k$ es la fracción de nodos en la red que tienen
exactamente $k$ vínculos. Mientras ⟨k⟩ da un número, $p_k$ da una **forma**.

Dos formas típicas:
- **Poisson** (en redes aleatorias tipo Erdős–Rényi): pico cerca de ⟨k⟩, cae rápido.
- **Ley de potencia** (en redes libres de escala): $p_k \sim k^{-\gamma}$, con
  cola pesada — unos pocos nodos acumulan muchísimos más vínculos que el resto.

Visualizamos $p_k$ en escala lineal y en **log-log**: una línea recta en log-log
es la firma de una ley de potencia, con pendiente $-\gamma$.
"""
EJ2_INTERPRETACION = """
**Para pensar:** ¿qué dice la **cola** de la distribución sobre la concentración
del poder económico en el mercado inmobiliario? Si $\gamma$ es bajo (cola pesada),
unos pocos actores intermedian la mayoría de las transacciones.
"""

# --- Ejercicio 3 ---
EJ3_ENUNCIADO = "Calcule la **centralidad de grado** de la misma red."
EJ3_FORMULA = r"C_i^{grado} = \frac{k_i}{N-1}"
EJ3_INTRO = """
La centralidad de grado normaliza el grado de cada nodo dividiéndolo por el
máximo posible ($N-1$). Permite comparar redes de tamaños distintos.

En una red dirigida podemos calcularla separadamente para $k^{in}$, $k^{out}$
o el grado total $k^{in}+k^{out}$.
"""
EJ3_INTERPRETACION = """
**Para pensar:** ¿quiénes son los actores más conectados? ¿son individuos,
familias, bancos o urbanizadoras? Eso te dice qué tipo de actor concentra
estructuralmente la actividad inmobiliaria.
"""

# --- Ejercicio 4 ---
EJ4_ENUNCIADO = (
    "Calcule la **centralidad por intermediación** del cluster más grande de la red "
    "(aquel en el que todos los pares de nodos están conectados por una trayectoria de vínculos)."
)
EJ4_FORMULA = r"C_i^{interm} = \sum_{s \neq i \neq t} \frac{\sigma_{st}(i)}{\sigma_{st}}"
EJ4_INTRO = """
La **centralidad por intermediación** (*betweenness*) mide cuántas trayectorias
más cortas entre pares de nodos pasan por un nodo dado.

Aquí $\sigma_{st}$ es el número de trayectorias más cortas entre $s$ y $t$, y
$\sigma_{st}(i)$ es cuántas de ellas pasan por $i$. Es la métrica clásica para
detectar **intermediarios** (*brokers*): nodos que conectan partes de la red
que de otra manera estarían aisladas.

El cálculo se restringe al **componente débilmente conectado más grande** (el
"cluster" del enunciado), porque entre nodos de componentes distintos no hay
trayectoria definida.
"""
EJ4_INTERPRETACION = """
**Para pensar:** los actores con alta intermediación no siempre son los más
conectados. ¿Encuentras algún *broker* — un nodo con menos grado que los hubs
pero alta intermediación? Esa es la figura del "puente" entre comunidades.
"""

# --- Ejercicio 5 ---
EJ5_ENUNCIADO = (
    "Las redes se clasifican en **conexas** y **no conexas**. ¿A cuál pertenece "
    "la red de transacciones inmobiliarias y por qué?"
)
EJ5_INTRO = """
Una red es **conexa** si entre cada par de nodos existe al menos una trayectoria.
Si al menos un par está a distancia infinita (no hay camino entre ellos), la
red es **no conexa**: se descompone en varios *componentes*.

En redes dirigidas distinguimos:
- **Débilmente conectado**: si ignoramos la dirección, hay un camino.
- **Fuertemente conectado**: respetando dirección, hay un camino $u \to v$ y otro $v \to u$.

En un mercado inmobiliario real, esperamos varios componentes: los actores
no necesariamente comercian todos con todos, y hay nichos cerrados.
"""
EJ5_INTERPRETACION = """
**Para pensar:** ¿qué nos dice la fragmentación del mercado sobre la
**informalidad** o el carácter de nicho de ciertas zonas? Los aislados pueden
representar transacciones únicas entre familias sin vínculos a la red más
amplia.
"""

# --- Ejercicio 6 ---
EJ6_ENUNCIADO = (
    "Calcule el **coeficiente local de clustering** para los tres agentes más "
    "conectados. ¿Están conectados entre sí? ¿O pertenecen a clusters distintos?"
)
EJ6_FORMULA = r"C_i = \frac{2 e_i}{k_i (k_i - 1)}"
EJ6_INTRO = """
El **coeficiente local de clustering** $C_i$ mide cuán conectados están los
vecinos de $i$ entre sí. $e_i$ es el número de aristas entre los vecinos de $i$,
y $k_i(k_i-1)/2$ es el número máximo posible.

$C_i = 1$ significa que los vecinos de $i$ forman un **clique** (todos conectados
entre sí). $C_i = 0$ significa que ninguno de sus vecinos se conoce entre sí.

Tomamos los tres nodos de mayor grado y vemos:
- $C_i$ de cada uno.
- Si los tres están conectados directamente entre sí.
- Cuántos vecinos comunes comparten por pares.
"""
EJ6_INTERPRETACION = """
**Para pensar:** los hubs con $C_i$ bajo son **integradores**: conectan partes
de la red que sin ellos estarían separadas. Los hubs con $C_i$ alto son parte
de un **clan** cerrado donde casi todos se conocen.
"""

# --- Ejercicio 7 ---
EJ7_ENUNCIADO = (
    "El coeficiente de clustering global mide el número de **triples completos** "
    "sobre el número total de **triples potenciales** de la red. Calculen el "
    "coeficiente de clustering global de la red total."
)
EJ7_FORMULA = r"C_{global} = \frac{3 \times \text{(número de triángulos)}}{\text{(número de triples conectados)}}"
EJ7_INTRO = """
El **coeficiente de clustering global** (también llamado *transitividad*) mide
qué tan cerrada en triángulos está la red en su conjunto.

Un **triple conectado** es un camino de dos aristas: tres nodos $a-b-c$ donde
$b$ está conectado tanto a $a$ como a $c$. Si además existe la arista $a-c$,
el triple se cierra en un **triángulo**.

Como cada triángulo contiene 3 triples conectados (uno por cada vértice
"central"), el factor 3 en el numerador asegura que $C_{global}$ esté entre 0 y 1.
"""

EJ7_NOTA_BARABASI = """
> **Nota de Daniel (Boris):** la **ecuación 21, página 45, del libro de Barabási**
> presenta numerador y denominador *invertidos*. La fórmula correcta de
> $C_{global}$ tiene los **triángulos en el numerador** (lo "cerrado") y los
> **triples conectados en el denominador** (lo "posible"). Lo que Barabási
> escribe equivaldría a un $1/C_{global}$ — un número $\geq 1$, lo cual no tiene
> sentido para un coeficiente que debe estar en $[0, 1]$.
>
> En esta app calculamos $C_{global}$ con la fórmula correcta y la
> comparamos con la implementación de NetworkX (`nx.transitivity`), que
> debería dar idéntico resultado.
"""

EJ7_INTERPRETACION = """
**Para pensar:** comparamos $C_{global}$ de la red observada con el de una red
Erdős–Rényi del mismo tamaño. Si nuestra red tiene mucho más clustering que el
ER, hay **fuerzas sociales** que cierran triángulos (intermediarios que
presentan compradores entre sí, familias que negocian en bloque, etc.).
"""

# --- Ejercicio 8 ---
EJ8_ENUNCIADO = (
    "¿Es la red de transacciones inmobiliarias dirigida o no dirigida? "
    "¿Es ponderada o no ponderada? Justifiquen sus respuestas."
)
EJ8_INTRO = """
- **Dirigida vs no dirigida:** un vínculo dirigido tiene origen y destino
  distinguibles ($A \to B \neq B \to A$). Una transacción inmobiliaria es
  inherentemente dirigida: hay un *vendedor* y un *comprador*.
- **Ponderada vs no ponderada:** una arista ponderada lleva un valor numérico
  (peso). En transacciones inmobiliarias el peso natural es el **valor en pesos**
  de la operación.

La asimetría entre $k^{in}$ y $k^{out}$ revela el rol estructural de cada actor:
- $k^{out} \gg k^{in}$: vendedores netos (urbanizadoras que liquidan lotes).
- $k^{in} \gg k^{out}$: compradores netos (familias que acumulan propiedad).
- Equilibrado: intermediarios.
"""
EJ8_INTERPRETACION = """
**Para pensar:** ¿qué se **pierde** si analizamos esta red como si fuera no
dirigida y no ponderada? Pista: pierdes la distinción entre vendedores y
compradores, y pierdes el tamaño económico de la operación.
"""

# --- Ejercicio 9 ---
EJ9_ENUNCIADO = (
    "Contrasten la **hipótesis de vinculación preferencial** de Barabási y "
    "Albert (1999) para explicar cómo evolucionó la red. Den la intuición "
    "para el comportamiento de compradores y vendedores en una red de "
    "transacciones inmobiliarias especulativas."
)
EJ9_FORMULA = r"\Pi(k_i) = \frac{k_i}{\sum_j k_j}"
EJ9_INTRO = """
La hipótesis de **vinculación preferencial** dice que un nodo nuevo se conecta
con probabilidad proporcional al grado del nodo existente: los ricos se hacen
más ricos. El resultado son redes **libres de escala** con $p_k \sim k^{-\gamma}$
y $\gamma \approx 3$ en el modelo BA puro.

Comparamos la distribución de grado observada con:
- **BA puro**: vinculación preferencial sin mecanismos adicionales.
- **Erdős–Rényi (ER)**: aleatorio puro, sin preferencia.

Si la distribución observada está más cerca de BA que de ER, la hipótesis
de Barabási tiene sustento.
"""
EJ9_INTERPRETACION = """
**Para pensar:** en un mercado inmobiliario especulativo, ¿qué mecanismos
producen vinculación preferencial?
- Los **bancos** atraen muchos compradores porque son la fuente del crédito.
- Las **urbanizadoras** atraen muchos vendedores porque tienen el lote.
- Las **familias notables** intermedian (capital social heredado).
- Los **especuladores** compran a unos pocos y venden a muchos.

Cada uno de estos genera atracción asimétrica del grado.
"""

# --- Sección final ---
PROYECTO_INTRO = """
## Síntesis: para tu proyecto

Las nueve medidas que acabas de calcular son tu **kit de inicio** para
analizar cualquier red — sea de familias, transacciones, infraestructura
o flujos de capital.

**Antes de cerrar, piensa:**

1. **¿Cuál de las 9 medidas resultará más informativa** para la red que tu
   equipo está construyendo? ¿Por qué?

2. **¿Qué medida esperas que se vea radicalmente distinta** en tu red
   respecto a la del taller (más o menos clustering, distribución más o
   menos heavy-tailed, más o menos componentes)? Atrévete a hacer una
   predicción.

3. **¿Hay alguna medida que NO aplique** a tu red — por ejemplo, porque tu
   red no es ponderada, o no es dirigida? Justifícalo.

Escribe abajo **un párrafo** que responda a las tres preguntas conectando
explícitamente una o más medidas con una pregunta concreta de tu proyecto.
"""
