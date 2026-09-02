# YoutubePlus for NVDA

> O YoutubePlus é um complemento para pessoas que adoram usar o YouTube, mas acham muitos recursos do site difíceis de acessar — como ler os comentários dos vídeos.
> Trazemos esses recursos para você através da interface de usuário do NVDA, em um formato fácil de navegar, com suporte a atalhos de teclado e totalmente personalizável — sem exigir que você lide com chaves de API ou conecte qualquer conta pessoal ao complemento.
> Você pode seguir seus canais favoritos e ter certeza de que verá todos os vídeos desses canais, sem que o algoritmo do YouTube os filtre.
> Também oferecemos um sistema de Favoritos para vídeos, canais, playlists, e uma lista de reprodução posterior para salvar conteúdo que interessa a você, mas que ainda não teve tempo de assistir.
> Há uma busca de vídeo integrada que exibe os resultados dentro da mesma interface de usuário utilizada em todo o complemento — não apenas uma caixa de busca que abre o YouTube em um navegador.
> Um recurso de download está incluído para salvar vídeos ou arquivos de áudio, embora seja oferecido como uma conveniência e não como o foco principal. Se baixar é sua necessidade principal, existem outros complementos dedicados a esse recurso que você pode querer explorar.
> A única coisa que este complemento não faz é incorporar um player de vídeo. Acreditamos que o player web do YouTube já é acessível o suficiente por si só. Se você ainda achar insuficiente, pode usar outros complementos como o [browserNav](https://addonstore.nvaccess.org/?channel=stable&language=en&apiVersion=2025.3.2&addonId=browsernav) para melhorar a experiência.

## Atalhos de teclado e comandos

Este complemento usa um sistema de atalhos em camadas para evitar conflitos com outros complementos ou comandos do NVDA.
Pressione **NVDA+Y** para entrar no modo de comandos do YoutubePlus e, em seguida, pressione uma das teclas abaixo para acessar cada recurso ou janela.

**Nota:** Se o atalho principal (`NVDA+Y`) entrar em conflito com outro complemento, você pode alterá-lo em `NVDA -> Preferências -> Gestos de Entrada...` na categoria "YoutubePlus".

### Teclas disponíveis na camada do YoutubePlus

* a: (add to...) — Abre um submenu para você escolher onde adicionar o vídeo ou canal atual
* f: (open favorites video) — Abre a janela de vídeos favoritos
* c: (open favorites channel) — Abre a janela de canais favoritos
* p: (open favorites playlist) — Abre a janela de playlists favoritas
* w: (show watch list) — Abre a janela da lista de reprodução posterior
* d: (download) — Pergunta se você deseja baixar como vídeo ou apenas áudio
* e: (search) — Abre a janela de busca de vídeos
* q: (quick search) — Busca no YouTube imediatamente usando o texto atualmente selecionado, ou o conteúdo da área de transferência se nada estiver selecionado — sem abrir a caixa de diálogo de busca primeiro
* control+h: (search history) — Abre a janela de Favoritos diretamente na aba de Histórico de Busca
* i: (info) — Abre a janela de detalhes do vídeo
* t: (show timestamp) — Exibe marcações de tempo ou capítulos, se disponíveis
* g: (get thumbnail description) — Baixa a miniatura do vídeo e a envia ao aplicativo Be My Eyes para obter uma descrição ao vivo
* m: (open manage subscription) — Abre a janela de gerenciamento de inscrições
* s: (open subscription feed) — Mostra vídeos dos canais que você segue
* u: (open User Profile Manager) — Abre a janela de gerenciamento de perfis de usuário
* l: (show comment) — Exibe comentários (detalhes explicados abaixo)
* shift+l: (stop monitor live chat) — Para o monitoramento do chat ao vivo
* r: (toggle automatic reading live chat) — Ativa/desativa a leitura automática das mensagens recebidas do chat ao vivo
* v: (show live chat) — Reabre a janela do chat ao vivo caso você a tenha fechado enquanto a transmissão ainda estava ativa
* y: (open YoutubePlus settings dialog) abre rapidamente as configurações do NVDA e foca na categoria YoutubePlus
* h: (help) — Abre uma janela listando todos os atalhos disponíveis

**Nota:** Para comandos que atuam diretamente sobre um vídeo, o complemento primeiro verifica a janela do navegador aberta. Se uma página de vídeo do YouTube estiver ativa, ele usa a URL desse vídeo. Se nenhuma página de vídeo estiver aberta, ele verifica a área de transferência em busca de uma URL do YouTube.

## Detalhes de recursos e comandos

### a: (add to...)

Este comando na camada do YoutubePlus envia informações do vídeo ou canal para o destino selecionado:

* Add to Favorite Videos (v)
* Add to Favorite Channels (c)
* Add to Favorite Playlist (p)
* Subscribe to Channel (s)
* Add to Watch List (w)

O complemento primeiro verifica a página do navegador aberta atualmente. Se for uma página de vídeo do YouTube, ele extrai a URL e a processa de acordo com sua seleção. Se a página não for um vídeo do YouTube ou nenhum navegador estiver aberto, ele verifica a área de transferência em busca de uma URL do YouTube.

A maioria dos comandos funciona com qualquer tipo de URL do YouTube, já que o complemento consegue derivar as informações necessárias. Por exemplo, se você estiver em uma página de vídeo e escolher "Add to Favorite Channels", o complemento pode extrair automaticamente a URL do canal. O mesmo se aplica para se inscrever em um canal.

A única exceção são as playlists — você precisa ter uma página de playlist do YouTube aberta, ou uma URL válida de playlist do YouTube copiada na área de transferência.

### d: (download video/audio)

Este comando abre uma pequena caixa de diálogo perguntando se você deseja baixar o vídeo ou apenas o áudio. Você pode definir o destino do download, e ajustar a qualidade/formato com mais detalhes, na seção de [Configurações](#configurações).

**Downloads de vídeo exigem o FFmpeg.** O YouTube não oferece mais a maioria dos vídeos como um único arquivo combinado de vídeo e áudio, então mesclar os fluxos separados exige o FFmpeg. O YoutubePlus não inclui o FFmpeg junto (para evitar inchar desnecessariamente a configuração do NVDA de cada usuário) — se o FFmpeg não for encontrado no seu sistema ao baixar um vídeo, e a ferramenta `winget` do Windows estiver disponível, o YoutubePlus vai oferecer para instalá-lo automaticamente com uma simples pergunta de Sim/Não; depois de instalado, seu download continua automaticamente, sem precisar reiniciar o NVDA. Se nem o FFmpeg nem o `winget` estiverem disponíveis, você será avisado e o download será cancelado de forma limpa.

Downloads somente de áudio não precisam do FFmpeg por padrão. Ele só é necessário se você tiver escolhido um formato de áudio diferente de "Best available (no conversion)" nas opções avançadas de formato abaixo, já que converter para outro formato de áudio também passa pelo FFmpeg.

Note que o recurso de download é oferecido por conveniência e pode ter limitações se usado intensamente. Se você precisar baixar grandes quantidades de conteúdo do YouTube, outras ferramentas dedicadas são recomendadas.

### e: (search)

Este comando abre uma janela de busca do YouTube. Digite sua consulta no campo de busca e pressione Enter para buscar imediatamente. Você também pode usar Tab para ajustar o número de resultados a exibir — o complemento lembra esse valor para buscas futuras.

O campo de busca é uma caixa de combinação que lembra suas buscas anteriores: pressione a seta para baixo (ou Alt+Baixo) para abrir uma lista de palavras-chave anteriores e escolher uma em vez de digitá-la novamente.

Os resultados são exibidos no mesmo formato de [lista de vídeos](#lista-de-vídeos) usado em todo o complemento, não como uma página web do YouTube. Você pode acessar todos os detalhes do vídeo da mesma forma que em qualquer outra lista de vídeos do complemento.

#### q: (quick search)

Uma alternativa mais rápida à caixa de diálogo de busca acima. Selecione algum texto em qualquer aplicativo (ou tenha uma consulta copiada na área de transferência se nada estiver selecionado), depois pressione Q na camada do YoutubePlus. O complemento busca no YouTube imediatamente usando esse texto e o número de resultados salvo da sua última busca — sem diálogo, sem pressionamentos de tecla extras.

#### Histórico de Busca

Toda busca que você faz — seja pela caixa de diálogo de busca ou pela busca rápida — é salva automaticamente. Pressione **Control+H** na camada do YoutubePlus para ir direto à aba de Histórico de Busca na janela de Favoritos, onde você pode:

* Pressionar Enter, ou o botão **Search Again**, para executar novamente uma busca anterior
* Pressionar **New Search (Alt+N)** para abrir a caixa de diálogo de busca
* Pressionar Delete, ou o botão **Remove**, para remover uma única entrada
* Pressionar o botão **Clear All** para limpar todo o histórico

### i: (video info)

Exibe os seguintes detalhes do vídeo atual:

* Título
* Canal
* Duração
* Data de upload
* Visualizações
* Curtidas
* Comentários
* Descrição

### t: (timestamp / chapter)

Exibe a lista de marcações de tempo ou capítulos do vídeo (se o criador incluiu essa informação). Se o complemento informar "No chapters found in this video", o vídeo simplesmente não possui dados de capítulos.

Esta janela oferece mais conveniência do que ler os capítulos pelo navegador:

* Um campo de busca para filtrar a lista de marcações de tempo/capítulos — os resultados são atualizados instantaneamente sem pressionar Enter
* A lista completa exibida com a descrição de cada seção primeiro, seguida de sua posição no tempo
* Uma área de texto somente leitura para ler descrições longas de capítulos
* Um botão "Open Chapter" — ou pressione Espaço ou Enter — para pular diretamente para aquele capítulo no vídeo
* Botão Copy Title (Alt+C) para copiar o nome do capítulo
* Botão Copy URL (Alt+U) para copiar a URL com a marcação de tempo daquele capítulo
* Botão Export (Alt+E) para salvar todos os dados de marcação de tempo/capítulos como um arquivo de texto

### g: (get thumbnail description)

Baixa uma imagem e a envia ao aplicativo **Be My Eyes** para obter uma descrição ao vivo, sem sair do NVDA. Este comando se adapta ao contexto: descreve a miniatura do vídeo quando você está em uma página de vídeo, o avatar do canal quando está em uma página de canal, e a capa da playlist quando está em uma página de playlist — usando a mesma ordem de detecção de URL dos demais comandos (primeiro a janela do navegador ativa, depois a área de transferência). Também disponível no menu Action do vídeo (Alt+A, apenas miniaturas de vídeo) e como uma Quick Action configurável (Barra de espaço).

O complemento sempre escolhe a imagem de maior resolução relatada pelo yt-dlp, garantindo que o arquivo enviado ao Be My Eyes seja sempre o melhor disponível.

Você também pode descrever o avatar de um canal ou a capa de uma playlist diretamente pela janela de Favoritos, sem precisar ter essa página aberta em lugar nenhum — veja os botões **Describe Avatar** e **Describe Cover** em [Favoritos](#favoritos) mais abaixo.

**Nota:** Este recurso requer que o aplicativo [Be My Eyes](https://www.bemyeyes.com/) esteja instalado separadamente no seu sistema — o complemento não o instala nem o inclui. Se ele não estiver instalado, o YoutubePlus vai oferecer para abrir a página dele na Microsoft Store, para que você possa instalá-lo na hora.

### Favoritos

Uma janela exibindo seus favoritos salvos, divididos em 5 abas por tipo:

* **Video:** Lista seus vídeos salvos, organizados em categorias criadas por você. Uma árvore de categorias fica à esquerda e a lista de vídeos da categoria selecionada fica à direita (veja [Categorias](#categorias-abas-vídeo-e-lista-de-reprodução-posterior) abaixo). Inclui botões de Action e Copy para cada item (descritos abaixo).
* **Channel:** Lista seus canais salvos com um painel de descrição do canal. Inclui botões para abrir o canal, navegar pelo seu conteúdo por tipo, e descrever seu avatar via Be My Eyes (Alt+D).
* **Playlist:** Lista suas playlists salvas. Pressione Espaço, Enter ou Alt+V para expandir todos os vídeos de uma playlist. Inclui um botão Open on Web (Alt+W) e um botão Describe Cover (Alt+D) para obter uma descrição de Be My Eyes da imagem de capa da playlist.
* **Watch List:** Lista seus vídeos salvos usando o mesmo layout de árvore de categorias + lista da aba Video, com seu próprio conjunto independente de categorias.
* **Search History:** Lista cada busca que você já fez, com opções para executar novamente, remover ou limpar entradas (veja [Histórico de Busca](#histórico-de-busca) acima).

#### Comandos da janela de Favoritos

* Pressione Control+1 a Control+5 para alternar entre abas
* Pressione Control+Cima/Baixo para reordenar abas
* Pressione Control+C (copiar), Control+X (recortar), ou Control+V (colar) para reordenar itens
    * Favorite Videos e Watch List oferecem suporte a copiar e mover itens entre si, incluindo itens dentro de uma categoria. As abas Video e Watch List mantêm cada uma sua própria lista de categorias separada, então quando um item se move entre elas, ele é colocado na categoria atualmente selecionada na aba de destino. Favorite Channels e Playlists só oferecem suporte a mover itens dentro de sua própria lista.
* Pressione Alt+R ou Delete para remover um item
* Pressione Alt+N para adicionar um novo item da área de transferência — para as abas de canal e playlist, a URL deve corresponder ao tipo da aba
* Pressione **Alt+O (Sort...)** para abrir a caixa de diálogo de ordenação da aba atual — veja [Ordenação](#ordenação) abaixo
* O campo de busca filtra os resultados instantaneamente enquanto você digita — não é necessário pressionar Enter

#### Categorias (abas Vídeo e Lista de Reprodução Posterior)

Tanto a aba Video quanto a de Lista de Reprodução Posterior permitem organizar itens em categorias próprias, usando uma visualização em árvore à esquerda, separada da lista de itens à direita. Cada aba mantém suas próprias categorias — criar uma categoria em uma não afeta a outra. Sempre há um nó padrão para itens sem categoria ("Videos" na aba Video, "Watch List" na aba Lista de Reprodução Posterior).

Com o foco na árvore de categorias:

* Pressione **Control+=** para adicionar uma nova categoria
* Pressione **F2** para renomear a categoria selecionada
* Pressione **Delete** para remover a categoria selecionada — se ela ainda contiver itens, você será perguntado se deseja movê-los para o nó padrão ou excluí-los junto com a categoria
* Pressione **Control+Shift+Cima** / **Control+Shift+Baixo** para reordenar a categoria selecionada
* Pressione Enter, ou Tab, para mover o foco para a lista de itens daquela categoria
* Clique com o botão direito, ou pressione a tecla Aplicativo/Menu, para um menu de contexto — seu conteúdo depende do que está selecionado: um nó de categoria mostra opções de gerenciamento de categoria (Adicionar/Renomear/Excluir/Mover), enquanto o nó padrão mostra apenas Add Category

Com o foco na lista de itens (lado direito), clique com o botão direito ou pressione a tecla Aplicativo/Menu para o mesmo menu Action usado em todo o complemento (View Info, Comments, Download, Add to..., etc.) — separado do menu de contexto de categoria da árvore.

Recortar, Copiar e Colar na lista de itens funcionam conforme descrito acima, e colar sempre coloca os itens na categoria atualmente selecionada na árvore.

#### Ordenação

O botão **Sort... (Alt+O)** está disponível em qualquer aba com uma lista ordenável — incluindo Video, Watch List, e Search History. Ele abre uma caixa de diálogo com:

* **Sort by:** o campo pelo qual ordenar (Title, Channel, Duration, Upload Date, Date Added — os campos variam ligeiramente por aba)
* **Ascending / Descending**
* **Sort only the current category:** quando marcado, a ordenação reordena apenas os itens dentro da categoria atualmente selecionada na árvore, deixando todas as outras categorias intocadas. Desmarcado por padrão, o que significa que a ordenação se aplica a todas as categorias de uma vez.
* **Apply permanently (saves to file):** quando marcado, a nova ordem é gravada no disco imediatamente. Quando desmarcado, a ordenação é temporária — ela muda o que você vê agora, mas volta ao normal na próxima vez que a lista for recarregada ou você buscar algo.
* **Clear Sort:** descarta qualquer ordenação temporária e restaura a ordem salva no disco.

#### Lista de vídeos

Nas abas de vídeo e lista de reprodução posterior, assim como em qualquer outra visualização que mostre uma lista de vídeos, você encontrará os botões **Action...** e **Copy...**. Esses são controles padrão em todas as visualizações de lista de vídeos, com o feed de inscrições adicionando uma opção extra de "Unsubscribe from this channel".

Pressione Enter em qualquer item para abrir o vídeo no seu navegador, ou pressione a barra de espaço para executar a Quick Action que você pode definir em [Configurações](#configurações).

##### Botão Action

Pressione Alt+A para abrir o menu Action, que inclui:

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

##### Botão Copy

Pressione Alt+C para abrir o menu Copy, que inclui:

* Copy Title (t)
* Copy Video URL (u)
* Copy Channel Name (c)
* Copy Channel URL (h)
* Copy Summary (s)

### Feed de inscrições

Uma janela exibindo vídeos dos canais que você segue dentro do complemento. Isso é independente das inscrições da sua conta do YouTube — nenhuma vinculação de conta ou dado pessoal é necessário.

Diferente da janela de Favoritos, esta visualização usa abas padrão divididas por tipo de conteúdo:

* **All:** Todos os tipos de conteúdo combinados
* **Video:** Apenas vídeos normais
* **Shorts:** Apenas vídeos curtos
* **Live:** Transmissões ao vivo e repetições de transmissões ao vivo

Além dessas categorias padrão, você pode criar categorias personalizadas e configurar quais canais aparecem em cada uma.

#### Comandos do feed de inscrições

* Pressione Control+1 a Control+0 para pular para uma aba de categoria (até 10 categorias)
* Pressione Control+Cima/Baixo para reordenar categorias, assim como na janela de Favoritos
* Pressione F2 para renomear uma categoria (exceto as 4 categorias padrão)
* Pressione Control+= para adicionar uma nova categoria
* Pressione Control+- para remover uma categoria (exceto as 4 categorias padrão)
* Acesse os botões Action e Copy de cada vídeo, ou pressione Enter para abri-lo em um navegador
* Pressione Delete ou Alt+S para marcar um vídeo como visto — ele será removido da lista
* Pressione Control+Delete para marcar todos os vídeos da aba atual como vistos

Botões adicionais nesta janela:

* **Mark as seen (Alt+S)** — remove o vídeo da lista; a tecla Delete também funciona
* **Add new Subscription from clipboard URL (Alt+N)** — inscreve-se em um canal usando a URL copiada na área de transferência
* **Update Feed (Alt+U)** — dispara manualmente uma atualização para todos os canais inscritos; o complemento também se atualiza automaticamente ao iniciar o NVDA por padrão
* **More... (Alt+M)** — abre um submenu com opções adicionais:
    * Mark all in current tab as seen (Ctrl+Delete) (a)
    * Show all videos (including seen) (v) — alterna entre mostrar apenas os não vistos e mostrar todos os vídeos; a configuração é salva automaticamente
    * Manage subscriptions... (m)
    * Add New Category... Ctrl+= (c)
    * Rename Current Category... F2 (r)
    * Remove Current Category... Ctrl+-
    * Clear All Feed Videos... — remove todos os vídeos do banco de dados sem remover suas inscrições; útil se o banco de dados crescer muito e afetar o desempenho do NVDA

### Gerenciar inscrições

Esta janela mostra todos os canais aos quais você está inscrito. A primeira seção é a lista de canais, seguida de opções de gerenciamento para cada canal:

* **Filter by Category** — filtra a lista de canais por categoria; o padrão é "All"
* **Assign to Categories** — escolha em quais categorias o conteúdo deste canal deve aparecer
* **Content Types to Fetch** — escolha quais tipos de conteúdo atualizar para este canal (Videos, Shorts, Live); útil para canais que publicam apenas determinados tipos
* **View Content... (Alt+C)** — navegue pelo conteúdo do canal, igual ao botão Action
* **Add new subscribe channel from Clipboard... (Alt+N)** — inscreva-se em um novo canal usando a URL na área de transferência
* **Unsubscribe from this Channel (Alt+U)** — remove o canal das suas inscrições
* **Save Changes** — **importante:** você precisa pressionar este botão antes de fechar a janela, ou suas alterações não serão salvas

### Gerenciador de perfis de usuário

Esta janela gerencia seus perfis de usuário. O complemento vem com um perfil "default". Você pode adicionar, excluir ou renomear perfis aqui. Para alternar entre perfis, vá ao painel de Configurações do complemento.

Nesta janela:

* Pressione F2 para renomear o perfil selecionado
* Pressione Delete para remover o perfil selecionado

**Nota:** Excluir um perfil apaga permanentemente todos os dados associados a ele. Quaisquer vídeos, canais ou inscrições salvos naquele perfil serão perdidos.

### l: (show comments)

Existem três tipos de comentários em vídeos do YouTube:

* **Comment** — comentários padrão de espectadores em vídeos comuns
* **Live chat** — mensagens enviadas durante uma transmissão ao vivo
* **Live chat replay** — o chat ao vivo gravado de um vídeo transmitido anteriormente, caso o dono do canal não o tenha removido

O YoutubePlus oferece acesso aos três tipos através deste comando.

#### Live chat of...

Para vídeos atualmente ao vivo, pressione L e o complemento abrirá uma nova janela exibindo as mensagens de chat recebidas. Somente as mensagens recebidas após você ativar o comando são exibidas — mensagens anteriores não são capturadas.

Você pode fechar esta janela e reabri-la mais tarde com o comando V na camada do YoutubePlus, desde que a transmissão ainda esteja ativa e o NVDA não tenha sido reiniciado.

Use o comando R para alternar se o NVDA lê as novas mensagens em voz alta à medida que chegam. Isso funciona bem para transmissões com mensagens pouco frequentes. Para transmissões de alto volume, pode ser mais fácil desativar a leitura automática e rolar a janela manualmente.

Pressione Shift+L para parar de monitorar o chat do vídeo atual.

Três configurações afetam diretamente este recurso:

- **Automatically speak incoming live chat:** quando marcado, o NVDA lê as novas mensagens em voz alta imediatamente — a mesma função do comando R, mas salva como preferência padrão.
- **Live chat refresh interval:** com que frequência (em segundos) o complemento verifica novas mensagens. O padrão é 5 segundos.
- **Message history limit:** o número máximo de mensagens armazenadas na memória durante uma sessão. A janela de chat ao vivo mostra apenas as mensagens mais recentes até esse limite (padrão: 5.000). O complemento mantém todas as mensagens em segundo plano para exportação, até um máximo de 200.000, para evitar uso excessivo de memória.

Quando uma transmissão termina — ou o complemento detecta que ela terminou — uma caixa de diálogo aparecerá automaticamente perguntando se você deseja exportar todas as mensagens coletadas. Pressione Sim para salvar o histórico do chat como um arquivo.

#### Comments / Live chat replay

Para vídeos enviados normalmente ou transmissões arquivadas, você pode acessar os comentários da mesma forma. Se tanto a repetição do chat ao vivo quanto os comentários padrão estiverem disponíveis, uma caixa de diálogo perguntará qual você deseja carregar.

Não há limite para o número de comentários exibidos, embora o carregamento possa demorar em vídeos com muitos comentários.

Os comentários são exibidos com os comentários fixados primeiro, seguidos de todos os outros na ordem de classificação configurada nas Configurações (mais recentes primeiro ou mais antigos primeiro).

#### Seções da janela de comentários

* **Campo de busca** — digite para filtrar comentários; os resultados são atualizados instantaneamente
* **Caixa de combinação de filtro** — selecione uma opção de filtro (o complemento preenche o campo de busca automaticamente):
    * No Filter — padrão; mostra todos os comentários
    * Filter by Selected Author — mostra apenas comentários do autor selecionado
    * Show Super Chats Only
    * Show Super Stickers Only
    * Show Super Thanks Only
* **Lista de comentários** — mostra o nome do autor seguido de sua mensagem
* **Área de texto somente leitura** — role pelo texto completo do comentário selecionado, útil quando um comentário é longo demais para ser exibido por completo na lista
* **Botão Copy (Alt+C ou Ctrl+C)** — copia o comentário selecionado
* **Botão Export (Alt+E)** — salva todos os comentários como um arquivo de texto na pasta definida nas Configurações
* **Campo de valor total pago** — exibido apenas para repetições de chat ao vivo; mostra o total de doações dos espectadores durante a transmissão

## Configurações

Acesse as configurações em `NVDA -> Preferências -> Configurações...` e selecione a categoria **"YoutubePlus"**.

- **Active Profile:** Selecione o perfil a ser usado. É necessário reiniciar após trocar de perfil.
- **Manage Profile button:** Abre a janela do Gerenciador de Perfis de Usuário.
- **Quick Action (Space bar):** Escolha o que a tecla Espaço faz nas janelas de lista de vídeos. Todas as opções do menu Action estão disponíveis.
- **Notification mode:** Escolha como o complemento sinaliza a atividade em segundo plano:
  - *Beep:* Bipes curtos
  - *Sound:* Efeito sonoro
  - *Silent:* Sem notificação sonora (as respostas faladas continuam ocorrendo)
- **Default sort order:** Escolha se as listas (comentários, vídeos do canal) são ordenadas por **Newest First** ou **Oldest First**.
- **Items to fetch:** Quantos itens obter por tipo de conteúdo ao navegar por um canal, e para atualizações do feed de inscrições. Padrão: 20.
- **Default content types:** Escolha quais tipos de conteúdo buscar para canais recém-inscritos: Videos, Shorts, e/ou Live.
- **Background update interval:** Com que frequência o complemento verifica novo conteúdo dos canais inscritos. Pode ser desativado ou definido de 15 minutos a 24 horas. O complemento também se atualiza automaticamente a cada inicialização do NVDA por padrão.
- **Automatically speak incoming live chat:** quando marcado, o NVDA lê novas mensagens de chat em voz alta à medida que chegam.
- **Live chat refresh interval:** Com que frequência (em segundos) o complemento verifica novas mensagens. Padrão: 5 segundos.
- **Message history limit:** Número máximo de mensagens de chat armazenadas na memória durante uma sessão.
- **Default subtitle format:** Formato do arquivo de legenda para downloads: SRT, VTT, TTML, ou TXT (texto simples sem marcações de tempo)
- **Download Quality and Format Options (Alt+D):** Uma seção recolhível (recolhida por padrão — pressione Alt+D em qualquer lugar da página de Configurações, ou ative-a diretamente, para expandir/recolher) contendo:
  - *Preferred video quality:* A melhor disponível, ou um limite de resolução de 2160p até 360p.
  - *Preferred video container:* MP4, MKV ou WebM.
  - *Preferred audio quality (when converting):* A melhor disponível, ou uma taxa de bits de 320 até 96 kbps. Só se aplica quando o formato de áudio abaixo não é "Best available."
  - *Preferred audio format:* Best available (sem conversão, o padrão — baixa o formato que o YouTube já fornece, sem precisar do FFmpeg), ou converte para MP3, WAV, M4A/AAC, FLAC, Opus ou Vorbis (OGG) — qualquer uma dessas conversões exige o FFmpeg, assim como os downloads de vídeo.
- **Cookie method (Experimental):** Selecione o navegador em que você está conectado ao YouTube. O complemento extrairá os cookies desse navegador para autenticar as solicitações, o que pode ajudar a resolver o erro "Sign in to confirm you're not a bot". Note que este recurso é experimental e os resultados variam conforme o navegador e a configuração do sistema.
- **Default download and export folder path:** A pasta de destino para vídeos/áudio baixados e chat exportado.
- **Backup data now:** Faz backup manual de todos os dados do perfil ativo. O complemento também realiza um backup diário automático em segundo plano.
- **Restore data from backup:** Mostra uma lista de backups disponíveis (até os últimos 5 dias) para você escolher de qual data restaurar.

## Informações adicionais

Este complemento depende de duas bibliotecas principais: [pytchat](https://pypi.org/project/pytchat/) para monitoramento de chat ao vivo, e [yt-dlp](https://pypi.org/project/yt-dlp/) para todo o restante do acesso a dados do YouTube. Estendemos nossos sinceros agradecimentos aos desenvolvedores de ambas as bibliotecas.

### Sobre o yt-dlp

O [yt-dlp](https://github.com/yt-dlp/yt-dlp) é uma das ferramentas de código aberto mais poderosas para baixar vídeo e áudio de sites ao redor do mundo — com suporte a mais de 1.000 sites, não apenas o YouTube. É gratuito, de código aberto, e mantido ativamente por uma comunidade global, sem anúncios ou malware, ao contrário de muitas ferramentas de download baseadas em navegador.

Dito isso, tenha em mente as seguintes diretrizes de uso:

1. **Fair Use:** Evite buscar grandes quantidades de dados ou enviar solicitações repetidas em pouco tempo. O YouTube pode detectar atividade incomum e restringir temporariamente o acesso a partir do seu endereço IP.
2. **Copyright and Privacy:** Qualquer dado ou conteúdo obtido deve ser apenas para visualização ou análise pessoal. Por favor, respeite os Termos de Serviço de cada plataforma e não use os dados de forma que infrinja direitos autorais.
3. **Responsibility:** Você é responsável por como usa este software. O desenvolvedor do complemento fornece apenas a interface para acessar dados do YouTube através da biblioteca yt-dlp.

**Dica:** Se você precisar processar grandes quantidades de dados, espace suas solicitações para manter a estabilidade da conexão e evitar restrições de acesso.
