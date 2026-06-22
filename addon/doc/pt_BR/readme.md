# YoutubePlus para NVDA

> O YoutubePlus é um complemento para usuários do NVDA que adoram o YouTube, mas consideram muitos recursos do site difíceis de acessar — como ler comentários, acompanhar canais ou monitorar o chat ao vivo.
>
> Trazemos esses recursos para a interface de usuário do NVDA em um formato de fácil navegação pelo teclado, com suporte a atalhos e totalmente personalizável — **sem a necessidade de chaves de API ou login em contas do Google/YouTube**.
>
> Você pode acompanhar seus canais favoritos e ter a certeza de que verá todos os vídeos deles, sem que o algoritmo do YouTube os filtre. Um sistema de Favoritos está incluso para vídeos, canais, playlists, além de uma Lista de Assistir Mais Tarde para salvar conteúdos nos quais você tem interesse, mas ainda não teve tempo de assistir.
>
> Há uma busca de vídeos integrada que exibe os resultados na própria interface do complemento — e não apenas uma caixa de pesquisa que abre o YouTube no navegador. Uma função de download está inclusa para salvar vídeos e áudios por conveniência — se o download for a sua necessidade principal, recomenda-se o uso de ferramentas dedicadas.
>
> O que este complemento **não** faz é embutir um reprodutor de vídeo. Acreditamos que o reprodutor web do YouTube já é acessível o suficiente por si só. Se você ainda achar que ele deixa a desejar, pode utilizar outros complementos, como o [browserNav](https://addonstore.nvaccess.org/?channel=stable&language=en&apiVersion=2025.3.2&addonId=browsernav), para melhorar a experiência.

---

## Sumário

- [Atalhos de Teclado](#atalhos-de-teclado)
- [Detalhes dos Recursos](#detalhes-dos-recursos)
  - [a: Menu Adicionar para...](#a-menu-adicionar-para)
  - [d: Baixar Vídeo/Áudio](#d-baixar-vídeoáudio)
  - [b: Baixar Legendas](#b-baixar-legendas)
  - [e: Pesquisar no YouTube](#e-pesquisar-no-youtube)
  - [i: Informações do Vídeo](#i-informações-do-vídeo)
  - [t: Capítulos / Marcadores de Tempo](#t-capítulos--marcadores-de-tempo)
  - [l: Comentários / Chat ao Vivo / Reprise do Chat ao Vivo](#l-comentários--chat-ao-vivo--reprise-do-chat-ao-vivo)
  - [Favoritos (f, c, p, w)](#favoritos-f-c-p-w)
  - [s: Feed de Inscrições](#s-feed-de-inscrições)
  - [m: Gerenciar Inscrições](#m-gerenciar-inscrições)
  - [u: Gerenciador de Perfis de Usuário](#u-gerenciador-de-perfis-de-usuário)
  - [Lista de Vídeos](#lista-de-vídeos)
- [Configurações](#configurações)
- [Informações Adicionais](#informações-adicionais)

---

## Atalhos de Teclado

Este complemento utiliza um sistema de **Comando em Camadas** para evitar conflitos com outros complementos ou comandos do NVDA.

**Como usar:**

1. Pressione **NVDA+Y** para entrar no Modo de Comando do YoutubePlus (você ouvirá um som de notificação).
2. Pressione a letra correspondente para ativar o recurso desejado.

> **Nota:** Se o atalho `NVDA+Y` conflitar com outro complemento, você pode alterá-lo em `NVDA → Preferências → Definir comandos...` sob a categoria "YoutubePlus".
> **Detecção de URL:** Para comandos que exigem a URL de um vídeo, o complemento verifica primeiro a **janela do navegador atualmente aberta**. Se nenhuma URL do YouTube for encontrada ali, ele passa automaticamente a verificar a **área de transferência**.

### Todas as teclas no modo YoutubePlus

| Tecla | Recurso |
| ----- | --------- |
| **a** | Menu "Adicionar para..." (Favoritos / Inscrever-se) |
| **f** | Abrir Vídeos Favoritos |
| **c** | Abrir Canais Favoritos |
| **p** | Abrir Playlists Favoritas |
| **w** | Abrir Lista de Assistir Mais Tarde |
| **b** | Baixar legendas |
| **d** | Baixar vídeo ou áudio |
| **e** | Pesquisar no YouTube |
| **q** | Pesquisa Rápida — pesquisa no YouTube imediatamente usando o texto selecionado ou o conteúdo da área de transferência, sem abrir o diálogo de pesquisa |
| **Control+H** | Abre a janela de Favoritos diretamente na aba Histórico de Pesquisa |
| **i** | Mostrar informações do vídeo |
| **t** | Mostrar Capítulos / Marcadores de Tempo |
| **m** | Gerenciar Inscrições |
| **s** | Abrir Feed de Inscrições |
| **u** | Gerenciar Perfis de Usuário |
| **l** | Mostrar comentários ou iniciar monitoramento do chat ao vivo |
| **Shift+L** | Parar monitoramento do chat ao vivo |
| **r** | Alternar a leitura automática do chat ao vivo |
| **v** | Reabrir a janela do chat ao vivo (enquanto a transmissão ainda estiver ativa) |
| **y** | Abrir Configurações do YoutubePlus |
| **h** | Abrir diálogo de Ajuda |

---

## Detalhes dos Recursos

### a: Menu Adicionar para...

Abre um submenu para escolher onde adicionar o vídeo ou canal atual:

- **Adicionar aos Vídeos Favoritos** — salva o vídeo atual nos Favoritos
- **Adicionar aos Canais Favoritos** — salva o canal do vídeo atual nos Favoritos
- **Adicionar às Playlists Favoritas** — salva a playlist atual nos Favoritos
- **Inscrever-se no Canal** — acompanha o canal através do sistema de Inscrições do complemento
- **Adicionar à Lista de Assistir Mais Tarde** — salva o vídeo atual na Lista de Assistir Mais Tarde para ver depois

A maioria dos comandos funciona com qualquer formato de URL do YouTube. Por exemplo, se você estiver na página de um vídeo e escolher "Adicionar aos Canais Favoritos", o complemento extrairá a URL do canal automaticamente.

**Exceção:** Para Playlists, você deve estar com a página de uma playlist do YouTube aberta ou ter uma URL de playlist válida na área de transferência.

---

### d: Baixar Vídeo/Áudio

Pressione **NVDA+Y → D** para abrir um diálogo perguntando se deseja baixar como:

- **Arquivo de vídeo (MP4)** — baixa o vídeo com áudio
- **Arquivo de áudio (M4A)** — baixa apenas o áudio

Um diálogo de progresso mostra a porcentagem do download enquanto ele é executado. O botão **Cancelar** está disponível a qualquer momento.

Defina a pasta de destino nas [Configurações](#configurações).

> **Nota:** Este recurso é fornecido por conveniência. Para downloads em lote, recomendam-se ferramentas dedicadas.

---

### b: Baixar Legendas

Pressione **NVDA+Y → B** para obter a lista de idiomas de legenda disponíveis para o vídeo atual e, em seguida, escolha em um diálogo. As legendas são listadas em dois tipos:

- **(manual)** — legendas criadas pelo criador do vídeo ou pela comunidade
- **(auto)** — legendas geradas automaticamente pelo YouTube

Formatos de arquivo suportados: **SRT, VTT, TTML** e **TXT** (texto simples sem marcadores de tempo). Configurável nas [Configurações](#configurações).

---

### e: Pesquisar no YouTube

Pressione **NVDA+Y → E** para abrir a janela de pesquisa. Digite sua busca e pressione Enter para pesquisar imediatamente. Pressione Tab para ajustar o número de resultados (o complemento lembra desse valor para a próxima vez).

O campo de pesquisa é uma caixa de combinação que lembra suas pesquisas anteriores: pressione a seta para baixo (ou Alt+Seta para baixo) para exibir uma lista de palavras-chave anteriores e selecionar uma em vez de redigitá-la.

Os resultados são exibidos no mesmo formato de Lista de Vídeos usado em todo o complemento — e não como uma página da web do YouTube. Os resultados podem incluir vídeos, canais e playlists.

#### q: Pesquisa Rápida

Uma alternativa mais rápida ao diálogo de pesquisa. Selecione algum texto em qualquer aplicativo (ou tenha uma consulta copiada na área de transferência se nada estiver selecionado), depois pressione Q na camada do YoutubePlus. O complemento pesquisa no YouTube imediatamente usando esse texto e o número de resultados salvo da sua última pesquisa — sem diálogo, sem teclas extras.

#### Histórico de Pesquisa

Cada pesquisa que você realiza — pelo diálogo de pesquisa ou pela pesquisa rápida — é salva automaticamente. Pressione **Control+H** na camada do YoutubePlus para ir diretamente à aba Histórico de Pesquisa na janela de Favoritos, onde você pode:

* Pressionar Enter, ou o botão **Pesquisar Novamente**, para repetir uma pesquisa anterior
* Pressionar **Nova Pesquisa (Alt+N)** para abrir o diálogo de pesquisa
* Pressionar Delete, ou o botão **Remover**, para remover uma entrada
* Pressionar o botão **Limpar Tudo** para limpar todo o histórico

---

### i: Informações do Vídeo

Pressione **NVDA+Y → I** para visualizar os seguintes detalhes do vídeo atual:

- Título
- Canal
- Duração
- Data de envio
- Contagem de visualizações
- Contagem de curtidas
- Contagem de comentários
- Descrição

---

### t: Capítulos / Marcadores de Tempo

Pressione **NVDA+Y → T** para visualizar a lista de capítulos ou marcadores de tempo do vídeo atual (se o criador incluiu essas informações). Se o complemento informar "Nenhum capítulo encontrado", o vídeo simplesmente não possui dados de capítulos.

Esta janela inclui:

- **Campo de pesquisa** — filtra a lista de capítulos em tempo real; não é necessário pressionar Enter
- **Lista de capítulos** — mostra o título do capítulo e o tempo de início
- **Área de texto** — exibe o nome do capítulo selecionado em um formato legível
- **Botão Abrir Capítulo** (o pressione Espaço/Enter) — pula direto para aquele capítulo no navegador
- **Botão Copiar Título** — copia o título do capítulo
- **Botão Copiar URL** — copia a URL com o marcador de tempo para aquele capítulo
- **Botão Exportar** — salva todos os capítulos em um arquivo de texto

---

### l: Comentários / Chat ao Vivo / Reprise do Chat ao Vivo

O YoutubePlus suporta três tipos de conteúdo através deste comando:

#### 1. Comentários (para vídeos normais)

Pressione **NVDA+Y → L** enquanto estiver na página de um vídeo. O complemento obterá todos os comentários. Os comentários fixados aparecem primeiro, seguidos por todos os outros na ordem de classificação configurada nas Configurações.

**A janela de Comentários inclui:**

- **Campo de pesquisa** — filtra os comentários em tempo real
- **Caixa de combinação de filtro** — filtros predefinidos:
  - Sem Filtro — mostra todos os comentários
  - Filtrar por Autor Selecionado — mostra apenas comentários do comentarista selecionado
  - Mostrar Apenas Super Chats
  - Mostrar Apenas Super Stickers
  - Mostrar Apenas Valeu Demais
- **Lista de comentários** — mostra o nome do comentarista e a mensagem; há suporte para tópicos de respostas
- **Área de texto somente leitura** — mostra o texto completo do comentário selecionado, útil para comentários longos
- **Botão Copiar** (Alt+C ou Ctrl+C) — copia o comentário selecionado
- **Botão Exportar** (Alt+E) — salva todos os comentários em um arquivo de texto

#### 2. Chat ao Vivo (para transmissões ao vivo ativas)

Para vídeos que estão transmitindo ao vivo no momento, pressione L para abrir uma janela que recebe as mensagens do chat. Apenas as mensagens recebidas após a ativação deste comando são exibidas — o histórico anterior não é capturado.

- Feche e reabra a janela com o comando **V**, desde que o monitoramento não tenha sido interrompido.
- Use o comando **R** para alternar a leitura automática de novas mensagens — ideal para transmissões com mensagens pouco frequentes. Para transmissões com grande volume de mensagens, recomenda-se desativar a leitura automática e rolar manualmente pela janela.
- Use **Shift+L** para parar o monitoramento. Quando interrompido, o complemento perguntará se você deseja salvar o histórico do chat em um arquivo.

**Configurações relacionadas:**

- **Falar chat ao vivo recebido automaticamente:** Lê novas mensagens em voz alta à medida que chegam (o mesmo que o comando R, mas salvo como uma preferência padrão).
- **Intervalo de atualização do chat ao vivo:** Com que frequência (inércia em segundos) o complemento verifica se há novas mensagens (padrão: 5 segundos).
- **Limite do histórico de mensagens:** Máximo de mensagens armazenadas na memória (padrão: 5.000). O complemento possui um limite máximo fixo de 200.000 mensagens para evitar o uso excessivo de memória.

#### 3. Reprise do Chat ao Vivo (para transmissões anteriores)

Para vídeos que já foram transmitidos ao vivo e onde o canal não removeu o chat, pressionar L exibirá um diálogo perguntando se deseja visualizar os **Comentários** ou a **Reprise do Chat ao Vivo**. A janela de reprise tem a mesma estrutura da janela de Comentários, com uma adição:

- **Valor Pago Total** — mostra o total de doações (Super Chats / Super Stickers) arrecadadas durante a transmissão

---

### Favoritos (f, c, p, w)

A janela de Favoritos está dividida em **5 abas**, cada uma acessível por comandos separados ou todas dentro da mesma janela.

| Tecla | Aba |
| ----- | ----- |
| **F** | Vídeos salvos (Vídeos Favoritos) — suporta categorias |
| **C** | Canais salvos (Canais Favoritos) |
| **P** | Playlists salvas (Playlists Favoritas) |
| **W** | Vídeos para assistir mais tarde (Lista de Assistir Mais Tarde) — suporta categorias |
| **Control+H** | Histórico de Pesquisa |

#### Atalhos na janela de Favoritos

- **Ctrl+1 a Ctrl+5** — alterna entre as abas
- **Ctrl+Seta para cima/Seta para baixo** — reordena as abas
- **Ctrl+C / Ctrl+X / Ctrl+V** — copia/recorta/cola para mover itens
  _(Vídeos Favoritos e Lista de Assistir Mais Tarde podem ser movidos entre si, incluindo itens dentro de uma categoria. Cada aba mantém sua própria lista de categorias separada, portanto, ao mover um item entre elas ele é colocado na categoria atualmente selecionada na aba de destino. Canais e Playlists só podem ser movidos dentro de sua própria lista.)_
- **F2** — renomeia manualmente o vídeo/canal/playlist selecionado
- **Alt+R ou Delete** — remove o item selecionado
- **Alt+N** — adiciona um novo item a partir de uma URL na área de transferência
- **Alt+S** — move o foco para o campo de pesquisa (os resultados são atualizados em tempo real)
- **Botão Ordenar... (Alt+O)** — ordena a lista:
  - Ordenar por: Título, Canal, Duração, Data de Adição ou Data de Envio
  - Escolha Crescente ou Decrescente
  - **Ordenar apenas a categoria atual:** quando marcado, a ordenação se aplica apenas aos itens da categoria selecionada na árvore, sem afetar as demais. Desmarcado por padrão.
  - **Aplicar permanentemente:** quando marcado, a ordem é salva no disco imediatamente; caso contrário, é temporária e é redefinida ao recarregar.
  - Pressione **Limpar Ordenação** para restaurar a ordem original

#### Categorias (Abas Vídeos e Lista de Assistir Mais Tarde)

Ambas as abas permitem organizar itens em categorias usando uma exibição em árvore à esquerda, separada da lista de itens à direita. Cada aba mantém suas próprias categorias de forma independente. Sempre há um nó padrão para itens sem categoria ("Vídeos" na aba Vídeos, "Lista de Assistir Mais Tarde" na aba Lista).

Com o foco na árvore de categorias:

- **Ctrl+=** — adiciona uma nova categoria
- **F2** — renomeia a categoria selecionada
- **Delete** — remove a categoria selecionada — se ainda contiver itens, será perguntado se deseja movê-los para o nó padrão ou excluí-los junto com a categoria
- **Ctrl+Shift+Seta para cima / Ctrl+Shift+Seta para baixo** — reordena a categoria selecionada
- **Enter ou Tab** — move o foco para a lista de itens daquela categoria
- **Clique direito ou tecla Aplicativo/Menu** — menu de contexto: em um nó de categoria mostra opções de gerenciamento (Adicionar/Renomear/Excluir/Mover); no nó padrão mostra apenas Adicionar Categoria

Com o foco na lista de itens (direita), clique direito ou pressione a tecla Aplicativo/Menu para o mesmo menu Ação usado em todo o complemento — separado do menu de contexto da árvore.

Recortar, Copiar e Colar na lista de itens sempre coloca os itens na categoria atualmente selecionada na árvore.

#### Aba Canais (Favoritos)

Esta aba oferece mais do que uma simples lista — ela também inclui:

- **Área de texto da descrição do canal** — mostra a biografia/informações sobre o canal
- **Botão Abrir canal no navegador**
- **Botões para navegar pelos conteúdos de Vídeos / Shorts / Ao Vivo** daquele canal diretamente

#### Aba Playlists (Favoritos)

- Pressione **Espaço, Enter ou Alt+V** — expande todos os vídeos da playlist
- **Botão Abrir na Web (Alt+W)** — abre a playlist no navegador
### s: Feed de Inscrições

Uma janela que exibe vídeos dos canais que você acompanha através do complemento. Isso é **independente** das inscrições da sua conta do YouTube — não é necessário fazer login.

A visualização padrão possui 4 abas por tipo de conteúdo:

| Aba | Conteúdo |
| ----- | --------- |
| **Tudo** | Todos os tipos de conteúdo combinados |
| **Vídeo** | Apenas vídeos normais |
| **Shorts** | Apenas vídeos de formato curto (Shorts) |
| **Ao Vivo** | Transmissões ao vivo e reprises de lives |

Você também pode criar **categorias personalizadas** e configurar quais canais aparecem em cada uma delas.

#### Atalhos no Feed de Inscrições

- **Ctrl+1 a Ctrl+0** — pula para uma aba de categoria (até 10 abas)
- **Ctrl+Seta para cima/Seta para baixo** — reordena as abas/categorias
- **F2** — renomeia uma categoria (exceto as 4 abas padrão)
- **Ctrl+= (Igual)** — adiciona uma nova categoria
- **Ctrl+- (Ífen)** — remove uma categoria (exceto as 4 abas padrão)
- **Delete ou Alt+S** — marca um vídeo como visto; ele será removido da lista
- **Ctrl+Delete** — marca todos os vídeos da aba atual como vistos

#### Botões na janela do Feed de Inscrições

- **Marcar como visto (Alt+S)** — marca o vídeo selecionado como visto
- **Adicionar nova Inscrição a partir da URL da área de transferência (Alt+N)** — inscreve-se em um canal usando a URL que estiver na área de transferência
- **Atualizar Feed (Alt+U)** — aciona manualmente uma atualização de todos os canais inscritos (o complemento também se atualiza automaticamente ao iniciar o NVDA)
- **Mais... (Alt+M)** — opções adicionais:
  - Marcar todos na aba atual como vistos (Ctrl+Delete)
  - Mostrar todos os vídeos (incluindo vistos) — alterna entre apenas não vistos e todos os vídeos; a configuração é salva automaticamente
  - Gerenciar inscrições...
  - Adicionar Nova Categoria... (Ctrl+=)
  - Renomear Categoria Atual... (F2)
  - Remover Categoria Atual... (Ctrl+-)
  - **Limpar Todos os Vídeos do Feed...** — remove todos os vídeos do banco de dados sem remover os canais inscritos; útil quando o banco de dados cresce muito e afeta o desempenho do NVDA

---

### m: Gerenciar Inscrições

Uma janela que mostra todos os canais nos quais você está inscrito, com opções de gerenciamento para cada um:

- **Filtrar por Categoria** — filtra a lista de canais por categoria (padrão: Tudo)
- **Atribuir a Categorias** — escolhe em quais categorias o conteúdo deste canal deve aparecer
- **Tipos de Conteúdo a Obter** — escolhe quais tipos de conteúdo atualizar para este canal (Vídeos, Shorts, Ao Vivo); útil para canais que publicam apenas certos tipos
- **Visualizar Conteúdo... (Alt+C)** — navega pelo conteúdo do canal (o mesmo que o botão Ação)
- **Adicionar novo canal de inscrição a partir da Área de Transferência... (Alt+N)** — inscreve-se em um novo canal usando a URL que estiver na área de transferência
- **Cancelar Inscrição deste Canal (Alt+U)** — remove o canal das suas inscrições
- **Salvar Alterações** — ⚠️ **Importante:** você deve pressionar este botão antes de fechar a janela, caso contrário, suas alterações não serão salvas

---

### u: Gerenciador de Perfis de Usuário

O complemento suporta múltiplos **Perfis de Usuário** na mesma máquina. Cada perfil mantém seus dados completamente separados (Favoritos, Inscrições, Lista de Assistir Mais Tarde).

Nesta janela:

- **F2** — renomeia o perfil selecionado
- **Delete** — exclui o perfil selecionado ⚠️ A exclusão é permanente; todos os dados daquele perfil serão perdidos

Para alternar de perfil, vá em [Configurações](#configurações) → Perfil Ativo e, em seguida, reinicie o NVDA.

---

### Lista de Vídeos

A lista de vídeos é a interface padrão usada em todo o complemento — nos resultados de pesquisa, Favoritos, Feed de Inscrições e na navegação de vídeos de canais.

- Pressione **Enter** para abrir o vídeo no navegador
- Pressione **Espaço** para realizar a Ação Rápida (configurável nas Configurações)

#### Botão Ação (Alt+A)

Abre o menu de Ações para o vídeo selecionado:

| Item do menu | Atalho |
| ----------- | --------- |
| Ver Informações do Vídeo | i |
| Ver Comentários / Reprise | c |
| Ver Capítulos/Marcadores de Tempo | t |
| Baixar Vídeo | d |
| Baixar Áudio | a |
| Baixar Legendas | b |
| Adicionar aos Vídeos Favoritos | f |
| Adicionar aos Canais Favoritos | f |
| Adicionar à Lista de Assistir Mais Tarde | w |
| Abrir vídeo no navegador | o |
| Abrir canal no navegador | h |
| Mostrar vídeos do canal | v |
| Mostrar shorts do canal | s |
| Mostrar lives do canal | l |

#### Botão Copiar (Alt+C)

Abre o menu de Cópia:

| Item do menu | Atalho |
| ----------- | --------- |
| Copiar Título | t |
| Copiar URL do Vídeo | u |
| Copiar Nome do Canal | c |
| Copiar URL do Canal | h |
| Copiar Resumo | s |

---

## Configurações

Acesse através de `NVDA → Preferências → Configurações...` e selecione a categoria **"YoutubePlus"**.

| Configuração | Descrição |
| --------- | ------------- |
| **Perfil Ativo** | Seleciona o perfil ativo (requer a reinicialização do NVDA após a alteração) |
| **Gerenciar Perfis** | Abre o Gerenciador de Perfis de Usuário |
| **Ação Rápida (Barra de espaço)** | Define o que a tecla Espaço faz nas janelas de lista de vídeos; todas as opções do menu de Ação estão disponíveis |
| **Modo de notificação** | Como o complemento sinaliza atividades em segundo plano: **Bip** (tons curtos), **Som** (arquivo de áudio), **Silencioso** (sem áudio, mensagens faladas ainda ocorrem) |
| **Ordem de classificação padrão** | Ordem de exibição padrão: **Mais recentes primeiro** ou **Mais antigos primeiro** — aplica-se a comentários, chat e listas de vídeos de canais |
| **Itens a obter** | Número de itens recuperados por tipo de conteúdo ao navegar em um canal ou atualizar o feed (padrão: 20, intervalo: 5–100) |
| **Tipos de conteúdo padrão** | Tipos de conteúdo a obter para canais recém-inscritos: Vídeos, Shorts, Ao Vivo |
| **Intervalo de atualização em segundo plano** | Com que frequência o complemento verifica automaticamente se há novos conteúdos nos canais inscritos (desativado, ou de 15 minutos a 24 horas) |
| **Falar chat ao vivo recebido automaticamente** | Lê novas mensagens do chat ao vivo em voz alta à medida que chegam |
| **Intervalo de atualização do chat ao vivo** | Com que frequência (em segundos) o complemento verifica se há novas mensagens (padrão: 5 segundos) |
| **Limite do histórico de mensagens** | Número máximo de mensagens de chat armazenadas na memória durante uma sessão (padrão: 5.000) |
| **Método de Cookies (Experimental)** | Selecione o navegador no qual você está logado no YouTube. O complemento extrairá os cookies desse navegador para autenticar as requisições, o que pode ajudar a resolver o erro "Faça login para confirmar que você não é um robô". Note que este recurso é experimental e os resultados variam dependendo do navegador e da configuração do sistema. |
| **Formato de legenda padrão** | Formato de arquivo de legenda para downloads: SRT, VTT, TTML ou TXT (texto simples sem marcadores de tempo) |
| **Caminho padrão da pasta de download e exportação** | Pasta de destino para vídeos baixados, áudios e arquivos exportados |
| **Fazer backup dos dados agora** | Faz o backup imediato de todos os dados do perfil ativo (o complemento também realiza um backup automático diário) |
| **Restaurar dados a partir do backup** | Mostra os backups disponíveis (até os últimos 5 dias) para escolher para a restauração |

---

## Informações Adicionais

Este complemento conta com duas bibliotecas principais: [pytchat](https://pypi.org/project/pytchat/) para o monitoramento do chat ao vivo, e [yt-dlp](https://pypi.org/project/yt-dlp/) para todos os outros acessos a dados do YouTube. Expressamos nossos sinceros agradecimentos aos desenvolvedores de ambas as bibliotecas.

### Sobre o yt-dlp

O [yt-dlp](https://github.com/yt-dlp/yt-dlp) é uma das ferramentas de código aberto mais poderosas para baixar vídeos e áudios de sites em todo o mundo — suportando mais de 1.000 sites, não apenas o YouTube. Ele é gratuito, de código aberto, mantido ativamente por uma comunidade global e não contém anúncios ou malwares, ao contrário de muitas ferramentas de download baseadas no navegador.

**Diretrizes de uso para ter em mente:**

1. **Uso Justo:** Evite obter grandes quantidades de dados ou enviar requisições repetidas em um curto espaço de tempo. O YouTube pode detectar atividade incomum e restringir temporariamente o acesso do seu endereço IP.
2. **Direitos Autorais e Privacidade:** Quaisquer dados ou conteúdos recuperados devem ser apenas para visualização ou análise pessoal. Por favor, respeite os Termos de Serviço de cada plataforma e não utilize os dados de maneiras que infrinjam os direitos autorais.
3. **Responsabilidade:** Você é responsável por como utiliza este software. O desenvolvedor do complemento fornece apenas a interface para acessar os dados do YouTube através da biblioteca yt-dlp.

> **Dica:** Se você precisar processar grandes quantidades de dados, espaçe suas requisições para manter a estabilidade da conexão e evitar restrições de acesso.
