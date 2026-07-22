# Conceitos e análises estatísticas com R e JASP — ebook estático

Site estático (HTML/CSS/JavaScript, sem framework e sem etapa de build para
servir) do livro **“Conceitos e análises estatísticas com R e JASP”**, com uma
**camada de anotações do autor** — Luis Anunciação (PUC-Rio) — sobreposta ao
texto do livro sem alterá-lo.

O conteúdo do livro foi importado da edição em [bookdown](https://bookdown.org/)
publicada em <https://anovabr.github.io/mqt_clone/>. Este repositório reempacota
esse conteúdo como um site de leitura leve, responsivo e “mobile-first”.

## Recursos

- **Barra lateral persistente** com a árvore completa de capítulos e seções,
  destaque da seção ativa (scrollspy) e recolhimento.
- **Coluna de leitura** com fonte serifada, entrelinha generosa e largura
  máxima de ~720px.
- **Tema claro/escuro** (respeita `prefers-color-scheme`, com preferência
  persistida em `localStorage`).
- **Ajuste de tamanho de fonte** persistido.
- **Barra de ação flutuante** ciente de rolagem (voltar ao topo, tema, fonte,
  compartilhar).
- **Compartilhamento** via Web Share API no celular, com alternativa em desktop
  (copiar link + WhatsApp, X/Twitter, LinkedIn e e-mail) em três níveis: livro,
  capítulo e seção (âncora profunda).
- **Matemática** renderizada com KaTeX e **código** com highlight.js (via CDN).
- **Navegação anterior/próximo**, barra de progresso de leitura e âncoras de
  seção que copiam um link direto.
- Meta tags **Open Graph** e **Twitter Card** por capítulo.
- Acessível: alvos de toque ≥44px, `prefers-reduced-motion`, `skip-link`,
  rótulos ARIA.

## Estrutura

```
.
├── index.html, <capítulo>.html      # páginas estáticas (uma por capítulo)
├── assets/
│   ├── css/style.css                # todo o estilo
│   ├── js/app.js                    # todo o comportamento (vanilla JS)
│   ├── img/                         # imagens do livro (/img importadas)
│   └── figure-html/                 # figuras geradas pelo R
├── content/
│   ├── <capítulo>.html              # texto do livro (fonte da verdade, limpo)
│   ├── toc.json                     # estrutura do livro (capítulos + âncoras)
│   └── annotations.json             # ← CAMADA DO AUTOR (edite este arquivo)
└── tools/
    ├── build.py                     # gerador (regenera as páginas)
    ├── verify.py                    # verificação estrutural
    └── src/                         # HTML bookdown original (entrada do build)
```

## Adicionando anotações do autor

Edite **`content/annotations.json`** — nenhuma outra alteração é necessária, e o
texto do livro não é tocado. As chaves são o *slug* do capítulo (nome do arquivo
sem `.html`) e, dentro dele, o `id` de uma seção (a âncora após o `#` na URL).
Campos por seção: `note` (destaque “Nota do autor”), `aside` (comentário
lateral). Use `_chapter` para um espaço de exemplos/relatórios no fim do
capítulo (`title`, `subtitle`, `body` em HTML, com suporte a
`<pre><code class="language-r">` e matemática KaTeX). Veja os exemplos já
presentes no arquivo.

## Servir localmente

```bash
python3 -m http.server 8971
# abra http://localhost:8971/index.html
```

(É preciso servir por HTTP — abrir via `file://` impede o carregamento de
`annotations.json`.)

## Regenerar as páginas (opcional)

Só é necessário se você reimportar o texto do livro. Requer
`beautifulsoup4` e `lxml`:

```bash
python3 tools/build.py     # regenera as páginas a partir de tools/src/
python3 tools/verify.py    # verificação estrutural (servidor local ativo)
```

## Site publicado

Este site é publicado em:

**<https://anovabr.github.io/mqt-ebook/>**

servido pelo GitHub Pages a partir da raiz do branch `main` de
[`anovabr/mqt-ebook`](https://github.com/anovabr/mqt-ebook).

Para publicar em outra conta/repositório, `publish.sh` cria um repositório
público e habilita o GitHub Pages em um único passo:

```bash
bash publish.sh
```

## Créditos e licença

Conteúdo do livro © seus autores originais (projeto
[`anovabr/mqt_clone`](https://github.com/anovabr/mqt_clone)); consulte a licença
do projeto original. Camada de anotações e empacotamento do site por
**Luis Anunciação** (PUC-Rio).