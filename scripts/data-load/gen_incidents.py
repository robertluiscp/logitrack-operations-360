#!/usr/bin/env python3
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from metahelp import *

ROOT = r"C:\Users\Robert Luis\Desktop\LogiTrack-SFDX\force-app\main\default"
I = os.path.join(ROOT, "objects", "LT_Operational_Incident__c")
ensure(I)

ITYPE = ["Retido com Motorista", "Retido na Base", "Sem Movimentacao",
         "Suspeita de Extravio", "Avaria em Transporte", "Entrada no Galpao sem Expedicao"]
ISTATUS = ["Aberta", "Em Tratamento", "Aguardando Terceiro", "Escalada", "Resolvida", "Cancelada"]
PRIO = ["Baixa", "Media", "Alta", "Critica"]
RESTYPE = ["Entregue", "Reagendada", "Devolvida ao Remetente", "Encaminhada para Extravio",
           "Localizada e Reintegrada", "Sem Acao Necessaria"]
ROOTC = ["Endereco Incorreto", "Cliente Ausente", "Falha de Triagem", "Extravio Interno",
         "Avaria", "Falha Sistemica", "Postura do Motorista", "Fora da Area de Cobertura", "Outro"]

wf(I, "LT_Shipment__c", lookup("LT_Shipment__c", "Remessa", "Remessa afetada pela ocorrencia.",
   "LT_Shipment__c", "Ocorrencias Operacionais", "LT_Operational_Incidents",
   required=True, delete="Restrict"))
wf(I, "LT_Incident_Type__c", picklist("LT_Incident_Type__c", "Tipo de Ocorrencia",
   "Natureza da ocorrencia operacional.", ITYPE, track=False))
wf(I, "LT_Status__c", picklist("LT_Status__c", "Status", "Situacao do tratamento da ocorrencia.", ISTATUS, default="Aberta"))
wf(I, "LT_Priority__c", picklist("LT_Priority__c", "Prioridade", "Prioridade de tratamento.", PRIO, default="Media"))
wf(I, "LT_Detected_Date__c", field("LT_Detected_Date__c", "Detectada em",
   "Data em que a ocorrencia foi identificada.", "Date", required=True))
wf(I, "LT_Owner_Unit__c", lookup("LT_Owner_Unit__c", "Unidade Responsavel",
   "Base ou CD responsavel pelo tratamento.", "LT_Logistics_Unit__c", "Ocorrencias", "LT_Operational_Incidents", lf_optional=True))
wf(I, "LT_Responsible_Driver__c", lookup("LT_Responsible_Driver__c", "Motorista Envolvido",
   "Motorista que esta com a remessa (retido com motorista).", "LT_Driver__c",
   "Ocorrencias", "LT_Operational_Incidents", lf_optional=True, track=False))
wf(I, "LT_Assigned_To__c", lookup("LT_Assigned_To__c", "Responsavel pelo Tratamento",
   "Usuario que esta tratando a ocorrencia.", "User", "Ocorrencias Atribuidas", "LT_Assigned_Incidents", track=False, lf_optional=True))
wf(I, "LT_Resolution_Deadline__c", field("LT_Resolution_Deadline__c", "Prazo de Resolucao",
   "Data limite para resolver a ocorrencia (SLA).", "Date"))
wf(I, "LT_Resolved_Date__c", field("LT_Resolved_Date__c", "Resolvida em", "Data/hora da resolucao.", "DateTime"))
wf(I, "LT_Resolution_Type__c", picklist("LT_Resolution_Type__c", "Tipo de Resolucao",
   "Como a ocorrencia foi encerrada.", RESTYPE, track=False))
wf(I, "LT_Root_Cause__c", picklist("LT_Root_Cause__c", "Causa Raiz",
   "Causa raiz identificada.", ROOTC, track=False))
wf(I, "LT_Escalated__c", field("LT_Escalated__c", "Escalada", "Marcada quando a ocorrencia foi escalada a coordenacao.", "Checkbox", default="false"))
wf(I, "LT_Escalation_Date__c", field("LT_Escalation_Date__c", "Data de Escalonamento", "Data em que a ocorrencia foi escalada.", "Date"))
wf(I, "LT_Description__c", field("LT_Description__c", "Descricao", "Detalhamento da ocorrencia.", "LongTextArea", length=8000, lines=4, track=False))
wf(I, "LT_Resolution_Notes__c", field("LT_Resolution_Notes__c", "Notas de Resolucao", "Registro do que foi feito para resolver.", "LongTextArea", length=8000, lines=4, track=False))

wf(I, "LT_Days_Open__c", formula("LT_Days_Open__c", "Dias em Aberto",
   "Dias entre a deteccao e a resolucao (ou hoje, se ainda aberta).", "Number",
   'IF(ISBLANK(LT_Detected_Date__c), NULL, IF(NOT(ISBLANK(LT_Resolved_Date__c)), DATEVALUE(LT_Resolved_Date__c) - LT_Detected_Date__c, TODAY() - LT_Detected_Date__c))',
   precision=6, scale=0))
wf(I, "LT_Is_Open__c", formula("LT_Is_Open__c", "Em Aberto",
   "Verdadeiro enquanto a ocorrencia nao foi resolvida nem cancelada.", "Checkbox",
   'AND(NOT(ISPICKVAL(LT_Status__c, "Resolvida")), NOT(ISPICKVAL(LT_Status__c, "Cancelada")))'))
wf(I, "LT_Is_Overdue__c", formula("LT_Is_Overdue__c", "Fora do Prazo",
   "Verdadeiro quando a ocorrencia esta aberta e passou do prazo de resolucao.", "Checkbox",
   'AND(LT_Is_Open__c, NOT(ISBLANK(LT_Resolution_Deadline__c)), TODAY() &gt; LT_Resolution_Deadline__c)'))
wf(I, "LT_Aging_Bucket__c", formula("LT_Aging_Bucket__c", "Faixa de Envelhecimento",
   "Classifica a ocorrencia pelo tempo em aberto. Acima de 10 dias vira candidata a extravio.", "Text",
   'IF(ISBLANK(LT_Days_Open__c), "-", IF(LT_Days_Open__c &lt;= 2, "0-2 dias", IF(LT_Days_Open__c &lt;= 5, "3-5 dias", IF(LT_Days_Open__c &lt;= 10, "6-10 dias", "+10 dias (candidata a extravio)"))))'))

wv(I, "LT_Incident_Resolved_Requires_Data", "Ocorrencia Resolvida exige data e tipo de resolucao.",
   'AND(ISPICKVAL(LT_Status__c, "Resolvida"), OR(ISBLANK(LT_Resolved_Date__c), ISBLANK(TEXT(LT_Resolution_Type__c))))',
   "Ao resolver informe a data e o tipo de resolucao.", "LT_Resolution_Type__c")
wv(I, "LT_Incident_Driver_Type_Requires_Driver", "Retido com Motorista exige o motorista envolvido.",
   'AND(ISPICKVAL(LT_Incident_Type__c, "Retido com Motorista"), ISBLANK(LT_Responsible_Driver__c))',
   "Informe o Motorista Envolvido para ocorrencias do tipo Retido com Motorista.", "LT_Responsible_Driver__c")
wv(I, "LT_Incident_In_Treatment_Requires_Assignee", "Ocorrencia Em Tratamento exige responsavel.",
   'AND(ISPICKVAL(LT_Status__c, "Em Tratamento"), ISBLANK(LT_Assigned_To__c))',
   "Atribua um responsavel antes de mover para Em Tratamento.", "LT_Assigned_To__c")
wv(I, "LT_Incident_Deadline_After_Detection", "O prazo de resolucao nao pode ser anterior a deteccao.",
   'AND(NOT(ISBLANK(LT_Resolution_Deadline__c)), NOT(ISBLANK(LT_Detected_Date__c)), LT_Resolution_Deadline__c &lt; LT_Detected_Date__c)',
   "O Prazo de Resolucao nao pode ser anterior a data de deteccao.", "LT_Resolution_Deadline__c")
wv(I, "LT_Incident_Escalated_Requires_Date", "Ocorrencia escalada exige data de escalonamento.",
   'AND(LT_Escalated__c, ISBLANK(LT_Escalation_Date__c))',
   "Informe a Data de Escalonamento.", "LT_Escalation_Date__c")

open(os.path.join(I, "compactLayouts", "LT_Operational_Incident_Summary.compactLayout-meta.xml"), "w", encoding="utf-8", newline="\n").write(
   compact("LT_Operational_Incident_Summary", "Ocorrencia - Resumo",
           ["Name", "LT_Incident_Type__c", "LT_Status__c", "LT_Priority__c", "LT_Days_Open__c", "LT_Assigned_To__c"]))
for n, l, cols, fil in [
  ("All", "Todas", ["NAME", "LT_Shipment__c", "LT_Incident_Type__c", "LT_Status__c", "LT_Priority__c", "LT_Detected_Date__c", "LT_Days_Open__c", "LT_Assigned_To__c"], None),
  ("Abertas", "Ocorrencias Abertas", ["NAME", "LT_Incident_Type__c", "LT_Priority__c", "LT_Detected_Date__c", "LT_Resolution_Deadline__c", "LT_Days_Open__c", "LT_Assigned_To__c"],
   [("LT_Is_Open__c", "equals", "true")]),
  ("Fora_do_Prazo", "Fora do Prazo", ["NAME", "LT_Incident_Type__c", "LT_Priority__c", "LT_Detected_Date__c", "LT_Resolution_Deadline__c", "LT_Days_Open__c", "LT_Assigned_To__c"],
   [("LT_Is_Overdue__c", "equals", "true")]),
  ("Candidatas_Extravio", "Candidatas a Extravio (+10 dias)", ["NAME", "LT_Shipment__c", "LT_Incident_Type__c", "LT_Detected_Date__c", "LT_Days_Open__c", "LT_Aging_Bucket__c"],
   [("LT_Aging_Bucket__c", "equals", "+10 dias (candidata a extravio)")]),
]:
    open(os.path.join(I, "listViews", f"{n}.listView-meta.xml"), "w", encoding="utf-8", newline="\n").write(listview(n, l, cols, fil))

wobj(I, "LT_Operational_Incident__c", "Ocorrencia Operacional", "Ocorrencias Operacionais",
     "Codigo da Ocorrencia", "AutoNumber", "OC-{000000}", compact="LT_Operational_Incident_Summary")

simple_layout(os.path.join(ROOT, "layouts", "LT_Operational_Incident__c-Ocorrencia Operacional Layout.layout-meta.xml"), [
  ("Ocorrencia", "TwoColumnsLeftToRight", [
    [("Readonly", "Name"), ("Required", "LT_Shipment__c"), ("Edit", "LT_Incident_Type__c"), ("Edit", "LT_Status__c"), ("Edit", "LT_Priority__c")],
    [("Required", "LT_Detected_Date__c"), ("Edit", "LT_Owner_Unit__c"), ("Edit", "LT_Responsible_Driver__c"), ("Edit", "LT_Assigned_To__c")]]),
  ("Tratamento e SLA", "TwoColumnsLeftToRight", [
    [("Edit", "LT_Resolution_Deadline__c"), ("Readonly", "LT_Days_Open__c"), ("Readonly", "LT_Aging_Bucket__c"), ("Readonly", "LT_Is_Overdue__c")],
    [("Edit", "LT_Escalated__c"), ("Edit", "LT_Escalation_Date__c"), ("Edit", "LT_Root_Cause__c")]]),
  ("Resolucao", "TwoColumnsLeftToRight", [
    [("Edit", "LT_Resolved_Date__c"), ("Edit", "LT_Resolution_Type__c")],
    [("Edit", "LT_Resolution_Notes__c")]]),
  ("Descricao", "OneColumn", [[("Edit", "LT_Description__c")]]),
], related=["RelatedHistoryList"])

print("Incident fields:", len(os.listdir(os.path.join(I, "fields"))))
