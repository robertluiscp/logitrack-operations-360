#!/usr/bin/env python3
"""Modulo K: Lightning Apps - home pages, app Executivo, utility bars enriquecidas.

Nota: flexipage:filterListCard e flexipage:reportChart nao validam contra list views
/ relatorios criados por metadata nesta org (erro "Error retrieving filter").
As home pages usam rich text com links diretos para as list views + componentes
padrao (Assistente, Itens Recentes, Tarefas e Eventos de Hoje). Dashboards e
graficos de relatorio ficam para o Modulo L.
"""
import os
ROOT = r"C:\Users\Robert Luis\Desktop\LogiTrack-SFDX\force-app\main\default"
FP = os.path.join(ROOT, "flexipages")
APP = os.path.join(ROOT, "applications")

def w(path, body):
    open(path, "w", encoding="utf-8", newline="\n").write(body.rstrip() + "\n")

def cprop(name, value):
    return f"                <componentInstanceProperties>\n                    <name>{name}</name>\n                    <value>{value}</value>\n                </componentInstanceProperties>"

def comp(cname, ident, props=None):
    p = ("\n" + "\n".join(cprop(k, v) for k, v in (props or []))) if props else ""
    return f"""        <itemInstances>
            <componentInstance>{p}
                <componentName>{cname}</componentName>
                <identifier>{ident}</identifier>
            </componentInstance>
        </itemInstances>"""

def region(name, rtype, items):
    return f"""    <flexiPageRegions>
{chr(10).join(items)}
        <name>{name}</name>
        <type>{rtype}</type>
    </flexiPageRegions>"""

def homepage(dev_name, label, top_items, left_items, right_items, sidebar_items):
    body = f"""<?xml version="1.0" encoding="UTF-8"?>
<FlexiPage xmlns="http://soap.sforce.com/2006/04/metadata">
{region('top', 'Region', top_items)}
{region('bottomLeft', 'Region', left_items)}
{region('bottomRight', 'Region', right_items)}
{region('sidebar', 'Region', sidebar_items)}
    <masterLabel>{label}</masterLabel>
    <template>
        <name>home:desktopTemplate</name>
    </template>
    <type>HomePage</type>
</FlexiPage>"""
    w(os.path.join(FP, f"{dev_name}.flexipage-meta.xml"), body)

def richtext(ident, html):
    return comp("flexipage:richText", ident, [("richTextValue", html)])

RECENT = lambda i: comp("home:recentRecordContainer", f"{i}Recent")
ASSISTANT = lambda i: comp("home:assistant", f"{i}Assist")
TASKS = lambda i: comp("runtime_sales_activities:todayTaskContainer", f"{i}Tasks")
EVENTS = lambda i: comp("home:eventContainer", f"{i}Events")

def lv_link(obj, fn, text):
    return f'&lt;li&gt;&lt;a href="/lightning/o/{obj}/list?filterName={fn}"&gt;{text}&lt;/a&gt;&lt;/li&gt;'

def panel(title, intro, links):
    lis = "".join(links)
    return (f'&lt;h2&gt;{title}&lt;/h2&gt;&lt;p&gt;{intro}&lt;/p&gt;'
            f'&lt;p&gt;&lt;b&gt;Filas para acompanhar:&lt;/b&gt;&lt;/p&gt;&lt;ul&gt;{lis}&lt;/ul&gt;')

# ==================== HOME PAGES ====================
homepage("LogiTrack_Operations_360_Home", "LogiTrack Operations 360 - Home",
    [richtext("ops", panel("Operacao Sul - visao do dia",
        "Priorize remessas retidas e sem movimentacao ha mais de 10 dias, ocorrencias fora do prazo e rotas em andamento.",
        [lv_link("LT_Shipment__c", "Retidas_e_Paradas", "Remessas retidas e sem movimentacao"),
         lv_link("LT_Shipment__c", "Atrasadas", "Remessas atrasadas"),
         lv_link("LT_Operational_Incident__c", "Fora_do_Prazo", "Ocorrencias fora do prazo"),
         lv_link("LT_Operational_Incident__c", "Candidatas_Extravio", "Candidatas a extravio (+10 dias)"),
         lv_link("LT_Route__c", "Em_Rota", "Rotas em andamento"),
         lv_link("LT_Manifest__c", "A_Pagar", "Romaneios a pagar")]))],
    [RECENT("ops")], [TASKS("ops")], [ASSISTANT("ops"), EVENTS("ops")])

homepage("LogiTrack_Comercial_Home", "LogiTrack Comercial - Home",
    [richtext("com", panel("Comercial - pipeline e carteira",
        "Prospeccao de embarcadores, contratos vigentes e faturamento mensal em aberto.",
        [lv_link("LT_Commercial_Agreement__c", "Vigentes", "Contratos vigentes"),
         lv_link("LT_Monthly_Billing__c", "Em_Aberto", "Faturamento mensal em aberto"),
         lv_link("Opportunity", "MyOpportunities", "Minhas oportunidades")]))],
    [RECENT("com")], [TASKS("com")], [ASSISTANT("com"), EVENTS("com")])

homepage("LogiTrack_Cadastro_Home", "LogiTrack Cadastro - Home",
    [richtext("cad", panel("Cadastro e Frota",
        "Motoristas ativos, CNHs a vencer e veiculos. Mantenha a documentacao em dia.",
        [lv_link("LT_Driver__c", "CNH_Pendente", "Motoristas com CNH pendente"),
         lv_link("LT_Driver__c", "Ativos", "Motoristas ativos"),
         lv_link("LT_Vehicle__c", "All", "Veiculos")]))],
    [RECENT("cad")], [TASKS("cad")], [ASSISTANT("cad")])

homepage("LogiTrack_SAC_Home", "LogiTrack SAC - Home",
    [richtext("sac", panel("SAC - fila de atendimento",
        "Chamados abertos, PNR em envelhecimento e extravios em apuracao.",
        [lv_link("Case", "MyOpenCases", "Meus chamados abertos"),
         lv_link("LT_Loss_Claim__c", "Em_Apuracao", "Extravios em apuracao"),
         lv_link("LT_Loss_Claim__c", "Ressarcidos", "Extravios ressarcidos")]))],
    [RECENT("sac")], [TASKS("sac")], [ASSISTANT("sac"), EVENTS("sac")])

homepage("LogiTrack_Financeiro_Home", "LogiTrack Financeiro - Home",
    [richtext("fin", panel("Financeiro - contas a pagar",
        "Solicitacoes aguardando aprovacao, aprovadas a pagar, vencidas e despesas previstas do mes.",
        [lv_link("LT_Payment_Request__c", "Em_Aprovacao", "Solicitacoes aguardando aprovacao"),
         lv_link("LT_Payment_Request__c", "A_Pagar", "Solicitacoes aprovadas a pagar"),
         lv_link("LT_Payment_Request__c", "Vencidas", "Solicitacoes vencidas"),
         lv_link("LT_Expense__c", "Previstas", "Despesas previstas"),
         lv_link("LT_Payment__c", "A_Conciliar", "Pagamentos a conciliar")]))],
    [RECENT("fin")], [TASKS("fin")], [ASSISTANT("fin")])

homepage("LogiTrack_Executivo_Home", "LogiTrack Executivo - Home",
    [richtext("exe", panel("LogiTrack Brasil - Cockpit Executivo",
        "Consolidacao das areas: operacao, comercial, prevencao de perdas e financeiro. Use os relatorios e dashboards para o acompanhamento semanal.",
        [lv_link("LT_Operational_Incident__c", "Candidatas_Extravio", "Ocorrencias candidatas a extravio"),
         lv_link("LT_Loss_Claim__c", "Ressarcidos", "Extravios ressarcidos"),
         lv_link("LT_Payment_Request__c", "A_Pagar", "Contas a pagar aprovadas"),
         lv_link("LT_Monthly_Billing__c", "Em_Aberto", "Faturamento a receber")]))],
    [RECENT("exe")], [TASKS("exe")], [ASSISTANT("exe")])

# ==================== APP: LogiTrack Executivo ====================
w(os.path.join(APP, "LogiTrack_Executivo.app-meta.xml"), """<?xml version="1.0" encoding="UTF-8"?>
<CustomApplication xmlns="http://soap.sforce.com/2006/04/metadata">
    <brand>
        <headerColor>#0B3D2E</headerColor>
        <shouldOverrideOrgTheme>false</shouldOverrideOrgTheme>
    </brand>
    <description>Cockpit executivo da LogiTrack Brasil: visao consolidada de operacao, comercial, prevencao de perdas e financeiro com relatorios e dashboards.</description>
    <formFactors>Large</formFactors>
    <isNavAutoTempTabsDisabled>false</isNavAutoTempTabsDisabled>
    <isNavPersonalizationDisabled>false</isNavPersonalizationDisabled>
    <isNavTabPersistenceDisabled>false</isNavTabPersistenceDisabled>
    <label>LogiTrack Executivo</label>
    <navType>Standard</navType>
    <tabs>standard-home</tabs>
    <tabs>standard-Dashboard</tabs>
    <tabs>standard-report</tabs>
    <tabs>Operational_Indicator__c</tabs>
    <tabs>LT_Shipment__c</tabs>
    <tabs>LT_Operational_Incident__c</tabs>
    <tabs>LT_Loss_Claim__c</tabs>
    <tabs>LT_Driver_Penalty__c</tabs>
    <tabs>LT_Payment_Request__c</tabs>
    <tabs>LT_Expense__c</tabs>
    <tabs>LT_Monthly_Billing__c</tabs>
    <tabs>LT_Logistics_Unit__c</tabs>
    <uiType>Lightning</uiType>
</CustomApplication>
""")

print("Modulo K: 6 home pages + app Executivo gerados.")
