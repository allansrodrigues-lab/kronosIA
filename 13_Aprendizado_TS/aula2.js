"use strict";
// ===== AULA 2 — Objetos, interfaces e decisões (if) =====
// 2) OBJETO = um cliente de verdade, seguindo a etiqueta acima.
//    Repara: precisa ter TODOS os campos, com os tipos certos.
let cliente = {
    nome: "Maria",
    telefone: "5519999999999",
    vip: true
};
// 3) FUNÇÃO que monta a mensagem. Recebe um Cliente, devolve um texto.
//    Pra pegar um campo de dentro do objeto, usa PONTO: c.nome, c.vip
function montarMensagem(c) {
    let msg = "Olá, " + c.nome + "! Sua consulta está confirmada. 😊";
    // 4) IF = uma DECISÃO. "SE o cliente for VIP, acrescenta o desconto."
    if (c.vip === true) {
        msg = msg + " Como você é VIP, ganhou 10% de desconto! 🎁";
    }
    return msg;
}
// Usa a função e manda o resultado pra tela.
console.log(montarMensagem(cliente));
