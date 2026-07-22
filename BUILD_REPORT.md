# BUILD_REPORT.md

Relatório de construção do site estático do ebook **“Conceitos e análises
estatísticas com R e JASP”**, com camada de anotações do autor
**Luis Anunciação (PUC-Rio)**.

- **Data do build:** 2026-07-22
- **Fonte:** conteúdo do livro em bookdown de <https://anovabr.github.io/mqt_clone/>
  (importado do repositório [`anovabr/mqt_clone`](https://github.com/anovabr/mqt_clone),
  pasta `docs/` renderizada).
- **Resultado:** 20/20 capítulos gerados e verificados. **0 falhas.**

---

## 1. Como o conteúdo foi obtido

O GitHub Pages de origem (`anovabr.github.io`) respondeu **HTTP 403** tanto para
`curl` (política de egresso do ambiente) quanto para o buscador de páginas, então
o conteúdo **não pôde ser baixado pela web**. Em vez de abortar, o repositório de
origem foi adicionado à sessão e clonado, e o HTML **já renderizado** foi lido da
pasta `docs/` — resultando em **fidelidade total** (títulos, parágrafos, código,
tabelas, imagens, matemática LaTeX e referências preservados exatamente), melhor
do que uma reconversão a partir de Markdown.

Para cada página, apenas o HTML real do capítulo foi extraído (o
`<section class="normal">` → `div.section.level1`), descartando toda a “moldura”
do gitbook (sumário lateral, cabeçalho, navegação, scripts). Foram preservados os
**números de capítulo** e as **âncoras de seção exatamente como na origem**.

## 2. O que foi construído

### Páginas (uma por capítulo, na raiz do repositório)

| # | Arquivo | Título | Seções | `<img>` | Blocos R |
|--:|---------|--------|:------:|:-------:|:--------:|
| 1 | `index.html` | Prefácio | 15 | 4 | 0 |
| 2 | `programas-estatísticos.html` | Programas estatísticos | 6 | 13 | 0 |
| 3 | `aspectos-gerais.html` | Aspectos gerais | 21 | 20 | 0 |
| 4 | `estatística-descritiva.html` | Estatística Descritiva | 28 | 45 | 21 |
| 5 | `família-de-distribuições.html` | Família de distribuições | 8 | 10 | 3 |
| 6 | `tipos-de-amostragem.html` | Tipos de amostragem | 13 | 8 | 0 |
| 7 | `estatística-inferencial.html` | Estatística Inferencial | 10 | 5 | 0 |
| 8 | `um-exemplo-real-de-pesquisa.html` | Um exemplo real de pesquisa | 8 | 5 | 0 |
| 9 | `qui-quadrado.html` | Qui quadrado | 8 | 14 | 4 |
| 10 | `fatores-de-risco.html` | Fatores de Risco | 8 | 17 | 6 |
| 11 | `teste-t.html` | Teste T | 17 | 18 | 20 |
| 12 | `anova.html` | ANOVA | 31 | 67 | 44 |
| 13 | `anova-de-medidas-repetidas.html` | ANOVA de medidas repetidas | 7 | 22 | 12 |
| 14 | `modelo-linear-misto.html` | Modelo linear misto | 6 | 17 | 8 |
| 15 | `correlação.html` | Correlação | 7 | 11 | 3 |
| 16 | `regressão-linear-simples.html` | Regressão linear simples | 8 | 33 | 11 |
| 17 | `regressão-linear-múltipla.html` | Regressão linear múltipla | 8 | 20 | 12 |
| 18 | `regressão-logística-binária.html` | Regressão logística binária | 8 | 18 | 8 |
| 19 | `quarta-capa.html` | Quarta capa | 0 | 0 | 0 |
| 20 | `referencias.html` | Referencias | 0 | 0 | 0 |

Totais: **347 referências de imagem**, **152 blocos de código R** com classe
`language-r` para realce. (Cap. 19 e 20 não têm subseções nem código, como no
original.)

### Recursos (assets)

- `assets/img/` — **261** imagens do livro (`/img` da origem), 35 MB.
- `assets/figure-html/` — **206** figuras geradas pelo R (`gitbook-demo_files/figure-html`), 5,1 MB.
- `assets/css/style.css` — todo o estilo (mobile-first, claro/escuro).
- `assets/js/app.js` — todo o comportamento (vanilla JS, sem dependências).
- `assets/img/favicon.svg` — favicon.

Todos os caminhos de asset e de navegação são **relativos e nunca começam com
`/`** — o site funciona em um subcaminho do GitHub Pages
(`https://usuario.github.io/mqt-ebook/`). Verificado: **324/324** assets
referenciados retornam HTTP 200; **0** caminhos absolutos; **0** vazamentos da
moldura do bookdown.

### Camada do autor (editável, sem tocar no texto do livro)

- `content/<capítulo>.html` — texto limpo do livro (fonte da verdade).
- `content/toc.json` — estrutura do livro (capítulos + âncoras).
- `content/annotations.json` — **camada do autor**, injetada em tempo de execução:
  destaques **“Nota do autor”**, **comentários laterais** e um **espaço por
  capítulo** para exemplos trabalhados (código + saída + interpretação), com
  metadados de autor **Luis Anunciação (PUC-Rio)**. Exemplos já preenchidos em
  `teste-t` e `correlação`.

### Recursos de UX implementados

Barra lateral persistente com árvore completa e recolhimento; **scrollspy**
(destaque da seção ativa); coluna de leitura serifada (~720px, entrelinha
generosa); **tema claro/escuro** (respeita `prefers-color-scheme`, persistido);
**ajuste de fonte** persistido; navegação anterior/próximo; **barra de progresso**;
**barra de ação flutuante** ciente de rolagem (topo, tema, fonte, compartilhar);
**Web Share API** com alternativa desktop (copiar link + WhatsApp, X/Twitter,
LinkedIn, e-mail) em 3 níveis (livro, capítulo, seção); âncoras de seção que
copiam deep link; **KaTeX** (matemática) e **highlight.js** (código) via CDN;
Open Graph + Twitter Card por capítulo; `prefers-reduced-motion`; rolagem suave.
Mobile: gaveta off-canvas com hambúrguer, alvos ≥44px, sem rolagem horizontal,
código com rolagem interna, tabelas responsivas.

## 3. Falhas e itens não totalmente verificáveis

### Falhas: nenhuma

- **Nenhuma página falhou.** Todos os 20 capítulos foram extraídos e gerados.
- **Nenhuma imagem faltando.** 3 imagens eram referenciadas com extensão `.PNG`
  (maiúsculas) enquanto o arquivo em disco é `.png` — isso quebraria no GitHub
  Pages (Linux, sensível a maiúsculas/minúsculas). O build **corrigiu
  automaticamente** o caso para o nome real do arquivo:
  `cap_anovarm_pressupostos`, `cap_reg_x_y2`, `cap_reg_x_y_SSE`.

### Não verificável neste ambiente (por design)

- **Renderização ao vivo de KaTeX e highlight.js:** os CDNs
  (`cdn.jsdelivr.net`) estão **bloqueados pela política de egresso** deste
  ambiente de build (retornam 000). Portanto a renderização de matemática/código
  **não pôde ser executada aqui**. Foi verificado que a **marcação de origem
  está presente** (spans `math inline`/`math display` com `\(…\)` e `\[…\]`;
  `<pre><code class="language-r">`) e que os **scripts de CDN e a inicialização
  estão corretamente ligados**. Renderizarão normalmente quando o site for
  servido publicamente (GitHub Pages tem acesso aberto à internet).
  - Observação: os delimitadores `$…$` foram **desativados** de propósito no
    KaTeX, pois este é um texto em português onde `R$` (moeda) seria
    interpretado como matemática.
- **Folha de compartilhamento nativa e gestos de toque:** não podem ser
  disparados em execução headless. Conforme solicitado, verificou-se a
  **presença e a ligação dos elementos e da alternativa** (não o comportamento
  ao vivo): o menu de fallback abre, com os 4 destinos (WhatsApp, X/Twitter,
  LinkedIn, e-mail) + copiar link e alternância de escopo livro/capítulo.

### Verificação estrutural executada (servidor local + navegador headless)

- `tools/verify.py`: 20/20 capítulos OK; 324/324 assets 200; todos os links
  internos válidos; 0 caminhos absolutos; 0 vazamentos de moldura;
  `annotations.json` carrega.
- Navegador headless (Chromium): em todos os 20 capítulos, **imagens carregam**
  (0 quebradas), marcação de matemática/código presente, **0 erros de JS**.
  Em capítulos representativos confirmou-se ao vivo: injeção das anotações do
  autor, âncoras de seção, alternância e **persistência** de tema, alteração e
  **persistência** de fonte, barra flutuante oculta no topo e revelada ao rolar,
  barra de progresso, menu de compartilhamento (fallback) com todos os destinos
  e escopos, scrollspy destacando a seção ativa, gaveta abrindo no hambúrguer e
  **ausência de rolagem horizontal** em 360px.

## 4. Estrutura de pastas

```
mqt-ebook/
├── index.html                       # Cap. 1 (Prefácio) — página inicial
├── programas-estatísticos.html      # Cap. 2
│   … (uma página .html por capítulo, Caps. 1–20) …
├── referencias.html                 # Cap. 20
├── assets/
│   ├── css/style.css
│   ├── js/app.js
│   ├── img/                         # 261 imagens do livro + favicon.svg
│   └── figure-html/                 # 206 figuras geradas pelo R
├── content/
│   ├── index.html … referencias.html  # texto limpo do livro (fonte da verdade)
│   ├── toc.json                     # estrutura do livro (capítulos + âncoras)
│   └── annotations.json             # ← CAMADA DO AUTOR (editável)
├── tools/
│   ├── build.py                     # gerador das páginas
│   ├── verify.py                    # verificação estrutural
│   ├── build_data.json              # manifesto do último build
│   └── src/                         # HTML bookdown original (entrada do build)
├── README.md
├── BUILD_REPORT.md                  # este arquivo
├── publish.sh                       # publicação em 1 passo
├── .gitignore
└── .nojekyll                        # impede o Jekyll de interferir nos assets
```

Tamanho total (sem `.git`): ~45 MB (dominado pelas imagens).

## 5. Servir localmente (comando exato)

```bash
cd mqt-ebook
python3 -m http.server 8971
```

Abra <http://localhost:8971/index.html>. (Sirva por HTTP; abrir via `file://`
impede o carregamento de `content/annotations.json`.)

## 6. Publicação

O site foi publicado no repositório existente
[`anovabr/mqt-ebook`](https://github.com/anovabr/mqt-ebook): o conteúdo está no
branch `main` (raiz) e o **GitHub Pages** foi habilitado servindo dessa raiz.

**URL do site:**

```
https://anovabr.github.io/mqt-ebook/
```

A primeira publicação do Pages pode levar 1–2 minutos após habilitado.

### Publicar em outra conta (opcional)

Para publicar em outra conta/repositório, `publish.sh` faz tudo em um passo:
roda `gh auth status` (para com mensagem clara se não autenticado), ajusta as
URLs canônicas/OG para o usuário detectado, cria um repositório **PÚBLICO**
`mqt-ebook` e habilita o GitHub Pages a partir da raiz.
