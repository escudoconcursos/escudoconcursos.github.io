/* ESCUDO Concursos: JS mínimo (zoom das páginas, barra de compra no celular e fim do cupom). A página funciona sem ele. */
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
