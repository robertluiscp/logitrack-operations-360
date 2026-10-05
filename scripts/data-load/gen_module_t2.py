#!/usr/bin/env python3
"""Modulo T (parte 2): Entitlements e Milestones de SLA no SAC.

  - Campo Case.LT_SLA_Violated__c (marcado pela violacao do milestone)
  - Workflow field update LT_Marcar_Violacao_SLA
  - 2 Milestone Types (Primeira Resposta, Resolucao)
  - Entitlement Process LT_Atendimento_SAC (1a resposta em 4h, resolucao em 72h)
  - Flow before-save que atribui o entitlement padrao a todo chamado novo
  - Lista relacionada de milestones no layout do SAC
  - Relatorio e grafico de SLA violado no painel do SAC
O Entitlement e a conta dele sao dados: ver apex em scripts/data-load (carga na org).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import metahelp as mh

ROOT = os.path.join(os.path.dirname(__file__), "..", "..", "force-app", "main", "default")
CASE = os.path.join(ROOT, "objects", "Case")


def w(path, body):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(body.rstrip() + "\n")


# --- campo
mh.ensure(CASE, ("fields",))
mh.wf(CASE, "LT_SLA_Violated__c", mh.field(
    "LT_SLA_Violated__c", "SLA Violado",
    "Marcado automaticamente quando um milestone do chamado (primeira resposta ou resolucao) estoura o prazo.",
    "Checkbox", track=True, default="false"))

# --- workflow (field update chamado pelas violacoes dos milestones)
w(os.path.join(ROOT, "workflows", "Case.workflow-meta.xml"), """<?xml version="1.0" encoding="UTF-8"?>
<Workflow xmlns="http://soap.sforce.com/2006/04/metadata">
    <fieldUpdates>
        <fullName>LT_Marcar_Violacao_SLA</fullName>
        <description>Marca o chamado como SLA violado quando um milestone estoura.</description>
        <field>LT_SLA_Violated__c</field>
        <literalValue>true</literalValue>
        <name>LT Marcar Violacao de SLA</name>
        <notifyAssignee>false</notifyAssignee>
        <operation>Literal</operation>
        <protected>false</protected>
        <reevaluateOnChange>false</reevaluateOnChange>
    </fieldUpdates>
</Workflow>""")

# --- milestone types
w(os.path.join(ROOT, "milestoneTypes", "LT_Primeira_Resposta.milestoneType-meta.xml"), """<?xml version="1.0" encoding="UTF-8"?>
<MilestoneType xmlns="http://soap.sforce.com/2006/04/metadata">
    <description>Tempo maximo para o SAC dar a primeira resposta ao cliente.</description>
    <recurrenceType>none</recurrenceType>
</MilestoneType>""")
w(os.path.join(ROOT, "milestoneTypes", "LT_Resolucao.milestoneType-meta.xml"), """<?xml version="1.0" encoding="UTF-8"?>
<MilestoneType xmlns="http://soap.sforce.com/2006/04/metadata">
    <description>Tempo maximo para resolver e fechar o chamado.</description>
    <recurrenceType>none</recurrenceType>
</MilestoneType>""")

# --- entitlement process
w(os.path.join(ROOT, "entitlementProcesses", "LT_Atendimento_SAC.entitlementProcess-meta.xml"), """<?xml version="1.0" encoding="UTF-8"?>
<EntitlementProcess xmlns="http://soap.sforce.com/2006/04/metadata">
    <SObjectType>Case</SObjectType>
    <active>true</active>
    <description>SLA do SAC LogiTrack: primeira resposta em 4h e resolucao em 72h. Violacao marca o chamado.</description>
    <entryStartDateField>Case.CreatedDate</entryStartDateField>
    <exitCriteriaFilterItems>
        <field>Case.IsClosed</field>
        <operation>equals</operation>
        <value>true</value>
    </exitCriteriaFilterItems>
    <milestones>
        <milestoneCriteriaFormula>ISBLANK(LT_First_Response_Date__c)</milestoneCriteriaFormula>
        <milestoneName>LT_Primeira_Resposta</milestoneName>
        <minutesToComplete>240</minutesToComplete>
        <timeTriggers>
            <actions>
                <name>LT_Marcar_Violacao_SLA</name>
                <type>FieldUpdate</type>
            </actions>
            <timeLength>0</timeLength>
            <workflowTimeTriggerUnit>Minutes</workflowTimeTriggerUnit>
        </timeTriggers>
        <useCriteriaStartTime>false</useCriteriaStartTime>
    </milestones>
    <milestones>
        <milestoneName>LT_Resolucao</milestoneName>
        <minutesToComplete>4320</minutesToComplete>
        <timeTriggers>
            <actions>
                <name>LT_Marcar_Violacao_SLA</name>
                <type>FieldUpdate</type>
            </actions>
            <timeLength>0</timeLength>
            <workflowTimeTriggerUnit>Minutes</workflowTimeTriggerUnit>
        </timeTriggers>
        <useCriteriaStartTime>false</useCriteriaStartTime>
    </milestones>
</EntitlementProcess>""")

# --- flow que atribui o entitlement padrao
w(os.path.join(ROOT, "flows", "LT_Case_Assign_Entitlement.flow-meta.xml"), """<?xml version="1.0" encoding="UTF-8"?>
<Flow xmlns="http://soap.sforce.com/2006/04/metadata">
    <apiVersion>62.0</apiVersion>
    <description>Antes de criar o chamado, atribui o entitlement padrao do SAC (que liga o chamado ao processo de SLA com milestones).</description>
    <environments>Default</environments>
    <interviewLabel>SAC - Atribuir Entitlement {!$Flow.CurrentDateTime}</interviewLabel>
    <label>SAC - Atribuir Entitlement Padrao</label>
    <processMetadataValues><name>BuilderType</name><value><stringValue>LightningFlowBuilder</stringValue></value></processMetadataValues>
    <processType>AutoLaunchedFlow</processType>
    <assignments>
        <name>Definir_Entitlement</name>
        <label>Definir Entitlement</label>
        <locationX>176</locationX>
        <locationY>396</locationY>
        <assignmentItems>
            <assignToReference>$Record.EntitlementId</assignToReference>
            <operator>Assign</operator>
            <value><elementReference>Buscar_Entitlement.Id</elementReference></value>
        </assignmentItems>
    </assignments>
    <decisions>
        <name>Achou_Entitlement</name>
        <label>Achou Entitlement?</label>
        <locationX>176</locationX>
        <locationY>288</locationY>
        <defaultConnectorLabel>Nao</defaultConnectorLabel>
        <rules>
            <name>Sim</name>
            <conditionLogic>and</conditionLogic>
            <conditions>
                <leftValueReference>Buscar_Entitlement</leftValueReference>
                <operator>IsNull</operator>
                <rightValue><booleanValue>false</booleanValue></rightValue>
            </conditions>
            <connector><targetReference>Definir_Entitlement</targetReference></connector>
            <label>Sim</label>
        </rules>
    </decisions>
    <recordLookups>
        <name>Buscar_Entitlement</name>
        <label>Buscar Entitlement</label>
        <locationX>176</locationX>
        <locationY>180</locationY>
        <assignNullValuesIfNoRecordsFound>false</assignNullValuesIfNoRecordsFound>
        <connector><targetReference>Achou_Entitlement</targetReference></connector>
        <filterLogic>and</filterLogic>
        <filters>
            <field>Name</field>
            <operator>EqualTo</operator>
            <value><stringValue>SAC Padrao LogiTrack</stringValue></value>
        </filters>
        <getFirstRecordOnly>true</getFirstRecordOnly>
        <object>Entitlement</object>
        <storeOutputAutomatically>true</storeOutputAutomatically>
    </recordLookups>
    <start>
        <locationX>50</locationX>
        <locationY>0</locationY>
        <connector><targetReference>Buscar_Entitlement</targetReference></connector>
        <filterLogic>and</filterLogic>
        <filters>
            <field>EntitlementId</field>
            <operator>IsNull</operator>
            <value><booleanValue>true</booleanValue></value>
        </filters>
        <object>Case</object>
        <recordTriggerType>Create</recordTriggerType>
        <triggerType>RecordBeforeSave</triggerType>
    </start>
    <status>Active</status>
</Flow>""")

# --- layout: lista relacionada de milestones
lay = os.path.join(ROOT, "layouts", "Case-LogiTrack SAC.layout-meta.xml")
txt = open(lay, encoding="utf-8").read()
if "RelatedCaseMilestoneList" not in txt and "RelatedCaseMilestoneList" not in txt:
    txt = txt.replace(
        "    <relatedLists>\n        <relatedList>RelatedHistoryList</relatedList>\n    </relatedLists>\n",
        "    <relatedLists>\n        <relatedList>RelatedCaseMilestoneList</relatedList>\n    </relatedLists>\n"
        "    <relatedLists>\n        <relatedList>RelatedHistoryList</relatedList>\n    </relatedLists>\n")
    w(lay, txt)

# --- campo no layout (secao SLA e Tratativa, coluna da direita)
txt = open(lay, encoding="utf-8").read()
if "LT_SLA_Violated__c" not in txt:
    old = ("            <layoutItems>\n                <behavior>Edit</behavior>\n"
           "                <field>LT_Reimbursement_Value__c</field>\n            </layoutItems>\n")
    assert old in txt
    txt = txt.replace(old, old + "            <layoutItems>\n                <behavior>Readonly</behavior>\n"
                      "                <field>LT_SLA_Violated__c</field>\n            </layoutItems>\n")
    w(lay, txt)

# --- FLS no LT_SAC
ps = os.path.join(ROOT, "permissionsets", "LT_SAC.permissionset-meta.xml")
ptxt = open(ps, encoding="utf-8").read()
if "Case.LT_SLA_Violated__c" not in ptxt:
    add = ("    <fieldPermissions>\n        <editable>false</editable>\n        <field>Case.LT_SLA_Violated__c</field>\n"
           "        <readable>true</readable>\n    </fieldPermissions>\n")
    idx = ptxt.rfind("</fieldPermissions>\n") + len("</fieldPermissions>\n")
    w(ps, ptxt[:idx] + add + ptxt[idx:])

# --- relatorio + grafico no painel
rdir = os.path.join(ROOT, "reports", "LT_Reports")
w(os.path.join(rdir, "LT_SAC_SLA_Violated_By_Type.report-meta.xml"), """<?xml version="1.0" encoding="UTF-8"?>
<Report xmlns="http://soap.sforce.com/2006/04/metadata">
    <chart>
        <backgroundColor1>#FFFFFF</backgroundColor1>
        <backgroundColor2>#FFFFFF</backgroundColor2>
        <backgroundFadeDir>Diagonal</backgroundFadeDir>
        <chartSummaries>
            <axisBinding>y</axisBinding>
            <column>RowCount</column>
        </chartSummaries>
        <chartType>HorizontalBar</chartType>
        <enableHoverLabels>false</enableHoverLabels>
        <expandOthers>true</expandOthers>
        <groupingColumn>RECORDTYPE</groupingColumn>
        <location>CHART_TOP</location>
        <showAxisLabels>true</showAxisLabels>
        <showPercentage>false</showPercentage>
        <showTotal>false</showTotal>
        <showValues>true</showValues>
        <size>Medium</size>
        <summaryAxisRange>Auto</summaryAxisRange>
        <textColor>#000000</textColor>
        <textSize>12</textSize>
        <title>Chamados com SLA violado por tipo</title>
        <titleColor>#000000</titleColor>
        <titleSize>18</titleSize>
    </chart>
    <columns>
        <field>CASE_NUMBER</field>
    </columns>
    <description>SAC - SLA Violado por Tipo</description>
    <filter>
        <criteriaItems>
            <column>Case.LT_SLA_Violated__c</column>
            <columnToColumn>false</columnToColumn>
            <isUnlocked>true</isUnlocked>
            <operator>equals</operator>
            <value>1</value>
        </criteriaItems>
    </filter>
    <format>Summary</format>
    <groupingsDown>
        <dateGranularity>None</dateGranularity>
        <field>RECORDTYPE</field>
        <sortOrder>Asc</sortOrder>
    </groupingsDown>
    <name>SAC - SLA Violado por Tipo</name>
    <params>
        <name>co</name>
        <value>1</value>
    </params>
    <reportType>CaseList</reportType>
    <scope>organization</scope>
    <showDetails>true</showDetails>
    <showGrandTotal>true</showGrandTotal>
    <showSubTotals>true</showSubTotals>
</Report>""")

dpath = os.path.join(ROOT, "dashboards", "LT_Operational_Dashboards", "LT_Dash_SAC.dashboard-meta.xml")
d = open(dpath, encoding="utf-8").read()
if "LT_SAC_SLA_Violated_By_Type" not in d:
    comp = """        <dashboardGridComponents>
            <colSpan>12</colSpan>
            <columnIndex>0</columnIndex>
            <dashboardComponent>
                <autoselectColumnsFromReport>true</autoselectColumnsFromReport>
                <chartAxisRange>Auto</chartAxisRange>
                <componentType>Bar</componentType>
                <displayUnits>Auto</displayUnits>
                <drillEnabled>false</drillEnabled>
                <drillToDetailEnabled>false</drillToDetailEnabled>
                <enableHover>true</enableHover>
                <expandOthers>true</expandOthers>
                <groupingSortProperties/>
                <header>SLA Violado por Tipo de Chamado (milestones)</header>
                <report>LT_Reports/LT_SAC_SLA_Violated_By_Type</report>
                <showPercentage>false</showPercentage>
                <showValues>true</showValues>
                <sortBy>RowValueDescending</sortBy>
                <sortLegendValues>true</sortLegendValues>
                <useReportChart>true</useReportChart>
            </dashboardComponent>
            <rowIndex>30</rowIndex>
            <rowSpan>8</rowSpan>
        </dashboardGridComponents>
"""
    d = d.replace("        <numberOfColumns>12</numberOfColumns>", comp + "        <numberOfColumns>12</numberOfColumns>")
    w(dpath, d)

print("Modulo T parte 2 (milestones) gerado.")
