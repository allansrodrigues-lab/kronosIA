"use strict";
// ===== AULA 4 — Conversando com a internet (async / await) =====
// 1) CAIXA PRETA (eu te dou pronta) — não precisa entender as tripas agora.
//    Esta função FINGE ser a Evolution API mandando uma mensagem.
//    Na vida real ela iria pra internet; aqui ela só "demora 1 segundo"
//    de propósito, pra tu sentir a espera. O "Promise" é a PROMESSA de
//    que a resposta VAI chegar (só que não na hora).
function enviarMensagem(numero, texto) {
    return new Promise((resolve) => {
        setTimeout(() => {
            resolve('✅ Mensagem enviada para ' + numero + ': "' + texto + '"');
        }, 1000); // 1000 ms = 1 segundo de "demora da internet"
    });
}
// 2) O QUE IMPORTA PRA TI: uma função "async" sabe ESPERAR.
async function principal() {
    console.log("📤 Mandando a mensagem... (aguarde)");
    // "await" = ESPERA a resposta chegar antes de seguir pra próxima linha.
    const resposta = await enviarMensagem("5519999999999", "Sua consulta está confirmada!");
    // Estas linhas só rodam DEPOIS que a resposta chegou (1 segundo depois).
    console.log(resposta);
    console.log("🏁 Pronto, terminei!");
}
// Chama a função principal pra tudo acontecer.
principal();
