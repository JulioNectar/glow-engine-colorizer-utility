// merge-files.js
const fs = require("fs");
const path = require("path");

const entrada = process.argv[2];
if (!entrada) {
    console.error("❌ Informe uma pasta ou arquivo. Ex: node merge-files.js src");
    process.exit(1);
}

const caminhoEntrada = path.resolve(entrada);
const saida = path.join(process.cwd(), "saida.txt");

function processarArquivo(caminhoArquivo) {
    if (fs.lstatSync(caminhoArquivo).isFile()) {
        const conteudo = fs.readFileSync(caminhoArquivo, "utf-8");
        const bloco = `arquivo ${path.basename(caminhoArquivo)}:\n${conteudo}\n\n----------------\n\n`;
        fs.appendFileSync(saida, bloco); // 🔑 acrescenta no final
        console.log(`📄 Arquivo adicionado: ${caminhoArquivo}`);
    }
}

if (fs.lstatSync(caminhoEntrada).isDirectory()) {
    const arquivos = fs.readdirSync(caminhoEntrada);
    arquivos.forEach((arquivo) => {
        const caminhoArquivo = path.join(caminhoEntrada, arquivo);
        processarArquivo(caminhoArquivo);
    });
} else {
    processarArquivo(caminhoEntrada);
}

console.log(`✅ Conteúdo atualizado em: ${saida}`);
