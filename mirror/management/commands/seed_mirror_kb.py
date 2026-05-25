"""
Seed de la Base de Conocimiento del Mirror Endonauta.
Crea MirrorDocumento + MirrorChunk para los 43 marcos teóricos
referenciados en Endonautica. Sin embeddings (usar index_mirror_docs
para agregar embeddings vía OpenAI).

Idempotente: usa get_or_create por nombre de documento.
"""

from django.core.management.base import BaseCommand
from mirror.models import MirrorDocumento, MirrorChunk


KB = [

    # ──────────────────────────────────────────────────────────────────
    # EBOOK: ENDONAUTICA
    # ──────────────────────────────────────────────────────────────────

    {
        "nombre": "Endonautica — Fundamentos del Viaje Interior",
        "categoria": "ebook",
        "autor_ref": "Franco Jeria Castro",
        "chunks": [
            """El endonauta es aquel que emprende el viaje hacia su propio interior. La palabra combina "endo" (interior) con "nauta" (navegante): navegante del mundo interior. A diferencia del astronauta que viaja hacia el cosmos externo, el endonauta explora el universo interno: sus emociones, pensamientos, patrones inconscientes, heridas, potenciales y conexión con algo más grande que sí mismo.

El viaje endonauta no es escapismo ni negación del mundo externo. Es una inversión de atención: en lugar de buscar afuera las respuestas, los recursos o la validación, el endonauta aprende a encontrar dentro de sí mismo la fuente de su poder, su propósito y su paz. La premisa central es que el mundo externo es siempre un reflejo del mundo interno.""",

            """Los pilares del endonauta son: el Observador (la capacidad de verse a sí mismo sin identificarse con lo que se ve), la Autorregulación (la habilidad de navegar los estados emocionales), el Autoconocimiento (conocer la estructura de la propia psique: yo, identidad, personalidad, sombra, heridas), el Cuerpo (como mapa y vehículo del ser), y la Filosofía (el marco de creencias desde el cual se interpreta la experiencia).

El observador es el aspecto de la conciencia que puede presenciar sin juzgar. No es la mente que analiza ni el ego que defiende: es la conciencia pura que observa los propios pensamientos, emociones y reacciones como si fueran nubes pasando por el cielo. Desarrollar el observador interno es el primer paso del viaje endonauta.""",

            """La autorregulación endonauta sigue un ciclo de cuatro etapas: 1) Identificación (reconocer el estado emocional o el impulso), 2) Expresión (dar cauce a lo que emerge, no suprimirlo), 3) Reflexión (entender el origen y el mensaje de esa emoción), y 4) Regulación (volver a un estado de equilibrio desde la comprensión, no desde la represión). Este ciclo, basado en la Gestalt y el trabajo de Joseph Zinker, reemplaza el control por la conciencia.

El autoconocimiento es el mapa del territorio interior. Incluye comprender la diferencia entre el yo esencial (la conciencia pura), la identidad (quién creo ser), y la personalidad (cómo me muestro al mundo). Incluye también reconocer la sombra —las partes de sí mismo que han sido rechazadas— y las heridas de infancia que siguen condicionando el presente.""",

            """La filosofía del endonauta se organiza en torno a varias leyes espirituales: la ley de la unidad (todo está interconectado), la ley de la dualidad (toda polaridad contiene su opuesto y su complemento), la ley fractal (los patrones se repiten a diferentes escalas), la ley de la vibración (todo es energía en movimiento), y la ley espejo (el mundo externo refleja el mundo interno).

El endonauta no busca un salvador externo. La filosofía del implícito (Mauricio Beuchot) y el focusing (Eugene Gendlin) nos recuerdan que gran parte de lo que necesitamos saber ya está en nosotros, en el lenguaje del cuerpo, en las emociones que emergen, en los patrones que se repiten. La tarea es aprender a leer ese lenguaje.""",

            """El cuerpo del endonauta es mucho más que un vehículo físico. Es el lugar donde se almacenan las emociones no procesadas, donde las heridas de infancia dejan su huella, donde la energía fluye o se bloquea. El Ayurveda, la Medicina Tradicional China y la Teoría Sintérgica de Jacobo Grinberg convergen en una visión del cuerpo como campo energético vivo, en constante diálogo con la mente y el entorno.

Los cuerpos sutiles —etérico, emocional, mental y espiritual— son capas de la experiencia que van más allá del cuerpo físico. El cuerpo de ensueño, concepto central en el chamanismo tolteca de Carlos Castaneda, es el vehículo de la conciencia en estados alterados, en el sueño lúcido y en la exploración de dimensiones no ordinarias de la realidad.""",
        ],
    },

    {
        "nombre": "Endonautica — El Espejo: Mundo Interior como Reflejo",
        "categoria": "ebook",
        "autor_ref": "Franco Jeria Castro",
        "chunks": [
            """La ley espejo es central en la filosofía endonauta: todo lo que experimentamos en el mundo exterior es un reflejo de nuestro mundo interior. Las personas que nos generan conflicto son espejos de aspectos de nosotros mismos que no hemos integrado. Las situaciones que se repiten son patrones fractales de creencias o heridas no resueltas.

Neville Goddard lo expresa con precisión: "Deja de intentar cambiar el mundo, ya que es solo un espejo. El intento del hombre de cambiar el mundo por la fuerza es tan infructuoso como romper un espejo con la esperanza de cambiar su rostro. Deja el espejo y cambia tu cara."

Esta perspectiva invierte radicalmente la relación con el conflicto: en lugar de ver al otro como el problema, el endonauta pregunta: ¿qué me está mostrando esta situación sobre mí mismo?""",

            """El espejo puede ser incómodo porque refleja no solo nuestra luz, sino también nuestra sombra. Jung llamó "proyección" al mecanismo por el cual atribuimos a otros lo que no queremos ver en nosotros mismos. Cuando alguien nos irrita profundamente, probablemente está reflejando una cualidad que hemos rechazado o reprimido en nuestra propia psique.

La herida de infancia también se activa a través del espejo relacional. Una persona que en la infancia no recibió suficiente reconocimiento tenderá a percibir rechazo donde quizás no lo hay. Una persona con herida de traición verá señales de deslealtad en comportamientos inocentes. El espejo relacional revela el sistema de percepción filtrado por la herida.""",

            """El trabajo con el espejo no es masoquismo ni autoflagelación. Es curiosidad. Es la práctica de preguntarse: "¿Qué dice este conflicto sobre mi mundo interior? ¿Qué emoción se activa en mí y de dónde viene? ¿Qué patrón se está repitiendo?" Esta actitud transforma el conflicto de un obstáculo en un maestro.

El Mirror Endonauta (Espejo de Conflictos) es un espacio para practicar exactamente esto: usar la conversación como espejo, explorar el mundo interior a través del conflicto, y devolver siempre la mirada hacia adentro. No para culpar al usuario, sino para empoderarle: si el conflicto emerge desde adentro, desde adentro también puede transformarse.""",
        ],
    },

    # ──────────────────────────────────────────────────────────────────
    # CARL GUSTAV JUNG
    # ──────────────────────────────────────────────────────────────────

    {
        "nombre": "Carl Gustav Jung — Arquetipos, Sombra e Individuación",
        "categoria": "marco_teorico",
        "autor_ref": "Carl Gustav Jung",
        "chunks": [
            """Carl Gustav Jung (1875-1961) fue psiquiatra suizo y fundador de la psicología analítica. Discípulo de Freud, se separó de él al rechazar el énfasis exclusivo en la sexualidad como motor del inconsciente y proponer en cambio una visión más amplia: el inconsciente colectivo.

Para Jung, la psique tiene tres niveles: la conciencia (lo que sabemos de nosotros mismos), el inconsciente personal (memorias, experiencias y emociones reprimidas o no procesadas), y el inconsciente colectivo (un sustrato compartido por toda la humanidad, compuesto de imágenes y patrones universales llamados arquetipos).

Jung afirmó: "De una manera u otra somos partes de una sola mente que todo lo abarca, un único gran ser humano." Esta perspectiva sitúa al individuo no como una entidad aislada, sino como una expresión única de un campo de conciencia compartido.""",

            """El concepto más conocido de Jung para el trabajo endonauta es la Sombra: el repositorio de todo lo que la persona ha rechazado, suprimido o negado de sí misma. La sombra no es simplemente lo "malo" —también puede contener potenciales no desarrollados, creatividad reprimida, sensibilidad bloqueada.

La sombra se proyecta en otros: lo que más nos molesta de los demás suele ser lo que no podemos ver en nosotros mismos. El trabajo con la sombra (que Jung llamó integración o individuación) no consiste en eliminarla sino en reconocerla, aceptarla y así recuperar la energía atrapada en la represión.

Las pesadillas, los sueños perturbadores y los personajes que nos generan reacciones emocionales intensas son frecuentemente mensajeros de la sombra que busca ser reconocida e integrada.""",

            """Los arquetipos son patrones universales de la psique humana, plantillas de experiencia que se repiten en todas las culturas y épocas. Jung identificó muchos: la Gran Madre, el Anciano Sabio, el Héroe, la Sombra, el Ánima (lo femenino en el hombre), el Ánimus (lo masculino en la mujer), el Sí-mismo (Self) —el centro totalizador de la psique.

Jean Shinoda Bolen expandió este trabajo identificando arquetipos específicos en figuras mitológicas griegas (dioses y diosas). Cada persona tiene arquetipos dominantes que moldean su psicología, sus relaciones y su camino de vida.

Conocer los propios arquetipos es una forma de autoconocimiento profundo: ayuda a entender patrones relacionales recurrentes, vocaciones no reconocidas, y la estructura del mundo interno.""",

            """La individuación es el proceso central de desarrollo psicológico en Jung: el camino hacia la integración de todas las partes de la psique en una totalidad funcional. No es un estado final sino un proceso continuo de hacerse uno mismo, de llegar a ser quien genuinamente se es.

La individuación requiere enfrentar la sombra, integrar el ánima/ánimus, y establecer una relación consciente con el Self (el centro ordenador de la psique, lo que Jung también relacionó con imágenes del Sí-mismo en diversas tradiciones espirituales).

Los sueños son para Jung el lenguaje privilegiado del inconsciente. A través de símbolos, los sueños comunican lo que la conciencia aún no puede ver. Llevar un diario de sueños y trabajar con sus imágenes es una práctica central del camino junguiano.""",

            """Los 12 arquetipos de personalidad que Jung identificó —y que han sido sistematizados en distintas versiones— incluyen el Inocente, el Explorador, el Sabio, el Héroe, el Forajido, el Mago, el Hombre Común, el Amante, el Bufón, el Cuidador, el Creador y el Gobernante. Cada uno representa una forma particular de estar en el mundo, de encontrar sentido y de relacionarse.

El conocimiento de los propios arquetipos dominantes —que puede explorarse a través de los tests de MirrorWork o mediante introspección profunda— permite comprender patrones que antes parecían misteriosos: por qué ciertos tipos de relaciones se repiten, qué roles asumimos sin darnos cuenta, qué necesidades fundamentales guían nuestras decisiones.""",
        ],
    },

    # ──────────────────────────────────────────────────────────────────
    # SIGMUND FREUD
    # ──────────────────────────────────────────────────────────────────

    {
        "nombre": "Sigmund Freud — Inconsciente, Estructura Psíquica y Sueños",
        "categoria": "marco_teorico",
        "autor_ref": "Sigmund Freud",
        "chunks": [
            """Sigmund Freud (1856-1939) fue el fundador del psicoanálisis y el primero en sistematizar el concepto del inconsciente como una instancia psíquica activa y determinante del comportamiento humano. Su contribución, aunque controversial y parcialmente superada, sigue siendo el punto de partida de toda la psicología profunda.

Freud propuso que la psique tiene dos grandes instancias: el inconsciente (material reprimido, inaccesible directamente a la conciencia), el preconsciente (material que puede acceder a la conciencia con cierto esfuerzo), y la conciencia. El inconsciente personal contiene las experiencias dolorosas, los deseos inaceptables y los traumas que el ego ha excluido de la conciencia.

La gran contribución de Freud es haber demostrado que lo que no sabemos que sabemos nos gobierna. Los "lapsus freudianos", los síntomas, los sueños y las repeticiones compulsivas son mensajes del inconsciente.""",

            """La segunda topología freudiana —la más conocida— divide la psique en tres instancias funcionales: el Ello (Id), el Yo (Ego) y el Superyó (Superego).

El Ello es la sede de los impulsos primarios, los deseos y la energía libidinal. Funciona según el principio del placer: quiere satisfacción inmediata sin consideración de la realidad o la moral. El Yo es la instancia mediadora que opera según el principio de realidad: gestiona las demandas del Ello, las restricciones del Superego y las exigencias del mundo externo. El Superego es el representante interno de las normas culturales y parentales: la conciencia moral, el ideal del yo.

Esta estructura —conocida en el Análisis Transaccional como Padre/Adulto/Niño— aparece de diversas formas en todos los sistemas de comprensión psicológica.""",

            """Para Freud, los sueños son "la vía regia al inconsciente". Durante el sueño, la censura del ego se relaja y el material inconsciente puede emerger, aunque generalmente disfrazado en símbolos y narrativas que Freud llamó "elaboración del sueño". Distinguió entre el contenido manifiesto (lo que el sueño parece contar) y el contenido latente (su significado profundo).

El trabajo con los sueños —desde Freud, expandido enormemente por Jung— es una práctica central del autoconocimiento. Los sueños revelan conflictos no resueltos, deseos no reconocidos, miedos operando bajo la conciencia, y también recursos y potenciales no desarrollados.

En el camino endonauta, los sueños son mensajeros del inconsciente y mapa del territorio interior. Registrarlos y explorarlos es parte del viaje.""",
        ],
    },

    # ──────────────────────────────────────────────────────────────────
    # CARLOS CASTANEDA / DON JUAN MATUS
    # ──────────────────────────────────────────────────────────────────

    {
        "nombre": "Carlos Castaneda / Don Juan — Cosmovisión Tolteca y Cuerpo Energético",
        "categoria": "marco_teorico",
        "autor_ref": "Carlos Castaneda",
        "chunks": [
            """Carlos Castaneda (1925-1998) fue un antropólogo y escritor que documentó sus enseñanzas con el chamán yaqui Don Juan Matus en una serie de libros que se convirtieron en referencia fundamental del pensamiento transpersonal del siglo XX. Aunque la veracidad de sus relatos ha sido debatida, su impacto cultural y espiritual es innegable.

La cosmovisión tolteca que Castaneda transmite presenta al ser humano como un ser luminoso —un huevo de energía— cuyo centro de conciencia (el punto de encaje) determina qué aspectos de la realidad puede percibir. La mayor parte de las personas tiene el punto de encaje fijo en una posición que genera la percepción ordinaria del mundo. Los estados alterados de conciencia, el sueño lúcido y ciertas prácticas chamánicas pueden mover el punto de encaje, abriendo la percepción a otras dimensiones de la realidad.

Castaneda cita a Don Juan: "Poco sabía yo en ese tiempo que don Juan no me estaba dando solamente una descripción intelectual atractiva; me estaba describiendo algo que él llamaba un hecho energético."
""",

            """El cuerpo de ensueño (cuerpo sutil o cuerpo de energía) es un concepto central en las enseñanzas toltecas. Es el vehículo de la conciencia que puede separarse del cuerpo físico durante el sueño lúcido o la meditación profunda. Castaneda describe prácticas para desarrollar este cuerpo: comenzar en el sueño lúcido por buscar las propias manos, estabilizar el sueño, y eventualmente usar el cuerpo de ensueño para exploración.

El sueño lúcido —el estado en que uno sabe que está soñando dentro del sueño— no es solo una curiosidad neurocientífica. En la tradición tolteca, es una puerta de acceso a realidades más profundas y una práctica de expansión de la conciencia. El endonauta puede usar el sueño lúcido para explorar la sombra, trabajar con arquetipos y acceder a dimensiones del inconsciente que la mente despierta no puede alcanzar.

Castaneda también habla del diálogo interno: la voz constante dentro de la mente que narra, juzga y etiqueta la experiencia. "El pasaje al mundo de los chamanes se abre cuando el guerrero ha aprendido a parar su diálogo interno."
""",

            """El Nagual y el Tonal son conceptos centrales en la cosmología tolteca, también presentes en el trabajo de Miguel Ruiz. El Tonal es todo lo que tiene nombre, toda la realidad conocida, el mundo organizado por la mente. El Nagual es lo indescriptible, lo que existe más allá de los nombres, la vasta realidad que la mente ordinaria no puede capturar.

La tradición tolteca propone que la sociedad y la cultura nos "domestican" desde la infancia, enseñándonos a percibir el mundo de una manera particular y a suprimir o ignorar todo lo que no cabe en esa descripción acordada del mundo. El camino del guerrero —el camino de conocimiento tolteca— es recuperar la conciencia de que esa descripción es solo una entre infinitas posibles.

Esta perspectiva es profundamente liberadora: si el problema no está en el mundo sino en la descripción del mundo que operamos, entonces transformar esa descripción transforma la experiencia de vivir.""",
        ],
    },

    # ──────────────────────────────────────────────────────────────────
    # JACOBO GRINBERG
    # ──────────────────────────────────────────────────────────────────

    {
        "nombre": "Jacobo Grinberg — Teoría Sintérgica y el Observador",
        "categoria": "marco_teorico",
        "autor_ref": "Jacobo Grinberg",
        "chunks": [
            """Jacobo Grinberg-Zylberbaum (1946-1994) fue un neurocientífico y psicólogo mexicano, creador de la Teoría Sintérgica, una de las propuestas más audaces de integración entre neurociencia, física cuántica y espiritualidad. Desapareció misteriosamente en 1994 y su obra sigue siendo referencia en los estudios de conciencia.

La Teoría Sintérgica propone que el cerebro actúa como un decodificador de un campo de energía fundamental al que Grinberg llamó el Lattice (la Lattice o Retícula). La Lattice es una estructura de energía que permea todo el universo, análoga al concepto de campo cuántico en física. El cerebro no genera la conciencia sino que la "sintoniza" desde este campo.

La experiencia que llamamos "mundo" no es la realidad objetiva sino una construcción neurológica: la mente interpreta las señales del Lattice y genera la percepción de un mundo externo. Esta idea —que la realidad percibida es una construcción de la conciencia— conecta la neurociencia con las enseñanzas de prácticamente todas las tradiciones espirituales.""",

            """El Observador es el concepto más importante de Grinberg para el camino endonauta. El Observador es la instancia de la conciencia que puede presenciar sin identificarse. No es el ego que reacciona, no es la mente que analiza: es la conciencia pura que observa los propios estados internos desde un espacio de ecuanimidad.

Grinberg propone que el desarrollo del Observador es la clave del desarrollo de la conciencia. Cuanto más desarrollado está el Observador, menos automática y reactiva es la persona, y más capaz de elegir sus respuestas en lugar de simplemente reaccionar desde el condicionamiento.

Ken Wilber (citado en Endonautica a través de Grinberg) sostiene que los límites que establecemos en nuestra identidad dependen de nuestro nivel de conciencia: en niveles bajos, nos identificamos solo con el ego; en niveles más altos, con el cuerpo; más allá, con la mente y el espíritu. El Observador puede eventualmente identificarse con la totalidad.""",

            """Grinberg identificó niveles neurológicos de la conciencia que corresponden a diferentes grados de apertura y presencia. El nivel más básico es el del automatismo reactivo (reaccionar desde el condicionamiento sin presencia). Los niveles superiores implican mayor apertura, menos filtrado de la experiencia, mayor capacidad de presencia y finalmente estados de conciencia expandida o unitiva.

La práctica de meditación, desde la perspectiva sintérgica, es literalmente un entrenamiento del cerebro para sintonizar con frecuencias más altas del Lattice. No es solo relajación o descanso: es una práctica de expansión de la conciencia con correlatos neurológicos medibles.

Este marco da base científica a prácticas que desde afuera pueden parecer meramente "espirituales": el silencio mental, la presencia plena, el trabajo con el cuerpo energético. Son, en la visión de Grinberg, maneras de afinar la antena que es el cerebro.""",
        ],
    },

    # ──────────────────────────────────────────────────────────────────
    # DAVID HAWKINS
    # ──────────────────────────────────────────────────────────────────

    {
        "nombre": "David Hawkins — Mapa de la Conciencia",
        "categoria": "marco_teorico",
        "autor_ref": "David Hawkins",
        "chunks": [
            """David R. Hawkins (1927-2012) fue psiquiatra, médico y maestro espiritual estadounidense, autor de "Power vs. Force" y creador del Mapa de la Conciencia —una escala que ubica los estados emocionales y espirituales en niveles de energía numerados del 20 al 1000.

La premisa del mapa es que cada estado de conciencia —cada emoción, cada creencia, cada nivel de desarrollo espiritual— tiene una frecuencia energética medible. Hawkins usó la kinesiología como método de investigación, aunque este método ha sido cuestionado científicamente. Sin embargo, el mapa como herramienta conceptual sigue siendo valioso para el trabajo de autoconocimiento.

Los niveles más bajos (vergüenza: 20, culpa: 30, apatía: 50, miedo: 100) drenan energía vital y perpetúan patrones de sufrimiento. El nivel 200 —coraje— es el punto de inflexión: por debajo, la energía va en contra de la vida; por encima, comienza a servir a la vida. El amor está en 500, la iluminación comienza en 700.""",

            """La escala de Hawkins ofrece un mapa útil para ubicar los propios estados emocionales no como juicios morales sino como niveles de frecuencia. Un estado de miedo no es "malo": es simplemente una vibración baja que genera ciertos tipos de percepción y comportamiento. El trabajo de conciencia consiste en elevar la propia frecuencia habitual.

Hawkins relaciona los niveles con estilos de vida, formas de relacionarse y patrones de pensamiento. La vergüenza genera autodestrucción. La culpa genera autopunición. El miedo genera evitación. La ira genera reactividad. La soberbia genera cerrazón. El coraje genera apertura. La neutralidad genera desapego funcional. La voluntad genera esfuerzo dirigido. La aceptación genera amor sin condiciones. La razón genera comprensión. El amor genera servicio. La alegría genera presencia. La paz genera quietud. La iluminación es la identidad con la conciencia misma.

Para el endonauta, este mapa permite preguntar en cualquier momento: ¿desde qué nivel de conciencia estoy operando ahora?""",

            """Hawkins propone que gran parte de las decisiones humanas se toman desde niveles de conciencia que la persona no puede ver claramente en sí misma. Las creencias operativas, los filtros emocionales y los condicionamientos funcionan por debajo del umbral de la conciencia ordinaria.

Una de sus afirmaciones más poderosas para el trabajo endonauta: la diferencia entre una vida con sufrimiento y una vida con sentido no depende de las circunstancias externas sino del nivel de conciencia desde el cual se interpreta la experiencia. Dos personas pueden vivir exactamente la misma situación y tener experiencias radicalmente diferentes según el nivel desde el que la perciben.

El trabajo de elevar la conciencia no es optimismo forzado ni negación. Es un trabajo real de liberarse de creencias limitantes, integrar la sombra, desarrollar el observador y ampliar la capacidad de amor y presencia.""",
        ],
    },

    # ──────────────────────────────────────────────────────────────────
    # NEVILLE GODDARD
    # ──────────────────────────────────────────────────────────────────

    {
        "nombre": "Neville Goddard — Conciencia como Proyectora de la Realidad",
        "categoria": "marco_teorico",
        "autor_ref": "Neville Goddard",
        "chunks": [
            """Neville Lancelot Goddard (1905-1972) fue un maestro espiritual barbadense-estadounidense que enseñó una interpretación radical de los textos bíblicos: toda la Biblia es psicología, un mapa del funcionamiento de la conciencia humana. Su enseñanza central es que la conciencia es la única realidad y que todo lo que experimentamos como "mundo externo" es una proyección de nuestro estado interno.

"Tu mundo no es más que una proyección de tu estado de conciencia" es su premisa fundamental. Esto no es pensamiento mágico sino una inversión epistemológica profunda: si la conciencia precede a la experiencia, entonces transformar el estado de conciencia transforma la experiencia de vivir.

Esta visión conecta con la ley espejo del pensamiento endonauta y con la Teoría Sintérgica de Grinberg: lo que percibimos como "realidad objetiva" es en gran medida una construcción de nuestra conciencia.""",

            """La ley espejo de Goddard se expresa en su cita más conocida: "Deja de intentar cambiar el mundo, ya que es solo un espejo. El intento del hombre de cambiar el mundo por la fuerza es tan infructuoso como romper un espejo con la esperanza de cambiar su rostro. Deja el espejo y cambia tu cara. Deja el mundo en paz y cambia tus concepciones de ti mismo."

Esta enseñanza es especialmente relevante para el trabajo con conflictos: si el conflicto externo es un espejo del mundo interno, buscar cambiar al otro o a la situación sin cambiar primero el estado interno es como reordenar los muebles mientras la casa está en llamas. El trabajo real es interior.

Esto no significa pasividad o resignación: significa que la transformación real comienza dentro. Una vez que cambia el estado interno, cambia la percepción, cambian las reacciones, y frecuentemente cambia también el mundo externo.""",

            """Goddard enseñó la importancia del sueño y del estado hipnagógico (el estado entre la vigilia y el sueño) como momentos de acceso privilegiado al subconsciente. En este estado, las imágenes y los sentimientos que asumimos como reales se "graban" en el subconsciente y se manifiestan en la experiencia.

La práctica que propone es lo que hoy llamaríamos visualización con estado emocional: no solo imaginar lo deseado sino sentirlo como ya real, habitar mentalmente el estado emocional de haberlo recibido. Esta práctica, que el endonauta puede usar para programar estados de conciencia más elevados, actúa directamente sobre el subconsciente.

Para el Mirror Endonauta, la enseñanza de Goddard invita a explorar: ¿Qué estado de conciencia estás proyectando en esta situación de conflicto? ¿Qué creencia o emoción subyacente está generando esta percepción?""",
        ],
    },

    # ──────────────────────────────────────────────────────────────────
    # MIGUEL RUIZ
    # ──────────────────────────────────────────────────────────────────

    {
        "nombre": "Miguel Ruiz — Los Cuatro Acuerdos y el Sueño del Planeta",
        "categoria": "marco_teorico",
        "autor_ref": "Miguel Ángel Ruiz",
        "chunks": [
            """Miguel Ángel Ruiz (1952) es un médico y maestro espiritual mexicano, heredero de la tradición tolteca transmitida por su madre chamán. Su libro "Los Cuatro Acuerdos" es uno de los más leídos del mundo en desarrollo personal.

Su concepto central es el del "Sueño del Planeta": desde la infancia, la familia, la cultura y la sociedad nos enseñan a soñar un sueño particular —una descripción del mundo, de nosotros mismos, de lo que es posible. Esto ocurre a través de un proceso que Ruiz llama la "domesticación": el niño aprende a obtener amor y aprobación comportándose de cierta manera, y gradualmente interioriza ese sistema de creencias.

Este sueño —este conjunto de acuerdos que hemos hecho sobre quiénes somos y cómo funciona el mundo— determina nuestra experiencia de realidad. Si los acuerdos son limitantes o dolorosos, el sueño es una pesadilla. La liberación consiste en tomar conciencia de los acuerdos que operamos y elegir nuevos acuerdos más alineados con nuestra verdad.""",

            """Los Cuatro Acuerdos de Ruiz son propuestas para una nueva forma de relacionarse con uno mismo y con el mundo:

1. Sé impecable con tus palabras: el lenguaje tiene poder creador. Lo que dices de ti mismo y de otros tiene consecuencias reales. Las palabras con las que te describes a ti mismo son acuerdos que el subconsciente acepta como verdad.

2. No te tomes nada personalmente: lo que los demás dicen y hacen es proyección de su propio sueño, no un comentario objetivo sobre ti. Tomar las cosas personalmente es el origen de gran parte del sufrimiento relacional.

3. No hagas suposiciones: gran parte del conflicto surge de suponer que sabemos lo que el otro piensa, siente o intenta. Preguntar en lugar de suponer transforma las relaciones.

4. Haz siempre lo máximo que puedas: lo máximo cambia según el momento. No es perfeccionismo sino presencia y honestidad en el esfuerzo.

Para el endonauta, estos acuerdos son prácticas concretas de transformación de los patrones de pensamiento y relacionamiento.""",

            """La historia del Espejo Humeante, que abre el libro de Ruiz, describe a un sabio tolteca que miraba el cielo estrellado y tuvo una revelación: los humanos son creadores, como el sol que emite luz. Pero en lugar de luz, emitimos sueños —proyecciones de nuestra conciencia. El problema es que soñamos dormidos, sin darnos cuenta de que estamos soñando.

El Espejo Humeante (Tezcatlipoca en la mitología azteca) es el espejo que no refleja con claridad porque está cubierto de humo —el humo de las creencias, los condicionamientos, las proyecciones. Ver con claridad requiere limpiar el espejo: tomar conciencia de los acuerdos que operamos.

Esta metáfora es el corazón del Mirror Endonauta: el espejo siempre refleja, pero cuanto más limpio está, más fiel es el reflejo. El trabajo de autoconocimiento es precisamente limpiar ese espejo para ver la propia verdad con mayor claridad.""",
        ],
    },

    # ──────────────────────────────────────────────────────────────────
    # JOSEPH CAMPBELL
    # ──────────────────────────────────────────────────────────────────

    {
        "nombre": "Joseph Campbell — El Viaje del Héroe",
        "categoria": "marco_teorico",
        "autor_ref": "Joseph Campbell",
        "chunks": [
            """Joseph Campbell (1904-1987) fue un mitólogo y escritor estadounidense cuya obra más conocida, "El Héroe de las Mil Caras" (1949), identifica un patrón narrativo universal presente en los mitos de todas las culturas del mundo: el monomito o Viaje del Héroe.

El Viaje del Héroe tiene tres grandes etapas: la Partida (el héroe recibe un llamado y abandona el mundo ordinario), la Iniciación (enfrenta pruebas, llega al punto más oscuro y obtiene el conocimiento o poder que busca), y el Retorno (vuelve al mundo ordinario transformado y trae consigo el conocimiento obtenido para compartirlo).

Campbell argumentó que este patrón no es solo una estructura narrativa sino un mapa del desarrollo psicológico humano. El "llamado" es la vocación interior que llama al individuo a crecer. La "cueva más oscura" es el encuentro con la sombra y los miedos más profundos. El "retorno" es la integración de la experiencia y la transmisión del aprendizaje.""",

            """Para el endonauta, el Viaje del Héroe es el mapa del propio camino de autoconocimiento. No se trata necesariamente de hazañas externas: la batalla más importante es la interna. El dragón que hay que enfrentar es la sombra propia, los miedos, las creencias limitantes, la herida de infancia.

El llamado puede manifestarse como una crisis, una pérdida, una insatisfacción profunda, o una pregunta que ya no puede ignorarse. Muchas personas rechazan el llamado por miedo al cambio —Campbell lo llamó el "rechazo del llamado". El resultado de ese rechazo no es la estabilidad sino el estancamiento y frecuentemente el sufrimiento.

La figura del Menthor en el viaje del héroe —el sabio que ofrece orientación, herramientas y coraje— puede manifestarse en personas concretas, en libros, en prácticas, en momentos de insight. El Mirror Endonauta puede funcionar como Mentor: no dando respuestas sino ayudando al héroe-endonauta a encontrar sus propias respuestas.""",

            """Campbell también subrayó la importancia de la "gracia peligrosa" del Viaje: el proceso de transformación genuino siempre implica riesgo. La persona que busca crecer sin incomodarse, sin perder certezas, sin enfrentar su sombra, no está en el viaje del héroe sino en una versión cómoda y estéril del autoconocimiento.

El punto de mayor oscuridad del viaje —la "cueva más oscura"— no debe evitarse sino atravesarse. Es en ese punto de máxima dificultad donde se encuentra el mayor recurso. En psicología junguiana, esto corresponde al trabajo con la sombra: los fragmentos de nosotros mismos que más rechazamos son, paradójicamente, los que contienen más energía vital.

Para el endonauta que enfrenta un conflicto: ¿en qué etapa del Viaje del Héroe te encuentras ahora? ¿Estás rechazando el llamado, atravesando la cueva oscura, o integrando el conocimiento obtenido?""",
        ],
    },

    # ──────────────────────────────────────────────────────────────────
    # CLAUDIO NARANJO
    # ──────────────────────────────────────────────────────────────────

    {
        "nombre": "Claudio Naranjo — Eneagrama, Psicología y Despertar",
        "categoria": "marco_teorico",
        "autor_ref": "Claudio Naranjo",
        "chunks": [
            """Claudio Naranjo (1932-2019) fue un psiquiatra chileno, uno de los pioneros de la psicología transpersonal y el integrador más importante del Eneagrama como sistema de autoconocimiento psicológico. Estudió con Fritz Perls (Gestalt), con las tradiciones espirituales de Oriente y Occidente, y desarrolló los programas de autoconocimiento SAT (Seekers After Truth).

Naranjo popularizó y sistematizó el Eneagrama de la personalidad —originalmente transmitido por Gurdjieff y Óscar Ichazo— como una herramienta de comprensión psicológica profunda, no solo tipológica sino terapéutica. Identificó los 9 tipos de personalidad no como categorías fijas sino como estructuras del ego que surgen de heridas de infancia y que ocultan el ser esencial de la persona.

Una de sus frases más citadas: "Al sistema le conviene que uno no esté tanto en contacto consigo mismo." Esta afirmación sitúa el autoconocimiento como un acto de liberación personal y colectiva.""",

            """El Eneagrama de Naranjo va más allá de la tipología: cada tipo de personalidad corresponde a una "pasión" (un patrón emocional central) y a un "vicio" (un patrón cognitivo automático). El trabajo con el Eneagrama no es solo identificar el propio tipo sino comprender la pasión que lo sostiene y desarrollar la virtud opuesta.

Los 9 tipos son: 1-Perfeccionista (ira/serenidad), 2-Servicial (orgullo/humildad), 3-Triunfador (vanidad/autenticidad), 4-Romántico (envidia/ecuanimidad), 5-Observador (avaricia/desapego), 6-Leal (miedo/coraje), 7-Entusiasta (gula/sobriedad), 8-Desafiador (lujuria/inocencia), 9-Mediador (pereza/acción).

Conocer el propio tipo permite ver el filtro automático que la personalidad aplica a la experiencia, las estrategias inconscientes que despliega, y los recursos que permanecen bloqueados por ese patrón.""",

            """Naranjo también fue pionero en la integración de psicodélicos, meditación y psicoterapia en el trabajo de autoconocimiento. Estudió con maestros espirituales de diversas tradiciones y propuso que el desarrollo humano genuino requiere una integración de las dimensiones psicológica, espiritual y somática.

Para el trabajo con el Mirror Endonauta, el Eneagrama ofrece un lenguaje preciso para identificar patrones relacionales: ¿qué tipo de personalidad está operando en este conflicto? ¿Qué pasión (ira, miedo, envidia, orgullo...) está activada? ¿Qué necesidad fundamental no satisfecha está en el origen del patrón?

El Eneagrama también permite comprender a los otros: cada tipo de personalidad tiene miedos, deseos y estrategias particulares. Conocerlos no es para etiquetar sino para generar comprensión y compasión.""",
        ],
    },

    # ──────────────────────────────────────────────────────────────────
    # EUGENE GENDLIN
    # ──────────────────────────────────────────────────────────────────

    {
        "nombre": "Eugene Gendlin — Focusing y la Sabiduría del Cuerpo",
        "categoria": "marco_teorico",
        "autor_ref": "Eugene Gendlin",
        "chunks": [
            """Eugene T. Gendlin (1926-2017) fue un filósofo y psicólogo estadounidense, colaborador de Carl Rogers en la Universidad de Chicago. Su trabajo más conocido es el Focusing, una técnica y una filosofía que propone que el cuerpo tiene un conocimiento implícito que precede al lenguaje y que puede accederse a través de una atención particular a las sensaciones corporales.

Gendlin desarrolló el concepto de "felt sense" (sensación sentida): la percepción holística, pre-verbal y corporal de una situación o problema. Esta sensación no es una emoción definida ni un pensamiento claro: es algo difuso, complejo, que el cuerpo "sabe" pero que aún no tiene palabras. El Focusing es el proceso de prestar atención a ese felt sense, acompañarlo con paciencia, y permitir que se revele y se movilice.

Esta perspectiva es radicalmente diferente al análisis intelectual: en lugar de pensar sobre el problema, el Focusing invita a sentir el problema desde adentro, a contactar lo que el cuerpo sabe sobre él.""",

            """La teoría procesal de Gendlin propone que la conciencia implícita —ese conocimiento que no puede expresarse con palabras— es un recurso fundamental para el cambio personal y el crecimiento. El proceso experiencial (lo que ocurre en el nivel del cuerpo y la conciencia en el momento presente) es más fundamental que los pensamientos o los comportamientos.

Gendlin desarrolló el Focusing a partir de su investigación sobre qué distinguía a los clientes que progresaban en terapia de los que no progresaban. La diferencia no estaba en el tipo de terapia ni en el terapeuta: estaba en que los clientes que progresaban tenían la habilidad de contactar y explorar sus sensaciones corporales relacionadas con sus problemas, en lugar de solo hablar sobre ellos desde afuera.

Para el endonauta, esto significa que el camino al autoconocimiento pasa por el cuerpo: la mente puede teorizar indefinidamente, pero el cambio real ocurre cuando se contacta el nivel somático de la experiencia.""",

            """Gendlin también relacionó su trabajo con la filosofía del lenguaje de Merleau-Ponty y con la hermenéutica. Su concepto de "filosofía del implícito" (también desarrollado por Mauricio Beuchot en el mundo hispano) propone que gran parte de lo que sabemos, sentimos y necesitamos existe en un nivel pre-verbal que el lenguaje puede comenzar a articular pero nunca captura completamente.

Esta perspectiva tiene implicaciones prácticas para el trabajo del Mirror Endonauta: a veces las preguntas más valiosas no son las que buscan respuestas racionales sino las que abren espacio para que emerja lo implícito. "¿Cómo se siente eso en tu cuerpo?" "¿Qué hay en ese malestar que todavía no tiene palabras?" "¿Qué sabe tu cuerpo sobre esta situación que tu mente todavía no puede articular?"

El diálogo con el cuerpo es una forma de autoconocimiento que la cultura racional ha marginado pero que el endonauta recupera.""",
        ],
    },

    # ──────────────────────────────────────────────────────────────────
    # FRITZ PERLS
    # ──────────────────────────────────────────────────────────────────

    {
        "nombre": "Fritz Perls — Gestalt y el Presente",
        "categoria": "marco_teorico",
        "autor_ref": "Fritz Perls",
        "chunks": [
            """Frederick "Fritz" Perls (1893-1970) fue psiquiatra alemán y cofundador de la Terapia Gestalt, una de las corrientes más influyentes de la psicología humanista. La Gestalt propone que el organismo humano tiende naturalmente hacia la completitud y el equilibrio —que los problemas psicológicos emergen cuando este proceso natural se interrumpe.

La palabra alemana "Gestalt" significa forma completa, totalidad, figura. En psicología, se refiere a la tendencia de la percepción a organizar los estímulos en patrones completos. Perls trasladó este principio a la psicología: cuando una experiencia emocional no se completa —cuando una emoción no se expresa, un conflicto no se resuelve, una necesidad no se satisface— queda como una "gestalt abierta" que demanda energía y atención, interfiriendo con el presente.

La Gestalt trabaja en el aquí y ahora: en lugar de analizar el pasado, trabaja con lo que ocurre en el momento presente, en el cuerpo, en la voz, en los gestos, en la respiración.""",

            """Perls dijo: "Deja que el plan surja dentro de ti." Esta frase resume una epistemología profunda: la dirección genuina para la propia vida no se construye desde el análisis racional sino que emerge desde adentro cuando hay suficiente presencia, honestidad y contacto con uno mismo.

La Gestalt propone que el ser humano tiene una sabiduría organísmica: el cuerpo y el organismo como totalidad saben lo que necesitan. El problema es que la mente, el ego, los condicionamientos y las "introyecciones" (creencias y mandatos absorbidos de otros sin cuestionamiento) interfieren con esa sabiduría natural.

Para el endonauta, la Gestalt ofrece un principio fundamental: confiar en el proceso interior. No en el ego que planifica y controla, sino en la sabiduría del organismo que, cuando hay espacio y presencia suficiente, sabe el camino.""",

            """La Gestalt distingue entre el ciclo de la experiencia y las interrupciones que lo bloquean. El ciclo sano tiene las siguientes etapas: Sensación (algo emerge en el cuerpo), Necesidad (se identifica la necesidad), Movilización (la energía se dirige hacia la satisfacción), Acción (contacto con el entorno), Satisfacción (la necesidad se completa), Retirada (el organismo descansa antes del próximo ciclo).

Las interrupciones del ciclo —retroflexión (hacer a uno mismo lo que querría hacerle al otro), proyección (atribuir al otro lo propio), introyección (absorber sin digerir), confluencia (fusionarse con el otro perdiendo el sí-mismo), deflexión (evitar el contacto real)— son los mecanismos que generan los patrones problemáticos.

Reconocer en qué punto del ciclo ocurre la interrupción propia es una clave diagnóstica y terapéutica del trabajo Gestalt.""",
        ],
    },

    # ──────────────────────────────────────────────────────────────────
    # LISE BOURBEAU
    # ──────────────────────────────────────────────────────────────────

    {
        "nombre": "Lise Bourbeau — Las 5 Heridas de Infancia",
        "categoria": "marco_teorico",
        "autor_ref": "Lise Bourbeau",
        "chunks": [
            """Lise Bourbeau (1941) es terapeuta y escritora canadiense de expresión francesa, autora de "Las 5 heridas que impiden ser uno mismo" —uno de los libros más leídos del desarrollo personal hispano. Su trabajo propone que prácticamente todo el sufrimiento psicológico adulto se origina en una de cinco heridas emocionales de la infancia, y que cada herida genera una máscara —una estructura de personalidad defensiva— para proteger al niño del dolor.

Las 5 heridas son: Rechazo, Abandono, Humillación, Traición e Injusticia. Cada una tiene un origen específico en la relación con los padres o cuidadores, genera una máscara particular (el Huidizo, el Dependiente, el Masoquista, el Controlador, el Rígido), y se activa en situaciones adultas que recuerdan inconscientemente la experiencia original de herida.

El sistema de Bourbeau proporciona un vocabulario preciso para identificar el origen emocional de los patrones relacionales, sin caer en la víctima o en la culpa.""",

            """Las 5 heridas y sus características:

RECHAZO: se siente no deseado, excluido, sin derecho a existir. Máscara del Huidizo: persona que tiende a desaparecer, a volverse pequeña, a evitar el conflicto y la visibilidad. Activada por cualquier situación que se interprete como rechazo.

ABANDONO: miedo a estar solo, necesidad de apoyo externo constante. Máscara del Dependiente: persona que se apoya excesivamente en otros, teme la soledad, crea vínculos de dependencia. Activada por cualquier situación de separación real o imaginada.

HUMILLACIÓN: vergüenza de ser, de tener necesidades, de tomar espacio. Máscara del Masoquista: persona que se pone en último lugar, se hace cargo de los demás, se sacrifica. Activada por situaciones donde siente que sus necesidades son un peso para otros.

TRAICIÓN: desconfianza, necesidad de control y de cumplir las expectativas propias y ajenas. Máscara del Controlador: persona que domina las situaciones, cumple sus promesas con rigidez y espera lo mismo de otros. Activada cuando percibe falta de confiabilidad.

INJUSTICIA: rigidez, perfeccionismo, dificultad para recibir. Máscara del Rígido: persona que se exige mucho a sí misma y a los demás, no se permite errores. Activada por situaciones que se perciben como injustas o que no se ajustan a sus estándares.""",

            """El trabajo con las heridas de Bourbeau no es para buscar culpables —ni en los padres ni en uno mismo. Los padres actuaron desde sus propias heridas no resueltas. La herida se transmite de generación en generación hasta que alguien toma conciencia de ella y la comienza a sanar.

Sanar la herida no significa que desaparezca: significa que deja de gobernar automáticamente las reacciones. El endonauta puede identificar cuándo una herida se activa (porque la reacción emocional es desproporcionada a la situación actual), nombrarla con compasión ("se activó mi herida de rechazo"), y trabajar con el niño/a herido que hay en esa reacción.

El sistema de Bourbeau conecta directamente con el trabajo de la sombra de Jung: la máscara es la estructura con la que el ego enfrenta al mundo, mientras que la herida es el material sombrío que esa máscara oculta. Integrar la herida es integrar la sombra.""",
        ],
    },

    # ──────────────────────────────────────────────────────────────────
    # JOSEPH ZINKER
    # ──────────────────────────────────────────────────────────────────

    {
        "nombre": "Joseph Zinker — Ciclo de Autorregulación",
        "categoria": "marco_teorico",
        "autor_ref": "Joseph Zinker",
        "chunks": [
            """Joseph Zinker (1934) es psicólogo y artista de origen polaco, conocido por su trabajo en Gestalt y por su libro "El proceso creativo en la terapia guestáltica". Su contribución más citada en el marco endonauta es el ciclo de autorregulación, que describe el proceso natural de respuesta a los propios estados internos.

El ciclo de autorregulación de Zinker —construido sobre el ciclo de la experiencia de Perls— tiene cuatro etapas principales en su aplicación endonauta: 1) Identificación (reconocer qué está ocurriendo internamente: qué emoción, sensación o impulso emerge), 2) Expresión (dar cauce a lo que surge, no suprimirlo ni volcarlo destructivamente), 3) Reflexión (comprender el origen y el mensaje de esa emoción), y 4) Regulación (volver a un estado de equilibrio desde la comprensión).

Este ciclo propone que la regulación emocional no es la supresión de las emociones sino su traversía consciente: la emoción emerge, se identifica, se expresa apropiadamente, se comprende, y entonces la energía que tenía atrapada queda liberada.""",

            """La diferencia fundamental entre el ciclo de Zinker y la gestión emocional ordinaria es que el ciclo no intenta "controlar" las emociones sino atravesarlas. La emoción no es el problema: el problema es la emoción no procesada, atrapada en el cuerpo, generando síntomas y reacciones automáticas.

Muchas personas saltan directamente del "identificar" al "regular", saltándose la expresión y la reflexión. Esto produce lo que en Gestalt se llama retroflexión: hacer a uno mismo lo que querría hacer al entorno (represión que se convierte en síntoma físico o en explosión descontrolada posterior).

La expresión no necesariamente significa gritar o llorar: puede ser escribir, moverse, hablar desde un lugar seguro, crear. Lo importante es que la energía de la emoción encuentre un cauce, no que se bloquee.""",
        ],
    },

    # ──────────────────────────────────────────────────────────────────
    # JEAN SHINODA BOLEN
    # ──────────────────────────────────────────────────────────────────

    {
        "nombre": "Jean Shinoda Bolen — Arquetipos en Mitología",
        "categoria": "marco_teorico",
        "autor_ref": "Jean Shinoda Bolen",
        "chunks": [
            """Jean Shinoda Bolen (1936) es psiquiatra jungiana y escritora estadounidense, conocida por sus libros "Las Diosas de Cada Mujer" (1984) y "Los Dioses de Cada Hombre" (1989). Su trabajo aplica la psicología arquetípica de Jung a través de las figuras mitológicas griegas, identificando arquetipos específicos activos en la psicología femenina y masculina.

Bolen propone que los dioses y diosas del panteón griego representan patrones arquetípicos vivos en la psique humana. No son solo figuras históricas o literarias: son mapas de formas particulares de ser, de amar, de sufrir y de encontrar sentido. Cada persona tiene uno o varios arquetipos dominantes que moldean su psicología, sus relaciones y su vocación.

Para las mujeres, Bolen identificó 7 arquetipos femeninos basados en diosas griegas: Artemisa (independencia, naturaleza, metas propias), Atenea (sabiduría estratégica, logro), Hestia (interioridad, espiritualidad), Hera (vínculo, matrimonio), Deméter (maternidad, cuidado), Perséfone (receptividad, iniciación), Afrodita (amor, belleza, creatividad transformadora).""",

            """Para los hombres, Bolen identificó 8 arquetipos basados en dioses griegos: Zeus (poder, autoridad), Poseidón (emociones, espiritualidad), Hades (introspección, lo invisible), Apolo (razón, orden, distancia), Hermes (comunicación, movimiento), Ares (pasión, acción), Hefesto (creatividad artística, soledad productiva), Dioniso (éxtasis, instinto, comunión).

El valor del trabajo de Bolen para el autoconocimiento no es etiquetar sino iluminar. Al reconocer el arquetipo dominante, la persona puede entender mejor sus motivaciones profundas, sus reacciones típicas en las relaciones, sus fuentes de energía y sus zonas de sombra particulares.

También permite reconocer qué arquetipos están subdesarrollados: un hombre muy apollíneo (racional, ordenado, distante) puede necesitar cultivar a Dioniso (corporalidad, conexión emocional, espontaneidad). Una mujer muy heraica (centrada en el vínculo) puede necesitar despertar a Artemisa (autonomía, metas propias).""",
        ],
    },

    # ──────────────────────────────────────────────────────────────────
    # CLARE GRAVES / SPIRAL DYNAMICS
    # ──────────────────────────────────────────────────────────────────

    {
        "nombre": "Clare Graves / Spiral Dynamics — Niveles de Conciencia",
        "categoria": "marco_teorico",
        "autor_ref": "Dr. Clare W. Graves",
        "chunks": [
            """El Dr. Clare W. Graves (1914-1986) fue psicólogo americano cuya investigación sobre el desarrollo de los valores humanos sentó las bases de lo que sus discípulos Don Beck y Christopher Cowan sistematizaron como Spiral Dynamics.

Graves identificó 8 niveles de desarrollo de valores y conciencia, cada uno representado por un color en el sistema de Beck y Cowan. Cada nivel no es mejor o peor moralmente sino una respuesta adaptativa a las condiciones de vida del momento. Los niveles se despliegan en una espiral que puede involucionar bajo presión o evolucionar cuando las condiciones lo permiten.

Los 8 niveles: Beige (supervivencia instintiva), Púrpura (pensamiento mágico tribal), Rojo (poder, ego, dominación), Azul (orden, moralidad, estructura), Naranja (logro, racionalismo, éxito), Verde (comunidad, relativismo, sensibilidad), Amarillo (integración sistémica, complejidad), Turquesa (holismo, conciencia global).""",

            """Para el trabajo endonauta, la Spiral Dynamics ofrece un mapa para comprender los patrones de valores y comportamiento propios y ajenos sin juzgarlos moralmente. Un conflicto frecuente es el que ocurre entre personas en diferentes niveles de la espiral: lo que es obvio y necesario desde un nivel puede ser incomprensible o amenazante desde otro.

El nivel Rojo (poder, ego, "el más fuerte gana") es funcional en ciertas condiciones pero problemático en relaciones íntimas. El nivel Verde (todos somos iguales, el proceso importa más que el resultado) puede ser paralizante en situaciones que requieren decisiones rápidas. El nivel Amarillo puede integrar las perspectivas de todos los niveles sin identificarse con ninguno.

David Hawkins relacionó esta escala con su Mapa de la Conciencia: ambos proponen que la evolución del individuo y la sociedad implica moverse hacia niveles de mayor complejidad, integración y amor.""",
        ],
    },

    # ──────────────────────────────────────────────────────────────────
    # JULIAN ROTTER
    # ──────────────────────────────────────────────────────────────────

    {
        "nombre": "Julian Rotter — Locus de Control",
        "categoria": "marco_teorico",
        "autor_ref": "Julian Rotter",
        "chunks": [
            """Julian B. Rotter (1916-2014) fue un psicólogo estadounidense cuya contribución más conocida es el concepto de Locus de Control, desarrollado en la década de 1950 en el marco de la psicología social del aprendizaje.

El Locus de Control describe el grado en que una persona percibe que los eventos de su vida son el resultado de sus propias acciones (Locus Interno) o de factores externos como el destino, la suerte o el poder de otros (Locus Externo).

Las personas con Locus Interno tienden a percibirse como agentes de su propia vida: creen que pueden influir en sus circunstancias a través de sus decisiones y acciones. Las personas con Locus Externo tienden a percibirse como víctimas o receptores de fuerzas externas que no pueden controlar.""",

            """El Locus de Control no es un rasgo fijo: puede cambiar con la experiencia, el desarrollo personal y el trabajo terapéutico. Cultivar el Locus Interno es uno de los objetivos centrales del camino endonauta.

Sin embargo, el camino endonauta matiza esta idea: no se trata de un Locus Interno egóico (la ilusión de que el ego controla todo), sino de un Locus Interno consciente: reconocer que aunque no podemos controlar todo lo que ocurre, sí podemos elegir cómo respondemos a lo que ocurre. Esta es la distinción entre responsabilidad (la capacidad de elegir la respuesta) y control (la ilusión de dominar los eventos).

Viktor Frankl, desde su experiencia en los campos de concentración, llegó a una conclusión similar: entre el estímulo y la respuesta existe un espacio, y en ese espacio reside nuestra libertad. El Locus Interno endonauta vive en ese espacio.""",
        ],
    },

    # ──────────────────────────────────────────────────────────────────
    # ECKHART TOLLE
    # ──────────────────────────────────────────────────────────────────

    {
        "nombre": "Eckhart Tolle — El Poder del Ahora y la Presencia",
        "categoria": "marco_teorico",
        "autor_ref": "Eckhart Tolle",
        "chunks": [
            """Eckhart Tolle (1948) es un maestro espiritual alemán radicado en Canadá, autor de "El Poder del Ahora" y "Una Nueva Tierra". Su enseñanza central es la diferencia entre el Ser (la conciencia pura, la presencia, el ahora) y el ego (la mente identificada con el pensamiento y el tiempo).

Tolle propone que la mayor parte del sufrimiento humano proviene de la identificación con la mente pensante —con el flujo constante de pensamientos, juicios, memorias y proyecciones que el ego genera— y de vivir en el pasado (remordimiento, culpa, resentimiento) o en el futuro (ansiedad, preocupación, expectativa), perdiendo el único momento que realmente existe: el presente.

La presencia —la conciencia despierta que observa el flujo de la mente sin identificarse con él— es lo que Tolle llama el Poder del Ahora. Esta conciencia no es el ego ni la mente: es el espacio dentro del cual los pensamientos y emociones ocurren.""",

            """El "cuerpo del dolor" (pain-body) es otro concepto central de Tolle: un campo de energía emocional acumulada de experiencias pasadas no procesadas que vive en el cuerpo y que periódicamente se activa, secuestrando la conciencia y generando reacciones automáticas y sufrimiento.

El cuerpo del dolor es lo que en la terminología endonauta corresponde a la sombra y a las heridas de infancia: el material emocional no integrado que busca su reconocimiento y liberación. Tolle propone que la práctica de la presencia —simplemente observar el cuerpo del dolor cuando se activa, sin identificarse con él y sin suprimirlo— permite que se libere progresivamente.

Esta práctica conecta con el trabajo del Observador de Grinberg: la conciencia que puede presenciar el propio sufrimiento sin ser absorbida por él es la clave de la liberación.""",

            """La inteligencia universal o inteligencia de la Presencia es la dimensión de la conciencia que está más allá de la mente pensante individual. Tolle propone que cuando el ego se silencia y la conciencia está verdaderamente presente, puede fluir a través del individuo una inteligencia mayor que la del intelecto ordinario.

Esta idea conecta con la Teoría Sintérgica de Grinberg (el Lattice como campo de inteligencia universal), con el inconsciente colectivo de Jung, y con la visión de unidad del pensamiento endonauta. No somos islas de conciencia aisladas: cuando el ego deja de dominar, accedemos a una inteligencia compartida.

Para el endonauta, la práctica de la presencia no es solo meditación formal. Es la calidad de atención que se trae a cada momento: comer presente, escuchar presente, sentir el cuerpo presente. Es el antídoto al piloto automático del ego.""",
        ],
    },

    # ──────────────────────────────────────────────────────────────────
    # TERENCE MCKENNA
    # ──────────────────────────────────────────────────────────────────

    {
        "nombre": "Terence McKenna — Conciencia, Cultura y el Inconsciente Colectivo",
        "categoria": "marco_teorico",
        "autor_ref": "Terence McKenna",
        "chunks": [
            """Terence McKenna (1946-2000) fue un etnobotánico, filósofo y escritor estadounidense, uno de los pensadores más originales y provocadores del siglo XX. Estudió las plantas psicoactivas, los estados alterados de conciencia y la naturaleza del lenguaje y la realidad.

Una de sus afirmaciones más resonantes para el camino endonauta: "La atrofia espiritual de la cultura contemporánea puede deberse en gran medida a su pérdida de sensibilidad a los procesos del inconsciente colectivo." Esta idea sugiere que la crisis espiritual de la modernidad no es falta de información sino pérdida de contacto con dimensiones más profundas de la conciencia que la cultura racional ha marginado.

McKenna también propuso: "Estamos aprisionados en algún tipo de obra de arte" —refiriéndose a la manera en que la cultura, el lenguaje y el consenso social crean una realidad aparentemente objetiva que en realidad es una construcción colectiva.""",

            """McKenna exploró con profundidad el papel de los psilocibios (hongos mágicos) y otras plantas maestras en el desarrollo de la conciencia humana. Propuso —controversialmente pero con argumentos sofisticados— que el contacto de los primates humanos con psilocibios fue un factor determinante en el desarrollo del lenguaje y la conciencia reflexiva.

Su visión sobre los estados alterados de conciencia como puertas de acceso al inconsciente colectivo, a dimensiones de la realidad no ordinarias, y a formas de inteligencia que la mente racional ordinaria no puede alcanzar, conecta directamente con el chamanismo tolteca de Castaneda y con la tradición endonauta.

McKenna también observó: "El movimiento de un solo átomo desde una posición conocida a otra posición conocida cambia una experiencia de nada a abrumadora. Esto significa que la mente y la materia en el nivel de la mecánica cuántica están hiladas juntas." Esta observación conecta la experiencia subjetiva con la física moderna.""",
        ],
    },

    # ──────────────────────────────────────────────────────────────────
    # NIKOLA TESLA
    # ──────────────────────────────────────────────────────────────────

    {
        "nombre": "Nikola Tesla — Energía, Frecuencia y Vibración",
        "categoria": "marco_teorico",
        "autor_ref": "Nikola Tesla",
        "chunks": [
            """Nikola Tesla (1856-1943) fue un inventor, físico e ingeniero serbio-estadounidense, uno de los científicos más brillantes y enigmáticos de la historia. Su frase más citada en el contexto espiritual: "Si quieres encontrar los secretos del universo, piensa en términos de energía, frecuencia y vibración."

Aunque Tesla trabajó principalmente en ingeniería eléctrica, su visión del universo como un campo de energía y vibración anticipó muchas ideas de la física cuántica moderna y conecta con tradiciones espirituales milenarias. La idea de que todo lo que existe es energía en diferentes estados de vibración es tanto un principio científico moderno como un principio espiritual universal.

En el marco endonauta, esta perspectiva tiene implicaciones prácticas: si todo es energía y vibración, entonces los estados emocionales, los pensamientos y las creencias no son solo fenómenos subjetivos sino estados de vibración que interactúan con el campo de energía que nos rodea.""",

            """La ley de la vibración —uno de los principios filosóficos del endonauta— propone que cada estado de conciencia, cada emoción y cada pensamiento tiene una frecuencia específica. Los estados de amor, gratitud y paz vibran a frecuencias elevadas. Los estados de miedo, resentimiento y desesperación vibran a frecuencias bajas.

Esta perspectiva conecta con el Mapa de la Conciencia de David Hawkins, con el trabajo de Emoto sobre cómo los pensamientos y emociones afectan la estructura del agua, y con la física cuántica en su comprensión del observador como participante activo en la realidad observada.

Para el endonauta, "elevar la vibración" no es una fórmula mágica sino un trabajo concreto: cultivar estados emocionales más elevados, limpiar las creencias limitantes, sanar las heridas, desarrollar el observador y practicar la presencia. Todo esto modifica la frecuencia habitual desde la que se percibe y se vive.""",
        ],
    },

    # ──────────────────────────────────────────────────────────────────
    # MIKAO USUI
    # ──────────────────────────────────────────────────────────────────

    {
        "nombre": "Mikao Usui — Reiki y la Energía de Sanación",
        "categoria": "marco_teorico",
        "autor_ref": "Mikao Usui",
        "chunks": [
            """Mikao Usui (1865-1926) fue un maestro espiritual japonés y fundador del sistema de sanación energética conocido como Reiki. La palabra "Reiki" se compone de "Rei" (espíritu universal, inteligencia divina) y "Ki" (energía vital, equivalente al Chi chino o al Prana indio).

El Reiki propone que existe una energía vital universal que fluye a través de todos los seres vivos. Cuando esta energía fluye libremente, hay salud y bienestar. Cuando se bloquea —por estrés, trauma, creencias limitantes, emociones no procesadas— emergen los desequilibrios físicos, emocionales y espirituales.

Los 5 principios del Reiki de Usui son una guía ética y práctica: "Solo por hoy, no te enojes. Solo por hoy, no te preocupes. Sé agradecido. Trabaja con diligencia. Sé amable con los demás." Estos principios invitan a una práctica de presencia y conciencia en lo cotidiano.""",

            """El Reiki se integra en el contexto endonauta como una práctica de trabajo con el cuerpo energético —los chakras y los cuerpos sutiles— que complementa el trabajo psicológico y espiritual. El cuerpo energético registra las experiencias emocionales, las heridas de infancia y los patrones inconscientes, y el trabajo energético puede acceder a estos registros por vías que el trabajo puramente verbal no alcanza.

Desde la perspectiva de la Teoría Sintérgica de Grinberg, el Reiki podría interpretarse como una forma de trabajar directamente con el campo de energía (Lattice) que subyace a la experiencia física y psicológica. La intención sanadora del practicante, al operar desde un estado de conciencia elevada, puede modificar el campo energético del receptor.

Para el endonauta, el Reiki es una de las herramientas del trabajo con el cuerpo: junto al Ayurveda, la Medicina Tradicional China, el sueño lúcido y las prácticas somáticas, forma parte del repertorio de acceso al mundo interior a través del cuerpo.""",
        ],
    },

    # ──────────────────────────────────────────────────────────────────
    # KEN WILBER
    # ──────────────────────────────────────────────────────────────────

    {
        "nombre": "Ken Wilber — Psicología Integral y Niveles de Conciencia",
        "categoria": "marco_teorico",
        "autor_ref": "Ken Wilber",
        "chunks": [
            """Ken Wilber (1949) es un filósofo estadounidense y creador de la Teoría Integral, un ambicioso intento de integrar en un único marco coherente los conocimientos de la ciencia, la psicología, la filosofía y las tradiciones espirituales de Oriente y Occidente.

Su modelo AQAL (All Quadrants, All Levels —Todos los Cuadrantes, Todos los Niveles) propone que toda visión del mundo que sea verdadera y completa debe incluir cuatro perspectivas básicas: el interior individual (subjetivo: pensamientos, emociones, experiencias), el exterior individual (objetivo: cerebro, comportamiento, biología), el interior colectivo (intersubjetivo: cultura, valores compartidos, lenguaje), y el exterior colectivo (interoobjetivo: sistemas sociales, estructuras institucionales).

Wilber argumenta que gran parte de los conflictos filosóficos y espirituales se deben a que diferentes sistemas enfatizan solo uno o dos de estos cuadrantes, descuidando los demás.""",

            """Para Grinberg (que cita a Wilber en Endonautica), los límites que establecemos en nuestra identidad dependen de nuestro nivel de conciencia. En los niveles más básicos, nos identificamos solo con el ego y el cuerpo físico. En niveles más altos, nos identificamos con el organismo completo, luego con la mente, luego con el campo total de la experiencia.

Esta progresión en la identidad corresponde a la individuación de Jung, al desarrollo de la conciencia de Hawkins y a la Spiral Dynamics de Graves: el crecimiento de la conciencia es un proceso de ampliación progresiva de los límites de la identidad, desde el ego aislado hasta la identidad con la totalidad.

Wilber también propone los "estados" de conciencia (que cualquiera puede experimentar temporalmente: sueño, meditación, éxtasis) vs. los "estadios" de conciencia (estructuras de desarrollo que se estabilizan con el tiempo). Esta distinción es útil para el endonauta: una experiencia de unidad o apertura en la meditación no implica automáticamente que se ha "alcanzado" un nivel de desarrollo superior.""",
        ],
    },

    # ──────────────────────────────────────────────────────────────────
    # ANNGWYN ST. JUST
    # ──────────────────────────────────────────────────────────────────

    {
        "nombre": "Anngwyn St. Just — Trauma Social y Patrones Fractales",
        "categoria": "marco_teorico",
        "autor_ref": "Anngwyn St. Just",
        "chunks": [
            """Anngwyn St. Just es una reconocida psicóloga transpersonal y experta en trauma social. Su trabajo se centra en la comprensión de cómo los eventos traumáticos afectan no solo a los individuos sino también a las comunidades y a la sociedad en su conjunto, generando patrones inconscientes que se repiten a través del tiempo.

St. Just aplica el concepto de fractales al trauma social: los patrones de trauma tienden a repetirse en diferentes escalas —desde el individuo hasta la familia, la comunidad y la sociedad— y a través del tiempo, reactivándose en fechas o contextos que inconcientemente recuerdan el trauma original.

Esta perspectiva conecta con la transmisión transgeneracional de las heridas: los traumas no procesados de las generaciones anteriores se transmiten —a través de patrones de comportamiento, emociones, creencias y respuestas somáticas— a las generaciones siguientes.""",

            """El trauma social de St. Just complementa el trabajo de las heridas individuales de Bourbeau y el trabajo de la sombra de Jung: no solo cargamos heridas personales sino también heridas colectivas de nuestra familia, nuestra cultura y nuestra historia.

Para el endonauta, reconocer la dimensión social y transgeneracional del propio sufrimiento permite ubicar el dolor en un contexto más amplio: "Este dolor no es solo mío. Es el dolor de mi familia, de mi cultura, de mi historia. Al tomarlo conscientemente, puedo comenzar a sanarlo no solo en mí sino en el linaje."

St. Just enfatiza que sanar el trauma social requiere tanto empatía y compasión colectiva como la capacidad de los individuos de asumir responsabilidad personal y actuar para cambiar las circunstancias en lugar de perpetuar los patrones.""",
        ],
    },

    # ──────────────────────────────────────────────────────────────────
    # MAURICIO BEUCHOT
    # ──────────────────────────────────────────────────────────────────

    {
        "nombre": "Mauricio Beuchot — Filosofía del Implícito",
        "categoria": "marco_teorico",
        "autor_ref": "Mauricio Beuchot",
        "chunks": [
            """Mauricio Beuchot (1950) es un filósofo mexicano, especialista en hermenéutica y semiótica. Su "filosofía del implícito" propone que el mundo está compuesto de lo explícito (lo que es visible, evidente, articulado) y lo implícito (lo que subyace, lo que se puede inferir pero no se ve directamente, lo que existe en un nivel pre-verbal o pre-consciente).

La filosofía del implícito sostiene que el conocimiento humano no se construye solo a partir de lo explícito y observable: gran parte de lo que sabemos, sentimos y somos existe en un nivel implícito que el lenguaje puede comenzar a articular pero que nunca captura completamente.

Esta perspectiva resuena profundamente con el focusing de Gendlin (el felt sense como conocimiento implícito del cuerpo), con el inconsciente de Freud y Jung, y con la Teoría Sintérgica de Grinberg (el Lattice como campo de información que el cerebro decodifica).""",

            """Para el endonauta y para el Mirror, la filosofía del implícito tiene implicaciones concretas: la comunicación no ocurre solo en las palabras sino también en el tono, la emoción, el gesto, el ritmo, lo que no se dice. Escuchar el nivel implícito de la comunicación —el "lenguaje entre las palabras"— es una habilidad central del autoconocimiento y de la presencia en las relaciones.

Beuchot también propone que los síntomas, las enfermedades, los conflictos relacionales y los sueños son formas de comunicación del nivel implícito: la psique comunica lo que no puede decir directamente a través de representaciones simbólicas, corporales y relacionales.

La pregunta del Mirror que emerge de esta filosofía es: ¿qué está comunicando esta situación en el nivel que todavía no tiene palabras? ¿Qué está "diciendo" el cuerpo, la emoción, el patrón que se repite?""",
        ],
    },

    # ──────────────────────────────────────────────────────────────────
    # LAO TSE / TAOISMO
    # ──────────────────────────────────────────────────────────────────

    {
        "nombre": "Lao Tse — Taoísmo, Yin/Yang y el Fluir",
        "categoria": "marco_teorico",
        "autor_ref": "Lao Tse",
        "chunks": [
            """Lao Tse (siglo VI a.C.) fue el legendario sabio chino al que se atribuye la composición del Tao Te Ching, el texto fundador del Taoísmo. Su nombre significa "el anciano maestro" y su enseñanza central es la del Tao: el camino, el principio ordenador del universo, la realidad inefable que subyace a toda existencia.

La frase citada en Endonautica: "La vida y la muerte son un hilo, la misma línea vista desde diferentes lados" sintetiza la perspectiva taoísta de la dualidad: los opuestos no se excluyen sino que se complementan, se definen mutuamente y se transforman el uno en el otro en un movimiento perpetuo.

El principio del Yin y el Yang —los dos polos complementarios de toda realidad— no es solo una categoría filosófica: es una herramienta de comprensión de la propia experiencia. Todo estado tiene su opuesto, todo momento su complemento. La oscuridad contiene la semilla de la luz; el caos contiene la semilla del orden.""",

            """El Wu Wei (no-acción, o acción sin fuerza) es uno de los conceptos centrales del Taoísmo: la idea de que la acción más poderosa es la que fluye con la naturaleza de las cosas, sin forzar, sin resistir, sin intentar controlar. El agua es la metáfora favorita de Lao Tse: suave pero capaz de horadar la roca más dura.

Para el endonauta, el Wu Wei no significa pasividad: significa acción desde la sabiduría del fluir en lugar de la acción desde el miedo o el control. Es la diferencia entre empujar contra la corriente y encontrar el camino del flujo natural.

Esta perspectiva conecta con el concepto Gestalt de la acción organísmica que emerge naturalmente cuando hay suficiente presencia, y con la enseñanza de Perls de dejar que el plan surja desde adentro en lugar de imponerlo desde el ego.""",
        ],
    },

    # ──────────────────────────────────────────────────────────────────
    # CARL ROGERS
    # ──────────────────────────────────────────────────────────────────

    {
        "nombre": "Carl Rogers — Terapia Centrada en el Cliente",
        "categoria": "marco_teorico",
        "autor_ref": "Carl Rogers",
        "chunks": [
            """Carl Rogers (1902-1987) fue uno de los psicólogos más influyentes del siglo XX, fundador de la Terapia Centrada en el Cliente (Person-Centered Therapy) y figura central de la psicología humanista. Su trabajo transformó la comprensión del proceso terapéutico y de las condiciones necesarias para el cambio.

Rogers propuso que el ser humano tiene una tendencia actualizante natural: una inclinación innata hacia el crecimiento, la salud y el despliegue de sus potenciales. El problema no es la falta de capacidad de crecimiento sino las condiciones externas (y la voz interna que las ha internalizado) que bloquean ese proceso natural.

Las tres condiciones que Rogers identificó como necesarias y suficientes para el cambio terapéutico son: la autenticidad del terapeuta (congruencia: ser genuino en lugar de jugar un rol), la aceptación positiva incondicional (recibir al cliente sin condiciones ni juicios), y la empatía (comprender el mundo del cliente desde la perspectiva del cliente mismo).""",

            """La aceptación positiva incondicional es probablemente el concepto más revolucionario de Rogers: la idea de que la presencia de un otro que te acepta sin condiciones —sin juzgarte, sin necesitar que cambies para merecer su respeto— tiene en sí mismo un poder transformador.

Esta condición es opuesta a la "domesticación" de Miguel Ruiz: si la domesticación condiciona el amor a la conformidad con las expectativas, la aceptación positiva incondicional ofrece un amor que no depende del comportamiento. En esa experiencia, la persona puede comenzar a verse a sí misma con los mismos ojos, generando la condición para el cambio genuino.

El Mirror Endonauta aspira a esta cualidad de presencia: no juzgar, no prescribir, no etiquetar. Acompañar al usuario en su exploración desde un espacio de aceptación radical que permite ver sin distorsión.""",
        ],
    },

    # ──────────────────────────────────────────────────────────────────
    # ALBERT HOFMANN
    # ──────────────────────────────────────────────────────────────────

    {
        "nombre": "Albert Hofmann — Mundo Interior, Mundo Exterior",
        "categoria": "marco_teorico",
        "autor_ref": "Albert Hofmann",
        "chunks": [
            """Albert Hofmann (1906-2008) fue un químico suizo conocido principalmente por ser el primer ser humano en sintetizar y experimentar los efectos del LSD (1943). Fue también el primero en aislar la psilocibina de los hongos sagrados. Vivió 102 años y en su vejez se convirtió en un pensador profundo sobre la naturaleza de la conciencia.

Su libro más filosófico, "LSD: Mi hijo problema" (y en colaboración "Las Plantas de los Dioses"), refleja una perspectiva que va más allá de la química: los estados alterados de conciencia producidos por sustancias psicoactivas revelan que la percepción ordinaria del mundo es solo una de las muchas formas posibles de experiencia, no la única ni necesariamente la más verdadera.

Su concepto de "mundo interior, mundo exterior" —citado en Endonautica— propone que la realidad tiene dos dimensiones que se corresponden: el mundo interno de la experiencia subjetiva y el mundo externo de la realidad física. Ambos son reales, ambos son necesarios, y existe una relación de correspondencia y espejeo entre ellos.""",

            """Hofmann fue un defensor de una relación reverente y cuidadosa con las plantas psicoactivas como herramientas de exploración de la conciencia —no como sustancias recreativas sino como "enteógenos" (generadores de lo divino interior). Su perspectiva es consistente con la tradición chamánica y con el trabajo de McKenna.

Para el endonauta, la contribución de Hofmann es el reconocimiento de que la conciencia ordinaria es solo una ventana estrecha sobre una realidad mucho más vasta. Las experiencias de expansión de la conciencia —ya sea a través de plantas maestras, meditación profunda, sueño lúcido o crisis existenciales— revelan dimensiones de la realidad que la mente racional ordinaria no puede capturar.

Esta perspectiva invita a la humildad epistemológica: no dar por sentado que lo que percibimos es toda la realidad, y mantener una apertura hacia las dimensiones más profundas del ser.""",
        ],
    },

    # ──────────────────────────────────────────────────────────────────
    # FILÓSOFOS OCCIDENTALES
    # ──────────────────────────────────────────────────────────────────

    {
        "nombre": "Platón, Aristóteles, Descartes — Dualidad Cuerpo-Mente en Occidente",
        "categoria": "marco_teorico",
        "autor_ref": "Platón / Aristóteles / Descartes",
        "chunks": [
            """La pregunta sobre la relación entre el cuerpo y la mente es tan antigua como la filosofía occidental. Los tres filósofos que más han marcado la respuesta occidental son Platón, Aristóteles y Descartes, y sus respuestas divergentes siguen siendo relevantes para el autoconocimiento contemporáneo.

PLATÓN (428-348 a.C.) propuso una visión dualista radical: el cuerpo es la prisión del alma. El alma (la parte divina e inmortal) existe antes de nacer y continúa después de morir; el cuerpo es una cárcel temporal que dificulta el acceso a la verdad y al conocimiento. El filósofo platónico busca liberarse del cuerpo a través del pensamiento y la contemplación.

ARISTÓTELES (384-322 a.C.) propuso una visión más integrada: el alma no es una entidad separada que habita el cuerpo sino la forma del cuerpo, su principio organizador. Cuerpo y alma están íntimamente relacionados: no puede haber experiencia sin cuerpo. Esta visión es mucho más cercana al enfoque somático del pensamiento endonauta.

DESCARTES (1596-1650) volvió al dualismo con su famosa distinción entre la res cogitans (la mente, la sustancia pensante) y la res extensa (el cuerpo, la sustancia extensa). Esta separación cartesiana —"Pienso, luego existo"— ha sido enormemente influyente en la ciencia y la cultura occidentales, generando una civilización que privilegia el pensamiento racional sobre el cuerpo y la experiencia.""",

            """La herencia cartesiana pesa sobre la cultura contemporánea: somos una sociedad que "vive en la cabeza", que prioriza el análisis racional sobre la sabiduría corporal, que desconfía de la experiencia subjetiva como fuente de conocimiento válido.

El camino endonauta es, en muchos sentidos, una corrección de este desequilibrio: recuperar la sabiduría del cuerpo (Gendlin, Ayurveda, MTC), integrar la dimensión espiritual y energética (Grinberg, Castaneda, Reiki), y reconocer que el pensamiento racional es un instrumento valioso pero limitado para la comprensión de la totalidad de la experiencia humana.

La paradoja es que Descartes inició su búsqueda filosófica desde la duda radical —cuestionando todo lo que daba por supuesto— lo cual es en sí mismo un gesto profundamente endonauta: no asumir que lo que nos han enseñado a pensar es necesariamente verdad.""",
        ],
    },

    {
        "nombre": "Husserl y Heidegger — Fenomenología del Yo",
        "categoria": "marco_teorico",
        "autor_ref": "Husserl / Heidegger",
        "chunks": [
            """Edmund Husserl (1859-1938) fue el fundador de la fenomenología —el estudio de la experiencia tal como se presenta a la conciencia, antes de cualquier interpretación teórica. Su método propone poner en "paréntesis" (epoché) todos los supuestos sobre la realidad exterior para observar con precisión cómo la experiencia se construye en la conciencia.

Para Husserl, el yo (ego) no es una sustancia estática sino un polo de intencionalidad: la conciencia siempre está orientada hacia algo —siempre es "conciencia de". Esta perspectiva convierte al yo en un observador activo de su propia experiencia, no en un receptor pasivo de impresiones.

La fenomenología es el método científico más coherente con el camino endonauta: estudiar la experiencia desde adentro, con rigor y sin supuestos previos. Es la base epistemológica del trabajo del Observador.""",

            """Martin Heidegger (1889-1976) fue discípulo de Husserl y uno de los filósofos más influyentes y complejos del siglo XX. Su obra central, "Ser y Tiempo" (1927), propone que la pregunta fundamental de la filosofía no es "¿qué existe?" sino "¿qué significa ser?".

Para Heidegger, el ser humano es un "Dasein" —ser-ahí, ser-en-el-mundo. No somos conciencias encerradas en cuerpos que observan un mundo externo: somos siempre ya en relación con el mundo, con otros, con el tiempo. La autenticidad —el vivir desde el propio ser más genuino en lugar de desde las expectativas del "se" (das Man, el uno impersonal)— es el imperativo ético central de Heidegger.

Esta distinción entre autenticidad e inautenticidad resuena profundamente con el camino endonauta: la domesticación de Miguel Ruiz, el Locus Externo de Rotter, el ego de Tolle son formas de inautenticidad. El trabajo de autoconocimiento es un retorno a la autenticidad.""",
        ],
    },

    {
        "nombre": "Kant — El Yo y los Límites del Conocimiento",
        "categoria": "marco_teorico",
        "autor_ref": "Immanuel Kant",
        "chunks": [
            """Immanuel Kant (1724-1804) fue el filósofo alemán que realizó lo que él mismo llamó "la revolución copernicana en la filosofía": en lugar de asumir que el conocimiento se adecúa al objeto (la mente recibe pasivamente lo que el mundo le da), propuso que el objeto se adecúa al conocimiento (la mente estructura activamente la experiencia).

Según Kant, el yo no puede conocerse a sí mismo como es en sí —el "yo noumonal" es incognoscible. Lo que conocemos de nosotros mismos es siempre ya mediado por las formas a priori de la intuición (espacio y tiempo) y las categorías del entendimiento. Esta limitación epistemológica es, paradójicamente, una invitación a la humildad: nunca vemos la realidad tal como es, siempre la vemos a través de los filtros de nuestra conciencia.

Para el endonauta, Kant aporta una perspectiva de humildad epistemológica: lo que percibimos como "realidad objetiva" es siempre una construcción de nuestra conciencia. Esto no niega la realidad sino que ubica al observador como participante activo en la construcción de su experiencia —que es exactamente la premisa de la ley espejo.""",
        ],
    },

    # ──────────────────────────────────────────────────────────────────
    # BF SKINNER
    # ──────────────────────────────────────────────────────────────────

    {
        "nombre": "B.F. Skinner — Conductismo y sus Límites",
        "categoria": "marco_teorico",
        "autor_ref": "B.F. Skinner",
        "chunks": [
            """Burrhus Frederic Skinner (1904-1990) fue el psicólogo americano más influyente del siglo XX y el principal representante del conductismo radical. Propuso que toda conducta humana puede explicarse como el resultado de condicionamientos —asociaciones entre estímulos y respuestas— sin necesidad de postular entidades internas como la mente, los sentimientos o la conciencia.

Para Skinner, la mente es simplemente una función del cerebro condicionado por el entorno: no hay un yo interno que elija, solo patrones de comportamiento reforzados o extinguidos por las consecuencias. Esta visión eliminatoria de la experiencia subjetiva contrasta radicalmente con el enfoque endonauta.

Sin embargo, la comprensión de los principios conductistas tiene valor práctico para el autoconocimiento: los patrones de comportamiento son en gran medida aprendidos y pueden desaprenderse. Los hábitos, las reacciones automáticas y los ciclos repetitivos siguen lógicas de condicionamiento que pueden identificarse y modificarse.""",

            """El valor del conductismo para el camino endonauta no está en su metafísica (la negación de la conciencia) sino en sus herramientas: la comprensión de cómo se forman y se modifican los hábitos, la importancia del refuerzo positivo en el cambio de comportamiento, y la distinción entre comportamientos respondientes (reflejos automáticos) y operantes (conductas voluntarias moldeadas por sus consecuencias).

El conflicto entre el conductismo y la psicología profunda refleja una tensión más amplia en la comprensión del ser humano: ¿somos fundamentalmente máquinas condicionadas o seres con conciencia y libre albedrío? El camino endonauta propone que somos ambas cosas: somos organismos condicionados que pueden desarrollar conciencia, y esa conciencia puede gradualmente liberar del automatismo del condicionamiento.""",
        ],
    },

    # ──────────────────────────────────────────────────────────────────
    # MARCOS SISTÉMICOS
    # ──────────────────────────────────────────────────────────────────

    {
        "nombre": "Eneagrama — Los 9 Tipos de Personalidad",
        "categoria": "tradicion",
        "autor_ref": "Claudio Naranjo / Oscar Ichazo",
        "chunks": [
            """El Eneagrama es un sistema de comprensión de la personalidad que describe 9 tipos o estructuras del ego, cada uno con motivaciones, miedos, fortalezas y patrones automáticos específicos. Sus raíces son diversas: se transmitió en Occidente a través de George Gurdjieff y fue sistematizado como tipología psicológica por Óscar Ichazo y, crucialmente, por el psiquiatra chileno Claudio Naranjo.

El Eneagrama no es solo tipología: es una herramienta de transformación. Cada tipo de personalidad corresponde a una "pasión" (el patrón emocional central que genera sufrimiento) y a una "virtud" (la cualidad que florece cuando ese patrón se trasciende). El trabajo eneagramático no es solo identificar el propio tipo sino comprender la dinámica interna que lo sostiene.

Los 9 tipos en síntesis: 1-Perfeccionista (ira/serenidad), 2-Servicial (orgullo/humildad), 3-Triunfador (vanidad/autenticidad), 4-Romántico (envidia/ecuanimidad), 5-Observador (avaricia/desapego), 6-Leal (miedo/coraje), 7-Entusiasta (gula/sobriedad), 8-Desafiador (lujuria/inocencia), 9-Mediador (pereza/acción).""",

            """Cada tipo del Eneagrama tiene alas (los tipos adyacentes que influyen), instintos (autoconservación, sexual, social —que modulan la expresión del tipo), y niveles de salud (el mismo tipo puede expresarse desde la disfunción hasta la integración, según el nivel de consciencia y trabajo personal).

Para el trabajo con el Mirror Endonauta, el Eneagrama ofrece un vocabulario preciso para identificar patrones: si se activa el tipo 2 (servicial), la pregunta puede ser "¿estás ayudando desde la abundancia o desde la necesidad de ser necesitado?". Si el tipo 4 (romántico), "¿estás viviendo el dolor de la situación actual o dolor de situaciones pasadas proyectado aquí?". Si el tipo 6 (leal), "¿qué dice tu mente sobre el peor escenario posible, y qué dice tu cuerpo sobre lo que realmente está ocurriendo?"

El Eneagrama más que etiquetar, ilumina: permite ver el propio condicionamiento automático con suficiente distancia como para no estar completamente atrapado en él.""",
        ],
    },

    {
        "nombre": "MBTI / Myers-Briggs — Tipos Psicológicos",
        "categoria": "tradicion",
        "autor_ref": "Isabel Briggs Myers / Katharine Cook Briggs",
        "chunks": [
            """El MBTI (Myers-Briggs Type Indicator) es un instrumento de tipología de personalidad basado en las teorías de tipos psicológicos de Carl Gustav Jung. Fue desarrollado por Isabel Briggs Myers y su madre Katharine Cook Briggs durante la Segunda Guerra Mundial y hoy es uno de los test de personalidad más ampliamente utilizados en el mundo.

El MBTI clasifica la personalidad en 4 dicotomías: Extraversión/Introversión (E/I: orientación de la energía hacia el exterior o el interior), Sensación/Intuición (S/N: preferencia por la información concreta y sensorial o por patrones y posibilidades), Pensamiento/Sentimiento (T/F: base de la toma de decisiones: lógica o valores), Juicio/Percepción (J/P: orientación hacia la estructura y los planes o hacia la flexibilidad y la apertura).

Las combinaciones de estas 4 dicotomías producen 16 tipos, cada uno con características y fortalezas específicas.""",

            """Limitaciones importantes del MBTI: los estudios de fiabilidad muestran que una parte significativa de las personas obtiene resultados diferentes al repetir el test semanas después. La teoría de los "tipos" fijos ha sido criticada por ser demasiado rígida y no capturar la fluidez de la personalidad real.

Sin embargo, como herramienta de autoconocimiento orientativa —no diagnóstica—, el MBTI tiene valor: ofrece vocabulario para reflexionar sobre las propias preferencias cognitivas y relacionales, facilita la comprensión de por qué ciertos estilos de comunicación o trabajo se ajustan mejor que otros, y puede abrir conversaciones sobre las diferencias individuales.

En MirrorWork, el MBTI se usa como herramienta de reflexión (instrumento adapted, no clínico). Los resultados se presentan como tendencias, no como etiquetas definitivas.""",
        ],
    },

    {
        "nombre": "Big Five — Los Cinco Grandes Factores de Personalidad",
        "categoria": "tradicion",
        "autor_ref": "Paul Costa / Robert McCrae",
        "chunks": [
            """El modelo de los Cinco Grandes (Big Five o OCEAN) es el marco de personalidad más respaldado por la investigación científica en psicología. Propone que la personalidad puede describirse en cinco dimensiones amplias: Apertura a la experiencia (O: curiosidad intelectual, creatividad, apertura a nuevas ideas), Conciencia (C: organización, responsabilidad, autodisciplina), Extraversión (E: sociabilidad, asertividad, energía en contextos sociales), Amabilidad (A: cooperación, empatía, orientación prosocial), Neuroticismo (N: tendencia a experimentar emociones negativas, reactividad emocional).

A diferencia del MBTI (que clasifica en tipos), el Big Five sitúa a cada persona en un continuo en cada dimensión. Esto es más consistente con la evidencia empírica sobre la naturaleza de la personalidad.

El Big Five tiene sólida validez transcultural: los cinco factores emergen consistentemente en estudios realizados en diferentes culturas y países.""",

            """Para el autoconocimiento endonauta, el Big Five ofrece un perfil de las propias tendencias naturales. Un neuroticismo alto indica mayor reactividad emocional y vulnerabilidad al estrés —que puede trabajarse con las herramientas de autorregulación del camino endonauta. Una apertura alta indica curiosidad y creatividad —que es un recurso en el viaje interior. Una conciencia baja puede indicar dificultad para sostener prácticas regulares —que requiere estrategias específicas de hábito.

Los rasgos del Big Five son relativamente estables pero no inmutables. La experiencia, el trabajo personal y el desarrollo de la conciencia pueden modificar gradualmente el perfil, especialmente reduciendo el neuroticismo y aumentando la apertura y la amabilidad.

En MirrorWork, los resultados del Big Five se integran con la lectura endonauta para identificar qué rasgos son recursos en el camino y cuáles generan fricción.""",
        ],
    },

    {
        "nombre": "Análisis Transaccional — Padre, Adulto y Niño",
        "categoria": "tradicion",
        "autor_ref": "Eric Berne",
        "chunks": [
            """El Análisis Transaccional (AT) fue desarrollado por el psiquiatra Eric Berne (1910-1970) y popularizado a través de su libro "Los Juegos en que Participamos" (1964). Propone que la personalidad tiene tres estados del yo —Padre, Adulto y Niño— que determinan cómo nos comunicamos y relacionamos.

El PADRE es el estado del yo que contiene las actitudes, creencias y comportamientos aprendidos de las figuras parentales y de autoridad. Puede ser Padre Nutritivo (protector, cariñoso, guía) o Padre Crítico (juzgador, controlador, exigente). El NIÑO es el estado del yo que contiene las respuestas emocionales y patrones de comportamiento aprendidos en la infancia. Puede ser Niño Libre (espontáneo, creativo, auténtico), Niño Adaptado (complaciente, sumiso) o Niño Rebelde (desafiante). El ADULTO es el estado del yo que procesa la información del momento presente de manera racional y objetiva, sin contaminación del Padre o del Niño.""",

            """Las "transacciones" son los intercambios comunicacionales entre personas. El AT analiza si las transacciones son complementarias (el estado del yo que responde es el esperado), cruzadas (el estado del yo que responde es inesperado, generando conflicto) o ulteriores (hay un mensaje explícito y uno implícito que operan simultáneamente).

Los "juegos psicológicos" de Berne son secuencias repetitivas de transacciones con un final predecible que confirma una posición de vida limitante. El triángulo dramático (Víctima-Perseguidor-Rescatador) es el juego más conocido: tres roles que las personas adoptan y rotan en dinámica codependiente.

Para el endonauta, el AT ofrece un mapa claro de los patrones relacionales automáticos: ¿desde qué estado del yo estás hablando ahora? ¿Desde qué estado del yo estás respondiendo? ¿Qué juego psicológico se está desplegando? Reconocer el patrón es el primer paso para salir de él.""",
        ],
    },

    # ──────────────────────────────────────────────────────────────────
    # TRADICIONES
    # ──────────────────────────────────────────────────────────────────

    {
        "nombre": "Ayurveda — Medicina del Ser",
        "categoria": "tradicion",
        "autor_ref": "Tradición védica (India)",
        "chunks": [
            """El Ayurveda (del sánscrito: Ayur = vida, Veda = conocimiento) es el sistema de medicina tradicional de la India, con más de 5,000 años de historia. Es probablemente el sistema de medicina integral más antiguo y completo del mundo, y su relevancia contemporánea sigue creciendo.

El Ayurveda propone que toda persona nace con una constitución única (prakriti) determinada por la combinación de tres doshas o principios bioenergéticos: Vata (energía del movimiento, compuesto de aire y espacio), Pitta (energía del metabolismo y la transformación, compuesto de fuego y agua), y Kapha (energía de la estructura y la cohesión, compuesto de tierra y agua).

Conocer la propia constitución ayurvédica permite entender las tendencias naturales del cuerpo y la mente: el tipo Vata tiende a la creatividad, la movilidad y la variabilidad, pero también a la ansiedad y la dispersión. El tipo Pitta tiende al liderazgo, la claridad y la determinación, pero también a la irritabilidad y el perfeccionismo. El tipo Kapha tiende a la estabilidad, la lealtad y la paciencia, pero también a la inercia y el apego.""",

            """Los 7 dhatus son los tejidos del cuerpo en el Ayurveda: rasa (plasma), rakta (sangre), mamsa (músculo), meda (grasa), asthi (hueso), majja (médula y sistema nervioso) y shukra/artava (tejido reproductivo). La salud del cuerpo depende de que los doshas y los dhatus estén en equilibrio.

El Ayurveda también reconoce los tres gunas o cualidades de la mente y la conciencia: tamas (inercia, oscuridad, torpeza), rajas (actividad, pasión, agitación) y sattva (claridad, armonía, equilibrio). El trabajo espiritual desde la perspectiva ayurvédica consiste en cultivar el sattva —la cualidad de claridad y armonía— para facilitar el desarrollo de la conciencia.

Para el endonauta, el Ayurveda ofrece un mapa del cuerpo como ecosistema vivo en constante diálogo con el entorno. La dieta, el ritmo de vida, las relaciones, las prácticas de meditación y el sueño son todos factores que modulan el equilibrio de los doshas y, a través de ellos, el equilibrio mental y espiritual.""",
        ],
    },

    {
        "nombre": "Medicina Tradicional China — Qi, Yin/Yang y los 5 Elementos",
        "categoria": "tradicion",
        "autor_ref": "Tradición China",
        "chunks": [
            """La Medicina Tradicional China (MTC) es un sistema de medicina que ha evolucionado durante más de 3,000 años. Su comprensión del cuerpo humano es radicalmente diferente a la medicina occidental: en lugar de ver el cuerpo como una máquina compuesta de órganos y sistemas, la MTC lo ve como un campo de energía viva en constante relación con el entorno, el tiempo y el cosmos.

El Qi (también escrito Chi) es la energía vital fundamental que fluye a través de todos los seres vivos y del universo. En el cuerpo, el Qi circula a través de canales de energía llamados meridianos. Cuando el Qi fluye libremente, hay salud. Cuando se bloquea, estanca o desequilibra, emergen los desequilibrios físicos, emocionales y espirituales.

El Yin y el Yang son los dos principios complementarios y opuestos que ordenan toda la realidad: frío/calor, oscuridad/luz, femenino/masculino, pasivo/activo, receptivo/expansivo. La salud en la MTC es el equilibrio dinámico entre el Yin y el Yang.""",

            """El sistema de los 5 Elementos (Madera/Fuego/Tierra/Metal/Agua) es otro mapa fundamental de la MTC. Cada elemento corresponde a un par de órganos, una emoción, una estación, un color, un sabor y un aspecto de la personalidad.

Madera (Hígado/Vesícula Biliar): visión, planificación, flexibilidad; emoción: ira. Fuego (Corazón/Intestino Delgado): joy, amor, conexión; emoción: alegría/ansiedad. Tierra (Bazo/Estómago): nutrición, reflexión, centramiento; emoción: preocupación. Metal (Pulmón/Intestino Grueso): rendición, duelo, valor; emoción: tristeza. Agua (Riñón/Vejiga): voluntad, sabiduría, misterio; emoción: miedo.

Las enfermedades físicas tienen correlatos emocionales: un Hígado desequilibrado (Madera) puede manifestarse en ira reprimida y frustración. Un Corazón desequilibrado puede manifestarse en ansiedad y falta de alegría. Para el endonauta, este mapa conecta directamente el trabajo emocional con el trabajo corporal.""",
        ],
    },

    {
        "nombre": "Chamanismo — Tradición de Acceso a Otros Mundos",
        "categoria": "tradicion",
        "autor_ref": "Tradición chamánica (global)",
        "chunks": [
            """El chamanismo es probablemente la forma más antigua de práctica espiritual humana, con evidencias arqueológicas de más de 30,000 años. No es una religión sino una tecnología del espíritu: un conjunto de prácticas para acceder a estados alterados de conciencia con propósitos de sanación, conocimiento y conexión con el mundo espiritual.

El chamán es el especialista espiritual que puede viajar conscientemente entre mundos —el mundo ordinario y los mundos no ordinarios— para obtener información, recuperar energía vital perdida, y sanar. El chamanismo existe en prácticamente todas las culturas del mundo, con variaciones locales pero con estructuras fundamentales similares.

Las plantas maestras (ayahuasca, peyote, psilocibios, entre otros) son herramientas de algunos sistemas chamánicos para inducir estados de conciencia que facilitan el acceso a información y experiencias que no están disponibles en la conciencia ordinaria. La tradición tolteca de Castaneda, el trabajo de McKenna y la cosmovisión andina de la ayahuasca son expresiones distintas de esta tradición universal.""",

            """El concepto tolteca del punto de encaje (de Castaneda) es el equivalente chamánico al principio de que nuestra percepción de la realidad es una construcción condicionada: el punto de encaje determina qué bandas de frecuencia de la realidad percibimos. Moverlo —a través de plantas, meditación, sueño lúcido o trabajo chamánico— abre la percepción a otras dimensiones.

El trabajo con los sueños, central en el chamanismo, es una práctica de exploración del mundo interior que el endonauta puede integrar sin necesariamente entrar en tradiciones específicas. Los sueños son mensajes del inconsciente (Jung), del subconsciente (Freud), o de "otros mundos" (chamanismo): independientemente del marco teórico, el trabajo con los sueños abre dimensiones de autoconocimiento inaccesibles a la mente racional.

Para el endonauta, el chamanismo ofrece la perspectiva de que el ser humano es más que su cuerpo físico y su mente racional: hay dimensiones del ser que solo pueden conocerse a través de prácticas que expanden la conciencia más allá de sus límites ordinarios.""",
        ],
    },

    # ──────────────────────────────────────────────────────────────────
    # ENRIQUE MARÍN
    # ──────────────────────────────────────────────────────────────────

    {
        "nombre": "Enrique Marín — Meditación como Herramienta Endonauta",
        "categoria": "marco_teorico",
        "autor_ref": "Enrique Marín",
        "chunks": [
            """Enrique Marín es el autor del artículo citado en Endonautica: "Endonautas: la meditación como herramienta clave". Su trabajo destaca la meditación no como práctica religiosa o espiritual exclusiva sino como una tecnología de la conciencia: un entrenamiento sistemático de la atención que tiene efectos medibles en el bienestar, la regulación emocional y el desarrollo de la conciencia.

La meditación en el contexto endonauta es la práctica central del Observador: el entrenamiento de la capacidad de presenciar los propios estados internos —pensamientos, emociones, sensaciones— sin identificarse completamente con ellos. Es el espacio donde el ego aprende que no es el dueño de la conciencia sino un habitante de ella.

Las formas de meditación relevantes para el endonauta incluyen: mindfulness (atención plena al momento presente), meditación de compasión (metta, cultivo del amor incondicional), meditación trascendental, meditación en movimiento (yoga, tai chi, qigong), y exploración del sueño lúcido como práctica meditativa extendida al sueño.""",
        ],
    },

    # ──────────────────────────────────────────────────────────────────
    # BIODESCODIFICACIÓN
    # ──────────────────────────────────────────────────────────────────

    {
        "nombre": "Biodescodificación — El Cuerpo como Mensajero",
        "categoria": "marco_teorico",
        "autor_ref": "Christian Flèche / Enric Corbera",
        "chunks": [
            """La biodescodificación (también llamada biodecodificación o biodescodificación biológica) es un enfoque que propone que los síntomas físicos son mensajes del inconsciente biológico: expresiones somáticas de conflictos emocionales no resueltos. Sus principales sistematizadores son el terapeuta francés Christian Flèche ("Mi cuerpo para curarme") y el catalán Enric Corbera ("El observador en la consulta").

El principio central: cada órgano, sistema o región del cuerpo corresponde a un tipo de conflicto emocional específico. Cuando ese conflicto no se procesa en el plano psíquico, el cuerpo lo expresa mediante un síntoma físico. El síntoma no es un error del organismo sino una solución biológica de emergencia —la mejor respuesta posible del cuerpo ante una situación que la psique no pudo resolver.

Para el endonauta, este enfoque es especialmente relevante cuando emergen síntomas físicos en el relato del usuario. La pregunta guía no es "¿qué tiene?" sino "¿qué conflicto emocional lleva el cuerpo a ese órgano o sistema?".""",

            """CORRESPONDENCIAS PRINCIPALES POR ÓRGANO Y SISTEMA:

PIEL: límites del yo, identidad, contacto y separación. La piel es la frontera entre el yo y el mundo. Enfermedades de piel (eccema, psoriasis, dermatitis) suelen vincularse a conflictos de separación ("quiero/no quiero contacto") o de identidad ("¿quién soy ante los demás?"). La zona afectada aporta información sobre el tipo de contacto en conflicto.

PULMONES: territorio respiratorio, libertad, duelo. Los pulmones representan la capacidad de "inhalar la vida". Conflictos de duelo (pérdida real o simbólica), miedo a la muerte, sensación de que "el territorio me es robado" o de que "no puedo respirar en este espacio". La tos crónica puede ser conflicto de territorio ("quiero echar a alguien de mi territorio").

CORAZÓN: centro del afecto, conflictos de amor. Problemas cardíacos frecuentemente vinculados a pérdidas afectivas profundas, conflictos relacionales de "territorio del corazón" (la familia, la pareja), o emociones de gran intensidad cronificadas. La hipertensión puede relacionarse con el exceso de control emocional o la presión interna que no se libera.

HÍGADO: cólera, territorialidad, repartos. El hígado procesa las toxinas —también las emociones tóxicas. La rabia acumulada, los conflictos de injusticia, la cólera que no se expresa ni se digiere son los conflictos más frecuentes del hígado. "No puedo digerir lo que me hicieron."

RIÑONES: miedo existencial, líquido vital, supervivencia. Los riñones filtran y mantienen el equilibrio. Conflictos de "no voy a sobrevivir", miedo profundo a la existencia, inseguridad fundamental. El edema y la retención de líquidos pueden señalar un conflicto de abandono o de falta de sostén.

ESTÓMAGO: indigestión emocional, angustia por obtener lo necesario. "No puedo digerir esto" —una situación, una persona, un evento. El estómago también se vincula a la angustia de no poder conseguir lo que se necesita para sobrevivir o para nutrir a otros. Gastritis, úlceras: conflicto de "rabia que corroe desde adentro".""",

            """SISTEMA MUSCULOESQUELÉTICO Y NEUROLÓGICO:

COLUMNA CERVICAL (cuello/nuca): el futuro, lo que "no quiero ver" delante de mí. Tensión en el cuello: rigidez ante los cambios, conflicto con lo que viene, bloqueo de la visión del futuro o de una situación que se avecina.

COLUMNA DORSAL (entre hombros): la carga simbólica, culpa, responsabilidad excesiva. "Cargo demasiado en la espalda." Cuando uno se siente responsable por todo y por todos. La zona entre los omóplatos corresponde especialmente a conflictos de afecto y culpa.

COLUMNA LUMBAR (zona baja): soporte material, dinero, territorio de lo doméstico. Problemas lumbares frecuentemente vinculados a conflictos económicos, inseguridad material, sensación de falta de apoyo fundamental. "No tengo donde apoyarme."

HUESOS: desvalorización profunda de la identidad. Los huesos son la estructura, el sostén. Fracturas, osteoporosis: conflictos de desvalorización intensa ("no valgo", "soy débil en mi núcleo"). La parte del cuerpo afectada indica el tipo de desvalorización (deportiva, sexual, intelectual, etc.).

MÚSCULOS: conflictos de acción e impotencia. La musculatura representa la capacidad de actuar, de moverse en el mundo, de ejercer fuerza. Contracturas crónicas: conflicto entre "quiero hacer" y "no puedo hacer" o "no me permiten hacer".

ARTICULACIONES: flexibilidad, cambios de dirección, decisiones. Las articulaciones permiten los giros. La rigidez articular (artritis, artrosis) puede vincularse a rigidez interna, dificultad para cambiar de dirección vital, conflicto con la adaptabilidad.

SISTEMA NERVIOSO: relación con el mundo, control. El sistema nervioso coordina la relación del organismo con el entorno. Neuralgias: conflicto de separación muy preciso ("me separan de algo o alguien que me es esencial"). Parálisis: conflicto de "no puedo moverme ante esto".""",

            """OTROS SISTEMAS Y PATRONES CRÓNICOS:

INTESTINO DELGADO: separar lo útil de lo inútil. Dificultad para discernir qué es bueno para uno, qué nutrir y qué desechar. Conflicto de "tragarse" situaciones que no se puede ni digerir ni eliminar.

INTESTINO GRUESO / COLON: soltar, dejar ir. Estreñimiento crónico puede vincularse a incapacidad de soltar, control excesivo, "no puedo dejar ir". Diarrea: urgencia de expulsar, rechazo violento de algo. Colon irritable: dualidad entre retener y soltar, ambivalencia crónica.

TIROIDES: conflicto de tiempo y urgencia. "No tengo tiempo para hacer lo que quiero." "Tengo que hacerlo todo muy rápido." El hipotiroidismo (lentitud) puede relacionarse con un conflicto de "no puedo avanzar". El hipertiroidismo (aceleración) con "debo hacerlo todo ya".

SISTEMA INMUNE (autoinmunes): conflicto de identidad, "¿qué es mío y qué no?". En enfermedades autoinmunes el sistema ataca al propio organismo —metáfora del autoataque, el autoboicot, la confusión entre lo propio y lo ajeno.

OJOS: conflicto con lo que se ve o no se quiere ver. Miopía: conflicto con el futuro ("no quiero ver lo que viene"), visión de lejos borrosa. Hipermetropía: conflicto con lo cercano ("no quiero ver lo que tengo cerca"). Problemas de visión súbitos: algo que el inconsciente "no quiere ver".

OÍDOS: conflicto con lo que se escucha o no se quiere escuchar. Sordera, tinnitus: "no quiero oír más esto", saturación del campo auditivo por un conflicto repetitivo.

GARGANTA / VOZ: expresión bloqueada, verdad no dicha. Nudo en la garganta, afonía, faringitis crónica: "no puedo decir lo que pienso", "hay algo que no puedo expresar". La garganta es el puente entre el corazón y la mente.

PATRONES CRÓNICOS: toda enfermedad crónica sugiere un conflicto cronificado —no resuelto en el plano psíquico, mantenido activo por la repetición de la situación o del estado emocional. La clave diagnóstica es identificar qué conflicto apareció antes del primer síntoma, o qué patrón emocional acompaña al síntoma desde siempre.""",
        ],
    },
]


class Command(BaseCommand):
    help = "Seed de la Base de Conocimiento del Mirror Endonauta (43 marcos teóricos)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Eliminar chunks existentes y regenerar todo",
        )

    def handle(self, *args, **options):
        total_docs = 0
        total_chunks = 0

        for doc_data in KB:
            doc, created = MirrorDocumento.objects.get_or_create(
                nombre=doc_data["nombre"],
                defaults={
                    "categoria": doc_data["categoria"],
                    "autor_ref": doc_data.get("autor_ref", ""),
                },
            )

            if not created and not options["force"]:
                self.stdout.write(f"  ~ ya existe: {doc.nombre}")
                continue

            if not created and options["force"]:
                doc.chunks.all().delete()

            chunks_data = doc_data["chunks"]
            for idx, contenido in enumerate(chunks_data):
                MirrorChunk.objects.create(
                    documento=doc,
                    categoria=doc_data["categoria"],
                    contenido=contenido.strip(),
                    chunk_index=idx,
                )

            doc.n_chunks = len(chunks_data)
            doc.save()

            total_docs += 1
            total_chunks += len(chunks_data)
            estado = "creado" if created else "actualizado"
            self.stdout.write(
                f"  ✓ {estado}: {doc.nombre} ({len(chunks_data)} chunks)"
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✅ KB Mirror lista: {total_docs} documentos, {total_chunks} chunks."
                "\n   Siguiente paso: python3 manage.py index_mirror_docs"
                " (requiere OPENAI_API_KEY en .env)"
            )
        )
