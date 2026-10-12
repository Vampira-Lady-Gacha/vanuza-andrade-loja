/* Vanuza Andrade · loja
   - Pedido guardado no navegador (localStorage); preço sempre vem do servidor.
   - Contornos do molde em volta das fotos, um por tamanho.
   - Página do pedido: cotação, fita métrica do atacado e envio para o WhatsApp. */

(() => {
  "use strict";

  const CHAVE = "va-pedido";
  // Na vitrine do GitHub Pages não há servidor: o pedido é calculado aqui e vai direto ao WhatsApp.
  const ESTATICO = window.VA_ESTATICO === true;
  const RAIZ = document.documentElement.dataset.raiz || "";
  const reaisFmt = new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" });
  const reais = (centavos) => reaisFmt.format(centavos / 100).replace(/ /g, " ");
  const SVG = "http://www.w3.org/2000/svg";
  const ORDEM_LINHAS = { P: "p", M: "m", G: "g", GG: "gg" };

  // ------------------------------------------------------------ pedido (localStorage)

  const Pedido = {
    ler() {
      try {
        const itens = JSON.parse(localStorage.getItem(CHAVE) || "[]");
        return Array.isArray(itens) ? itens.filter((i) => Number.isInteger(i.v) && i.q > 0) : [];
      } catch {
        return [];
      }
    },
    gravar(itens) {
      try { localStorage.setItem(CHAVE, JSON.stringify(itens)); } catch { /* modo privado */ }
      atualizarContador(true);
    },
    pecas() { return this.ler().reduce((s, i) => s + i.q, 0); },
    por(varianteId, qtd) {
      const itens = this.ler();
      const item = itens.find((i) => i.v === varianteId);
      if (item) item.q = Math.min(999, item.q + qtd);
      else itens.push({ v: varianteId, q: qtd });
      this.gravar(itens);
    },
    definir(varianteId, qtd) {
      const itens = this.ler().map((i) => (i.v === varianteId ? { ...i, q: qtd } : i)).filter((i) => i.q > 0);
      this.gravar(itens);
    },
    limpar() { this.gravar([]); },
  };

  function atualizarContador(pulsar = false) {
    const total = Pedido.pecas();
    document.querySelectorAll("[data-contador]").forEach((el) => {
      el.textContent = total > 99 ? "99+" : String(total);
      el.toggleAttribute("data-zero", total === 0);
      el.setAttribute("aria-hidden", "true");
    });
    document.querySelectorAll("[data-botao-pedido]").forEach((link) =>
      link.setAttribute("aria-label", `Pedido, ${total} ${total === 1 ? "peça" : "peças"}`));
    if (pulsar) {
      const botao = document.querySelector("[data-botao-pedido]");
      if (botao) {
        botao.classList.remove("pulsa");
        void botao.offsetWidth;
        botao.classList.add("pulsa");
      }
    }
  }

  // ------------------------------------------------------------ contornos do molde

  let mascaras = 0;

  function el(nome, attrs = {}) {
    const n = document.createElementNS(SVG, nome);
    for (const [k, v] of Object.entries(attrs)) n.setAttribute(k, v);
    return n;
  }

  function desenharMolde(molde) {
    const foto = molde.querySelector(".foto");
    if (!foto) return;
    const tamanhos = (molde.dataset.tamanhos || "").split(",").filter(Boolean);
    const disponiveis = new Set((molde.dataset.disponiveis || "").split(",").filter(Boolean));
    const W = molde.clientWidth, H = molde.clientHeight;
    const x0 = foto.offsetLeft, y0 = foto.offsetTop, w = foto.offsetWidth, h = foto.offsetHeight;
    if (!w || !h) return;

    molde.querySelector("svg.contornos")?.remove();
    const svg = el("svg", { class: "contornos", viewBox: `0 0 ${W} ${H}`, "aria-hidden": "true" });
    const folga = Math.min(x0, y0);
    const passo = Math.max(3.5, Math.min(6, (folga - 4) / Math.max(1, tamanhos.length) - 1));
    const defs = el("defs");
    svg.append(defs);

    // Graduação: cada tamanho abre um pouco mais para fora, mais na barra do que no ombro,
    // com ombro chanfrado e barra levemente curva, como um molde de vestido.
    const n = Math.max(1, tamanhos.length);
    const grande = folga > 24;
    const evase = grande ? 4 : 2.5; // quanto cada tamanho abre a mais na barra
    const contorno = (i) => {
      const o = 4 + passo * i;
      const ob = o + evase * i; // a barra abre mais que o ombro
      const c = (grande ? 14 : 9) + i * (grande ? 4 : 2.5); // chanfro do ombro cresce com o tamanho
      const curva = (grande ? 4 : 3) + i * (grande ? 3 : 2); // a barra desce no meio
      const L = x0 - o, R = x0 + w + o, T = y0 - o;
      const Lb = x0 - ob, Rb = x0 + w + ob, B = y0 + h + o;
      return {
        d: `M${L} ${T + c}L${L + c} ${T}H${R - c}L${R} ${T + c}L${Rb} ${B}Q${x0 + w / 2} ${B + curva * 2} ${Lb} ${B}Z`,
        xDireita: (y) => R + (Rb - R) * ((y - T) / (B - T)),
        xEsquerda: (y) => L + (Lb - L) * ((y - T) / (B - T)),
        T, B, L, c, curva,
      };
    };

    tamanhos.forEach((t, i) => {
      const { d, xDireita } = contorno(i);
      const classe = ORDEM_LINHAS[t] || "x";
      const id = `mm${++mascaras}`;
      const mascara = el("mask", { id, maskUnits: "userSpaceOnUse", x: 0, y: 0, width: W, height: H });
      const traco = el("path", { d, pathLength: "1" });
      mascara.append(traco);
      defs.append(mascara);
      const linha = el("path", { d, class: `c ${classe}`, "data-t": t, mask: `url(#${id})` });
      if (!disponiveis.has(t)) linha.style.opacity = "0.12";
      svg.append(linha);

      // Letra do tamanho sobre a própria linha, na lateral direita
      const ty = y0 + h * 0.2 + i * 15;
      const rotulo = el("text", { x: xDireita(ty), y: ty, "text-anchor": "middle", "dominant-baseline": "middle", class: "tl" });
      rotulo.style.fill = classe === "x" ? "var(--tinta-2)" : `var(--linha-${classe})`;
      rotulo.style.paintOrder = "stroke";
      rotulo.style.stroke = "var(--papel)";
      rotulo.style.strokeWidth = "5px";
      rotulo.textContent = t;
      svg.append(rotulo);
    });

    // Piques no contorno de fora, no meio das laterais
    const fora = contorno(n - 1);
    const meio = y0 + h / 2;
    const p = 6;
    const xe = fora.xEsquerda(meio), xd = fora.xDireita(meio);
    svg.append(el("path", { class: "pique", d: `M${xe} ${meio - p}L${xe + p * 1.3} ${meio}L${xe} ${meio + p}Z` }));
    svg.append(el("path", { class: "pique", d: `M${xd} ${meio - p}L${xd - p * 1.3} ${meio}L${xd} ${meio + p}Z` }));

    if (grande) {
      // Seta de fio reto, dentro da peça, com halo para ler sobre a foto
      const fx = x0 + 18, f1 = y0 + h * 0.34, f2 = y0 + h * 0.66;
      const seta = `M${fx} ${f1}V${f2}`;
      svg.append(el("path", { d: seta, stroke: "rgb(255 255 255 / 0.85)", "stroke-width": "4", fill: "none" }));
      svg.append(el("path", { d: seta, class: "fio-reto" }));
      svg.append(el("path", { class: "fio-ponta", d: `M${fx - 4} ${f1 + 8}L${fx} ${f1}L${fx + 4} ${f1 + 8}Z` }));
      svg.append(el("path", { class: "fio-ponta", d: `M${fx - 4} ${f2 - 8}L${fx} ${f2}L${fx + 4} ${f2 - 8}Z` }));
      const fio = el("text", { x: fx + 13, y: (f1 + f2) / 2, transform: `rotate(-90 ${fx + 13} ${(f1 + f2) / 2})`, "text-anchor": "middle" });
      fio.textContent = "FIO";
      fio.style.paintOrder = "stroke";
      fio.style.stroke = "rgb(255 255 255 / 0.85)";
      fio.style.strokeWidth = "3px";
      svg.append(fio);

      // Anotações na margem do molde: referência em cima, preço embaixo
      if (molde.dataset.rotulo) {
        const nota = el("text", { x: fora.L, y: fora.T - 7 });
        nota.textContent = molde.dataset.rotulo.toUpperCase() + " · CORTE 1X";
        svg.append(nota);
      }
      if (molde.dataset.preco) {
        const preco = el("text", { x: x0 + w / 2, y: fora.B + fora.curva + 16, "text-anchor": "middle", class: "preco-margem" });
        preco.textContent = molde.dataset.preco.toUpperCase();
        svg.append(preco);
      }
    }

    molde.append(svg);
    marcarTamanho(molde, molde.dataset.escolhido || "", false);
  }

  function marcarTamanho(molde, tamanho, animar = true) {
    if (tamanho) molde.dataset.escolhido = tamanho;
    else delete molde.dataset.escolhido;
    molde.querySelectorAll("path.c").forEach((linha) => {
      const ativa = linha.dataset.t === tamanho;
      linha.classList.toggle("ativo", ativa);
      const mascara = molde.querySelector(`${linha.getAttribute("mask").slice(4, -1)} path`);
      if (!mascara) return;
      mascara.classList.remove("desenha");
      if (ativa && animar) {
        void mascara.getBoundingClientRect();
        mascara.classList.add("desenha");
      }
    });
  }

  // Redesenha só quando o tamanho muda, para não cortar a animação de abertura
  const observador = "ResizeObserver" in window
    ? new ResizeObserver((entradas) => entradas.forEach((e) => {
        const m = e.target;
        const tam = `${m.clientWidth}x${m.clientHeight}`;
        if (m.dataset.tam !== tam) { m.dataset.tam = tam; desenharMolde(m); }
      }))
    : null;

  // A peça em destaque mostra a graduação uma vez ao abrir: do GG para o P
  function apresentar(molde) {
    if (!molde.hasAttribute("data-apresentar") || matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    const tracos = [...molde.querySelectorAll("mask path")];
    tracos.forEach((m, i) => {
      m.style.animationDelay = `${0.2 + (tracos.length - 1 - i) * 0.18}s`;
      m.classList.add("desenha");
      m.addEventListener("animationend", () => { m.classList.remove("desenha"); m.style.animationDelay = ""; }, { once: true });
    });
  }

  function prepararMoldes(raiz = document) {
    raiz.querySelectorAll("[data-molde]").forEach((molde) => {
      const img = molde.querySelector("img");
      const pronto = () => {
        molde.dataset.tam = `${molde.clientWidth}x${molde.clientHeight}`;
        desenharMolde(molde);
        apresentar(molde);
        observador?.observe(molde);
      };
      if (img && !img.complete) img.addEventListener("load", pronto, { once: true });
      else pronto();
    });
  }

  // ------------------------------------------------------------ escolher e pôr no pedido

  function prepararCompra(form) {
    let grade = [];
    try { grade = JSON.parse(form.querySelector("[data-grade]").textContent); } catch { /* sem grade */ }
    const molde = form.closest(".peca-destaque, .peca-pagina")?.querySelector("[data-molde]");
    const aviso = form.querySelector("[data-estoque-aviso]");
    const confirma = form.querySelector("[data-confirma]");
    const campoQtd = form.querySelector("[data-quantidade]");

    const corAtual = () =>
      form.querySelector("[data-cor]:checked")?.value ?? form.querySelector("[data-cor-unica]")?.value ?? grade[0]?.cor;
    const tamanhoAtual = () => form.querySelector("[data-tamanho]:checked")?.value;
    const variante = () => grade.find((v) => v.cor === corAtual() && v.tamanho === tamanhoAtual());

    function refletirCor() {
      // Tamanhos sem estoque na cor escolhida ficam desligados
      const cor = corAtual();
      form.querySelectorAll("[data-tamanho]").forEach((radio) => {
        const v = grade.find((g) => g.cor === cor && g.tamanho === radio.value);
        radio.disabled = !v || v.estoque <= 0;
        if (radio.disabled && radio.checked) radio.checked = false;
      });
      if (molde) {
        const disp = grade.filter((g) => g.cor === cor && g.estoque > 0).map((g) => g.tamanho);
        molde.dataset.disponiveis = disp.join(",");
        desenharMolde(molde);
      }
      refletirTamanho(false);
    }

    function refletirTamanho(animar = true) {
      const v = variante();
      if (molde) marcarTamanho(molde, tamanhoAtual() || "", animar);
      aviso.classList.remove("pouco");
      if (!tamanhoAtual()) aviso.textContent = "";
      else if (v && v.estoque <= 3) {
        aviso.textContent = v.estoque === 1 ? `Última peça no ${v.tamanho}.` : `Últimas ${v.estoque} no ${v.tamanho}.`;
        aviso.classList.add("pouco");
      } else aviso.textContent = `${v?.tamanho ?? ""} disponível.`;
      if (campoQtd && v) {
        campoQtd.max = String(v.estoque);
        if (+campoQtd.value > v.estoque) campoQtd.value = String(v.estoque);
      }
      confirma.textContent = "";
      confirma.classList.remove("erro");
    }

    form.addEventListener("change", (e) => {
      if (e.target.matches("[data-cor]")) refletirCor();
      if (e.target.matches("[data-tamanho]")) refletirTamanho();
    });

    form.querySelector("[data-menos]")?.addEventListener("click", () => {
      campoQtd.value = String(Math.max(1, (+campoQtd.value || 1) - 1));
    });
    form.querySelector("[data-mais]")?.addEventListener("click", () => {
      const max = +campoQtd.max || 99;
      campoQtd.value = String(Math.min(max, (+campoQtd.value || 1) + 1));
    });

    form.addEventListener("submit", (e) => {
      e.preventDefault();
      const v = variante();
      if (!tamanhoAtual() || !v) {
        confirma.textContent = "Escolha o tamanho pela linha do molde.";
        confirma.classList.add("erro");
        form.querySelector("[data-tamanho]:not(:disabled)")?.focus();
        return;
      }
      const qtd = Math.max(1, Math.min(v.estoque, parseInt(campoQtd?.value || "1", 10) || 1));
      const jaTem = Pedido.ler().find((i) => i.v === v.id)?.q || 0;
      if (jaTem + qtd > v.estoque) {
        confirma.innerHTML = `Você já tem ${jaTem} no pedido e só temos ${v.estoque} no ${v.tamanho}. <a href="${RAIZ}/pedido/">Ver pedido</a>`;
        confirma.classList.add("erro");
        return;
      }
      Pedido.por(v.id, qtd);
      confirma.classList.remove("erro");
      confirma.innerHTML = `${qtd > 1 ? qtd + " peças" : "Peça"} no pedido (${v.cor}, ${v.tamanho}). <a href="${RAIZ}/pedido/">Ver pedido</a>`;
    });

    refletirCor();
  }

  // ------------------------------------------------------------ galeria e barra do celular

  function prepararGaleria() {
    const principal = document.querySelector(".galeria [data-foto-principal]");
    document.querySelectorAll("[data-miniatura]").forEach((botao) => {
      botao.addEventListener("click", () => {
        if (!principal) return;
        principal.src = botao.dataset.miniatura;
        document.querySelectorAll("[data-miniatura]").forEach((b) => b.setAttribute("aria-pressed", String(b === botao)));
      });
    });

    const barra = document.querySelector("[data-barra-celular]");
    const compra = document.querySelector(".peca-pagina [data-compra]");
    if (barra && compra && "IntersectionObserver" in window) {
      new IntersectionObserver(([e]) => barra.classList.toggle("mostra", !e.isIntersecting && e.boundingClientRect.top < 0))
        .observe(compra);
      barra.querySelector("[data-ir-compra]").addEventListener("click", (e) => {
        e.preventDefault();
        compra.scrollIntoView({ behavior: "smooth", block: "center" });
        compra.querySelector("[data-tamanho]:not(:disabled)")?.focus({ preventScroll: true });
      });
    }
  }

  // ------------------------------------------------------------ página do pedido

  async function postar(url, corpo) {
    const resp = await fetch(RAIZ + url, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(corpo) });
    const dados = await resp.json().catch(() => ({}));
    if (!resp.ok) throw new Error(dados.erro || "Não foi possível falar com a loja. Confira a internet e tente de novo.");
    return dados;
  }

  // ------------------------------------------------------------ pedido sem servidor (GitHub Pages)

  let catalogo = null;
  async function catalogoEstatico() {
    if (!catalogo) {
      const resp = await fetch(`${RAIZ}/catalogo.json`);
      if (!resp.ok) throw new Error("Não foi possível carregar os preços. Confira a internet e tente de novo.");
      catalogo = await resp.json();
    }
    return catalogo;
  }

  // Mesma regra do servidor (app/servicos.py, cotar)
  function cotarLocal(itens, cat) {
    const minimo = parseInt(cat.loja.atacado_minimo, 10) || 1;
    const linhas = [];
    const removidos = [];
    for (const i of itens) {
      const v = cat.variantes[String(i.v)];
      if (!v) { removidos.push(i.v); continue; }
      linhas.push({ variante_id: i.v, ...v, quantidade: Math.min(i.q, 999), disponivel: v.estoque, preco: v.preco_varejo });
    }
    const quantidade = linhas.reduce((s, l) => s + l.quantidade, 0);
    const atacado = quantidade >= minimo && linhas.some((l) => l.preco_atacado != null);
    let totalVarejo = 0;
    for (const l of linhas) {
      totalVarejo += l.quantidade * l.preco_varejo;
      if (atacado && l.preco_atacado != null) l.preco = l.preco_atacado;
      l.subtotal = l.quantidade * l.preco;
      l.subtotal_fmt = reais(l.subtotal);
      l.preco_fmt = reais(l.preco);
    }
    const total = linhas.reduce((s, l) => s + l.subtotal, 0);
    return {
      linhas, removidos, quantidade, atacado,
      minimo_atacado: minimo,
      faltam_para_atacado: Math.max(0, minimo - quantidade),
      total, total_fmt: reais(total),
      economia_fmt: atacado ? reais(totalVarejo - total) : "",
    };
  }

  // Mesmo formato de app/servicos.py, mensagem_whatsapp
  function mensagemLocal(c, dados, loja) {
    const entregas = { retirada: "Retirada na loja", excursao: "Excursão", transportadora: "Transportadora" };
    const linhas = [`Olá, ${loja.nome_loja}! Quero fazer este pedido:`, ""];
    for (const l of c.linhas) {
      const ref = l.referencia ? ` (ref. ${l.referencia})` : "";
      linhas.push(`• ${l.quantidade}x ${l.peca}${ref} · ${l.cor} · ${l.tamanho} · ${l.preco_fmt} cada`);
    }
    linhas.push(
      "",
      `*Total: ${c.total_fmt}* (${c.quantidade} peças, preço de ${c.atacado ? "atacado" : "varejo"})`,
      `Entrega: ${entregas[dados.entrega]}${dados.detalhe_entrega ? " · " + dados.detalhe_entrega.trim() : ""}`,
      `Nome: ${dados.nome.trim()}`,
      `WhatsApp: ${dados.whatsapp.trim()}`,
    );
    if (dados.cidade?.trim()) linhas.push(`Cidade: ${dados.cidade.trim()}`);
    if (dados.observacao?.trim()) linhas.push(`Obs.: ${dados.observacao.trim()}`);
    return linhas.join("\n");
  }

  function prepararPaginaPedido(secao) {
    const minimo = parseInt(secao.dataset.minimo, 10) || 1;
    const q = (s) => secao.querySelector(s);
    const lista = q("[data-linhas]");
    const modelo = q("[data-modelo-linha]");
    const form = q("[data-form-envio]");
    const erro = q("[data-erro]");
    let cotacao = null;
    let atraso;

    function marcasFita(n) {
      const marcas = q("[data-fita-marcas]");
      if (marcas.childElementCount === n) return;
      marcas.innerHTML = "";
      for (let i = 1; i <= n; i++) {
        const s = document.createElement("span");
        s.textContent = String(i);
        marcas.append(s);
      }
    }

    function render() {
      q("[data-carregando]").hidden = true;
      const vazio = !cotacao || cotacao.linhas.length === 0;
      q("[data-vazio]").hidden = !vazio;
      q("[data-cheio]").hidden = vazio;
      form.hidden = vazio;
      if (vazio) return;

      lista.innerHTML = "";
      for (const l of cotacao.linhas) {
        const no = modelo.content.firstElementChild.cloneNode(true);
        const $ = (s) => no.querySelector(s);
        no.querySelectorAll("[data-l-link]").forEach((a) => (a.href = `${RAIZ}/peca/${l.slug}/`));
        if (l.foto) $("[data-l-foto]").src = RAIZ + l.foto;
        $("[data-l-nome]").textContent = l.peca;
        $("[data-l-amostra]").style.setProperty("--amostra", l.cor_hex);
        $("[data-l-cor]").textContent = l.cor;
        $("[data-l-tam]").textContent = `Tamanho ${l.tamanho}`;
        $("[data-l-subtotal]").textContent = l.subtotal_fmt;
        $("[data-l-unit]").textContent = `${l.preco_fmt} cada`;
        const campo = $("[data-l-qtd]");
        campo.value = String(l.quantidade);
        campo.max = String(Math.max(l.disponivel, 1));
        $("[data-l-menos]").addEventListener("click", () => mudar(l.variante_id, l.quantidade - 1));
        $("[data-l-mais]").disabled = l.quantidade >= l.disponivel;
        $("[data-l-mais]").addEventListener("click", () => mudar(l.variante_id, l.quantidade + 1));
        campo.addEventListener("change", () => mudar(l.variante_id, Math.max(0, parseInt(campo.value, 10) || 0)));
        $("[data-l-tirar]").addEventListener("click", () => mudar(l.variante_id, 0));
        if (l.quantidade > l.disponivel) {
          const alerta = $("[data-l-alerta]");
          alerta.hidden = false;
          alerta.textContent = l.disponivel > 0
            ? `Só temos ${l.disponivel} em estoque. Diminua a quantidade para enviar.`
            : "Esgotou. Tire esta peça para enviar o pedido.";
        }
        lista.append(no);
      }

      // Fita métrica: peças até o atacado
      const fita = q("[data-fita]");
      marcasFita(minimo);
      fita.style.setProperty("--pecas", String(minimo));
      fita.style.setProperty("--tem", String(cotacao.quantidade));
      q("[data-fita-titulo]").textContent = `Fita métrica do atacado · ${minimo} peças`;
      q("[data-fita-conta]").textContent = `${cotacao.quantidade} de ${minimo}`;
      q("[data-fita-texto]").textContent = cotacao.atacado
        ? "Preço de atacado ativo."
        : cotacao.faltam_para_atacado === 1
          ? "Falta 1 peça para o preço de atacado."
          : `Faltam ${cotacao.faltam_para_atacado} peças para o preço de atacado.`;
      q("[data-modalidade]").textContent = cotacao.atacado ? "· atacado" : "· varejo";
      q("[data-total]").textContent = cotacao.total_fmt;
      const economia = q("[data-economia]");
      economia.hidden = !cotacao.economia_fmt;
      economia.textContent = cotacao.economia_fmt ? `Você economiza ${cotacao.economia_fmt} com o preço de atacado.` : "";
    }

    async function cotar() {
      const itens = Pedido.ler();
      if (!itens.length) { cotacao = null; render(); return; }
      try {
        cotacao = ESTATICO
          ? cotarLocal(itens, await catalogoEstatico())
          : await postar("/api/cotacao", { itens: itens.map((i) => ({ variante_id: i.v, quantidade: i.q })) });
        if (cotacao.removidos.length) {
          Pedido.gravar(itens.filter((i) => !cotacao.removidos.includes(i.v)));
        }
        render();
      } catch (e) {
        const aviso = q("[data-carregando]");
        aviso.hidden = false;
        aviso.innerHTML = `<p class="erro-form">${e.message}</p>`;
      }
    }

    function mudar(varianteId, qtd) {
      Pedido.definir(varianteId, qtd);
      clearTimeout(atraso);
      atraso = setTimeout(cotar, 120);
    }

    // Detalhe de entrega aparece só para excursão e transportadora
    const detalhe = q("[data-detalhe]");
    form.addEventListener("change", (e) => {
      if (e.target.name !== "entrega") return;
      detalhe.hidden = e.target.value === "retirada";
      q("[data-detalhe-rotulo]").textContent = e.target.value === "excursao" ? "Nome da excursão e box" : "Transportadora";
    });

    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      erro.textContent = "";
      form.querySelectorAll("[aria-invalid]").forEach((c) => c.removeAttribute("aria-invalid"));
      const dados = Object.fromEntries(new FormData(form));
      const invalido = (nome, msg) => {
        const campo = form.elements[nome];
        campo.setAttribute("aria-invalid", "true");
        campo.focus();
        erro.textContent = msg;
      };
      if ((dados.nome || "").trim().length < 2) return invalido("nome", "Informe seu nome.");
      if ((dados.whatsapp || "").replace(/\D/g, "").length < 10) return invalido("whatsapp", "Informe seu WhatsApp com DDD.");
      if (dados.entrega !== "retirada" && !(dados.detalhe_entrega || "").trim())
        return invalido("detalhe_entrega", dados.entrega === "excursao" ? "Informe o nome da excursão." : "Informe a transportadora.");

      const botao = q("[data-enviar]");
      const original = botao.innerHTML;
      if (ESTATICO) {
        const cat = await catalogoEstatico();
        const c = cotarLocal(Pedido.ler(), cat);
        const falta = c.linhas.find((l) => l.quantidade > l.disponivel);
        if (falta) {
          erro.textContent = `${falta.peca} (${falta.cor}, ${falta.tamanho}): só temos ${falta.disponivel} em estoque.`;
          return;
        }
        const url = `https://wa.me/${cat.loja.whatsapp.replace(/\D/g, "")}?text=${encodeURIComponent(mensagemLocal(c, dados, cat.loja))}`;
        Pedido.limpar();
        window.location.href = url;
        return;
      }

      botao.disabled = true;
      botao.innerHTML = '<span class="carregando" aria-hidden="true"></span> Registrando o pedido…';
      try {
        const r = await postar("/api/pedidos", {
          ...dados,
          itens: Pedido.ler().map((i) => ({ variante_id: i.v, quantidade: i.q })),
        });
        Pedido.limpar();
        window.location.href = r.url;
      } catch (falha) {
        erro.textContent = falha.message;
        botao.disabled = false;
        botao.innerHTML = original;
        cotar();
      }
    });

    cotar();
  }

  // ------------------------------------------------------------ início

  document.addEventListener("DOMContentLoaded", () => {
    atualizarContador();
    prepararMoldes();
    document.querySelectorAll("[data-compra]").forEach(prepararCompra);
    prepararGaleria();
    document.querySelectorAll("[data-auto-enviar]").forEach((s) => s.addEventListener("change", () => s.form.submit()));
    const pagina = document.querySelector("[data-pagina-pedido]");
    if (pagina) prepararPaginaPedido(pagina);
  });
  window.addEventListener("storage", (e) => e.key === CHAVE && atualizarContador());
})();
