#!/usr/bin/env python3
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from metahelp import *

ROOT = r"C:\Users\Robert Luis\Desktop\LogiTrack-SFDX\force-app\main\default"
RT = os.path.join(ROOT, "objects", "LT_Route__c")
DA = os.path.join(ROOT, "objects", "LT_Delivery_Attempt__c")
ensure(RT); ensure(DA)

# ==================== LT_Route__c ====================
RSTATUS = ["Planejada", "Em Triagem", "Carregada", "Em Rota", "Concluida", "Cancelada"]
RTYPE = ["Last Mile (Entrega)", "Mini Transferencia"]

wf(RT, "LT_Base__c", lookup("LT_Base__c", "Base de Entrega",
   "Base que monta e despacha a rota.", "LT_Logistics_Unit__c", "Rotas", "LT_Routes",
   required=True, delete="Restrict",
   lf_items=[("LT_Logistics_Unit__c.Unit_Type__c", "equals", "Base de Entrega")],
   lf_msg="A rota deve partir de uma Base de Entrega."))
wf(RT, "LT_Route_Date__c", field("LT_Route_Date__c", "Data da Rota", "Dia de operacao da rota.", "Date", required=True))
wf(RT, "LT_Route_Type__c", picklist("LT_Route_Type__c", "Tipo de Rota",
   "Rota de entrega Last Mile ou de Mini Transferencia entre unidades.", RTYPE, default="Last Mile (Entrega)"))
wf(RT, "LT_Status__c", picklist("LT_Status__c", "Status da Rota", "Etapa atual da rota.", RSTATUS, default="Planejada"))
wf(RT, "LT_Driver__c", lookup("LT_Driver__c", "Motorista", "Motorista responsavel pela rota.",
   "LT_Driver__c", "Rotas", "LT_Routes", lf_optional=True))
wf(RT, "LT_Vehicle__c", lookup("LT_Vehicle__c", "Veiculo", "Veiculo utilizado na rota.",
   "LT_Vehicle__c", "Rotas", "LT_Routes", lf_optional=True, track=False))
wf(RT, "LT_Target_City__c", field("LT_Target_City__c", "Cidade Alvo", "Cidade predominante da rota.", "Text", length=80, track=False))
wf(RT, "LT_Destination_Unit__c", lookup("LT_Destination_Unit__c", "Unidade de Destino",
   "Unidade de destino da mini transferencia.", "LT_Logistics_Unit__c", "Rotas de Destino", "LT_Destination_Routes", lf_optional=True))
wf(RT, "LT_Cage_Code__c", field("LT_Cage_Code__c", "Gaiola", "Identificador da gaiola da rota na base.", "Text", length=20, track=False))
wf(RT, "LT_Distance_Km__c", field("LT_Distance_Km__c", "Distancia (km)",
   "Distancia da rota. Mini Transferencia so e elegivel acima de 60 km.", "Number", precision=6, scale=1))
wf(RT, "LT_Planned_Packages__c", field("LT_Planned_Packages__c", "Pacotes Planejados", "Quantidade prevista de pacotes na rota.", "Number", precision=6, scale=0))
wf(RT, "LT_Loaded_Packages__c", field("LT_Loaded_Packages__c", "Pacotes Carregados", "Quantidade efetivamente bipada / carregada.", "Number", precision=6, scale=0))
wf(RT, "LT_Departure_Time__c", field("LT_Departure_Time__c", "Saida", "Data/hora de saida do motorista.", "DateTime", track=False))
wf(RT, "LT_Return_Time__c", field("LT_Return_Time__c", "Retorno", "Data/hora de retorno do motorista.", "DateTime", track=False))
wf(RT, "LT_Notes__c", field("LT_Notes__c", "Observacoes", "Observacoes da rota.", "LongTextArea", length=4000, lines=3, track=False))

wf(RT, "LT_Attempts_Count__c", rollup("LT_Attempts_Count__c", "Tentativas na Rota",
   "Total de tentativas de entrega registradas na rota.", "LT_Delivery_Attempt__c", "LT_Route__c", "count"))
wf(RT, "LT_Delivered_Count__c", rollup("LT_Delivered_Count__c", "Entregas Concluidas",
   "Tentativas com resultado Entregue na rota.", "LT_Delivery_Attempt__c", "LT_Route__c", "count",
   filters=[("LT_Is_Success__c", "equals", "true")]))
wf(RT, "LT_Success_Rate__c", formula("LT_Success_Rate__c", "Taxa de Sucesso",
   "Percentual de tentativas da rota com entrega concluida.", "Percent",
   'IF(OR(ISBLANK(LT_Attempts_Count__c), LT_Attempts_Count__c = 0), 0, LT_Delivered_Count__c / LT_Attempts_Count__c)',
   precision=5, scale=2))
wf(RT, "LT_MR_Eligible__c", formula("LT_MR_Eligible__c", "MR Elegivel",
   "Mini Transferencia so e valida para destinos a mais de 60 km.", "Checkbox",
   'OR(NOT(ISPICKVAL(LT_Route_Type__c, "Mini Transferencia")), AND(NOT(ISBLANK(LT_Distance_Km__c)), LT_Distance_Km__c &gt; 60))'))
wf(RT, "LT_Driver_Max_Packages__c", formula("LT_Driver_Max_Packages__c", "Limite do Motorista",
   "Maximo de pacotes por frete da categoria do motorista (0 = sem limite).", "Number",
   'BLANKVALUE(LT_Driver__r.LT_Max_Packages_Per_Trip__c, 0)', precision=6, scale=0))

wv(RT, "LT_Route_MR_Distance", "Mini Transferencia exige destino a mais de 60 km.",
   'AND(ISPICKVAL(LT_Route_Type__c, "Mini Transferencia"), NOT(ISBLANK(LT_Distance_Km__c)), LT_Distance_Km__c &lt;= 60)',
   "Rota de Mini Transferencia so e elegivel para destinos a mais de 60 km da base mais proxima.", "LT_Distance_Km__c")
wv(RT, "LT_Route_MR_Requires_Destination", "Mini Transferencia exige unidade de destino.",
   'AND(ISPICKVAL(LT_Route_Type__c, "Mini Transferencia"), ISBLANK(LT_Destination_Unit__c))',
   "Informe a Unidade de Destino da mini transferencia.", "LT_Destination_Unit__c")
wv(RT, "LT_Route_In_Route_Requires_Driver", "Rota Em Rota ou Concluida exige motorista.",
   'AND(OR(ISPICKVAL(LT_Status__c, "Em Rota"), ISPICKVAL(LT_Status__c, "Concluida")), ISBLANK(LT_Driver__c))',
   "Defina o motorista antes de colocar a rota Em Rota.", "LT_Driver__c")
wv(RT, "LT_Route_Loaded_Not_Above_Planned", "Pacotes carregados nao podem exceder o planejado.",
   'AND(NOT(ISBLANK(LT_Planned_Packages__c)), LT_Loaded_Packages__c &gt; LT_Planned_Packages__c)',
   "Pacotes Carregados nao pode ser maior que Pacotes Planejados.", "LT_Loaded_Packages__c")
wv(RT, "LT_Route_Packages_Positive", "Quantidades de pacotes nao podem ser negativas.",
   'OR(LT_Planned_Packages__c &lt; 0, LT_Loaded_Packages__c &lt; 0)',
   "As quantidades de pacotes nao podem ser negativas.")
wv(RT, "LT_Route_Concluded_Requires_Return", "Rota Concluida exige data/hora de retorno.",
   'AND(ISPICKVAL(LT_Status__c, "Concluida"), ISBLANK(LT_Return_Time__c))',
   "Informe o horario de Retorno ao concluir a rota.", "LT_Return_Time__c")
wv(RT, "LT_Route_Driver_Capacity", "Carga da rota acima do limite da categoria do motorista.",
   'AND(NOT(ISBLANK(LT_Driver__c)), LT_Driver__r.LT_Max_Packages_Per_Trip__c &gt; 0, LT_Loaded_Packages__c &gt; LT_Driver__r.LT_Max_Packages_Per_Trip__c)',
   "A carga da rota excede o maximo de pacotes por frete da categoria do motorista.", "LT_Loaded_Packages__c")

open(os.path.join(RT, "compactLayouts", "LT_Route_Summary.compactLayout-meta.xml"), "w", encoding="utf-8", newline="\n").write(
   compact("LT_Route_Summary", "Rota - Resumo",
           ["Name", "LT_Base__c", "LT_Route_Date__c", "LT_Status__c", "LT_Driver__c", "LT_Success_Rate__c"]))
open(os.path.join(RT, "listViews", "All.listView-meta.xml"), "w", encoding="utf-8", newline="\n").write(
   listview("All", "Todas", ["NAME", "LT_Base__c", "LT_Route_Date__c", "LT_Route_Type__c", "LT_Status__c", "LT_Driver__c", "LT_Loaded_Packages__c"]))
open(os.path.join(RT, "listViews", "Em_Rota.listView-meta.xml"), "w", encoding="utf-8", newline="\n").write(
   listview("Em_Rota", "Rotas Em Andamento",
            ["NAME", "LT_Base__c", "LT_Route_Date__c", "LT_Driver__c", "LT_Loaded_Packages__c", "LT_Success_Rate__c"],
            filters=[("LT_Status__c", "equals", "Em Rota,Carregada")]))

wobj(RT, "LT_Route__c", "Rota", "Rotas", "Codigo da Rota", "AutoNumber", "ROT-{000000}", compact="LT_Route_Summary")

# ==================== LT_Delivery_Attempt__c ====================
RESULT = ["Entregue", "Destinatario Ausente", "Endereco Nao Localizado", "Recusado pelo Destinatario",
          "Avaria Identificada", "Area de Risco", "Estabelecimento Fechado", "Cliente Remarcou"]
RELN = ["Proprio", "Familiar", "Porteiro", "Vizinho", "Funcionario", "Outro"]

wf(DA, "LT_Shipment__c", lookup("LT_Shipment__c", "Remessa", "Remessa alvo da tentativa de entrega.",
   "LT_Shipment__c", "Tentativas de Entrega", "LT_Delivery_Attempts", required=True, delete="Restrict"))
wf(DA, "LT_Route__c", lookup("LT_Route__c", "Rota", "Rota em que a tentativa foi realizada.",
   "LT_Route__c", "Tentativas de Entrega", "LT_Delivery_Attempts", lf_optional=True))
wf(DA, "LT_Driver__c", lookup("LT_Driver__c", "Motorista", "Motorista que realizou a tentativa.",
   "LT_Driver__c", "Tentativas de Entrega", "LT_Delivery_Attempts", lf_optional=True, track=False))
wf(DA, "LT_Attempt_Number__c", field("LT_Attempt_Number__c", "Numero da Tentativa", "Sequencial da tentativa para a remessa.", "Number", precision=2, scale=0, track=False))
wf(DA, "LT_Attempt_DateTime__c", field("LT_Attempt_DateTime__c", "Data/Hora da Tentativa", "Momento da tentativa.", "DateTime", required=True, track=False))
wf(DA, "LT_Result__c", picklist("LT_Result__c", "Resultado", "Resultado da tentativa de entrega.", RESULT, track=False))
wf(DA, "LT_Recipient_Doc__c", field("LT_Recipient_Doc__c", "Documento do Recebedor", "Documento de quem recebeu (entregas concluidas).", "Text", length=30, track=False))
wf(DA, "LT_Recipient_Relationship__c", picklist("LT_Recipient_Relationship__c", "Relacao do Recebedor",
   "Relacao de quem recebeu com o destinatario.", RELN, track=False))
wf(DA, "LT_Geolocation__c", """<?xml version="1.0" encoding="UTF-8"?>
<CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>LT_Geolocation__c</fullName>
    <description>Coordenadas registradas no momento da tentativa.</description>
    <label>Geolocalizacao</label>
    <displayLocationInDecimal>true</displayLocationInDecimal>
    <required>false</required>
    <scale>6</scale>
    <type>Location</type>
</CustomField>""")
wf(DA, "LT_Photo_Link__c", field("LT_Photo_Link__c", "Link da Foto", "Link para a foto do comprovante de entrega.", "Url", track=False))
wf(DA, "LT_Notes__c", field("LT_Notes__c", "Observacoes", "Observacoes da tentativa.", "Text", length=255, track=False))
wf(DA, "LT_Is_Success__c", formula("LT_Is_Success__c", "Entrega Concluida",
   "Verdadeiro quando a tentativa resultou em entrega.", "Checkbox",
   'ISPICKVAL(LT_Result__c, "Entregue")'))

wv(DA, "LT_Attempt_Delivered_Requires_Receiver", "Entrega concluida exige documento e motorista.",
   'AND(ISPICKVAL(LT_Result__c, "Entregue"), OR(ISBLANK(LT_Recipient_Doc__c), ISBLANK(LT_Driver__c)))',
   "Para registrar Entregue informe o documento do recebedor e o motorista.", "LT_Recipient_Doc__c")
wv(DA, "LT_Attempt_Not_Future", "A tentativa nao pode ter data futura.",
   'LT_Attempt_DateTime__c &gt; NOW() + 0.0417',
   "A Data/Hora da Tentativa nao pode estar no futuro.", "LT_Attempt_DateTime__c")
wv(DA, "LT_Attempt_Number_Positive", "O numero da tentativa deve ser maior que zero.",
   'LT_Attempt_Number__c &lt;= 0',
   "Informe um Numero da Tentativa maior que zero.", "LT_Attempt_Number__c")

open(os.path.join(DA, "compactLayouts", "LT_Delivery_Attempt_Summary.compactLayout-meta.xml"), "w", encoding="utf-8", newline="\n").write(
   compact("LT_Delivery_Attempt_Summary", "Tentativa - Resumo",
           ["Name", "LT_Shipment__c", "LT_Result__c", "LT_Attempt_DateTime__c", "LT_Driver__c"]))
open(os.path.join(DA, "listViews", "All.listView-meta.xml"), "w", encoding="utf-8", newline="\n").write(
   listview("All", "Todas", ["NAME", "LT_Shipment__c", "LT_Route__c", "LT_Result__c", "LT_Attempt_DateTime__c", "LT_Driver__c"]))

wobj(DA, "LT_Delivery_Attempt__c", "Tentativa de Entrega", "Tentativas de Entrega",
     "Codigo da Tentativa", "AutoNumber", "TE-{000000}", compact="LT_Delivery_Attempt_Summary")

# ==================== layouts ====================
simple_layout(os.path.join(ROOT, "layouts", "LT_Route__c-Rota Layout.layout-meta.xml"), [
  ("Planejamento", "TwoColumnsLeftToRight", [
    [("Readonly", "Name"), ("Required", "LT_Base__c"), ("Required", "LT_Route_Date__c"), ("Edit", "LT_Route_Type__c"), ("Edit", "LT_Status__c")],
    [("Edit", "LT_Driver__c"), ("Edit", "LT_Vehicle__c"), ("Edit", "LT_Target_City__c"), ("Edit", "LT_Cage_Code__c")]]),
  ("Carga e Distancia", "TwoColumnsLeftToRight", [
    [("Edit", "LT_Planned_Packages__c"), ("Edit", "LT_Loaded_Packages__c"), ("Readonly", "LT_Driver_Max_Packages__c")],
    [("Edit", "LT_Distance_Km__c"), ("Edit", "LT_Destination_Unit__c"), ("Readonly", "LT_MR_Eligible__c")]]),
  ("Execucao", "TwoColumnsLeftToRight", [
    [("Edit", "LT_Departure_Time__c"), ("Edit", "LT_Return_Time__c")],
    [("Readonly", "LT_Attempts_Count__c"), ("Readonly", "LT_Delivered_Count__c"), ("Readonly", "LT_Success_Rate__c")]]),
  ("Observacoes", "OneColumn", [[("Edit", "LT_Notes__c")]]),
], related=["LT_Delivery_Attempt__c.LT_Route__c", "RelatedHistoryList"])

simple_layout(os.path.join(ROOT, "layouts", "LT_Delivery_Attempt__c-Tentativa de Entrega Layout.layout-meta.xml"), [
  ("Tentativa", "TwoColumnsLeftToRight", [
    [("Readonly", "Name"), ("Required", "LT_Shipment__c"), ("Edit", "LT_Route__c"), ("Edit", "LT_Driver__c")],
    [("Edit", "LT_Attempt_Number__c"), ("Required", "LT_Attempt_DateTime__c"), ("Edit", "LT_Result__c"), ("Readonly", "LT_Is_Success__c")]]),
  ("Comprovacao", "TwoColumnsLeftToRight", [
    [("Edit", "LT_Recipient_Doc__c"), ("Edit", "LT_Recipient_Relationship__c")],
    [("Edit", "LT_Geolocation__c"), ("Edit", "LT_Photo_Link__c"), ("Edit", "LT_Notes__c")]]),
])

print("Route:", len(os.listdir(os.path.join(RT, "fields"))), "| Attempt:", len(os.listdir(os.path.join(DA, "fields"))))
