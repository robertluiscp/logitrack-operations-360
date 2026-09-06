#!/usr/bin/env python3
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from metahelp import *

ROOT = r"C:\Users\Robert Luis\Desktop\LogiTrack-SFDX\force-app\main\default"
C = os.path.join(ROOT, "objects", "Case")
for s in ("fields", "recordTypes", "compactLayouts"):
    os.makedirs(os.path.join(C, s), exist_ok=True)

def wc(name, xml):
    open(os.path.join(C, "fields", f"{name}.field-meta.xml"), "w", encoding="utf-8", newline="\n").write(xml.strip() + "\n")

# ---------- fields ----------
wc("LT_Shipment__c", lookup("LT_Shipment__c", "Remessa", "Remessa objeto da reclamacao.",
   "LT_Shipment__c", "Chamados SAC", "LT_Cases", lf_optional=True))
wc("LT_Driver_Involved__c", lookup("LT_Driver_Involved__c", "Motorista Envolvido",
   "Motorista relacionado ao chamado (assinado nao recebido, avaria, postura).", "LT_Driver__c",
   "Chamados SAC", "LT_Cases", lf_optional=True, track=False))
wc("LT_Base__c", lookup("LT_Base__c", "Base Responsavel",
   "Base de entrega responsavel pela tratativa.", "LT_Logistics_Unit__c", "Chamados SAC", "LT_Cases", lf_optional=True))
wc("LT_Customer_Channel__c", picklist("LT_Customer_Channel__c", "Canal de Contato",
   "Canal pelo qual o cliente acionou o SAC.",
   ["Telefone", "Chat", "E-mail", "Marketplace", "App do Cliente", "Redes Sociais"], track=False))
wc("LT_Marketplace__c", picklist("LT_Marketplace__c", "Marketplace de Origem",
   "Marketplace de origem do pedido reclamado.",
   ["Shopee", "Mercado Livre", "Shein", "TikTok Shop", "Amazon", "Magalu", "Loja Propria", "C2C", "Outro"], track=False))
wc("LT_Root_Cause__c", picklist("LT_Root_Cause__c", "Causa Raiz",
   "Causa raiz apurada pelo SAC.",
   ["Falha do Motorista", "Falha da Base", "Endereco Incorreto", "Extravio Interno", "Avaria em Transporte",
    "Problema Sistemico", "Informacao Incorreta do Cliente", "Sem Culpa da LogiTrack", "Outro"], track=False))
wc("LT_Resolution_Deadline__c", field("LT_Resolution_Deadline__c", "Prazo de Resolucao (SLA)",
   "Data/hora limite para resolver o chamado.", "DateTime"))
wc("LT_First_Response_Date__c", field("LT_First_Response_Date__c", "Primeira Resposta em",
   "Data/hora da primeira resposta ao cliente.", "DateTime"))
wc("LT_Forwarded_To_Driver_Date__c", field("LT_Forwarded_To_Driver_Date__c", "Encaminhado ao Motorista em",
   "Data/hora em que o chamado foi encaminhado ao motorista.", "DateTime"))
wc("LT_Driver_Response_Deadline__c", field("LT_Driver_Response_Deadline__c", "Prazo do Motorista",
   "Prazo para o motorista resolver antes do chamado virar PNR.", "DateTime"))
wc("LT_PNR_Flag__c", field("LT_PNR_Flag__c", "Virou PNR",
   "Marcado quando o chamado nao foi tratado no prazo e virou PNR (Paguei Nao Recebi).", "Checkbox", default="false"))
wc("LT_Reimbursement_Value__c", field("LT_Reimbursement_Value__c", "Valor de Ressarcimento",
   "Valor a ressarcir ao embarcador em caso de extravio/avaria confirmados.", "Currency", precision=12, scale=2))
wc("LT_Driver_Penalized__c", field("LT_Driver_Penalized__c", "Motorista Penalizado",
   "Marcado quando o motorista foi penalizado em decorrencia do chamado.", "Checkbox", default="false"))
wc("LT_Days_Open__c", formula("LT_Days_Open__c", "Dias em Aberto",
   "Dias corridos desde a abertura (ou ate o fechamento).", "Number",
   'IF(IsClosed, (ClosedDate - CreatedDate), (NOW() - CreatedDate))', precision=6, scale=1))
wc("LT_Is_Overdue__c", formula("LT_Is_Overdue__c", "Fora do Prazo",
   "Verdadeiro quando o chamado esta aberto e passou do prazo de SLA.", "Checkbox",
   'AND(NOT(IsClosed), NOT(ISBLANK(LT_Resolution_Deadline__c)), NOW() &gt; LT_Resolution_Deadline__c)'))
wc("LT_First_Response_Hours__c", formula("LT_First_Response_Hours__c", "Horas ate 1a Resposta",
   "Horas entre a abertura do chamado e a primeira resposta.", "Number",
   'IF(ISBLANK(LT_First_Response_Date__c), NULL, (LT_First_Response_Date__c - CreatedDate) * 24)', precision=6, scale=1))

# ---------- record types ----------
RTS = [
 ("LT_Assinado_Nao_Recebido", "Assinado nao Recebido",
  "Pedido consta como entregue no app, mas o cliente afirma que nao recebeu. Encaminhado ao motorista para resolucao; se nao tratado no prazo, vira PNR."),
 ("LT_Agilizacao", "Agilizacao de Entrega",
  "Cliente solicita agilizacao da entrega por falta de evolucao no rastreamento."),
 ("LT_Avaria_Pos_Entrega", "Avaria apos a Entrega",
  "Pedido chegou avariado/quebrado. Motorista e informado e a remessa segue para extravio/ressarcimento."),
 ("LT_Postura_Motorista", "Postura do Motorista",
  "Reclamacao sobre conduta ou falta de respeito do motorista. Se confirmada pelo SAC, o motorista e penalizado."),
 ("LT_PNR", "PNR - Paguei Nao Recebi",
  "Chamado de Assinado nao Recebido que nao foi tratado no prazo. Segue para extravio e ressarcimento ao embarcador."),
]
for dev, label, desc in RTS:
    open(os.path.join(C, "recordTypes", f"{dev}.recordType-meta.xml"), "w", encoding="utf-8", newline="\n").write(
f"""<?xml version="1.0" encoding="UTF-8"?>
<RecordType xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>{dev}</fullName>
    <active>true</active>
    <compactLayoutAssignment>LT_SAC_Highlights</compactLayoutAssignment>
    <description>{desc}</description>
    <label>{label}</label>
</RecordType>
""")

# ---------- compact layout ----------
open(os.path.join(C, "compactLayouts", "LT_SAC_Highlights.compactLayout-meta.xml"), "w", encoding="utf-8", newline="\n").write(
   compact("LT_SAC_Highlights", "SAC - Destaques",
           ["CaseNumber", "Status", "Priority", "LT_Shipment__c", "LT_Resolution_Deadline__c", "OwnerId"]))

# ---------- standard value sets: relabel + extend ----------
def svs(name, values, extra_attr=None):
    # values: list of (fullName, label, dict_of_extra)
    vs = ""
    for fn, lab, ex in values:
        exl = "".join(f"\n        <{k}>{v}</{k}>" for k, v in (ex or {}).items())
        vs += f"""    <standardValue>
        <fullName>{fn}</fullName>
        <default>false</default>
        <label>{lab}</label>{exl}
    </standardValue>
"""
    open(os.path.join(ROOT, "standardValueSets", f"{name}.standardValueSet-meta.xml"), "w", encoding="utf-8", newline="\n").write(
f"""<?xml version="1.0" encoding="UTF-8"?>
<StandardValueSet xmlns="http://soap.sforce.com/2006/04/metadata">
    <sorted>false</sorted>
{vs}</StandardValueSet>
""")

svs("CaseStatus", [
  ("New", "Novo", {"closed": "false"}),
  ("Working", "Em Analise", {"closed": "false"}),
  ("Encaminhado ao Motorista", "Encaminhado ao Motorista", {"closed": "false"}),
  ("Aguardando Cliente", "Aguardando Cliente", {"closed": "false"}),
  ("Escalated", "Escalado", {"closed": "false"}),
  ("Resolvido", "Resolvido", {"closed": "true"}),
  ("Closed", "Fechado", {"closed": "true"}),
])
svs("CaseOrigin", [
  ("Phone", "Telefone", {}),
  ("Email", "E-mail", {}),
  ("Chat", "Chat", {}),
  ("Marketplace", "Marketplace", {}),
  ("App", "App do Cliente", {}),
  ("Web", "Portal", {}),
])
svs("CaseReason", [
  ("Assinado nao Recebido", "Assinado nao Recebido", {}),
  ("Atraso na Entrega", "Atraso na Entrega", {}),
  ("Avaria", "Avaria", {}),
  ("Extravio", "Extravio", {}),
  ("Postura do Motorista", "Postura do Motorista", {}),
  ("Endereco Incorreto", "Endereco Incorreto", {}),
  ("Outro", "Outro", {}),
])

print("SAC: fields", len(os.listdir(os.path.join(C, "fields"))), "RTs", len(RTS))
