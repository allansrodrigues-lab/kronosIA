// ===== AULA 3 — Listas (arrays) e percorrer com loop =====

// Mesma ficha de Cliente da aula 2.
interface Cliente {
  nome: string;
  telefone: string;
  vip: boolean;
}

// 1) ARRAY = uma LISTA. Repara nos colchetes [ ].
//    "Cliente[]" quer dizer "uma lista de Clientes".
//    Antes a gente tinha 1 cliente; agora temos VÁRIOS numa lista só.
let clientes: Cliente[] = [
  { nome: "Maria", telefone: "5519990000001", vip: true  },
  { nome: "João",  telefone: "5519990000002", vip: false },
  { nome: "Aline", telefone: "5519990000003", vip: true  }
];

// Função que monta a mensagem pra UM cliente (igualzinha à aula 2).
function montarMensagem(c: Cliente): string {
  let msg = "Olá, " + c.nome + "! Sua consulta está confirmada. 😊";
  if (c.vip === true) {
    msg = msg + " Como você é VIP, ganhou 10% de desconto! 🎁";
  }
  return msg;
}

// 2) LOOP = PERCORRER a lista, um por um.
//    Lê assim: "para CADA cliente c, DENTRO de clientes, faça..."
for (const c of clientes) {
  console.log(montarMensagem(c));
}
