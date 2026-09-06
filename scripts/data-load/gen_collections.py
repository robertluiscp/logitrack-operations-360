#!/usr/bin/env python3
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from metahelp import *

ROOT = r"C:\Users\Robert Luis\Desktop\LogiTrack-SFDX\force-app\main\default"
PR = os.path.join(ROOT, "objects", "LT_Pickup_Request__c")
MF = os.path.join(ROOT, "objects", "LT_Manifest__c")
ML = os.path.join(ROOT, "objects", "LT_Manifest_Line__c")
for d in (PR, MF, ML):
    ensure(d)

# ==================== LT_Pickup_Request__c ====================
PTYPE = ["Coleta no Seller", "Coleta no DropOff", "C2C - Venda de Etiqueta"]
PSTATUS = ["Solicitada", "Agendada", "Motorista a Caminho", "Coletada", "Nao Realizada", "Cancelada"]

wf(PR, "LT_Pickup_Type__c", picklist("LT_Pickup_Type__c", "Tipo de Coleta",
   "Natureza da coleta First Mile.", PTYPE, default="Coleta no Seller"))
wf(PR, "LT_Status__c", picklist("LT_Status__c", "Status da Coleta",
   "Situacao da solicitacao de coleta.", PSTATUS, default="Solicitada"))
wf(PR, "LT_Shipper__c", lookup("LT_Shipper__c", "Embarcador",
   "Embarcador que solicitou a coleta (coletas no Seller).", "Account", "Coletas", "LT_Pickup_Requests",
   lf_items=[("Account.RecordType.DeveloperName", "equals", "LT_Shipper")],
   lf_msg="Selecione uma conta do tipo Embarcador.", lf_optional=True))
wf(PR, "LT_Pickup_Point__c", lookup("LT_Pickup_Point__c", "Ponto de Coleta (DropOff)",
   "Ponto de coleta fisico (coletas DropOff).", "Account", "Coletas Recebidas", "LT_DropOff_Pickups",
   lf_items=[("Account.LT_Operating_Partner_Type__c", "equals", "Parceiro DropOff")],
   lf_msg="Selecione uma conta do tipo Parceiro DropOff.", lf_optional=True))
wf(PR, "LT_First_Mile_Driver__c", lookup("LT_First_Mile_Driver__c", "Motorista First Mile",
   "Motorista responsavel pela coleta.", "LT_Driver__c", "Coletas", "LT_Pickup_Requests", lf_optional=True))
wf(PR, "LT_Origin_Base__c", lookup("LT_Origin_Base__c", "Unidade de Origem",
   "Base ou CD que despachou a coleta.", "LT_Logistics_Unit__c", "Coletas de Origem", "LT_Origin_Pickups", lf_optional=True))
wf(PR, "LT_Destination_CD__c", lookup("LT_Destination_CD__c", "CD de Destino",
   "Centro de Distribuicao para onde os pacotes coletados serao enviados.", "LT_Logistics_Unit__c",
   "Coletas (CD de Destino)", "LT_CD_Pickups",
   lf_items=[("LT_Logistics_Unit__c.Unit_Type__c", "equals", "Centro de Distribuicao")],
   lf_msg="Selecione um Centro de Distribuicao.", lf_optional=True))
wf(PR, "LT_Manifest__c", lookup("LT_Manifest__c", "Romaneio",
   "Romaneio em que esta coleta foi consolidada para pagamento.", "LT_Manifest__c",
   "Coletas", "LT_Pickup_Requests", lf_optional=True))
wf(PR, "LT_Requested_By__c", field("LT_Requested_By__c", "Solicitante", "Quem pediu a coleta.", "Text", length=120, track=False))
wf(PR, "LT_Pickup_Address__c", field("LT_Pickup_Address__c", "Endereco de Coleta", "Endereco onde a coleta sera realizada.", "Text", length=255, track=False))
wf(PR, "LT_Pickup_City__c", field("LT_Pickup_City__c", "Cidade da Coleta", "Cidade da coleta.", "Text", length=80, track=False))
wf(PR, "LT_Pickup_State__c", gvs_picklist("LT_Pickup_State__c", "UF da Coleta", "Estado da coleta.", "Brazilian_States"))
wf(PR, "LT_Scheduled_Date__c", field("LT_Scheduled_Date__c", "Data Agendada", "Data agendada para a coleta.", "Date"))
wf(PR, "LT_Window_Start__c", field("LT_Window_Start__c", "Inicio da Janela", "Inicio da janela de coleta.", "DateTime", track=False))
wf(PR, "LT_Window_End__c", field("LT_Window_End__c", "Fim da Janela", "Fim da janela de coleta.", "DateTime", track=False))
wf(PR, "LT_Estimated_Packages__c", field("LT_Estimated_Packages__c", "Pacotes Estimados", "Quantidade estimada de pacotes a coletar.", "Number", precision=6, scale=0))
wf(PR, "LT_Collected_Packages__c", field("LT_Collected_Packages__c", "Pacotes Coletados", "Quantidade efetivamente coletada.", "Number", precision=6, scale=0))
wf(PR, "LT_Completed_DateTime__c", field("LT_Completed_DateTime__c", "Data/Hora da Coleta", "Momento em que a coleta foi concluida.", "DateTime"))
wf(PR, "LT_C2C_Sender_Name__c", field("LT_C2C_Sender_Name__c", "C2C - Remetente", "Remetente pessoa fisica (Venda de Etiqueta).", "Text", length=120, track=False))
wf(PR, "LT_C2C_Recipient_Name__c", field("LT_C2C_Recipient_Name__c", "C2C - Destinatario", "Destinatario (Venda de Etiqueta).", "Text", length=120, track=False))
wf(PR, "LT_C2C_Dest_City__c", field("LT_C2C_Dest_City__c", "C2C - Cidade de Destino", "Cidade de destino (Venda de Etiqueta).", "Text", length=80, track=False))
wf(PR, "LT_Notes__c", field("LT_Notes__c", "Observacoes", "Observacoes da coleta.", "LongTextArea", length=4000, lines=3, track=False))
wf(PR, "LT_Fill_Rate__c", formula("LT_Fill_Rate__c", "Aproveitamento",
   "Percentual coletado em relacao ao estimado.", "Percent",
   'IF(OR(ISBLANK(LT_Estimated_Packages__c), LT_Estimated_Packages__c = 0), 0, LT_Collected_Packages__c / LT_Estimated_Packages__c)',
   precision=5, scale=2))

wv(PR, "LT_Pickup_Seller_Requires_Shipper", "Coleta no Seller exige o embarcador.",
   'AND(ISPICKVAL(LT_Pickup_Type__c, "Coleta no Seller"), ISBLANK(LT_Shipper__c))',
   "Informe o Embarcador para coletas no Seller.", "LT_Shipper__c")
wv(PR, "LT_Pickup_DropOff_Requires_Point", "Coleta no DropOff exige o ponto de coleta.",
   'AND(ISPICKVAL(LT_Pickup_Type__c, "Coleta no DropOff"), ISBLANK(LT_Pickup_Point__c))',
   "Informe o Ponto de Coleta (DropOff).", "LT_Pickup_Point__c")
wv(PR, "LT_Pickup_Window_Order", "O fim da janela nao pode ser antes do inicio.",
   'AND(NOT(ISBLANK(LT_Window_Start__c)), NOT(ISBLANK(LT_Window_End__c)), LT_Window_End__c &lt; LT_Window_Start__c)',
   "O Fim da Janela nao pode ser anterior ao Inicio.", "LT_Window_End__c")
wv(PR, "LT_Pickup_Packages_Positive", "Quantidades de pacotes nao podem ser negativas.",
   'OR(LT_Estimated_Packages__c &lt; 0, LT_Collected_Packages__c &lt; 0)',
   "As quantidades de pacotes nao podem ser negativas.")
wv(PR, "LT_Pickup_Scheduled_Requires_Data", "Coleta Agendada exige motorista e data.",
   'AND(ISPICKVAL(LT_Status__c, "Agendada"), OR(ISBLANK(LT_First_Mile_Driver__c), ISBLANK(LT_Scheduled_Date__c)))',
   "Informe o Motorista First Mile e a Data Agendada.", "LT_First_Mile_Driver__c")
wv(PR, "LT_Pickup_Collected_Requires_Data", "Coleta concluida exige motorista, quantidade e data/hora.",
   'AND(ISPICKVAL(LT_Status__c, "Coletada"), OR(ISBLANK(LT_First_Mile_Driver__c), ISBLANK(LT_Collected_Packages__c), ISBLANK(LT_Completed_DateTime__c)))',
   "Para concluir a coleta informe motorista, pacotes coletados e data/hora.")

open(os.path.join(PR, "compactLayouts", "LT_Pickup_Request_Summary.compactLayout-meta.xml"), "w", encoding="utf-8", newline="\n").write(
   compact("LT_Pickup_Request_Summary", "Coleta - Resumo",
           ["Name", "LT_Pickup_Type__c", "LT_Status__c", "LT_Pickup_City__c", "LT_Scheduled_Date__c", "LT_First_Mile_Driver__c"]))
open(os.path.join(PR, "listViews", "All.listView-meta.xml"), "w", encoding="utf-8", newline="\n").write(
   listview("All", "Todas", ["NAME", "LT_Pickup_Type__c", "LT_Status__c", "LT_Pickup_City__c", "LT_Pickup_State__c", "LT_Scheduled_Date__c", "LT_First_Mile_Driver__c"]))
open(os.path.join(PR, "listViews", "Pendentes.listView-meta.xml"), "w", encoding="utf-8", newline="\n").write(
   listview("Pendentes", "Coletas Pendentes",
            ["NAME", "LT_Pickup_Type__c", "LT_Status__c", "LT_Pickup_City__c", "LT_Estimated_Packages__c", "LT_First_Mile_Driver__c"],
            filters=[("LT_Status__c", "notEqual", "Coletada,Cancelada,Nao Realizada")]))

wobj(PR, "LT_Pickup_Request__c", "Solicitacao de Coleta", "Solicitacoes de Coleta",
     "Codigo da Coleta", "AutoNumber", "COL-{000000}", compact="LT_Pickup_Request_Summary")

# ==================== LT_Manifest__c ====================
MTYPE = ["Coleta (First Mile)", "Mini Transferencia (MR)"]
PAYS = ["Em Conferencia", "Aprovado", "Pago", "Rejeitado"]

wf(MF, "LT_Driver__c", lookup("LT_Driver__c", "Motorista",
   "Motorista First Mile ou de Mini Transferencia pago por este romaneio.", "LT_Driver__c",
   "Romaneios", "LT_Manifests", required=True, delete="Restrict"))
wf(MF, "LT_Manifest_Type__c", picklist("LT_Manifest_Type__c", "Tipo de Romaneio",
   "Coleta First Mile ou Mini Transferencia.", MTYPE, default="Coleta (First Mile)"))
wf(MF, "LT_Reference_Date__c", field("LT_Reference_Date__c", "Data de Referencia",
   "Dia de trabalho a que o romaneio se refere.", "Date", required=True))
wf(MF, "LT_Origin_Unit__c", lookup("LT_Origin_Unit__c", "Unidade de Origem",
   "Base ou CD de origem do romaneio.", "LT_Logistics_Unit__c", "Romaneios de Origem", "LT_Origin_Manifests", lf_optional=True))
wf(MF, "LT_Destination_Unit__c", lookup("LT_Destination_Unit__c", "Unidade de Destino",
   "Base de destino da mini transferencia.", "LT_Logistics_Unit__c", "Romaneios de Destino", "LT_Destination_Manifests", lf_optional=True))
wf(MF, "LT_Distance_Km__c", field("LT_Distance_Km__c", "Distancia (km)",
   "Distancia entre origem e destino. Mini Transferencia so e elegivel acima de 60 km.", "Number", precision=6, scale=1))
wf(MF, "LT_Rate_Per_Package__c", field("LT_Rate_Per_Package__c", "Valor por Pacote",
   "Valor pago ao motorista por pacote coletado/transferido.", "Currency", precision=8, scale=2, required=True))
wf(MF, "LT_Bonus_Adjustment__c", field("LT_Bonus_Adjustment__c", "Bonus / Ajuste",
   "Bonus ou ajuste manual sobre o valor bruto.", "Currency", precision=10, scale=2))
wf(MF, "LT_Payment_Status__c", picklist("LT_Payment_Status__c", "Status do Pagamento",
   "Etapa de conferencia e pagamento do romaneio.", PAYS, default="Em Conferencia"))
wf(MF, "LT_Approved_By__c", lookup("LT_Approved_By__c", "Aprovado Por",
   "Usuario que aprovou o romaneio para pagamento.", "User", "Romaneios Aprovados", "LT_Approved_Manifests", track=False, lf_optional=True))
wf(MF, "LT_Payment_Date__c", field("LT_Payment_Date__c", "Data do Pagamento", "Data em que o romaneio foi pago.", "Date"))
wf(MF, "LT_Notes__c", field("LT_Notes__c", "Observacoes", "Observacoes do romaneio.", "LongTextArea", length=4000, lines=3, track=False))
wf(MF, "LT_Total_Packages__c", rollup("LT_Total_Packages__c", "Total de Pacotes",
   "Soma dos pacotes das linhas do romaneio.", "LT_Manifest_Line__c", "LT_Manifest__c", "sum", summ_field="LT_Package_Count__c"))
wf(MF, "LT_Line_Count__c", rollup("LT_Line_Count__c", "Qtd. de Linhas",
   "Quantidade de linhas do romaneio.", "LT_Manifest_Line__c", "LT_Manifest__c", "count"))
wf(MF, "LT_Gross_Amount__c", formula("LT_Gross_Amount__c", "Valor Bruto",
   "Total de Pacotes x Valor por Pacote.", "Currency",
   'BLANKVALUE(LT_Total_Packages__c, 0) * BLANKVALUE(LT_Rate_Per_Package__c, 0)', precision=16, scale=2))
wf(MF, "LT_Net_Amount__c", formula("LT_Net_Amount__c", "Valor Liquido",
   "Valor Bruto + Bonus / Ajuste.", "Currency",
   'LT_Gross_Amount__c + BLANKVALUE(LT_Bonus_Adjustment__c, 0)', precision=16, scale=2))
wf(MF, "LT_Driver_Category__c", formula("LT_Driver_Category__c", "Categoria do Motorista",
   "Categoria do motorista do romaneio (deve pagar por Romaneio).", "Text",
   'TEXT(LT_Driver__r.LT_Category_Code__c)'))

wv(MF, "LT_Manifest_Driver_Pay_Model", "O motorista do romaneio precisa ser pago por Romaneio (Coleta ou MR).",
   'NOT(CONTAINS(LT_Driver__r.LT_Payment_Model__c, "Romaneio"))',
   "Romaneios so podem ser emitidos para motoristas das categorias Coleta ou Mini Transferencia.", "LT_Driver__c")
wv(MF, "LT_Manifest_MR_Requires_Destination", "Mini Transferencia exige unidade de destino.",
   'AND(ISPICKVAL(LT_Manifest_Type__c, "Mini Transferencia (MR)"), ISBLANK(LT_Destination_Unit__c))',
   "Informe a Unidade de Destino da mini transferencia.", "LT_Destination_Unit__c")
wv(MF, "LT_Manifest_MR_Distance", "Mini Transferencia so e elegivel para destinos a mais de 60 km.",
   'AND(ISPICKVAL(LT_Manifest_Type__c, "Mini Transferencia (MR)"), NOT(ISBLANK(LT_Distance_Km__c)), LT_Distance_Km__c &lt;= 60)',
   "Rota de Mini Transferencia exige destino a mais de 60 km da base mais proxima.", "LT_Distance_Km__c")
wv(MF, "LT_Manifest_Rate_Positive", "O valor por pacote deve ser maior que zero.",
   'LT_Rate_Per_Package__c &lt;= 0',
   "Informe um Valor por Pacote maior que zero.", "LT_Rate_Per_Package__c")
wv(MF, "LT_Manifest_Approved_Requires_Approver", "Romaneio aprovado ou pago exige o aprovador.",
   'AND(OR(ISPICKVAL(LT_Payment_Status__c, "Aprovado"), ISPICKVAL(LT_Payment_Status__c, "Pago")), ISBLANK(LT_Approved_By__c))',
   "Informe quem aprovou o romaneio.", "LT_Approved_By__c")
wv(MF, "LT_Manifest_Paid_Requires_Date", "Romaneio pago exige a data do pagamento.",
   'AND(ISPICKVAL(LT_Payment_Status__c, "Pago"), ISBLANK(LT_Payment_Date__c))',
   "Informe a Data do Pagamento.", "LT_Payment_Date__c")

open(os.path.join(MF, "compactLayouts", "LT_Manifest_Summary.compactLayout-meta.xml"), "w", encoding="utf-8", newline="\n").write(
   compact("LT_Manifest_Summary", "Romaneio - Resumo",
           ["Name", "LT_Driver__c", "LT_Manifest_Type__c", "LT_Reference_Date__c", "LT_Net_Amount__c", "LT_Payment_Status__c"]))
open(os.path.join(MF, "listViews", "All.listView-meta.xml"), "w", encoding="utf-8", newline="\n").write(
   listview("All", "Todos", ["NAME", "LT_Driver__c", "LT_Manifest_Type__c", "LT_Reference_Date__c", "LT_Total_Packages__c", "LT_Net_Amount__c", "LT_Payment_Status__c"]))
open(os.path.join(MF, "listViews", "A_Pagar.listView-meta.xml"), "w", encoding="utf-8", newline="\n").write(
   listview("A_Pagar", "Romaneios a Pagar",
            ["NAME", "LT_Driver__c", "LT_Manifest_Type__c", "LT_Reference_Date__c", "LT_Net_Amount__c", "LT_Payment_Status__c"],
            filters=[("LT_Payment_Status__c", "equals", "Aprovado")]))

wobj(MF, "LT_Manifest__c", "Romaneio", "Romaneios", "Numero do Romaneio", "AutoNumber", "RMN-{000000}", compact="LT_Manifest_Summary")

# ==================== LT_Manifest_Line__c ====================
wf(ML, "LT_Manifest__c", mdfield("LT_Manifest__c", "Romaneio", "Romaneio a que a linha pertence.",
   "LT_Manifest__c", "Linhas do Romaneio", "LT_Manifest_Lines"))
wf(ML, "LT_Pickup_Request__c", lookup("LT_Pickup_Request__c", "Solicitacao de Coleta",
   "Coleta que esta linha representa.", "LT_Pickup_Request__c", "Linhas de Romaneio", "LT_Manifest_Lines", lf_optional=True, track=False))
wf(ML, "LT_Shipment__c", lookup("LT_Shipment__c", "Remessa",
   "Remessa individual transferida (mini transferencia).", "LT_Shipment__c", "Linhas de Romaneio", "LT_Manifest_Lines", lf_optional=True, track=False))
wf(ML, "LT_Package_Count__c", field("LT_Package_Count__c", "Qtd. de Pacotes",
   "Quantidade de pacotes desta linha.", "Number", precision=6, scale=0, required=True, track=False))
wf(ML, "LT_Collection_City__c", field("LT_Collection_City__c", "Cidade", "Cidade da coleta/transferencia desta linha.", "Text", length=80, track=False))
wf(ML, "LT_Description__c", field("LT_Description__c", "Descricao", "Descricao da linha.", "Text", length=255, track=False))

wv(ML, "LT_Line_Package_Count_Positive", "A quantidade de pacotes deve ser maior que zero.",
   'LT_Package_Count__c &lt;= 0',
   "Informe uma quantidade de pacotes maior que zero.", "LT_Package_Count__c")

open(os.path.join(ML, "compactLayouts", "LT_Manifest_Line_Summary.compactLayout-meta.xml"), "w", encoding="utf-8", newline="\n").write(
   compact("LT_Manifest_Line_Summary", "Linha do Romaneio - Resumo",
           ["Name", "LT_Manifest__c", "LT_Package_Count__c", "LT_Collection_City__c"]))
open(os.path.join(ML, "listViews", "All.listView-meta.xml"), "w", encoding="utf-8", newline="\n").write(
   listview("All", "Todas", ["NAME", "LT_Manifest__c", "LT_Package_Count__c", "LT_Collection_City__c", "LT_Pickup_Request__c"]))

wobj(ML, "LT_Manifest_Line__c", "Linha do Romaneio", "Linhas do Romaneio",
     "Codigo da Linha", "AutoNumber", "LR-{000000}", compact="LT_Manifest_Line_Summary", mdchild=True)

# ==================== layouts ====================
simple_layout(os.path.join(ROOT, "layouts", "LT_Pickup_Request__c-Solicitacao de Coleta Layout.layout-meta.xml"), [
  ("Solicitacao", "TwoColumnsLeftToRight", [
    [("Readonly", "Name"), ("Edit", "LT_Pickup_Type__c"), ("Edit", "LT_Status__c"), ("Edit", "LT_Requested_By__c")],
    [("Edit", "LT_Shipper__c"), ("Edit", "LT_Pickup_Point__c"), ("Edit", "LT_Origin_Base__c"), ("Edit", "LT_Destination_CD__c")]]),
  ("Local e Janela", "TwoColumnsLeftToRight", [
    [("Edit", "LT_Pickup_Address__c"), ("Edit", "LT_Pickup_City__c"), ("Edit", "LT_Pickup_State__c")],
    [("Edit", "LT_Scheduled_Date__c"), ("Edit", "LT_Window_Start__c"), ("Edit", "LT_Window_End__c")]]),
  ("Execucao", "TwoColumnsLeftToRight", [
    [("Edit", "LT_First_Mile_Driver__c"), ("Edit", "LT_Estimated_Packages__c"), ("Edit", "LT_Collected_Packages__c")],
    [("Readonly", "LT_Fill_Rate__c"), ("Edit", "LT_Completed_DateTime__c"), ("Edit", "LT_Manifest__c")]]),
  ("C2C - Venda de Etiqueta", "TwoColumnsLeftToRight", [
    [("Edit", "LT_C2C_Sender_Name__c"), ("Edit", "LT_C2C_Recipient_Name__c")],
    [("Edit", "LT_C2C_Dest_City__c"), ("Edit", "LT_Notes__c")]]),
], related=["LT_Manifest_Line__c.LT_Pickup_Request__c", "RelatedHistoryList"])

simple_layout(os.path.join(ROOT, "layouts", "LT_Manifest__c-Romaneio Layout.layout-meta.xml"), [
  ("Romaneio", "TwoColumnsLeftToRight", [
    [("Readonly", "Name"), ("Required", "LT_Driver__c"), ("Edit", "LT_Manifest_Type__c"), ("Required", "LT_Reference_Date__c"), ("Readonly", "LT_Driver_Category__c")],
    [("Edit", "LT_Origin_Unit__c"), ("Edit", "LT_Destination_Unit__c"), ("Edit", "LT_Distance_Km__c")]]),
  ("Valores", "TwoColumnsLeftToRight", [
    [("Readonly", "LT_Total_Packages__c"), ("Readonly", "LT_Line_Count__c"), ("Required", "LT_Rate_Per_Package__c")],
    [("Readonly", "LT_Gross_Amount__c"), ("Edit", "LT_Bonus_Adjustment__c"), ("Readonly", "LT_Net_Amount__c")]]),
  ("Pagamento", "TwoColumnsLeftToRight", [
    [("Edit", "LT_Payment_Status__c"), ("Edit", "LT_Approved_By__c")],
    [("Edit", "LT_Payment_Date__c"), ("Edit", "LT_Notes__c")]]),
], related=["LT_Manifest_Line__c.LT_Manifest__c", "LT_Pickup_Request__c.LT_Manifest__c", "RelatedHistoryList"])

simple_layout(os.path.join(ROOT, "layouts", "LT_Manifest_Line__c-Linha do Romaneio Layout.layout-meta.xml"), [
  ("Linha", "TwoColumnsLeftToRight", [
    [("Required", "LT_Manifest__c"), ("Required", "LT_Package_Count__c"), ("Edit", "LT_Collection_City__c")],
    [("Edit", "LT_Pickup_Request__c"), ("Edit", "LT_Shipment__c"), ("Edit", "LT_Description__c")]]),
])

print("Pickup:", len(os.listdir(os.path.join(PR, "fields"))),
      "| Manifest:", len(os.listdir(os.path.join(MF, "fields"))),
      "| Line:", len(os.listdir(os.path.join(ML, "fields"))))
