#!/usr/bin/env python3
import os
ROOT = r"C:\Users\Robert Luis\Desktop\LogiTrack-SFDX\force-app\main\default"

def fp(f, e): return f'    <fieldPermissions>\n        <editable>{str(e).lower()}</editable>\n        <field>{f}</field>\n        <readable>true</readable>\n    </fieldPermissions>'
def op(o,c,e,d): return f'    <objectPermissions>\n        <allowCreate>{str(c).lower()}</allowCreate>\n        <allowDelete>{str(d).lower()}</allowDelete>\n        <allowEdit>{str(e).lower()}</allowEdit>\n        <allowRead>true</allowRead>\n        <modifyAllRecords>false</modifyAllRecords>\n        <object>{o}</object>\n        <viewAllFields>false</viewAllFields>\n        <viewAllRecords>false</viewAllRecords>\n    </objectPermissions>'
def tab(t): return f'    <tabSettings>\n        <tab>{t}</tab>\n        <visibility>Visible</visibility>\n    </tabSettings>'

lc_e = ["LT_Loss_Reason__c","LT_Responsibility__c","LT_Status__c","LT_Case__c","LT_Operational_Incident__c",
  "LT_Responsible_Driver__c","LT_Responsible_Base__c","LT_Declared_Value__c","LT_Reimbursement_Value__c",
  "LT_Driver_Charge_Value__c","LT_Approved_By__c","LT_Approval_Date__c","LT_Reimbursement_Date__c",
  "LT_Batch_Reference__c","LT_Description__c","LT_Resolution_Notes__c"]
lc_r = ["LT_Days_To_Resolve__c","LT_Net_Company_Cost__c","LT_Generates_Penalty__c","LT_Shipment_Key__c"]
dp_e = ["LT_Penalty_Type__c","LT_Origin__c","LT_Status__c","LT_Loss_Claim__c","LT_Case__c","LT_Applied_In_Manifest__c",
  "LT_Amount__c","LT_Applied_By__c","LT_Contested__c","LT_Contest_Date__c","LT_Contest_Outcome__c","LT_Description__c"]
dp_r = ["LT_Effective_Amount__c","LT_Is_Financial__c"]

L = ['<?xml version="1.0" encoding="UTF-8"?>','<PermissionSet xmlns="http://soap.sforce.com/2006/04/metadata">']
L.append('    <description>Prevencao de perdas: apuracao de extravios, aprovacao de ressarcimento a embarcadores e penalizacao de motoristas.</description>')
L.append('    <hasActivationRequired>false</hasActivationRequired>')
L.append('    <label>LT - Extravios e Penalizacoes</label>')
for f in lc_e: L.append(fp(f"LT_Loss_Claim__c.{f}", True))
for f in lc_r: L.append(fp(f"LT_Loss_Claim__c.{f}", False))
for f in dp_e: L.append(fp(f"LT_Driver_Penalty__c.{f}", True))
for f in dp_r: L.append(fp(f"LT_Driver_Penalty__c.{f}", False))
L.append(fp("Case.LT_Loss_Claim__c", True))
L.append('    <applicationVisibilities>\n        <application>LogiTrack_Operations_360</application>\n        <visible>true</visible>\n    </applicationVisibilities>')
L.append('    <applicationVisibilities>\n        <application>LogiTrack_SAC</application>\n        <visible>true</visible>\n    </applicationVisibilities>')
L.append(op("LT_Loss_Claim__c", True, True, True))
L.append(op("LT_Driver_Penalty__c", True, True, True))
L.append(op("LT_Shipment__c", False, True, False))
L.append(op("LT_Driver__c", False, False, False))
L.append(op("Case", False, True, False))
for t in ["LT_Loss_Claim__c","LT_Driver_Penalty__c"]:
    L.append(tab(t))
L.append('</PermissionSet>')
open(os.path.join(ROOT, "permissionsets", "LT_Loss_Prevention.permissionset-meta.xml"), "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")

# app tabs
p = os.path.join(ROOT, "applications", "LogiTrack_Operations_360.app-meta.xml")
t = open(p, encoding="utf-8").read()
if "<tabs>LT_Loss_Claim__c</tabs>" not in t:
    t = t.replace("    <tabs>LT_Operational_Incident__c</tabs>\n",
                  "    <tabs>LT_Operational_Incident__c</tabs>\n    <tabs>LT_Loss_Claim__c</tabs>\n    <tabs>LT_Driver_Penalty__c</tabs>\n")
open(p, "w", encoding="utf-8", newline="\n").write(t)

# paths
for obj, fld, label, steps in [
 ("LT_Loss_Claim__c", "LT_Status__c", "Fluxo do Extravio", [
   ("Em Apuracao", ["LT_Loss_Reason__c","LT_Responsibility__c"], "Extravio registrado. Apure o motivo e a responsabilidade; levante o valor declarado."),
   ("Em Aprovacao", ["LT_Reimbursement_Value__c","LT_Driver_Charge_Value__c"], "Valores definidos. Submeta para aprovacao da coordenacao (acima de R$ 300)."),
   ("Aprovado", ["LT_Approved_By__c","LT_Approval_Date__c"], "Ressarcimento aprovado. Se a responsabilidade for do motorista, a penalizacao e criada automaticamente."),
   ("Ressarcido", ["LT_Reimbursement_Date__c"], "Embarcador ressarcido. Remessa marcada como ressarcida no rastreamento."),
   ("Indeferido", ["LT_Resolution_Notes__c"], "Ressarcimento indeferido. Justifique o motivo."),
 ]),
 ("LT_Driver_Penalty__c", "LT_Status__c", "Fluxo da Penalizacao", [
   ("Registrada", ["LT_Penalty_Type__c","LT_Amount__c"], "Penalizacao registrada. Informe o motorista da penalizacao e do valor."),
   ("Em Contestacao", ["LT_Contest_Date__c"], "Motorista contestou a penalizacao. SAC/Coordenacao analisa."),
   ("Confirmada", [], "Penalizacao confirmada apos analise. Pronta para desconto no proximo romaneio."),
   ("Descontada", ["LT_Applied_In_Manifest__c"], "Valor descontado no romaneio do motorista."),
   ("Revertida", ["LT_Contest_Outcome__c"], "Penalizacao revertida apos contestacao procedente."),
 ]),
]:
    ps = ""
    for val, flds, info in steps:
        fn = "".join(f"        <fieldNames>{x}</fieldNames>\n" for x in flds)
        ps += f"""    <pathAssistantSteps>
{fn}        <info>&lt;p&gt;{info}&lt;/p&gt;</info>
        <picklistValueName>{val}</picklistValueName>
    </pathAssistantSteps>
"""
    open(os.path.join(ROOT, "pathAssistants", f"{obj}_Path.pathAssistant-meta.xml"), "w", encoding="utf-8", newline="\n").write(
f"""<?xml version="1.0" encoding="UTF-8"?>
<PathAssistant xmlns="http://soap.sforce.com/2006/04/metadata">
    <active>true</active>
    <entityName>{obj}</entityName>
    <fieldName>{fld}</fieldName>
    <masterLabel>{label}</masterLabel>
    <recordTypeName>__MASTER__</recordTypeName>
{ps}</PathAssistant>
""")

print("I security + app + paths written")
