# YoutubePlus para NVDA

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

* a: (adicionar a...) — Abre um submenu para você escolher onde adicionar o vídeo ou canal atual
* f: (abrir vídeos favoritos) — Abre a janela de vídeos favoritos
* c: (abrir canais favoritos) — Abre a janela de canais favoritos
* p: (abrir playlists favoritas) — Abre a janela de playlists favoritas
* w: (mostrar lista de reprodução posterior) — Abre a janela da lista de reprodução posterior
* d: (baixar) — Pergunta se você deseja baixar como vídeo ou apenas áudio
* e: (buscar) — Abre a janela de busca de vídeos
* q: (busca rápida) — Busca no YouTube imediatamente usando o texto atualmente selecionado, ou o conteúdo da área de transferência se nada estiver selecionado — sem abrir a caixa de diálogo de busca primeiro
* control+h: (histórico de busca) — Abre a janela de Favoritos diretamente na aba de Histórico de Busca
* i: (informações) — Abre a janela de detalhes do vídeo
* t: (mostrar marcações de tempo) — Exibe marcações de tempo ou capítulos, se disponíveis
* g: (obter descrição da miniatura) — Baixa a miniatura do vídeo e a envia ao aplicativo Be My Eyes para obter uma descrição ao vivo
* m: (abrir gerenciamento de inscrições) — Abre a janela de gerenciamento de inscrições
* s: (abrir feed de inscrições) — Mostra vídeos dos canais que você segue
* u: (abrir gerenciador de perfis de usuário) — Abre a janela de gerenciamento de perfis de usuário
* l: (mostrar comentários) — Exibe comentários (detalhes explicados abaixo)
* shift+l: (parar monitoramento do chat ao vivo) — Para o monitoramento do chat ao vivo
* r: (alternar leitura automática do chat ao vivo) — Ativa/desativa a leitura automática das mensagens recebidas do chat ao vivo
* v: (mostrar chat ao vivo) — Reabre a janela do chat ao vivo caso você a tenha fechado enquanto a transmissão ainda estava ativa
* y: (abrir configurações do YoutubePlus) abre rapidamente as configurações do NVDA e foca na categoria YoutubePlus
* h: (ajuda) — Abre uma janela listando todos os atalhos disponíveis

**Nota:** Para comandos que atuam diretamente sobre um vídeo, o complemento primeiro verifica a janela do navegador aberta. Se uma página de vídeo do YouTube estiver ativa, ele usa a URL desse vídeo. Se nenhuma página de vídeo estiver aberta, ele verifica a área de transferência em busca de uma URL do YouTube.

## Detalhes de recursos e comandos

### a: (adicionar a...)

Este comando na camada do YoutubePlus envia informações do vídeo ou canal para o destino selecionado:

* Adicionar aos vídeos favoritos (v)
* Adicionar aos canais favoritos (c)
* Adicionar às playlists favoritas (p)
* Inscrever-se no canal (s)
* Adicionar à lista de reprodução posterior (w)

O complemento primeiro verifica a página do navegador aberta atualmente. Se for uma página de vídeo do YouTube, ele extrai a URL e a processa de acordo com sua seleção. Se a página não for um vídeo do YouTube ou nenhum navegador estiver aberto, ele verifica a área de transferência em busca de uma URL do YouTube.

A maioria dos comandos funciona com qualquer tipo de URL do YouTube, já que o complemento consegue derivar as informações necessárias. Por exemplo, se você estiver em uma página de vídeo e escolher "Adicionar aos canais favoritos", o complemento pode extrair automaticamente a URL do canal. O mesmo se aplica para se inscrever em um canal.

A única exceção são as playlists — você precisa ter uma página de playlist do YouTube aberta, ou uma URL válida de playlist do YouTube copiada na área de transferência.

### d: (baixar vídeo/áudio)

Este comando abre uma pequena caixa de diálogo perguntando se você deseja baixar o vídeo ou apenas o áudio. Você pode definir o destino do download, e ajustar a qualidade/formato com mais detalhes, na seção de [Configurações](#configurações).

**Downloads de vídeo exigem o FFmpeg.** O YouTube não oferece mais a maioria dos vídeos como um único arquivo combinado de vídeo e áudio, então mesclar os fluxos separados exige o FFmpeg. O YoutubePlus não inclui o FFmpeg junto (para evitar inchar desnecessariamente a configuração do NVDA de cada usuário) — se o FFmpeg não for encontrado no seu sistema ao baixar um vídeo, e a ferramenta `winget` do Windows estiver disponível, o YoutubePlus vai oferecer para instalá-lo automaticamente com uma simples pergunta de Sim/Não; depois de instalado, seu download continua automaticamente, sem precisar reiniciar o NVDA. Se nem o FFmpeg nem o `winget` estiverem disponíveis, você será avisado e o download será cancelado de forma limpa.

Downloads somente de áudio não precisam do FFmpeg por padrão. Ele só é necessário se você tiver escolhido um formato de áudio diferente de "Melhor disponível (sem conversão)" nas opções avançadas de formato abaixo, já que converter para outro formato de áudio também passa pelo FFmpeg.

Note que o recurso de download é oferecido por conveniência e pode ter limitações se usado intensamente. Se você precisar baixar grandes quantidades de conteúdo do YouTube, outras ferramentas dedicadas são recomendadas.

### e: (buscar)

Este comando abre uma janela de busca do YouTube. Digite sua consulta no campo de busca e pressione Enter para buscar imediatamente. Você também pode usar Tab para ajustar o número de resultados a exibir — o complemento lembra esse valor para buscas futuras.

O campo de busca é uma caixa de combinação que lembra suas buscas anteriores: pressione a seta para baixo (ou Alt+Baixo) para abrir uma lista de palavras-chave anteriores e escolher uma em vez de digitá-la novamente.

Abaixo do campo de consulta, quatro filtros permitem refinar os resultados, e podem ser combinados livremente (por exemplo, playlists publicadas neste mês, ordenadas por número de visualizações):

* **Tipo de conteúdo:** Vídeos (padrão), Canais, ou Playlists
* **Duração:** Qualquer, Curta (menos de 4 minutos), Média (4-20 minutos), ou Longa (mais de 20 minutos)
* **Data de envio:** Qualquer, Última hora, Hoje, Esta semana, Este mês, ou Este ano
* **Ordenar por:** Relevância (padrão), Data de envio, ou Número de visualizações

Os resultados são exibidos no mesmo formato de [lista de vídeos](#lista-de-vídeos) usado em todo o complemento, não como uma página web do YouTube. Um resultado do tipo Canais abre/copia a URL do canal e exibe um menu Ação reduzido (sem download, comentários, ou outras ações exclusivas de vídeo); um resultado do tipo Playlists se expande na sua própria lista de vídeos, da mesma forma que uma playlist favorita.

#### Buscando dentro de um canal

O campo **Neste canal** restringe a busca aos próprios vídeos de um único canal, em vez de todo o YouTube. Quando definido, os quatro filtros acima não se aplicam à página de busca própria do canal e ficam ocultos.

Comece a digitar o nome de um canal e uma lista suspensa sugere canais do seu Histórico de Busca, Canais favoritos, e Canais inscritos. Se o que você digitou não corresponder a nenhum desses (por exemplo, um canal que você nunca buscou nem favoritou antes), o complemento faz uma busca no YouTube e mostra um seletor para você confirmar qual canal você quis dizer — ele nunca adivinha silenciosamente. Você também pode colar a URL de um canal diretamente, em vez de digitar um nome.

Você também pode abrir esta caixa de diálogo já com um canal pré-preenchido: na aba Canal da janela de Favoritos, selecione um canal e pressione o botão **Buscar neste canal...**.

#### q: (busca rápida)

Uma alternativa mais rápida à caixa de diálogo de busca acima. Selecione algum texto em qualquer aplicativo (ou tenha uma consulta copiada na área de transferência se nada estiver selecionado), depois pressione Q na camada do YoutubePlus. O complemento busca no YouTube imediatamente usando esse texto e o número de resultados salvo da sua última busca — sem diálogo, sem pressionamentos de tecla extras.

#### Histórico de Busca

Toda busca que você faz — seja pela caixa de diálogo de busca ou pela busca rápida — é salva automaticamente, junto com os filtros usados (incluindo um canal definido via "Neste canal"). Pressione **Control+H** na camada do YoutubePlus para ir direto à aba de Histórico de Busca na janela de Favoritos, onde você pode:

* Pressionar Enter, ou o botão **Buscar novamente**, para executar novamente uma busca anterior com exatamente os mesmos filtros (ou o mesmo canal, no caso de uma busca restrita a um canal) — uma entrada restrita a um canal é exibida na lista como "palavra-chave (no Nome do Canal)", para ficar claro à primeira vista
* Pressionar **Nova busca (Alt+N)** para abrir a caixa de diálogo de busca
* Pressionar Delete, ou o botão **Remover**, para remover uma única entrada
* Pressionar o botão **Limpar tudo** para limpar todo o histórico

### i: (informações do vídeo)

Exibe os seguintes detalhes do vídeo atual:

* Título
* Canal
* Duração
* Data de upload
* Visualizações
* Curtidas
* Comentários
* Descrição

### t: (marcação de tempo / capítulo)

Exibe a lista de marcações de tempo ou capítulos do vídeo (se o criador incluiu essa informação). Se o complemento informar "Nenhum capítulo encontrado neste vídeo", o vídeo simplesmente não possui dados de capítulos.

Esta janela oferece mais conveniência do que ler os capítulos pelo navegador:

* Um campo de busca para filtrar a lista de marcações de tempo/capítulos — os resultados são atualizados instantaneamente sem pressionar Enter
* A lista completa exibida com a descrição de cada seção primeiro, seguida de sua posição no tempo
* Uma área de texto somente leitura para ler descrições longas de capítulos
* Um botão "Abrir capítulo" — ou pressione Espaço ou Enter — para pular diretamente para aquele capítulo no vídeo
* Botão Copiar título (Alt+C) para copiar o nome do capítulo
* Botão Copiar URL (Alt+U) para copiar a URL com a marcação de tempo daquele capítulo
* Botão Exportar (Alt+E) para salvar todos os dados de marcação de tempo/capítulos como um arquivo de texto

### g: (obter descrição da miniatura)

Baixa uma imagem e a envia ao aplicativo **Be My Eyes** para obter uma descrição ao vivo, sem sair do NVDA. Este comando se adapta ao contexto: descreve a miniatura do vídeo quando você está em uma página de vídeo, o avatar do canal quando está em uma página de canal, e a capa da playlist quando está em uma página de playlist — usando a mesma ordem de detecção de URL dos demais comandos (primeiro a janela do navegador ativa, depois a área de transferência). Também disponível no menu Ação do vídeo (apenas miniaturas de vídeo) e como uma Ação rápida configurável (Barra de espaço).

O complemento sempre escolhe a imagem de maior resolução relatada pelo yt-dlp, garantindo que o arquivo enviado ao Be My Eyes seja sempre o melhor disponível.

Você também pode descrever o avatar de um canal ou a capa de uma playlist diretamente pela janela de Favoritos, sem precisar ter essa página aberta em lugar nenhum — veja os botões **Descrever avatar** e **Descrever capa** em [Favoritos](#favoritos) mais abaixo.

**Nota:** Este recurso requer que o aplicativo [Be My Eyes](https://www.bemyeyes.com/) esteja instalado separadamente no seu sistema — o complemento não o instala nem o inclui. Se ele não estiver instalado, o YoutubePlus vai oferecer para abrir a página dele na Microsoft Store, para que você possa instalá-lo na hora.

### Favoritos

Uma janela exibindo seus favoritos salvos, divididos em 5 abas por tipo:

* **Vídeo:** Lista seus vídeos salvos, organizados em categorias criadas por você. Uma árvore de categorias fica à esquerda e a lista de vídeos da categoria selecionada fica à direita (veja [Categorias](#categorias-abas-vídeo-e-lista-de-reprodução-posterior) abaixo). Inclui botões de Ação e Copiar para cada item (descritos abaixo).
* **Canal:** Lista seus canais salvos com um painel de descrição do canal. Inclui botões para abrir o canal, navegar pelo seu conteúdo por tipo, buscar dentro do canal, e descrever seu avatar via Be My Eyes (Alt+D).
* **Playlist:** Lista suas playlists salvas. Pressione Espaço, Enter ou Alt+V para expandir todos os vídeos de uma playlist. Inclui um botão Abrir na Web (Alt+W) e um botão Descrever capa (Alt+D) para obter uma descrição de Be My Eyes da imagem de capa da playlist.
* **Lista de reprodução posterior:** Lista seus vídeos salvos usando o mesmo layout de árvore de categorias + lista da aba Vídeo, com seu próprio conjunto independente de categorias.
* **Histórico de busca:** Lista cada busca que você já fez, com opções para executar novamente, remover ou limpar entradas (veja [Histórico de Busca](#histórico-de-busca) acima).

#### Comandos da janela de Favoritos

* Pressione Control+1 a Control+5 para alternar entre abas
* Pressione Control+Cima/Baixo para reordenar abas
* Pressione Control+C (copiar), Control+X (recortar), ou Control+V (colar) para reordenar itens
    * Vídeos favoritos e Lista de reprodução posterior oferecem suporte a copiar e mover itens entre si, incluindo itens dentro de uma categoria. As abas Vídeo e Lista de reprodução posterior mantêm cada uma sua própria lista de categorias separada, então quando um item se move entre elas, ele é colocado na categoria atualmente selecionada na aba de destino. Canais favoritos e Playlists só oferecem suporte a mover itens dentro de sua própria lista.
* Pressione Alt+R ou Delete para remover um item
* Pressione Alt+N para adicionar um novo item da área de transferência — para as abas de canal e playlist, a URL deve corresponder ao tipo da aba
* Pressione **Alt+O (Ordenar...)** para abrir a caixa de diálogo de ordenação da aba atual — veja [Ordenação](#ordenação) abaixo
* O campo de busca filtra os resultados instantaneamente enquanto você digita — não é necessário pressionar Enter

#### Categorias (abas Vídeo e Lista de Reprodução Posterior)

Tanto a aba Vídeo quanto a de Lista de Reprodução Posterior permitem organizar itens em categorias próprias, usando uma visualização em árvore à esquerda, separada da lista de itens à direita. Cada aba mantém suas próprias categorias — criar uma categoria em uma não afeta a outra. Sempre há um nó padrão para itens sem categoria ("Vídeos" na aba Vídeo, "Lista de reprodução posterior" na aba Lista de Reprodução Posterior).

Com o foco na árvore de categorias:

* Pressione **Control+=** para adicionar uma nova categoria
* Pressione **F2** para renomear a categoria selecionada
* Pressione **Delete** para remover a categoria selecionada — se ela ainda contiver itens, você será perguntado se deseja movê-los para o nó padrão ou excluí-los junto com a categoria
* Pressione **Control+Shift+Cima** / **Control+Shift+Baixo** para reordenar a categoria selecionada
* Pressione Enter, ou Tab, para mover o foco para a lista de itens daquela categoria
* Clique com o botão direito, ou pressione a tecla Aplicativo/Menu, para um menu de contexto — seu conteúdo depende do que está selecionado: um nó de categoria mostra opções de gerenciamento de categoria (Adicionar/Renomear/Excluir/Mover), enquanto o nó padrão mostra apenas Adicionar categoria

Com o foco na lista de itens (lado direito), clique com o botão direito ou pressione a tecla Aplicativo/Menu para o mesmo menu Ação usado em todo o complemento (Ver informações, Comentários, Baixar, Adicionar a..., etc.) — separado do menu de contexto de categoria da árvore.

Recortar, Copiar e Colar na lista de itens funcionam conforme descrito acima, e colar sempre coloca os itens na categoria atualmente selecionada na árvore.

#### Ordenação

O botão **Ordenar... (Alt+O)** está disponível em qualquer aba com uma lista ordenável — incluindo Vídeo, Lista de reprodução posterior, e Histórico de busca. Ele abre uma caixa de diálogo com:

* **Ordenar por:** o campo pelo qual ordenar (Título, Canal, Duração, Data de envio, Data de adição — os campos variam ligeiramente por aba)
* **Crescente / Decrescente**
* **Ordenar apenas a categoria atual:** quando marcado, a ordenação reordena apenas os itens dentro da categoria atualmente selecionada na árvore, deixando todas as outras categorias intocadas. Desmarcado por padrão, o que significa que a ordenação se aplica a todas as categorias de uma vez.
* **Aplicar permanentemente (salvar no arquivo):** quando marcado, a nova ordem é gravada no disco imediatamente. Quando desmarcado, a ordenação é temporária — ela muda o que você vê agora, mas volta ao normal na próxima vez que a lista for recarregada ou você buscar algo.
* **Limpar ordenação:** descarta qualquer ordenação temporária e restaura a ordem salva no disco.

#### Lista de vídeos

Nas abas de vídeo e lista de reprodução posterior, assim como em qualquer outra visualização que mostre uma lista de vídeos, você encontrará os botões **Ação...** e **Copiar...**. Esses são controles padrão em todas as visualizações de lista de vídeos, com o feed de inscrições adicionando uma opção extra de "Cancelar inscrição neste canal".

Pressione Enter em qualquer item para abrir o vídeo no seu navegador, ou pressione a barra de espaço para executar a Ação rápida que você pode definir em [Configurações](#configurações).

##### Botão Ação

Pressione Alt+A para abrir o menu Ação, que inclui:

* Ver informações do vídeo... (i)
* Ver comentários / replay... (c)
* Ver capítulos/marcações de tempo... (t)
* Obter descrição da miniatura (Be My Eyes)... (g)
* Baixar vídeo (d)
* Baixar áudio (a)
* Adicionar aos vídeos favoritos (f)
* Adicionar aos canais favoritos (f)
* Adicionar à lista de reprodução posterior (w)
* Abrir vídeo no navegador (b)
* Abrir canal no navegador (h)
* Mostrar vídeos do canal (v)
* Mostrar Shorts do canal (s)
* Mostrar transmissões ao vivo do canal (l)
* Mostrar playlists do canal (l)
* Mostrar podcasts do canal (p)

##### Botão Copiar

Pressione Alt+C para abrir o menu Copiar, que inclui:

* Copiar título (t)
* Copiar URL do vídeo (u)
* Copiar nome do canal (c)
* Copiar URL do canal (h)
* Copiar resumo (s)

### Feed de inscrições

Uma janela exibindo vídeos dos canais que você segue dentro do complemento. Isso é independente das inscrições da sua conta do YouTube — nenhuma vinculação de conta ou dado pessoal é necessário.

Diferente da janela de Favoritos, esta visualização usa abas padrão divididas por tipo de conteúdo:

* **Todos:** Todos os tipos de conteúdo combinados
* **Vídeo:** Apenas vídeos normais
* **Shorts:** Apenas vídeos curtos
* **Ao vivo:** Transmissões ao vivo e repetições de transmissões ao vivo

Além dessas categorias padrão, você pode criar categorias personalizadas e configurar quais canais aparecem em cada uma.

#### Comandos do feed de inscrições

* Pressione Control+1 a Control+0 para pular para uma aba de categoria (até 10 categorias)
* Pressione Control+Cima/Baixo para reordenar categorias, assim como na janela de Favoritos
* Pressione F2 para renomear uma categoria (exceto as 4 categorias padrão)
* Pressione Control+= para adicionar uma nova categoria
* Pressione Control+- para remover uma categoria (exceto as 4 categorias padrão)
* Acesse os botões Ação e Copiar de cada vídeo, ou pressione Enter para abri-lo em um navegador
* Pressione Delete ou Alt+S para marcar um vídeo como visto — ele será removido da lista
* Pressione Control+Delete para marcar todos os vídeos da aba atual como vistos

Botões adicionais nesta janela:

* **Marcar como visto (Alt+S)** — remove o vídeo da lista; a tecla Delete também funciona
* **Adicionar nova inscrição pela URL da área de transferência (Alt+N)** — inscreve-se em um canal usando a URL copiada na área de transferência
* **Atualizar feed (Alt+U)** — dispara manualmente uma atualização para todos os canais inscritos; o complemento também se atualiza automaticamente ao iniciar o NVDA por padrão
* **Mais... (Alt+M)** — abre um submenu com opções adicionais:
    * Marcar todos na aba atual como vistos (Ctrl+Delete) (a)
    * Mostrar todos os vídeos (incluindo os vistos) (v) — alterna entre mostrar apenas os não vistos e mostrar todos os vídeos; a configuração é salva automaticamente
    * Gerenciar inscrições... (m)
    * Adicionar nova categoria... Ctrl+= (c)
    * Renomear categoria atual... F2 (r)
    * Remover categoria atual... Ctrl+-
    * Limpar todos os vídeos do feed... — remove todos os vídeos do banco de dados sem remover suas inscrições; útil se o banco de dados crescer muito e afetar o desempenho do NVDA

### Gerenciar inscrições

Esta janela mostra todos os canais aos quais você está inscrito. A primeira seção é a lista de canais, seguida de opções de gerenciamento para cada canal:

* **Filtrar por categoria** — filtra a lista de canais por categoria; o padrão é "Todos"
* **Atribuir a categorias** — escolha em quais categorias o conteúdo deste canal deve aparecer
* **Tipos de conteúdo a buscar** — escolha quais tipos de conteúdo atualizar para este canal (Vídeos, Shorts, Ao vivo); útil para canais que publicam apenas determinados tipos
* **Ver conteúdo... (Alt+C)** — navegue pelo conteúdo do canal, igual ao botão Ação
* **Inscrever-se em novo canal pela área de transferência... (Alt+N)** — inscreva-se em um novo canal usando a URL na área de transferência
* **Cancelar inscrição neste canal (Alt+U)** — remove o canal das suas inscrições
* **Salvar alterações** — **importante:** você precisa pressionar este botão antes de fechar a janela, ou suas alterações não serão salvas

### Gerenciador de perfis de usuário

Esta janela gerencia seus perfis de usuário. O complemento vem com um perfil "padrão". Você pode adicionar, excluir ou renomear perfis aqui. Para alternar entre perfis, vá ao painel de Configurações do complemento.

Nesta janela:

* Pressione F2 para renomear o perfil selecionado
* Pressione Delete para remover o perfil selecionado

**Nota:** Excluir um perfil apaga permanentemente todos os dados associados a ele. Quaisquer vídeos, canais ou inscrições salvos naquele perfil serão perdidos.

### l: (mostrar comentários)

Existem três tipos de comentários em vídeos do YouTube:

* **Comentário** — comentários padrão de espectadores em vídeos comuns
* **Chat ao vivo** — mensagens enviadas durante uma transmissão ao vivo
* **Replay do chat ao vivo** — o chat ao vivo gravado de um vídeo transmitido anteriormente, caso o dono do canal não o tenha removido

O YoutubePlus oferece acesso aos três tipos através deste comando.

#### Chat ao vivo de...

Para vídeos atualmente ao vivo, pressione L e o complemento abrirá uma nova janela exibindo as mensagens de chat recebidas. Somente as mensagens recebidas após você ativar o comando são exibidas — mensagens anteriores não são capturadas.

Você pode fechar esta janela e reabri-la mais tarde com o comando V na camada do YoutubePlus, desde que a transmissão ainda esteja ativa e o NVDA não tenha sido reiniciado.

Use o comando R para alternar se o NVDA lê as novas mensagens em voz alta à medida que chegam. Isso funciona bem para transmissões com mensagens pouco frequentes. Para transmissões de alto volume, pode ser mais fácil desativar a leitura automática e rolar a janela manualmente.

Pressione Shift+L para parar de monitorar o chat do vídeo atual.

Três configurações afetam diretamente este recurso:

- **Ler automaticamente as mensagens recebidas do chat ao vivo:** quando marcado, o NVDA lê as novas mensagens em voz alta imediatamente — a mesma função do comando R, mas salva como preferência padrão.
- **Intervalo de atualização do chat ao vivo:** com que frequência (em segundos) o complemento verifica novas mensagens. O padrão é 5 segundos.
- **Limite do histórico de mensagens:** o número máximo de mensagens armazenadas na memória durante uma sessão. A janela de chat ao vivo mostra apenas as mensagens mais recentes até esse limite (padrão: 5.000). O complemento mantém todas as mensagens em segundo plano para exportação, até um máximo de 200.000, para evitar uso excessivo de memória.

Quando uma transmissão termina — ou o complemento detecta que ela terminou — uma caixa de diálogo aparecerá automaticamente perguntando se você deseja exportar todas as mensagens coletadas. Pressione Sim para salvar o histórico do chat como um arquivo.

#### Comentários / replay do chat ao vivo

Para vídeos enviados normalmente ou transmissões arquivadas, você pode acessar os comentários da mesma forma. Se tanto a repetição do chat ao vivo quanto os comentários padrão estiverem disponíveis, uma caixa de diálogo perguntará qual você deseja carregar.

Não há limite para o número de comentários exibidos, embora o carregamento possa demorar em vídeos com muitos comentários.

Os comentários são exibidos com os comentários fixados primeiro, seguidos de todos os outros na ordem de classificação configurada nas Configurações (mais recentes primeiro ou mais antigos primeiro).

#### Seções da janela de comentários

* **Campo de busca** — digite para filtrar comentários; os resultados são atualizados instantaneamente
* **Caixa de combinação de filtro** — selecione uma opção de filtro (o complemento preenche o campo de busca automaticamente):
    * Sem filtro — padrão; mostra todos os comentários
    * Filtrar pelo autor selecionado — mostra apenas comentários do autor selecionado
    * Mostrar apenas Super Chats
    * Mostrar apenas Super Stickers
    * Mostrar apenas Super Thanks
* **Lista de comentários** — mostra o nome do autor seguido de sua mensagem
* **Área de texto somente leitura** — role pelo texto completo do comentário selecionado, útil quando um comentário é longo demais para ser exibido por completo na lista
* **Botão Copiar (Alt+C ou Ctrl+C)** — copia o comentário selecionado
* **Botão Exportar (Alt+E)** — salva todos os comentários como um arquivo de texto na pasta definida nas Configurações
* **Campo de valor total pago** — exibido apenas para repetições de chat ao vivo; mostra o total de doações dos espectadores durante a transmissão

## Configurações

Acesse as configurações em `NVDA -> Preferências -> Configurações...` e selecione a categoria **"YoutubePlus"**.

- **Perfil ativo:** Selecione o perfil a ser usado. É necessário reiniciar após trocar de perfil.
- **Botão Gerenciar perfis:** Abre a janela do Gerenciador de Perfis de Usuário.
- **Ação rápida (barra de espaço):** Escolha o que a tecla Espaço faz nas janelas de lista de vídeos. Todas as opções do menu Ação estão disponíveis.
- **Modo de notificação:** Escolha como o complemento sinaliza a atividade em segundo plano:
  - *Bipe:* Bipes curtos
  - *Som:* Efeito sonoro
  - *Silencioso:* Sem notificação sonora (as respostas faladas continuam ocorrendo)
- **Ordem de classificação padrão:** Escolha se as listas (comentários, vídeos do canal) são ordenadas por **Mais recentes primeiro** ou **Mais antigos primeiro**.
- **Itens a buscar:** Quantos itens obter por tipo de conteúdo ao navegar por um canal, e para atualizações do feed de inscrições. Padrão: 20.
- **Tipos de conteúdo padrão:** Escolha quais tipos de conteúdo buscar para canais recém-inscritos: Vídeos, Shorts, e/ou Ao vivo.
- **Intervalo de atualização em segundo plano:** Com que frequência o complemento verifica novo conteúdo dos canais inscritos. Pode ser desativado ou definido de 15 minutos a 24 horas. O complemento também se atualiza automaticamente a cada inicialização do NVDA por padrão.
- **Ler automaticamente as mensagens recebidas do chat ao vivo:** quando marcado, o NVDA lê novas mensagens de chat em voz alta à medida que chegam.
- **Intervalo de atualização do chat ao vivo:** Com que frequência (em segundos) o complemento verifica novas mensagens. Padrão: 5 segundos.
- **Limite do histórico de mensagens:** Número máximo de mensagens de chat armazenadas na memória durante uma sessão.
- **Formato padrão de legenda:** Formato do arquivo de legenda para downloads: SRT, VTT, TTML, ou TXT (texto simples sem marcações de tempo)
- **Opções de qualidade e formato de download (Alt+D):** Uma seção recolhível (recolhida por padrão — pressione Alt+D em qualquer lugar da página de Configurações, ou ative-a diretamente, para expandir/recolher) contendo:
  - *Qualidade de vídeo preferida:* A melhor disponível, ou um limite de resolução de 2160p até 360p.
  - *Contêiner de vídeo preferido:* MP4, MKV ou WebM.
  - *Qualidade de áudio preferida (ao converter):* A melhor disponível, ou uma taxa de bits de 320 até 96 kbps. Só se aplica quando o formato de áudio abaixo não é "Melhor disponível."
  - *Formato de áudio preferido:* Melhor disponível (sem conversão, o padrão — baixa o formato que o YouTube já fornece, sem precisar do FFmpeg), ou converte para MP3, WAV, M4A/AAC, FLAC, Opus ou Vorbis (OGG) — qualquer uma dessas conversões exige o FFmpeg, assim como os downloads de vídeo.
- **Método de cookies (experimental):** Selecione o navegador em que você está conectado ao YouTube. O complemento extrairá os cookies desse navegador para autenticar as solicitações, o que pode ajudar a resolver o erro "Faça login para confirmar que você não é um robô". Note que este recurso é experimental e os resultados variam conforme o navegador e a configuração do sistema.
- **Caminho padrão da pasta de download e exportação:** A pasta de destino para vídeos/áudio baixados e chat exportado.
- **Fazer backup dos dados agora:** Faz backup manual de todos os dados do perfil ativo. O complemento também realiza um backup diário automático em segundo plano.
- **Restaurar dados de backup:** Mostra uma lista de backups disponíveis (até os últimos 5 dias) para você escolher de qual data restaurar.

## Informações adicionais

Este complemento depende de duas bibliotecas principais: [pytchat](https://pypi.org/project/pytchat/) para monitoramento de chat ao vivo, e [yt-dlp](https://pypi.org/project/yt-dlp/) para todo o restante do acesso a dados do YouTube. Estendemos nossos sinceros agradecimentos aos desenvolvedores de ambas as bibliotecas.

### Sobre o yt-dlp

O [yt-dlp](https://github.com/yt-dlp/yt-dlp) é uma das ferramentas de código aberto mais poderosas para baixar vídeo e áudio de sites ao redor do mundo — com suporte a mais de 1.000 sites, não apenas o YouTube. É gratuito, de código aberto, e mantido ativamente por uma comunidade global, sem anúncios ou malware, ao contrário de muitas ferramentas de download baseadas em navegador.

Dito isso, tenha em mente as seguintes diretrizes de uso:

1. **Uso justo:** Evite buscar grandes quantidades de dados ou enviar solicitações repetidas em pouco tempo. O YouTube pode detectar atividade incomum e restringir temporariamente o acesso a partir do seu endereço IP.
2. **Direitos autorais e privacidade:** Qualquer dado ou conteúdo obtido deve ser apenas para visualização ou análise pessoal. Por favor, respeite os Termos de Serviço de cada plataforma e não use os dados de forma que infrinja direitos autorais.
3. **Responsabilidade:** Você é responsável por como usa este software. O desenvolvedor do complemento fornece apenas a interface para acessar dados do YouTube através da biblioteca yt-dlp.

**Dica:** Se você precisar processar grandes quantidades de dados, espace suas solicitações para manter a estabilidade da conexão e evitar restrições de acesso.
