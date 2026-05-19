  # YoutubePlus para NVDA

> YoutubePlus es un complemento para personas que aman usar YouTube pero encuentran que muchas funciones del sitio web son difíciles de acceder, como leer los comentarios de los videos.
> Te traemos estas funciones a través de la interfaz de usuario de NVDA en un formato que es fácil de navegar, admite atajos de teclado y es totalmente personalizable, sin necesidad de lidiar con claves API ni de conectar ninguna cuenta personal al complemento.
> Puedes seguir tus canales favoritos y tener la seguridad de que verás cada video de esos canales, sin que el algoritmo de YouTube los filtre.
> También proporcionamos un sistema de Favoritos para videos, canales, listas de reproducción y una lista de seguimiento para guardar el contenido que te interesa pero que aún no has tenido tiempo de ver.
> Incluye una búsqueda de videos integrada que muestra los resultados dentro de la misma interfaz de usuario utilizada en todo el complemento, no solo un cuadro de búsqueda que abre YouTube en un navegador.
> Se incluye una función de descarga para guardar videos o archivos de audio, aunque se proporciona como una comodidad más que como el enfoque principal. Si la descarga es tu necesidad principal, existen otros complementos dedicados a esta función que quizás quieras explorar.
> Lo único que este complemento no hace es incrustar un reproductor de video. Creemos que el reproductor web de YouTube ya es lo suficientemente accesible por sí solo. Si consideras que aún le falta accesibilidad, puedes usar otros complementos como [browserNav](https://addonstore.nvaccess.org/?channel=stable&language=en&apiVersion=2025.3.2&addonId=browsernav) para mejorar la experiencia.

## Atajos de Teclado y Comandos

Este complemento utiliza un sistema de atajos por capas para evitar conflictos con otros complementos o comandos de NVDA.
Presiona **NVDA+Y** para ingresar al modo de comando de YoutubePlus, luego presiona una de las siguientes teclas para acceder a cada función o ventana.

**Nota:** Si el atajo principal (`NVDA+Y`) tiene conflicto con otro complemento, puedes cambiarlo a través de `NVDA -> Preferencias -> Gestos de entrada...` bajo la categoría "YoutubePlus".

### Teclas disponibles en la capa de YoutubePlus

* a: (añadir a...) — Abre un submenú que te permite elegir dónde añadir el video o canal actual
* f: (abrir videos favoritos) — Abre la ventana de videos favoritos
* c: (abrir canales favoritos) — Abre la ventana de canales favoritos
* p: (abrir listas de reproducción favoritas) — Abre la ventana de listas de reproducción favoritas
* w: (mostrar lista de seguimiento) — Abre la ventana de la lista de seguimiento
* b: (descargar subtítulos) - Descarga los subtítulos del video actual. Aparecerá un cuadro de diálogo de selección de idioma 
* d: (descargar) — Te pide confirmar si deseas descargar como video o solo audio
* e: (buscar) — Abre la ventana de búsqueda de videos
* i: (información) — Abre la ventana de detalles del video
* t: (mostrar marca de tiempo) — Muestra las marcas de tiempo o capítulos si están disponibles
* m: (abrir administrar suscripciones) — Abre la ventana de administración de suscripciones
* s: (abrir feed de suscripciones) — Muestra los videos de los canales que sigues
* u: (abrir Administrador de Perfiles de Usuario) — Abre la ventana de administración de Perfiles de Usuario
* l: (mostrar comentarios) — Muestra los comentarios (los detalles se explican más abajo)
* shift+l: (detener monitoreo de chat en vivo) — Detiene el monitoreo del chat en vivo
* r: (alternar lectura automática de chat en vivo) — Alterna la voz automática para los mensajes entrantes del chat en vivo
* v: (mostrar chat en vivo) — Vuelve a abrir la ventana del chat en vivo si la cerraste mientras la transmisión aún sigue activa
* y: (abrir diálogo de opciones de YoutubePlus) abre rápidamente las opciones de NVDA y se enfoca en la categoría YoutubePlus.
* h: (ayuda) — Abre una ventana que enumera todos los atajos disponibles

**Nota:** Para los comandos que actúan directamente sobre un video, el complemento verifica primero la ventana del navegador que tienes abierta. Si una página de video de YouTube está activa, utiliza la URL de ese video. Si no hay ninguna página de video abierta, verifica el portapapeles en busca de una URL de YouTube.

## Detalles de las Funciones y Comandos

### a: (añadir a...)

Este comando en la capa de YoutubePlus envía la información del video o canal al destino seleccionado:

* Añadir a Videos Favoritos  (v)
* Añadir a Canales Favoritos  (c)
* Añadir a Listas de Reproducción Favoritas  (p)
* Suscribirse al Canal  (s)
* Añadir a la Lista de Seguimiento  (w)

El complemento verifica primero la página del navegador abierta actualmente. Si es una página de video de YouTube, extrae la URL y la procesa según tu selección. Si la página no es un video de YouTube o no hay ningún navegador abierto, verifica el portapapeles en busca de una URL de YouTube.

La mayoría de los comandos funcionan con cualquier tipo de URL de YouTube, ya que el complemento puede derivar la información necesaria. Por ejemplo, si estás en la página de un video y eliges "Añadir a Canales Favoritos", el complemento puede extraer la URL del canal automáticamente. Lo mismo se aplica para suscribirse a un canal.

La única excepción son las listas de reproducción: debes tener abierta una página de lista de reproducción de YouTube o tener una URL válida de lista de reproducción de YouTube copiada en el portapapeles.

### d: (descargar video/audio)

Este comando abre un pequeño cuadro de diálogo que pregunta si deseas descargar el video como un archivo MP4 o solo el audio como M4A. Puedes establecer el destino de la descarga en la sección de [Opciones](https://www.google.com/search?q=%23opciones).

Ten en cuenta que la función de descarga se proporciona por comodidad y puede tener limitaciones si se usa en exceso. Si necesitas descargar grandes cantidades de contenido de YouTube, se recomiendan otras herramientas dedicadas.

### e: (buscar)

Este comando abre una ventana de búsqueda de YouTube. Escribe tu consulta en el campo de búsqueda y presiona Enter para buscar inmediatamente. También puedes pulsar Tab para ajustar la cantidad de resultados a mostrar; el complemento recordará este valor para futuras búsquedas.

Los resultados se muestran en el mismo formato de [lista de videos](https://www.google.com/search?q=%23lista-de-videos) utilizado en todo el complemento, no como una página web de YouTube. Puedes acceder a todos los detalles del video de la misma manera que en cualquier otra lista de videos del complemento.

### i: (información del video)

Muestra los siguientes detalles del video actual:

* Título
* Canal
* Duración
* Subido
* Vistas
* Me gusta
* Comentarios
* Descripción

### t: (marca de tiempo / capítulo)

Muestra la marca de tiempo o la lista de capítulos del video (si el creador incluyó esta información). Si el complemento informa "No se encontraron capítulos en este video", el video simplemente no tiene datos de capítulos.

Esta ventana ofrece más comodidad que leer los capítulos desde el navegador:

* Un campo de búsqueda para filtrar la lista de marcas de tiempo/capítulos; los resultados se actualizan instantáneamente sin presionar Enter.
* La lista completa se muestra con la descripción de cada sección primero, seguida de su posición de tiempo.
* Un área de texto de solo lectura para leer descripciones largas de capítulos.
* Un botón "Abrir capítulo" — o presiona Espacio o Enter — para saltar directamente a ese capítulo en el video.
* Botón Copiar título (Alt+C) para copiar el nombre del capítulo.
* Botón Copiar URL (Alt+U) para copiar la URL con la marca de tiempo de ese capítulo.
* Botón Exportar (Alt+E) para guardar todos los datos de marcas de tiempo/capítulos como un archivo de texto.

### Favoritos

Una ventana que muestra tus favoritos guardados, dividida en 4 pestañas por tipo:

* **Video:** Enumera tus videos guardados. Incluye botones de Acción y Copiar para cada elemento (descritos más abajo).
* **Canal:** Enumera tus canales guardados con un panel de descripción del canal. Incluye botones para abrir el canal y explorar su contenido por tipo.
* **Lista de reproducción:** Enumera tus listas de reproducción guardadas. Presiona Espacio, Enter o Alt+V para expandir todos los videos de una lista de reproducción. Incluye un botón Abrir en la Web (Alt+W) para abrir la lista de reproducción en un navegador.
* **Lista de seguimiento:** Enumera tus videos guardados con la misma estructura y diseño que la pestaña Video.

#### Comandos de la ventana de Favoritos

* Presiona Control+1 a Control+4 para cambiar entre pestañas.
* Presiona Control+Flecha arriba/abajo para reordenar las pestañas.
* Presiona Control+C (copiar), Control+X (cortar) o Control+V (pegar) para reordenar los elementos.
* Las pestañas de Videos Favoritos y Lista de Seguimiento admiten copiar y mover elementos entre sí. Las pestañas de Canales y Listas de Reproducción Favoritas solo admiten mover elementos dentro de su propia lista.


* Presiona F2 para renombrar manualmente el título del video / canal / lista de reproducción.
* Presiona Alt+R o Suprimir para eliminar un elemento.
* Presiona Alt+N para añadir un nuevo elemento desde el portapapeles; para las pestañas de canal y lista de reproducción, la URL debe coincidir con el tipo de pestaña.
* Presiona Alt+S para ir al campo de búsqueda que filtra los resultados instantáneamente a medida que escribes, sin necesidad de presionar Enter.
* Presiona el botón **Ordenar...** (al lado del campo de búsqueda) para ordenar la lista. 
Puedes ordenar por Título, Canal, Duración, Fecha de adición o Fecha de subida. 
Elige orden ascendente o descendente. 
Si marcas "Aplicar permanentemente", el orden se guardará en el archivo. 
De lo contrario, el ordenamiento es temporal y se restablecerá al buscar o actualizar la lista. 
Presiona "Limpiar orden" para restaurar el orden original.

#### Lista de videos

En las pestañas de video y lista de seguimiento, así como en cualquier otra vista que muestre una lista de videos, encontrarás los botones **Acción...** y **Copiar...**. Estos son controles estándar en todas las vistas de listas de videos, y el feed de suscripciones añade una opción adicional de "Anular suscripción a este canal".

Presiona Enter en cualquier elemento para abrir el video en tu navegador, o presiona la barra espaciadora para realizar la acción rápida que puedes configurar en [Opciones](https://www.google.com/search?q=%23opciones).

##### Botón Acción

Presiona Alt+A para abrir el menú Acción, que incluye:

* Ver información del video...  (i)
* Ver comentarios / Reproducción...  (c)
* Ver capítulos/marcas de tiempo...  (t)
* Descargar video  (d)
* Descargar audio  (a)
* Descargar subtítulos  (b)
* Añadir a Videos Favoritos  (f)
* Añadir a Canales Favoritos  (f)
* Añadir a la Lista de Seguimiento  (w)
* Abrir video en el navegador  (o)
* Abrir canal en el navegador  (h)
* Mostrar videos del canal  (v)
* Mostrar shorts del canal  (s)
* Mostrar transmisiones en vivo del canal  (l)

##### Botón Copiar

Presiona Alt+C para abrir el menú Copiar, que incluye:

* Copiar título  (t)
* Copiar URL del video  (u)
* Copiar nombre del canal  (c)
* Copiar URL del canal  (h)
* Copiar resumen  (s)

### Feed de suscripciones

Una ventana que muestra los videos de los canales que sigues dentro del complemento. Esto es independiente de las suscripciones de tu cuenta de YouTube; no se requiere vinculación de cuentas ni datos personales.

A diferencia de la ventana de Favoritos, esta vista utiliza pestañas estándar divididas por tipo de contenido:

* **Todo:** Todos los tipos de contenido combinados.
* **Video:** Solo videos regulares.
* **Shorts:** Solo videos cortos (Shorts).
* **En vivo:** Transmisiones en vivo y repeticiones de transmisiones en vivo.

Más allá de estas categorías predeterminadas, puedes crear categorías personalizadas y configurar qué canales aparecen en cada una.

#### Comandos del feed de suscripciones

* Presiona Control+1 a Control+0 para saltar a una pestaña de categoría (hasta 10 categorías).
* Presiona Control+Flecha arriba/abajo para reordenar las categorías, al igual que en la ventana de Favoritos.
* Presiona F2 para renombrar una categoría (excepto las 4 categorías predeterminadas).
* Presiona Control+= para añadir una nueva categoría.
* Presiona Control+- para eliminar una categoría (excepto las 4 categorías predeterminadas).
* Accede a los botones Acción y Copiar de cada video, o presiona Enter para abrirlo en un navegador.
* Presiona Suprimir o Alt+S para marcar un video como visto; se eliminará de la lista.
* Presiona Control+Suprimir para marcar todos los videos de la pestaña actual como vistos.

Botones adicionales en esta ventana:

* **Mark as seen (Alt+S)** (Marcar como visto) — elimina el video de la lista; la tecla Suprimir también funciona.
* **Add new Subscription from clipboard URL (Alt+N)** (Añadir nueva suscripción desde URL del portapapeles) — te suscribe a un canal usando la URL copiada en el portapapeles.
* **Update Feed (Alt+U)** (Actualizar feed) — activa manualmente una actualización para todos los canales suscritos; el complemento también se actualiza automáticamente al iniciar NVDA de forma predeterminada.
* **More... (Alt+M)** (Más...) — abre un submenú con opciones adicionales:
* Marcar todos en la pestaña actual como vistos (Ctrl+Suprimir)  (a)
* Mostrar todos los videos (incluyendo vistos)  (v) — alterna entre solo no vistos y todos los videos; la opción se guarda automáticamente.
* Administrar suscripciones...  (m)
* Añadir nueva categoría...  Ctrl+=  (c)
* Renombrar categoría actual...  F2  (r)
* Eliminar categoría actual...  Ctrl+-
* Limpiar todos los videos del feed... — elimina todos los videos de la base de datos sin eliminar tus suscripciones; es útil si la base de datos crece demasiado y afecta el rendimiento de NVDA.



### Administrar suscripciones

Esta ventana muestra todos los canales a los que estás suscrito. El primer bloque es la lista de canales, seguido de las opciones de administración para cada canal:

* **Filtrar por categoría** — filtra la lista de canales por categoría; de forma predeterminada es "Todo".
* **Asignar a categorías** — elige en qué categorías debe aparecer el contenido de este canal.
* **Tipos de contenido a obtener** — elige qué tipos de contenido actualizar para este canal (Videos, Shorts, En vivo); útil para canales que solo publican ciertos tipos de contenido.
* **Ver contenido... (Alt+C)** — explora el contenido del canal, igual que el botón Acción.
* **Añadir nuevo canal de suscripción desde el portapapeles... (Alt+N)** — se suscribe a un nuevo canal usando la URL del portapapeles.
* **Anular suscripción a este canal (Alt+U)** — elimina el canal de tus suscripciones.
* **Guardar cambios** — **importante:** debes presionar esto antes de cerrar la ventana, o tus cambios no se guardarán.

### Administrador de Perfiles de Usuario

Esta ventana gestiona tus perfiles de usuario. El complemento viene con un perfil "predeterminado" (default). Puedes añadir, eliminar o renombrar perfiles aquí. Para cambiar entre perfiles, ve al panel de Opciones del complemento.

En esta ventana:

* Presiona F2 para renombrar el perfil seleccionado.
* Presiona Suprimir para eliminar el perfil seleccionado.

**Nota:** Eliminar un perfil borra permanentemente todos los datos asociados a él. Cualquier video, canal o suscripción guardada en ese perfil se perderá.

### l: (mostrar comentarios)

Hay tres tipos de comentarios en los videos de YouTube:

* **Comentario** — comentarios estándar de los espectadores en videos regulares.
* **Chat en vivo** — mensajes enviados durante una transmisión en vivo.
* **Repetición del chat en vivo** — el chat en vivo grabado de un video transmitido previamente, si el propietario del canal no lo ha eliminado.

YoutubePlus admite el acceso a los tres tipos a través de este comando.

#### Chat en vivo de...

Para videos actualmente en vivo, presiona L y el complemento abrirá una nueva ventana que muestra los mensajes de chat entrantes. Solo se muestran los mensajes recibidos después de activar el comando; los mensajes anteriores no se capturan.

Puedes cerrar esta ventana y volver a abrirla más tarde con el comando V en la capa de YoutubePlus, siempre que la transmisión siga activa y no se haya reiniciado NVDA.

Usa el comando R para alternar si NVDA lee los nuevos mensajes en voz alta a medida que llegan. Esto funciona bien para transmisiones con mensajes poco frecuentes. Para transmisiones de alto volumen, puede ser más fácil desactivar la lectura automática y desplazarse por la ventana manualmente.

Presiona Shift+L para detener el monitoreo del chat para el video actual.

Tres opciones afectan directamente a esta función:

* **Verbalizar automáticamente el chat en vivo entrante:** Cuando está marcada, NVDA lee los nuevos mensajes en voz alta inmediatamente — la misma función que el comando R, pero guardada como una preferencia predeterminada.
* **Intervalo de actualización del chat en vivo:** Cada cuántos segundos el complemento verifica si hay nuevos mensajes. El valor predeterminado es 5 segundos.
* **Límite de historial de mensajes:** El número máximo de mensajes almacenados en memoria durante una sesión. La ventana del chat en vivo muestra solo los mensajes más recientes hasta este límite (predeterminado: 5.000). El complemento conserva todos los mensajes en segundo plano para su exportación, hasta un máximo de 200.000 para evitar un uso excesivo de memoria.

Cuando una transmisión termina — o el complemento detecta que ha terminado — aparecerá automáticamente un cuadro de diálogo preguntando si deseas exportar todos los mensajes recopilados. Presiona Sí para guardar el historial del chat como un archivo.

#### Comentarios / Repetición del chat en vivo

Para videos subidos regulares o transmisiones archivadas, puedes acceder a los comentarios de la misma manera. Si tanto la repetición del chat en vivo como los comentarios estándar están disponibles, un cuadro de diálogo preguntará cuáles deseas cargar.

No hay límite en la cantidad de comentarios mostrados, aunque la carga puede tomar tiempo para videos con muchos comentarios.

Los comentarios se muestran con los comentarios fijados primero, seguidos de todos los demás en el orden de clasificación configurado en Opciones (los más nuevos primero o los más antiguos primero).

#### Secciones de la ventana de comentarios

* **Campo de búsqueda** — escribe para filtrar los comentarios; los resultados se updatean instantáneamente.
* **Cuadro combinado de filtro** — selecciona una opción de filtro (el complemento rellena el campo de búsqueda automáticamente):
* Sin filtro — predeterminado; muestra todos los comentarios.
* Filtrar por autor seleccionado — muestra solo los comentarios del usuario seleccionado.
* Mostrar solo Super Chats
* Mostrar solo Super Stickers
* Mostrar solo Super Gracias


* **Lista de comentarios** — muestra el nombre del usuario seguido de su mensaje.
* **Área de texto de solo lectura** — desplázate por el texto completo del comentario seleccionado, útil cuando un comentario es demasiado largo para mostrarse por completo en la lista.
* **Botón Copiar (Alt+C o Control+C)** — copia el comentario seleccionado.
* **Botón Exportar (Alt+E)** — guarda todos los comentarios como un archivo de texto en la carpeta establecida en Opciones.
* **Campo de cantidad total pagada** — se muestra solo para las repeticiones de chat en vivo; muestra las donaciones totales de los espectadores durante la transmisión.

## Opciones

Accede a las opciones a través de `NVDA -> Preferencias -> Opciones...` y selecciona la categoría **"YoutubePlus"**.

* **Perfil activo:** Selecciona el perfil a usar. Se requiere reiniciar después de cambiar de perfil.
* **Botón Administrar perfil:** Abre la ventana del Administrador de Perfiles de Usuario.
* **Acción rápida (Barra espaciadora):** Elige qué hace la tecla Espacio en las ventanas de listas de videos. Todas las opciones del menú Acción están disponibles.
* **Modo de notificación:** Elige cómo señala el complemento la actividad en segundo plano:
* *Pitido:* Tonos de pitido cortos
* *Sonido:* Efecto de audio
* *Silencioso:* Sin notificación de audio (las respuestas habladas continúan ocurriendo)


* **Orden de clasificación predeterminado:** Elige si las listas (comentarios, videos del canal) se ordenan por **Los más nuevos primero** o **Los más antiguos primero**.
* **Elementos a obtener:** Cuántos elementos recuperar por tipo de contenido al explorar un canal y para las actualizaciones del feed de suscripciones. Predeterminado: 20.
* **Tipos de contenido predeterminados:** Elige qué tipos de contenido obtener para los canales recién suscritos: Videos, Shorts y/o En vivo.
* **Intervalo de actualización en segundo plano:** Cada cuánto tiempo el complemento busca nuevo contenido de los canales suscritos. Se puede desactivar o configurar desde 15 minutos hasta 24 horas. El complemento también se actualiza automáticamente en cada inicio de NVDA de forma predeterminada.
* **Verbalizar automáticamente el chat en vivo entrante:** Cuando está marcada, NVDA lee los nuevos mensajes de chat en voz alta a medida que llegan.
* **Intervalo de actualización del chat en vivo:** Cada cuántos segundos el complemento verifica si hay nuevos mensajes. Predeterminado: 5 segundos.
* **Límite de historial de mensajes:** Número máximo de mensajes de chat almacenados en memoria durante una sesión.
* **Método de cookies (Experimental)**: Puedes elegir el navegador en el que hayas iniciado sesión con tu cuenta de YouTube para intentar solucionar el error "Inicia sesión para confirmar que no eres un robot". 
* **Formato de subtítulos predeterminado:** Elige el formato de archivo de subtítulos para las descargas: srt, vtt, ttml o txt para subtítulos sin marca de tiempo.
* **Ruta predeterminada de la carpeta de descarga y exportación:** La carpeta de destino para los videos/audio descargados y el chat exportado.
* **Respaldar datos ahora:** Respalda manualmente todos los datos del perfil activo. El complemento también realiza un respaldo automático diario en segundo plano.
* **Restaurar datos desde un respaldo:** Muestra una lista de los respaldos disponibles (hasta los últimos 5 días) para que puedas elegir desde qué fecha restaurar.

## Información Adicional

Este complemento se basa en dos bibliotecas principales: [pytchat]() para el monitoreo del chat en vivo, y [yt-dlp]() para todo el acceso restante a los datos de YouTube. Extendemos nuestro sincero agradecimiento a los desarrolladores de ambas bibliotecas.

### Acerca de yt-dlp

[yt-dlp]() es una de las herramientas de código abierto más potentes para descargar video y audio de sitios web de todo el mundo, admitiendo más de 1.000 sitios, no solo YouTube. Es gratuito, de código abierto y mantenido activamente por una comunidad global, sin anuncios ni malware a diferencia de muchas herramientas de descarga basadas en navegador.

Dicho esto, por favor ten en cuenta las siguientes pautas de uso:

1. **Uso justo:** Evita obtener grandes cantidades de datos o enviar solicitudes repetidas en poco tiempo. YouTube puede detectar actividad inusual y restringir temporalmente el acceso desde tu dirección IP.
2. **Derechos de autor y privacidad:** Cualquier dato o contenido recuperado debe ser solo para visualización o análisis personal. Por favor, respeta los Términos de servicio de cada plataforma y no utilices los datos de formas que infrinjan los derechos de autor.
3. **Responsabilidad:** Tú eres responsable de cómo utilizas este software. El desarrollador del complemento proporciona únicamente la interfaz para acceder a los datos de YouTube a través de la biblioteca yt-dlp.

**Consejo:** Si necesitas procesar grandes cantidades de datos, espacia tus solicitudes para mantener la estabilidad de la conexión y evitar restricciones de acceso.
