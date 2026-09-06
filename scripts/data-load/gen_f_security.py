#!/usr/bin/env python3
import os
ROOT = r"C:\Users\Robert Luis\Desktop\LogiTrack-SFDX\force-app\main\default"

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
def tab(t):
    return f"""    <tabSettings>
        <tab>{t}</tab>
        <visibility>Visible</visibility>
    </tabSettings>"""

route_e = ["LT_Route_Type__c", "LT_Status__c", "LT_Driver__c", "LT_Vehicle__c", "LT_Target_City__c",
  "LT_Destination_Unit__c", "LT_Cage_Code__c", "LT_Distance_Km__c", "LT_Planned_Packages__c",
  "LT_Loaded_Packages__c", "LT_Departure_Time__c", "LT_Return_Time__c", "LT_Notes__c"]
route_r = ["LT_Attempts_Count__c", "LT_Delivered_Count__c", "LT_Success_Rate__c", "LT_MR_Eligible__c", "LT_Driver_Max_Packages__c"]
att_e = ["LT_Driver__c", "LT_Attempt_Number__c", "LT_Result__c", "LT_Recipient_Doc__c",
  "LT_Recipient_Relationship__c", "LT_Geolocation__c", "LT_Photo_Link__c", "LT_Notes__c"]

L = ['<?xml version="1.0" encoding="UTF-8"?>', '<PermissionSet xmlns="http://soap.sforce.com/2006/04/metadata">']
L.append('    <description>Ultima milha: montagem de rotas de entrega e mini transferencia e registro de tentativas de entrega.</description>')
L.append('    <hasActivationRequired>false</hasActivationRequired>')
L.append('    <label>LT - Rotas e Entregas</label>')
for f in route_e: L.append(fp(f"LT_Route__c.{f}", True))
for f in route_r: L.append(fp(f"LT_Route__c.{f}", False))
for f in att_e: L.append(fp(f"LT_Delivery_Attempt__c.{f}", True))
L.append(fp("LT_Delivery_Attempt__c.LT_Attempt_DateTime__c", True))
L.append(fp("LT_Delivery_Attempt__c.LT_Is_Success__c", False))
L.append("""    <applicationVisibilities>
        <application>LogiTrack_Operations_360</application>
        <visible>true</visible>
    </applicationVisibilities>""")
L.append(op("LT_Route__c", True, True, True))
L.append(op("LT_Delivery_Attempt__c", True, True, True))
L.append(op("LT_Shipment__c", False, True, False))
L.append(op("LT_Driver__c", False, False, False))
L.append(op("LT_Logistics_Unit__c", False, False, False))
for t in ["LT_Route__c", "LT_Delivery_Attempt__c"]:
    L.append(tab(t))
L.append('</PermissionSet>')
open(os.path.join(ROOT, "permissionsets", "LT_Routes_Deliveries.permissionset-meta.xml"), "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")

# app
p = os.path.join(ROOT, "applications", "LogiTrack_Operations_360.app-meta.xml")
t = open(p, encoding="utf-8").read()
if "<tabs>LT_Route__c</tabs>" not in t:
    t = t.replace("    <tabs>LT_Manifest__c</tabs>\n",
                  "    <tabs>LT_Manifest__c</tabs>\n    <tabs>LT_Route__c</tabs>\n    <tabs>LT_Delivery_Attempt__c</tabs>\n")
open(p, "w", encoding="utf-8", newline="\n").write(t)

# path
open(os.path.join(ROOT, "pathAssistants", "LT_Route_Path.pathAssistant-meta.xml"), "w", encoding="utf-8", newline="\n").write(
"""<?xml version="1.0" encoding="UTF-8"?>
<PathAssistant xmlns="http://soap.sforce.com/2006/04/metadata">
    <active>true</active>
    <entityName>LT_Route__c</entityName>
    <fieldName>LT_Status__c</fieldName>
    <masterLabel>Fluxo da Rota</masterLabel>
    <recordTypeName>__MASTER__</recordTypeName>
    <pathAssistantSteps>
        <fieldNames>LT_Planned_Packages__c</fieldNames>
        <fieldNames>LT_Target_City__c</fieldNames>
        <info>&lt;p&gt;Rota planejada a partir da triagem da base: cidade alvo e volume previsto.&lt;/p&gt;</info>
        <picklistValueName>Planejada</picklistValueName>
    </pathAssistantSteps>
    <pathAssistantSteps>
        <fieldNames>LT_Cage_Code__c</fieldNames>
        <info>&lt;p&gt;Pacotes sendo alocados na gaiola da rota.&lt;/p&gt;</info>
        <picklistValueName>Em Triagem</picklistValueName>
    </pathAssistantSteps>
    <pathAssistantSteps>
        <fieldNames>LT_Driver__c</fieldNames>
        <fieldNames>LT_Loaded_Packages__c</fieldNames>
        <fieldNames>LT_Vehicle__c</fieldNames>
        <info>&lt;p&gt;Motorista bipou os pacotes. Confira a carga contra o limite da categoria.&lt;/p&gt;</info>
        <picklistValueName>Carregada</picklistValueName>
    </pathAssistantSteps>
    <pathAssistantSteps>
        <fieldNames>LT_Departure_Time__c</fieldNames>
        <info>&lt;p&gt;Motorista saiu para entrega. Acompanhe as tentativas em tempo real.&lt;/p&gt;</info>
        <picklistValueName>Em Rota</picklistValueName>
    </pathAssistantSteps>
    <pathAssistantSteps>
        <fieldNames>LT_Return_Time__c</fieldNames>
        <info>&lt;p&gt;Rota concluida. Pacotes nao entregues retornam a base como retidos.&lt;/p&gt;</info>
        <picklistValueName>Concluida</picklistValueName>
    </pathAssistantSteps>
    <pathAssistantSteps>
        <info>&lt;p&gt;Rota cancelada.&lt;/p&gt;</info>
        <picklistValueName>Cancelada</picklistValueName>
    </pathAssistantSteps>
</PathAssistant>
""")

# record-triggered flow: delivery attempt creates tracking event
open(os.path.join(ROOT, "flows", "LT_Delivery_Attempt_Creates_Event.flow-meta.xml"), "w", encoding="utf-8", newline="\n").write(
"""<?xml version="1.0" encoding="UTF-8"?>
<Flow xmlns="http://soap.sforce.com/2006/04/metadata">
    <apiVersion>62.0</apiVersion>
    <description>Ao registrar uma tentativa de entrega, cria o evento de rastreamento correspondente na remessa (Entregue ou Tentativa de Entrega), mantendo o historico consistente.</description>
    <environments>Default</environments>
    <interviewLabel>TE - Tentativa gera Evento {!$Flow.CurrentDateTime}</interviewLabel>
    <label>TE - Tentativa de Entrega gera Evento de Rastreamento</label>
    <processMetadataValues>
        <name>BuilderType</name>
        <value><stringValue>LightningFlowBuilder</stringValue></value>
    </processMetadataValues>
    <processType>AutoLaunchedFlow</processType>
    <formulas>
        <name>fEventType</name>
        <dataType>String</dataType>
        <expression>IF(ISPICKVAL({!$Record.LT_Result__c}, "Entregue"), "Entregue", IF(ISPICKVAL({!$Record.LT_Result__c}, "Avaria Identificada"), "Avaria Identificada", IF(ISPICKVAL({!$Record.LT_Result__c}, "Recusado pelo Destinatario"), "Recusado pelo Destinatario", IF(ISPICKVAL({!$Record.LT_Result__c}, "Endereco Nao Localizado"), "Endereco Nao Localizado", IF(ISPICKVAL({!$Record.LT_Result__c}, "Destinatario Ausente"), "Destinatario Ausente", "Tentativa de Entrega")))))</expression>
    </formulas>
    <recordCreates>
        <name>Criar_Evento_de_Rastreamento</name>
        <label>Criar Evento de Rastreamento</label>
        <locationX>176</locationX>
        <locationY>288</locationY>
        <inputAssignments>
            <field>LT_Shipment__c</field>
            <value><elementReference>$Record.LT_Shipment__c</elementReference></value>
        </inputAssignments>
        <inputAssignments>
            <field>LT_Event_Type__c</field>
            <value><elementReference>fEventType</elementReference></value>
        </inputAssignments>
        <inputAssignments>
            <field>LT_Event_DateTime__c</field>
            <value><elementReference>$Record.LT_Attempt_DateTime__c</elementReference></value>
        </inputAssignments>
        <inputAssignments>
            <field>LT_Driver__c</field>
            <value><elementReference>$Record.LT_Driver__c</elementReference></value>
        </inputAssignments>
        <inputAssignments>
            <field>LT_Notes__c</field>
            <value><elementReference>$Record.LT_Notes__c</elementReference></value>
        </inputAssignments>
        <object>LT_Tracking_Event__c</object>
        <storeOutputAutomatically>true</storeOutputAutomatically>
    </recordCreates>
    <start>
        <locationX>50</locationX>
        <locationY>0</locationY>
        <connector><targetReference>Criar_Evento_de_Rastreamento</targetReference></connector>
        <object>LT_Delivery_Attempt__c</object>
        <recordTriggerType>Create</recordTriggerType>
        <triggerType>RecordAfterSave</triggerType>
    </start>
    <status>Active</status>
</Flow>
""")

print("F security + app + path + flow written")
