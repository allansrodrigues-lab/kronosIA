// ===== "n8n de mentirinha" — agora mandando VÁRIOS itens =====
const { BuscarCep } = require('./dist/BuscarCep.node.js');

// 2 CEPs: o 1º é válido (Av. Paulista), o 2º é inválido (pra testar o erro).
const ceps = ['01310100', '99999999'];

const contextoFake = {
  // o n8n entrega a LISTA de itens de entrada. Aqui fingimos 2 itens:
  getInputData() {
    return [{ json: {} }, { json: {} }];
  },
  // pra cada item (indice 0 e 1), devolve o CEP correspondente:
  getNodeParameter(nome, indice) {
    if (nome === 'cep') return ceps[indice];
    return '';
  },
};

async function testar() {
  const node = new BuscarCep();
  const resultado = await node.execute.call(contextoFake);

  console.log("✅ O node processou os 2 CEPs! Resultado:\n");
  console.log(JSON.stringify(resultado, null, 2));
}

testar();
