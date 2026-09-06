#!/usr/bin/env python3
import os
ROOT = r"C:\Users\Robert Luis\Desktop\LogiTrack-SFDX\force-app\main\default"

# queue
os.makedirs(os.path.join(ROOT, "queues"), exist_ok=True)
open(os.path.join(ROOT, "queues", "Ocorrencias_Operacionais.queue-meta.xml"), "w", encoding="utf-8", newline="\n").write(
"""<?xml version="1.0" encoding="UTF-8"?>
<Queue xmlns="http://soap.sforce.com/2006/04/metadata">
    <name>Ocorrencias Operacionais</name>
    <doesSendEmailToMembers>false</doesSendEmailToMembers>
    <queueSobject>
        <sobjectType>LT_Operational_Incident__c</sobjectType>
    </queueSobject>
</Queue>
""")

# permission set
def fp(f, e):
    return f"""    <fieldPermissions>
        <editable>{str(e).lower()}</editable>
        <field>{f}</field>
        <readable>true</readable>
    </fieldPermissions>"""
def op(o, c, e, d):
    return f"""    <objectPermissions>
        <allowCreate>{str(c).lower()}</allowCreate>
        <allowDelete>{str(d).lower()}</allowDelete>
        <allowEdit>{str(e).lower()}</allowEdit>
        <allowRead>true</allowRead>
        <modifyAllRecords>false</modifyAllRecords>
        <object>{o}</object>
        <viewAllFields>false</viewAllFields>
        <viewAllRecords>false</viewAllRecords>
    </objectPermissions>"""

edit = ["LT_Incident_Type__c", "LT_Status__c", "LT_Priority__c", "LT_Owner_Unit__c",
  "LT_Responsible_Driver__c", "LT_Assigned_To__c", "LT_Resolution_Deadline__c", "LT_Resolved_Date__c",
  "LT_Resolution_Type__c", "LT_Root_Cause__c", "LT_Escalated__c", "LT_Escalation_Date__c",
  "LT_Description__c", "LT_Resolution_Notes__c"]
read = ["LT_Days_Open__c", "LT_Is_Open__c", "LT_Is_Overdue__c", "LT_Aging_Bucket__c"]

L = ['<?xml version="1.0" encoding="UTF-8"?>', '<PermissionSet xmlns="http://soap.sforce.com/2006/04/metadata">']
L.append('    <description>Tratamento de ocorrencias operacionais (retidos, sem movimentacao, avarias) com SLA e escalonamento.</description>')
L.append('    <hasActivationRequired>false</hasActivationRequired>')
L.append('    <label>LT - Ocorrencias Operacionais</label>')
for f in edit: L.append(fp(f"LT_Operational_Incident__c.{f}", True))
for f in read: L.append(fp(f"LT_Operational_Incident__c.{f}", False))
L.append("""    <applicationVisibilities>
        <application>LogiTrack_Operations_360</application>
        <visible>true</visible>
    </applicationVisibilities>""")
L.append(op("LT_Operational_Incident__c", True, True, True))
L.append(op("LT_Shipment__c", False, True, False))
L.append(op("LT_Driver__c", False, False, False))
L.append(op("LT_Logistics_Unit__c", False, False, False))
L.append("""    <tabSettings>
        <tab>LT_Operational_Incident__c</tab>
        <visibility>Visible</visibility>
    </tabSettings>""")
L.append('</PermissionSet>')
open(os.path.join(ROOT, "permissionsets", "LT_Incidents.permissionset-meta.xml"), "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")

# app
p = os.path.join(ROOT, "applications", "LogiTrack_Operations_360.app-meta.xml")
t = open(p, encoding="utf-8").read()
if "<tabs>LT_Operational_Incident__c</tabs>" not in t:
    t = t.replace("    <tabs>LT_Delivery_Attempt__c</tabs>\n",
                  "    <tabs>LT_Delivery_Attempt__c</tabs>\n    <tabs>LT_Operational_Incident__c</tabs>\n")
open(p, "w", encoding="utf-8", newline="\n").write(t)

# path
open(os.path.join(ROOT, "pathAssistants", "LT_Incident_Path.pathAssistant-meta.xml"), "w", encoding="utf-8", newline="\n").write(
"""<?xml version="1.0" encoding="UTF-8"?>
<PathAssistant xmlns="http://soap.sforce.com/2006/04/metadata">
    <active>true</active>
    <entityName>LT_Operational_Incident__c</entityName>
    <fieldName>LT_Status__c</fieldName>
    <masterLabel>Tratamento da Ocorrencia</masterLabel>
    <recordTypeName>__MASTER__</recordTypeName>
    <pathAssistantSteps>
        <fieldNames>LT_Incident_Type__c</fieldNames>
        <fieldNames>LT_Priority__c</fieldNames>
        <info>&lt;p&gt;Ocorrencia aberta. Classifique o tipo e a prioridade; o prazo de SLA e calculado automaticamente.&lt;/p&gt;</info>
        <picklistValueName>Aberta</picklistValueName>
    </pathAssistantSteps>
    <pathAssistantSteps>
        <fieldNames>LT_Assigned_To__c</fieldNames>
        <info>&lt;p&gt;Ocorrencia atribuida a um responsavel que esta em contato com base/motorista/cliente.&lt;/p&gt;</info>
        <picklistValueName>Em Tratamento</picklistValueName>
    </pathAssistantSteps>
    <pathAssistantSteps>
        <info>&lt;p&gt;Aguardando retorno de terceiro (cliente, transportadora parceira, area interna).&lt;/p&gt;</info>
        <picklistValueName>Aguardando Terceiro</picklistValueName>
    </pathAssistantSteps>
    <pathAssistantSteps>
        <fieldNames>LT_Escalation_Date__c</fieldNames>
        <info>&lt;p&gt;Ocorrencia escalada a coordenacao (SLA estourado ou +10 dias em aberto).&lt;/p&gt;</info>
        <picklistValueName>Escalada</picklistValueName>
    </pathAssistantSteps>
    <pathAssistantSteps>
        <fieldNames>LT_Resolution_Type__c</fieldNames>
        <fieldNames>LT_Root_Cause__c</fieldNames>
        <fieldNames>LT_Resolution_Notes__c</fieldNames>
        <info>&lt;p&gt;Ocorrencia resolvida. Registre o tipo de resolucao, a causa raiz e o que foi feito.&lt;/p&gt;</info>
        <picklistValueName>Resolvida</picklistValueName>
    </pathAssistantSteps>
    <pathAssistantSteps>
        <info>&lt;p&gt;Ocorrencia cancelada (aberta por engano ou duplicada).&lt;/p&gt;</info>
        <picklistValueName>Cancelada</picklistValueName>
    </pathAssistantSteps>
</PathAssistant>
""")

print("G queue + permset + app + path written")
