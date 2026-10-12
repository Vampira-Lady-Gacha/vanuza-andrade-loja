# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

Python 3.12 + FastAPI + SQLite (SQLAlchemy 2), páginas renderizadas no servidor com Jinja2, gerenciado com uv. Escolhido pelo usuário entre as opções oferecidas. Hospedagem prevista em serviço de container simples (Render/Railway); ainda não decidida.

## Users

- **Cliente de varejo:** mulher que conhece a loja pelo Instagram ou passa no Mega Moda Shopping, vê a peça no celular e quer saber preço, tamanho e cor disponíveis antes de chamar no WhatsApp.
- **Lojista / revendedora (atacado):** compra em quantidade para revender, normalmente recebe por excursão ou transportadora; quer ver o preço de atacado e montar o pedido rápido.
- **Vanuza e equipe (painel):** cadastram peças, fotos, tamanhos, cores e estoque; acompanham pedidos e mudam o status. Usam o celular no balcão da loja.

## Product Purpose

Vitrine e loja online da Vanuza Andrade. A cliente monta o carrinho e fecha o pedido pelo WhatsApp da loja; o pedido fica registrado no painel. Sucesso: menos perguntas repetidas no direct ("tem M?", "quanto custa?") e pedidos chegando prontos no WhatsApp.

## Positioning

Fabricação própria de peças em viscose e viscolinho premium, com loja física no Mega Moda Shopping. Vende no varejo e no atacado a partir do mesmo catálogo.

## Operating Context

- Loja física: Mega Moda Shopping, Entrada 8, Rua Alameda dos Eventos, loja 263.
- Pedido fechado pelo WhatsApp (número configurável no painel). Sem gateway de pagamento.
- Entrega: retirada na loja ou envio por excursão / transportadora informada pela cliente.
- Instagram: @vanuzaandradeloja (cerca de 1,4 mil seguidores).

## Capabilities and Constraints

- Catálogo com categorias, peças, várias fotos por peça, variações de cor e tamanho com estoque.
- Preço de varejo por peça e preço de atacado a partir de uma quantidade mínima configurável.
- Grade padrão de tamanhos: P, M, G, GG (editável por peça).
- Painel administrativo com login: peças, categorias, pedidos, configurações da loja.
- Ainda não decidido: valor do pedido mínimo de atacado, número do WhatsApp, horário de funcionamento, domínio.

## Brand Commitments

- Nome: Vanuza Andrade. Logo atual: monograma "VA" com o nome em caixa alta sobre círculo roxo com aro dourado (`static/img/logo-instagram.jpg`, baixa resolução).
- Bordão do perfil: "Conforto e estilo você encontra aqui".
- Tom: próximo, feminino, direto; português do Brasil.

## Evidence on Hand

- 12 fotos de produto publicadas no Instagram (fev. e mar. 2026), em `static/img/catalogo/`. Nomes, preços e descrições das peças **não** são conhecidos: o catálogo inicial usa nomes e preços de exemplo marcados para revisão no painel.
- Não há depoimentos, avaliações, número de clientes nem prêmios. Não inventar.

## Product Principles

1. A peça é a protagonista: foto grande, preço e tamanhos à vista sem clique extra.
2. O WhatsApp é o caixa: todo caminho de compra termina numa mensagem pronta e legível para a vendedora.
3. Atacado sem atrito: a revendedora vê o preço dela e monta quantidades sem um site separado.
4. O painel tem de funcionar no celular, no balcão, com uma mão.
5. Nada de alegação que a loja não confirmou.

## Accessibility & Inclusion

Uso majoritário em celular, muitas vezes com conexão de dados móvel: páginas leves, fotos otimizadas, contraste AA e alvos de toque de pelo menos 44 px.
