# Interfaz gráfica
La interfaz permite hacer simulaciones con MCDS de forma sencilla, además contiene una sección para añadir archivos de FLUKA, se pueden generar bases de datos y contiene una interfaz de ploteo incorporada.

## Ejecución
Antes de ejecutar el código, se deben tener instaladas las librerías de python: PyQt5, matplotlib, numpy, scipy, uncertainties y natsort.
Para utilizar la interfaz basta con ejecutar `main.py`

# Uso
Se debe especificar el nombre de la carpeta donde se guardarán los archivos en caso de hacer simulaciones con MCDS o crear una base de datos. Esto se puede ignorar, en cuyo caso la carpeta tendrá un nombre predeterminado.
En el menú superior se encuentran las distintas opciones: MCDS, Fluka, Graficar, Base de datos y Modelo.

## MCDS
Contiene los parámetros necesarios para crear un archivo input, cada set de parámetros puede añadirse a la interfaz según se requiera. Luego de definir los valores, se debe seleccionar `Generar input` para crear un archivo `.inp` en la carpeta escogida al inicio. Se puede seleccionar una carpeta distinta en `Nueva carpeta`.
Una vez terminada la generación de inputs, se puede ejecutar la simulación seleccionando `Lanzar simulaciones`. Esto último abre una selección de carpeta y luego ejecuta las simulaciones para todos los archivos dentro de esta.
Finalmente se incorpora una opción para calcular supervivencia celular usando el modelo seleccionado (ver **Modelo**) y escogiendo el tipo de célula a usar (HSG y V79 actualmente).

## Fluka
Se puede añadir esta opción seleccionando `Añadir parámetros fluka`. En esta ventana se deben escoger 2 carpetas con archivos obtenidos desde Fluka: `dose data`, `spectrum data`. Además se debe añadir una carpeta con al menos una base de datos (ver **Base de datos**).

Se deben añadir valores para la profundidad mínima y máxima del haz junto a la separación de puntos (bins) coincidiendo con los archivos de Fluka. Además se debe especificar el tipo de célula (V79 o HSG), la cantidad de ADN, el diámetro del núcleo celular y el máximo de dosis. Una vez añadidos todos los parámetros, se puede seleccionar `Fluka -> survival` en el menú superior para obtener un archivo output con supervivencia a distinta profundidad. Los parámetros del archivo output son:
- Profundidad
- Dosis + error
- Yield de DSB's + error
- Lambda + error
- Supervivencia + error.

## Graficar
Se muestra la interfaz de ploteo. Se debe especificar el tipo de gráfico y la carpeta que contenga los archivos con información por graficar. Se puede especificar el label del gráfico y un set de datos experimentales, pero es opcional.
Una vez añadidos los parámetros necesarios, se selecciona `Generar plots`y el programa grafica lo que se encuentra en la carpeta entregada, mostrando un gráfico a la vez. Se puede seleccionar `Siguiente plot` o `Plot anterior` para navegar por los archivos de la carpeta en orden. Se puede cambiar el tipo de gráfico cambiando la selección en `Tipo de plot`y volviendo a generar los plots.

Para añadir más de una curva o puntos a la vez, se debe seleccionar `Añadir otro plot`. Al lado se despliegan los distintos plots enumerados, al seleccionar uno de estos se puede especificar la carpeta, set de datos experimentales, label y separación de puntos para esa curva. Finalmente al hacer click en `Generar plots` se grafican todas las curvas juntas con sus respectivos labels. Si no se especificó un label, se usa uno predeterminado

## Base de datos

Se puede generar una base de datos que puede usarse luego en la sección de **Fluka**. Se debe escoger el tipo de partícula, el número de puntos de energía o de dosis y se pueden especificar rangos de energía/dosis distintos a los predeterminados. Además se pueden especificar valores para la seed, número de simulaciones (nocs), diámetro nuclear y cantidad de adn distintos a los valores predeterminados.
Finalmente al seleccionar `Generar base de datos` se generan los inputs y outputs dentro de una carpeta con el nombre entregado en la ventana inicial y finalmente se crea un archivo `.database` que contiene:
- Energía
- LET de entrada a la célula
- LET de entrada al núcleo
- LET de salida del núcleo
- Yield de DSB's + error
- Lambda + error
Se puede escoger una carpeta distinta seleccionando `Nueva carpeta` dentro del menú superior `MCDS`

## Modelo
Se puede seleccionar el tipo de modelo para calcular la supervivencia. Actualmente solo se utiliza el de Wang (2018)

## Shortcuts
-  `Ctrl+Q` para generar un input de MCDS
-  `Ctrl+W` para lanzar las simulaciones de la carpeta seleccionada