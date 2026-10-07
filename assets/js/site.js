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
      var txt = { cupom: juntos ? "Cupom e inscrições até " : "Cupom até ", inscricoes: "Inscrições até ", prova: "Prova em " }[x.tipo] + ddmm(x.data);
      var faltam = Math.round((data(x.data) - hoje) / DIA);
      if (faltam <= 7) txt += faltam === 0 ? " · último dia" : " · faltam " + faltam + " dia" + (faltam > 1 ? "s" : "");
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
    var filtra = function (k, rolar) {
      if (!chips.some(function (b) { return !b.hidden && b.getAttribute("data-filtro") === k; })) k = "";
      chips.forEach(function (b) { b.setAttribute("aria-pressed", String(b.getAttribute("data-filtro") === k)); });
      abertos.forEach(function (li) { li.hidden = !!k && li.getAttribute("data-carreira") !== k; });
      if (rolar) { var sec = document.getElementById("cursos"); if (sec) sec.scrollIntoView(); }
    };
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
