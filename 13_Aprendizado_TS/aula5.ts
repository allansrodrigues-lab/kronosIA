// ===== AULA 5 — Chamando uma API DE VERDADE com fetch =====

// Agora não é mais "faz de conta": vamos NA INTERNET buscar dados reais.
// Usamos o ViaCEP — API pública e gratuita que devolve o endereço de um CEP.

// "async" porque vamos ESPERAR (await) a internet responder — igual a aula 4.
async function buscarEndereco(cep: string) {
  console.log("🔎 Buscando o endereço do CEP " + cep + "...");

  // fetch = "vai na internet buscar". Retorna uma Promise → await pra esperar.
  const resposta = await fetch("https://viacep.com.br/ws/" + cep + "/json/");

  // A resposta vem "crua"; .json() transforma em dados que dá pra usar (também é async).
  const dados = await resposta.json();

  // Usamos os dados REAIS que chegaram da internet:
  console.log("📍 Rua:    " + dados.logradouro);
  console.log("🏘️  Bairro: " + dados.bairro);
  console.log("🏙️  Cidade: " + dados.localidade + " - " + dados.uf);
}

// Testa com um CEP real (Avenida Paulista, São Paulo).
buscarEndereco("01310100");
