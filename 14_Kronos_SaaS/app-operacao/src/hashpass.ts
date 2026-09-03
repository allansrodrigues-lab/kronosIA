// Utilitário: gera salt+hash de uma senha pra colocar no users.json.
// Uso: node dist/hashpass.js "minha-senha"
import { hashPassword } from './auth';

const pass = process.argv[2];
if (!pass) {
  console.log('uso: node dist/hashpass.js <senha>');
  process.exit(1);
}
console.log(JSON.stringify(hashPassword(pass)));
