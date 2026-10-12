# Vanuza Andrade · loja online

Vitrine e loja da Vanuza Andrade (viscose e viscolinho premium, Mega Moda Shopping, loja 263), com pedido fechado pelo WhatsApp e painel para manter as peças.

## O que tem

**Loja (pública)**
- Página inicial com peça em destaque, compra direta (cor, tamanho e "Pôr no pedido"), coleção, fabricação, atacado e endereço.
- Catálogo com categorias, busca, filtro por tamanho em estoque e ordenação.
- Página da peça: galeria, preço de varejo e de atacado, cores, grade de tamanhos com estoque, aviso de últimas peças, dados para Google (schema.org) e prévia para WhatsApp/Instagram (Open Graph).
- Pedido: guardado no navegador e calculado pelo servidor. A **fita métrica** mostra quantas peças faltam para o atacado e o preço muda sozinho. O formulário registra nome, WhatsApp, cidade, entrega (retirada, excursão ou transportadora) e observação.
- Ao enviar, o pedido é gravado, o estoque é reservado e a cliente recebe o botão para abrir o WhatsApp com a mensagem pronta.
- Como comprar, trocas, `sitemap.xml`, `robots.txt` e página 404.

**Painel (`/admin`)**
- Início: pedidos novos, pedidos da semana, vendido no mês e estoque baixo.
- Peças: criar, editar, esconder, destacar, apagar, enviar várias fotos (redimensionadas automaticamente), escolher a capa, editar a grade cor × tamanho com estoque.
- Categorias: criar, renomear, ordenar, desativar.
- Pedidos: filtrar por situação, buscar, ver detalhes, mudar situação (novo, confirmado, separado, entregue, cancelado) e falar com a cliente no WhatsApp. Cancelar devolve as peças ao estoque.
- Loja: WhatsApp, Instagram, endereço, horário, mínimo do atacado e textos de entrega, atacado e trocas.
- Minha senha: trocar a senha do painel.

Segurança: senha com scrypt, sessão em cookie assinado, proteção CSRF nos formulários do painel, limite de tentativas de login e link do pedido com token.

## Rodar no computador

```bash
uv sync
```

```bash
uv run uvicorn app.main:app --reload --port 8040
```

Abra http://localhost:8040. Na primeira execução o banco é criado em `dados/` com as 3 peças iniciais, e o acesso ao painel é salvo em `dados/acesso-painel.txt`. Troque a senha em `/admin/conta`.

Testes:

```bash
uv run pytest
```

## Antes de divulgar

1. Em **Painel → Loja**, troque o WhatsApp de exemplo pelo número real (com 55 e DDD) e preencha o horário.
2. Em **Painel → Peças**, revise nome, preço, atacado e estoque das 3 peças iniciais. Eles são **de exemplo**: as fotos vieram do Instagram, mas o perfil não publica esses dados. Depois clique em "Já revisei" no início do painel.
3. Cadastre as outras peças com fotos.
4. Confira com a loja o prazo de trocas (o texto padrão diz 7 dias) e o mínimo do atacado (padrão 6 peças).

## Publicar

No Render, use o `render.yaml` deste repositório: **New → Blueprint**, escolha o repositório e preencha `ADMIN_EMAIL`, `ADMIN_SENHA` e `URL_PUBLICA`. Ele cria o serviço no plano Starter com disco persistente em `/var/data` (sem disco, banco e fotos somem a cada deploy).

Em outro serviço que rode Python (Railway, Fly.io, uma VPS), configure as variáveis de ambiente:

| Variável | Para quê |
| --- | --- |
| `SECRET_KEY` | Chave das sessões. Use um valor longo e aleatório. |
| `ADMIN_EMAIL` / `ADMIN_SENHA` | Acesso inicial do painel (só na primeira execução). |
| `LOJA_DADOS` | Pasta do banco e das fotos. Precisa ser um **disco persistente**. |
| `COOKIE_SEGURO=1` | Liga o cookie só em HTTPS (use em produção). |
| `URL_PUBLICA` | Endereço do site, para as prévias de link (ex.: `https://vanuzaandrade.com.br`). |

Comando de início: `uv run uvicorn app.main:app --host 0.0.0.0 --port $PORT`.

Faça backup da pasta `dados/` (banco `loja.db` e `uploads/`).

## Estrutura

| Arquivo | Faz |
| --- | --- |
| `app/models.py` | Tabelas: categoria, peça, foto, variante (cor × tamanho × estoque), pedido, item, configuração, usuário |
| `app/servicos.py` | Preço varejo/atacado, criação de pedido, estoque, mensagem do WhatsApp, fotos, senhas |
| `app/rotas_loja.py` | Páginas públicas e API do pedido (`/api/cotacao`, `/api/pedidos`) |
| `app/rotas_admin.py` | Painel |
| `app/seed.py` | Cria banco, usuário do painel e catálogo inicial |
| `app/templates/` | Páginas (Jinja2) |
| `static/` | CSS, JavaScript, logo e fotos iniciais |

O visual segue o mundo "Folha de Molde" (ver `DESIGN.md` e `PRODUCT.md`): as linhas em volta das fotos são os tamanhos em estoque, P contínua, M tracejada, G traço e ponto, GG pontilhada.
