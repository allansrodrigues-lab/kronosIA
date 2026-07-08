"use strict";
// ===== AULA 4 (EXPERIMENTO) — O QUE ACONTECE SEM O await =====
// É igual ao aula4.ts, MAS tiramos o "await" de propósito pra ver a bagunça.
// (mesma caixa preta que finge a Evolution)
function enviarMensagem(numero, texto) {
    return new Promise((resolve) => {
        setTimeout(() => {
            resolve('✅ Mensagem enviada para ' + numero + ': "' + texto + '"');
        }, 1000);
    });
}
async function principal() {
    console.log("📤 Mandando a mensagem... (aguarde)");
    // 👇 SEM o "await": o programa NÃO espera a resposta chegar.
    const resposta = enviarMensagem("5519999999999", "Sua consulta está confirmada!");
    console.log(resposta); // vai imprimir "Promise { <pending> }" (a promessa vazia)
    console.log("🏁 Pronto, terminei!"); // vai aparecer NA HORA, sem esperar a mensagem
}
principal();
