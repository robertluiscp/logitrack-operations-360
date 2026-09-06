#!/usr/bin/env python3
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from metahelp import simple_layout

ROOT = r"C:\Users\Robert Luis\Desktop\LogiTrack-SFDX\force-app\main\default"

# ---------- queues ----------
QUEUES = [
 ("SAC_Triagem", "SAC - Triagem"),
 ("SAC_Regional_Sul", "SAC - Regional Sul"),
 ("SAC_Motoristas", "SAC - Tratativa com Motoristas"),
 ("SAC_PNR_Extravio", "SAC - PNR e Extravio"),
]
for dev, label in QUEUES:
    open(os.path.join(ROOT, "queues", f"{dev}.queue-meta.xml"), "w", encoding="utf-8", newline="\n").write(
f"""<?xml version="1.0" encoding="UTF-8"?>
<Queue xmlns="http://soap.sforce.com/2006/04/metadata">
    <name>{label}</name>
    <doesSendEmailToMembers>false</doesSendEmailToMembers>
    <queueSobject>
        <sobjectType>Case</sobjectType>
    </queueSobject>
</Queue>
""")

# ---------- Case assignment rules (replaces the file) ----------
open(os.path.join(ROOT, "objects", "Case", "..", "..", "assignmentRules", "Case.assignmentRules-meta.xml"), "w", encoding="utf-8", newline="\n").write(
"""<?xml version="1.0" encoding="UTF-8"?>
<AssignmentRules xmlns="http://soap.sforce.com/2006/04/metadata">
    <assignmentRule>
        <fullName>LT Roteamento SAC</fullName>
        <active>true</active>
        <ruleEntry>
            <assignedTo>SAC - PNR e Extravio</assignedTo>
            <assignedToType>Queue</assignedToType>
            <criteriaItems>
                <field>Case.RecordType</field>
                <operation>equals</operation>
                <value>PNR - Paguei Nao Recebi</value>
            </criteriaItems>
        </ruleEntry>
        <ruleEntry>
            <assignedTo>SAC - Regional Sul</assignedTo>
            <assignedToType>Queue</assignedToType>
            <criteriaItems>
                <field>Case.RecordType</field>
                <operation>equals</operation>
                <value>Postura do Motorista</value>
            </criteriaItems>
        </ruleEntry>
        <ruleEntry>
            <assignedTo>SAC - Regional Sul</assignedTo>
            <assignedToType>Queue</assignedToType>
            <criteriaItems>
                <field>Case.RecordType</field>
                <operation>equals</operation>
                <value>Avaria apos a Entrega</value>
            </criteriaItems>
        </ruleEntry>
        <ruleEntry>
            <assignedTo>SAC - Tratativa com Motoristas</assignedTo>
            <assignedToType>Queue</assignedToType>
            <criteriaItems>
                <field>Case.RecordType</field>
                <operation>equals</operation>
                <value>Assinado nao Recebido</value>
            </criteriaItems>
        </ruleEntry>
        <ruleEntry>
            <assignedTo>SAC - Triagem</assignedTo>
            <assignedToType>Queue</assignedToType>
            <criteriaItems>
                <field>Case.CreatedDate</field>
                <operation>notEqual</operation>
                <value></value>
            </criteriaItems>
        </ruleEntry>
    </assignmentRule>
</AssignmentRules>
""")

# ---------- layout ----------
simple_layout(os.path.join(ROOT, "layouts", "Case-LogiTrack SAC.layout-meta.xml"), [
  ("Identificacao do Chamado", "TwoColumnsLeftToRight", [
    [("Readonly", "CaseNumber"), ("Edit", "RecordTypeId"), ("Edit", "Status"), ("Edit", "Priority"), ("Edit", "Origin")],
    [("Edit", "AccountId"), ("Edit", "ContactId"), ("Edit", "LT_Customer_Channel__c"), ("Edit", "LT_Marketplace__c"), ("Edit", "OwnerId")]]),
  ("Objeto da Reclamacao", "TwoColumnsLeftToRight", [
    [("Edit", "LT_Shipment__c"), ("Edit", "LT_Driver_Involved__c"), ("Edit", "LT_Base__c")],
    [("Required", "Subject"), ("Edit", "Reason"), ("Edit", "LT_Root_Cause__c")]]),
  ("SLA e Tratativa", "TwoColumnsLeftToRight", [
    [("Edit", "LT_Resolution_Deadline__c"), ("Edit", "LT_First_Response_Date__c"), ("Readonly", "LT_First_Response_Hours__c"), ("Readonly", "LT_Days_Open__c"), ("Readonly", "LT_Is_Overdue__c")],
    [("Edit", "LT_Forwarded_To_Driver_Date__c"), ("Edit", "LT_Driver_Response_Deadline__c"), ("Edit", "LT_PNR_Flag__c"), ("Edit", "LT_Driver_Penalized__c"), ("Edit", "LT_Reimbursement_Value__c")]]),
  ("Descricao", "OneColumn", [[("Edit", "Description")]]),
], related=["RelatedHistoryList", "RelatedCaseSolution", "RelatedEmailList"])

# ---------- path ----------
open(os.path.join(ROOT, "pathAssistants", "LT_SAC_Case_Path.pathAssistant-meta.xml"), "w", encoding="utf-8", newline="\n").write(
"""<?xml version="1.0" encoding="UTF-8"?>
<PathAssistant xmlns="http://soap.sforce.com/2006/04/metadata">
    <active>true</active>
    <entityName>Case</entityName>
    <fieldName>Status</fieldName>
    <masterLabel>Fluxo do Chamado SAC</masterLabel>
    <recordTypeName>__MASTER__</recordTypeName>
    <pathAssistantSteps>
        <fieldNames>LT_Shipment__c</fieldNames>
        <fieldNames>LT_Customer_Channel__c</fieldNames>
        <info>&lt;p&gt;Chamado aberto. Vincule a remessa e registre o canal de contato do cliente.&lt;/p&gt;</info>
        <picklistValueName>New</picklistValueName>
    </pathAssistantSteps>
    <pathAssistantSteps>
        <fieldNames>LT_First_Response_Date__c</fieldNames>
        <fieldNames>LT_Root_Cause__c</fieldNames>
        <info>&lt;p&gt;Em analise: primeira resposta dada ao cliente; SAC apura a causa. Encaminhe ao motorista se aplicavel.&lt;/p&gt;</info>
        <picklistValueName>Working</picklistValueName>
    </pathAssistantSteps>
    <pathAssistantSteps>
        <fieldNames>LT_PNR_Flag__c</fieldNames>
        <fieldNames>LT_Reimbursement_Value__c</fieldNames>
        <info>&lt;p&gt;Escalado a coordenacao / PNR / extravio. Avalie ressarcimento ao embarcador e penalizacao do motorista.&lt;/p&gt;</info>
        <picklistValueName>Escalated</picklistValueName>
    </pathAssistantSteps>
    <pathAssistantSteps>
        <info>&lt;p&gt;Chamado encerrado. Registre a resolucao final e feche.&lt;/p&gt;</info>
        <picklistValueName>Closed</picklistValueName>
    </pathAssistantSteps>
</PathAssistant>
""")

# ---------- app ----------
open(os.path.join(ROOT, "applications", "LogiTrack_SAC.app-meta.xml"), "w", encoding="utf-8", newline="\n").write(
"""<?xml version="1.0" encoding="UTF-8"?>
<CustomApplication xmlns="http://soap.sforce.com/2006/04/metadata">
    <brand>
        <headerColor>#B02A37</headerColor>
        <shouldOverrideOrgTheme>false</shouldOverrideOrgTheme>
    </brand>
    <description>Aplicativo do Atendimento ao Cliente (SAC) da LogiTrack: chamados, PNR, extravios e tratativa com motoristas.</description>
    <formFactors>Large</formFactors>
    <formFactors>Small</formFactors>
    <isNavAutoTempTabsDisabled>false</isNavAutoTempTabsDisabled>
    <isNavPersonalizationDisabled>false</isNavPersonalizationDisabled>
    <isNavTabPersistenceDisabled>false</isNavTabPersistenceDisabled>
    <label>LogiTrack SAC</label>
    <navType>Standard</navType>
    <tabs>standard-home</tabs>
    <tabs>standard-Case</tabs>
    <tabs>standard-Contact</tabs>
    <tabs>standard-Account</tabs>
    <tabs>LT_Shipment__c</tabs>
    <tabs>LT_Operational_Incident__c</tabs>
    <tabs>standard-report</tabs>
    <tabs>standard-Dashboard</tabs>
    <uiType>Lightning</uiType>
</CustomApplication>
""")

# ---------- permission set ----------
def fp(f, e): return f'    <fieldPermissions>\n        <editable>{str(e).lower()}</editable>\n        <field>{f}</field>\n        <readable>true</readable>\n    </fieldPermissions>'
def op(o,c,e,d): return f'    <objectPermissions>\n        <allowCreate>{str(c).lower()}</allowCreate>\n        <allowDelete>{str(d).lower()}</allowDelete>\n        <allowEdit>{str(e).lower()}</allowEdit>\n        <allowRead>true</allowRead>\n        <modifyAllRecords>false</modifyAllRecords>\n        <object>{o}</object>\n        <viewAllFields>false</viewAllFields>\n        <viewAllRecords>false</viewAllRecords>\n    </objectPermissions>'

cf = ["LT_Shipment__c","LT_Driver_Involved__c","LT_Base__c","LT_Customer_Channel__c","LT_Marketplace__c",
  "LT_Root_Cause__c","LT_Resolution_Deadline__c","LT_First_Response_Date__c","LT_Forwarded_To_Driver_Date__c",
  "LT_Driver_Response_Deadline__c","LT_PNR_Flag__c","LT_Reimbursement_Value__c","LT_Driver_Penalized__c"]
rf = ["LT_Days_Open__c","LT_Is_Overdue__c","LT_First_Response_Hours__c"]
L = ['<?xml version="1.0" encoding="UTF-8"?>','<PermissionSet xmlns="http://soap.sforce.com/2006/04/metadata">']
L.append('    <description>Atendimento ao Cliente (SAC): chamados, PNR, extravios, tratativa com motoristas e ressarcimento a embarcadores.</description>')
L.append('    <hasActivationRequired>false</hasActivationRequired>')
L.append('    <label>LT - SAC</label>')
for f in cf: L.append(fp(f"Case.{f}", True))
for f in rf: L.append(fp(f"Case.{f}", False))
L.append('    <applicationVisibilities>\n        <application>LogiTrack_SAC</application>\n        <visible>true</visible>\n    </applicationVisibilities>')
L.append('    <applicationVisibilities>\n        <application>LogiTrack_Operations_360</application>\n        <visible>true</visible>\n    </applicationVisibilities>')
for rt in ["LT_Assinado_Nao_Recebido","LT_Agilizacao","LT_Avaria_Pos_Entrega","LT_Postura_Motorista","LT_PNR"]:
    L.append(f'    <recordTypeVisibilities>\n        <recordType>Case.{rt}</recordType>\n        <visible>true</visible>\n    </recordTypeVisibilities>')
L.append(op("Case", True, True, False))
L.append(op("LT_Shipment__c", False, True, False))
L.append(op("LT_Driver__c", False, False, False))
L.append(op("LT_Logistics_Unit__c", False, False, False))
L.append('</PermissionSet>')
open(os.path.join(ROOT, "permissionsets", "LT_SAC.permissionset-meta.xml"), "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")

print("SAC2: queues, assignment rules, layout, path, app, permset written")
