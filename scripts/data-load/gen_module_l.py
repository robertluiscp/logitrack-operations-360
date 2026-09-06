#!/usr/bin/env python3
"""Modulo L: Reports & Dashboards por area."""
import os
ROOT = r"C:\Users\Robert Luis\Desktop\LogiTrack-SFDX\force-app\main\default"
RDIR = os.path.join(ROOT, "reports", "LT_Reports")
DDIR = os.path.join(ROOT, "dashboards", "LT_Operational_Dashboards")
os.makedirs(RDIR, exist_ok=True)

def w(path, body):
    open(path, "w", encoding="utf-8", newline="\n").write(body.rstrip() + "\n")

# report folder
w(os.path.join(ROOT, "reports", "LT_Reports.reportFolder-meta.xml"),
"""<?xml version="1.0" encoding="UTF-8"?>
<ReportFolder xmlns="http://soap.sforce.com/2006/04/metadata">
    <folderShares>
        <accessLevel>Manage</accessLevel>
        <sharedTo>ciderblockafram@gmail.com</sharedTo>
        <sharedToType>User</sharedToType>
    </folderShares>
    <name>LogiTrack - Relatorios</name>
</ReportFolder>""")

CHART_SUM = {
    "count": "<chartSummaries>\n            <axisBinding>y</axisBinding>\n            <column>RowCount</column>\n        </chartSummaries>",
}
def chart_sum_field(agg, field):
    return f"<chartSummaries>\n            <aggregate>{agg}</aggregate>\n            <axisBinding>y</axisBinding>\n            <column>{field}</column>\n        </chartSummaries>"

def report(dev, name, rtype, group_field, cols, chart_type=None, chart_col="count",
           chart_title=None, filters=None, fmt="Summary", scope="organization", date_gran="None"):
    colblocks = ""
    for c in cols:
        if isinstance(c, tuple):
            colblocks += f"    <columns>\n        <aggregateTypes>{c[1]}</aggregateTypes>\n        <field>{c[0]}</field>\n    </columns>\n"
        else:
            colblocks += f"    <columns>\n        <field>{c}</field>\n    </columns>\n"
    fblock = ""
    if filters:
        items = "".join(
f"""        <criteriaItems>
            <column>{col}</column>
            <columnToColumn>false</columnToColumn>
            <isUnlocked>true</isUnlocked>
            <operator>{op}</operator>
            <value>{val}</value>
        </criteriaItems>
""" for col, op, val in filters)
        fblock = f"    <filter>\n{items}    </filter>\n"
    chartblock = ""
    if chart_type:
        cs = CHART_SUM["count"] if chart_col == "count" else chart_sum_field(chart_col[0], chart_col[1])
        legend = "        <legendPosition>Right</legendPosition>\n" if chart_type in ("Donut", "Pie", "Funnel") else ""
        ctitle = (chart_title or name)[:40]
        chartblock = f"""    <chart>
        <backgroundColor1>#FFFFFF</backgroundColor1>
        <backgroundColor2>#FFFFFF</backgroundColor2>
        <backgroundFadeDir>Diagonal</backgroundFadeDir>
        {cs}
        <chartType>{chart_type}</chartType>
        <enableHoverLabels>false</enableHoverLabels>
        <expandOthers>true</expandOthers>
        <groupingColumn>{group_field}</groupingColumn>
{legend}        <location>CHART_TOP</location>
        <showAxisLabels>true</showAxisLabels>
        <showPercentage>false</showPercentage>
        <showTotal>false</showTotal>
        <showValues>true</showValues>
        <size>Medium</size>
        <summaryAxisRange>Auto</summaryAxisRange>
        <textColor>#000000</textColor>
        <textSize>12</textSize>
        <title>{ctitle}</title>
        <titleColor>#000000</titleColor>
        <titleSize>18</titleSize>
    </chart>
"""
    gblock = ""
    if group_field and fmt != "Tabular":
        gblock = f"""    <groupingsDown>
        <dateGranularity>{date_gran}</dateGranularity>
        <field>{group_field}</field>
        <sortOrder>Asc</sortOrder>
    </groupingsDown>
"""
    rname = name if len(name) <= 40 else name[:40]
    body = f"""<?xml version="1.0" encoding="UTF-8"?>
<Report xmlns="http://soap.sforce.com/2006/04/metadata">
{chartblock}{colblocks}    <description>{name}</description>
{fblock}    <format>{fmt}</format>
{gblock}    <name>{rname}</name>
    <params>
        <name>co</name>
        <value>1</value>
    </params>
    <reportType>{rtype}</reportType>
    <scope>{scope}</scope>
    <showDetails>true</showDetails>
    <showGrandTotal>true</showGrandTotal>
    <showSubTotals>true</showSubTotals>
</Report>"""
    w(os.path.join(RDIR, f"{dev}.report-meta.xml"), body)

CE = lambda o: f"CustomEntity${o}"

# ==================== OPERACAO ====================
report("LT_Op_Shipments_By_Status", "Operacao - Remessas por Status", CE("LT_Shipment__c"),
       "LT_Shipment__c.LT_Status__c", ["CUST_NAME"], "Donut", "count",
       "Remessas por status atual")
report("LT_Op_Incidents_By_Type", "Operacao - Ocorrencias por Tipo", CE("LT_Operational_Incident__c"),
       "LT_Operational_Incident__c.LT_Incident_Type__c", ["CUST_NAME"], "HorizontalBar", "count",
       "Ocorrencias operacionais por tipo")
report("LT_Op_Incidents_By_Base", "Operacao - Ocorrencias por Base", CE("LT_Operational_Incident__c"),
       "LT_Operational_Incident__c.LT_Owner_Unit__c", ["CUST_NAME"], "HorizontalBar", "count",
       "Ocorrencias operacionais por base responsavel")
report("LT_Op_Routes_Success_By_Base", "Operacao - Sucesso das Rotas por Base", CE("LT_Route__c"),
       "LT_Route__c.LT_Base__c", [("LT_Route__c.LT_Success_Rate__c", "Average")], "HorizontalBar",
       ("Average", "LT_Route__c.LT_Success_Rate__c"), "Taxa media de sucesso das rotas por base")

# ==================== COMERCIAL ====================
report("LT_Com_Agreements_By_Status", "Comercial - Contratos por Status", CE("LT_Commercial_Agreement__c"),
       "LT_Commercial_Agreement__c.LT_Agreement_Status__c", ["CUST_NAME"], "Donut", "count",
       "Contratos comerciais por status")
report("LT_Com_Agreements_By_Rep", "Comercial - Contratos por Representante", CE("LT_Commercial_Agreement__c"),
       "LT_Commercial_Agreement__c.LT_Agreement_Commercial_Rep__c",
       [("LT_Commercial_Agreement__c.LT_Minimum_Monthly_Volume__c", "Sum")], "HorizontalBar",
       ("Sum", "LT_Commercial_Agreement__c.LT_Minimum_Monthly_Volume__c"), "Volume minimo contratado por representante")

# ==================== CADASTRO ====================
report("LT_Cad_Drivers_By_Category", "Cadastro - Motoristas por Categoria", CE("LT_Driver__c"),
       "LT_Driver__c.LT_Category_Code__c", ["CUST_NAME"], "Donut", "count",
       "Motoristas por categoria de contratacao")
report("LT_Cad_Drivers_By_Status", "Cadastro - Motoristas por Situacao", CE("LT_Driver__c"),
       "LT_Driver__c.LT_Driver_Status__c", ["CUST_NAME"], "HorizontalBar", "count",
       "Motoristas por situacao cadastral")
report("LT_Cad_Vehicles_By_Type", "Cadastro - Veiculos por Tipo", CE("LT_Vehicle__c"),
       "LT_Vehicle__c.LT_Vehicle_Type__c", ["CUST_NAME"], "HorizontalBar", "count",
       "Veiculos por tipo")

# ==================== PREVENCAO DE PERDAS ====================
report("LT_Loss_By_Reason", "Perdas - Extravios por Motivo", CE("LT_Loss_Claim__c"),
       "LT_Loss_Claim__c.LT_Loss_Reason__c",
       [("LT_Loss_Claim__c.LT_Reimbursement_Value__c", "Sum")], "HorizontalBar",
       ("Sum", "LT_Loss_Claim__c.LT_Reimbursement_Value__c"), "Valor ressarcido por motivo de extravio")
report("LT_Loss_By_Responsibility", "Perdas - Extravios por Responsabilidade", CE("LT_Loss_Claim__c"),
       "LT_Loss_Claim__c.LT_Responsibility__c", ["CUST_NAME"], "Donut", "count",
       "Extravios por responsabilidade apurada")
report("LT_Loss_By_Status", "Perdas - Extravios por Status", CE("LT_Loss_Claim__c"),
       "LT_Loss_Claim__c.LT_Status__c", [("LT_Loss_Claim__c.LT_Reimbursement_Value__c", "Sum")], "HorizontalBar",
       ("Sum", "LT_Loss_Claim__c.LT_Reimbursement_Value__c"), "Valor de ressarcimento por status do extravio")
report("LT_Penalties_By_Type", "Perdas - Penalizacoes por Tipo", CE("LT_Driver_Penalty__c"),
       "LT_Driver_Penalty__c.LT_Penalty_Type__c", [("LT_Driver_Penalty__c.LT_Effective_Amount__c", "Sum")], "HorizontalBar",
       ("Sum", "LT_Driver_Penalty__c.LT_Effective_Amount__c"), "Valor efetivo das penalizacoes por tipo")

# ==================== FINANCEIRO ====================
report("LT_Fin_Requests_By_Status", "Financeiro - Solicitacoes por Status", CE("LT_Payment_Request__c"),
       "LT_Payment_Request__c.LT_Status__c", [("LT_Payment_Request__c.LT_Amount__c", "Sum")], "Donut",
       ("Sum", "LT_Payment_Request__c.LT_Amount__c"), "Valor solicitado por status")
report("LT_Fin_Requests_By_CostCenter", "Financeiro - Solicitacoes por Centro", CE("LT_Payment_Request__c"),
       "LT_Payment_Request__c.LT_Cost_Center__c", [("LT_Payment_Request__c.LT_Amount__c", "Sum")], "HorizontalBar",
       ("Sum", "LT_Payment_Request__c.LT_Amount__c"), "Valor solicitado por centro de custo")
report("LT_Fin_Requests_By_Type", "Financeiro - Solicitacoes por Tipo", CE("LT_Payment_Request__c"),
       "LT_Payment_Request__c.LT_Request_Type__c", [("LT_Payment_Request__c.LT_Amount__c", "Sum")], "HorizontalBar",
       ("Sum", "LT_Payment_Request__c.LT_Amount__c"), "Valor solicitado por tipo de solicitacao")
report("LT_Fin_Expenses_By_Category", "Financeiro - Despesas por Categoria", CE("LT_Expense__c"),
       "LT_Expense__c.LT_Expense_Category__c", [("LT_Expense__c.LT_Amount__c", "Sum")], "HorizontalBar",
       ("Sum", "LT_Expense__c.LT_Amount__c"), "Despesas por categoria contabil")
report("LT_Fin_Expenses_By_Month", "Financeiro - Despesas por Competencia", CE("LT_Expense__c"),
       "LT_Expense__c.LT_Competency_Month__c", [("LT_Expense__c.LT_Amount__c", "Sum")], "Line",
       ("Sum", "LT_Expense__c.LT_Amount__c"), "Despesas por mes de competencia")

print("Relatorios gerados:", len(os.listdir(RDIR)))
