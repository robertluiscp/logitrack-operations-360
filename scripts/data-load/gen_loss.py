#!/usr/bin/env python3
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from metahelp import *

ROOT = r"C:\Users\Robert Luis\Desktop\LogiTrack-SFDX\force-app\main\default"
LC = os.path.join(ROOT, "objects", "LT_Loss_Claim__c")
DP = os.path.join(ROOT, "objects", "LT_Driver_Penalty__c")
ensure(LC); ensure(DP)

# ==================== LT_Loss_Claim__c ====================
REASON = ["PNR - Paguei Nao Recebi", "Assinado Nao Recebido", "Avaria na Entrega", "Avaria em Transporte",
          "Retido +10 dias", "Sem Movimentacao +10 dias", "Roubo / Furto de Carga", "Sinistro (Acidente)",
          "Endereco Inexistente", "Outro"]
RESP = ["Motorista", "Base", "Transporte (SC / MR / Coleta)", "Cliente / Embarcador", "Terceiro", "Sem Responsavel Definido"]
LCSTATUS = ["Em Apuracao", "Em Aprovacao", "Aprovado", "Ressarcido", "Indeferido", "Cancelado"]

wf(LC, "LT_Shipment__c", lookup("LT_Shipment__c", "Remessa", "Remessa extraviada.",
   "LT_Shipment__c", "Extravios", "LT_Loss_Claims", required=True, delete="Restrict"))
wf(LC, "LT_Shipment_Key__c", field("LT_Shipment_Key__c", "Chave da Remessa",
   "Chave tecnica que impede dois extravios para a mesma remessa.", "Text",
   length=20, unique=True, extid=True, track=False))
wf(LC, "LT_Loss_Reason__c", picklist("LT_Loss_Reason__c", "Motivo do Extravio",
   "Motivo pelo qual a remessa foi considerada extraviada.", REASON, track=False))
wf(LC, "LT_Responsibility__c", picklist("LT_Responsibility__c", "Responsabilidade",
   "Parte responsavel apurada pelo extravio.", RESP, default="Sem Responsavel Definido"))
wf(LC, "LT_Status__c", picklist("LT_Status__c", "Status do Extravio",
   "Etapa de apuracao, aprovacao e ressarcimento.", LCSTATUS, default="Em Apuracao"))
wf(LC, "LT_Case__c", lookup("LT_Case__c", "Chamado de Origem", "Chamado SAC que originou o extravio.",
   "Case", "Extravios", "LT_Loss_Claims", lf_optional=True, track=False))
wf(LC, "LT_Operational_Incident__c", lookup("LT_Operational_Incident__c", "Ocorrencia de Origem",
   "Ocorrencia operacional que originou o extravio.", "LT_Operational_Incident__c",
   "Extravios", "LT_Loss_Claims", lf_optional=True, track=False))
wf(LC, "LT_Responsible_Driver__c", lookup("LT_Responsible_Driver__c", "Motorista Responsavel",
   "Motorista responsabilizado pelo extravio.", "LT_Driver__c", "Extravios", "LT_Loss_Claims", lf_optional=True, track=False))
wf(LC, "LT_Responsible_Base__c", lookup("LT_Responsible_Base__c", "Base Responsavel",
   "Base responsabilizada pelo extravio.", "LT_Logistics_Unit__c", "Extravios", "LT_Loss_Claims", lf_optional=True, track=False))
wf(LC, "LT_Detected_Date__c", field("LT_Detected_Date__c", "Data de Deteccao", "Data em que o extravio foi registrado.", "Date", required=True))
wf(LC, "LT_Declared_Value__c", field("LT_Declared_Value__c", "Valor Declarado", "Valor declarado da remessa.", "Currency", precision=12, scale=2))
wf(LC, "LT_Reimbursement_Value__c", field("LT_Reimbursement_Value__c", "Valor de Ressarcimento",
   "Valor aprovado para ressarcir o embarcador.", "Currency", precision=12, scale=2))
wf(LC, "LT_Driver_Charge_Value__c", field("LT_Driver_Charge_Value__c", "Valor Descontado do Motorista",
   "Valor a descontar do motorista quando ele e o responsavel.", "Currency", precision=12, scale=2))
wf(LC, "LT_Approved_By__c", lookup("LT_Approved_By__c", "Aprovado Por", "Usuario que aprovou o ressarcimento.",
   "User", "Extravios Aprovados", "LT_Approved_Loss_Claims", lf_optional=True, track=False))
wf(LC, "LT_Approval_Date__c", field("LT_Approval_Date__c", "Data de Aprovacao", "Data da aprovacao do ressarcimento.", "Date"))
wf(LC, "LT_Reimbursement_Date__c", field("LT_Reimbursement_Date__c", "Data do Ressarcimento", "Data em que o embarcador foi ressarcido.", "Date"))
wf(LC, "LT_Batch_Reference__c", field("LT_Batch_Reference__c", "Lote de Extravio",
   "Identificador do lote quando o extravio foi processado em massa.", "Text", length=30, track=False))
wf(LC, "LT_Description__c", field("LT_Description__c", "Descricao", "Detalhamento do extravio.", "LongTextArea", length=8000, lines=4, track=False))
wf(LC, "LT_Resolution_Notes__c", field("LT_Resolution_Notes__c", "Notas de Encerramento", "Justificativa de aprovacao ou indeferimento.", "LongTextArea", length=8000, lines=3, track=False))

wf(LC, "LT_Days_To_Resolve__c", formula("LT_Days_To_Resolve__c", "Dias ate Resolucao",
   "Dias entre a deteccao e o ressarcimento (ou hoje, se em aberto).", "Number",
   'IF(ISBLANK(LT_Detected_Date__c), NULL, IF(NOT(ISBLANK(LT_Reimbursement_Date__c)), LT_Reimbursement_Date__c - LT_Detected_Date__c, TODAY() - LT_Detected_Date__c))',
   precision=6, scale=0))
wf(LC, "LT_Net_Company_Cost__c", formula("LT_Net_Company_Cost__c", "Custo Liquido da Empresa",
   "Valor ressarcido menos o que foi recuperado do motorista.", "Currency",
   'BLANKVALUE(LT_Reimbursement_Value__c, 0) - BLANKVALUE(LT_Driver_Charge_Value__c, 0)', precision=16, scale=2))
wf(LC, "LT_Generates_Penalty__c", formula("LT_Generates_Penalty__c", "Gera Penalizacao",
   "Verdadeiro quando o motorista e o responsavel e ha valor a descontar dele.", "Checkbox",
   'AND(ISPICKVAL(LT_Responsibility__c, "Motorista"), BLANKVALUE(LT_Driver_Charge_Value__c, 0) &gt; 0)'))

wv(LC, "LT_Claim_Driver_Resp_Requires_Driver", "Responsabilidade Motorista exige o motorista responsavel.",
   'AND(ISPICKVAL(LT_Responsibility__c, "Motorista"), ISBLANK(LT_Responsible_Driver__c))',
   "Informe o Motorista Responsavel.", "LT_Responsible_Driver__c")
wv(LC, "LT_Claim_Approved_Requires_Data", "Extravio aprovado ou ressarcido exige aprovador e valor.",
   'AND(OR(ISPICKVAL(LT_Status__c, "Aprovado"), ISPICKVAL(LT_Status__c, "Ressarcido")), OR(ISBLANK(LT_Approved_By__c), ISBLANK(LT_Reimbursement_Value__c)))',
   "Informe o aprovador e o valor de ressarcimento.", "LT_Reimbursement_Value__c")
wv(LC, "LT_Claim_Reimbursed_Requires_Date", "Extravio Ressarcido exige a data do ressarcimento.",
   'AND(ISPICKVAL(LT_Status__c, "Ressarcido"), ISBLANK(LT_Reimbursement_Date__c))',
   "Informe a Data do Ressarcimento.", "LT_Reimbursement_Date__c")
wv(LC, "LT_Claim_Values_Not_Negative", "Valores do extravio nao podem ser negativos.",
   'OR(LT_Reimbursement_Value__c &lt; 0, LT_Driver_Charge_Value__c &lt; 0, LT_Declared_Value__c &lt; 0)',
   "Os valores do extravio nao podem ser negativos.")
wv(LC, "LT_Claim_Charge_Not_Above_Reimb", "Desconto do motorista nao pode exceder o ressarcimento.",
   'AND(NOT(ISBLANK(LT_Driver_Charge_Value__c)), NOT(ISBLANK(LT_Reimbursement_Value__c)), LT_Driver_Charge_Value__c &gt; LT_Reimbursement_Value__c)',
   "O valor descontado do motorista nao pode ser maior que o valor de ressarcimento.", "LT_Driver_Charge_Value__c")
wv(LC, "LT_Claim_Denied_Requires_Notes", "Extravio Indeferido exige justificativa.",
   'AND(ISPICKVAL(LT_Status__c, "Indeferido"), ISBLANK(LT_Resolution_Notes__c))',
   "Justifique o indeferimento em Notas de Encerramento.", "LT_Resolution_Notes__c")

open(os.path.join(LC, "compactLayouts", "LT_Loss_Claim_Summary.compactLayout-meta.xml"), "w", encoding="utf-8", newline="\n").write(
   compact("LT_Loss_Claim_Summary", "Extravio - Resumo",
           ["Name", "LT_Shipment__c", "LT_Loss_Reason__c", "LT_Status__c", "LT_Reimbursement_Value__c", "LT_Responsibility__c"]))
for n, l, cols, fil in [
  ("All", "Todos", ["NAME", "LT_Shipment__c", "LT_Loss_Reason__c", "LT_Responsibility__c", "LT_Status__c", "LT_Reimbursement_Value__c", "LT_Detected_Date__c"], None),
  ("Em_Apuracao", "Em Apuracao e Aprovacao", ["NAME", "LT_Loss_Reason__c", "LT_Responsibility__c", "LT_Status__c", "LT_Declared_Value__c", "LT_Days_To_Resolve__c"],
   [("LT_Status__c", "equals", "Em Apuracao,Em Aprovacao")]),
  ("Ressarcidos", "Ressarcidos", ["NAME", "LT_Shipment__c", "LT_Loss_Reason__c", "LT_Reimbursement_Value__c", "LT_Net_Company_Cost__c", "LT_Reimbursement_Date__c"],
   [("LT_Status__c", "equals", "Ressarcido")]),
]:
    open(os.path.join(LC, "listViews", f"{n}.listView-meta.xml"), "w", encoding="utf-8", newline="\n").write(listview(n, l, cols, fil))

wobj(LC, "LT_Loss_Claim__c", "Extravio", "Extravios", "Codigo do Extravio", "AutoNumber", "EXT-{000000}", compact="LT_Loss_Claim_Summary")

# ==================== LT_Driver_Penalty__c ====================
PTYPE = ["Desconto por Extravio", "Desconto por Avaria", "Advertencia (Postura)",
         "Suspensao Temporaria", "Desligamento", "Multa Contratual"]
PORIGIN = ["Extravio", "Chamado SAC", "Ocorrencia Operacional", "Auditoria", "Outro"]
PSTATUS = ["Registrada", "Em Contestacao", "Confirmada", "Descontada", "Revertida", "Cancelada"]
COUTCOME = ["Pendente", "Mantida", "Reduzida", "Cancelada"]

wf(DP, "LT_Driver__c", lookup("LT_Driver__c", "Motorista", "Motorista penalizado.",
   "LT_Driver__c", "Penalizacoes", "LT_Penalties", required=True, delete="Restrict"))
wf(DP, "LT_Penalty_Type__c", picklist("LT_Penalty_Type__c", "Tipo de Penalizacao",
   "Natureza da penalizacao aplicada ao motorista.", PTYPE, track=False))
wf(DP, "LT_Origin__c", picklist("LT_Origin__c", "Origem", "De onde partiu a penalizacao.", PORIGIN, track=False))
wf(DP, "LT_Status__c", picklist("LT_Status__c", "Status", "Situacao da penalizacao.", PSTATUS, default="Registrada"))
wf(DP, "LT_Loss_Claim__c", lookup("LT_Loss_Claim__c", "Extravio de Origem",
   "Extravio que originou a penalizacao.", "LT_Loss_Claim__c", "Penalizacoes", "LT_Penalties", lf_optional=True, track=False))
wf(DP, "LT_Case__c", lookup("LT_Case__c", "Chamado de Origem",
   "Chamado SAC que originou a penalizacao.", "Case", "Penalizacoes", "LT_Penalties", lf_optional=True, track=False))
wf(DP, "LT_Applied_In_Manifest__c", lookup("LT_Applied_In_Manifest__c", "Descontada no Romaneio",
   "Romaneio em que o desconto foi aplicado.", "LT_Manifest__c", "Penalizacoes Aplicadas", "LT_Applied_Penalties", lf_optional=True, track=False))
wf(DP, "LT_Amount__c", field("LT_Amount__c", "Valor", "Valor do desconto ou multa.", "Currency", precision=12, scale=2))
wf(DP, "LT_Reference_Date__c", field("LT_Reference_Date__c", "Data de Referencia", "Data do fato gerador da penalizacao.", "Date", required=True))
wf(DP, "LT_Applied_By__c", lookup("LT_Applied_By__c", "Aplicada Por", "Usuario que aplicou a penalizacao.",
   "User", "Penalizacoes Aplicadas Por", "LT_Applied_By_Penalties", lf_optional=True, track=False))
wf(DP, "LT_Contested__c", field("LT_Contested__c", "Contestada", "Marcada quando o motorista contesta a penalizacao.", "Checkbox", default="false"))
wf(DP, "LT_Contest_Date__c", field("LT_Contest_Date__c", "Data da Contestacao", "Data em que o motorista contestou.", "Date"))
wf(DP, "LT_Contest_Outcome__c", picklist("LT_Contest_Outcome__c", "Resultado da Contestacao",
   "Desfecho da contestacao do motorista.", COUTCOME, default="Pendente", track=False))
wf(DP, "LT_Description__c", field("LT_Description__c", "Descricao", "Detalhamento da penalizacao.", "LongTextArea", length=8000, lines=3, track=False))
wf(DP, "LT_Effective_Amount__c", formula("LT_Effective_Amount__c", "Valor Efetivo",
   "Valor realmente descontado apos a contestacao (Cancelada = 0, Reduzida = 50%).", "Currency",
   'CASE(TEXT(LT_Contest_Outcome__c), "Cancelada", 0, "Reduzida", BLANKVALUE(LT_Amount__c, 0) * 0.5, BLANKVALUE(LT_Amount__c, 0))',
   precision=16, scale=2))
wf(DP, "LT_Is_Financial__c", formula("LT_Is_Financial__c", "Penalizacao Financeira",
   "Verdadeiro para penalizacoes com valor a descontar.", "Checkbox",
   'OR(ISPICKVAL(LT_Penalty_Type__c, "Desconto por Extravio"), ISPICKVAL(LT_Penalty_Type__c, "Desconto por Avaria"), ISPICKVAL(LT_Penalty_Type__c, "Multa Contratual"))'))

wv(DP, "LT_Penalty_Financial_Requires_Amount", "Penalizacao financeira exige valor maior que zero.",
   'AND(OR(ISPICKVAL(LT_Penalty_Type__c, "Desconto por Extravio"), ISPICKVAL(LT_Penalty_Type__c, "Desconto por Avaria"), ISPICKVAL(LT_Penalty_Type__c, "Multa Contratual")), OR(ISBLANK(LT_Amount__c), LT_Amount__c &lt;= 0))',
   "Informe um valor maior que zero para penalizacoes financeiras.", "LT_Amount__c")
wv(DP, "LT_Penalty_Contested_Requires_Date", "Penalizacao contestada exige a data da contestacao.",
   'AND(LT_Contested__c, ISBLANK(LT_Contest_Date__c))',
   "Informe a Data da Contestacao.", "LT_Contest_Date__c")
wv(DP, "LT_Penalty_Discounted_Requires_Manifest", "Penalizacao Descontada exige o romaneio de aplicacao.",
   'AND(ISPICKVAL(LT_Status__c, "Descontada"), ISBLANK(LT_Applied_In_Manifest__c))',
   "Informe o romaneio em que o desconto foi aplicado.", "LT_Applied_In_Manifest__c")
wv(DP, "LT_Penalty_Reverted_Requires_Contest", "Penalizacao Revertida exige contestacao com resultado.",
   'AND(ISPICKVAL(LT_Status__c, "Revertida"), OR(NOT(LT_Contested__c), ISPICKVAL(LT_Contest_Outcome__c, "Pendente")))',
   "So e possivel reverter uma penalizacao contestada e julgada.", "LT_Status__c")

open(os.path.join(DP, "compactLayouts", "LT_Driver_Penalty_Summary.compactLayout-meta.xml"), "w", encoding="utf-8", newline="\n").write(
   compact("LT_Driver_Penalty_Summary", "Penalizacao - Resumo",
           ["Name", "LT_Driver__c", "LT_Penalty_Type__c", "LT_Status__c", "LT_Effective_Amount__c", "LT_Reference_Date__c"]))
for n, l, cols, fil in [
  ("All", "Todas", ["NAME", "LT_Driver__c", "LT_Penalty_Type__c", "LT_Origin__c", "LT_Status__c", "LT_Amount__c", "LT_Effective_Amount__c", "LT_Reference_Date__c"], None),
  ("Contestadas", "Contestadas", ["NAME", "LT_Driver__c", "LT_Penalty_Type__c", "LT_Amount__c", "LT_Contest_Date__c", "LT_Contest_Outcome__c"],
   [("LT_Contested__c", "equals", "1")]),
  ("A_Descontar", "A Descontar", ["NAME", "LT_Driver__c", "LT_Penalty_Type__c", "LT_Effective_Amount__c", "LT_Reference_Date__c"],
   [("LT_Status__c", "equals", "Confirmada")]),
]:
    open(os.path.join(DP, "listViews", f"{n}.listView-meta.xml"), "w", encoding="utf-8", newline="\n").write(listview(n, l, cols, fil))

wobj(DP, "LT_Driver_Penalty__c", "Penalizacao de Motorista", "Penalizacoes de Motorista",
     "Codigo da Penalizacao", "AutoNumber", "PEN-{000000}", compact="LT_Driver_Penalty_Summary")

# ---------- Case: add loss claim lookup ----------
open(os.path.join(ROOT, "objects", "Case", "fields", "LT_Loss_Claim__c.field-meta.xml"), "w", encoding="utf-8", newline="\n").write(
   lookup("LT_Loss_Claim__c", "Extravio", "Extravio aberto a partir deste chamado.",
          "LT_Loss_Claim__c", "Chamados", "LT_Cases", lf_optional=True, track=False).strip() + "\n")

# ---------- layouts ----------
simple_layout(os.path.join(ROOT, "layouts", "LT_Loss_Claim__c-Extravio Layout.layout-meta.xml"), [
  ("Extravio", "TwoColumnsLeftToRight", [
    [("Readonly", "Name"), ("Required", "LT_Shipment__c"), ("Edit", "LT_Loss_Reason__c"), ("Edit", "LT_Status__c"), ("Required", "LT_Detected_Date__c")],
    [("Edit", "LT_Responsibility__c"), ("Edit", "LT_Responsible_Driver__c"), ("Edit", "LT_Responsible_Base__c"), ("Edit", "LT_Batch_Reference__c")]]),
  ("Origem", "TwoColumnsLeftToRight", [
    [("Edit", "LT_Case__c"), ("Edit", "LT_Operational_Incident__c")],
    [("Edit", "LT_Description__c")]]),
  ("Valores e Aprovacao", "TwoColumnsLeftToRight", [
    [("Edit", "LT_Declared_Value__c"), ("Edit", "LT_Reimbursement_Value__c"), ("Edit", "LT_Driver_Charge_Value__c"), ("Readonly", "LT_Net_Company_Cost__c"), ("Readonly", "LT_Generates_Penalty__c")],
    [("Edit", "LT_Approved_By__c"), ("Edit", "LT_Approval_Date__c"), ("Edit", "LT_Reimbursement_Date__c"), ("Readonly", "LT_Days_To_Resolve__c")]]),
  ("Encerramento", "OneColumn", [[("Edit", "LT_Resolution_Notes__c")]]),
], related=["LT_Driver_Penalty__c.LT_Loss_Claim__c", "RelatedHistoryList"])

simple_layout(os.path.join(ROOT, "layouts", "LT_Driver_Penalty__c-Penalizacao de Motorista Layout.layout-meta.xml"), [
  ("Penalizacao", "TwoColumnsLeftToRight", [
    [("Readonly", "Name"), ("Required", "LT_Driver__c"), ("Edit", "LT_Penalty_Type__c"), ("Edit", "LT_Origin__c"), ("Edit", "LT_Status__c")],
    [("Required", "LT_Reference_Date__c"), ("Edit", "LT_Amount__c"), ("Readonly", "LT_Effective_Amount__c"), ("Edit", "LT_Applied_By__c")]]),
  ("Origem e Aplicacao", "TwoColumnsLeftToRight", [
    [("Edit", "LT_Loss_Claim__c"), ("Edit", "LT_Case__c")],
    [("Edit", "LT_Applied_In_Manifest__c"), ("Readonly", "LT_Is_Financial__c")]]),
  ("Contestacao", "TwoColumnsLeftToRight", [
    [("Edit", "LT_Contested__c"), ("Edit", "LT_Contest_Date__c")],
    [("Edit", "LT_Contest_Outcome__c"), ("Edit", "LT_Description__c")]]),
])

print("Loss Claim fields:", len(os.listdir(os.path.join(LC, "fields"))), "| Penalty fields:", len(os.listdir(os.path.join(DP, "fields"))))
