# Auditoria — Trilhas de Administrador (Trailhead) × Projeto LogiTrack

Data: 2026-09-06. Compara o conteúdo das trilhas **Admin Beginner** e **Admin
Intermediate** do Trailhead com o que foi efetivamente construído na org.

Fontes das trilhas:
- Admin Beginner — https://trailhead.salesforce.com/content/learn/trails/force_com_admin_beginner
- Admin Intermediate — https://trailhead.salesforce.com/content/learn/trails/force_com_admin_intermediate

Legenda: ✅ coberto com profundidade · 🟡 parcial · ❌ não coberto

---

## Parte 1 — Trilha Admin Beginner

### Módulo: Data Modeling ✅
| Unidade | No projeto |
|---|---|
| Standard & Custom Objects | 19 objetos personalizados + `Operational_Indicator__c`; extensão de Account, Case, Contact, Opportunity |
| Object Relationships | 67 Lookup, 7 Master‑Detail (roll‑ups reais), hierarquia em User (papéis). `LT_Manifest_Line__c`, `LT_Tracking_Event__c`, `LT_Delivery_Attempt__c`, `LT_Payment__c` como filhos MD |
| Schema Builder | conceito aplicado (o modelo inteiro é um schema), sem uso do Schema Builder em si (é ferramenta visual, não gera metadata distinto) |

**Tipos de campo usados:** Text, LongTextArea, Picklist (63), Number, Currency (25), Percent, Date (34), DateTime, Checkbox (27), Lookup (67), Master‑Detail (7), Formula (56), Roll‑Up Summary (13), Geolocation (`LT_Delivery_Attempt__c.LT_Location__c`), AutoNumber (todos os objetos transacionais), URL, Phone, External Id (8).

### Módulo: Data Management 🟡
| Tópico | No projeto |
|---|---|
| Importar/exportar dados | ✅ Bulk API 2.0 usado em massa (166 bases, ~4.500 registros), com upsert por External Id, split PJ/PF, tratamento de picklist restrita |
| Data Loader / Data Import Wizard | ✅ equivalente via `sf data import bulk` (a habilidade é a mesma: mapear colunas, external id, tratar erros) |
| **Regras de Duplicação / Matching Rules** | ❌ **nenhuma criada**. Só as 3 padrão (Account/Contact/Lead). Faltou, por ex., uma regra de duplicação em `LT_Driver__c` por CPF/CNPJ e em `Account` (Embarcador) por CNPJ |
| Qualidade de dados / Data.com | n/a (recurso descontinuado) |

### Módulo: Lightning Experience Customization 🟡
| Unidade | No projeto |
|---|---|
| Set Up Your Org (empresa, ano fiscal, idioma, moeda) | ❌ **não configurado** — fuso/idioma/moeda default da org; sem Business Hours e Holidays |
| Create & Customize Apps | ✅ 6 Lightning Apps (Operations 360, Comercial, Cadastro, SAC, Financeiro, Executivo) com abas, branding, utility bar e **Home pages** atribuídas via `actionOverrides` |
| Create & Customize List Views | ✅ 46 list views nos objetos LT, várias com filtros e `<sharedTo>` |
| Compact Layouts | ✅ **todos os 19 objetos** têm compact layout personalizado |
| Customize Record Page Components & Fields | 🟡 **só 2 Lightning Record Pages** (`LT_Logistics_Unit__c`, `Operational_Indicator__c`) + 1 de Account (RT Parceiro). Faltam record pages para os 17 objetos novos (Dynamic Forms). Page Layouts clássicos existem em todos |
| **Custom Buttons & Links** | ❌ **nenhum criado**. Ex. que caberia: botão URL "Rastrear no site" na Remessa, link "Ver no mapa" na Tentativa de Entrega |
| **Quick Actions** | 🟡 **só 1** (`Update_Logistics_Unit`). Faltam ações rápidas como "Registrar ocorrência" na Remessa, "Nova tentativa" na Rota, "Abrir extravio" no Case, "Registrar chamada" |

### Módulo: User Engagement (In‑App Guidance) ❌
**Nada foi feito.** Nenhum Prompt (flutuante / direcionado / ancorado), nenhum
Walkthrough, nenhum Learning Path / caminho de aprendizagem. É um módulo inteiro
do Admin Beginner ausente do projeto.

### Módulo: Reports & Dashboards ✅
| Tópico | No projeto |
|---|---|
| Relatórios | ✅ 18 relatórios (pasta `LogiTrack - Relatorios`), formato Summary, agrupamentos, colunas com Sum/Average, filtros, **todos com gráfico** (Donut, HorizontalBar, Line) |
| **Custom Report Type** | ✅ 1 (`Unidades Logísticas com Indicadores Operacionais`, com join) |
| Dashboards | ✅ 9 dashboards grid‑layout: 6 por área + Executivo + 2 herdados atualizados. Componentes Metric, Bar, Donut, Line; **5 metric cards** no "Dashboard Executivo — Sul"; filtros de dashboard (UF, unidade) nos herdados |
| Dashboards dinâmicos / assinatura | 🟡 todos `SpecifiedUser`; sem dashboard dinâmico nem assinatura agendada |
| Report subscriptions / notificações | ❌ não configurado |

---

## Parte 2 — Trilha Admin Intermediate

### Módulo: Formulas and Validations ✅
| Tópico | No projeto |
|---|---|
| Campos de fórmula | ✅ **56 campos de fórmula**: texto, número, moeda, checkbox, data. Ex.: alçada de aprovação, custo líquido da empresa, aging bucket, dias em trânsito, valor efetivo da penalização |
| Fórmulas cross‑object | ✅ ex. em roll‑ups e em fórmulas que leem `LT_Shipment__r`, `RecordType.DeveloperName` |
| Regras de validação | ✅ **110 regras** distribuídas por 21 objetos, incl. REGEX (placa Mercosul, mês de competência AAAA‑MM), guardas `ISNEW()`, `ISCHANGED()`, `PRIORVALUE()`, dependências entre campos e status |

### Módulo: Data Security 🟡
| Unidade | No projeto |
|---|---|
| Control Access to the Org | ❌ sem configuração de IP ranges / horários de login / política de senha (é config de org, não versionável) |
| Control Access to Objects | ✅ via **Permission Sets** (10) e **Permission Set Groups** (6) — projeto *permission‑set‑led*, perfis no `.forceignore` |
| Control Access to Fields (FLS) | ✅ FLS definida nos permission sets para todos os campos LT (editável/somente‑leitura conforme fórmula/rollup) |
| Control Access to Records (OWD) | 🟡 **1 objeto** com OWD restrita: `LT_Logistics_Unit__c` = Public Read Only. Os outros 12 ficaram em Public Read/Write (default); 7 são ControlledByParent (MD) |
| Role Hierarchy | ✅ **17 papéis** (CEO Brasil → diretorias → gerências → coordenações → analistas / supervisão de base) |
| **Sharing Rules** | 🟡 **1 regra** (owner‑based: compartilha Unidades Logísticas com o grupo público `Operational_Analysts` em Edit). Faltam regras **criteria‑based** (ex.: compartilhar remessas de uma UF com a gerência regional) |
| Manual sharing / Restrição de acesso | ❌ não demonstrado |

### Módulo: Picklist Administration 🟡
| Tópico | No projeto |
|---|---|
| Tipos de picklist | ✅ 63 picklists; **51 restritas** |
| Global Value Sets | ✅ `Brazilian_States` usado em 3 campos (Unidade, Coleta, Remessa) |
| Standard Value Sets | ✅ `OpportunityStage` (relabel PT) e `CaseStatus` customizados |
| **Picklists dependentes (field dependency)** | ❌ **nenhuma criada** — 0 campos com `controllingField`. Ex. que caberia: Motivo do Extravio → Sub‑motivo; Tipo de Ocorrência → Causa Raiz |

### Módulo: Approve Records with Approval Processes ✅
| Tópico | No projeto |
|---|---|
| Processo de aprovação | ✅ **2 processos**: ressarcimento de extravio (> R$ 300, 1 etapa) e **pagamento por alçada (multinível)**: Coordenação sempre → Gerência ≥ R$ 2.000 → Diretoria ≥ R$ 10.000 |
| Critérios de entrada / de etapa | ✅ fórmulas de entrada; `entryCriteria` por etapa com `ifCriteriaNotMet=ApproveRecord` |
| Ações (inicial / final / rejeição / recall) | ✅ Field Updates de workflow (`workflows/LT_Payment_Request__c.workflow`, `LT_Loss_Claim__c.workflow`) em todas as fases |
| Aprovadores | ✅ usuário nomeado + `whenMultipleApprovers` |
| Testado | ✅ submit → *Em Aprovação*; recall → *Rascunho*; aprovação total → *Paga* + carimbo de data (via Apex `Approval.process`) |

### Módulo: AgentExchange Basics ❌
Não aplicável a um projeto de construção — o módulo é sobre **instalar apps/serviços
do AppExchange/AgentExchange** numa org. Nenhum pacote gerenciado instalado (o
projeto é 100% construído à mão, o que é a escolha certa para portfólio).

### Módulo: External Services ❌
**Não coberto.** Nenhum **Named Credential + External Service** conectando uma API
REST externa, nem Flow que invoque a ação gerada. Ex. que caberia: consulta de CEP
(ViaCEP), rastreamento dos Correios, ou um webhook fictício de status. O
`namedCredentials/Bank.namedCredential` presente é padrão da org.

### Módulo: Salesforce Mobile App Rollout ❌
Não coberto explicitamente. Os apps têm `formFactors>Small`, e os compact layouts
ajudam no mobile, mas não há estratégia de rollout, navegação mobile dedicada,
nem ações otimizadas para o app Salesforce Mobile.

### Projetos da trilha (Suggestion Box, Space Station) ✅ (equivalente)
Os apps de exemplo foram **deletados de propósito** (o usuário pediu remover todo
conteúdo Trailhead). As habilidades que esses projetos exercitam — criar objeto,
abas, campos, layout, app do zero — estão amplamente cobertas pelos 19 objetos.

---

## Parte 3 — Lacunas priorizadas (o que faria o projeto "fechar" as trilhas)

| # | Lacuna | Trilha / módulo | Esforço | Valor p/ portfólio |
|---|---|---|---|---|
| 1 | **In‑App Guidance** (2–3 prompts + 1 walkthrough) | Beginner / User Engagement | baixo | alto (módulo inteiro faltando) |
| 2 | **Custom Buttons & Links** (2–3: rastrear no site, ver no mapa, ligar p/ motorista) | Beginner / LEX Customization | baixo | médio |
| 3 | **Quick Actions** (4–5: registrar ocorrência, nova tentativa, abrir extravio, log a call) | Beginner / LEX Customization | baixo | alto |
| 4 | **Regras de Duplicação + Matching Rules** (Driver por CPF/CNPJ; Account por CNPJ) | Beginner / Data Management | baixo | alto |
| 5 | **Picklists dependentes** (Motivo → Sub‑motivo; Tipo de Ocorrência → Causa Raiz) | Interm. / Picklist Admin | baixo | médio |
| 6 | **Sharing Rules criteria‑based** + apertar OWD de 1–2 objetos sensíveis (`LT_Payment_Request__c`, `LT_Driver_Penalty__c`) | Interm. / Data Security | médio | alto |
| 7 | **Lightning Record Pages** (Dynamic Forms) para os objetos‑bandeira (Remessa, Motorista, Solicitação de Pagamento, Extravio, Case) | Beginner / LEX Customization | médio‑alto | alto |
| 8 | **External Services** (ViaCEP ou mock) + Flow que chama a ação | Interm. / External Services | médio | médio‑alto |
| 9 | **Set Up Your Org**: Business Hours + Holidays (usar nos SLAs), Company Info, fuso pt‑BR | Beginner / LEX Customization | baixo | médio |
| 10 | **Report/Dashboard subscriptions** + 1 dashboard dinâmico | Beginner / Reports & Dashboards | baixo | baixo |
| 11 | **Salesforce Mobile**: navegação mobile + ações mobile‑first + compact layouts revisados | Interm. / Mobile Rollout | médio | baixo‑médio |
| 12 | **AppExchange**: instalar 1 pacote gratuito útil (ex.: um utilitário de qualidade de dados) | Interm. / AgentExchange | baixo | baixo (foge do "100% declarativo à mão") |

> Itens 2, 3, 4, 5, 9 são "vitórias rápidas" — juntos fecham a maior parte das
> lacunas com pouco esforço. Itens 1, 6, 7, 8 são os que mais agregam ao portfólio.

---

## Parte 4 — Mapa completo do que foi criado na org

### Objetos personalizados (19 + 1)
| Objeto | Papel | Nº campos | RTs | VRs |
|---|---|---:|---:|---:|
| `LT_Logistics_Unit__c` | Regional / CD / Base de entrega | — | — | 8 |
| `Operational_Indicator__c` | Indicadores operacionais diários | — | — | 6 |
| `LT_Commercial_Agreement__c` | Contrato comercial | — | — | 4 |
| `LT_Monthly_Billing__c` | Faturamento mensal (MD de Account) | — | — | 5 |
| `LT_Driver__c` | Motorista | — | 5 (TAC/MEI/ETC/MR/Coleta) | 10 |
| `LT_Vehicle__c` | Veículo | — | — | 5 |
| `LT_Driver_Document__c` | Documento do motorista (MD) | — | — | 2 |
| `LT_Shipment__c` | Remessa | — | — | 6 |
| `LT_Tracking_Event__c` | Evento de rastreamento (MD) | — | — | 2 |
| `LT_Pickup_Request__c` | Solicitação de coleta | — | — | 6 |
| `LT_Manifest__c` | Romaneio | — | — | 6 |
| `LT_Manifest_Line__c` | Linha do romaneio (MD) | — | — | 1 |
| `LT_Route__c` | Rota de entrega | — | — | 7 |
| `LT_Delivery_Attempt__c` | Tentativa de entrega (MD de Rota) | — | — | 3 |
| `LT_Operational_Incident__c` | Ocorrência operacional | — | — | 5 |
| `LT_Loss_Claim__c` | Extravio | — | — | 6 |
| `LT_Driver_Penalty__c` | Penalização de motorista | — | — | 4 |
| `LT_Payment_Request__c` | Solicitação de pagamento | 33 | — | 8 |
| `LT_Payment__c` | Pagamento (MD) | 13 | — | 4 |
| `LT_Expense__c` | Despesa | 14 | — | 3 |

Extensões em objetos padrão: **Account** (2 RTs, 13 campos, 9 VRs), **Case**
(5 RTs, Support Process, 17 campos), **Contact** (1 campo), **Opportunity**
(1 RT, Business Process de 9 etapas, 5 campos).

### Automação
- **Flows: 19** — 8 record‑triggered *before‑save*, 5 record‑triggered *after‑save*,
  5 *scheduled* (diários), 1 **Screen Flow** (baixa de tentativa de entrega, 3 telas).
- **Processos de aprovação: 2** (+ 2 workflows só com field updates para as ações).
- **Regra de atribuição de Case** (roteia por Record Type para 5 filas).

### Interface
- **6 Lightning Apps** + **6 Home pages** (FlexiPage) + 1 utility bar.
- **3 Lightning Record Pages** (`LT_Logistics_Unit__c`, `Operational_Indicator__c`, Account/Parceiro).
- **Page Layouts** em todos os objetos; **19 Compact Layouts**; **11 Paths**;
  **46 List Views**; **1 Quick Action**.

### Dados e segurança
- **Hierarquia de papéis: 17.**
- **Permission Sets: 10** · **Permission Set Groups: 6** · **1 grupo público**
  (`Operational_Analysts`) · **5 filas** (SAC ×4 + Ocorrências).
- **OWD:** `LT_Logistics_Unit__c` Public Read Only + **1 Sharing Rule**.
- **Global Value Set:** `Brazilian_States`. **Standard Value Sets** customizados:
  `OpportunityStage`, `CaseStatus`.
- **External Ids: 8.** **Field History Tracking:** 19 objetos.

### Análise
- **1 Custom Report Type** · **18 relatórios** (com gráfico) · **9 dashboards**.

### Dados fictícios
~4.500 registros carregados por Bulk API 2.0, por área (bases, comercial,
motoristas, remessas, coletas, rotas, ocorrências, SAC, extravios, financeiro).
