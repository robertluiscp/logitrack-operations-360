#!/usr/bin/env python3
"""Modulo T: Service Cloud em profundidade (suporte ao cliente).

  T1  CSAT: 3 campos no Case + 2 validacoes + flow que cria tarefa de coleta
      de CSAT quando o chamado e fechado + secao no layout + FLS no LT_SAC.
  T2  Relatorios de Case (volume, tipo, fila, atraso, 1a resposta, CSAT) e o
      painel LT_Dash_SAC (metricas + graficos).

Entitlements/Milestones ficam em gen_module_t2.py.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import metahelp as mh

ROOT = os.path.join(os.path.dirname(__file__), "..", "..", "force-app", "main", "default")
CASE = os.path.join(ROOT, "objects", "Case")
RDIR = os.path.join(ROOT, "reports", "LT_Reports")
DDIR = os.path.join(ROOT, "dashboards", "LT_Operational_Dashboards")
FLOWS = os.path.join(ROOT, "flows")


def w(path, body):
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(body.rstrip() + "\n")


# ============================================================ T1 · CSAT
mh.ensure(CASE, ("fields", "validationRules"))

mh.wf(CASE, "LT_CSAT_Score__c", mh.field(
    "LT_CSAT_Score__c", "Nota CSAT",
    "Nota de satisfacao do cliente com o atendimento (1 a 5), registrada ao fechar o chamado.",
    "Number", precision=1, scale=0, help="Nota de 1 (muito insatisfeito) a 5 (muito satisfeito)."))
mh.wf(CASE, "LT_CSAT_Comment__c", mh.field(
    "LT_CSAT_Comment__c", "Comentario CSAT",
    "Comentario livre do cliente sobre o atendimento.", "Text", length=255, track=False))
mh.wf(CASE, "LT_CSAT_Date__c", mh.field(
    "LT_CSAT_Date__c", "Data da Pesquisa CSAT",
    "Data em que a nota CSAT foi coletada.", "Date", track=False))

mh.wv(CASE, "LT_CSAT_Score_Range",
      "A nota CSAT deve ficar entre 1 e 5.",
      "AND(NOT(ISBLANK(LT_CSAT_Score__c)), OR(LT_CSAT_Score__c &lt; 1, LT_CSAT_Score__c &gt; 5))",
      "A nota CSAT deve ser um numero de 1 a 5.", field="LT_CSAT_Score__c")
mh.wv(CASE, "LT_CSAT_Only_When_Closed",
      "CSAT so pode ser registrado depois que o chamado for fechado.",
      "AND(NOT(ISBLANK(LT_CSAT_Score__c)), NOT(IsClosed))",
      "Registre a nota CSAT somente depois de fechar o chamado.", field="LT_CSAT_Score__c")

w(os.path.join(FLOWS, "LT_Case_Request_CSAT.flow-meta.xml"), """<?xml version="1.0" encoding="UTF-8"?>
<Flow xmlns="http://soap.sforce.com/2006/04/metadata">
    <apiVersion>62.0</apiVersion>
    <description>Quando um chamado passa a Fechado sem nota CSAT, cria uma tarefa para quem o fechou coletar a nota de satisfacao do cliente em ate 2 dias.</description>
    <environments>Default</environments>
    <formulas>
        <name>fSubject</name>
        <dataType>String</dataType>
        <expression>"Coletar CSAT - Chamado " &amp; {!$Record.CaseNumber}</expression>
    </formulas>
    <formulas>
        <name>fDue</name>
        <dataType>Date</dataType>
        <expression>TODAY() + 2</expression>
    </formulas>
    <interviewLabel>SAC - Solicitar CSAT {!$Flow.CurrentDateTime}</interviewLabel>
    <label>SAC - Solicitar CSAT ao Fechar</label>
    <processMetadataValues><name>BuilderType</name><value><stringValue>LightningFlowBuilder</stringValue></value></processMetadataValues>
    <processType>AutoLaunchedFlow</processType>
    <recordCreates>
        <name>Criar_Tarefa_CSAT</name>
        <label>Criar Tarefa CSAT</label>
        <locationX>176</locationX>
        <locationY>288</locationY>
        <inputAssignments>
            <field>Subject</field>
            <value><elementReference>fSubject</elementReference></value>
        </inputAssignments>
        <inputAssignments>
            <field>ActivityDate</field>
            <value><elementReference>fDue</elementReference></value>
        </inputAssignments>
        <inputAssignments>
            <field>OwnerId</field>
            <value><elementReference>$Record.LastModifiedById</elementReference></value>
        </inputAssignments>
        <inputAssignments>
            <field>WhatId</field>
            <value><elementReference>$Record.Id</elementReference></value>
        </inputAssignments>
        <inputAssignments>
            <field>Status</field>
            <value><stringValue>Not Started</stringValue></value>
        </inputAssignments>
        <inputAssignments>
            <field>Priority</field>
            <value><stringValue>Normal</stringValue></value>
        </inputAssignments>
        <inputAssignments>
            <field>Description</field>
            <value><stringValue>Contatar o cliente, registrar a nota CSAT (1 a 5) e o comentario no chamado.</stringValue></value>
        </inputAssignments>
        <object>Task</object>
        <storeOutputAutomatically>true</storeOutputAutomatically>
    </recordCreates>
    <start>
        <locationX>50</locationX>
        <locationY>0</locationY>
        <connector><targetReference>Criar_Tarefa_CSAT</targetReference></connector>
        <doesRequireRecordChangedToMeetCriteria>true</doesRequireRecordChangedToMeetCriteria>
        <filterLogic>and</filterLogic>
        <filters>
            <field>IsClosed</field>
            <operator>EqualTo</operator>
            <value><booleanValue>true</booleanValue></value>
        </filters>
        <filters>
            <field>LT_CSAT_Score__c</field>
            <operator>IsNull</operator>
            <value><booleanValue>true</booleanValue></value>
        </filters>
        <object>Case</object>
        <recordTriggerType>CreateAndUpdate</recordTriggerType>
        <triggerType>RecordAfterSave</triggerType>
    </start>
    <status>Active</status>
</Flow>""")

# --- layout: secao de CSAT antes da Descricao
lay = os.path.join(ROOT, "layouts", "Case-LogiTrack SAC.layout-meta.xml")
txt = open(lay, encoding="utf-8").read()
if "LT_CSAT_Score__c" not in txt:
    marker = ("    <layoutSections>\n        <customLabel>true</customLabel>\n"
              "        <detailHeading>true</detailHeading>\n        <editHeading>true</editHeading>\n"
              "        <label>Descricao</label>")
    section = """    <layoutSections>
        <customLabel>true</customLabel>
        <detailHeading>true</detailHeading>
        <editHeading>true</editHeading>
        <label>Satisfacao do Cliente (CSAT)</label>
        <layoutColumns>
            <layoutItems>
                <behavior>Edit</behavior>
                <field>LT_CSAT_Score__c</field>
            </layoutItems>
            <layoutItems>
                <behavior>Edit</behavior>
                <field>LT_CSAT_Date__c</field>
            </layoutItems>
        </layoutColumns>
        <layoutColumns>
            <layoutItems>
                <behavior>Edit</behavior>
                <field>LT_CSAT_Comment__c</field>
            </layoutItems>
        </layoutColumns>
        <style>TwoColumnsLeftToRight</style>
    </layoutSections>
"""
    assert marker in txt, "marcador de layout nao encontrado"
    w(lay, txt.replace(marker, section + marker))

# --- FLS dos campos novos no permission set LT_SAC (insere apos o ultimo fieldPermissions)
ps = os.path.join(ROOT, "permissionsets", "LT_SAC.permissionset-meta.xml")
ptxt = open(ps, encoding="utf-8").read()
if "Case.LT_CSAT_Score__c" not in ptxt:
    add = "".join(
        f"    <fieldPermissions>\n        <editable>true</editable>\n        <field>Case.{f}</field>\n"
        "        <readable>true</readable>\n    </fieldPermissions>\n"
        for f in ("LT_CSAT_Score__c", "LT_CSAT_Comment__c", "LT_CSAT_Date__c"))
    idx = ptxt.rfind("</fieldPermissions>\n") + len("</fieldPermissions>\n")
    w(ps, ptxt[:idx] + add + ptxt[idx:])

# ============================================================ T2 · relatorios
os.makedirs(RDIR, exist_ok=True)


def chart_sum(agg, col):
    if col == "RowCount":
        return "<chartSummaries>\n            <axisBinding>y</axisBinding>\n            <column>RowCount</column>\n        </chartSummaries>"
    return (f"<chartSummaries>\n            <aggregate>{agg}</aggregate>\n            <axisBinding>y</axisBinding>\n"
            f"            <column>{col}</column>\n        </chartSummaries>")


def report(dev, name, group, ctype, filters=None, agg=None, title=None):
    cols = "    <columns>\n        <field>CASE_NUMBER</field>\n    </columns>\n"
    if agg:
        cols += f"    <columns>\n        <aggregateTypes>{agg[0]}</aggregateTypes>\n        <field>{agg[1]}</field>\n    </columns>\n"
    fblock = ""
    if filters:
        items = "".join(
            f"        <criteriaItems>\n            <column>{c}</column>\n            <columnToColumn>false</columnToColumn>\n"
            f"            <isUnlocked>true</isUnlocked>\n            <operator>{o}</operator>\n            <value>{v}</value>\n"
            "        </criteriaItems>\n" for c, o, v in filters)
        fblock = f"    <filter>\n{items}    </filter>\n"
    cs = chart_sum(*(agg if agg else ("Sum", "RowCount")))
    legend = "        <legendPosition>Right</legendPosition>\n" if ctype in ("Donut", "Pie", "Funnel") else ""
    chart = f"""    <chart>
        <backgroundColor1>#FFFFFF</backgroundColor1>
        <backgroundColor2>#FFFFFF</backgroundColor2>
        <backgroundFadeDir>Diagonal</backgroundFadeDir>
        {cs}
        <chartType>{ctype}</chartType>
        <enableHoverLabels>false</enableHoverLabels>
        <expandOthers>true</expandOthers>
        <groupingColumn>{group}</groupingColumn>
{legend}        <location>CHART_TOP</location>
        <showAxisLabels>true</showAxisLabels>
        <showPercentage>false</showPercentage>
        <showTotal>false</showTotal>
        <showValues>true</showValues>
        <size>Medium</size>
        <summaryAxisRange>Auto</summaryAxisRange>
        <textColor>#000000</textColor>
        <textSize>12</textSize>
        <title>{(title or name)[:40]}</title>
        <titleColor>#000000</titleColor>
        <titleSize>18</titleSize>
    </chart>
"""
    body = f"""<?xml version="1.0" encoding="UTF-8"?>
<Report xmlns="http://soap.sforce.com/2006/04/metadata">
{chart}{cols}    <description>{name}</description>
{fblock}    <format>Summary</format>
    <groupingsDown>
        <dateGranularity>None</dateGranularity>
        <field>{group}</field>
        <sortOrder>Asc</sortOrder>
    </groupingsDown>
    <name>{name[:40]}</name>
    <params>
        <name>co</name>
        <value>1</value>
    </params>
    <reportType>CaseList</reportType>
    <scope>organization</scope>
    <showDetails>true</showDetails>
    <showGrandTotal>true</showGrandTotal>
    <showSubTotals>true</showSubTotals>
</Report>"""
    w(os.path.join(RDIR, f"{dev}.report-meta.xml"), body)


report("LT_SAC_Cases_By_Status", "SAC - Chamados por Status", "STATUS", "Donut", title="Chamados por status")
report("LT_SAC_Cases_By_Type", "SAC - Chamados por Tipo", "RECORDTYPE", "HorizontalBar", title="Chamados por tipo")
report("LT_SAC_Cases_By_Priority", "SAC - Chamados por Prioridade", "PRIORITY", "Donut", title="Chamados por prioridade")
report("LT_SAC_Cases_By_Origin", "SAC - Chamados por Origem", "ORIGIN", "HorizontalBar", title="Chamados por canal de origem")
report("LT_SAC_Open_By_Owner", "SAC - Abertos por Fila ou Analista", "OWNER", "HorizontalBar",
       filters=[("CLOSED", "equals", "0")], title="Chamados abertos por fila/analista")
report("LT_SAC_Overdue_By_Type", "SAC - Atrasados por Tipo", "RECORDTYPE", "HorizontalBar",
       filters=[("Case.LT_Is_Overdue__c", "equals", "1")], title="Chamados fora do prazo por tipo")
report("LT_SAC_First_Response_By_Type", "SAC - 1a Resposta Media por Tipo", "RECORDTYPE", "HorizontalBar",
       agg=("Average", "Case.LT_First_Response_Hours__c"), title="Horas ate a 1a resposta (media)")
report("LT_SAC_CSAT_By_Type", "SAC - CSAT Medio por Tipo", "RECORDTYPE", "HorizontalBar",
       filters=[("Case.LT_CSAT_Score__c", "greaterThan", "0")],
       agg=("Average", "Case.LT_CSAT_Score__c"), title="CSAT medio por tipo de chamado")

# ============================================================ T2 · painel


def chart_comp(rep, header, col, row, colspan, rowspan, ctype="Bar"):
    return f"""        <dashboardGridComponents>
            <colSpan>{colspan}</colSpan>
            <columnIndex>{col}</columnIndex>
            <dashboardComponent>
                <autoselectColumnsFromReport>true</autoselectColumnsFromReport>
                <chartAxisRange>Auto</chartAxisRange>
                <componentType>{ctype}</componentType>
                <displayUnits>Auto</displayUnits>
                <drillEnabled>false</drillEnabled>
                <drillToDetailEnabled>false</drillToDetailEnabled>
                <enableHover>true</enableHover>
                <expandOthers>true</expandOthers>
                <groupingSortProperties/>
                <header>{header}</header>
                <report>LT_Reports/{rep}</report>
                <showPercentage>false</showPercentage>
                <showValues>true</showValues>
                <sortBy>RowValueDescending</sortBy>
                <sortLegendValues>true</sortLegendValues>
                <useReportChart>true</useReportChart>
            </dashboardComponent>
            <rowIndex>{row}</rowIndex>
            <rowSpan>{rowspan}</rowSpan>
        </dashboardGridComponents>"""


def metric(rep, header, label, col, summary, prec=0):
    return f"""        <dashboardGridComponents>
            <colSpan>3</colSpan>
            <columnIndex>{col}</columnIndex>
            <dashboardComponent>
                <autoselectColumnsFromReport>false</autoselectColumnsFromReport>
                <chartSummary>
{summary}
                </chartSummary>
                <componentType>Metric</componentType>
                <decimalPrecision>{prec}</decimalPrecision>
                <displayUnits>Auto</displayUnits>
                <groupingSortProperties/>
                <header>{header}</header>
                <indicatorBreakpoint1>0.0</indicatorBreakpoint1>
                <indicatorBreakpoint2>1.0</indicatorBreakpoint2>
                <indicatorHighColor>#00716B</indicatorHighColor>
                <indicatorLowColor>#C23934</indicatorLowColor>
                <indicatorMiddleColor>#CA8501</indicatorMiddleColor>
                <metricLabel>{label}</metricLabel>
                <report>LT_Reports/{rep}</report>
                <showRange>false</showRange>
            </dashboardComponent>
            <rowIndex>0</rowIndex>
            <rowSpan>6</rowSpan>
        </dashboardGridComponents>"""


ROWCOUNT = "                    <column>RowCount</column>"
comps = [
    metric("LT_SAC_Cases_By_Status", "Total de Chamados", "Chamados registrados", 0, ROWCOUNT),
    metric("LT_SAC_Overdue_By_Type", "Fora do Prazo", "Chamados atrasados", 3, ROWCOUNT),
    metric("LT_SAC_First_Response_By_Type", "1a Resposta (horas)", "Media ate a 1a resposta", 6,
           "                    <aggregate>Average</aggregate>\n                    <column>Case.LT_First_Response_Hours__c</column>", 1),
    metric("LT_SAC_CSAT_By_Type", "CSAT Medio", "Nota media (1 a 5)", 9,
           "                    <aggregate>Average</aggregate>\n                    <column>Case.LT_CSAT_Score__c</column>", 2),
    chart_comp("LT_SAC_Cases_By_Status", "Chamados por Status", 0, 6, 4, 8, "Donut"),
    chart_comp("LT_SAC_Cases_By_Type", "Chamados por Tipo", 4, 6, 4, 8, "Bar"),
    chart_comp("LT_SAC_Cases_By_Priority", "Chamados por Prioridade", 8, 6, 4, 8, "Donut"),
    chart_comp("LT_SAC_Open_By_Owner", "Abertos por Fila/Analista", 0, 14, 6, 8, "Bar"),
    chart_comp("LT_SAC_Overdue_By_Type", "Fora do Prazo por Tipo", 6, 14, 6, 8, "Bar"),
    chart_comp("LT_SAC_First_Response_By_Type", "1a Resposta Media por Tipo (h)", 0, 22, 6, 8, "Bar"),
    chart_comp("LT_SAC_CSAT_By_Type", "CSAT Medio por Tipo", 6, 22, 6, 8, "Bar"),
]
dash = f"""<?xml version="1.0" encoding="UTF-8"?>
<Dashboard xmlns="http://soap.sforce.com/2006/04/metadata">
    <backgroundEndColor>#FFFFFF</backgroundEndColor>
    <backgroundFadeDirection>Diagonal</backgroundFadeDirection>
    <backgroundStartColor>#FFFFFF</backgroundStartColor>
    <chartTheme>light</chartTheme>
    <colorPalette>unity</colorPalette>
    <dashboardChartTheme>light</dashboardChartTheme>
    <dashboardColorPalette>unity</dashboardColorPalette>
    <dashboardGridLayout>
{chr(10).join(comps)}
        <numberOfColumns>12</numberOfColumns>
        <rowHeight>36</rowHeight>
    </dashboardGridLayout>
    <dashboardType>SpecifiedUser</dashboardType>
    <description>Painel do SAC: volume, tipo, fila, prazo, tempo de primeira resposta e satisfacao (CSAT).</description>
    <isGridLayout>true</isGridLayout>
    <owner>ciderblockafram@gmail.com</owner>
    <runningUser>ciderblockafram@gmail.com</runningUser>
    <textColor>#000000</textColor>
    <title>SAC - Painel de Atendimento</title>
    <titleColor>#000000</titleColor>
    <titleSize>12</titleSize>
</Dashboard>"""
w(os.path.join(DDIR, "LT_Dash_SAC.dashboard-meta.xml"), dash)

print("Modulo T (T1 + T2) gerado.")
