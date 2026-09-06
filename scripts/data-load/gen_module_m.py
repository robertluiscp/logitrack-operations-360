#!/usr/bin/env python3
"""Modulo M: Permission Set Groups por area."""
import os
ROOT = r"C:\Users\Robert Luis\Desktop\LogiTrack-SFDX\force-app\main\default"
PSG = os.path.join(ROOT, "permissionsetgroups")

def psg(dev, label, desc, sets):
    ps = "\n".join(f"    <permissionSets>{s}</permissionSets>" for s in sets)
    open(os.path.join(PSG, f"{dev}.permissionsetgroup-meta.xml"), "w", encoding="utf-8", newline="\n").write(
f"""<?xml version="1.0" encoding="UTF-8"?>
<PermissionSetGroup xmlns="http://soap.sforce.com/2006/04/metadata">
    <description>{desc}</description>
    <hasActivationRequired>false</hasActivationRequired>
    <label>{label}</label>
{ps}
    <status>Updated</status>
</PermissionSetGroup>
""")

psg("LT_PSG_Operacao", "LT - Perfil Operacao",
    "Perfil de acesso da operacao: remessas, rastreamento, coletas, romaneios, rotas, tentativas de entrega e ocorrencias operacionais.",
    ["LT_Operations", "LT_Routes_Deliveries", "LT_Collections", "LT_Incidents", "Manage_Logistics_Units", "Manage_Operational_Indicators"])

psg("LT_PSG_Comercial", "LT - Perfil Comercial",
    "Perfil de acesso do comercial: embarcadores, contratos comerciais, faturamento mensal e prospeccao.",
    ["LT_Commercial", "LT_Partner_Management"])

psg("LT_PSG_Cadastro", "LT - Perfil Cadastro e Frota",
    "Perfil de acesso do cadastro: motoristas, veiculos, documentos e parceiros operacionais.",
    ["LT_Cadastro", "LT_Partner_Management"])

psg("LT_PSG_SAC", "LT - Perfil SAC e Perdas",
    "Perfil do atendimento ao cliente: chamados, PNR, extravios e penalizacao de motoristas.",
    ["LT_SAC", "LT_Loss_Prevention", "LT_Incidents"])

psg("LT_PSG_Financeiro", "LT - Perfil Financeiro",
    "Perfil do financeiro: solicitacoes de pagamento, aprovacao por alcada, pagamentos e despesas.",
    ["LT_Finance", "LT_Partner_Management"])

psg("LT_PSG_Gestao", "LT - Perfil Gestao Consolidada",
    "Perfil de gestao/diretoria: acesso amplo de leitura e operacao em todas as areas para acompanhamento executivo.",
    ["LT_Operations", "LT_Routes_Deliveries", "LT_Collections", "LT_Incidents",
     "LT_Commercial", "LT_Partner_Management", "LT_Cadastro", "LT_SAC",
     "LT_Loss_Prevention", "LT_Finance", "Manage_Logistics_Units", "Manage_Operational_Indicators"])

print("PSGs gerados:", len([f for f in os.listdir(PSG) if f.startswith("LT_PSG_")]))
