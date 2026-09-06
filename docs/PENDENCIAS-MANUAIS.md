# LogiTrack Operations 360 — Pendências para finalização manual

Este documento lista o que **não pôde ser entregue via Metadata API** (limitações
conhecidas do Salesforce) ou foi **deliberadamente adiado**, para conclusão manual
no Setup / Lightning App Builder. Nada aqui bloqueia o uso do projeto — são
polimentos e itens de configuração de ambiente.

Última atualização: 2026-09-06 (após Módulo L).

---

## 1. Home pages — cards de list view e gráficos de relatório

**Status:** as 6 Home pages existem e já estão atribuídas aos apps
(`LogiTrack_*_Home`, via `actionOverrides` no CustomApplication). Elas trazem
rich text com links diretos para as list views + Assistente, Itens Recentes,
Tarefas e Eventos de Hoje.

**O que falta (fazer no Lightning App Builder, editando cada Home page):**
- Adicionar componentes **"Lista"** (list view) para as filas de cada área.
  Os componentes `flexipage:filterListCard` **não passam no deploy de metadata**
  desta org (`Error retrieving filter [obj.view] for entity`), mesmo com a list
  view existindo e compartilhada — por isso ficaram de fora.
- Adicionar componentes **"Gráfico de Relatório"** apontando para os relatórios
  da pasta *LogiTrack - Relatórios* (Módulo L). O `flexipage:reportChart` também
  não resolve relatórios de metadata no deploy (`no reports found`).

Sugestão de cards por Home page:

| Home page | List views | Gráficos de relatório |
|---|---|---|
| Operations 360 | Remessas: Retidas e Paradas / Atrasadas · Ocorrências: Fora do Prazo / Candidatas Extravio · Rotas: Em Rota · Romaneios: A Pagar | LT_Op_Shipments_By_Status · LT_Op_Incidents_By_Type |
| Comercial | Contratos: Vigentes · Faturamento: Em Aberto | LT_Com_Agreements_By_Status |
| Cadastro | Motoristas: CNH Pendente / Ativos · Veículos: All | LT_Cad_Drivers_By_Category |
| SAC | Casos: Meus Casos Abertos · Extravios: Em Apuração / Ressarcidos | LT_Loss_By_Responsibility |
| Financeiro | Solicitações: Em Aprovação / A Pagar / Vencidas · Despesas: Previstas · Pagamentos: A Conciliar | LT_Fin_Requests_By_Status · LT_Fin_Requests_By_CostCenter |
| Executivo | Ocorrências: Candidatas Extravio · Extravios: Ressarcidos · Solicitações: A Pagar · Faturamento: Em Aberto | LT_Dash_Executivo (dashboard) |

---

## 2. Lightning Record Pages (FlexiPages) dos objetos novos

**Status:** não construídas. A UI de registro já está coberta por **Page Layouts**
completos + **Path** em todos os objetos (Módulos A–J). Só existem record pages
customizadas para `LT_Logistics_Unit__c` e `Operational_Indicator__c` (herdadas).

**O que falta (opcional, no Lightning App Builder):** criar Record Pages com
Dynamic Forms para os objetos principais e atribuí-las aos apps:

- `LT_Shipment__c`, `LT_Tracking_Event__c`
- `LT_Driver__c`, `LT_Vehicle__c`, `LT_Driver_Document__c`
- `LT_Route__c`, `LT_Delivery_Attempt__c`
- `LT_Manifest__c`, `LT_Manifest_Line__c`, `LT_Pickup_Request__c`
- `LT_Operational_Incident__c`
- `LT_Loss_Claim__c`, `LT_Driver_Penalty__c`
- `LT_Payment_Request__c`, `LT_Payment__c`, `LT_Expense__c`
- `LT_Commercial_Agreement__c`, `LT_Monthly_Billing__c`
- `Case` (layout SAC já existe; falta a record page com Path + related lists)

---

## 3. Status de Case em português

**Status:** os Cases usam os 4 status **padrão em inglês** (New / Working /
Escalated / Closed) porque customizar o `CaseStatus` (StandardValueSet) quebra
todo deploy de Business Process do Case com `Picklist value: New not found`.

**O que falta (no Setup → Picklist Value Sets → Case Status):** adicionar os
valores em português (ex.: Novo, Em Andamento, Aguardando Cliente, Escalado,
Resolvido, Fechado) e reordenar o Support Process `LT_SAC_Process`. Fazer
**direto no Setup**, não por metadata.

---

## 4. Relatórios que não puderam ser gerados por metadata

- **Faturamento por embarcador / por mês / por status** (`LT_Monthly_Billing__c`):
  o report type do objeto (Master-Detail de Account) retorna `Report is Obsolete`
  no deploy. Criar no **construtor de relatórios** usando o tipo
  "Contas com Faturamento Mensal" (ou similar).
- **Pipeline comercial por etapa** (Opportunity): refs de campo padrão
  (`Opportunity.StageName`, `Opportunity.Amount`) rejeitadas no XML. Criar no
  construtor de relatórios (tipo Oportunidades) — funil por Etapa, soma de Valor,
  filtro Record Type = "Prospecção de Embarcador".

---

## 5. Higienização final do metadata local (fazer no fim do projeto)

Itens que ficaram **stale no source local** mas são inofensivos na org:

- ~40 Profiles padrão e `settings/Search.settings` ainda referenciam objetos
  Trailhead **já deletados** da org.
- Campos de exemplo Trailhead não removidos: `Product2.Macaron_Flavor__c`,
  `Product2.Shirt__c`, `User.Account_ID__c`, `User.Account_Type__c`, e o
  Global Value Set `Flavors`.

**Ação:** fazer um **re-retrieve limpo** (`sf project retrieve start` com um
`package.xml` só do que interessa) antes da publicação final, ou remover esses
arquivos do `force-app/` manualmente.

---

## 6. Notificações e templates

- **Templates de e-mail** dos Approval Processes (`LT_Reimbursement_Approval`,
  `LT_Payment_Approval`) não foram criados — a aprovação usa o e-mail padrão.
  Criar templates em pt-BR se quiser um toque mais realista.
- **Alertas de e-mail** dos flows agendados (`LT_Driver_CNH_Expiry_Alert`,
  `LT_Case_PNR_Aging`, `LT_Incident_Escalate_Aging`, `LT_Shipment_Detect_*`)
  hoje só atualizam campos / criam registros; não enviam e-mail. Adicionar
  ação de e-mail se desejado.

---

## 7. Segurança / compartilhamento

- **OWD (Organization-Wide Defaults):** a maioria dos objetos está em
  Public Read/Write (padrão). Para um portfólio mais rico, definir
  Private / Public Read Only em objetos sensíveis (ex.: `LT_Payment_Request__c`,
  `LT_Driver_Penalty__c`) + **Sharing Rules** por base/regional.
- **Permission Set Assignments:** hoje só o usuário admin (Robert Pestana) tem
  os permission sets. Os usuários de teste do Módulo M precisarão receber os
  sets certos por área.

---

## 8. Agendamento dos flows

Os flows agendados foram deployados como `Scheduled` + `Active`, mas **confirme
no Setup → Flows** que a frequência (diária) e o horário de início estão como
desejado; o deploy nem sempre materializa o agendamento até a primeira edição.
