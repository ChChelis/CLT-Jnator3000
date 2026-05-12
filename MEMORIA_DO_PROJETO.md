# Memoria do Projeto - CLT-Jnator 3000

## Estado atual - 20260512_00:07:39

O app agora se chama `CLT-Jnator 3000`. Ele e um timer de tarefas para Windows, abre como uma janela comum, sem terminal, e permite criar tarefas, parar tarefas, continuar tarefas paradas e registrar descricoes obrigatorias quando uma parte de trabalho e encerrada.

A interface principal foi migrada para PySide6/Qt. A tentativa inicial era usar PyWebView com HTML/CSS, mas a instalacao falhou no Python 3.14 por causa da dependencia `pythonnet`. PySide6 instalou corretamente e entrega o objetivo principal da migracao: sombras reais, estilos mais modernos e melhor controle visual do que Tkinter.

A UI agora usa Manrope, tem tema configuravel por hexcode em `Interface > Cor`, preserva o scroll da lista de tarefas durante o tick do relogio e para oficialmente a tarefa antes de abrir a janela de descricao.

Os textos e icones da interface principal agora derivam da cor de destaque configurada, evitando tons roxos fixos quando o tema e alterado. Menus e campos de sistema usam fonte de sistema.

O aplicativo agora usa como icone a imagem fornecida pelo usuario em `assets\cltjnator_icon.png`, convertida para `.ico` e aplicada tanto na janela quanto no executavel.

O app tambem permite criar lembretes durante a execucao. Cada lembrete tem nome, descricao, modo por timer ou horario fixo, e recorrencia opcional diaria, semanal ou mensal no dia X.

No formulario de lembrete, o modo `Timer` mostra apenas o campo de timer e assume recorrencia diaria automaticamente. O modo `Horario fixo` mostra o horario e as opcoes de recorrencia.

O formulario de lembretes agora se reajusta verticalmente quando campos aparecem ou desaparecem, evitando que os campos fiquem amontoados.

Os lembretes agora disparam notificacoes nativas do Windows com som padrao. Se a notificacao nativa falhar, o app usa um popup interno como fallback.

A pasta do projeto foi limpa de imagens antigas e residuos de build. Para distribuir o app de forma simples, basta enviar o conteudo da pasta `dist`.

Os lembretes agora tambem ficam salvos em arquivo JSON ao lado do executavel, permitindo criar lembretes padrao antes de enviar o app para outra pessoa.

Cada tarefa pode ter uma ou varias partes. Quando uma tarefa e parada e depois continuada, o app guarda cada periodo separadamente, com inicio e fim em timestamp no formato `YYYYMMDD_HH:mm:ss`.

O app tambem permite renomear tarefas pelo botao direito do mouse, salvar relatorios em `csv`, `txt` ou `md`, e pedir salvamento automaticamente ao fechar quando houver dados ainda nao salvos.

Na exportacao CSV, alem dos dados principais da planilha, existe uma secao separada de resumo de horas. Ela usa os cabecalhos `Inicio`, `Almoco`, `Retorno Almoco` e `Fim`.

O menu `Arquivo` tambem tem uma opcao `Sair`, que fecha sem salvar depois de exibir um alerta de confirmacao.

A interface esta em teste visual com uma aparencia mais moderna: fundo em degrade roxo, cartao central arredondado com sombra suave e botoes circulares com icones.

Arquivo principal do codigo:

```text
D:\PROJETOS PYTHON\clt_jnator_qt.py
```

Executavel atual:

```text
D:\PROJETOS PYTHON\dist\CLT-Jnator 3000.exe
```

## Resumo da versao atual

- Abre como aplicativo de janela no Windows.
- O botao circular com icone de play cria uma nova tarefa.
- Se uma tarefa estiver rodando, iniciar outra encerra a atual antes.
- O botao circular com icone de stop encerra a parte atual da tarefa.
- O comando `Continuar` fica no menu de contexto do botao direito, junto com `Renomear`.
- Ao encerrar uma parte, o app exige uma descricao com pelo menos 50 caracteres.
- O botao `Confirmar` da descricao so libera apos os 50 caracteres, a menos que a checkbox de excecao seja marcada manualmente.
- A tecla `Enter` confirma as janelas de descricao e renomeacao.
- O botao direito em uma tarefa abre um menu de contexto com `Continuar` e `Renomear`.
- O menu `Arquivo > Salvar como` exporta os dados em `csv`, `txt` ou `md`.
- O menu `Arquivo > Sair` fecha sem salvar, mas pede confirmacao antes.
- A interface usa um cartao central claro sobre fundo em degrade, com botoes circulares e tons da cor de destaque.
- A versao atual usa PySide6/Qt em vez de Tkinter para melhorar sombras, radius e estilo.
- A fonte principal da UI e Manrope, embutida no projeto.
- A cor de destaque pode ser alterada em tempo real pelo menu `Interface`.
- Textos, icones, bordas e sombras principais herdam tons derivados da cor de destaque.
- Menus e campos de sistema usam fonte do sistema em vez de Manrope.
- O executavel e a janela usam o icone fornecido pelo usuario.
- O menu `Lembretes > Novo lembrete` cria lembretes com timer, horario fixo e recorrencia.
- Lembretes por timer escondem recorrencia e horario fixo, pois sao sempre diarios.
- A janela de lembrete reajusta o tamanho conforme o modo e a recorrencia escolhidos.
- Lembretes disparam notificacoes do Windows com som.
- Distribuicao simples: enviar `dist\CLT-Jnator 3000.exe`, `dist\ui_settings.json` e `dist\reminders.json`.
- A lista de tarefas preserva a posicao de scroll durante atualizacoes do contador.
- A sombra dos botoes foi suavizada para cerca de 30% de opacidade.
- Ao fechar, o app so pede salvamento se ainda nao foi salvo ou se houve mudanca desde o ultimo salvamento.
- No CSV, ha uma secao extra de resumo com horarios em `HH:mm`, arredondando segundos acima de 30 para o proximo minuto.
- A tarefa de almoco e reconhecida mesmo sem acento ou com erros comuns, como `Almoco`, `Almoso` e `Almooco`.

## Historico de iteracoes

### 1. Timer inicial em Tkinter

Foi criado um app minimo usando `tkinter`, biblioteca grafica padrao do Python. A primeira versao tinha uma janela simples, um contador no formato `HH:MM:SS` e um unico botao para iniciar e parar o timer.

O codigo foi estruturado com uma classe `TimerApp` e uma funcao `main()`, permitindo executar o app diretamente com:

```powershell
python timer_app.py
```

### 2. Organizacao em pasta no disco D:

O arquivo foi movido para:

```text
D:\PROJETOS PYTHON\timer_app.py
```

Isso transformou a pasta em um ponto fixo de projeto, facilitando empacotamento, execucao e manutencao.

### 3. Criacao de tarefas sequenciais

O timer deixou de ser apenas um contador unico e passou a trabalhar com tarefas. O botao `Iniciar` passou a criar tarefas com nomes padrao:

```text
Tarefa 1
Tarefa 2
Tarefa 3
```

Tambem foi adicionada uma lista visual para mostrar as tarefas criadas, seus tempos e seus estados.

### 4. Separacao entre iniciar e parar

Foi criado um botao `Parar` separado. Ele fica desativado quando nao ha tarefa em andamento e so para a tarefa atual.

Tambem foi adicionada a regra de que, se o usuario clicar em `Iniciar` enquanto uma tarefa estiver rodando, a tarefa atual e encerrada e uma nova tarefa e criada.

### 5. Continuar tarefa parada

Foi adicionada a funcao `Continuar`. A partir dela, uma tarefa parada pode voltar a rodar sem perder o tempo anterior.

Para isso, a estrutura interna precisou mudar: em vez de guardar apenas um tempo acumulado, cada tarefa passou a guardar uma lista de partes. Cada parte tem:

```text
inicio
fim
descricao
```

Essa mudanca abriu caminho para tarefas multipartes.

### 6. Timestamps no formato padrao do app

Os tempos passaram a ser registrados como timestamps no formato:

```text
YYYYMMDD_HH:mm:ss
```

Exemplo:

```text
20260511_20:01:06
```

O app ainda mostra duracoes em `HH:MM:SS`, mas os registros de inicio e fim das partes usam timestamp.

### 7. Empacotamento como executavel

O PyInstaller foi instalado e usado para gerar um executavel Windows sem terminal:

```powershell
python -m PyInstaller --onefile --windowed --name TimerDeTarefas timer_app.py
```

O executavel final passou a ficar em:

```text
D:\PROJETOS PYTHON\dist\TimerDeTarefas.exe
```

### 8. Descricao obrigatoria ao encerrar partes

Foi criada uma janela modal de descricao sempre que uma parte de tarefa e encerrada. Essa janela aparece ao clicar em `Parar` ou quando uma tarefa em andamento e interrompida por outra acao.

A janela:

- bloqueia o restante do app enquanto esta aberta;
- nao fecha pelo `X`;
- exige pelo menos 50 caracteres;
- libera o botao `Confirmar` apenas quando a regra e cumprida;
- salva o texto dentro da parte encerrada.

### 9. Renomeacao por menu de contexto

O campo fixo de renomear foi removido da tela principal. A renomeacao passou para um menu de contexto aberto com o botao direito do mouse sobre uma tarefa.

Essa mudanca deixou a tela principal mais limpa e moveu a acao de renomear para perto do item afetado.

### 10. Confirmacao com Enter

A tecla `Enter` passou a confirmar e fechar as janelas de descricao e renomeacao.

Na descricao, o Enter so fecha se o texto ja tiver pelo menos 50 caracteres. Caso contrario, a janela continua aberta.

### 11. Exportacao ao fechar

Foi criada uma rotina de exportacao ao fechar o app. O usuario escolhe onde salvar, qual nome usar e o formato do arquivo.

Formatos aceitos:

- `csv`
- `txt`
- `md`

O CSV usa UTF-8 e separa tarefa principal e subtarefas em colunas diferentes. As subtarefas ficam nas linhas abaixo da tarefa principal, deslocadas uma coluna para a direita.

Os formatos `txt` e `md` usam estrutura Markdown com titulo, resumo e detalhes das tarefas.

### 12. Salvar como dentro do app e controle de modificacoes

Foi adicionado o botao `Salvar como` na janela principal.

Tambem foi implementado um controle simples de modificacoes:

- criar tarefa marca o app como modificado;
- continuar tarefa marca como modificado;
- parar tarefa marca como modificado;
- renomear tarefa marca como modificado;
- salvar limpa o estado de modificacao.

Com isso, ao fechar o app, a janela de salvamento so aparece se:

- o app nunca foi salvo naquela execucao; ou
- houve alguma alteracao desde o ultimo salvamento.

Se nada mudou desde o ultimo salvamento, o aplicativo fecha direto.

### 13. Secao especial de horarios no CSV

Foi adicionada uma secao separada no final do CSV, afastada dos dados principais por linhas em branco. Essa secao registra quatro valores:

```text
Primeiro registro de hora do arquivo
Primeiro registro de hora do arquivo que a tarefa chamar "Almoço"
Fim do registro "Almoço"
Fim do registro do arquivo
```

Os horarios dessa secao usam apenas `HH:mm`. Para montar esse formato, foi criada uma funcao propria que arredonda segundos: valores acima de 30 segundos sobem para o minuto seguinte; valores ate 30 segundos permanecem no minuto atual.

Tambem foi criada uma deteccao tolerante para a tarefa `Almoço`. O app remove acentos, ignora maiusculas/minusculas e aceita erros comuns de digitacao, como `Almoco`, `Almoso`, `Almooco` e nomes com palavras extras como `Almoco equipe`.

### 14. Cabecalhos curtos no resumo CSV

A secao especial do CSV foi ajustada para usar nomes de coluna mais curtos e legiveis:

```text
Inicio
Almoco
Retorno Almoco
Fim
```

Essa mudanca deixou a planilha mais direta para leitura humana, sem repetir as descricoes longas usadas na especificacao inicial.

### 15. Renomeacao visual para CLT-Jnator 3000 e reorganizacao dos comandos

O aplicativo passou a se chamar `CLT-Jnator 3000`. O titulo da janela e o executavel foram atualizados para refletir esse nome.

O comando `Continuar` saiu da barra principal e foi movido para o mesmo menu de contexto de `Renomear`, aberto com o botao direito sobre uma tarefa. O item `Continuar` so fica ativo quando a tarefa selecionada esta parada.

Os botoes principais `Iniciar` e `Parar` foram trocados por botoes circulares com icones. Para isso, foi criado um componente `RoundIconButton` baseado em `tk.Canvas`, porque os botoes padrao do Tkinter nao oferecem um formato circular real.

A acao `Salvar como` saiu da barra de botoes e foi colocada no menu superior `Arquivo`, seguindo o padrao visual de aplicativos Windows.

Foi adicionada a fonte `Font Awesome Free Solid` ao projeto em:

```text
D:\PROJETOS PYTHON\assets\fa-solid-900.ttf
```

O app carrega essa fonte em modo privado ao iniciar, e o build do PyInstaller inclui o arquivo dentro do executavel. Isso evita exigir que outra pessoa instale a fonte manualmente para ver os icones.

### 16. Menu de contexto estavel, excecao de descricao e saida sem salvar

O menu de contexto estava piscando quando aberto durante uma tarefa em andamento. A causa provavel era a atualizacao do contador a cada 200 ms, que tambem redesenhava a lista de tarefas e reconfigurava o menu. A correcao foi pausar a atualizacao da lista enquanto o menu de contexto esta aberto, mantendo apenas o contador principal atualizado.

A janela de descricao ganhou uma checkbox opt-in para permitir confirmar com menos de 50 caracteres. Ela sempre abre desmarcada, preservando a regra padrao de descricao minima.

O item `Arquivo > Sair` passou a ser uma saida sem salvamento. Antes de fechar, ele mostra um popup de alerta pedindo confirmacao. O fechamento pelo `X` da janela continua seguindo o fluxo normal de salvamento quando ha dados novos ou nao salvos.

### 17. Teste visual com degrade, cartao e botoes circulares

Foi aplicado um teste de interface inspirado por referencias de UI com tons de destaque. A janela passou a usar um fundo em degrade roxo, um cartao central claro com cantos arredondados e uma sombra projetada suave.

Os botoes principais mantiveram a forma circular, mas ganharam sombra, cores de destaque e estados de hover/desativado mais coerentes. As listas tambem foram ajustadas para usar fundo claro, selecao roxa e bordas discretas.

Para desenhar cantos arredondados no Tkinter, foi adicionada uma camada `Canvas` que cria formas suavizadas. A estrutura funcional do app foi mantida; a mudanca foi focada no visual da janela principal.

### 18. Migracao pratica de UI para PySide6/Qt

Foi tentada a instalacao de PyWebView, recomendada inicialmente para usar HTML/CSS. No ambiente atual, com Python `3.14.4`, a instalacao falhou porque a dependencia `pythonnet` precisou compilar localmente e quebrou durante uma etapa do NuGet.

Como alternativa proxima ao objetivo visual, foi instalada a biblioteca PySide6. Ela permite criar um app desktop Windows com sombras reais via `QGraphicsDropShadowEffect`, estilos via Qt Style Sheets, menus nativos e melhor controle de layout.

Foi criada uma nova entrada principal:

```text
D:\PROJETOS PYTHON\clt_jnator_qt.py
```

Essa versao manteve as funcoes principais existentes:

- criar tarefa;
- parar tarefa com descricao obrigatoria;
- permitir excecao manual abaixo de 50 caracteres;
- continuar e renomear pelo menu de contexto;
- salvar em `csv`, `txt` e `md`;
- sair sem salvar com alerta;
- pedir salvamento ao fechar quando necessario;
- reconhecer `Almoço` e erros comuns no resumo CSV.

O executavel `CLT-Jnator 3000.exe` passou a ser gerado a partir da versao PySide6. O arquivo ficou maior porque inclui o runtime Qt dentro do empacotamento.

### 19. Refinos de UI, tema e limpeza de projeto

Foi aplicado o padrao de limpeza do projeto. Os diretorios temporarios `build` e `__pycache__` foram removidos depois do empacotamento. Foram mantidos apenas os arquivos relevantes: fonte Qt atual, executavel, spec atual, assets, configuracao de UI, memoria e backups Tkinter.

Foram mantidos os backups Tkinter:

```text
D:\PROJETOS PYTHON\timer_app.py
D:\PROJETOS PYTHON\timer_app_tkinter_v1.py
```

A sombra dos botoes circulares foi reduzida para aproximadamente 30% de opacidade. Isso mantem profundidade visual sem deixar a sombra pesada.

A lista de tarefas deixou de ser reconstruida do zero a cada tick do relogio. Agora, quando a quantidade de tarefas nao muda, o app atualiza somente o texto das linhas existentes e preserva o valor do scroll. Isso evita que a lista volte para outra posicao enquanto o usuario esta navegando.

O campo de partes da tarefa ficou mais baixo para liberar mais espaco vertical para a lista principal de tarefas.

A fonte Manrope foi adicionada aos assets:

```text
D:\PROJETOS PYTHON\assets\Manrope-Variable.ttf
```

Foi criado o menu `Interface`, com um campo unico de hexcode para configurar a cor de destaque. A mudanca acontece em tempo real e atualiza tons derivados como hover, selecao, fundo em degrade e sombras. A configuracao e persistida em:

```text
D:\PROJETOS PYTHON\ui_settings.json
```

Tambem foi corrigido o fluxo de parada: ao abrir a janela de descricao, a parte da tarefa ja esta encerrada com timestamp de fim. Assim o timer nao continua contando no fundo enquanto o usuario escreve a descricao.

### 20. Tema mais consistente e menus com fonte de sistema

Foram removidos roxos fixos remanescentes em textos, icones, bordas e sombras da interface principal. Agora esses elementos usam tons calculados a partir da cor base configurada no menu `Interface`.

Tambem foi separado o uso de fontes: a UI principal continua com Manrope, mas menus e campos de configuracao considerados "de sistema" usam fonte de sistema (`Segoe UI`). Isso deixa `Arquivo`, `Interface` e o campo de hexcode mais proximos do padrao Windows.

### 21. Icone proprio do aplicativo

Foi criado inicialmente um asset similar ao icone de referencia. Depois, o usuario adicionou a imagem exata primeiro em JPG e depois em PNG. A versao PNG passou a ser a fonte atual do icone:

```text
D:\PROJETOS PYTHON\assets\cltjnator_icon.png
```

Essa imagem foi usada como fonte real do icone do aplicativo, convertida para PNG e ICO.

Arquivos adicionados:

```text
D:\PROJETOS PYTHON\assets\cltjnator_icon.jpg
D:\PROJETOS PYTHON\assets\cltjnator_icon.png
D:\PROJETOS PYTHON\assets\app_icon.png
D:\PROJETOS PYTHON\assets\app_icon.ico
D:\PROJETOS PYTHON\assets\app_icon_current.png
D:\PROJETOS PYTHON\assets\app_icon_current.ico
```

O `.ico` atual foi aplicado na janela Qt com `QIcon` e tambem passado ao PyInstaller com `--icon`, para aparecer no executavel Windows.

O icone foi validado extraindo o recurso diretamente do `.exe` apos o build.

### 22. Criacao de lembretes

Foi adicionado o menu:

```text
Lembretes > Novo lembrete
```

Cada lembrete possui:

- nome;
- descricao;
- modo `Timer` ou `Horario fixo`;
- recorrencia `Nao recorrente`, `Diario`, `Semanal` ou `Mensal no dia X`.

O app verifica os lembretes periodicamente e mostra um popup quando algum vence. Lembretes recorrentes recalculam automaticamente o proximo disparo depois do alerta.

Nesta primeira versao, os lembretes ficam em memoria enquanto o app esta aberto. Ainda nao ha persistencia em arquivo entre execucoes.

### 23. Ajuste de formulario dos lembretes

O formulario de lembrete passou a mostrar apenas os campos relevantes para o modo escolhido:

- `Timer`: mostra somente o campo de minutos do timer e grava recorrencia diaria automaticamente.
- `Horario fixo`: mostra o campo de horario e as opcoes de recorrencia.

Isso reduz ambiguidade e evita combinacoes que nao fazem sentido, como timer com recorrencia manual.

### 24. Redimensionamento do formulario de lembretes

O dialogo de lembretes foi ajustado para recalcular seu tamanho quando os campos visiveis mudam. Antes, ao alternar entre opcoes que revelavam campos adicionais, o conteudo ficava comprimido no mesmo espaco.

Agora o layout e invalidado e ativado novamente, seguido de `adjustSize()`, com limites minimos e maximos de altura. O campo de descricao tambem ficou um pouco menor para liberar espaco para as opcoes condicionais.

### 25. Notificacoes nativas do Windows

O disparo dos lembretes deixou de ser apenas um `QMessageBox` interno. Foi adicionada a biblioteca `winotify` para enviar Toast Notifications nativas do Windows.

Cada lembrete disparado agora usa:

- titulo com o nome do lembrete;
- descricao como corpo da notificacao;
- icone do app;
- som padrao de notificacao do Windows.

Se a notificacao nativa falhar por permissao, politica do sistema ou outro erro, o app ainda mostra um popup interno como fallback.

### 26. Limpeza final e distribuicao

Foram removidos assets antigos que nao eram mais usados, incluindo versoes anteriores de icone geradas durante os testes. Tambem foi removido um atalho `.lnk` da raiz do projeto.

Assets mantidos:

```text
D:\PROJETOS PYTHON\assets\app_icon_current.ico
D:\PROJETOS PYTHON\assets\cltjnator_icon.png
D:\PROJETOS PYTHON\assets\fa-solid-900.ttf
D:\PROJETOS PYTHON\assets\Manrope-Variable.ttf
```

Para enviar o app a outra pessoa, o caminho simples e enviar:

```text
D:\PROJETOS PYTHON\dist\CLT-Jnator 3000.exe
D:\PROJETOS PYTHON\dist\ui_settings.json
```

O executavel ja contem Python, PySide6, fontes e icone embutidos. O arquivo `ui_settings.json` ao lado do executavel guarda a cor de destaque configurada.

### 27. Persistencia de lembretes

Os lembretes deixaram de existir apenas em memoria. Agora sao salvos em:

```text
D:\PROJETOS PYTHON\dist\reminders.json
```

Durante o desenvolvimento, tambem existe:

```text
D:\PROJETOS PYTHON\reminders.json
```

O app carrega esse arquivo ao iniciar, recalcula lembretes vencidos para o proximo horario valido e salva novamente quando um lembrete e criado ou quando um lembrete recorrente dispara.

Isso permite configurar lembretes padrao antes de distribuir o app. Para enviar para outra pessoa, incluir `reminders.json` junto do executavel.

## Observacoes tecnicas

- Interface atual feita com `PySide6/Qt`.
- Versao anterior em `tkinter` preservada em `timer_app.py` como fallback temporario.
- Empacotamento feito com `PyInstaller`.
- Icones vindos de `Font Awesome Free Solid`, embutidos no executavel.
- Arquivos exportados em UTF-8.
- CSV gerado com o modulo padrao `csv`.
- Exportacao `.txt` e `.md` usa sintaxe Markdown.
- Datas internas usam `datetime`.
- A duracao exibida ainda e calculada dinamicamente a partir das partes da tarefa.
