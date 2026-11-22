/* ESCUDO Concursos: JS mínimo (vitrine, zoom das páginas, barra de compra no celular e fim do cupom). A página funciona sem ele. */
(function () {
  "use strict";

  /* 1. Fim do cupom: elementos com data-cupom-ate somem depois da data; os com data-sem-cupom aparecem.
        Links com data-href-sem-cupom trocam de destino. */
  var agora = Date.now();
  document.querySelectorAll("[data-cupom-ate]").forEach(function (el) {
    var fim = Date.parse(el.getAttribute("data-cupom-ate"));
    if (isNaN(fim) || agora <= fim) return;
    var escopo = el.closest("[data-oferta]") || document;
    el.hidden = true;
    escopo.querySelectorAll("[data-sem-cupom]").forEach(function (s) { s.hidden = false; });
  });
  document.querySelectorAll("a[data-href-sem-cupom][data-fim-cupom]").forEach(function (a) {
    if (agora > Date.parse(a.getAttribute("data-fim-cupom"))) a.href = a.getAttribute("data-href-sem-cupom");
  });

  /* 4. Vitrine da página inicial: refaz selos e ordem com a data de hoje, esconde curso com prova passada
        e filtra por carreira. O filtro fica no endereço (#policial) para dar link direto num post. */
  var vitrine = document.querySelector("[data-vitrine]");
  if (vitrine) {
    var DIA = 864e5;
    var hoje = new Date(new Date().toLocaleString("en-US", { timeZone: "America/Sao_Paulo" }));
    hoje.setHours(0, 0, 0, 0);
    var data = function (s) { var p = s.split("-"); return new Date(+p[0], p[1] - 1, +p[2]); };
    var ddmm = function (s) { var p = s.split("-"); return p[2] + "/" + p[1]; };
    var cartoes = Array.prototype.slice.call(vitrine.querySelectorAll(".produto"));
    cartoes.forEach(function (li) {
      var ev = [];
      try { ev = JSON.parse(li.getAttribute("data-eventos")) || []; } catch (err) { return; }
      var prox = ev.filter(function (x) { return data(x.data) >= hoje; });
      if (!prox.length) { li.hidden = true; li.setAttribute("data-encerrado", ""); return; }
      var x = prox[0], selo = li.querySelector("[data-selo]");
      var juntos = x.tipo === "cupom" && prox.some(function (y) { return y.tipo === "inscricoes" && y.data === x.data; });
      // "previsto" = curso sem edital novo (data 2099-12-31 no vitrine.py): selo sem data e o cartão nunca some
      var txt = x.tipo === "previsto" ? "Edital previsto" : x.tipo === "prevenda" ? "Pré-venda até sair o edital" :
        { cupom: juntos ? "Cupom e inscrições até " : "Cupom até ", inscricoes: "Inscrições até ", prova: "Prova em " }[x.tipo] + ddmm(x.data);
      var faltam = Math.round((data(x.data) - hoje) / DIA);
      if (faltam <= 7 && x.tipo !== "previsto" && x.tipo !== "prevenda") txt += faltam === 0 ? " · último dia" : " · faltam " + faltam + " dia" + (faltam > 1 ? "s" : "");
      if (selo) { selo.textContent = txt; selo.classList.toggle("urgente", faltam <= 7); }
      li.setAttribute("data-chave", x.data);
    });
    cartoes.filter(function (li) { return !li.hasAttribute("data-encerrado"); })
      .sort(function (a, b) { return a.getAttribute("data-chave") < b.getAttribute("data-chave") ? -1 : 1; })
      .forEach(function (li) { vitrine.appendChild(li); });

    var abertos = cartoes.filter(function (li) { return !li.hasAttribute("data-encerrado"); });
    var caixa = document.querySelector("[data-filtros]"), vazia = document.querySelector("[data-vazia]");
    var chips = caixa ? Array.prototype.slice.call(caixa.querySelectorAll("[data-filtro]")) : [];
    chips.forEach(function (b) {
      var k = b.getAttribute("data-filtro");
      var n = abertos.filter(function (li) { return !k || li.getAttribute("data-carreira") === k; }).length;
      var conta = b.querySelector("[data-conta]");
      if (conta) conta.textContent = n;
      if (k && !n) b.hidden = true;
    });
    var visiveis = chips.filter(function (b) { return !b.hidden; });
    if (vazia) vazia.hidden = abertos.length > 0;
    /* Busca por concurso (07/11/2026): soma com o filtro de carreira; ignora acento, caixa e hífen. */
    var limpa = function (t) { return (t || "").normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().replace(/[^a-z0-9]+/g, " ").trim(); };
    var campo = document.querySelector("[data-busca-campo]"), semRes = document.querySelector("[data-sem-resultado]");
    var atual = "";
    var aplica = function () {
      var termos = limpa(campo ? campo.value : "").split(" ").filter(Boolean), n = 0;
      abertos.forEach(function (li) {
        var txt = " " + limpa(li.getAttribute("data-busca")) + " ";
        var ok = (!atual || li.getAttribute("data-carreira") === atual) &&
          termos.every(function (t) { return txt.indexOf(" " + t) >= 0; });
        li.hidden = !ok; if (ok) n++;
      });
      if (semRes) semRes.hidden = n > 0 || !abertos.length;
      /* busca sem resultado: conta no GoatCounter o que a pessoa procurou (mostra demanda de apostila nova) */
      clearTimeout(aplica.t);
      var q = campo ? campo.value.trim() : "";
      if (!n && q.length >= 3) aplica.t = setTimeout(function () {
        if (window.goatcounter && goatcounter.count) goatcounter.count({ path: "busca-sem-resultado/" + limpa(q).replace(/ /g, "-").slice(0, 60), title: q.slice(0, 80), event: true });
      }, 1500);
    };
    var pedirBusca = document.querySelector("[data-pedir-busca]");
    if (pedirBusca) pedirBusca.addEventListener("click", function () {
      var c = document.querySelector("[data-pedido-concurso]");
      if (c && campo) { c.value = campo.value.trim(); setTimeout(function () { c.focus(); }, 300); }
    });
    var filtra = function (k, rolar) {
      if (!chips.some(function (b) { return !b.hidden && b.getAttribute("data-filtro") === k; })) k = "";
      chips.forEach(function (b) { b.setAttribute("aria-pressed", String(b.getAttribute("data-filtro") === k)); });
      atual = k;
      aplica();
      if (rolar) { var sec = document.getElementById("cursos"); if (sec) sec.scrollIntoView(); }
    };
    if (campo && abertos.length > 6) {
      campo.closest("[data-busca-caixa]").hidden = false;
      campo.addEventListener("input", aplica);
    }
    if (caixa && visiveis.length > 2) {
      caixa.hidden = false;
      caixa.addEventListener("click", function (ev) {
        var b = ev.target.closest("[data-filtro]");
        if (!b) return;
        var k = b.getAttribute("data-filtro");
        filtra(k, false);
        if (history.replaceState) history.replaceState(null, "", k ? "#" + k : location.pathname + location.search);
      });
    }
    var h = decodeURIComponent(location.hash.slice(1));
    if (h && h !== "cursos" && h !== "conteudo") filtra(h, true);
  }

  /* 2. Zoom das páginas do PDF */
  var dlg = document.getElementById("zoom");
  if (dlg && typeof dlg.showModal === "function") {
    var img = dlg.querySelector("img"), leg = dlg.querySelector("p");
    document.querySelectorAll("[data-zoom]").forEach(function (a) {
      a.addEventListener("click", function (e) {
        e.preventDefault();
        var mini = a.querySelector("img");
        img.src = a.getAttribute("href");
        img.alt = mini ? mini.alt : "";
        leg.textContent = a.getAttribute("data-zoom");
        dlg.showModal();
      });
    });
    dlg.addEventListener("click", function (e) { if (e.target === dlg || e.target.closest("button")) dlg.close(); });
    dlg.addEventListener("close", function () { img.removeAttribute("src"); });
  }

  /* 3. Barra fixa de compra: aparece depois que o botão do topo passou e some no bloco final de compra */
  var barra = document.querySelector(".barra"), alvo = document.querySelector("[data-observa]");
  if (barra && alvo) {
    document.body.classList.add("com-barra");
    var fim = document.querySelector("[data-esconde-barra]"), pendente = false;
    var atualiza = function () {
      pendente = false;
      var passou = alvo.getBoundingClientRect().bottom < 0;
      var noFim = fim ? fim.getBoundingClientRect().top < window.innerHeight : false;
      barra.classList.toggle("on", passou && !noFim);
    };
    var agenda = function () { if (!pendente) { pendente = true; requestAnimationFrame(atualiza); } };
    window.addEventListener("scroll", agenda, { passive: true });
    window.addEventListener("resize", agenda);
    atualiza();
  }
})();

/* Origem da visita, repassada aos links do checkout:
   - ?src=gads (ou outro) troca o src=site, para a Hotmart mostrar a origem no filtro "Origem (SRC)";
   - gclid, gbraid, wbraid e utm_* seguem junto, para o pixel do Google Ads na Hotmart ligar a venda ao clique.
   Guardado na sessão: vale também se a pessoa entra pela home e só depois abre a página do curso. */
(function () {
  var CHAVES = ["src", "gclid", "gbraid", "wbraid", "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content"];
  var guardado = {};
  try { guardado = JSON.parse(sessionStorage.getItem("escudo-origem") || "{}"); } catch (e) { guardado = {}; }
  var url = new URLSearchParams(location.search), novo = false;
  CHAVES.forEach(function (k) {
    var v = url.get(k);
    if (v && /^[\w.~-]{1,200}$/.test(v)) { guardado[k] = v; novo = true; }
  });
  /* Sem src na URL: usa utm_source ou o site de onde a pessoa veio (06/11/2026), para a Hotmart separar
     ChatGPT, Google, Instagram etc. em vez de juntar tudo em src=site. */
  if (!guardado.src) {
    var origem = guardado.utm_source || "";
    if (!origem && document.referrer) {
      var host = "";
      try { host = new URL(document.referrer).hostname.replace(/^www\./, ""); } catch (e) {}
      var MAPA = [[/chatgpt\.com|openai\.com/, "chatgpt"], [/instagram\.com/, "instagram"], [/facebook\.com|fb\.com/, "facebook"],
        [/whatsapp|wa\.me/, "whatsapp"], [/gemini\.google|bard\.google/, "gemini"], [/google\./, "google"], [/bing\.com/, "bing"],
        [/perplexity\.ai/, "perplexity"], [/youtube\.com/, "youtube"], [/t\.co$|twitter\.com|x\.com/, "x"],
        [/escudoconcursos\.(github\.io|com\.br)$/, ""]];
      for (var i = 0; i < MAPA.length; i++) { if (MAPA[i][0].test(host)) { origem = MAPA[i][1]; break; } }
      if (!origem && host) origem = "ref-" + host.replace(/[^\w.-]/g, "").slice(0, 40);
    }
    origem = origem.replace(/\.(com|ai|me)$/, "").replace(/[^\w.~-]/g, "").slice(0, 40);
    if (origem) { guardado.src = "site-" + origem; novo = true; }
  }
  if (novo) { try { sessionStorage.setItem("escudo-origem", JSON.stringify(guardado)); } catch (e) {} }

  /* Página de entrada e página do clique no sck (21/11/2026): o src diz de onde a pessoa veio (chatgpt, google,
     instagram), o sck diz por qual parte do site ela entrou (guia, blog, amostra, hub, home ou o próprio curso).
     No relatório da Hotmart, filtro "Código de origem do checkout (SCK)". Ex.: src=site-chatgpt, sck=guia-pm-pe_curso. */
  function tipo(caminho) {
    var p = (caminho || "/").replace(/^\/+|\/+$/g, ""), partes = p.split("/");
    if (!p) return "home";
    if (partes[0] === "noticias") return partes[1] ? "blog-" + partes[1].slice(0, 24) : "blog";
    if (partes[1] === "amostra") return "amostra";
    if (/^concurso-/.test(partes[0])) return "guia-" + partes[0].replace(/^concurso-/, "").slice(0, 28);
    if (/^concursos-/.test(partes[0])) return "hub-" + partes[0].replace(/^concursos-/, "").slice(0, 20);
    if (/-20\d\d$/.test(partes[0])) return "curso";
    return partes[0].slice(0, 20);
  }
  var entrada = "";
  try { entrada = sessionStorage.getItem("escudo-entrada") || ""; } catch (e) {}
  if (!entrada) { entrada = tipo(location.pathname); try { sessionStorage.setItem("escudo-entrada", entrada); } catch (e) {} }
  var aqui = tipo(location.pathname), sck = (entrada === aqui ? entrada : entrada + "_" + aqui).replace(/[^\w.~-]/g, "").slice(0, 60);
  if (!guardado.src) guardado.src = "site";
  guardado.sck = sck;
  document.querySelectorAll('a[href*="pay.hotmart.com"]').forEach(function (a) {
    var u = new URL(a.href);
    Object.keys(guardado).forEach(function (k) { u.searchParams.set(k, guardado[k]); });
    a.href = u.toString();
  });
})();

/* 7. Pedido de apostila que não está no site (07/11/2026): envia direto para o Apps Script do Mateus
      (planilha + e-mail) quando o bloco tem data-endpoint; senão abre um e-mail pronto. Conta no GoatCounter. */
(function () {
  document.querySelectorAll("[data-pedido-form]").forEach(function (f) {
    f.addEventListener("submit", function (ev) {
      ev.preventDefault();
      var caixa = f.closest("[data-pedido]"), email = caixa.getAttribute("data-email"), url = caixa.getAttribute("data-endpoint");
      var concurso = (f.elements.concurso.value || "").trim(), cargo = (f.elements.cargo.value || "").trim();
      var contato = (f.elements.contato.value || "").trim();
      if (!concurso) { f.elements.concurso.focus(); return; }
      if (window.goatcounter && goatcounter.count) goatcounter.count({ path: "pedido-apostila", title: (concurso + (cargo ? " / " + cargo : "")).slice(0, 100), event: true });
      var ok = caixa.querySelector(".pedido-ok");
      if (!ok) { ok = document.createElement("p"); ok.className = "pedido-ok"; ok.setAttribute("role", "status"); caixa.appendChild(ok); }
      var porEmail = function () {
        var corpo = "Olá, ESCUDO! Não encontrei no site a apostila que procuro.\n\nConcurso: " + concurso + "\nCargo: " + (cargo || "(não sei ainda)") + "\n\nPode me avisar se vocês fizerem?\n";
        location.href = "mailto:" + email + "?subject=" + encodeURIComponent("Pedido de apostila: " + concurso + (cargo ? " - " + cargo : "")) + "&body=" + encodeURIComponent(corpo);
        ok.textContent = "Abrimos o seu e-mail com o pedido pronto. É só enviar.";
      };
      if (!url) { porEmail(); return; }
      var dados = new URLSearchParams({ concurso: concurso, cargo: cargo, pagina: location.pathname,
        origem: (function () { try { return (JSON.parse(sessionStorage.getItem("escudo-origem") || "{}").src) || ""; } catch (e) { return ""; } })(),
        site_url: f.elements.site_url.value });
      if (/@/.test(contato)) dados.set("email", contato); else dados.set("whatsapp", contato);
      var botao = f.querySelector("button"); botao.disabled = true; ok.textContent = "Enviando...";
      fetch(url, { method: "POST", mode: "no-cors", body: dados }).then(function () {
        ok.textContent = "Pedido enviado! Obrigado. " + (contato ? "Vamos te avisar quando o curso sair." : "Acompanhe as novidades no Instagram @escudoconcursos.");
        f.reset();
      }).catch(porEmail).then(function () { botao.disabled = false; });
    });
  });
})();

/* 8. Lista "Avise-me quando sair o edital" (22/11/2026): e-mail e WhatsApp vão para o mesmo App da Web dos pedidos,
      com tipo=lista (aba "Lista de espera" da planilha). Sem endpoint, abre um e-mail pronto. Conta no GoatCounter. */
(function () {
  var origem = function () { try { return (JSON.parse(sessionStorage.getItem("escudo-origem") || "{}").src) || ""; } catch (e) { return ""; } };
  document.querySelectorAll("[data-lista-form]").forEach(function (f) {
    f.addEventListener("submit", function (ev) {
      ev.preventDefault();
      var caixa = f.closest("[data-lista]"), url = caixa.getAttribute("data-endpoint");
      var email = (f.elements.email.value || "").trim(), zap = (f.elements.whatsapp.value || "").replace(/[^\d+]/g, "");
      if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) { f.elements.email.focus(); return; }
      var curso = caixa.getAttribute("data-curso"), concurso = caixa.getAttribute("data-concurso");
      if (window.goatcounter && goatcounter.count) goatcounter.count({ path: "lista-edital", title: curso, event: true });
      var ok = caixa.querySelector(".pedido-ok");
      if (!ok) { ok = document.createElement("p"); ok.className = "pedido-ok"; ok.setAttribute("role", "status"); f.parentNode.insertBefore(ok, f.nextSibling); }
      var porEmail = function () {
        location.href = "mailto:" + caixa.getAttribute("data-email") + "?subject=" + encodeURIComponent("Avise-me do edital: " + concurso) +
          "&body=" + encodeURIComponent("Quero o aviso quando sair o edital " + concurso + ".\nWhatsApp: " + (zap || "-") + "\n");
        ok.textContent = "Abrimos o seu e-mail com o pedido pronto. É só enviar.";
      };
      if (!url) { porEmail(); return; }
      var dados = new URLSearchParams({ tipo: "lista", curso: curso, concurso: concurso, cargo: caixa.getAttribute("data-cargo") || "",
        email: email, whatsapp: zap, pagina: location.pathname, origem: origem() + "|" + (caixa.getAttribute("data-origem-bloco") || ""),
        site_url: f.elements.site_url.value });
      var botao = f.querySelector("button"); botao.disabled = true; ok.textContent = "Enviando...";
      fetch(url, { method: "POST", mode: "no-cors", body: dados }).then(function () {
        ok.textContent = "Pronto! Você está na lista do edital " + concurso + ". Avisamos no dia em que ele sair.";
        f.reset();
      }).catch(porEmail).then(function () { botao.disabled = false; });
    });
  });
})();

/* 9. Simulado grátis (22/11/2026): as questões vêm num <script type="application/json" id="simulado-dados">.
      Nota na hora por disciplina; o gabarito comentado aparece depois do e-mail (tipo=simulado no App da Web). */
(function () {
  var raiz = document.querySelector("[data-simulado]");
  var fonte = document.getElementById("simulado-dados");
  if (!raiz || !fonte) return;
  var S = JSON.parse(fonte.textContent), Q = S.questoes, lista = raiz.querySelector("[data-sim-questoes]");
  var esc = function (s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); };
  var md = function (s) { return esc(s).replace(/\*\*(.+?)\*\*/g, "<b>$1</b>").replace(/\n{2,}/g, "</p><p>").replace(/\n/g, "<br>"); };
  var letras = function (q) { return q.tipo === "ce" ? ["C", "E"] : Object.keys(q.alternativas); };
  var rotulo = function (q, l) { return q.tipo === "ce" ? (l === "C" ? "Certo" : "Errado") : q.alternativas[l]; };
  lista.innerHTML = Q.map(function (q, i) {
    return '<li class="sim-q" id="q' + (i + 1) + '"><p class="sim-disc">' + esc(q.disciplina) + '</p><div class="sim-enun"><p>' + md(q.enunciado) + "</p></div>" +
      '<fieldset><legend class="sr">Questão ' + (i + 1) + "</legend>" + letras(q).map(function (l) {
        return '<label class="sim-alt"><input type="radio" name="q' + i + '" value="' + l + '"><b>' + l + "</b><span>" + md(rotulo(q, l)) + "</span></label>";
      }).join("") + '</fieldset><div class="sim-coment" hidden></div></li>';
  }).join("");
  var conta = function (ev) { if (window.goatcounter && goatcounter.count) goatcounter.count({ path: ev, title: S.curso_id, event: true }); };
  var comecou = false;
  lista.addEventListener("change", function () { if (!comecou) { comecou = true; conta("simulado-inicio"); } });
  var resultado = raiz.querySelector("[data-sim-resultado]"), gate = raiz.querySelector("[data-sim-gate]");
  var respostas = function () { return Q.map(function (q, i) { var m = lista.querySelector('input[name="q' + i + '"]:checked'); return m ? m.value : ""; }); };
  raiz.querySelector("[data-sim-corrigir]").addEventListener("click", function () {
    var r = respostas(), brancas = r.filter(function (x) { return !x; }).length;
    if (brancas && !confirm("Faltam " + brancas + " questões. Corrigir assim mesmo?")) return;
    var por = {}, total = 0;
    Q.forEach(function (q, i) {
      var d = por[q.disciplina] || (por[q.disciplina] = { a: 0, n: 0 }); d.n++;
      if (r[i] === q.gabarito) { d.a++; total++; }
    });
    var pct = Math.round(total / Q.length * 100);
    resultado.innerHTML = '<p class="sim-nota"><b>' + total + " de " + Q.length + "</b> (" + pct + "%)</p>" +
      '<p class="sim-frase">' + (pct >= 70 ? "Ótimo resultado. Agora é manter o ritmo até a prova." : pct >= 50 ? "Bom começo. Veja no gabarito comentado onde estão os pontos a reforçar." : "Ainda há chão pela frente, e o gabarito comentado mostra por onde começar.") + "</p>" +
      '<table class="sim-tabela"><thead><tr><th>Disciplina</th><th>Acertos</th></tr></thead><tbody>' +
      Object.keys(por).map(function (k) { return "<tr><td>" + esc(k) + "</td><td>" + por[k].a + "/" + por[k].n + "</td></tr>"; }).join("") + "</tbody></table>";
    resultado.hidden = false; gate.hidden = false;
    raiz.setAttribute("data-nota", total + "/" + Q.length);
    conta("simulado-nota");
    resultado.scrollIntoView({ behavior: "smooth", block: "start" });
  });
  var revela = function () {
    var r = respostas();
    Q.forEach(function (q, i) {
      var li = lista.children[i], c = li.querySelector(".sim-coment");
      li.classList.add(r[i] === q.gabarito ? "certa" : "errada");
      li.querySelectorAll(".sim-alt").forEach(function (lab) {
        var v = lab.querySelector("input").value;
        if (v === q.gabarito) lab.classList.add("gabarito");
        else if (v === r[i]) lab.classList.add("marcada-errada");
      });
      c.innerHTML = "<p><b>Gabarito: " + esc(q.tipo === "ce" ? rotulo(q, q.gabarito) : q.gabarito) + ".</b> " + md(q.comentario) + "</p>";
      c.hidden = false;
    });
    gate.hidden = true;
    raiz.querySelector("[data-sim-final]").hidden = false;
    try { localStorage.setItem("escudo-sim-" + S.curso_id, "1"); } catch (e) {}
  };
  var f = gate.querySelector("form");
  f.addEventListener("submit", function (ev) {
    ev.preventDefault();
    var email = (f.elements.email.value || "").trim();
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) { f.elements.email.focus(); return; }
    var url = raiz.getAttribute("data-endpoint");
    conta("simulado-gabarito");
    if (url) {
      var dados = new URLSearchParams({ tipo: "simulado", curso: S.curso_id, concurso: S.titulo, email: email,
        whatsapp: (f.elements.whatsapp.value || "").replace(/[^\d+]/g, ""), nota: raiz.getAttribute("data-nota") || "",
        pagina: location.pathname, site_url: f.elements.site_url.value });
      fetch(url, { method: "POST", mode: "no-cors", body: dados }).catch(function () {});
    }
    revela();
  });
})();
