# YoutubePlus for NVDA

> YoutubePlus es un complemento para las personas que disfrutan usando YouTube pero encuentran que muchas funciones del sitio web son difíciles de usar — como leer los comentarios de los videos.
> Te traemos estas funciones a través de la interfaz de usuario de NVDA en un formato fácil de navegar, con soporte para atajos de teclado y totalmente personalizable — sin necesidad de manejar claves de API ni conectar ninguna cuenta personal al complemento.
> Puedes seguir tus canales favoritos y tener la certeza de que verás cada video de esos canales, sin que el algoritmo de YouTube los filtre.
> También ofrecemos un sistema de Favoritos para videos, canales, listas de reproducción, y una lista de seguimiento para guardar contenido que te interesa pero que aún no has tenido tiempo de ver.
> Hay una búsqueda de video integrada que muestra los resultados dentro de la misma interfaz de usuario utilizada en todo el complemento — no solo un cuadro de búsqueda que abre YouTube en un navegador.
> Se incluye una función de descarga para guardar videos o archivos de audio, aunque se ofrece como una comodidad más que como el enfoque principal. Si descargar es tu necesidad principal, existen otros complementos dedicados a esta función que quizás quieras explorar.
> Lo único que este complemento no hace es incrustar un reproductor de video. Creemos que el reproductor web de YouTube ya es lo suficientemente accesible por sí solo. Si aún lo encuentras insuficiente, puedes usar otros complementos como [browserNav](https://addonstore.nvaccess.org/?channel=stable&language=en&apiVersion=2025.3.2&addonId=browsernav) para mejorar la experiencia.

## Atajos de teclado y comandos

Este complemento usa un sistema de atajos por capas para evitar conflictos con otros complementos o comandos de NVDA.
Presiona **NVDA+Y** para entrar en el modo de comandos de YoutubePlus, y luego presiona una de las siguientes teclas para acceder a cada función o ventana.

**Nota:** Si el atajo principal (`NVDA+Y`) entra en conflicto con otro complemento, puedes cambiarlo desde `NVDA -> Preferencias -> Gestos de entrada...` en la categoría "YoutubePlus".

### Teclas disponibles en la capa de YoutubePlus

* a: (add to...) — Abre un submenú que te permite elegir dónde añadir el video o canal actual
* f: (open favorites video) — Abre la ventana de videos favoritos
* c: (open favorites channel) — Abre la ventana de canales favoritos
* p: (open favorites playlist) — Abre la ventana de listas de reproducción favoritas
* w: (show watch list) — Abre la ventana de la lista de seguimiento
* d: (download) — Te pregunta si deseas descargar como video o solo audio
* e: (search) — Abre la ventana de búsqueda de videos
* q: (quick search) — Busca en YouTube inmediatamente usando el texto actualmente seleccionado, o el contenido del portapapeles si no hay nada seleccionado — sin abrir primero el diálogo de búsqueda
* control+h: (search history) — Abre la ventana de Favoritos directamente en la pestaña de Historial de Búsqueda
* i: (info) — Abre la ventana de detalles del video
* t: (show timestamp) — Muestra marcas de tiempo o capítulos si están disponibles
* g: (get thumbnail description) — Descarga la miniatura del video y la envía a la aplicación Be My Eyes para obtener una descripción en vivo
* m: (open manage subscription) — Abre la ventana de gestión de suscripciones
* s: (open subscription feed) — Muestra videos de los canales que sigues
* u: (open User Profile Manager) — Abre la ventana de gestión de perfiles de usuario
* l: (show comment) — Muestra comentarios (detalles explicados abajo)
* shift+l: (stop monitor live chat) — Detiene el monitoreo del chat en vivo
* r: (toggle automatic reading live chat) — Activa/desactiva la lectura automática de los mensajes del chat en vivo entrantes
* v: (show live chat) — Vuelve a abrir la ventana del chat en vivo si la cerraste mientras la transmisión seguía activa
* y: (open YoutubePlus settings dialog) abre rápidamente la configuración de NVDA y enfoca la categoría YoutubePlus
* h: (help) — Abre una ventana que enumera todos los atajos disponibles

**Nota:** Para los comandos que actúan directamente sobre un video, el complemento primero revisa la ventana del navegador que tienes abierta. Si hay una página de video de YouTube activa, usa la URL de ese video. Si no hay ninguna página de video abierta, revisa el portapapeles en busca de una URL de YouTube.

## Detalles de funciones y comandos

### a: (add to...)

Este comando en la capa de YoutubePlus envía información del video o canal al destino seleccionado:

* Add to Favorite Videos (v)
* Add to Favorite Channels (c)
* Add to Favorite Playlist (p)
* Subscribe to Channel (s)
* Add to Watch List (w)

El complemento primero revisa la página del navegador que está abierta actualmente. Si es una página de video de YouTube, extrae la URL y la procesa según tu selección. Si la página no es un video de YouTube o no hay ningún navegador abierto, revisa el portapapeles en busca de una URL de YouTube.

La mayoría de los comandos funcionan con cualquier tipo de URL de YouTube, ya que el complemento puede derivar la información necesaria. Por ejemplo, si estás en una página de video y eliges "Add to Favorite Channels," el complemento puede extraer automáticamente la URL del canal. Lo mismo aplica para suscribirse a un canal.

La única excepción son las listas de reproducción — debes tener abierta una página de lista de reproducción de YouTube, o tener copiada en el portapapeles una URL válida de una lista de reproducción de YouTube.

### d: (download video/audio)

Este comando abre un pequeño cuadro de diálogo que pregunta si deseas descargar el video o solo el audio. Puedes configurar el destino de la descarga, y ajustar la calidad/formato con más detalle, en la sección de [Configuración](#configuración).

**Las descargas de video requieren FFmpeg.** YouTube ya no ofrece la mayoría de los videos como un único archivo combinado de video y audio, por lo que combinar las transmisiones por separado requiere FFmpeg. YoutubePlus no incluye FFmpeg (para evitar que el complemento infle innecesariamente la configuración de NVDA de cada usuario) — si no se encuentra FFmpeg en tu sistema al descargar un video, y la herramienta `winget` de Windows está disponible, YoutubePlus te ofrecerá instalarlo automáticamente con una simple pregunta de Sí/No; una vez instalado, tu descarga continuará automáticamente sin necesidad de reiniciar NVDA. Si no se encuentra ni FFmpeg ni `winget`, se te informará y la descarga se cancelará de forma limpia.

Las descargas de solo audio no necesitan FFmpeg de forma predeterminada. Solo se requiere si has elegido un formato de audio distinto de "Best available (no conversion)" en las opciones avanzadas de formato descritas abajo, ya que convertir a otro formato de audio también pasa por FFmpeg.

Ten en cuenta que la función de descarga se ofrece como una comodidad y puede tener limitaciones si se usa intensamente. Si necesitas descargar grandes cantidades de contenido de YouTube, se recomiendan otras herramientas dedicadas a esta función.

### e: (search)

Este comando abre una ventana de búsqueda de YouTube. Escribe tu consulta en el campo de búsqueda y presiona Enter para buscar de inmediato. También puedes usar Tab para ajustar la cantidad de resultados a mostrar — el complemento recuerda este valor para búsquedas futuras.

El campo de búsqueda es un cuadro combinado que recuerda tus búsquedas anteriores: presiona la flecha abajo (o Alt+Abajo) para desplegar una lista de palabras clave anteriores y elegir una en lugar de volver a escribirla.

Los resultados se muestran en el mismo formato de [lista de videos](#lista-de-videos) usado en todo el complemento, no como una página web de YouTube. Puedes acceder a todos los detalles del video de la misma forma que en cualquier otra lista de videos del complemento.

#### q: (quick search)

Una alternativa más rápida al diálogo de búsqueda anterior. Selecciona algún texto en cualquier aplicación (o ten una consulta copiada en el portapapeles si no hay nada seleccionado), luego presiona Q en la capa de YoutubePlus. El complemento busca en YouTube de inmediato usando ese texto y la cantidad de resultados guardada de tu última búsqueda — sin diálogo, sin pulsaciones de tecla adicionales.

#### Historial de búsqueda

Cada búsqueda que realizas — ya sea desde el diálogo de búsqueda o la búsqueda rápida — se guarda automáticamente. Presiona **Control+H** en la capa de YoutubePlus para ir directamente a la pestaña de Historial de Búsqueda en la ventana de Favoritos, donde puedes:

* Presionar Enter, o el botón **Search Again**, para volver a ejecutar una búsqueda anterior
* Presionar **New Search (Alt+N)** para abrir el diálogo de búsqueda
* Presionar Delete, o el botón **Remove**, para eliminar una entrada individual
* Presionar el botón **Clear All** para borrar todo el historial

### i: (video info)

Muestra los siguientes detalles del video actual:

* Título
* Canal
* Duración
* Fecha de subida
* Visualizaciones
* Me gusta
* Comentarios
* Descripción

### t: (timestamp / chapter)

Muestra la lista de marcas de tiempo o capítulos del video (si el creador incluyó esta información). Si el complemento indica "No chapters found in this video," el video simplemente no tiene datos de capítulos.

Esta ventana ofrece más comodidad que leer los capítulos desde el navegador:

* Un campo de búsqueda para filtrar la lista de marcas de tiempo/capítulos — los resultados se actualizan al instante sin presionar Enter
* La lista completa se muestra con la descripción de cada sección primero, seguida de su posición temporal
* Un área de texto de solo lectura para leer descripciones largas de capítulos
* Un botón "Open Chapter" — o presiona Espacio o Enter — para saltar directamente a ese capítulo en el video
* Botón Copy Title (Alt+C) para copiar el nombre del capítulo
* Botón Copy URL (Alt+U) para copiar la URL con la marca de tiempo de ese capítulo
* Botón Export (Alt+E) para guardar todos los datos de marcas de tiempo/capítulos como un archivo de texto

### g: (get thumbnail description)

Descarga una imagen y la envía a la aplicación **Be My Eyes** para obtener una descripción en vivo, sin salir de NVDA. Este comando se adapta al contexto: describe la miniatura del video cuando estás en una página de video, el avatar del canal cuando estás en una página de canal, y la portada de la lista de reproducción cuando estás en una página de lista de reproducción — usando el mismo orden de detección de URL que el resto de comandos (primero la ventana del navegador activa, luego el portapapeles). También está disponible desde el menú Action del video (solo miniaturas de video) y como una Quick Action configurable (barra espaciadora).

El complemento siempre elige la imagen de mayor resolución que reporta yt-dlp, para que el archivo enviado a Be My Eyes sea siempre el mejor disponible.

También puedes describir el avatar de un canal o la portada de una lista de reproducción directamente desde la ventana de Favoritos, sin necesidad de tener esa página abierta — consulta los botones **Describe Avatar** y **Describe Cover** en [Favoritos](#favoritos) más abajo.

**Nota:** Esta función requiere que la aplicación [Be My Eyes](https://www.bemyeyes.com/) esté instalada por separado en tu sistema — el complemento no la instala ni la incluye. Si no está instalada, YoutubePlus te ofrecerá abrir su página en la Microsoft Store para que puedas instalarla al instante.

### Favoritos

Una ventana que muestra tus favoritos guardados, dividida en 5 pestañas por tipo:

* **Video:** Enumera tus videos guardados, organizados en categorías creadas por ti. Un árbol de categorías se ubica a la izquierda y la lista de videos de la categoría seleccionada a la derecha (ver [Categorías](#categorías-pestañas-video-y-lista-de-seguimiento) abajo). Incluye botones de Action y Copy para cada elemento (descritos abajo).
* **Channel:** Enumera tus canales guardados con un panel de descripción del canal. Incluye botones para abrir el canal, explorar su contenido por tipo, y describir su avatar mediante Be My Eyes (Alt+D).
* **Playlist:** Enumera tus listas de reproducción guardadas. Presiona Espacio, Enter o Alt+V para expandir todos los videos de una lista de reproducción. Incluye un botón Open on Web (Alt+W) y un botón Describe Cover (Alt+D) para obtener una descripción de Be My Eyes de la imagen de portada de la lista de reproducción.
* **Watch List:** Enumera tus videos guardados usando el mismo diseño de árbol de categorías + lista que la pestaña Video, con su propio conjunto independiente de categorías.
* **Search History:** Enumera cada búsqueda que has realizado, con opciones para volver a ejecutarla, eliminarla o borrar las entradas (ver [Historial de búsqueda](#historial-de-búsqueda) arriba).

#### Comandos de la ventana de Favoritos

* Presiona Control+1 a Control+5 para cambiar entre pestañas
* Presiona Control+Arriba/Abajo para reordenar pestañas
* Presiona Control+C (copiar), Control+X (cortar), o Control+V (pegar) para reordenar elementos
    * Favorite Videos y Watch List admiten copiar y mover elementos entre sí, incluyendo elementos dentro de una categoría. Las pestañas Video y Watch List mantienen cada una su propia lista de categorías separada, así que cuando un elemento se mueve entre ellas, se coloca en la categoría que esté seleccionada actualmente en la pestaña de destino. Favorite Channels y Playlists solo admiten mover elementos dentro de su propia lista.
* Presiona Alt+R o Delete para eliminar un elemento
* Presiona Alt+N para añadir un nuevo elemento desde el portapapeles — para las pestañas de canal y lista de reproducción, la URL debe coincidir con el tipo de pestaña
* Presiona **Alt+O (Sort...)** para abrir el diálogo de ordenación de la pestaña actual — ver [Ordenación](#ordenación) abajo
* El campo de búsqueda filtra los resultados al instante mientras escribes — no es necesario presionar Enter

#### Categorías (pestañas Video y Lista de Seguimiento)

Tanto la pestaña Video como la de Lista de Seguimiento te permiten organizar elementos en categorías propias, usando una vista de árbol a la izquierda, separada de la lista de elementos a la derecha. Cada pestaña mantiene sus propias categorías — crear una categoría en una no afecta a la otra. Siempre hay un nodo predeterminado para elementos sin categoría ("Videos" en la pestaña Video, "Watch List" en la pestaña Lista de Seguimiento).

Con el foco en el árbol de categorías:

* Presiona **Control+=** para añadir una nueva categoría
* Presiona **F2** para renombrar la categoría seleccionada
* Presiona **Delete** para eliminar la categoría seleccionada — si todavía contiene elementos, se te preguntará si deseas moverlos al nodo predeterminado o eliminarlos junto con la categoría
* Presiona **Control+Mayús+Arriba** / **Control+Mayús+Abajo** para reordenar la categoría seleccionada
* Presiona Enter, o Tab, para mover el foco a la lista de elementos de esa categoría
* Haz clic derecho, o presiona la tecla Aplicación/Menú, para un menú contextual — su contenido depende de lo que esté seleccionado: un nodo de categoría muestra opciones de gestión de categorías (Añadir/Renombrar/Eliminar/Mover), mientras que el nodo predeterminado solo muestra Add Category

Con el foco en la lista de elementos (lado derecho), haz clic derecho o presiona la tecla Aplicación/Menú para el mismo menú Action usado en todo el complemento (View Info, Comments, Download, Add to..., etc.) — separado del menú contextual de categorías del árbol.

Cortar, Copiar y Pegar en la lista de elementos funcionan como se describió arriba, y pegar siempre coloca los elementos en la categoría que esté seleccionada actualmente en el árbol.

#### Ordenación

El botón **Sort... (Alt+O)** está disponible en cualquier pestaña con una lista ordenable — incluyendo Video, Watch List, y Search History. Abre un diálogo con:

* **Sort by:** el campo por el cual ordenar (Title, Channel, Duration, Upload Date, Date Added — los campos varían ligeramente según la pestaña)
* **Ascending / Descending**
* **Sort only the current category:** cuando está activado, la ordenación solo reordena los elementos dentro de la categoría actualmente seleccionada en el árbol, dejando intactas todas las demás categorías. Desactivado de forma predeterminada, lo que significa que la ordenación se aplica a todas las categorías a la vez.
* **Apply permanently (saves to file):** cuando está activado, el nuevo orden se escribe en el disco de inmediato. Cuando está desactivado, la ordenación es temporal — cambia lo que ves en este momento, pero se revierte la próxima vez que la lista se recargue o busques algo.
* **Clear Sort:** descarta cualquier ordenación temporal y restaura el orden guardado en el disco.

#### Lista de videos

En las pestañas de video y lista de seguimiento, así como en cualquier otra vista que muestre una lista de videos, encontrarás los botones **Action...** y **Copy...**. Estos son controles estándar en todas las vistas de listas de videos, y el feed de suscripciones añade una opción adicional de "Unsubscribe from this channel".

Presiona Enter en cualquier elemento para abrir el video en tu navegador, o presiona la barra espaciadora para ejecutar la Quick Action que puedes configurar desde [Configuración](#configuración).

##### Botón Action

Presiona Alt+A para abrir el menú Action, que incluye:

* View Video Info... (i)
* View Comments / Replay... (c)
* View Chapters/Timestamps... (t)
* Get Thumbnail Description (Be My Eyes)... (g)
* Download Video (d)
* Download Audio (a)
* Add to Favorite Videos (f)
* Add to Favorite Channels (f)
* Add to Watch List (w)
* Open video in browser (b)
* Open channel in browser (h)
* Show channel videos (v)
* Show channel shorts (s)
* Show channel live (l)
* Show channel playlist (l)
* Show channel podcast (p)

##### Botón Copy

Presiona Alt+C para abrir el menú Copy, que incluye:

* Copy Title (t)
* Copy Video URL (u)
* Copy Channel Name (c)
* Copy Channel URL (h)
* Copy Summary (s)

### Feed de suscripciones

Una ventana que muestra videos de los canales que sigues dentro del complemento. Esto es independiente de las suscripciones de tu cuenta de YouTube — no se requiere vincular ninguna cuenta ni datos personales.

A diferencia de la ventana de Favoritos, esta vista usa pestañas estándar divididas por tipo de contenido:

* **All:** Todos los tipos de contenido combinados
* **Video:** Solo videos normales
* **Shorts:** Solo videos cortos
* **Live:** Transmisiones en vivo y repeticiones de transmisiones en vivo

Además de estas categorías predeterminadas, puedes crear categorías personalizadas y configurar qué canales aparecen en cada una.

#### Comandos del feed de suscripciones

* Presiona Control+1 a Control+0 para saltar a una pestaña de categoría (hasta 10 categorías)
* Presiona Control+Arriba/Abajo para reordenar categorías, igual que en la ventana de Favoritos
* Presiona F2 para renombrar una categoría (excepto las 4 categorías predeterminadas)
* Presiona Control+= para añadir una nueva categoría
* Presiona Control+- para eliminar una categoría (excepto las 4 categorías predeterminadas)
* Accede a los botones Action y Copy de cada video, o presiona Enter para abrirlo en un navegador
* Presiona Delete o Alt+S para marcar un video como visto — se eliminará de la lista
* Presiona Control+Delete para marcar todos los videos de la pestaña actual como vistos

Botones adicionales en esta ventana:

* **Mark as seen (Alt+S)** — elimina el video de la lista; la tecla Delete también funciona
* **Add new Subscription from clipboard URL (Alt+N)** — se suscribe a un canal usando la URL copiada en el portapapeles
* **Update Feed (Alt+U)** — activa manualmente una actualización para todos los canales suscritos; el complemento también se actualiza automáticamente al iniciar NVDA de forma predeterminada
* **More... (Alt+M)** — abre un submenú con opciones adicionales:
    * Mark all in current tab as seen (Ctrl+Delete) (a)
    * Show all videos (including seen) (v) — alterna entre mostrar solo los no vistos y mostrar todos los videos; la configuración se guarda automáticamente
    * Manage subscriptions... (m)
    * Add New Category... Ctrl+= (c)
    * Rename Current Category... F2 (r)
    * Remove Current Category... Ctrl+-
    * Clear All Feed Videos... — elimina todos los videos de la base de datos sin eliminar tus suscripciones; útil si la base de datos crece demasiado y afecta el rendimiento de NVDA

### Gestionar suscripciones

Esta ventana muestra todos los canales a los que estás suscrito. La primera sección es la lista de canales, seguida de opciones de gestión para cada canal:

* **Filter by Category** — filtra la lista de canales por categoría; por defecto es "All"
* **Assign to Categories** — elige en qué categorías debe aparecer el contenido de este canal
* **Content Types to Fetch** — elige qué tipos de contenido actualizar para este canal (Videos, Shorts, Live); útil para canales que solo publican ciertos tipos
* **View Content... (Alt+C)** — explora el contenido del canal, igual que el botón Action
* **Add new subscribe channel from Clipboard... (Alt+N)** — se suscribe a un nuevo canal usando la URL del portapapeles
* **Unsubscribe from this Channel (Alt+U)** — elimina el canal de tus suscripciones
* **Save Changes** — **importante:** debes presionar esto antes de cerrar la ventana, o tus cambios no se guardarán

### Administrador de perfiles de usuario

Esta ventana gestiona tus perfiles de usuario. El complemento viene con un perfil "default". Puedes añadir, eliminar o renombrar perfiles aquí. Para cambiar entre perfiles, ve al panel de Configuración del complemento.

En esta ventana:

* Presiona F2 para renombrar el perfil seleccionado
* Presiona Delete para eliminar el perfil seleccionado

**Nota:** Eliminar un perfil borra permanentemente todos los datos asociados con él. Cualquier video, canal o suscripción guardados en ese perfil se perderán.

### l: (show comments)

Hay tres tipos de comentarios en los videos de YouTube:

* **Comment** — comentarios estándar de espectadores en videos normales
* **Live chat** — mensajes enviados durante una transmisión en vivo
* **Live chat replay** — el chat en vivo grabado de un video que se transmitió anteriormente, si el dueño del canal no lo ha eliminado

YoutubePlus admite el acceso a los tres tipos a través de este comando.

#### Live chat of...

Para videos actualmente en vivo, presiona L y el complemento abrirá una nueva ventana mostrando los mensajes del chat entrantes. Solo se muestran los mensajes recibidos después de activar el comando — los mensajes anteriores no se capturan.

Puedes cerrar esta ventana y volver a abrirla más tarde con el comando V en la capa de YoutubePlus, siempre que la transmisión siga activa y no se haya reiniciado NVDA.

Usa el comando R para alternar si NVDA lee los mensajes nuevos en voz alta a medida que llegan. Esto funciona bien para transmisiones con mensajes poco frecuentes. Para transmisiones con mucho volumen, puede ser más fácil desactivar la lectura automática y desplazarte por la ventana manualmente.

Presiona Shift+L para detener el monitoreo del chat del video actual.

Tres configuraciones afectan directamente esta función:

- **Automatically speak incoming live chat:** cuando está activado, NVDA lee los mensajes nuevos en voz alta de inmediato — la misma función que el comando R, pero guardada como preferencia predeterminada.
- **Live chat refresh interval:** con qué frecuencia (en segundos) el complemento revisa si hay mensajes nuevos. El valor predeterminado es 5 segundos.
- **Message history limit:** el número máximo de mensajes almacenados en memoria durante una sesión. La ventana de chat en vivo solo muestra los mensajes más recientes hasta este límite (predeterminado: 5,000). El complemento conserva todos los mensajes en segundo plano para exportación, hasta un máximo de 200,000, para evitar un uso excesivo de memoria.

Cuando una transmisión termina — o el complemento detecta que ha terminado — aparecerá automáticamente un diálogo preguntando si deseas exportar todos los mensajes recopilados. Presiona Sí para guardar el historial del chat como archivo.

#### Comments / Live chat replay

Para videos subidos normalmente o transmisiones archivadas, puedes acceder a los comentarios de la misma manera. Si tanto la repetición del chat en vivo como los comentarios estándar están disponibles, un diálogo te preguntará cuál deseas cargar.

No hay límite en la cantidad de comentarios mostrados, aunque la carga puede tardar en videos con muchos comentarios.

Los comentarios se muestran con los comentarios fijados primero, seguidos de todos los demás en el orden de clasificación configurado en Configuración (más recientes primero o más antiguos primero).

#### Secciones de la ventana de comentarios

* **Campo de búsqueda** — escribe para filtrar comentarios; los resultados se actualizan al instante
* **Cuadro combinado de filtro** — selecciona una opción de filtro (el complemento rellena el campo de búsqueda automáticamente):
    * No Filter — predeterminado; muestra todos los comentarios
    * Filter by Selected Author — muestra solo los comentarios del comentarista seleccionado
    * Show Super Chats Only
    * Show Super Stickers Only
    * Show Super Thanks Only
* **Lista de comentarios** — muestra el nombre del comentarista seguido de su mensaje
* **Área de texto de solo lectura** — desplázate por el texto completo del comentario seleccionado, útil cuando un comentario es demasiado largo para mostrarse completo en la lista
* **Botón Copy (Alt+C o Ctrl+C)** — copia el comentario seleccionado
* **Botón Export (Alt+E)** — guarda todos los comentarios como un archivo de texto en la carpeta establecida en Configuración
* **Campo de monto total pagado** — se muestra solo para repeticiones de chat en vivo; muestra el total de donaciones de los espectadores durante la transmisión

## Configuración

Accede a la configuración a través de `NVDA -> Preferencias -> Configuración...` y selecciona la categoría **"YoutubePlus"**.

- **Active Profile:** Selecciona el perfil a usar. Se requiere reiniciar después de cambiar de perfil.
- **Manage Profile button:** Abre la ventana del Administrador de perfiles de usuario.
- **Quick Action (Space bar):** Elige qué hace la tecla Espacio en las ventanas de listas de video. Están disponibles todas las opciones del menú Action.
- **Notification mode:** Elige cómo el complemento señala la actividad en segundo plano:
  - *Beep:* Tonos de pitido cortos
  - *Sound:* Efecto de audio
  - *Silent:* Sin notificación de audio (las respuestas habladas siguen ocurriendo)
- **Default sort order:** Elige si las listas (comentarios, videos del canal) se ordenan **Newest First** o **Oldest First**.
- **Items to fetch:** Cuántos elementos obtener por tipo de contenido al explorar un canal, y para las actualizaciones del feed de suscripciones. Predeterminado: 20.
- **Default content types:** Elige qué tipos de contenido obtener para los canales recién suscritos: Videos, Shorts, y/o Live.
- **Background update interval:** Con qué frecuencia el complemento revisa si hay contenido nuevo de los canales suscritos. Se puede desactivar o configurar de 15 minutos a 24 horas. El complemento también se actualiza automáticamente en cada inicio de NVDA de forma predeterminada.
- **Automatically speak incoming live chat:** cuando está activado, NVDA lee los mensajes de chat nuevos en voz alta a medida que llegan.
- **Live chat refresh interval:** Con qué frecuencia (en segundos) el complemento revisa si hay mensajes nuevos. Predeterminado: 5 segundos.
- **Message history limit:** Número máximo de mensajes de chat almacenados en memoria durante una sesión.
- **Default subtitle format:** Formato de archivo de subtítulos para las descargas: SRT, VTT, TTML, o TXT (texto plano sin marcas de tiempo)
- **Download Quality and Format Options (Alt+D):** Una sección plegable (contraída de forma predeterminada — presiona Alt+D en cualquier parte de la página de Configuración, o actívala directamente, para expandirla/contraerla) que contiene:
  - *Preferred video quality:* La mejor disponible, o un límite de resolución desde 2160p hasta 360p.
  - *Preferred video container:* MP4, MKV o WebM.
  - *Preferred audio quality (when converting):* La mejor disponible, o una tasa de bits desde 320 hasta 96 kbps. Solo aplica cuando el formato de audio de abajo no es "Best available."
  - *Preferred audio format:* Best available (sin conversión, la opción predeterminada — descarga el formato que YouTube ya ofrece, sin necesitar FFmpeg), o convertir a MP3, WAV, M4A/AAC, FLAC, Opus o Vorbis (OGG) — cualquiera de estas conversiones requiere FFmpeg, igual que las descargas de video.
- **Cookie method (Experimental):** Selecciona el navegador en el que tienes la sesión iniciada en YouTube. El complemento extraerá las cookies de ese navegador para autenticar las solicitudes, lo que puede ayudar a resolver el error "Sign in to confirm you're not a bot". Ten en cuenta que esta función es experimental y los resultados varían según el navegador y la configuración del sistema.
- **Default download and export folder path:** La carpeta de destino para los videos/audio descargados y el chat exportado.
- **Backup data now:** Respalda manualmente todos los datos del perfil activo. El complemento también realiza una copia de seguridad diaria automática en segundo plano.
- **Restore data from backup:** Muestra una lista de las copias de seguridad disponibles (hasta los últimos 5 días) para que puedas elegir desde qué fecha restaurar.

## Información adicional

Este complemento depende de dos bibliotecas principales: [pytchat](https://pypi.org/project/pytchat/) para el monitoreo del chat en vivo, y [yt-dlp](https://pypi.org/project/yt-dlp/) para todo el resto del acceso a datos de YouTube. Extendemos nuestro sincero agradecimiento a los desarrolladores de ambas bibliotecas.

### Sobre yt-dlp

[yt-dlp](https://github.com/yt-dlp/yt-dlp) es una de las herramientas de código abierto más poderosas para descargar video y audio de sitios web de todo el mundo — soportando más de 1,000 sitios, no solo YouTube. Es gratuito, de código abierto, y mantenido activamente por una comunidad global, sin anuncios ni malware a diferencia de muchas herramientas de descarga basadas en navegador.

Dicho esto, ten en cuenta las siguientes pautas de uso:

1. **Fair Use:** Evita obtener grandes cantidades de datos o enviar solicitudes repetidas en poco tiempo. YouTube puede detectar actividad inusual y restringir temporalmente el acceso desde tu dirección IP.
2. **Copyright and Privacy:** Cualquier dato o contenido obtenido debe ser solo para visualización o análisis personal. Por favor respeta los Términos de Servicio de cada plataforma y no uses los datos de manera que infrinja derechos de autor.
3. **Responsibility:** Eres responsable de cómo uses este software. El desarrollador del complemento solo proporciona la interfaz para acceder a los datos de YouTube a través de la biblioteca yt-dlp.

**Consejo:** Si necesitas procesar grandes cantidades de datos, espacía tus solicitudes para mantener la estabilidad de la conexión y evitar restricciones de acceso.
