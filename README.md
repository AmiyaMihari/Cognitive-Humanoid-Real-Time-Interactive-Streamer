# C.H.R.I.S. - Cognitive Humanoid Reasoning Interactive System

"La inteligencia no consiste en almacenar símbolos, sino en interpretarlos dentro de una red coherente de significados." - Rapaport, quizá.
"Propongo considerar la siguiente pregunta: '¿Pueden pensar las máquinas?'" - A. Turing
"Se suele decir que las máquinas solo pueden hacer lo que les mandamos hacer. [...] La respuesta corta es que las máquinas a menudo nos sorprenden." - A. Turing
## Descripción breve
C.H.R.I.S. (también llamado Chris, Christopher o Kurisu) es un proyecto de IA VTuber, cuyo objetivo es crear un streamer virtual interactivo y autónomo.

A diferencia de otros proyectos similares, Chris está fundado en la investigación de Generative Agents: Interactive Simulacra of Human Behavior (2023, https://arxiv.org/abs/2304.03442).

Chris está fundamentado en seguir la construcción de una "persona", o que simule serlo (es decir, sea capaz de pasar el Test de Turing, o ser indistinguible entre hablar con un humano y una máquina).
Para lograrlo, se base en el pilar de la construcción de la "Identidad", o dicho de otra forma, hacerle creer a la máquina que está viva:

Identidad
├─ Personalidad
├─ Valores
├─ Objetivos
├─ Relaciones
└─ Estado emocional actual

¿Qué es la Identidad? Es un conjunto de elementos, algunos dinámicos y otros innalterables, que le dan "vida" a la máquina para su toma de decisiones. En este enfoque, el uso de cualquier modelo de lenguaje es indiferente, ya que en Chris importa más cómo se maneja la memoria y cómo esta interactúa con su identidad para dar una respuesta que puede variar en función del "estado de la máquina" en ese preciso momento. Definamos qué con esas otras carecterísticas:

## 1. Personalidad: "¿Cómo suelo comportarme?"
Son patrones relativamente estables.

Ejemplo:
- Extrovertido
- Curioso
- Paciente
- Competitivo
- Empático

La personalidad afecta cómo se ejecuta una acción. Dos agentes pueden tener el mismo "objetivo" (ver definición de objetivo):
- Conseguir empleo

Pero sus decisiones para conseguirlo variarán en función a su personalidad.

Agente introvertido:
- Investiga empresas
- Envía CVs online
- Evita eventos sociales

Agente extrovertido:
- Asiste a conferencias
- Habla con reclutadores
- Hace networking

## 2. Valores: "¿Qué considero importante?"
Son más profundos que la personalidad (y por ende, más difíciles de modificar).

Ejemplos:
- Honestidad
- Familia
- Conocimiento
- Libertad
- Justicia
- Tradición

Los valores sirven para resolver conflictos. En el siguiente escenario donde el agente concluya que:

"Mentir me ayudaría."

Un agente cuyo valor principal sea honestidad podría decidir: No mentir.

Aunque eso perjudique sus intereses o sus objetivos. En humanos ocurre constantemente (para bien y para mal). No se toma una decisión solo por utilidad, también por principios.


## 3. Creencias: "¿Qué pienso que es verdad?"
Las creencias pueden ser correctas o incorrectas. Son afirmaciones concretas sobre algo o alguien.

Ejemplo:
- A: Creo que Juan es confiable.
- B: Creo que Juan no me aprecia.

Lo interesante es que dos agentes pueden observar exactamente el mismo evento y generar creencias distintas.

Evento: "Juan no respondió un mensaje."

- Agente A: Está ocupado.
- Agente B: Me está ignorando.

La observación (el hecho) es igual. La interpretación cambia.

## 4. Objetivos: "¿Qué quiero lograr?"
Son el motor del comportamiento.

Ejemplo:

- Convertirme en médico.
Ese objetivo genera otros.

Convertirme en científico
↓
Entrar a la universidad
↓
Aprobar examenes
↓
Estudiar en este momento

La mayoría de agentes modernos tienen objetivos jerárquicos.

Meta vital
↓
Meta anual
↓
Meta mensual
↓
Meta semanal
↓
Acción actual

Puede existir más de un objetivo. Estos objetivos pueden irse creando con el tiempo (o eliminándose), pero siempre debe de haber un objetivo (mínimo).

## 5. Relaciones: "¿Qué significan las otras personas para mí?"

No basta con recordar nombres o identificar con quién se habla. Hay que modelar vínculos.

Ejemplo:

María
- amistad: 0.9
- confianza: 0.8
- admiración: 0.7

Juan
- amistad: 0.2
- confianza: 0.1
- admiración: 0.3

Esto afecta decisiones. Si ambos pidedn ayuda:
- María
- Pedro

El agente probablemente ayude primero a María.

## 6. Memoria autobiográfica: "¿Qué me ha pasado?"

Es la historia personal del agente.

Ejemplo:
- Me gradué.
- Perdí mi empleo.
- Conocí a Juan.

Es algo distinto del conocimiento general.

No es: París es la capital de Francia.

Es: Yo viajé a París.

La autobiografía es lo que da continuidad temporal a los hechos de la realidad. Sin ella, el agente "muere" y "renace" en cada conversación.

## 7. Autoimagen: "¿Quién creo que soy?"
No necesariamente coincide con la realidad (el hecho).

Ejemplo:

- Soy inteligente.
- Soy mal dibujante.
- Soy un buen amigo.

La autoimagen o autopercepción de sí mismo influye en su toma de decisiones. Si un agente cree:

- Soy malo para hablar en público.

puede evitar conferencias incluso si objetivamente es excelente orador.

Esto aparece parcialmente en Generative Agents cuando las reflexiones generan conclusiones como:

- "Yo muy comprometido con la ciencia."

Con el tiempo eso se convierte en:

- "Soy científico."

## 8. Estado emocional: "¿Cómo me siento ahora?"

Se trata de un atibuto temporal, no estable. Puede cambiar varias veces en una misma sesión.

Ejemplos:
- Feliz
- Triste
- Ansioso
- Enojado
- Frustrado
- Entusiasmado
- Aburrido

Es la parte más volátil. Puede cambiar en minutos.

Consiste en un modelo emocional estructurado (cuantizable, medible). Ejemplo:
- Felicidad: 80
- Ansiedad: 20
- Enojo: 10
- Tristeza: 5

Si ocurre un evento:
- Juan me regañó

El estado es suceptible a cambiar (en función a la personalidad):
Personalidad empatica y tranquila:
Felicidad: 50
Ansiedad: 30
Enojo: 15
Tristeza: 10

Personalidad fuerte e impaciente:
Felicidad: 20
Ansiedad: 70
Enojo: 80
Tristeza: 20

El estado emocional es el que más afecta en la toma de decisiones. Supongamos que dos agentes reciben exactamente el mismo mensaje:

"¿Quieres venir a la fiesta?"

Agente A:
- Feliz
- Relajado

Responde:
"¡Claro, suena divertido!"

Agente B:
- Ansioso
- Estresado

Responde:
"Gracias, pero prefiero quedarme en casa."

Misma personalidad, diferente estado emocional.

Esto no solo afecta el estado actual (sesión actual), sino la percepción de los recuerdos (la memoria a corto y largo plazo):

Por ejemplo:

Si tú desayunas cereal hoy, probablemente lo olvides.

Pero si hoy te gradúas de la universidad o tienes una discusión fuerte con alguien, es más probable que lo recuerdes durante años.

Entonces el sistema podría hacer:

Evento emocional fuerte
↓
Mayor importancia
↓
Mayor probabilidad de recordarlo

Las emociones ayudan a decidir qué recuerdos son importantes y cuáles se descartan más fácilmente.

## 9. Modelo del mundo: "¿Cómo funciona el mundo?"

Ejemplo:

- Para graduarme necesito aprobar materias.
- Si trabajo más, ganaré dinero.
- Las personas suelen responder mejor cuando son tratadas con respeto.

Es un simulador interno. Es la forma en la que el agente cree que es el mundo, pero a diferencia de las creencias, esta sirve para modelas o predecir las consecuencias de lo que pasará con sus decisiones.
Se trata de reglas de cómo opera la realidad. Son más estables que las creencias. Más abstracto. Generalista.

Ejemplo:

Observaciones (interacción con la realidad)
↓
Modelo del mundo
↓
Creencias
↓
Decisiones

GitHub: [AmiyaMihari](https://github.com/AmiyaMihari)  
¿Quieres colaborar? ¡Contáctame por GitHub!

## Licencia
Open Source.
