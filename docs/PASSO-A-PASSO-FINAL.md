# Passo a passo para finalizar o LogiTrack Operations 360

Estado: **todos os 18 módulos (A–R) construídos e deployados**. 36 commits.
O que falta é **ação sua** — nada mais de desenvolvimento.

Ordem recomendada: Etapa 1 → 2 (essenciais) → 3 → 4 (polimento antes do vídeo) → 5 → 6.

---

## ETAPA 1 — Decidir sobre o seu e-mail no repositório (2 min)

`ciderblockafram@gmail.com` aparece em ~20 arquivos de metadata (aprovadores dos
processos de aprovação, `owner`/`runningUser` dos dashboards, `contactEmail`,
regras de atribuição). É o seu e-mail, num repo que será **público**.

- **Opção A (recomendada):** deixar como está. É comum em portfólios Salesforce e
  não é um segredo. Vá direto para a Etapa 2.
- **Opção B (scrub):** me peça para trocar por um placeholder
  (`admin@logitrack360.demo`) antes do push. Aviso: os processos de aprovação e
  dashboards deixam de bater com o usuário real da org até você reapontar no Setup.

**Verificação de segurança (já OK):** `server.key` e `server.crt` estão no
`.gitignore` e **não** estão versionados — confirmado.

---

## ETAPA 2 — Publicar no GitHub (15 min) — ESSENCIAL

### 2a. Instalar o GitHub CLI (uma vez)
No PowerShell:
```
winget install --id GitHub.cli
```
Feche e reabra o terminal. Depois:
```
gh auth login
```
(escolha GitHub.com → HTTPS → autenticar pelo navegador)

### 2b. Criar o repositório e subir o código
Na pasta do projeto (`C:\Users\Robert Luis\Desktop\LogiTrack-SFDX`):
```
gh repo create logitrack-operations-360 --public --source=. --remote=origin --push --description "Ambiente Salesforce completo para transportadora de ultima milha - projeto de portfolio, 100% declarativo"
```

### Alternativa sem instalar o gh
1. Crie um repositório **vazio** em https://github.com/new
   (nome: `logitrack-operations-360`, público, **sem** README/gitignore/license).
2. No terminal do projeto:
```
git remote add origin https://github.com/SEU_USUARIO/logitrack-operations-360.git
git push -u origin main
```
(o Git vai pedir login do GitHub na primeira vez)

### 2c. Conferir no GitHub
- O `README.md` aparece formatado na home do repo.
- A pasta `docs/` tem os 6 documentos.
- **NÃO** deve haver `server.key` nem `server.crt` na lista de arquivos.
- Anote a URL do repo — você vai usar no vídeo e no LinkedIn.

---

## ETAPA 3 — Polimento no Setup (~40 min) — antes de gravar o vídeo

São coisas que a Metadata API não deixa versionar. Faça logado como **admin**.

### 3a. Business Hours + feriados (10 min)
Setup → **Business Hours**:
- Editar "Default" → Nome: `LogiTrack - Horario Comercial`, Time Zone:
  `(GMT-03:00) Horario de Brasilia (America/Sao_Paulo)`, marcar "Active".
- Horários: Seg–Sex `08:00–18:00`, Sáb `08:00–12:00`, Dom fechado.

Setup → **Holidays** (os 12 feriados de 2026 já estão criados via Apex):
- Abrir cada feriado → botão "Add/Remove" → associar ao business hours `LogiTrack - Horario Comercial`.
  (ou deixar org-wide, que já vale para todos)

### 3b. Cards de list view e gráficos nas Home pages (15 min)
As 6 Home pages existem e já estão atribuídas aos apps. Falta enriquecer no
**Lightning App Builder** (Setup → Lightning App Builder → editar cada `LogiTrack_* Home`):
- Adicionar componente **"Lista"** para as filas da área (ver a tabela no
  `PENDENCIAS-MANUAIS.md` seção 1 — quais list views por app).
- Adicionar componente **"Gráfico de Relatório"** apontando para os relatórios da
  pasta *LogiTrack - Relatorios*.
- Salvar e **Ativar**.

> Por que manual: `filterListCard` e `reportChart` não passam no deploy de metadata
> nesta org (bug conhecido — testado à exaustão).

### 3c. Ação "Consultar CEP" numa record page (2 min)
Lightning App Builder → record page **Remessa** (`LT_Shipment_Record_Page`):
- Na seção "Salesforce Mobile e Lightning Experience Actions" (ou no Highlights
  Panel), adicionar a ação **`Consultar CEP`**. Salvar/Ativar.

### 3d. (Opcional) Status de Case em português (10 min)
Setup → Picklist Value Sets → **Case Status**:
- Adicionar: Novo, Em Andamento, Aguardando Cliente, Escalado, Resolvido, Fechado.
- Setup → Object Manager → Case → Support Processes → `LT SAC Process` → reordenar.
> Não dá para fazer por metadata (quebra o Business Process). Detalhe em `PENDENCIAS-MANUAIS.md` seção 3.

### 3e. Confirmar agendamento dos flows (3 min)
Setup → Flows → abrir cada flow **Scheduled** (`LT_Driver_CNH_Expiry_Alert`,
`LT_Case_PNR_Aging`, `LT_Incident_Escalate_Aging`, `LT_Shipment_Detect_No_Movement`,
`LT_Shipment_Detect_Retained`) → confirmar frequência diária e horário. Se não
mostrar agendamento, editar e salvar uma vez.

---

## ETAPA 4 — Limpeza final do metadata (10 min) — opcional, recomendado

Sobrou pouca coisa do Trailhead no source local (inofensivo, mas feio num portfólio):
`globalValueSets/Flavors`, `objects/Product2/fields/Macaron_Flavor__c` e `Shirt__c`,
mais referências em `settings/Search.settings`.

Me peça: **"limpe o metadata Trailhead residual"** — eu removo os arquivos, faço
um deploy destrutivo do que estiver na org, e commito. É rápido.

---

## ETAPA 5 — Gravar o vídeo de demonstração (seu ritmo)

- Roteiro pronto em **`docs/ROTEIRO-VIDEO.md`** (~7 min, cena a cena).
- Grave numa org **com os dados carregados** (senão os dashboards ficam vazios).
- Use o usuário **admin**, mas mostre 1x o login como usuário de área (ex.: Ana /
  Comercial) para provar o modelo de permissão.
- Sugestão: legendas em pt-BR; se for postar para público internacional, narração
  em inglês.
- Suba no YouTube (não listado ou público) e anote a URL.

---

## ETAPA 6 — Postar no LinkedIn

- Textos prontos em **`docs/LINKEDIN.md`** (3 versões: curta, longa, linha de perfil).
- Substituir `[GITHUB_URL]` e `[VIDEO_URL]` pelas URLs reais.
- Anexar um carrossel (3–5 imagens: App Launcher, um dashboard, uma record page,
  o processo de aprovação, o diagrama de objetos) ou o vídeo.
- Postar. Atualizar a seção "Sobre" do perfil com a linha curta.

---

## Resumo do que é ESSENCIAL vs POLIMENTO

| | Etapas |
|---|---|
| **Essencial p/ "publicado"** | 1, 2, 5, 6 |
| **Polimento (deixa o vídeo melhor)** | 3, 4 |

Se quiser o mínimo: Etapa 1 → 2 → 5 → 6. O projeto já está completo e funcional.
