# Passo a passo para publicar o LogiTrack Operations 360

Estado: **projeto 100% construído e validado**. Todos os 18 módulos (A–R) estão
deployados na org, o repositório local está limpo (só o que foi construído neste
projeto — a metadata padrão do Salesforce foi removida) e a última validação
contra a org passou com **0 erros**.

O que falta é **ação sua**: subir para o GitHub e postar no LinkedIn.
Opcionalmente, alguns ajustes de polimento no Setup.

---

## ETAPA 1 — Subir o código para o GitHub (5 min) — ESSENCIAL

O repositório remoto já existe: **https://github.com/robertluiscp/logitrack-operations-360**
(vazio). Falta ligar o repositório local a ele e dar `push`.

No terminal, dentro da pasta do projeto
(`C:\Users\Robert Luis\Desktop\LogiTrack-SFDX`):

```bash
git remote add origin https://github.com/robertluiscp/logitrack-operations-360.git
```

```bash
git branch -M main
```

```bash
git push -u origin main
```

Na primeira vez o Git pede login do GitHub — abre o navegador ou pede um token.
Se pedir token: GitHub → Settings → Developer settings → Personal access tokens →
Fine-grained → dar acesso de `Contents: Read and write` ao repositório.

### Conferir depois do push
- O `README.md` aparece formatado na home do repositório.
- A pasta `docs/` tem os documentos (showcase, LINKEDIN, auditoria, pendências…).
- **NÃO** pode haver `server.key` nem `server.crt` na lista de arquivos
  (estão no `.gitignore` — já conferido).
- `force-app/` tem ~820 arquivos (só componentes autorais), não milhares.

---

## ETAPA 2 — Postar no LinkedIn (15 min) — ESSENCIAL

Textos prontos em **`docs/LINKEDIN.md`** — três versões (curta para o feed, longa
para artigo/carrossel, e uma linha para a seção "Sobre" do perfil). O link do
GitHub já está preenchido nos três.

**Sugestão de carrossel (3–5 imagens):**
1. App Launcher mostrando os 6 apps LogiTrack.
2. Um dashboard operacional com dados.
3. Uma record page com Dynamic Forms (ex.: Remessa).
4. O processo de aprovação de pagamento (alçada multinível).
5. O diagrama de objetos da página-vitrine (`docs/showcase.html`).

Ou anexe o PDF `docs/LogiTrack-Operations-360.pdf` diretamente ao post.

Depois de postar, atualize a seção **"Sobre"** do perfil com a linha curta.

---

## ETAPA 3 — Página-vitrine para quem não tem Salesforce (pronta)

Para recrutadores sem conta Salesforce, há duas peças já prontas em `docs/`:

- **`showcase.html`** — página interativa de uma tela (tema claro/escuro,
  diagrama de objetos, matriz de competências Trailhead). Abre em qualquer
  navegador. Também publicada como link privado do Claude.
- **`LogiTrack-Operations-360.pdf`** — a mesma vitrine em PDF A4 (5 páginas),
  para anexar em e-mail ou candidatura. Cópia também na sua Área de Trabalho.

Nenhuma das duas exige login. O GitHub cobre quem quer ver o metadata; a vitrine
cobre quem quer entender o projeto em 3 minutos.

---

## ETAPA 4 — Polimento no Setup (~40 min) — OPCIONAL

Coisas que a Metadata API não deixa versionar. Faça logado como **admin**.
Nenhuma é bloqueante — o projeto já está completo e funcional sem elas.

### 4a. Business Hours + feriados (10 min)
Setup → **Business Hours** → editar "Default":
- Nome: `LogiTrack - Horario Comercial`; Time Zone: `America/Sao_Paulo`; "Active".
- Seg–Sex `08:00–18:00`, Sáb `08:00–12:00`, Dom fechado.

Os 12 feriados de 2026 já estão criados (via Apex). Se quiser, associe cada um ao
business hours acima em Setup → **Holidays**.

### 4b. Cards de lista e gráficos nas Home pages (15 min)
As 6 Home pages existem e estão atribuídas aos apps. Falta enriquecer no
**Lightning App Builder** (editar cada `LogiTrack_* Home`):
- Componente **"Lista"** para as filas da área (tabela em
  `PENDENCIAS-MANUAIS.md` seção 1).
- Componente **"Gráfico de Relatório"** apontando para a pasta
  *LogiTrack - Relatorios*.
- Salvar e **Ativar**.

> Por que manual: `filterListCard` e `reportChart` não passam no deploy de
> metadata nesta org (bug conhecido, testado à exaustão).

### 4c. Ação "Consultar CEP" numa record page (2 min)
Lightning App Builder → record page **Remessa** (`LT_Shipment_Record_Page`) →
adicionar a ação **`Consultar CEP`** no Highlights Panel → Salvar/Ativar.

### 4d. (Opcional) Status de Case em português (10 min)
Setup → Picklist Value Sets → **Case Status** → adicionar: Novo, Em Andamento,
Aguardando Cliente, Escalado, Resolvido, Fechado. Depois reordenar o support
process `LT SAC Process`. Detalhe em `PENDENCIAS-MANUAIS.md` seção 3.

### 4e. Confirmar agendamento dos flows (3 min)
Setup → Flows → abrir cada flow **Scheduled** (`LT_Driver_CNH_Expiry_Alert`,
`LT_Case_PNR_Aging`, `LT_Incident_Escalate_Aging`, `LT_Shipment_Detect_No_Movement`,
`LT_Shipment_Detect_Retained`) → confirmar frequência diária. Se não mostrar
agendamento, editar e salvar uma vez.

---

## Resumo

| | Etapas |
|---|---|
| **Essencial p/ "publicado"** | 1, 2 |
| **Já pronto, só usar** | 3 |
| **Polimento (opcional)** | 4 |

O mínimo é a Etapa 1 seguida da Etapa 2. O projeto já está completo, validado e
com a vitrine pronta.
