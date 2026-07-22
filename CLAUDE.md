# CLAUDE.md — guia para o Claude Code (e para o mantenedor)

> Leia este arquivo primeiro. Ele explica **o que** este repositório é, **por que**
> foi construído assim, e **como** estendê-lo com segurança. Mantenha-o atualizado
> quando fizer mudanças estruturais.

## O que é

Site estático do livro **“Conceitos e análises estatísticas com R e JASP”**
(autor: **Luis Anunciação, PUC-Rio**), com uma **camada de anotações do autor**
sobreposta ao texto do livro **sem alterá-lo**.

- **Publicado em:** <https://anovabr.github.io/mqt-ebook/>
- **Servido por:** GitHub Pages, modo **“Deploy from a branch” → `main` / `/root`**.
  Todo push para `main` dispara automaticamente o workflow dinâmico
  “pages build and deployment”. **Não há workflow em `.github/`** (veja “Decisões”).
- **Conteúdo importado de:** a edição bookdown em
  <https://anovabr.github.io/mqt_clone/> (repo [`anovabr/mqt_clone`](https://github.com/anovabr/mqt_clone),
  pasta `docs/` renderizada). O HTML bruto original está em `tools/src/`.

## Princípios (não quebre estes)

1. **O site servido é HTML/CSS/JS puro, sem framework e sem etapa de build para
   rodar.** `tools/build.py` é um gerador usado só quando se reimporta/edita o
   texto do livro; o artefato servido são os `*.html` na raiz.
2. **Todos os caminhos são relativos e nunca começam com `/`** — o site tem que
   funcionar no subcaminho `…/mqt-ebook/`. Nunca introduza `src="/..."` ou
   `href="/..."`.
3. **Não edite o texto do livro** para adicionar comentários do autor. Use a
   camada de anotações (`content/annotations.json`). O texto do livro é
   importado e tratado como fonte estável.
4. **Dependency-light.** Sem bundler, sem npm em runtime. Só KaTeX + highlight.js
   via CDN. JS é vanilla.
5. **Mobile-first e acessível:** alvos de toque ≥44px, sem scroll horizontal,
   `prefers-reduced-motion`, `prefers-color-scheme`.

## Estrutura

```
index.html, <capítulo>.html      # 20 páginas geradas (Cap. 1–20), servidas na raiz
assets/
  css/style.css                  # TODO o estilo (mobile-first, claro/escuro)
  js/app.js                      # TODO o comportamento (vanilla JS)
  img/                           # imagens do livro (261) + favicon.svg
    capa_jolie.png               # CAPA OFICIAL (com selo "Versão do autor")
    capa_jolie_original.png      # capa original sem selo (backup)
  figure-html/                   # figuras geradas pelo R (206)
content/
  <capítulo>.html                # texto limpo do livro (fragmentos, fonte da verdade p/ o build)
  toc.json                       # estrutura do livro (capítulos + âncoras)
  annotations.json               # ← CAMADA DO AUTOR (edite aqui)
tools/
  build.py                       # gerador das páginas (lê tools/src/, escreve content/ e *.html)
  verify.py                      # verificação estrutural (precisa de servidor local)
  make_cover_badge.py            # gera a capa com o selo "Versão do autor"
  src/                           # HTML bookdown ORIGINAL (entrada do build.py)
  build_data.json                # manifesto do último build (gerado)
publish.sh                       # cria um repo público novo e habilita Pages (uso opcional/outra conta)
.nojekyll                        # impede o Jekyll de interferir nos assets
```

## Como as coisas funcionam

- **`tools/build.py`** lê cada arquivo de `tools/src/*.html` (o bookdown
  original), extrai só o conteúdo real do capítulo (`section.normal` →
  `div.section.level1`), descarta a moldura gitbook, e:
  - reescreve imagens `img/…` → `assets/img/…` e `gitbook-demo_files/figure-html/…`
    → `assets/figure-html/…` (corrige diferença de maiúsculas `.PNG`/`.png`,
    pois o Linux do Pages é sensível a isso);
  - converte blocos de código para `<pre><code class="language-r">` (realce
    via highlight.js);
  - envolve tabelas em `.table-wrap` (scroll horizontal no mobile);
  - grava o fragmento limpo em `content/<arquivo>.html` **e** a página completa
    (com sidebar, nav, meta OG/Twitter, etc.) na raiz;
  - gera `content/toc.json` (a sidebar de todas as páginas vem daqui).
  - **Importante:** o build **sobrescreve** `content/*.html` e os `*.html` da
    raiz a partir de `tools/src/`. Portanto, mudanças no texto/estrutura devem
    ser feitas em `tools/src/` (durável) — não direto em `content/` nem nos
    `*.html` da raiz, pois o próximo build as apaga.
- **`assets/js/app.js`** faz tema (persistido em `localStorage: mqt-theme`),
  tamanho de fonte (`mqt-fontsize`), sidebar/scrollspy/colapso, barra de
  progresso, barra de ação flutuante ciente de rolagem, compartilhamento
  (Web Share API + fallback WhatsApp/X/LinkedIn/e-mail; níveis livro/capítulo/
  seção), âncoras de seção com deep-link, e **injeção das anotações** a partir de
  `content/annotations.json`.
- **KaTeX** usa só os delimitadores `\( \)` e `\[ \]`. **Não** habilite `$…$`
  (o texto em português usa `R$` de moeda).

## Fluxos de trabalho comuns

### Adicionar anotações do autor (o caso mais comum) — NÃO precisa de build

Edite **`content/annotations.json`** (pode ser direto no GitHub). Chaves de 1º
nível = *slug* do capítulo (nome do arquivo sem `.html`, ex.: `teste-t`,
`correlação`). Dentro, use o `id` de uma seção (a âncora após `#` na URL):

```json
{
  "teste-t": {
    "tamanho-do-efeito-1": {
      "note": "Destaque 'Nota do autor' logo após o título da seção.",
      "aside": "Comentário lateral inline."
    },
    "_chapter": {
      "title": "Exemplos e análises do autor",
      "subtitle": "código + saída + interpretação",
      "body": "<p>HTML livre; aceita <pre><code class=\"language-r\">…</code></pre> e matemática KaTeX.</p>"
    }
  }
}
```

`note`/`aside` são injetados após o título da seção; `_chapter.body` vai ao fim
do capítulo. Nenhuma outra alteração é necessária — o `app.js` carrega o JSON em
runtime. Descubra `id`s de seção em `content/toc.json` ou na URL do site.

### Regerar as páginas (após editar o texto do livro em `tools/src/`)

```bash
pip install beautifulsoup4 lxml
python3 tools/build.py
```

### Verificar

```bash
python3 -m http.server 8971            # servir
python3 tools/verify.py                # checagem estrutural (20/20, 0 falhas esperado)
```

### Ver localmente

```bash
python3 -m http.server 8971    # abra http://localhost:8971/index.html
```
(Sirva por HTTP; `file://` quebra o fetch de `annotations.json`.)

### Atualizar a capa / o selo "Versão do autor"

A capa oficial é `assets/img/capa_jolie.png` (com selo). O original está em
`assets/img/capa_jolie_original.png`. Para regenerar o selo:

```bash
pip install Pillow
python3 tools/make_cover_badge.py assets/img/capa_jolie.png assets/img/capa_jolie_original.png
```

### Atualizar a data "última atualização" mostrada sob a capa

O texto fica em **`tools/src/index.html`** (procure `class="cover-note"`).
Edite a data e rode `python3 tools/build.py`. (Ou edite direto a `<p class="cover-note">`
em `index.html`, ciente de que um rebuild a sobrescreve a partir de `tools/src/`.)

### Publicar mudanças

```bash
git add -A && git commit -m "..." && git push origin main
```
O Pages redeploya sozinho em ~1 min. (Dê hard-refresh; imagens ficam em cache.)

## Decisões (o "porquê")

- **Conteúdo lido do repo, não da web.** `anovabr.github.io` responde **403** a
  fetchers; o HTML renderizado foi obtido clonando `anovabr/mqt_clone` e lendo
  `docs/`. Maior fidelidade que reconverter de Markdown.
- **Nomes de arquivo acentuados** (`correlação.html` etc.) foram **mantidos**
  para preservar navegação e âncoras exatamente como na origem. O Pages serve
  UTF-8 sem problema.
- **Pages por branch, sem workflow em `.github/`.** Tentamos um workflow com
  `actions/configure-pages` (`enablement: true`), mas o token do Actions é
  barrado pela política da org (`Resource not accessible by integration`) para
  *criar* o site Pages. Como é um site estático puro, “Deploy from a branch”
  (`main`/root) é mais simples e confiável. **Não recrie** um workflow de deploy
  a menos que o dono da org habilite a permissão; ele ficaria vermelho à toa.
- **Camada de anotações separada do texto** para o autor comentar sem editar o
  livro e sem reprocessar nada.
- **Capa com selo "Versão do autor"** substitui a capa exibida e a imagem de
  preview social (OG/Twitter); a original é preservada.

## Convenções ao editar

- CSS: um arquivo só (`assets/css/style.css`); use as variáveis de tema
  (`--bg`, `--text`, `--accent`, …) e estilize **os dois** temas.
- JS: vanilla, sem dependências novas; funções pequenas, seletores `$`/`$$`.
- Cuidado com **overflow horizontal no mobile** (já houve bug com token longo em
  `<code>`; corrigido com `overflow-wrap`). Teste em ~360px.
- Ao concluir uma mudança estrutural, **atualize este CLAUDE.md** e o
  `BUILD_REPORT.md`, rode `tools/verify.py`, e faça commit + push para `main`.

## Estado atual (atualize conforme evoluir)

- 20 capítulos, 261 imagens + 206 figuras, matemática (KaTeX) e código R
  (highlight.js). Verificação estrutural: 20/20, 0 falhas.
- Capa oficial com selo "Versão do autor" + legenda datada sob a capa na home.
- Próximos passos ficam com o mantenedor (Luis) no VS Code.
