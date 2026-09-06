#!/usr/bin/env python3
"""Modulo L: dashboards por area + finalizacao do Dashboard Executivo Sul."""
import os
ROOT = r"C:\Users\Robert Luis\Desktop\LogiTrack-SFDX\force-app\main\default"
DDIR = os.path.join(ROOT, "dashboards", "LT_Operational_Dashboards")

def w(path, body):
    open(path, "w", encoding="utf-8", newline="\n").write(body.rstrip() + "\n")

def chart_comp(report_dev, header, col, row, colspan, rowspan, ctype="Bar"):
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
                <report>LT_Reports/{report_dev}</report>
                <showPercentage>false</showPercentage>
                <showValues>true</showValues>
                <sortBy>RowValueDescending</sortBy>
                <sortLegendValues>true</sortLegendValues>
                <useReportChart>true</useReportChart>
            </dashboardComponent>
            <rowIndex>{row}</rowIndex>
            <rowSpan>{rowspan}</rowSpan>
        </dashboardGridComponents>"""

def metric_comp(report_ref, agg, column, header, label, col, row, colspan=3, rowspan=6, units="Integer", prec=0):
    return f"""        <dashboardGridComponents>
            <colSpan>{colspan}</colSpan>
            <columnIndex>{col}</columnIndex>
            <dashboardComponent>
                <autoselectColumnsFromReport>false</autoselectColumnsFromReport>
                <chartSummary>
                    <aggregate>{agg}</aggregate>
                    <column>{column}</column>
                </chartSummary>
                <componentType>Metric</componentType>
                <decimalPrecision>{prec}</decimalPrecision>
                <displayUnits>{units}</displayUnits>
                <groupingSortProperties/>
                <header>{header}</header>
                <indicatorBreakpoint1>0.0</indicatorBreakpoint1>
                <indicatorBreakpoint2>1.0</indicatorBreakpoint2>
                <indicatorHighColor>#00716B</indicatorHighColor>
                <indicatorLowColor>#C23934</indicatorLowColor>
                <indicatorMiddleColor>#CA8501</indicatorMiddleColor>
                <metricLabel>{label}</metricLabel>
                <report>{report_ref}</report>
                <showRange>false</showRange>
            </dashboardComponent>
            <rowIndex>{row}</rowIndex>
            <rowSpan>{rowspan}</rowSpan>
        </dashboardGridComponents>"""

def dashboard(dev, title, desc, components):
    body = f"""<?xml version="1.0" encoding="UTF-8"?>
<Dashboard xmlns="http://soap.sforce.com/2006/04/metadata">
    <backgroundEndColor>#FFFFFF</backgroundEndColor>
    <backgroundFadeDirection>Diagonal</backgroundFadeDirection>
    <backgroundStartColor>#FFFFFF</backgroundStartColor>
    <chartTheme>light</chartTheme>
    <colorPalette>unity</colorPalette>
    <dashboardChartTheme>light</dashboardChartTheme>
    <dashboardColorPalette>unity</dashboardColorPalette>
    <dashboardGridLayout>
{chr(10).join(components)}
        <numberOfColumns>12</numberOfColumns>
        <rowHeight>36</rowHeight>
    </dashboardGridLayout>
    <dashboardType>SpecifiedUser</dashboardType>
    <description>{desc}</description>
    <isGridLayout>true</isGridLayout>
    <owner>ciderblockafram@gmail.com</owner>
    <runningUser>ciderblockafram@gmail.com</runningUser>
    <textColor>#000000</textColor>
    <title>{title}</title>
    <titleColor>#000000</titleColor>
    <titleSize>12</titleSize>
</Dashboard>"""
    w(os.path.join(DDIR, f"{dev}.dashboard-meta.xml"), body)

# ==================== DASHBOARDS POR AREA ====================
dashboard("LT_Dash_Operacao", "Operacao - Painel Regional Sul",
    "Painel operacional: remessas, ocorrencias e rotas da regional Sul.",
    [chart_comp("LT_Op_Shipments_By_Status", "Remessas por Status", 0, 0, 6, 8, "Donut"),
     chart_comp("LT_Op_Routes_Success_By_Base", "Sucesso das Rotas por Base", 6, 0, 6, 8, "Bar"),
     chart_comp("LT_Op_Incidents_By_Type", "Ocorrencias por Tipo", 0, 8, 6, 8, "Bar"),
     chart_comp("LT_Op_Incidents_By_Base", "Ocorrencias por Base", 6, 8, 6, 8, "Bar")])

dashboard("LT_Dash_Comercial", "Comercial - Painel de Carteira",
    "Painel comercial: contratos por status e por representante.",
    [chart_comp("LT_Com_Agreements_By_Status", "Contratos por Status", 0, 0, 6, 9, "Donut"),
     chart_comp("LT_Com_Agreements_By_Rep", "Volume Contratado por Representante", 6, 0, 6, 9, "Bar")])

dashboard("LT_Dash_Cadastro", "Cadastro e Frota - Painel",
    "Painel de cadastro: motoristas por categoria e situacao, veiculos por tipo.",
    [chart_comp("LT_Cad_Drivers_By_Category", "Motoristas por Categoria", 0, 0, 4, 9, "Donut"),
     chart_comp("LT_Cad_Drivers_By_Status", "Motoristas por Situacao", 4, 0, 4, 9, "Bar"),
     chart_comp("LT_Cad_Vehicles_By_Type", "Veiculos por Tipo", 8, 0, 4, 9, "Bar")])

dashboard("LT_Dash_Perdas", "Prevencao de Perdas - Painel",
    "Painel de prevencao de perdas: extravios por motivo, responsabilidade e status; penalizacoes.",
    [chart_comp("LT_Loss_By_Reason", "Ressarcimento por Motivo", 0, 0, 6, 8, "Bar"),
     chart_comp("LT_Loss_By_Responsibility", "Extravios por Responsabilidade", 6, 0, 6, 8, "Donut"),
     chart_comp("LT_Loss_By_Status", "Ressarcimento por Status", 0, 8, 6, 8, "Bar"),
     chart_comp("LT_Penalties_By_Type", "Penalizacoes por Tipo", 6, 8, 6, 8, "Bar")])

dashboard("LT_Dash_Financeiro", "Financeiro - Painel de Contas a Pagar",
    "Painel financeiro: solicitacoes por status, centro de custo e tipo; despesas por categoria e competencia.",
    [chart_comp("LT_Fin_Requests_By_Status", "Solicitacoes por Status", 0, 0, 6, 8, "Donut"),
     chart_comp("LT_Fin_Requests_By_CostCenter", "Solicitacoes por Centro de Custo", 6, 0, 6, 8, "Bar"),
     chart_comp("LT_Fin_Requests_By_Type", "Solicitacoes por Tipo", 0, 8, 4, 8, "Bar"),
     chart_comp("LT_Fin_Expenses_By_Category", "Despesas por Categoria", 4, 8, 4, 8, "Bar"),
     chart_comp("LT_Fin_Expenses_By_Month", "Despesas por Competencia", 8, 8, 4, 8, "Line")])

dashboard("LT_Dash_Executivo", "LogiTrack Brasil - Painel Executivo",
    "Visao consolidada: operacao, comercial, prevencao de perdas e financeiro.",
    [chart_comp("LT_Op_Shipments_By_Status", "Remessas por Status", 0, 0, 6, 8, "Donut"),
     chart_comp("LT_Loss_By_Status", "Ressarcimento de Extravios por Status", 6, 0, 6, 8, "Bar"),
     chart_comp("LT_Fin_Requests_By_Status", "Contas a Pagar por Status", 0, 8, 6, 8, "Donut"),
     chart_comp("LT_Com_Agreements_By_Status", "Contratos Comerciais por Status", 6, 8, 6, 8, "Donut")])

# ==================== FINALIZAR: Operacao - Dashboard Executivo - Sul ====================
DP = "unfiled$public/Daily_Performance_by_Unit"
cards = [
    metric_comp(DP, "Sum", "Operational_Indicator__c.Total_Orders__c", "Total de Pedidos", "Volume total previsto", 0, 0),
    metric_comp(DP, "Sum", "Operational_Indicator__c.Delivered_Orders__c", "Entregues", "Pedidos entregues", 3, 0),
    metric_comp(DP, "Sum", "Operational_Indicator__c.Undelivered_Orders__c", "Nao Entregues", "Pedidos nao entregues", 6, 0),
    metric_comp(DP, "Average", "Operational_Indicator__c.Delivery_Percentage__c", "% de Entregas", "Media de entregas no periodo", 9, 0, units="Auto", prec=2),
    metric_comp(DP, "Average", "Operational_Indicator__c.SLA__c", "SLA Medio", "Media de SLA no periodo", 0, 6, units="Auto", prec=2),
]
charts = [
    chart_comp("LT_Op_Shipments_By_Status", "Remessas por Status", 3, 6, 4, 10, "Donut"),
    chart_comp("LT_Op_Incidents_By_Base", "Ocorrencias por Base", 7, 6, 5, 10, "Bar"),
]
existing_bars = f"""        <dashboardGridComponents>
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
                <header>Entregues x Nao Entregues por Unidade</header>
                <report>unfiled$public/Operation_Order_Volume_Per_Unit</report>
                <showPercentage>false</showPercentage>
                <showPicturesOnCharts>false</showPicturesOnCharts>
                <showValues>false</showValues>
                <sortBy>RowLabelAscending</sortBy>
                <sortLegendValues>false</sortLegendValues>
                <useReportChart>true</useReportChart>
            </dashboardComponent>
            <rowIndex>16</rowIndex>
            <rowSpan>12</rowSpan>
        </dashboardGridComponents>"""

body = f"""<?xml version="1.0" encoding="UTF-8"?>
<Dashboard xmlns="http://soap.sforce.com/2006/04/metadata">
    <backgroundEndColor>#FFFFFF</backgroundEndColor>
    <backgroundFadeDirection>Diagonal</backgroundFadeDirection>
    <backgroundStartColor>#FFFFFF</backgroundStartColor>
    <chartTheme>light</chartTheme>
    <colorPalette>unity</colorPalette>
    <dashboardChartTheme>light</dashboardChartTheme>
    <dashboardColorPalette>unity</dashboardColorPalette>
    <dashboardGridLayout>
{chr(10).join(cards + charts)}
{existing_bars}
        <numberOfColumns>12</numberOfColumns>
        <rowHeight>36</rowHeight>
    </dashboardGridLayout>
    <dashboardType>SpecifiedUser</dashboardType>
    <description>Visao executiva do desempenho operacional das unidades logisticas da Regiao Sul.</description>
    <isGridLayout>true</isGridLayout>
    <owner>ciderblockafram@gmail.com</owner>
    <runningUser>ciderblockafram@gmail.com</runningUser>
    <textColor>#000000</textColor>
    <title>Operacao - Dashboard Executivo - Sul</title>
    <titleColor>#000000</titleColor>
    <titleSize>12</titleSize>
</Dashboard>"""
w(os.path.join(DDIR, "vLtgxbIJVugJpUjsQSfBBuztrjfKgT.dashboard-meta.xml"), body)

print("Dashboards gerados:", len([f for f in os.listdir(DDIR) if f.endswith('.xml')]))
