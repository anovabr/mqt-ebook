#!/usr/bin/env bash
#
# publish.sh — cria um repositório público no GitHub e habilita o GitHub Pages
# para este site estático, em um único passo.
#
#   bash publish.sh
#
# Requer o GitHub CLI (`gh`) autenticado. Nada é enviado se você não estiver
# autenticado. É seguro rodar de novo: se o repositório já existir, o script
# avisa e para sem sobrescrever nada.
set -euo pipefail

REPO_NAME="mqt-ebook"
PAGES_PATH="/"   # servir a partir da raiz do repositório

say()  { printf '\033[1;34m==>\033[0m %s\n' "$*"; }
err()  { printf '\033[1;31mErro:\033[0m %s\n' "$*" >&2; }

# --- 1) pré-requisitos -------------------------------------------------------
if ! command -v gh >/dev/null 2>&1; then
  err "GitHub CLI (gh) não encontrado. Instale em https://cli.github.com/ e rode novamente."
  exit 1
fi

say "Verificando autenticação do GitHub CLI (gh auth status)…"
if ! gh auth status >/dev/null 2>&1; then
  err "Você não está autenticado no GitHub CLI."
  err "Rode 'gh auth login' e execute 'bash publish.sh' novamente."
  exit 1
fi

OWNER="$(gh api user -q .login)"
if [ -z "${OWNER}" ]; then
  err "Não foi possível determinar seu usuário do GitHub."
  exit 1
fi
OWNER_LC="$(printf '%s' "${OWNER}" | tr '[:upper:]' '[:lower:]')"
PAGES_URL="https://${OWNER_LC}.github.io/${REPO_NAME}/"
say "Autenticado como '${OWNER}'. O site ficará em: ${PAGES_URL}"

# --- 2) garantir um commit e branch -----------------------------------------
if [ ! -d .git ]; then
  err "Este diretório não é um repositório git. Rode 'git init' primeiro."
  exit 1
fi
if [ -n "$(git status --porcelain)" ]; then
  say "Há mudanças não commitadas — commitando antes de publicar…"
  git add -A
  git commit -m "Publish: site estático do ebook" >/dev/null
fi
BRANCH="$(git rev-parse --abbrev-ref HEAD)"
say "Branch atual: ${BRANCH}"

# --- 3) corrigir as URLs canônicas/OG para o seu usuário ---------------------
# As páginas foram geradas com uma base de exemplo; aqui ajustamos para a sua.
CURRENT_BASE="$(grep -oE 'https://[a-zA-Z0-9._-]+\.github\.io/mqt-ebook' index.html | head -n1 || true)"
DESIRED_BASE="https://${OWNER_LC}.github.io/${REPO_NAME}"
if [ -n "${CURRENT_BASE}" ] && [ "${CURRENT_BASE}" != "${DESIRED_BASE}" ]; then
  say "Ajustando URLs canônicas/OG: ${CURRENT_BASE} -> ${DESIRED_BASE}"
  # macOS e Linux: sed -i com sufixo de backup vazio via arquivo temporário
  find . -maxdepth 1 -name '*.html' -type f -print0 | while IFS= read -r -d '' f; do
    tmp="$(mktemp)"
    sed "s#${CURRENT_BASE//./\\.}#${DESIRED_BASE}#g" "$f" > "$tmp" && mv "$tmp" "$f"
  done
  git add -A
  git commit -m "Set canonical/OG base URL to ${DESIRED_BASE}" >/dev/null || true
fi

# --- 4) criar o repositório e enviar -----------------------------------------
if gh repo view "${OWNER}/${REPO_NAME}" >/dev/null 2>&1; then
  err "O repositório '${OWNER}/${REPO_NAME}' já existe. Nada foi feito para não sobrescrevê-lo."
  err "Se quiser republicar, envie manualmente: git push -u origin ${BRANCH}"
  exit 1
fi

# Se já existir um remote 'origin' (ex.: este projeto foi preparado a partir de
# outro repositório), preserve-o como 'upstream' para liberar o nome 'origin'.
if git remote get-url origin >/dev/null 2>&1; then
  say "Remote 'origin' já existe — renomeando para 'upstream' para publicar sob seu usuário."
  git remote rename origin upstream 2>/dev/null || git remote remove origin
fi

say "Criando repositório PÚBLICO '${REPO_NAME}' e enviando o conteúdo…"
gh repo create "${REPO_NAME}" --public --source=. --remote=origin --push

# --- 5) habilitar o GitHub Pages (não-interativo) ----------------------------
say "Habilitando o GitHub Pages (branch '${BRANCH}', pasta '${PAGES_PATH}')…"
if gh api --method POST "repos/${OWNER}/${REPO_NAME}/pages" \
     -f "source[branch]=${BRANCH}" -f "source[path]=${PAGES_PATH}" >/dev/null 2>&1; then
  say "GitHub Pages habilitado."
else
  say "Não foi possível habilitar o Pages automaticamente (pode já estar habilitado"
  say "ou exigir permissão). Habilite manualmente em:"
  say "  Settings → Pages → Source: branch '${BRANCH}', pasta '/ (root)'."
fi

echo
say "Pronto! Seu site estará disponível em alguns instantes em:"
printf '    \033[1;32m%s\033[0m\n' "${PAGES_URL}"
say "A primeira publicação do Pages pode levar 1–2 minutos."
