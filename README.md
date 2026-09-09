# LogiTrack Operations 360

**Ambiente Salesforce completo para uma transportadora de última milha (last‑mile),
construído do zero como projeto de portfólio de administração Salesforce.**

O projeto modela a operação de uma transportadora fictícia — **LogiTrack Brasil** —
inspirada no dia a dia de um carrier de encomendas: bases de entrega e franquias,
embarcadores (e‑commerces e marketplaces), motoristas terceirizados, coletas,
romaneios, rotas, rastreamento de remessas, ocorrências operacionais, SAC, prevenção
de perdas (extravios / PNR) e o financeiro de contas a pagar.

Tudo foi entregue via **Salesforce DX / Metadata API** (source‑tracked), com os
dados fictícios carregados por **Bulk API 2.0**. Nenhum código Apex de produção —
o objetivo é demonstrar **configuração declarativa (clicks, not code)** no nível de
um administrador que concluiu as trilhas *Administrador Básico* e *Administrador
Intermediário* do Trailhead.

> ⚠️ Empresa, marcas, nomes de pessoas, embarcadores, motoristas, CNPJs, valores e
> endereços são **fictícios**. As 167 bases/cidades são reais apenas como referência
> geográfica do Sul do Brasil.

---

## Números do projeto

| | |
|---|---:|
| Objetos personalizados | 19 (+ `Operational_Indicator__c`) |
| Campos personalizados | ~507 |
| Record Types | 14 |
| Regras de validação | 110 |
| Flows | 19 (8 before‑save, 5 after‑save, 5 agendados, 1 tela) |
| Processos de aprovação | 2 (ressarcimento de extravio; pagamento por alçada) |
| Permission Sets / Permission Set Groups | 10 / 6 |
| Lightning Apps | 6 |
| Filas (Queues) | 5 |
| Relatórios / Dashboards | 18 / 9 |
| Registros de dados fictícios | ~4.500 |
| Commits | 27 (um bloco por módulo) |

---

## Áreas funcionais (os 6 apps Lightning)

### 1. LogiTrack Operations 360 — núcleo operacional
- **`LT_Logistics_Unit__c`** — Regional → Centro de Distribuição (SC) → Base de
  Entrega (própria / franqueada / parceira credenciada). 166 bases carregadas de um
  arquivo real de bases e cidades, re‑parenteadas sob o CD do seu estado.
- **`LT_Shipment__c` + `LT_Tracking_Event__c`** — remessa e sua linha do tempo de
  rastreamento (19 tipos de evento). Flows mapeiam evento → status da remessa e
  detectam remessas **retidas** e **sem movimentação +10 dias** (candidatas a extravio).
- **`LT_Pickup_Request__c` + `LT_Manifest__c` + `LT_Manifest_Line__c`** — coletas
  (seller / drop‑off / C2C), romaneios de pagamento a motorista com regras de
  elegibilidade (motorista pago *por romaneio*, MR exige destino + distância > 60 km).
- **`LT_Route__c` + `LT_Delivery_Attempt__c`** — rotas de entrega, carga vs. planejado
  vs. teto da categoria do motorista, tentativas com geolocalização e comprovação.
  Inclui um **Screen Flow** de baixa de tentativa (telas de resultado + prova).
- **`LT_Operational_Incident__c`** — ocorrências operacionais (retidos, sem
  movimentação) com SLA por prioridade, *aging bucket* e escalonamento agendado.
- **`Operational_Indicator__c`** — indicadores diários por unidade (pedidos,
  entregues, SLA, % de entregas) e a classificação de status operacional por SLA.

### 2. LogiTrack Comercial
- **`Account`** (Record Types Embarcador / Parceiro Operacional) + **`LT_Commercial_Agreement__c`**
  (contrato comercial) + **`LT_Monthly_Billing__c`** (faturamento mensal, Master‑Detail
  de Account, com roll‑ups). Chave única embarcador‑mês via Flow.
- **`Opportunity`** — processo de negócio de *Prospecção de Embarcador* (9 etapas)
  com Path.

### 3. LogiTrack Cadastro
- **`LT_Driver__c`** — motorista com 5 Record Types (TAC / MEI / ETC / Coleta / MR),
  campos derivados por RT (sigla, modelo de pagamento, mín/máx de pacotes por viagem,
  exigência de veículo, situação da CNH). Flow agendado de alerta de CNH a vencer.
- **`LT_Vehicle__c` + `LT_Driver_Document__c`** — veículos (placa Mercosul/antiga via
  regra de validação REGEX, CRLV, capacidade) e documentos do motorista.

### 4. LogiTrack SAC
- **`Case`** — 5 Record Types (Assinado Não Recebido, Agilização, Avaria Pós‑Entrega,
  Postura do Motorista, PNR) + Support Process, 5 filas e **regra de atribuição**
  que roteia por Record Type. Flows de SLA e *aging* de PNR.

### 5. Prevenção de Perdas (dentro do SAC / Operações)
- **`LT_Loss_Claim__c`** — extravio: apuração de motivo e responsabilidade, valor
  declarado, ressarcimento ao embarcador, valor a descontar do motorista, chave
  única por remessa.
- **`LT_Driver_Penalty__c`** — penalização do motorista com fluxo de contestação
  (fórmula *valor efetivo*: Cancelada = 0, Reduzida = 50 %).
- **Processo de aprovação** de ressarcimento acima de R$ 300 + **Flow** que cria a
  penalização automaticamente quando o extravio é aprovado com culpa do motorista.

### 6. LogiTrack Financeiro
- **`LT_Payment_Request__c`** — solicitação de pagamento (ressarcimento a embarcador,
  romaneio de motorista, folha, insumos, verba de viagem, abertura de galpão,
  fornecedor, reembolso) com fórmula de **alçada** (Coordenação / Gerência / Diretoria
  conforme o valor).
- **`LT_Payment__c`** (Master‑Detail, pagamentos e conciliação bancária) e
  **`LT_Expense__c`** (despesas por centro de custo e mês de competência).
- **Processo de aprovação multinível**: Coordenação sempre, Gerência acima de
  R$ 2.000, Diretoria acima de R$ 10.000. Flow marca a solicitação como *Paga*
  quando os pagamentos confirmados cobrem o valor.

### LogiTrack Executivo
App consolidado (somente leitura) com os indicadores, o **Painel Executivo** e o
**Dashboard Executivo — Sul** (5 metric cards: Total de Pedidos, Entregues,
Não Entregues, % de Entregas, SLA Médio).

---

## Recursos de administração demonstrados

`Objetos e campos` (todos os tipos, incl. Fórmula, Roll‑Up Summary, Geolocalização,
AutoNumber, External Id) · `Record Types + Business Processes` · `Regras de validação`
· `Page Layouts` e `Compact Layouts` · `Path` (11) · `List Views` compartilhadas ·
`Flows` record‑triggered / agendados / de tela / autolaunched · `Processos de aprovação`
com *field updates* de workflow · `Filas` e `regras de atribuição` · `Global Value Sets`
· `Lightning Apps`, `abas`, `home pages` e `utility bars` · `Relatórios` com gráfico e
`Dashboards` de grade · `Hierarquia de papéis` (17 papéis) · `Permission Sets` e
`Permission Set Groups` (projeto *permission‑set‑led* — perfis ficam no `.forceignore`)
· `Data Loader` / Bulk API 2.0 para carga de dados.

---

## Estrutura do repositório

```
force-app/main/default/     Metadados (fonte da verdade)
  objects/                  19 objetos LT + Account/Case/Contact/Opportunity estendidos
  flows/  approvalProcesses/  workflows/  permissionsets/  permissionsetgroups/
  applications/  flexipages/  tabs/  layouts/  pathAssistants/  quickActions/
  reports/LT_Reports/       18 relatórios
  dashboards/LT_Operational_Dashboards/   9 dashboards
  roles/  queues/  globalValueSets/  standardValueSets/
scripts/data-load/          Geradores Python (metadados + dados) + metahelp.py
data/                       CSVs dos dados fictícios, por área
docs/                       PENDENCIAS-MANUAIS.md, ROTEIRO-VIDEO.md, LINKEDIN.md
```

Os metadados foram gerados por **scripts Python** (`scripts/data-load/`) que escrevem
o XML a partir de um módulo auxiliar compartilhado (`metahelp.py`) — abordagem
"infra‑as‑code" para manter 500+ campos e 110 regras consistentes.

---

## Como explorar

```bash
git clone https://github.com/robertluiscp/logitrack-operations-360.git
```

1. Autentique a org (JWT Bearer Flow — ver `docs` interno; a chave `server.key`
   **não** vai para o Git).
2. `sf project deploy start -d force-app` para uma org limpa (Developer Edition).
3. Carregue os dados: veja a ordem em `scripts/data-load/` (bases → comercial →
   motoristas → remessas → coletas → rotas → ocorrências → SAC → extravios →
   financeiro).
4. Atribua um Permission Set Group (`LT_PSG_Operacao`, `_Comercial`, `_Cadastro`,
   `_SAC`, `_Financeiro` ou `_Gestao`) e abra o app correspondente.

### Usuários de teste

| Usuário | Área | Permission Set Group |
|---|---|---|
| Robert Luis Costa Pestana (admin) | Gestão / Diretoria | `LT_PSG_Gestao` |
| Ana Beatriz Correia | Comercial | `LT_PSG_Comercial` |
| Rafael Nunes | Operação | `LT_PSG_Operacao` |
| Maria Thompson | Cadastro / Frota | `LT_PSG_Cadastro` |
| Bruno Tavares | Financeiro | `LT_PSG_Financeiro` |

_(SAC não tem usuário de teste dedicado por limite de licença Salesforce na
Developer Edition — ver `docs/PENDENCIAS-MANUAIS.md`.)_

---

## Limitações conhecidas

Alguns itens não passam pela Metadata API nesta org e ficam para configuração
manual no Setup / Lightning App Builder — todos listados em
[`docs/PENDENCIAS-MANUAIS.md`](docs/PENDENCIAS-MANUAIS.md): cards de list view e
gráficos de relatório nas home pages, Lightning Record Pages dos objetos novos,
status de Case em português, e a higienização final de metadados *stale* herdados
da org de origem.

---

## Licença

Projeto de portfólio, sem fins comerciais. Sinta‑se à vontade para se inspirar na
modelagem. As trilhas de referência são da Salesforce (Trailhead).
