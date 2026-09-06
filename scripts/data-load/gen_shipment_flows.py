#!/usr/bin/env python3
import os
FL = r"C:\Users\Robert Luis\Desktop\LogiTrack-SFDX\force-app\main\default\flows"
os.makedirs(FL, exist_ok=True)

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

E = "{!$Record.LT_Event_Type_Text__c}"
DT = "{!$Record.LT_Event_DateTime__c}"
UNIT = "{!$Record.LT_Unit__c}"
DRV = "{!$Record.LT_Driver__c}"

def pr(f):
    return "{!$Record.LT_Shipment__r." + f + "}"

def nested(pairs, default):
    expr = default
    for cond, val in reversed(pairs):
        expr = "IF(" + cond + ", " + val + ", " + expr + ")"
    return expr

status_expr = nested([
  (f'{E} = "Etiqueta Gerada"', '"Etiqueta Gerada"'),
  (f'{E} = "Coleta Realizada"', '"Coletado"'),
  (f'OR({E} = "Chegada ao SC", {E} = "Triagem no SC")', '"Em Triagem no SC"'),
  (f'{E} = "Saida do SC (Transferencia)"', '"Em Transferencia"'),
  (f'{E} = "Chegada a Base"', '"Recebido na Base"'),
  (f'OR({E} = "Triagem na Base", {E} = "Bipado para Rota")', '"Em Triagem na Base"'),
  (f'{E} = "Saiu para Entrega"', '"Em Rota de Entrega"'),
  (f'{E} = "Entregue"', '"Entregue"'),
  (f'OR({E} = "Tentativa de Entrega", {E} = "Destinatario Ausente", {E} = "Endereco Nao Localizado", {E} = "Recusado pelo Destinatario")', '"Tentativa de Entrega"'),
  (f'{E} = "Retido"', '"Retido"'),
  (f'{E} = "Sem Movimentacao Detectada"', '"Sem Movimentacao"'),
  (f'{E} = "Devolucao Iniciada"', '"Devolvido ao Remetente"'),
  (f'{E} = "Extravio Registrado"', '"Extraviado"'),
], pr("LT_Status_Text__c"))

holder_expr = nested([
  (f'OR({E} = "Etiqueta Gerada")', '"Ponto de Coleta"'),
  (f'{E} = "Coleta Realizada"', '"Motorista de Coleta"'),
  (f'OR({E} = "Chegada ao SC", {E} = "Triagem no SC")', '"Centro de Distribuicao"'),
  (f'{E} = "Saida do SC (Transferencia)"', '"Em Transferencia"'),
  (f'OR({E} = "Chegada a Base", {E} = "Triagem na Base", {E} = "Bipado para Rota")', '"Base de Entrega"'),
  (f'{E} = "Saiu para Entrega"', '"Motorista Last Mile"'),
  (f'OR({E} = "Tentativa de Entrega", {E} = "Destinatario Ausente", {E} = "Endereco Nao Localizado", {E} = "Recusado pelo Destinatario")', '"Motorista Last Mile"'),
  (f'{E} = "Entregue"', '"Entregue"'),
  (f'{E} = "Devolucao Iniciada"', '"Devolvido"'),
], pr("LT_Holder_Text__c"))

collected_expr = "IF(" + E + " = \"Coleta Realizada\", " + DT + ", " + pr("LT_Collected_Date__c") + ")"
delivered_expr = "IF(" + E + " = \"Entregue\", " + DT + ", " + pr("LT_Delivered_Date__c") + ")"
posted_expr = "IF(AND(" + E + " = \"Etiqueta Gerada\", ISBLANK(" + pr("LT_Posted_Date__c") + ")), " + DT + ", " + pr("LT_Posted_Date__c") + ")"
base_expr = "IF(AND(" + E + " = \"Chegada a Base\", NOT(ISBLANK(" + UNIT + "))), " + UNIT + ", " + pr("LT_Delivery_Base__c") + ")"
cd_expr = "IF(AND(" + E + " = \"Chegada ao SC\", NOT(ISBLANK(" + UNIT + "))), " + UNIT + ", " + pr("LT_Destination_CD__c") + ")"
driver_expr = "IF(AND(OR(" + E + " = \"Saiu para Entrega\", " + E + " = \"Bipado para Rota\"), NOT(ISBLANK(" + DRV + "))), " + DRV + ", " + pr("LT_Last_Mile_Driver__c") + ")"
attempts_expr = pr("LT_Delivery_Attempts__c") + " + IF(OR(" + E + " = \"Tentativa de Entrega\", " + E + " = \"Destinatario Ausente\", " + E + " = \"Endereco Nao Localizado\", " + E + " = \"Recusado pelo Destinatario\"), 1, 0)"

formulas = [
  ("fStatus", "String", status_expr),
  ("fHolder", "String", holder_expr),
  ("fCollected", "DateTime", collected_expr),
  ("fDelivered", "DateTime", delivered_expr),
  ("fPosted", "DateTime", posted_expr),
  ("fBase", "String", base_expr),
  ("fCD", "String", cd_expr),
  ("fDriver", "String", driver_expr),
  ("fAttempts", "Number", attempts_expr),
]
fx = "\n".join(f"""    <formulas>
        <name>{n}</name>
        <dataType>{dt}</dataType>
        <expression>{esc(expr)}</expression>{'' if dt != 'Number' else '<scale>0</scale>'}
    </formulas>""" for n, dt, expr in formulas)

flow = f"""<?xml version="1.0" encoding="UTF-8"?>
<Flow xmlns="http://soap.sforce.com/2006/04/metadata">
    <apiVersion>62.0</apiVersion>
    <description>Ao criar um evento de rastreamento, atualiza o status, o responsavel atual, as datas e a roteirizacao da remessa correspondente.</description>
    <environments>Default</environments>
    <interviewLabel>RMS - Evento atualiza a Remessa {{!$Flow.CurrentDateTime}}</interviewLabel>
    <label>RMS - Evento de Rastreamento atualiza a Remessa</label>
    <processMetadataValues>
        <name>BuilderType</name>
        <value><stringValue>LightningFlowBuilder</stringValue></value>
    </processMetadataValues>
    <processType>AutoLaunchedFlow</processType>
{fx}
    <recordUpdates>
        <name>Atualizar_Remessa</name>
        <label>Atualizar Remessa</label>
        <locationX>176</locationX>
        <locationY>288</locationY>
        <inputAssignments>
            <field>LT_Status__c</field>
            <value><elementReference>fStatus</elementReference></value>
        </inputAssignments>
        <inputAssignments>
            <field>LT_Current_Holder__c</field>
            <value><elementReference>fHolder</elementReference></value>
        </inputAssignments>
        <inputAssignments>
            <field>LT_Collected_Date__c</field>
            <value><elementReference>fCollected</elementReference></value>
        </inputAssignments>
        <inputAssignments>
            <field>LT_Delivered_Date__c</field>
            <value><elementReference>fDelivered</elementReference></value>
        </inputAssignments>
        <inputAssignments>
            <field>LT_Posted_Date__c</field>
            <value><elementReference>fPosted</elementReference></value>
        </inputAssignments>
        <inputAssignments>
            <field>LT_Delivery_Base__c</field>
            <value><elementReference>fBase</elementReference></value>
        </inputAssignments>
        <inputAssignments>
            <field>LT_Destination_CD__c</field>
            <value><elementReference>fCD</elementReference></value>
        </inputAssignments>
        <inputAssignments>
            <field>LT_Last_Mile_Driver__c</field>
            <value><elementReference>fDriver</elementReference></value>
        </inputAssignments>
        <inputAssignments>
            <field>LT_Delivery_Attempts__c</field>
            <value><elementReference>fAttempts</elementReference></value>
        </inputAssignments>
        <inputReference>$Record.LT_Shipment__r</inputReference>
    </recordUpdates>
    <start>
        <locationX>50</locationX>
        <locationY>0</locationY>
        <connector><targetReference>Atualizar_Remessa</targetReference></connector>
        <object>LT_Tracking_Event__c</object>
        <recordTriggerType>Create</recordTriggerType>
        <triggerType>RecordAfterSave</triggerType>
    </start>
    <status>Active</status>
</Flow>
"""
open(os.path.join(FL, "LT_Shipment_Event_Updates_Status.flow-meta.xml"), "w", encoding="utf-8", newline="\n").write(flow)

# ---- scheduled: no-movement detector ----
nomove = """<?xml version="1.0" encoding="UTF-8"?>
<Flow xmlns="http://soap.sforce.com/2006/04/metadata">
    <apiVersion>62.0</apiVersion>
    <description>Fluxo agendado diario: remessas nao finalizadas sem evento ha mais de 6 horas passam para Sem Movimentacao e ganham um evento de rastreamento.</description>
    <environments>Default</environments>
    <interviewLabel>RMS - Detectar Sem Movimentacao {!$Flow.CurrentDateTime}</interviewLabel>
    <label>RMS - Detectar Remessas Sem Movimentacao</label>
    <processMetadataValues>
        <name>BuilderType</name>
        <value><stringValue>LightningFlowBuilder</stringValue></value>
    </processMetadataValues>
    <processType>AutoLaunchedFlow</processType>
    <recordCreates>
        <name>Registrar_Evento_Sem_Movimentacao</name>
        <label>Registrar Evento Sem Movimentacao</label>
        <locationX>176</locationX>
        <locationY>396</locationY>
        <inputAssignments>
            <field>LT_Shipment__c</field>
            <value><elementReference>$Record.Id</elementReference></value>
        </inputAssignments>
        <inputAssignments>
            <field>LT_Event_Type__c</field>
            <value><stringValue>Sem Movimentacao Detectada</stringValue></value>
        </inputAssignments>
        <inputAssignments>
            <field>LT_Event_DateTime__c</field>
            <value><elementReference>$Flow.CurrentDateTime</elementReference></value>
        </inputAssignments>
        <inputAssignments>
            <field>LT_Notes__c</field>
            <value><stringValue>Remessa sem atualizacao sistemica ha mais de 6 horas - sinalizada automaticamente.</stringValue></value>
        </inputAssignments>
        <object>LT_Tracking_Event__c</object>
        <storeOutputAutomatically>true</storeOutputAutomatically>
    </recordCreates>
    <recordUpdates>
        <name>Marcar_Sem_Movimentacao</name>
        <label>Marcar Sem Movimentacao</label>
        <locationX>176</locationX>
        <locationY>288</locationY>
        <connector><targetReference>Registrar_Evento_Sem_Movimentacao</targetReference></connector>
        <inputAssignments>
            <field>LT_Status__c</field>
            <value><stringValue>Sem Movimentacao</stringValue></value>
        </inputAssignments>
        <inputReference>$Record</inputReference>
    </recordUpdates>
    <start>
        <locationX>50</locationX>
        <locationY>0</locationY>
        <connector><targetReference>Marcar_Sem_Movimentacao</targetReference></connector>
        <filterLogic>and</filterLogic>
        <filters>
            <field>LT_Is_Terminal__c</field>
            <operator>EqualTo</operator>
            <value><booleanValue>false</booleanValue></value>
        </filters>
        <filters>
            <field>LT_Hours_Without_Movement__c</field>
            <operator>GreaterThanOrEqualTo</operator>
            <value><numberValue>6.0</numberValue></value>
        </filters>
        <filters>
            <field>LT_Status__c</field>
            <operator>NotEqualTo</operator>
            <value><stringValue>Sem Movimentacao</stringValue></value>
        </filters>
        <object>LT_Shipment__c</object>
        <schedule>
            <frequency>Daily</frequency>
            <startDate>2026-09-07</startDate>
            <startTime>05:00:00.000Z</startTime>
        </schedule>
        <triggerType>Scheduled</triggerType>
    </start>
    <status>Active</status>
</Flow>
"""
open(os.path.join(FL, "LT_Shipment_Detect_No_Movement.flow-meta.xml"), "w", encoding="utf-8", newline="\n").write(nomove)

# ---- scheduled: retained detector ----
retained = """<?xml version="1.0" encoding="UTF-8"?>
<Flow xmlns="http://soap.sforce.com/2006/04/metadata">
    <apiVersion>62.0</apiVersion>
    <description>Fluxo agendado diario: remessas nao entregues que passaram do prazo de SLA entram no status Retido.</description>
    <environments>Default</environments>
    <interviewLabel>RMS - Detectar Retidos {!$Flow.CurrentDateTime}</interviewLabel>
    <label>RMS - Detectar Remessas Retidas</label>
    <processMetadataValues>
        <name>BuilderType</name>
        <value><stringValue>LightningFlowBuilder</stringValue></value>
    </processMetadataValues>
    <processType>AutoLaunchedFlow</processType>
    <recordCreates>
        <name>Registrar_Evento_Retido</name>
        <label>Registrar Evento Retido</label>
        <locationX>176</locationX>
        <locationY>396</locationY>
        <inputAssignments>
            <field>LT_Shipment__c</field>
            <value><elementReference>$Record.Id</elementReference></value>
        </inputAssignments>
        <inputAssignments>
            <field>LT_Event_Type__c</field>
            <value><stringValue>Retido</stringValue></value>
        </inputAssignments>
        <inputAssignments>
            <field>LT_Event_DateTime__c</field>
            <value><elementReference>$Flow.CurrentDateTime</elementReference></value>
        </inputAssignments>
        <inputAssignments>
            <field>LT_Notes__c</field>
            <value><stringValue>Remessa passou do prazo de entrega (SLA) sem ser entregue - marcada como Retida.</stringValue></value>
        </inputAssignments>
        <object>LT_Tracking_Event__c</object>
        <storeOutputAutomatically>true</storeOutputAutomatically>
    </recordCreates>
    <recordUpdates>
        <name>Marcar_Retido</name>
        <label>Marcar Retido</label>
        <locationX>176</locationX>
        <locationY>288</locationY>
        <connector><targetReference>Registrar_Evento_Retido</targetReference></connector>
        <inputAssignments>
            <field>LT_Status__c</field>
            <value><stringValue>Retido</stringValue></value>
        </inputAssignments>
        <inputReference>$Record</inputReference>
    </recordUpdates>
    <start>
        <locationX>50</locationX>
        <locationY>0</locationY>
        <connector><targetReference>Marcar_Retido</targetReference></connector>
        <filterLogic>and</filterLogic>
        <filters>
            <field>LT_Is_Late__c</field>
            <operator>EqualTo</operator>
            <value><booleanValue>true</booleanValue></value>
        </filters>
        <filters>
            <field>LT_Is_Terminal__c</field>
            <operator>EqualTo</operator>
            <value><booleanValue>false</booleanValue></value>
        </filters>
        <filters>
            <field>LT_Status__c</field>
            <operator>NotEqualTo</operator>
            <value><stringValue>Retido</stringValue></value>
        </filters>
        <object>LT_Shipment__c</object>
        <schedule>
            <frequency>Daily</frequency>
            <startDate>2026-09-07</startDate>
            <startTime>04:30:00.000Z</startTime>
        </schedule>
        <triggerType>Scheduled</triggerType>
    </start>
    <status>Active</status>
</Flow>
"""
open(os.path.join(FL, "LT_Shipment_Detect_Retained.flow-meta.xml"), "w", encoding="utf-8", newline="\n").write(retained)

print("3 shipment flows written")
