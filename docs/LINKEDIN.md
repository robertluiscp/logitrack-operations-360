# Post para LinkedIn

Três versões: **curta** (feed), **longa** (artigo/carrossel) e **linha de "Sobre"
do perfil**. Ajuste o link do GitHub e do vídeo antes de publicar.

---

## Versão curta (feed + imagem/carrossel)

> 🚚 **LogiTrack Operations 360** — construí do zero um ambiente Salesforce completo
> para uma transportadora de última milha, como projeto de portfólio.
>
> Peguei tudo o que estudei nas trilhas **Administrador Básico** e **Administrador
> Intermediário** do Trailhead e apliquei em um caso real de logística: bases e
> franquias, embarcadores, motoristas terceirizados (TAC / MEI / ETC / MR / Coleta),
> coletas, romaneios, rotas, rastreamento de remessas, ocorrências operacionais,
> SAC, prevenção de perdas (extravio / PNR) e o financeiro de contas a pagar.
>
> 📦 O que tem dentro:
> • 19 objetos personalizados, ~507 campos, 110 regras de validação
> • 14 Record Types com Business Processes e Path
> • 19 Flows (record‑triggered, agendados, de tela) + 2 processos de aprovação
>   (um deles multinível, por alçada de valor)
> • 6 Lightning Apps, hierarquia de 17 papéis, Permission Set Groups por área
> • 18 relatórios e 9 dashboards
> • ~4.500 registros fictícios carregados por Bulk API
>
> Tudo declarativo — **clicks, not code**. Os metadados foram versionados no Git
> (27 commits, um por módulo) e gerados por scripts para manter a consistência.
>
> 🔗 Código e documentação: [GITHUB_URL]
> 🎥 Vídeo de 7 min mostrando as 6 áreas: [VIDEO_URL]
>
> Feedback é muito bem‑vindo. 🙌
>
> #Salesforce #SalesforceAdmin #Trailhead #Logística #Admin360 #CRM

---

## Versão longa (artigo do LinkedIn / legenda de carrossel)

**Como transformei o que aprendi no Trailhead em um ambiente Salesforce inteiro**

Depois de concluir as trilhas *Administrador Básico* e *Administrador Intermediário*,
quis provar que sabia usar aquilo junto — não em exercícios soltos, mas num sistema
que faz sentido de ponta a ponta. Escolhi um domínio que eu conheço: **logística de
última milha**.

Nasceu o **LogiTrack Operations 360**: o Salesforce de uma transportadora fictícia,
a LogiTrack Brasil.

**As 6 áreas**

1. **Operação** — a unidade logística (Regional → CD → Base), a remessa e sua linha
   do tempo de rastreamento, coletas, romaneios de pagamento a motorista e rotas de
   entrega com tentativas geolocalizadas. Flows detectam remessas retidas e sem
   movimentação e abrem ocorrências automaticamente.
2. **Comercial** — embarcadores, contratos, faturamento mensal com roll‑ups e um
   funil de prospecção em 9 etapas.
3. **Cadastro e Frota** — motoristas com 5 modelos de contratação, cada um com
   regras próprias (mínimo de pacotes, exigência de veículo, situação da CNH), e a
   frota com validação de placa Mercosul.
4. **SAC** — casos de PNR, avaria, agilização e postura do motorista, com filas e
   roteamento automático por tipo.
5. **Prevenção de Perdas** — apuração de extravios, ressarcimento ao embarcador com
   aprovação por valor, e penalização do motorista com fluxo de contestação. Quando
   o extravio é aprovado com culpa do motorista, a penalização é criada sozinha.
6. **Financeiro** — solicitações de pagamento com **aprovação multinível por alçada**
   (Coordenação → Gerência → Diretoria), pagamentos com conciliação bancária e
   despesas por centro de custo.

**O que isso exercitou**

Objetos e todos os tipos de campo (fórmula, roll‑up, geolocalização, autonumber,
external id), Record Types e Business Processes, 110 regras de validação, Page
Layouts e Compact Layouts, Path, Flows dos quatro tipos, processos de aprovação com
field updates, filas e regras de atribuição, Lightning App Builder (apps, abas, home
pages), relatórios e dashboards, hierarquia de papéis e — em vez de perfis — 
**Permission Sets e Permission Set Groups** por área.

**Como foi feito**

Salesforce DX, com os metadados versionados no Git em 27 commits (um bloco por
módulo). Para não perder a consistência em mais de 500 campos, gerei o XML dos
metadados a partir de scripts — uma pegada de "infraestrutura como código" aplicada
à configuração declarativa. Os ~4.500 registros fictícios foram carregados por
Bulk API 2.0.

O repositório traz um `README` completo, um roteiro de vídeo e a lista honesta do
que ficou para configuração manual (algumas coisas realmente não passam pela
Metadata API).

🔗 [GITHUB_URL] · 🎥 [VIDEO_URL]

Se você trabalha com Salesforce e tiver críticas, manda ver — é assim que eu aprendo.

#Salesforce #SalesforceAdmin #Trailhead #Admin #Logistica #CRM #ClicksNotCode

---

## Linha para a seção "Sobre" do perfil

> Administrador Salesforce em formação. Projeto de portfólio: **LogiTrack Operations
> 360**, um ambiente Salesforce completo (19 objetos, 19 Flows, aprovações
> multinível, 6 apps, dashboards) para uma transportadora de última milha —
> 100 % declarativo e versionado no Git. [GITHUB_URL]
