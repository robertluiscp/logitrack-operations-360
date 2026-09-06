#!/usr/bin/env python3
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from metahelp import *

ROOT = r"C:\Users\Robert Luis\Desktop\LogiTrack-SFDX\force-app\main\default"
S = os.path.join(ROOT, "objects", "LT_Shipment__c")
E = os.path.join(ROOT, "objects", "LT_Tracking_Event__c")
ensure(S); ensure(E)

STATUS = ["Etiqueta Gerada", "Coletado", "Em Triagem no SC", "Em Transferencia",
          "Recebido na Base", "Em Triagem na Base", "Em Rota de Entrega", "Tentativa de Entrega",
          "Entregue", "Retido", "Sem Movimentacao", "Devolvido ao Remetente", "Extraviado"]
HOLDER = ["Ponto de Coleta", "Motorista de Coleta", "Centro de Distribuicao", "Em Transferencia",
          "Base de Entrega", "Motorista Last Mile", "Entregue", "Devolvido"]
MKT = ["Shopee", "Mercado Livre", "Shein", "TikTok Shop", "Amazon", "AliExpress", "Magalu",
       "Loja Propria", "C2C - Venda de Etiqueta", "Outro"]
COLL = ["Coleta no Seller", "Coleta no DropOff", "C2C - Venda de Etiqueta"]
PKG = ["Pacote", "Envelope", "Caixa", "Volume Grande"]

# ================= LT_Shipment__c =================
wf(S, "LT_Tracking_Code__c", field("LT_Tracking_Code__c", "Codigo de Rastreio",
   "Codigo unico de rastreio da remessa (visivel ao destinatario).", "Text",
   length=20, unique=True, extid=True, required=True,
   help="Codigo unico da remessa, ex.: LT771234567BR."))
wf(S, "LT_Shipper__c", lookup("LT_Shipper__c", "Embarcador",
   "Embarcador (cliente) dono da remessa.", "Account", "Remessas", "LT_Shipments",
   required=True, delete="Restrict",
   lf_items=[("Account.RecordType.DeveloperName", "equals", "LT_Shipper")],
   lf_msg="A remessa deve pertencer a uma conta do tipo Embarcador."))
wf(S, "LT_Origin_Marketplace__c", picklist("LT_Origin_Marketplace__c", "Marketplace de Origem",
   "Canal / marketplace que originou o pedido.", MKT))
wf(S, "LT_Collection_Type__c", picklist("LT_Collection_Type__c", "Tipo de Coleta",
   "Como a remessa entrou na malha LogiTrack.", COLL))
wf(S, "LT_Package_Type__c", picklist("LT_Package_Type__c", "Tipo de Volume", "Formato fisico da remessa.", PKG, default="Pacote"))
wf(S, "LT_Sender_Name__c", field("LT_Sender_Name__c", "Remetente", "Nome do remetente.", "Text", length=120, track=False))
wf(S, "LT_Recipient_Name__c", field("LT_Recipient_Name__c", "Destinatario", "Nome do destinatario.", "Text", length=120, required=True, track=False))
wf(S, "LT_Recipient_Phone__c", field("LT_Recipient_Phone__c", "Telefone do Destinatario", "Telefone de contato do destinatario.", "Phone", track=False))
wf(S, "LT_Dest_Street__c", field("LT_Dest_Street__c", "Endereco de Entrega", "Logradouro e numero de entrega.", "Text", length=255, track=False))
wf(S, "LT_Dest_District__c", field("LT_Dest_District__c", "Bairro", "Bairro de entrega.", "Text", length=80, track=False))
wf(S, "LT_Dest_City__c", field("LT_Dest_City__c", "Cidade de Destino", "Cidade de destino da remessa.", "Text", length=80, required=True, track=False))
wf(S, "LT_Dest_State__c", gvs_picklist("LT_Dest_State__c", "UF de Destino", "Estado de destino da remessa.", "Brazilian_States"))
wf(S, "LT_Dest_ZIP__c", field("LT_Dest_ZIP__c", "CEP de Destino", "CEP de destino (formato 00000-000).", "Text", length=9, required=True, track=False,
   help="Informe o CEP no formato 00000-000."))
wf(S, "LT_Weight_Kg__c", field("LT_Weight_Kg__c", "Peso (kg)", "Peso da remessa em quilogramas.", "Number", precision=6, scale=3, track=False))
wf(S, "LT_Declared_Value__c", field("LT_Declared_Value__c", "Valor Declarado", "Valor declarado do conteudo (base para ressarcimento em extravio).", "Currency", precision=12, scale=2))

wf(S, "LT_Origin_Pickup_Point__c", lookup("LT_Origin_Pickup_Point__c", "Ponto de Coleta (DropOff)",
   "Ponto de coleta fisico onde a remessa foi deixada (coletas DropOff).", "Account",
   "Remessas Coletadas", "LT_DropOff_Shipments",
   lf_items=[("Account.LT_Operating_Partner_Type__c", "equals", "Parceiro DropOff")],
   lf_msg="Selecione uma conta do tipo Parceiro DropOff.", lf_optional=True))
wf(S, "LT_Destination_CD__c", lookup("LT_Destination_CD__c", "Centro de Distribuicao de Destino",
   "SC responsavel por triar e redistribuir a remessa.", "LT_Logistics_Unit__c",
   "Remessas (CD de Destino)", "LT_Shipments_As_CD",
   lf_items=[("LT_Logistics_Unit__c.Unit_Type__c", "equals", "Centro de Distribuicao")],
   lf_msg="Selecione um Centro de Distribuicao.", lf_optional=True))
wf(S, "LT_Delivery_Base__c", lookup("LT_Delivery_Base__c", "Base de Entrega",
   "Base de entrega responsavel pela ultima milha.", "LT_Logistics_Unit__c",
   "Remessas (Base de Entrega)", "LT_Shipments_As_Base",
   lf_items=[("LT_Logistics_Unit__c.Unit_Type__c", "equals", "Base de Entrega")],
   lf_msg="Selecione uma Base de Entrega.", lf_optional=True))
wf(S, "LT_Last_Mile_Driver__c", lookup("LT_Last_Mile_Driver__c", "Motorista Last Mile",
   "Motorista responsavel pela entrega final.", "LT_Driver__c",
   "Remessas Entregues", "LT_LastMile_Shipments", lf_optional=True))

wf(S, "LT_Status__c", picklist("LT_Status__c", "Status da Remessa",
   "Etapa atual da remessa no fluxo operacional.", STATUS, default="Etiqueta Gerada",
   helptext="Atualizado automaticamente pelos eventos de rastreamento."))
wf(S, "LT_Current_Holder__c", picklist("LT_Current_Holder__c", "Responsavel Atual",
   "Quem esta com a remessa neste momento.", HOLDER))
wf(S, "LT_Posted_Date__c", field("LT_Posted_Date__c", "Data de Postagem", "Data/hora em que a etiqueta foi gerada / o pedido foi postado.", "DateTime"))
wf(S, "LT_Collected_Date__c", field("LT_Collected_Date__c", "Data da Coleta", "Data/hora da coleta da remessa.", "DateTime"))
wf(S, "LT_SLA_Deadline__c", field("LT_SLA_Deadline__c", "Prazo de Entrega (SLA)", "Data limite de entrega acordada.", "Date", required=True))
wf(S, "LT_Delivered_Date__c", field("LT_Delivered_Date__c", "Data da Entrega", "Data/hora da entrega ao destinatario.", "DateTime"))
wf(S, "LT_Delivery_Attempts__c", field("LT_Delivery_Attempts__c", "Tentativas de Entrega", "Numero de tentativas de entrega realizadas.", "Number", precision=2, scale=0, default="0"))
wf(S, "LT_Value_Reimbursed__c", field("LT_Value_Reimbursed__c", "Valor Ressarcido", "Marcado quando o embarcador foi ressarcido por extravio.", "Checkbox", default="false"))

# roll-ups from tracking events
wf(S, "LT_Event_Count__c", rollup("LT_Event_Count__c", "Qtd. de Eventos",
   "Quantidade de eventos de rastreamento da remessa.", "LT_Tracking_Event__c", "LT_Shipment__c", "count"))
wf(S, "LT_Last_Event_Date__c", rollup("LT_Last_Event_Date__c", "Ultimo Evento em",
   "Data/hora do evento de rastreamento mais recente.", "LT_Tracking_Event__c", "LT_Shipment__c", "max",
   summ_field="LT_Event_DateTime__c"))

# formulas
wf(S, "LT_Is_Delivered__c", formula("LT_Is_Delivered__c", "Entregue",
   "Verdadeiro quando a remessa esta com status Entregue.", "Checkbox",
   'ISPICKVAL(LT_Status__c, "Entregue")'))
wf(S, "LT_Is_Terminal__c", formula("LT_Is_Terminal__c", "Fluxo Encerrado",
   "Verdadeiro quando a remessa chegou a um status final.", "Checkbox",
   'OR(ISPICKVAL(LT_Status__c, "Entregue"), ISPICKVAL(LT_Status__c, "Devolvido ao Remetente"), ISPICKVAL(LT_Status__c, "Extraviado"))'))
wf(S, "LT_On_Time__c", formula("LT_On_Time__c", "Entregue no Prazo",
   "Verdadeiro quando a remessa foi entregue ate a data limite do SLA.", "Checkbox",
   'AND(ISPICKVAL(LT_Status__c, "Entregue"), NOT(ISBLANK(LT_Delivered_Date__c)), NOT(ISBLANK(LT_SLA_Deadline__c)), DATEVALUE(LT_Delivered_Date__c) &lt;= LT_SLA_Deadline__c)'))
wf(S, "LT_Is_Late__c", formula("LT_Is_Late__c", "Em Atraso",
   "Verdadeiro quando a remessa passou do prazo sem ter sido entregue no prazo.", "Checkbox",
   'IF(ISPICKVAL(LT_Status__c, "Entregue"), AND(NOT(ISBLANK(LT_Delivered_Date__c)), DATEVALUE(LT_Delivered_Date__c) &gt; LT_SLA_Deadline__c), '
   'AND(NOT(LT_Is_Terminal__c), NOT(ISBLANK(LT_SLA_Deadline__c)), TODAY() &gt; LT_SLA_Deadline__c))'))
wf(S, "LT_Days_In_Transit__c", formula("LT_Days_In_Transit__c", "Dias em Transito",
   "Dias entre a postagem e a entrega (ou hoje, se ainda em transito).", "Number",
   'IF(ISBLANK(LT_Posted_Date__c), NULL, IF(NOT(ISBLANK(LT_Delivered_Date__c)), DATEVALUE(LT_Delivered_Date__c) - DATEVALUE(LT_Posted_Date__c), TODAY() - DATEVALUE(LT_Posted_Date__c)))',
   precision=6, scale=0))
wf(S, "LT_Hours_Without_Movement__c", formula("LT_Hours_Without_Movement__c", "Horas sem Movimentacao",
   "Horas desde o ultimo evento de rastreamento (usado para detectar remessas paradas).", "Number",
   'IF(OR(ISBLANK(LT_Last_Event_Date__c), LT_Is_Terminal__c), 0, (NOW() - LT_Last_Event_Date__c) * 24)',
   precision=6, scale=1))

# validation rules
wv(S, "LT_Shipment_ZIP_Format", "Valida a mascara do CEP (00000-000).",
   'AND(NOT(ISBLANK(LT_Dest_ZIP__c)), NOT(REGEX(LT_Dest_ZIP__c, "^[0-9]{5}-[0-9]{3}$")))',
   "Informe o CEP no formato 00000-000.", "LT_Dest_ZIP__c")
wv(S, "LT_Shipment_Delivered_Requires_Date", "Remessa Entregue precisa da data da entrega.",
   'AND(ISPICKVAL(LT_Status__c, "Entregue"), ISBLANK(LT_Delivered_Date__c))',
   "Informe a Data da Entrega ao marcar a remessa como Entregue.", "LT_Delivered_Date__c")
wv(S, "LT_Shipment_Weight_Value_Positive", "Peso e valor declarado nao podem ser negativos.",
   'OR(LT_Weight_Kg__c &lt; 0, LT_Declared_Value__c &lt; 0)',
   "Peso e valor declarado nao podem ser negativos.")
wv(S, "LT_Shipment_Route_Requires_Driver", "Remessa Em Rota de Entrega precisa de motorista Last Mile.",
   'AND(ISPICKVAL(LT_Status__c, "Em Rota de Entrega"), ISBLANK(LT_Last_Mile_Driver__c))',
   "Defina o Motorista Last Mile ao colocar a remessa Em Rota de Entrega.", "LT_Last_Mile_Driver__c")
wv(S, "LT_Shipment_Base_Statuses_Require_Base", "Status de base exigem a Base de Entrega preenchida.",
   'AND(OR(ISPICKVAL(LT_Status__c, "Recebido na Base"), ISPICKVAL(LT_Status__c, "Em Triagem na Base"), ISPICKVAL(LT_Status__c, "Em Rota de Entrega")), ISBLANK(LT_Delivery_Base__c))',
   "Informe a Base de Entrega para remessas em processamento na base.", "LT_Delivery_Base__c")
wv(S, "LT_Shipment_SLA_After_Posted", "O prazo de entrega nao pode ser anterior a data de postagem.",
   'AND(NOT(ISBLANK(LT_Posted_Date__c)), NOT(ISBLANK(LT_SLA_Deadline__c)), LT_SLA_Deadline__c &lt; DATEVALUE(LT_Posted_Date__c))',
   "O Prazo de Entrega (SLA) nao pode ser anterior a Data de Postagem.", "LT_SLA_Deadline__c")

# compact + list views
open(os.path.join(S, "compactLayouts", "LT_Shipment_Summary.compactLayout-meta.xml"), "w", encoding="utf-8", newline="\n").write(
   compact("LT_Shipment_Summary", "Remessa - Resumo",
           ["LT_Tracking_Code__c", "LT_Status__c", "LT_Current_Holder__c", "LT_Dest_City__c", "LT_SLA_Deadline__c", "LT_Last_Mile_Driver__c"]))
for n, l, cols, fil in [
  ("All", "Todas", ["LT_Tracking_Code__c", "LT_Shipper__c", "LT_Status__c", "LT_Dest_City__c", "LT_Dest_State__c", "LT_SLA_Deadline__c", "LT_Delivery_Base__c"], None),
  ("Em_Transito", "Em Transito", ["LT_Tracking_Code__c", "LT_Status__c", "LT_Current_Holder__c", "LT_Dest_City__c", "LT_SLA_Deadline__c", "LT_Hours_Without_Movement__c"],
   [("LT_Is_Terminal__c", "equals", "0")]),
  ("Atrasadas", "Em Atraso", ["LT_Tracking_Code__c", "LT_Status__c", "LT_Delivery_Base__c", "LT_Last_Mile_Driver__c", "LT_SLA_Deadline__c", "LT_Days_In_Transit__c"],
   [("LT_Is_Late__c", "equals", "1")]),
  ("Retidas_e_Paradas", "Retidas e Sem Movimentacao", ["LT_Tracking_Code__c", "LT_Status__c", "LT_Delivery_Base__c", "LT_Hours_Without_Movement__c", "LT_SLA_Deadline__c"],
   [("LT_Status__c", "notEqual", "Entregue")]),
]:
    open(os.path.join(S, "listViews", f"{n}.listView-meta.xml"), "w", encoding="utf-8", newline="\n").write(listview(n, l, cols, fil))

wobj(S, "LT_Shipment__c", "Remessa", "Remessas", "Codigo da Remessa", "AutoNumber", "RMS-{000000}", compact="LT_Shipment_Summary")

# ================= LT_Tracking_Event__c =================
ETYPE = ["Etiqueta Gerada", "Coleta Realizada", "Chegada ao SC", "Triagem no SC",
         "Saida do SC (Transferencia)", "Chegada a Base", "Triagem na Base", "Bipado para Rota",
         "Saiu para Entrega", "Entregue", "Tentativa de Entrega", "Destinatario Ausente",
         "Endereco Nao Localizado", "Recusado pelo Destinatario", "Avaria Identificada",
         "Retido", "Sem Movimentacao Detectada", "Devolucao Iniciada", "Extravio Registrado"]

wf(E, "LT_Shipment__c", mdfield("LT_Shipment__c", "Remessa", "Remessa a que o evento pertence.",
   "LT_Shipment__c", "Eventos de Rastreamento", "LT_Tracking_Events"))
wf(E, "LT_Event_Type__c", picklist("LT_Event_Type__c", "Tipo de Evento", "Natureza do evento de rastreamento.", ETYPE, track=False))
wf(E, "LT_Event_DateTime__c", field("LT_Event_DateTime__c", "Data/Hora do Evento", "Momento em que o evento ocorreu.", "DateTime", required=True, track=False))
wf(E, "LT_Unit__c", lookup("LT_Unit__c", "Unidade", "Unidade logistica onde o evento ocorreu.",
   "LT_Logistics_Unit__c", "Eventos de Rastreamento", "LT_Tracking_Events", track=False, lf_optional=True))
wf(E, "LT_Driver__c", lookup("LT_Driver__c", "Motorista", "Motorista que manuseou a remessa neste evento.",
   "LT_Driver__c", "Eventos de Rastreamento", "LT_Tracking_Events", track=False, lf_optional=True))
wf(E, "LT_Location_City__c", field("LT_Location_City__c", "Cidade do Evento", "Cidade onde o evento foi registrado.", "Text", length=80, track=False))
wf(E, "LT_Responsible_User__c", lookup("LT_Responsible_User__c", "Registrado Por", "Usuario que registrou o evento.",
   "User", "Eventos de Rastreamento Registrados", "LT_Registered_Tracking_Events", track=False, lf_optional=True))
wf(E, "LT_Notes__c", field("LT_Notes__c", "Observacoes", "Observacoes do evento.", "Text", length=255, track=False))

wv(E, "LT_Event_Not_Future", "O evento nao pode ter data futura.",
   'LT_Event_DateTime__c &gt; NOW() + 0.0417',
   "A Data/Hora do Evento nao pode estar no futuro.", "LT_Event_DateTime__c")
wv(E, "LT_Event_Delivered_Requires_Driver", "Evento Entregue exige o motorista responsavel.",
   'AND(ISPICKVAL(LT_Event_Type__c, "Entregue"), ISBLANK(LT_Driver__c))',
   "Informe o Motorista no evento de entrega.", "LT_Driver__c")

open(os.path.join(E, "compactLayouts", "LT_Tracking_Event_Summary.compactLayout-meta.xml"), "w", encoding="utf-8", newline="\n").write(
   compact("LT_Tracking_Event_Summary", "Evento - Resumo",
           ["LT_Event_Type__c", "LT_Event_DateTime__c", "LT_Unit__c", "LT_Location_City__c", "LT_Driver__c"]))
open(os.path.join(E, "listViews", "All.listView-meta.xml"), "w", encoding="utf-8", newline="\n").write(
   listview("All", "Todos", ["NAME", "LT_Shipment__c", "LT_Event_Type__c", "LT_Event_DateTime__c", "LT_Unit__c", "LT_Driver__c"]))

wobj(E, "LT_Tracking_Event__c", "Evento de Rastreamento", "Eventos de Rastreamento",
     "Codigo do Evento", "AutoNumber", "EV-{000000}", compact="LT_Tracking_Event_Summary", mdchild=True)

# layouts
simple_layout(os.path.join(ROOT, "layouts", "LT_Shipment__c-Remessa Layout.layout-meta.xml"), [
  ("Identificacao", "TwoColumnsLeftToRight", [
    [("Required", "Name"), ("Required", "LT_Tracking_Code__c"), ("Required", "LT_Shipper__c"), ("Edit", "LT_Origin_Marketplace__c"), ("Edit", "LT_Collection_Type__c")],
    [("Edit", "LT_Status__c"), ("Edit", "LT_Current_Holder__c"), ("Edit", "LT_Package_Type__c"), ("Edit", "LT_Weight_Kg__c"), ("Edit", "LT_Declared_Value__c")]]),
  ("Remetente e Destinatario", "TwoColumnsLeftToRight", [
    [("Edit", "LT_Sender_Name__c"), ("Required", "LT_Recipient_Name__c"), ("Edit", "LT_Recipient_Phone__c")],
    [("Edit", "LT_Dest_Street__c"), ("Edit", "LT_Dest_District__c"), ("Required", "LT_Dest_City__c"), ("Edit", "LT_Dest_State__c"), ("Required", "LT_Dest_ZIP__c")]]),
  ("Roteirizacao", "TwoColumnsLeftToRight", [
    [("Edit", "LT_Origin_Pickup_Point__c"), ("Edit", "LT_Destination_CD__c")],
    [("Edit", "LT_Delivery_Base__c"), ("Edit", "LT_Last_Mile_Driver__c")]]),
  ("Prazos e Rastreamento", "TwoColumnsLeftToRight", [
    [("Edit", "LT_Posted_Date__c"), ("Edit", "LT_Collected_Date__c"), ("Required", "LT_SLA_Deadline__c"), ("Edit", "LT_Delivered_Date__c")],
    [("Readonly", "LT_Days_In_Transit__c"), ("Readonly", "LT_Last_Event_Date__c"), ("Readonly", "LT_Hours_Without_Movement__c"), ("Edit", "LT_Delivery_Attempts__c")]]),
  ("Indicadores", "TwoColumnsLeftToRight", [
    [("Readonly", "LT_Is_Delivered__c"), ("Readonly", "LT_On_Time__c"), ("Readonly", "LT_Is_Late__c")],
    [("Readonly", "LT_Is_Terminal__c"), ("Readonly", "LT_Event_Count__c"), ("Readonly", "LT_Value_Reimbursed__c")]]),
], related=["LT_Tracking_Event__c.LT_Shipment__c", "RelatedHistoryList"])

simple_layout(os.path.join(ROOT, "layouts", "LT_Tracking_Event__c-Evento de Rastreamento Layout.layout-meta.xml"), [
  ("Evento", "TwoColumnsLeftToRight", [
    [("Required", "LT_Shipment__c"), ("Edit", "LT_Event_Type__c"), ("Required", "LT_Event_DateTime__c")],
    [("Edit", "LT_Unit__c"), ("Edit", "LT_Driver__c"), ("Edit", "LT_Location_City__c")]]),
  ("Detalhes", "OneColumn", [
    [("Edit", "LT_Responsible_User__c"), ("Edit", "LT_Notes__c")]]),
])

print("Shipment fields:", len(os.listdir(os.path.join(S, "fields"))), "| Event fields:", len(os.listdir(os.path.join(E, "fields"))))
