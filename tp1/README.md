

**<h3>Trabajo Práctico</h3>**

**<h1>Tratamiento y Análisis de Textos</h1>**



Juan Cardona (122124)

juan\_cardona@outlook.com


**<h3>PUNTO 1</h3>**

La información extraída mediante el programa realizado en este
ejercicio provee una representación del campus dado de manera tal que se
puedan implementar mecanismos de recuperación sobre los archivos de
dicho campus.

Dicha representación, la cual se describe como “indexación de la
colección” tiene por función la identificación de los conceptos que
describen el contenido del documento y la traducción de los mismos a una
forma computacionalmente manejable.

En este ejercicio dichos conceptos son los términos normalizados y
poseen información adicional asociada como puede ser su frecuencia en el
texto o la cantidad de documentos en donde aparece.

Para llevar a cabo esta tarea se realizó un análisis lexicográfico de
los documentos el cual consiste en convertir un flujo de caracteres en
palabras o tokens normalizados.

La etapa de normalización incluye las siguientes fases:

- Eliminar saltos de lineas.

- Remover acentos.

- Convertir caracteres a minúsculas.

- Quitar signos de puntuación

- Remover símbolos no alfa-numéricos

Posteriormente se seleccionó de los tokens obtenidos aquellos que no
representan palabras vacías ya que suponen una frecuencia demasiado alta
y por tanto no son buenos discriminantes. Otro beneficio adicional es
que dicho filtro reduce el tamaño del índice considerablemente.

Asimismo se selecciona del conjunto de tokens solo aquellos que cumplen
con un rango de tamaño especificado. Así es que los términos elegidos no
pueden tener una longitud inferior a 3 caracteres ni superar los 23
caracteres de longitud. De esta manera se filtra tokens que son costosos
de mantener y que no proveen una buena representación del campus.

De esta manera se obtienen un conjunto de términos normalizados que
representan al campus dado y a partir de los cuales se pueden realizar
búsquedas.

**<h3>PUNTO 2</h3>**

Para este ejercicio se extrajeron una serie de tokens en base a
expresiones regulares definidas. Para esto se creo un nuevo nuevo modulo
'regex\_tokenizer.py' el cual define una clase RegexTokenizer que es
instanciada por el 'lex\_analyser.py'.

De esta manera se extraen:

- <h4>Abreviaturas</h4>

Se trabajo en base al paper “What is a word. What is a sentence?
Problems of tokenization ” de Grefenstette y Tapanainen, a partir del
cual se extrajeron las siguientes expresiones regulares:

`([A-Za-z]\\.(?:[A-Za-z0-9]\\.)+)`

`[A-Z][bcdfghj-np-tvxz]+\\.`

Las siguientes regex se decidió` descartar debido a no ser lo suficientemente
efectivas para el corpus dado:

`([A-Za-z][A-Za-z]\*\\.)([,?]| [a-z0-9])`

`([A-Za-z][\^ ]\*\\.)([,?]| [a-z0-9])`

`([A-Za-z]\\.)`

- <h4>E-Mails</h4>

Se confeccionó la siguiente expresión regular:

``[a-zA-Z0-9!\#\\\$%&'\\\*\\+\\-\\/=\\?\\\^\_\`{\\|}\~\\.]+@[a-z0-9\\-]+\\.[a-z]+(?:\\.[a-z]+)+``

- <h4>URLs</h4>

Se confeccionó la siguiente expresión regular:

`(https?:\\/\\/(?:www\\.|(?!www))[a-z0-9\\.]+\\.[a-z0-9\\/\\?=]{2,}|www\\.[a-z0-9]+\\.[a-z0-9\\/\\?=]{2,})`

- <h4>Números</h4>

Basado nuevamente en el paper de Grefenstette y Tapanainen, del mismo se
seleccionaron las siguientes expresiones:

Fechas: `[0-9]{1,2}[\\/|\\-][0-9]{1,2}[\\/|\\-](?:[0-9]{2,4})`

Porcentajes: `(\\+\\-)?[0-9]+()?[0-9]\*%`

Moneda: `\\\$\\d+(?:,\\d{1,2})?`

Teléfonos: `(?:\\(\\d{2,}\\))\\s?\\d{2,}(?:\\-\\d+)?\\s`

- <h4>Nombres Propios</h4>:

Mediante la siguiente expresion regular:

`[A-Z][a-z]+(?:[\\s][A-Z][a-z]+)+`

Asimismo se decidió extraer las siguientes expresiones y descartarlas
del vocabulario del corpus:

- <h4>Caracteres especiales de HTML</h4>

Para lo cual se hizo uso de la siguiente expresión:

`\\s(&[\\S\^;]+;) | &(?:[a-z]+|\#x?\\d+);`

De esta manera se eliminaron del índice 6544 tokens y la palabra “raquo”
dejó de pertenecer al ranking de palabras de mayor frecuencia.



**<h3>PUNTO 3</h3>**

Al realizar el analisis léxico sobre la colección T12012-qm se ha
podido visualizar lo siguiente:

- Existe un alto número de fórmulas químicas que se pierden al tokenizar
como en el ejercicio 1) y las cuales juegan un papel central para los
documentos del corpus. Ejemplo:

'Na2O + SiO2 =\> Na2SiO3'


- Las fórmulas químicas tienen una composición en donde el mismo
caracter en mayúsculas tiene un valor semántico diferente que su
equivalente en minúsculas y el cual se pierde con la normalización de
mayúsculas a minúsculas. Tal es el caso para fórmulas como 'MnO2' o
'PbO2'.

- Se pierden valores referidos a temperaturas, los cuales también cargan
con un alto valor representativo para el corpus. Ejemplos pueden ser:
'150.2°', '-0.43°'.


- Se pierde el símbolo 'μ' utilizado en varias fórmulas. Ejemplo: '2 px
μ 2 py μ 2 pz μ'.


- El simbolo '-' es eliminado. Para este corpus es necesario que dicho
carácter se mantenga al menos cuando se trate de fórmulas químicas o
enlaces. Ejemplos: 'Si-Si', 'Si-H'.


- Existen en algunos documentos estructuras de tablas que son
irreproducibles para el analizador léxico. De esta manera se pierde el
valor dado a una fila para una columna en particular.


- Otros símbolos importantes que se pierden son: 'Å' (Longitud de
enlace), '·' (utilizado en formulas de densidad como '8.99·10-5
g·cm-3'), 'β', '\>'(ejemplo: 'H2O \> D2O'), '+'.



**<h3>PUNTO 4</h3>** 

Para el stemmer se seleccionó el algoritmo de Snowball en su
versión en castellano y se aplicó con el mismo analizador léxico y
corpus del ejercicio 1.

Como resultado se puede observar que el ranking de terminos más
frecuentes varió con la aparición de nuevos términos como el de la
familia de raíz 'estudi' o 'academ' que son altamente representativos.
Además se logra reducir la longitud del índice y dar una mayor cantidad
de respuestas a una consulta dada.

Sin embargo, también se aprecian anomalías que pueden jugar en contra a
la recuperación eficiente de información. Por ejemplo, existen términos
que tienen la misma raíz pero que el stemmer los trató diferente como el
par 'reducian' y 'reducción' que fueron traducidos como 'reducir' en el
primer caso y 'reduccion' en el segundo; mismo caso para la raíz
'estudi' que incluye términos como 'estudiante' pero no 'estudiantil'.
Asimismo, existen términos de distinta raíz que fueron tratados de la
misma manera, tal ocurre para 'casos' y 'casa' (ambos traducidos a
'cas') y 'universo' y 'universidad' (a 'univers'), entre otros.



**<h3>PUNTO 5</h3>** 

En este ejercicio se propone verificar la ley de Zipf mediante el
análisis de la novela 'El ingenioso hidalgo don Quijote de la Mancha' de
Cervantes. Como resultado se obtuvieron los siguientes gráficos:

![Zipf Lineal](https://github.com/Juancard/recuperacion-informacion-works/blob/master/tp1/punto5/zipf_lineal.png)

![Zipf log-log](https://github.com/Juancard/recuperacion-informacion-works/blob/master/tp1/punto5/zipf_loglog.png)


En el primero de los gráficos se puede observar que, tal como lo enuncia
Zipf, existen unos pocos términos que se repiten muchas veces en el
vocabulario así como muchos términos que se repitan pocas veces.

Al aplicar la escala logarítmica a ambos ejes se obtiene la segunda
gráfica en la cual vemos que la curva resultante (color azul) sigue una
distribución muy similar a una recta de pendiente negativa (color rojo).

Se puede concluir entonces que se cumple la ley de Zipf para el texto
analizado. Esto significa que se podrá realizar predicciones sobre
nuevos términos, por ejemplo, podemos conocer el orden de una palabra si
se dispone de su frecuencia en el campus.

Por otro lado, realizando podas sobre los términos más y menos
frecuentes se obtuvieron los siguientes resultados:

![Zipf Lineal - poda 5%](https://github.com/Juancard/recuperacion-informacion-works/blob/master/tp1/punto5/zipf_lineal_poda_05.png)

![Zipf log-log - poda 5%](https://github.com/Juancard/recuperacion-informacion-works/blob/master/tp1/punto5/zipf_loglog_poda_05.png)

![Zipf Lineal - poda 10%](https://github.com/Juancard/recuperacion-informacion-works/blob/master/tp1/punto5/zipf_lineal_poda_10.png)

![Zipf log-log - poda 10%](https://github.com/Juancard/recuperacion-informacion-works/blob/master/tp1/punto5/zipf_loglog_poda_10.png)

![Zipf Lineal - poda 15%](https://github.com/Juancard/recuperacion-informacion-works/blob/master/tp1/punto5/zipf_lineal_poda_15.png)

![Zipf log-log - poda 15%](https://github.com/Juancard/recuperacion-informacion-works/blob/master/tp1/punto5/zipf_loglog_poda_15.png)


Se podría concluir entonces que con una poda del 15% se obtiene una
mejor predicción sobre el texto ya que su curva se aproxima más a una
curva recta de pendiente negativa.



**<h3>PUNTO 6</h3>** 

A partir de los calculos realizados en la notebook 'punto6.ipynb'
se obtiene lo siguiente:

- Según estimación de Zipf: Se omite el **11.12%** de los términos.

- Segun datos reales: Se omite el **7.2%** de los términos.


**<h3>PUNTO 7</h3>** 

Para verificar si se cumple la ley de Heaps se ha trazado el
siguiente gráfico:

![Estimación de ley de Heaps](https://github.com/Juancard/recuperacion-informacion-works/blob/master/tp1/punto7/heaps_quijote.png)

Para llevar a cabo la estimación se utilizaron los siguientes
parámetros:

K = 10

β = 0.6

Los resultados de la ley de Heaps plantean que a medida que se
incorporan documentos a una colección, cada vez se descubrirán nuevos términos para el vocabulario.

Su aplicación es directa ya que permite estimar el tamaño del
vocabulario con lo cual se puede determinar – por ejemplo – la escalabilidad de las
estructuras de datosnecesarias para almacenar los índices que soportan el SRI. Esto es
altamente útil si se utilizará una tabla de hash en memoria para el índice.
