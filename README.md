#   momoscrape
Momoscrape es un conjunto de varios scripts escritos en python con una serie de funciones implementadas con el fin de formar una base de datos de
agrupaciones, autores y componentes del Carnaval de Cádiz. Para ello, se emplean técnicas de web scraping, accediendo al sitio 
[El Buscador del Falla](https://www.elbuscadordelfalla.com/Home/Index), posiblemente el sitio web más completo sobre el Carnaval de 
Cádiz y que ofrece una base de datos de acceso libre y gratuito, así como una serie de artículos, tanto históricos como de actualidad.

Existen tres ficheros. En el primero de ellos, se definen las funciones para obtener la información relativa a las agrupaciones.
El formato de los documentos de agrupación es similar al que se encuentra en [El Buscador del Falla](https://www.elbuscadordelfalla.com/Home/Index):
    -   id_: identificador numérico de la agrupación
    -   nombre: nombre oficial de la agrupación 
    -   modalidad: modalidad del concurso a la que se presentó la agrupación (existen cuatro opciones: coro, cuarteto, comparsa
        y chirigota).
    -   calificación: calificación final de la agrupación en el concurso.
    -   origen: localidad de origen de la agrupación. 
    -   tipo: se refiere al disfraz o personaje interpretado.
    -   agrupación anterior: referencia a la agrupación del año anterior.
    -   imagen: url de la imagen de la agrupación.
    -   componentes: una lista de referencias a cada uno de los integrantes de la agrupación, así como su autor o autores.

El segundo de los ficheros es similar, pero en este caso se ocupa de la información de autores y componentes. El formato de los
documentos de autor/componente es el siguiente:
    -   id_: identificador numérico del autor/componente.
    -   apodo: apodo carnavalesco del autor/componente en caso de que exista.
    -   origen: localidad de origen del autor/componente.
    -   antifaz: si el autor/componente es poseedor del Antifaz de Oro, almacena el año en que le fue conseguido. En caso contrario,
        almacena un valor nulo.
    -   imagen: url de la imagen del autor/componente
    -   agrupaciones: una lista de referencias de las agrupaciones en que ha participado el autor/componente, así como el rol 
        desempeñado en dicha agrupación.

Por último, en database.py, se implementa un script para formar una base de datos mongo en el servidor local con toda la información, 
tanto de agrupaciones como de autores/componentes.

Hasta el momento, sólo se forma un base de datos mongo, aunque en el futuro se añadirá la funcionalidad para formar una base de datos sql.

La posible utilidad de esta herramienta radica en la posibiilidad de utilizar esta base de datos para ser consumida por alguna API o
cualquier otra aplicación de cualquier tipo.

Cualquier sugerencia de mejora es más que bienvenida.