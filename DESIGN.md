---
name: Vanuza Andrade
description: Loja de confecção própria de viscose desenhada como folha de molde, com a grade de tamanhos como interface.
colors:
  acao: "#5b2a86"
  acao-escura: "#451f67"
  acao-clara: "#efe7f6"
  linha-p: "#c2185b"
  linha-m: "#00796b"
  linha-g: "#c75b00"
  linha-gg: "#1f5fbf"
  papel: "#f1f1ee"
  papel-2: "#e4e3de"
  papel-3: "#fbfbf9"
  tinta: "#26222e"
  tinta-2: "#57515f"
  tinta-3: "#7c7684"
  fio: "#d6d4ce"
  ouro: "#b88a2e"
  fita: "#f2d873"
  whatsapp: "#1f7a4d"
  whatsapp-escuro: "#17603c"
  erro: "#b3261e"
  ok: "#2f6f4f"
  branco: "#ffffff"
typography:
  display:
    fontFamily: "Bodoni Moda, Didot, Bodoni 72, serif"
    fontSize: "clamp(3.4rem, 10.5vw, 9rem)"
    fontWeight: 500
    lineHeight: 0.95
    letterSpacing: "-0.025em"
  display-italico:
    fontFamily: "Bodoni Moda, Didot, Bodoni 72, serif"
    fontSize: "clamp(3.5rem, 13vw, 11.5rem)"
    fontWeight: 400
    lineHeight: 0.85
    letterSpacing: "-0.035em"
  headline:
    fontFamily: "Bodoni Moda, Didot, Bodoni 72, serif"
    fontSize: "clamp(2.4rem, 6vw, 5rem)"
    fontWeight: 500
    lineHeight: 0.95
    letterSpacing: "-0.025em"
  title:
    fontFamily: "Bodoni Moda, Didot, Bodoni 72, serif"
    fontSize: "clamp(1.6rem, 3vw, 2.2rem)"
    fontWeight: 500
    lineHeight: 1.05
    letterSpacing: "-0.025em"
  nome-peca:
    fontFamily: "Bodoni Moda, Didot, Bodoni 72, serif"
    fontSize: "1.45rem"
    fontWeight: 500
    lineHeight: 1.1
    letterSpacing: "-0.01em"
  body:
    fontFamily: "Archivo, system-ui, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.6
    fontVariation: "\"wdth\" 100"
  body-texto:
    fontFamily: "Archivo, system-ui, sans-serif"
    fontSize: "1.0625rem"
    fontWeight: 400
    lineHeight: 1.6
  label:
    fontFamily: "Archivo, system-ui, sans-serif"
    fontSize: "0.8rem"
    fontWeight: 600
    lineHeight: 1.35
    letterSpacing: "0.08em"
    fontVariation: "\"wdth\" 68"
  menu:
    fontFamily: "Archivo, system-ui, sans-serif"
    fontSize: "0.82rem"
    fontWeight: 600
    letterSpacing: "0.08em"
    fontVariation: "\"wdth\" 75"
  anotacao-molde:
    fontFamily: "Archivo, system-ui, sans-serif"
    fontSize: "10px"
    fontWeight: 600
    lineHeight: 1
    letterSpacing: "0.12em"
    fontVariation: "\"wdth\" 68"
rounded:
  raio: "4px"
  fita: "3px"
  pilula: "999px"
  painel-bloco: "12px"
spacing:
  margem: "clamp(1rem, 4vw, 3rem)"
  ritmo: "clamp(4rem, 9vw, 8rem)"
  largura: "82rem"
  folga-molde: "34px"
  folga-molde-pequeno: "20px"
  folga-molde-celular: "22px"
  quadricula: "38px"
components:
  button-primary:
    backgroundColor: "{colors.acao}"
    textColor: "{colors.branco}"
    rounded: "{rounded.raio}"
    padding: "0 1.6rem"
    height: "52px"
  button-primary-hover:
    backgroundColor: "{colors.acao-escura}"
    textColor: "{colors.branco}"
  button-primary-disabled:
    backgroundColor: "{colors.papel-2}"
    textColor: "{colors.tinta-3}"
  button-linha:
    backgroundColor: "transparent"
    textColor: "{colors.tinta}"
    rounded: "{rounded.raio}"
    padding: "0 1.6rem"
    height: "52px"
  button-linha-hover:
    backgroundColor: "{colors.tinta}"
    textColor: "{colors.papel}"
  button-whatsapp:
    backgroundColor: "{colors.whatsapp}"
    textColor: "{colors.branco}"
    rounded: "{rounded.raio}"
    height: "52px"
  button-whatsapp-hover:
    backgroundColor: "{colors.whatsapp-escuro}"
  botao-pedido:
    backgroundColor: "{colors.acao}"
    textColor: "{colors.branco}"
    rounded: "{rounded.pilula}"
    padding: "0 1rem"
    height: "44px"
  campo:
    backgroundColor: "{colors.papel-3}"
    textColor: "{colors.tinta}"
    rounded: "{rounded.raio}"
    padding: "0.7rem 0.9rem"
    height: "48px"
  tamanho:
    backgroundColor: "{colors.papel-3}"
    textColor: "{colors.tinta}"
    rounded: "{rounded.raio}"
    height: "60px"
    width: "5.5rem"
  tamanho-escolhido:
    backgroundColor: "{colors.branco}"
  aba:
    backgroundColor: "transparent"
    textColor: "{colors.tinta}"
    rounded: "{rounded.pilula}"
    padding: "0.55rem 1rem"
    height: "44px"
  aba-atual:
    backgroundColor: "{colors.tinta}"
    textColor: "{colors.papel}"
  folha-envio:
    backgroundColor: "{colors.papel-3}"
    rounded: "{rounded.raio}"
    padding: "clamp(1.25rem, 3vw, 2rem)"
  fita-metrica:
    backgroundColor: "{colors.fita}"
    textColor: "{colors.tinta}"
    rounded: "{rounded.fita}"
    height: "52px"
  painel-lado:
    backgroundColor: "{colors.tinta}"
    textColor: "{colors.papel}"
    width: "15rem"
  painel-bloco:
    backgroundColor: "{colors.papel-3}"
    rounded: "{rounded.painel-bloco}"
    padding: "clamp(1rem, 2.5vw, 1.6rem)"
---

# Design System: Vanuza Andrade

## Overview

**Creative North Star: "Folha de Molde"**

A loja é uma folha de molde de confecção. O chão é papel de modelagem branco-acinzentado, a escrita é tinta grafite, e a única coisa colorida no mundo são as linhas de graduação do molde: P, M, G e GG, cada uma com cor e traço próprios, desenhadas em volta da foto de cada peça como contornos aninhados. A grade de tamanhos não é um seletor ao lado do produto; é o próprio desenho. Escolher um tamanho faz a linha daquele tamanho se desenhar em volta da peça enquanto as outras recuam.

A tipografia vem de dois lugares do ateliê: a Didone de revista de moda (Bodoni Moda) para títulos e nomes de peças, e a grotesca condensada em caixa alta (Archivo estreitado) para as anotações que se escrevem na margem do molde, como "VESTIDO · VISCOLINHO · CORTE 1X". O roxo da marca não decora nada: ele aparece só no que se aperta. A densidade é de vitrine editorial na loja pública (modo Persuade) e de ferramenta enxuta no painel /admin (modo Operate), que herda papel, tinta e linhas sem encenar o molde.

A loja recusa a fórmula banner + faixa de categorias + grade de cartões iguais. As peças ficam desencontradas como num encaixe de molde, a primeira tela já mostra uma peça com os quatro contornos e o botão de compra ativo.

**Key Characteristics:**
- Papel de molde claro e tinta grafite como base; cor só em linhas, carimbos e ações.
- Quatro linhas de graduação fixas no site inteiro: P magenta contínua, M verde-petróleo tracejada, G laranja traço-ponto, GG azul pontilhada.
- Fotos tratadas como peças de molde: contornos graduados, piques triangulares nas laterais, seta de fio reto, anotação condensada na margem.
- Bodoni Moda nos títulos, Archivo condensado em caixa alta nas anotações.
- Interação-assinatura: escolher o tamanho desenha o contorno (stroke-dashoffset via máscara) e recua os demais.

## Colors

Paleta de papel e grafite quase acromática, com quatro cores de linha de graduação reservadas ao molde e um roxo de marca reservado à ação.

### Primary
- **Roxo de Ação** (`acao`): fundo de todo botão primário, do botão "Pedido" no topo, do preenchimento da fita métrica, da opção de entrega escolhida e do anel de foco. É a cor do que se aperta e de nada mais.
- **Roxo de Ação Escuro** (`acao-escura`): hover do botão primário e do botão "Pedido".
- **Lavanda de Ação** (`acao-clara`): halo de foco dos campos (sombra de 3px) e fundo da opção de entrega marcada; etiqueta "destaque" no painel.

### Secondary: as linhas de graduação
Cada tamanho tem uma cor e um traço, e o par cor + traço é o mesmo em todo lugar: contorno em volta da foto, amostra na legenda de tamanhos, disponibilidade no card, letra do tamanho sobre a linha.
- **Magenta P** (`linha-p`): linha contínua. Também é a cor de seleção de texto, do cursor dos campos, do sublinhado do menu atual, do aviso "poucas peças" e do contador de pendências no painel.
- **Verde-Petróleo M** (`linha-m`): tracejado `7 4`.
- **Laranja G** (`linha-g`): traço-ponto `11 3.5 2 3.5`.
- **Azul GG** (`linha-gg`): pontilhado `0.5 4.5` com ponta redonda e traço mais grosso (2.25 no contorno, 3 na amostra).
- Tamanho fora da grade P–GG usa a tinta média com tracejado `3 3`.

### Tertiary: carimbos
- **Ouro do Monograma** (`ouro`): só o anel de 1.5px em volta do monograma circular no topo.
- **Amarelo de Fita Métrica** (`fita`): fundo da fita métrica do atacado, e só dela.
- **Verde WhatsApp** (`whatsapp`, hover `whatsapp-escuro`): botão de enviar o pedido pelo WhatsApp.
- **Erro** (`erro`) e **Ok** (`ok`): mensagens de estado, campo inválido, economia de atacado, botão de perigo no painel.

### Neutral
- **Papel de Molde** (`papel`): fundo do corpo, da folha quadriculada e do topo translúcido (94%).
- **Papel Sombreado** (`papel-2`): fundo de foto enquanto carrega, botão desabilitado, trilho da barra de rolagem.
- **Papel Claro** (`papel-3`): superfícies de trabalho: campos, botões de tamanho e cor, quantidade, folha de envio, recibo, blocos do painel.
- **Tinta Grafite** (`tinta`): texto, piques, seta de fio, bordas fortes de 1.5px no topo de listas e fichas, rodapé e lateral do painel.
- **Tinta Média** (`tinta-2`): texto de apoio, anotações, preço de atacado.
- **Tinta Clara** (`tinta-3`): placeholder, estado esgotado, hover de borda.
- **Fio** (`fio`): divisórias de 1px e bordas de repouso de 1.5px.
- **Quadrícula** (`rgb(38 34 46 / 0.055)`): linhas do papel quadriculado de 38px.

### Named Rules
**A Regra das Linhas Fixas.** P é sempre magenta contínua, M sempre verde-petróleo tracejada, G sempre laranja traço-ponto, GG sempre azul pontilhada. Nenhuma tela troca o par cor + traço, e nenhuma dessas quatro cores vira cor de interface genérica (exceto o magenta nos micro-acentos listados acima).

**A Regra do Roxo que se Aperta.** O roxo da marca aparece só em elementos clicáveis de ação e no foco. Título, ilustração, fundo de seção ou ícone decorativo nunca são roxos.

**A Regra da Cor só em Linha e Carimbo.** Fora do roxo de ação, cor só existe como linha (graduação), carimbo (monograma, fita métrica, etiqueta de status, mensagem de estado) ou amostra de tecido. Superfícies são papel; texto é tinta.

## Typography

**Display Font:** Bodoni Moda (com Didot, Bodoni 72, serif), tamanho óptico automático, pesos 400–700 com itálico.
**Body Font:** Archivo (com system-ui, sans-serif), eixo de largura 62–125, largura 100 no texto corrido.
**Label Font:** Archivo estreitado (`wdth` 68 a 75), caixa alta, espaçado.

**Character:** A Didone de alto contraste é a voz de revista de moda; a grotesca condensada em caixa alta é a mão da modelista anotando a margem do molde. Uma vende, a outra explica.

### Hierarchy
- **Display** (500, `clamp(3.4rem, 10.5vw, 9rem)`, 0.95): título de abertura "Conforto *e estilo*", com a segunda linha recuada 0.9em e em itálico 400. No desktop largo (≥1180px) cai para `clamp(4.5rem, 6.6vw, 7.5rem)` para caber na primeira tela.
- **Display itálico** (400 itálico, `clamp(3.5rem, 13vw, 11.5rem)`, 0.85, -0.035em): a palavra grande do bloco de fabricação, com a segunda linha em romano 500.
- **Headline** (500, `clamp(2.4rem, 6vw, 5rem)`, 0.95): títulos de seção e de página; na página da peça, `clamp(2.3rem, 4.6vw, 4rem)`. `em` dentro dele vira itálico 400.
- **Title** (500, `clamp(1.6rem, 3vw, 2.2rem)`, 1.05): subtítulos. Os passos de "Como comprar" usam Bodoni 500 a 1.5rem.
- **Nome de peça** (Bodoni, 1.45rem, 1.1): nome no card; 1.25rem na linha do pedido. Total do pedido em Bodoni 500 a 2.3rem com algarismos tabulares.
- **Body** (Archivo 400, 1rem, 1.6): texto corrido. Blocos de texto longo a 1.0625rem, cor tinta média, máximo 62ch.
- **Label / Anotação** (Archivo 600, 0.8rem, `wdth` 68, 0.08em, caixa alta, tinta média): legendas de campos de tamanho e cor, categoria e tecido no card, endereço, termos da ficha técnica, rótulos do rodapé.
- **Menu** (Archivo 600, 0.82rem, `wdth` 75, 0.08em, caixa alta): links do topo. Cabeçalho de tabela do painel usa o mesmo desenho a 0.78rem.
- **Anotação no molde** (Archivo 600, 10px, `wdth` 68, 0.12em): texto dentro do SVG do contorno; letra do tamanho a 11px 700; preço na margem a 11px.

Todo número de preço, quantidade e total usa algarismos tabulares e alinhados.

### Named Rules
**A Regra das Duas Mãos.** Bodoni só para o que se lê como revista (títulos, nomes de peça, endereço, total). Archivo condensado em caixa alta só para o que se lê como anotação de molde. Nunca Bodoni em caixa alta espaçada, nunca Archivo condensado em título.

**A Regra Sem Sobretítulo.** Anotação condensada não fica em cima de título como chamada de seção. Ela anota a peça, o campo ou a margem; o título abre a seção sozinho.

## Layout

- **Container:** largura máxima de 82rem centrada; margem lateral fluida `clamp(1rem, 4vw, 3rem)`.
- **Ritmo vertical:** seções com `clamp(4rem, 9vw, 8rem)` em cima e embaixo; seções vizinhas separadas por um fio de 1px.
- **Papel quadriculado:** quadrícula de 38px em linhas de 1px a 5,5% de tinta. Aparece só nas folhas de trabalho: abertura do início, página da peça, visita à loja, confirmação do pedido, página de erro e entrada do painel. Catálogo, coleção e textos ficam em papel liso.
- **Abertura:** duas colunas (1.05fr título | 0.95fr peça) até 1180px; a partir de 1180px, três colunas (título | peça | compra) com tudo na primeira tela, a foto limitada a `calc(68vh * 0.8 + 68px)`. Abaixo de 900px, uma coluna com a peça antes do título.
- **Folha de peças:** grade `auto-fill` com mínimo de 17rem. Na página inicial, encaixe desencontrado: a cada três peças, a segunda desce `clamp(0rem, 8vw, 6rem)` e a terceira `clamp(0rem, 3vw, 2.5rem)`; abaixo de 640px, tudo alinhado.
- **Página da peça:** galeria 1.1fr fixa (sticky a 5rem do topo) e ficha 0.9fr; uma coluna abaixo de 900px, com barra fixa de compra no rodapé do celular.
- **Pedido:** linhas 1.25fr e folha de envio 1fr (sticky); uma coluna abaixo de 900px.
- **Folga do molde:** o contorno ocupa uma margem de 34px em volta da foto (20px no card, 22px abaixo de 520px). Anotações e preços do card se alinham à mesma folga.
- **Topo:** barra fina fixa de 4rem, papel translúcido com desfoque de 8px.
- **Pontos de quebra:** 420px (topo compacto), 520px (some o texto do molde), 640px, 720px (some "Como comprar" e o rótulo "Pedido"), 800px, 900px (uma coluna), 1180px (abertura em três colunas). Painel: 700px e 860px.
- **Alvos de toque:** mínimo de 44px em links do menu, abas, cores, quantidade e botões; botão primário com 52px.

## Elevation & Depth

Plano por padrão, como papel sobre a mesa. Profundidade vem de bordas internas de 1.5px, fios de 1px e diferença de tom entre papel e papel claro. Sombra existe em três papéis só.

### Shadow Vocabulary
- **Folha sobre a mesa** (`box-shadow: 0 1px 2px rgb(38 34 46 / 0.08), 0 8px 24px -12px rgb(38 34 46 / 0.22)`): a foto dentro do molde, a folha de envio e o recibo. Uma folha de papel levemente erguida.
- **Botão primário** (`box-shadow: 0 1px 0 rgb(0 0 0 / 0.1), 0 10px 22px -14px rgb(38 34 46 / 0.45)`): sombra curta embaixo do botão de ação; some no estado desabilitado.
- **Bloco do painel** (`box-shadow: 0 1px 2px rgb(38 34 46 / 0.06), 0 0 0 1px var(--fio)`): só no /admin.

### Named Rules
**A Regra da Borda por Dentro.** Bordas de controles são `inset` (box-shadow interno de 1.5px em fio; 2–2.5px na cor da linha ou em tinta quando escolhido). Nada de borda que empurra o layout ao mudar de estado.

## Shapes

Cantos quase retos de 4px em botões, campos, botões de tamanho, quantidade, folha de envio e recibo: papel cortado, não bolha. Pílula (999px) só em três lugares: o botão "Pedido" do topo, as abas de categoria e os botões de cor de tecido; amostra de tecido é círculo de 30px. A fita métrica tem 3px. A foto do molde é retangular 4:5, sem canto arredondado. O contorno do molde tem silhueta própria: ombro chanfrado em cima, laterais que abrem para a barra e barra levemente curva para baixo, crescendo a cada tamanho. Piques são triângulos de tinta nas laterais do contorno de fora. O painel usa cantos maiores (12px nos blocos, 6px nas fotos, 10px na área de envio), o que é dele e não volta para a loja.

## Components

### Molde (assinatura)
A foto da peça recortada como peça de molde, desenhada em SVG por cima da foto.
- **Estrutura:** foto 4:5 com sombra de folha, enquadrada a 50% 18%, dentro de uma folga de 34px. Por cima, um contorno por tamanho da peça, do P (mais justo) ao GG (mais aberto), em espessura 1.5 e opacidade 0.55.
- **Graduação:** cada tamanho abre 3,5 a 6px a mais no ombro e mais ainda na barra (4px por tamanho na folga grande, 2.5px na pequena); o chanfro do ombro e a curva da barra crescem com o tamanho.
- **Marcas:** letra do tamanho sobre a própria linha, na lateral direita, com halo de papel; dois piques no meio das laterais do contorno de fora. Na folga grande: seta de fio reto de duas pontas dentro da foto com o rótulo "FIO", anotação "REF · TECIDO · CORTE 1X" acima do contorno e preço anotado na margem de baixo.
- **Esgotado:** a linha de um tamanho sem estoque cai para opacidade 0.12.
- **Pequeno (card):** folga de 20px, sem texto no SVG. Abaixo de 520px, o texto some em qualquer molde.
- **Tamanho escolhido:** as outras linhas recuam para 0.16; a escolhida vai a opacidade 1 e espessura 2.75 (3.25 no GG) e se desenha.

### Legenda de tamanhos
Os botões de tamanho são a legenda do molde.
- **Forma:** grade de 4 colunas de até 5.5rem, botões de 60px de altura, canto de 4px, papel claro, borda interna de 1.5px em fio. Dentro, uma amostra de linha de 8px com a cor e o traço do tamanho e a letra em Archivo 700 a 1.05rem.
- **Hover:** borda vai para tinta clara.
- **Escolhido:** fundo branco e borda interna de 2.5px na cor da linha do tamanho.
- **Esgotado:** letra riscada, tinta clara, amostra a 30%, sem fundo, cursor bloqueado.
- **Foco:** anel de 2px no roxo de ação, afastado 2px.
- A legenda leva a anotação "Tamanho · escolha pela linha do molde".

### Card de peça
- Molde pequeno sem moldura extra, nome em Bodoni 1.45rem (hover roxo), preços com varejo 700 a 1.15rem e atacado em tinta média ("atacado **R$** a partir de N peças"), anotação de categoria · tecido.
- **Disponibilidade:** uma fileira com amostra de linha de 1.4rem + letra para cada tamanho; esgotado vem riscado em tinta clara com amostra a 35%.

### Fita métrica (atacado)
Uma fita métrica amarela de 52px com um traço de tinta por peça do mínimo de atacado, número tabular 700 em cada divisão e meia-marca de 9px no centro. Uma faixa roxa de 12px na base preenche da esquerda conforme as peças do pedido (escala horizontal, 0.6s com a curva de saída). Legenda embaixo com o que falta.

### Botões
- **Forma:** cantos de 4px; altura de 52px (44px no painel, 36px no pequeno).
- **Primário:** roxo de ação, texto branco Archivo 600 a 1rem, ícone de traço de 1.25em antes do texto, sombra curta de botão.
- **Hover / Ativo / Foco:** hover para roxo escuro; ativo desce 1px; foco com anel de 2px roxo afastado 3px.
- **Desabilitado:** papel sombreado, tinta clara, sem sombra.
- **Linha (secundário):** transparente com borda interna de 1.5px em tinta; hover inverte para tinta com texto papel.
- **WhatsApp:** verde próprio, mesmo desenho do primário.
- **Perigo (painel):** transparente com borda e texto em erro; hover enche de erro.
- **Botão "Pedido" do topo:** pílula roxa de 44px com ícone de sacola, rótulo e contador branco (vira translúcido quando vazio); pulsa a 1.08 por 0.6s ao receber uma peça.
- **Link com seta:** Archivo 600 com sublinhado de 1.5px em currentColor; hover roxo.

### Campos
- **Estilo:** 48px de altura, papel claro, borda de 1.5px em fio, canto de 4px, padding `0.7rem 0.9rem`, cursor magenta. Rótulo em Archivo 600 a 0.92rem, ajuda em tinta média 0.85rem.
- **Hover:** borda em tinta clara.
- **Foco:** borda roxa e halo de 3px em lavanda.
- **Erro:** borda em erro.
- **Cores de tecido:** pílulas de 44px com amostra circular de 30px; escolhida ganha borda interna de 2px em tinta e fundo branco.
- **Quantidade:** caixa de papel claro com botões de 48 × 52px e número tabular 700.
- **Opção de entrega:** cartão de 4px com borda interna em fio; marcada vira borda de 2px roxa sobre lavanda.

### Navegação
- **Topo:** monograma circular de 40px com anel de ouro, nome em Bodoni 1.3rem; links em Archivo condensado caixa alta; página atual com sublinhado magenta de 2px afastado 0.45em. No celular some "Como comprar" e o rótulo do pedido fica só no contador.
- **Abas do catálogo:** pílulas de 44px com borda interna em fio; atual em tinta cheia com texto papel.
- **Rodapé:** tinta grafite, nome em Bodoni `clamp(2rem, 4vw, 3rem)`, rótulos em anotação clara, três colunas que viram uma abaixo de 800px.

### Painel (/admin, modo Operate)
Mesma tinta e papel da vitrine, sem molde nem quadrícula (exceto na tela de entrar). Lateral em tinta de 15rem com links de 44px, atual em branco a 12%, contador em magenta P. Conteúdo em blocos de papel claro com canto de 12px e borda de fio. Tabelas com cabeçalho em Archivo condensado caixa alta sobre fio grosso de tinta. Etiquetas de status em pílula com fundo claro e texto escuro do mesmo matiz: novo magenta, confirmado azul, separado laranja, entregue verde, cancelado riscado. A grade de estoque marca tamanho zerado em magenta. Abaixo de 860px, a lateral vira barra superior com rolagem horizontal.

### Movimento
- **Curva de saída:** `cubic-bezier(0.16, 1, 0.3, 1)` em tudo que se desenha ou entra.
- **Desenho do contorno:** cada linha do molde é recortada por uma máscara cujo traço tem `pathLength` 1; o traço da máscara anima `stroke-dashoffset` de 1 a 0 em 0.9s. Assim o tracejado próprio de cada tamanho se mantém enquanto a linha se desenha.
- **Abertura:** a peça em destaque do início desenha a graduação uma vez ao carregar, do GG para o P, com 0.2s de espera e 0.18s entre linhas.
- **Escolha:** ao escolher o tamanho, só a linha escolhida se redesenha; as outras recuam em 0.4s de opacidade.
- **Outros:** botão "Pedido" pulsa 0.6s; fita métrica preenche em 0.6s; barra de compra do celular sobe em 0.35s; transições de estado de 0.15–0.2s.
- **Movimento reduzido:** toda animação e transição cai para 0.01ms, a rolagem suave é desligada e a apresentação de abertura não roda; os contornos aparecem já desenhados.

## Do's and Don'ts

### Do:
- **Do** usar o par fixo de cor e traço de cada tamanho (P magenta contínua, M verde-petróleo `7 4`, G laranja `11 3.5 2 3.5`, GG azul `0.5 4.5` redondo) em contorno, legenda, card e qualquer novo lugar que mostre tamanho.
- **Do** reservar o roxo de ação para botões, o botão "Pedido", seleção de opção, preenchimento da fita e anel de foco.
- **Do** escrever anotações em Archivo condensado (`wdth` 68), 600, caixa alta, 0.08em, ligadas por " · ", como se anotassem a margem do molde.
- **Do** desenhar contornos com a máscara de `pathLength` 1 e `stroke-dashoffset`, e mostrar o resultado final sem animação quando o movimento estiver reduzido.
- **Do** manter a folga do molde (34px, 20px no card) e alinhar anotação e preços a ela.
- **Do** usar bordas internas de 1.5px em fio para controles em repouso e cantos de 4px.
- **Do** manter algarismos tabulares em preços, quantidades e totais.

### Don't:
- **Don't** pôr anotação ou chamada em caixa alta acima de um título como sobretítulo; o título abre a seção sozinho.
- **Don't** usar o papel quadriculado fora das folhas de trabalho (abertura, peça, visita, confirmação, erro, entrada do painel); catálogo e textos ficam em papel liso.
- **Don't** pintar superfícies, títulos ou ícones decorativos com cor; cor só existe em linha, carimbo, amostra de tecido e ação.
- **Don't** usar uma cor de linha de graduação como cor de marca, fundo ou botão.
- **Don't** montar a loja como banner + faixa de categorias + grade de cartões iguais.
- **Don't** arredondar foto de peça nem usar pílula fora do botão "Pedido", abas e cores de tecido.
- **Don't** levar o molde, os contornos ou a quadrícula para dentro do painel de operação.
