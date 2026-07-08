// ===== AULA 1 — As "etiquetas" do TypeScript =====

// Aqui a gente cria uma "caixa" chamada nomeCliente.
// O ": string" é a ETIQUETA dela: diz que essa caixa só guarda TEXTO.
let nomeCliente: string = "Maria";

// Outra caixa, agora com a etiqueta ": number" = só guarda NÚMERO.
let pedidosHoje: number = 3;

// Uma função é uma "receita". Esta recebe um nome (texto) e devolve
// uma saudação (texto). Repara nas etiquetas:
//   (nome: string)  -> o que ENTRA é texto
//   : string        -> o que SAI também é texto
function montarSaudacao(nome: string): string {
  return "Olá, " + nome + "! Tudo bem?";
}

// Agora a gente usa a receita e manda o resultado pra tela.
console.log(montarSaudacao(nomeCliente));
console.log("Pedidos de hoje:", pedidosHoje);
