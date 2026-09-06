# Estratégia de rollout do app Salesforce Mobile — LogiTrack

Módulo R. Cobre a parte de **configuração** (feita neste repo) e a parte de
**change management** (checklist para o piloto).

---

## 1. O que já está configurado

| Item | Estado |
|---|---|
| Form factors dos apps | Todos os 6 apps LogiTrack com `Large` **e** `Small` |
| Compact Layouts | Os 19 objetos personalizados têm compact layout — é o "cartão" que aparece no mobile e nas buscas |
| Lightning Record Pages | 6 objetos-bandeira com Dynamic Forms (renderizam bem no mobile por serem responsivas) |
| Global Quick Actions (barra de ações) | `Nova solicitação de pagamento` e `Registrar ocorrência operacional` na Global Layout — aparecem na barra de ações do app mobile |
| Quick Action de Flow | `Consultar CEP` (ViaCEP) criada; colocar num Lightning Record Page ou utility bar pelo App Builder (Flow não entra na lista de ações clássica) |
| Paths | 11 objetos com Path — o Path funciona no mobile e guia o preenchimento |

## 2. Perfis / personas que usam o mobile

| Persona | Uso mobile principal |
|---|---|
| Supervisor de base | Consultar remessas retidas, abrir ocorrência, ver rotas do dia |
| Coordenação regional | Aprovar solicitações de pagamento e ressarcimentos (aprovações funcionam no mobile) |
| Atendente SAC (campo) | Abrir extravio a partir do chamado, registrar penalização |
| Analista de cadastro | Consultar CNH a vencer, atualizar documento de veículo |

## 3. Checklist de rollout (fazer no Setup / com o piloto)

- [ ] **Salesforce Mobile App QuickStart** — rodar o assistente (Setup → Salesforce Mobile App).
- [ ] **Navegação mobile por app** — em cada app Lightning, revisar a ordem dos itens de navegação (a mesma config serve desktop e mobile no Lightning).
- [ ] **Ações da página** — no App Builder, revisar a seção "Salesforce Mobile e Lightning Experience Actions" das record pages (Remessa, Extravio, Solicitação de Pagamento) e deixar as 3–4 ações mais usadas primeiro.
- [ ] **Notificações push** — habilitar em Setup → Notification Builder; ligar as notificações de aprovação pendente e de menção.
- [ ] **Offline** — avaliar o Mobile Offline (briefcase) para as list views de remessas retidas e rotas do dia (uso em área sem sinal).
- [ ] **Compact layout por Record Type** — Case e Motorista têm vários RTs; conferir se o compact layout escolhido faz sentido para cada um.
- [ ] **Piloto** — 3 a 5 supervisores de base por 2 semanas; coletar feedback por um Case interno ou um formulário.
- [ ] **Treinamento** — vídeo curto (o mesmo roteiro de `ROTEIRO-VIDEO.md`, versão mobile) + card de "primeiros passos" via In-App Guidance (os prompts do Módulo N já aparecem no mobile).
- [ ] **Métricas** — acompanhar adoção em Setup → Salesforce Mobile App → Analytics (logins mobile, ações executadas).

## 4. Boas práticas aplicadas

- Compact layouts curtos (5–6 campos) — o topo do registro no mobile.
- Campos obrigatórios das quick actions são poucos — formulário rápido de preencher com o polegar.
- Fórmulas e roll-ups como *readonly* nas record pages — nada de teclado numérico desnecessário.
- Path em vez de instruções soltas — orienta o próximo passo sem abrir ajuda.
