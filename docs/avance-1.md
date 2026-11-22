# CRCE — Avance 1: Avisos y notas

## Tarjetas CRC

> **Estado del documento:** borrador sujeto a revisión académica. Actualiza las
> tarjetas CRC del documento del avance (sección 5) según la revisión de diseño.
> Describe el diseño acordado; tres decisiones todavía no están aplicadas en el
> código (ver [Correspondencia con el código](#correspondencia-con-el-código)).

### Convención utilizada

Cada tarjeta separa lo que la clase **sabe** (`[Sabe]`) de lo que **hace**
(`[Hace]`), siguiendo la consigna del avance: "qué sabe, qué hace y con quién
colabora".

Cada colaborador indica el motivo de la colaboración:

| Código | Significado |
| --- | --- |
| `M` | Envía o recibe mensajes. |
| `C` | Crea instancias. |
| `T` | Transmite información necesaria para una operación. |
| `R` | Referencia esencial del dominio para cumplir una responsabilidad. |

Esta clasificación es una **convención propia de este análisis**, no una
notación formal de la cátedra. Las relaciones de herencia no se cuentan como
colaboración: la superclase se indica en la línea **Clase**.

---

### CRC 01 — Reportante

**Clase:** `Reportante`

**Responsabilidades**

- **[Sabe]** Su propia identidad, con la que figura como reportante de sus
  avisos y como autor de sus notas.
- **[Hace]** Registrar un aviso nuevo con ubicación, tipo de situación,
  gravedad estimada, descripción y la fecha y hora recibida, figurando como su
  reportante.
- **[Hace]** Generar el identificador único del aviso nuevo (UUID).
- **[Hace]** Crear notas cuya autoría corresponde a su propia identidad, con la
  fecha y hora recibida.
- **[Hace]** Solicitar al aviso que agregue la nota.

**Colaboradores**

- `Aviso` (C, M): lo crea al registrarlo y le solicita agregar notas.
- `Nota` (C): crea cada nota con su identidad como autor.

---

### CRC 02 — Operador

**Clase:** `Operador`

**Responsabilidades**

- **[Sabe]** Su propia identidad, que queda registrada como responsable del
  descarte.
- **[Hace]** Solicitar el descarte de un aviso, proporcionando la
  justificación, la fecha y hora y su propia identidad.

**Colaboradores**

- `Aviso` (M): recibe la solicitud de descarte.

---

### CRC 03 — Aviso

**Clase:** `Aviso`

**Responsabilidades**

- **[Sabe]** Su identificador, su reportante, su fecha y hora de registro y sus
  datos originales: ubicación, tipo de situación, gravedad estimada y
  descripción.
- **[Sabe]** Sus notas, en el orden en que fueron agregadas.
- **[Sabe]** Su estado actual, único y de propiedad exclusiva.
- **[Hace]** Encontrarse en estado pendiente cuando no se le indica otro
  estado, con una instancia de estado propia.
- **[Hace]** Impedir que un tipo de situación o una gravedad fuera de los
  catálogos cerrados forme parte del aviso.
- **[Hace]** Preservar sus datos originales: ninguna operación, incluido el
  agregado de notas, los modifica.
- **[Hace]** Centralizar la validación de cada operación: verificar que el
  autor de la nota sea su reportante y consultar a su estado si la operación
  está permitida, antes de modificar nada.
- **[Hace]** Delegar en su estado actual qué operaciones se admiten o se
  rechazan y cuál es el estado siguiente, sin preguntar en qué estado se
  encuentra.
- **[Hace]** Agregar la nota solo cuando las validaciones resultan
  satisfactorias, conservando el orden de llegada.
- **[Hace]** Exponer sus notas como una colección inmutable (tupla), sin
  permitir modificaciones externas.
- **[Hace]** Reemplazar su estado solo cuando la transición se completó
  correctamente, de modo que una operación rechazada no deje modificaciones
  parciales.

**Colaboradores**

- `EstadoAviso` (M): delega en él la admisión de notas y la resolución del
  descarte.
- `Pendiente` (C): lo crea como estado inicial propio cuando no se le indica
  otro.
- `Nota` (M): consulta su autor para verificar la autoría antes de agregarla.
- `Reportante` (R): es la referencia contra la que se verifica la autoría de
  cada nota.
- `Operador` (T): recibe su identidad en la solicitud de descarte y la
  transmite al estado para que quede registrada.

---

### CRC 04 — Nota

**Clase:** `Nota`

**Responsabilidades**

- **[Sabe]** Su autor, su fecha y hora y su texto, que no pueden modificarse
  una vez creada.
- **[Hace]** Existir solo completa: autor, fecha y hora y texto nacen juntos.
- **[Hace]** Rechazar un texto vacío o compuesto solo por espacios.
  *(Supuesto de diseño pendiente de confirmación; ver
  [Decisiones pendientes](#decisiones-pendientes).)*

**Colaboradores**

- `Reportante` (R): es el autor que la nota debe conservar y la referencia que
  el aviso usa para verificar la autoría.

---

### CRC 05 — EstadoAviso (abstracta)

**Clase:** `EstadoAviso` (abstracta; superclase de `Pendiente`, `Aceptado` y
`Descartado`)

**Responsabilidades**

- **[Sabe]** Que todo estado se identifica con un nombre, que se usa para
  informar un rechazo.
- **[Hace]** Definir el contrato común de los estados del aviso: decidir si se
  admite agregar una nota y resolver un descarte devolviendo el estado
  siguiente.
- **[Hace]** Obligar a cada estado concreto a decidir si admite notas
  (`validar_agregado_nota`, abstracto).
- **[Hace]** Rechazar el descarte por defecto (`descartar`, comportamiento
  predeterminado que se puede redefinir), de modo que solo lo redefina el
  estado que lo admite.
- **[Hace]** Garantizar que ningún estado modifique al aviso: un estado valida
  o devuelve el estado siguiente, y el cambio lo aplica el aviso.

**Colaboradores**

- Ninguno entre las ocho clases. Los rechazos se comunican mediante la
  jerarquía de excepciones `ErrorCRCE`, que queda fuera de estas tarjetas.

---

### CRC 06 — Pendiente

**Clase:** `Pendiente` (concreta; subclase de `EstadoAviso`)

**Responsabilidades**

- **[Hace]** Admitir el agregado de notas (implementa `validar_agregado_nota`).
- **[Hace]** Admitir el descarte (sobrescribe `descartar`): construye y
  devuelve un nuevo estado descartado con el operador, la justificación y la
  fecha y hora recibidos.

**Colaboradores**

- `Descartado` (C): lo construye como estado siguiente.
- `Operador` (T): recibe su identidad y la transmite al estado descartado.

---

### CRC 07 — Aceptado

**Clase:** `Aceptado` (concreta; subclase de `EstadoAviso`; hereda sin
redefinir el rechazo de `descartar`)

**Responsabilidades**

- **[Hace]** Rechazar el agregado de notas sobre un aviso aceptado
  (implementa `validar_agregado_nota`).

**Colaboradores**

- Ninguno.

*La operación de aceptar no forma parte de este avance. Este estado se
instancia directamente para probar el rechazo de notas sobre un aviso
aceptado.*

---

### CRC 08 — Descartado

**Clase:** `Descartado` (concreta; subclase de `EstadoAviso`; hereda sin
redefinir el rechazo de `descartar`)

**Responsabilidades**

- **[Sabe]** El operador responsable, la justificación y la fecha y hora del
  descarte, que no pueden modificarse y quedan disponibles para consulta.
- **[Hace]** Garantizar que nunca exista un descarte cuya justificación esté
  vacía o compuesta solo por espacios.
- **[Hace]** Rechazar el agregado de notas sobre un aviso descartado
  (implementa `validar_agregado_nota`).

**Colaboradores**

- `Operador` (R): es el responsable del descarte que este estado debe
  conservar.

---

### Notas de diseño

- **Quién solicita y quién decide.** `Reportante` y `Operador` solicitan las
  operaciones que les corresponden. `Operador` no valida la justificación ni
  decide si el estado permite el descarte, y `Reportante` no verifica la
  autoría ni decide si se admite la nota: esas decisiones corresponden a
  `Aviso`, a su estado y a `Descartado`. La autorización por perfil no forma
  parte de este avance.
- **Atomicidad del descarte.** La justificación se valida al construir
  `Descartado`. `Pendiente` construye y devuelve el nuevo estado, y `Aviso`
  lo adopta recién cuando esa construcción terminó; si falla, el aviso sigue
  pendiente.
- **Propiedad del estado.** `Aviso` y `EstadoAviso` se relacionan por
  composición. Cada aviso tiene su propia instancia de estado; inyectar un
  estado transfiere su propiedad exclusiva, por lo que una misma instancia no
  debe compartirse entre avisos distintos.
- **Clases sin tarjeta.** `TipoSituacion` y `GravedadEstimada` son catálogos
  cerrados sin comportamiento propio en este avance. Las excepciones de la
  jerarquía `ErrorCRCE` se documentan por separado.

### Correspondencia con el código

Estas tarjetas describen decisiones ya acordadas que el código todavía no
refleja:

| Decisión acordada | Código actual |
| --- | --- |
| `Descartado` valida su justificación al construirse. | La validación está en `Pendiente.descartar` (`dominio/estados.py`). |
| Cada aviso crea su propia instancia de `Pendiente`. | El valor por defecto `Pendiente()` se evalúa una sola vez y lo comparten todos los avisos (`dominio/aviso.py`). |
| La excepción base se llama `ErrorCRCE`. | Se llama `ErrorDeDominio` (`dominio/excepciones.py`). |

Hasta que el código se actualice, las tarjetas y la implementación no
coinciden en estos tres puntos.

### Decisiones pendientes

1. **Identidad de los actores.** Falta decidir si `Reportante` y `Operador` se
   comparan por su identificador o por el valor completo de sus atributos (el
   código actual compara por valor: identificador y nombre). La decisión
   afecta la verificación de autoría que hace `Aviso`; las tarjetas usan la
   expresión "su identidad" para no anticiparla.
2. **Texto de la nota.** Falta confirmar si el texto no vacío es un requisito
   del enunciado o una decisión de diseño adicional. La consigna habla de
   "notas de texto" sin exigir explícitamente que no estén vacías; por eso la
   tarjeta de `Nota` lo presenta como supuesto.
