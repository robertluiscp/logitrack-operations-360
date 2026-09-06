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

pick_edit = ["LT_Pickup_Type__c", "LT_Status__c", "LT_Shipper__c", "LT_Pickup_Point__c",
  "LT_First_Mile_Driver__c", "LT_Origin_Base__c", "LT_Destination_CD__c", "LT_Manifest__c",
  "LT_Requested_By__c", "LT_Pickup_Address__c", "LT_Pickup_City__c", "LT_Pickup_State__c",
  "LT_Scheduled_Date__c", "LT_Window_Start__c", "LT_Window_End__c", "LT_Estimated_Packages__c",
  "LT_Collected_Packages__c", "LT_Completed_DateTime__c", "LT_C2C_Sender_Name__c",
  "LT_C2C_Recipient_Name__c", "LT_C2C_Dest_City__c", "LT_Notes__c"]
man_edit = ["LT_Manifest_Type__c", "LT_Origin_Unit__c", "LT_Destination_Unit__c", "LT_Distance_Km__c",
  "LT_Bonus_Adjustment__c", "LT_Payment_Status__c", "LT_Approved_By__c", "LT_Payment_Date__c", "LT_Notes__c"]
man_read = ["LT_Total_Packages__c", "LT_Line_Count__c", "LT_Gross_Amount__c", "LT_Net_Amount__c", "LT_Driver_Category__c"]
line_edit = ["LT_Pickup_Request__c", "LT_Shipment__c", "LT_Collection_City__c", "LT_Description__c"]

L = ['<?xml version="1.0" encoding="UTF-8"?>', '<PermissionSet xmlns="http://soap.sforce.com/2006/04/metadata">']
L.append('    <description>Coletas First Mile e romaneios de pagamento de motoristas de coleta e mini transferencia.</description>')
L.append('    <hasActivationRequired>false</hasActivationRequired>')
L.append('    <label>LT - Coletas e Romaneios</label>')
for f in pick_edit: L.append(fp(f"LT_Pickup_Request__c.{f}", True))
for f in pick_edit[:1]: pass
L.append(fp("LT_Pickup_Request__c.LT_Fill_Rate__c", False))
for f in man_edit: L.append(fp(f"LT_Manifest__c.{f}", True))
for f in man_read: L.append(fp(f"LT_Manifest__c.{f}", False))
for f in line_edit: L.append(fp(f"LT_Manifest_Line__c.{f}", True))
L.append("""    <applicationVisibilities>
        <application>LogiTrack_Operations_360</application>
        <visible>true</visible>
    </applicationVisibilities>""")
L.append(op("LT_Pickup_Request__c", True, True, True))
L.append(op("LT_Manifest__c", True, True, True))
L.append(op("LT_Manifest_Line__c", True, True, True))
L.append(op("LT_Driver__c", False, False, False))
L.append(op("LT_Logistics_Unit__c", False, False, False))
L.append(op("Account", False, False, False))
for t in ["LT_Pickup_Request__c", "LT_Manifest__c", "LT_Manifest_Line__c"]:
    L.append(tab(t))
L.append('</PermissionSet>')
open(os.path.join(ROOT, "permissionsets", "LT_Collections.permissionset-meta.xml"), "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")

# app update
p = os.path.join(ROOT, "applications", "LogiTrack_Operations_360.app-meta.xml")
t = open(p, encoding="utf-8").read()
if "<tabs>LT_Pickup_Request__c</tabs>" not in t:
    t = t.replace("    <tabs>LT_Vehicle__c</tabs>\n",
                  "    <tabs>LT_Vehicle__c</tabs>\n    <tabs>LT_Pickup_Request__c</tabs>\n    <tabs>LT_Manifest__c</tabs>\n")
open(p, "w", encoding="utf-8", newline="\n").write(t)

# Path for pickup
open(os.path.join(ROOT, "pathAssistants", "LT_Pickup_Request_Path.pathAssistant-meta.xml"), "w", encoding="utf-8", newline="\n").write(
"""<?xml version="1.0" encoding="UTF-8"?>
<PathAssistant xmlns="http://soap.sforce.com/2006/04/metadata">
    <active>true</active>
    <entityName>LT_Pickup_Request__c</entityName>
    <fieldName>LT_Status__c</fieldName>
    <masterLabel>Fluxo da Coleta</masterLabel>
    <recordTypeName>__MASTER__</recordTypeName>
    <pathAssistantSteps>
        <fieldNames>LT_Pickup_Type__c</fieldNames>
        <fieldNames>LT_Estimated_Packages__c</fieldNames>
        <info>&lt;p&gt;Coleta solicitada pelo embarcador ou ponto DropOff. Confirme o tipo e o volume estimado.&lt;/p&gt;</info>
        <picklistValueName>Solicitada</picklistValueName>
    </pathAssistantSteps>
    <pathAssistantSteps>
        <fieldNames>LT_First_Mile_Driver__c</fieldNames>
        <fieldNames>LT_Scheduled_Date__c</fieldNames>
        <info>&lt;p&gt;Coleta agendada. Atribua o motorista First Mile e a data.&lt;/p&gt;</info>
        <picklistValueName>Agendada</picklistValueName>
    </pathAssistantSteps>
    <pathAssistantSteps>
        <info>&lt;p&gt;Motorista a caminho do endereco de coleta.&lt;/p&gt;</info>
        <picklistValueName>Motorista a Caminho</picklistValueName>
    </pathAssistantSteps>
    <pathAssistantSteps>
        <fieldNames>LT_Collected_Packages__c</fieldNames>
        <fieldNames>LT_Completed_DateTime__c</fieldNames>
        <info>&lt;p&gt;Coleta realizada. Registre a quantidade coletada e consolide no romaneio do motorista.&lt;/p&gt;</info>
        <picklistValueName>Coletada</picklistValueName>
    </pathAssistantSteps>
    <pathAssistantSteps>
        <info>&lt;p&gt;Coleta nao realizada (endereco fechado, sem volume, etc.).&lt;/p&gt;</info>
        <picklistValueName>Nao Realizada</picklistValueName>
    </pathAssistantSteps>
    <pathAssistantSteps>
        <info>&lt;p&gt;Coleta cancelada pelo solicitante.&lt;/p&gt;</info>
        <picklistValueName>Cancelada</picklistValueName>
    </pathAssistantSteps>
</PathAssistant>
""")

# before-save flow: stamp payment date on Pago
open(os.path.join(ROOT, "flows", "LT_Manifest_Stamp_Payment_Date.flow-meta.xml"), "w", encoding="utf-8", newline="\n").write(
"""<?xml version="1.0" encoding="UTF-8"?>
<Flow xmlns="http://soap.sforce.com/2006/04/metadata">
    <apiVersion>62.0</apiVersion>
    <description>Antes do salvamento, se o romaneio passou para Pago sem data de pagamento, preenche com a data de hoje.</description>
    <environments>Default</environments>
    <interviewLabel>RMN - Carimbar Data de Pagamento {!$Flow.CurrentDateTime}</interviewLabel>
    <label>RMN - Carimbar Data de Pagamento</label>
    <processMetadataValues>
        <name>BuilderType</name>
        <value><stringValue>LightningFlowBuilder</stringValue></value>
    </processMetadataValues>
    <processType>AutoLaunchedFlow</processType>
    <assignments>
        <name>Definir_Data_Pagamento</name>
        <label>Definir Data de Pagamento</label>
        <locationX>176</locationX>
        <locationY>288</locationY>
        <assignmentItems>
            <assignToReference>$Record.LT_Payment_Date__c</assignToReference>
            <operator>Assign</operator>
            <value><elementReference>$Flow.CurrentDate</elementReference></value>
        </assignmentItems>
    </assignments>
    <start>
        <locationX>50</locationX>
        <locationY>0</locationY>
        <connector><targetReference>Definir_Data_Pagamento</targetReference></connector>
        <filterLogic>and</filterLogic>
        <filters>
            <field>LT_Payment_Status__c</field>
            <operator>EqualTo</operator>
            <value><stringValue>Pago</stringValue></value>
        </filters>
        <filters>
            <field>LT_Payment_Date__c</field>
            <operator>IsNull</operator>
            <value><booleanValue>true</booleanValue></value>
        </filters>
        <object>LT_Manifest__c</object>
        <recordTriggerType>CreateAndUpdate</recordTriggerType>
        <triggerType>RecordBeforeSave</triggerType>
    </start>
    <status>Active</status>
</Flow>
""")

print("E security + app + path + flow written")
