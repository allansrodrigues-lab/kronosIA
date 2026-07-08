"use strict";
// ===== TEU PRIMEIRO CUSTOM NODE n8n — BuscarCep =====
// Repara: usa TUDO que tu já aprendeu (interface, objeto, async, await, fetch).
Object.defineProperty(exports, "__esModule", { value: true });
exports.BuscarCep = void 0;
const node_dns_1 = require("node:dns");
class BuscarCep {
    // 🎭 PARTE 1 — A CARA do node (o que aparece na tela do n8n)
    description = {
        displayName: 'Buscar CEP', // nome que aparece no n8n
        name: 'buscarCep', // nome interno (sem espaços)
        icon: 'fa:map-marker-alt', // ícone
        group: ['transform'],
        version: 1,
        description: 'Busca o endereço de um CEP no ViaCEP',
        defaults: { name: 'Buscar CEP' },
        inputs: ['main'], // entrada
        outputs: ['main'], // saída
        properties: [
            // 👇 o CAMPO que o usuário preenche no n8n
            {
                displayName: 'CEP',
                name: 'cep',
                type: 'string',
                default: '',
                placeholder: '01310100',
                description: 'O CEP que você quer consultar',
            },
        ],
    };
    // ⚙️ PARTE 2 — O MIOLO (o que o node FAZ quando roda)
    async execute() {
        // Força IPv4 — a rede local não tem IPv6 funcional (senão o fetch dá ENETUNREACH).
        (0, node_dns_1.setDefaultResultOrder)('ipv4first');
        // O n8n manda uma LISTA de itens pra processar (ex: vários clientes).
        const items = this.getInputData();
        const resultados = [];
        // 🔁 percorre CADA item, um por um (igual ao loop da aula 3!)
        for (let i = 0; i < items.length; i++) {
            const cep = this.getNodeParameter('cep', i);
            // 🛡️ try/catch = "tenta isto; SE der erro, faz aquilo" (não quebra tudo)
            try {
                const resposta = await fetch('https://viacep.com.br/ws/' + cep + '/json/');
                const dados = await resposta.json();
                if (dados.erro) {
                    // o ViaCEP devolve { erro: true } quando o CEP não existe
                    resultados.push({ json: { erro: 'CEP não encontrado: ' + cep } });
                }
                else {
                    resultados.push({ json: dados });
                }
            }
            catch (e) {
                // caiu aqui = falha de rede/conexão
                resultados.push({ json: { erro: 'Falha ao buscar o CEP ' + cep } });
            }
        }
        // devolve a lista de resultados pro n8n
        return [resultados];
    }
}
exports.BuscarCep = BuscarCep;
