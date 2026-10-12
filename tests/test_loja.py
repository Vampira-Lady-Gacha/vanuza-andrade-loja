from urllib.parse import unquote

from sqlalchemy import select

from app.models import Pedido, Peca, Variante
from app.servicos import ler_centavos, mensagem_whatsapp, reais, slugificar
from tests.conftest import csrf_de


def _variante(sessao, nome="Vestido Midi Felino", tamanho="M") -> Variante:
    peca = sessao.scalar(select(Peca).where(Peca.nome == nome))
    return next(v for v in peca.variantes if v.tamanho == tamanho)


def _pedido(cliente, itens, **extra):
    corpo = {"nome": "Ana Souza", "whatsapp": "(62) 98888-7777", "entrega": "retirada", "itens": itens} | extra
    return cliente.post("/api/pedidos", json=corpo)


def test_utilidades():
    assert reais(15990) == "R$ 159,90"
    assert reais(123456789) == "R$ 1.234.567,89"
    assert ler_centavos("1.189,90") == 118990
    assert ler_centavos("189.9") == 18990
    assert ler_centavos("") is None
    assert slugificar("Vestido Longo Folhagem Pêssego") == "vestido-longo-folhagem-pessego"


def test_paginas_publicas(cliente):
    for url in ["/", "/catalogo", "/catalogo?tamanho=GG", "/como-comprar", "/pedido", "/sitemap.xml", "/robots.txt"]:
        assert cliente.get(url).status_code == 200, url
    pagina = cliente.get("/peca/vestido-midi-felino")
    assert pagina.status_code == 200
    assert "R$ 159,90" in pagina.text
    assert cliente.get("/peca/nao-existe").status_code == 404


def test_busca_no_catalogo(cliente):
    assert "Mosaico" in cliente.get("/catalogo?q=mosaico").text
    assert "Nenhuma peça encontrada" in cliente.get("/catalogo?q=jaqueta").text


def test_cotacao_varejo_e_atacado(cliente, sessao):
    m = _variante(sessao).id
    varejo = cliente.post("/api/cotacao", json={"itens": [{"variante_id": m, "quantidade": 2}]}).json()
    assert not varejo["atacado"]
    assert varejo["total"] == 2 * 15990
    assert varejo["faltam_para_atacado"] == 4

    g = _variante(sessao, tamanho="G").id
    atacado = cliente.post(
        "/api/cotacao", json={"itens": [{"variante_id": m, "quantidade": 3}, {"variante_id": g, "quantidade": 3}]}
    ).json()
    assert atacado["atacado"]
    assert atacado["total"] == 6 * 11990
    assert atacado["economia_fmt"] == reais(6 * (15990 - 11990))


def test_cotacao_ignora_variante_inexistente(cliente):
    r = cliente.post("/api/cotacao", json={"itens": [{"variante_id": 99999, "quantidade": 1}]}).json()
    assert r["linhas"] == [] and r["removidos"] == [99999]


def test_pedido_baixa_estoque_e_gera_whatsapp(cliente, sessao):
    variante = _variante(sessao)
    antes = variante.estoque
    r = _pedido(cliente, [{"variante_id": variante.id, "quantidade": 2}])
    assert r.status_code == 200, r.text
    dados = r.json()
    assert dados["codigo"] == "VA-0001"
    texto = unquote(dados["url_whatsapp"])
    assert "2x Vestido Midi Felino" in texto and "R$ 319,80" in texto

    sessao.expire_all()
    assert _variante(sessao).estoque == antes - 2
    assert cliente.get(dados["url"]).status_code == 200
    # Sem o token certo, ninguém vê o pedido
    assert cliente.get("/pedido/VA-0001?t=errado").status_code == 404


def test_pedido_recusa_estoque_insuficiente(cliente, sessao):
    variante = _variante(sessao, tamanho="GG")
    r = _pedido(cliente, [{"variante_id": variante.id, "quantidade": variante.estoque + 1}])
    assert r.status_code == 422
    assert "só temos" in r.json()["erro"]


def test_pedido_exige_dados(cliente, sessao):
    v = _variante(sessao).id
    assert _pedido(cliente, [{"variante_id": v, "quantidade": 1}], nome="").status_code == 422
    assert _pedido(cliente, [{"variante_id": v, "quantidade": 1}], whatsapp="123").status_code == 422
    r = _pedido(cliente, [{"variante_id": v, "quantidade": 1}], entrega="excursao")
    assert r.status_code == 422 and "excursão" in r.json()["erro"]
    assert _pedido(cliente, [], nome="Ana").status_code == 422


def test_painel_exige_login(cliente):
    resp = cliente.get("/admin", follow_redirects=False)
    assert resp.status_code == 303 and resp.headers["location"] == "/admin/entrar"


def test_login_errado(cliente):
    pagina = cliente.get("/admin/entrar")
    r = cliente.post("/admin/entrar", data={"email": "teste@loja.com", "senha": "x", "csrf": csrf_de(pagina.text)})
    assert r.status_code == 401


def test_post_sem_csrf_e_recusado(admin):
    r = admin.post("/admin/configuracoes", data={"whatsapp": "5562911112222"})
    assert r.status_code == 400


def test_cancelar_pedido_devolve_estoque(admin, sessao):
    variante = _variante(sessao)
    antes = variante.estoque
    _pedido(admin, [{"variante_id": variante.id, "quantidade": 3}])
    pedido = sessao.scalar(select(Pedido))
    pagina = admin.get(f"/admin/pedidos/{pedido.id}")
    assert "Ana Souza" in pagina.text
    admin.post(f"/admin/pedidos/{pedido.id}/status", data={"status": "cancelado", "csrf": csrf_de(pagina.text)})
    sessao.expire_all()
    assert _variante(sessao).estoque == antes
    assert sessao.get(Pedido, pedido.id).status == "cancelado"


def test_criar_peca_e_grade(admin, sessao):
    csrf = csrf_de(admin.get("/admin/pecas/nova").text)
    r = admin.post(
        "/admin/pecas/nova",
        data={"csrf": csrf, "nome": "Conjunto Linho Areia", "preco_varejo": "199,90", "preco_atacado": "149,90", "ativa": "on"},
        follow_redirects=False,
    )
    assert r.status_code == 303
    peca = sessao.scalar(select(Peca).where(Peca.nome == "Conjunto Linho Areia"))
    assert peca.preco_varejo == 19990 and peca.slug == "conjunto-linho-areia"
    assert sorted(v.tamanho for v in peca.variantes) == ["G", "GG", "M", "P"]

    admin.post(
        f"/admin/pecas/{peca.id}/grade",
        data={
            "csrf": csrf,
            "tamanhos": "P, M, G",
            "cor_nome": ["Areia", "Preto"],
            "cor_hex": ["#d8c3a5", "#111111"],
            "cor_original-0": "Única",
            "estoque-0-P": "2", "estoque-0-M": "5", "estoque-0-G": "0",
            "estoque-1-P": "1", "estoque-1-M": "1", "estoque-1-G": "1",
        },
    )
    sessao.expire_all()
    peca = sessao.get(Peca, peca.id)
    assert {(v.cor, v.tamanho, v.estoque) for v in peca.variantes} == {
        ("Areia", "P", 2), ("Areia", "M", 5), ("Areia", "G", 0),
        ("Preto", "P", 1), ("Preto", "M", 1), ("Preto", "G", 1),
    }


def test_preco_atacado_maior_que_varejo_e_recusado(admin):
    csrf = csrf_de(admin.get("/admin/pecas/nova").text)
    r = admin.post("/admin/pecas/nova", data={"csrf": csrf, "nome": "Blusa", "preco_varejo": "50", "preco_atacado": "60"})
    assert r.status_code == 422 and "atacado" in r.text


def test_configuracoes_mudam_whatsapp(admin, sessao):
    csrf = csrf_de(admin.get("/admin/configuracoes").text)
    admin.post("/admin/configuracoes", data={"csrf": csrf, "whatsapp": "+55 (62) 91111-2222", "atacado_minimo": "10"})
    v = _variante(sessao).id
    dados = _pedido(admin, [{"variante_id": v, "quantidade": 1}]).json()
    assert dados["url_whatsapp"].startswith("https://wa.me/5562911112222?text=")


def test_mensagem_whatsapp_formata_entrega(sessao, cliente):
    v = _variante(sessao).id
    _pedido(cliente, [{"variante_id": v, "quantidade": 1}], entrega="excursao", detalhe_entrega="Excursão Bahia, box 12")
    pedido = sessao.scalar(select(Pedido))
    texto = mensagem_whatsapp(pedido, {"nome_loja": "Vanuza Andrade"})
    assert "Entrega: Excursão · Excursão Bahia, box 12" in texto


def test_catalogo_json_e_modo_estatico(cliente, sessao):
    dados = cliente.get("/api/catalogo.json").json()
    v = _variante(sessao)
    item = dados["variantes"][str(v.id)]
    assert item["preco_varejo"] == 15990 and item["preco_atacado"] == 11990
    assert dados["loja"]["atacado_minimo"] == "6"

    estatica = cliente.get("/pedido", headers={"X-Exportar-Estatico": "1"}).text
    assert "window.VA_ESTATICO = true" in estatica and 'href="/admin"' not in estatica
    assert "window.VA_ESTATICO" not in cliente.get("/pedido").text
