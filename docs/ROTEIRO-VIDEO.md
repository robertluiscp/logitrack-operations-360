# Roteiro de vídeo — LogiTrack Operations 360 (~6 a 8 min)

Demonstração para portfólio (LinkedIn / YouTube). Tela gravada + narração.
Ritmo: mostrar, não ler. Cada bloco abaixo é uma "cena".

---

## 0. Abertura (20 s)
- Tela: App Launcher com os 6 apps LogiTrack.
- Fala: *"Construí do zero um ambiente Salesforce completo para uma transportadora
  de última milha. Tudo declarativo — sem Apex de produção — aplicando o que
  aprendi nas trilhas de Administrador Básico e Intermediário. Vou mostrar as seis
  áreas."*

## 1. Estrutura e segurança (45 s)
- Setup → Object Manager: rolar a lista de objetos `LT_*`.
- Hierarquia de papéis (17 papéis, CEO → diretorias → gerências → analistas).
- Permission Set Groups: abrir `LT_PSG_Operacao` e mostrar os permission sets que
  ele agrupa. Mencionar que o projeto é *permission‑set‑led* (perfis no `.forceignore`).

## 2. Operação — a remessa de ponta a ponta (90 s)
- App **LogiTrack Operations 360** → aba Remessas → abrir uma remessa.
- Mostrar o **Path** (13 etapas) e a related list de **Eventos de Rastreamento**.
- Criar um evento "Chegada na base de destino" → salvar → mostrar o status da
  remessa mudando **sozinho** (Flow record‑triggered).
- Abrir uma **Rota** → related list de Tentativas de Entrega → rodar o **Screen Flow**
  "Registrar tentativa de entrega" (tela de resultado + tela de prova).
- Aba **Ocorrências Operacionais** → filtrar "Candidatas a Extravio" → explicar a
  fórmula de *aging* ("+10 dias sem movimentação").

## 3. Comercial (40 s)
- App **LogiTrack Comercial** → um Embarcador → Contrato Comercial + Faturamento
  Mensal (roll‑ups no Account).
- Oportunidade de Prospecção → Path de 9 etapas.

## 4. Cadastro e Frota (40 s)
- App **LogiTrack Cadastro** → um Motorista → mostrar os campos **derivados do
  Record Type** (sigla, modelo de pagamento, mín/máx de pacotes).
- Regra de validação da placa (Mercosul x antiga) — tentar salvar placa inválida.
- Flow agendado de CNH a vencer (mostrar no Setup → Flows).

## 5. SAC + Prevenção de Perdas (75 s)
- App **LogiTrack SAC** → criar um Case do tipo **PNR** → mostrar a **regra de
  atribuição** jogando na fila certa.
- Abrir um **Extravio** (`LT_Loss_Claim__c`) → preencher valores → mudar status para
  "Em Aprovação" → **submeter para aprovação** (> R$ 300 exige coordenação).
- Aprovar → mostrar a **Penalização de Motorista criada automaticamente** pelo Flow.
- Abrir a penalização → simular contestação → mostrar a fórmula "valor efetivo".

## 6. Financeiro (75 s)
- App **LogiTrack Financeiro** → nova **Solicitação de Pagamento** de R$ 12.000 →
  mostrar a fórmula de **alçada** dizendo "Diretoria".
- Submeter → mostrar o **processo de aprovação multinível** (Coordenação → Gerência
  → Diretoria) no histórico de aprovação.
- Aprovar todos os níveis → lançar um **Pagamento** filho → mostrar a solicitação
  virando "Paga" sozinha (Flow) e os roll‑ups (Valor Pago / Saldo).
- Aba Despesas → agrupar por centro de custo.

## 7. Relatórios e Dashboards (50 s)
- Pasta **LogiTrack — Relatórios** (18 relatórios com gráfico).
- **Dashboard Executivo — Sul**: os 5 metric cards + gráficos.
- **Painel Financeiro** e **Painel de Prevenção de Perdas**.

## 8. Fechamento (20 s)
- Tela: o repositório no GitHub (README + estrutura de pastas).
- Fala: *"27 commits, um por módulo. Os metadados foram gerados por scripts Python
  para manter 500+ campos e 110 regras de validação consistentes. Código e
  documentação no GitHub; link na descrição."*

---

### Dicas de gravação
- Gravar em uma org **com os dados carregados** (senão os dashboards ficam vazios).
- Usar o usuário **admin** para ter acesso a tudo, mas mostrar 1x o login como
  usuário de área (ex.: Ana / Comercial) para provar o modelo de permissão.
- Cortar tempos de carregamento na edição.
- Legendas em português; se for postar internacional, versão com narração em inglês.
