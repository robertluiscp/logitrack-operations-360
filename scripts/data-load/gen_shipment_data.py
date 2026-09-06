#!/usr/bin/env python3
import csv, random, datetime, os
random.seed(31)
OUT = os.path.dirname(os.path.abspath(__file__))
TODAY = datetime.date(2026, 9, 6)
NOW = datetime.datetime(2026, 9, 6, 14, 0, 0)

SHIPPERS = """001g800000kdoNSAAY|Xitou Marketplace|PR
001g800000kdoNTAAY|Compria Marketplace|PR
001g800000kdoNUAAY|ShopLivre|RS
001g800000kdoNVAAY|VendeMais Online|SC
001g800000kdoNWAAY|Calcados Prime|RS
001g800000kdoNXAAY|Livraria Pagina Viva|RS
001g800000kdoNYAAY|AutoPecas do Sul|PR
001g800000kdoNZAAY|FerramentasMax|RS
001g800000kdoNaAAI|Distribuidora Farmasul|SC
001g800000kdqDxAAI|ModaMix Confeccoes|PR
001g800000kdqDyAAI|TechNova BR|SC
001g800000kdqDzAAI|Casa e Cor Online|RS
001g800000kdqE0AAI|PetLar Suprimentos|PR
001g800000kdqE1AAI|SuplementaBR|PR
001g800000kdqE2AAI|Moveis Serra Sul|RS
001g800000kdqE4AAI|Confeccoes Vale do Itajai|SC
001g800000kdqkDAAQ|Joao Pedro Nogueira|PR
001g800000kdqkEAAQ|Marilia Fontes Atelie|RS"""
shippers = [l.split("|") for l in SHIPPERS.splitlines()]

DRIVERS = """a0Fg8000006qKonEAE|ARP-PR|PR
a0Fg8000006qKooEAE|ARP-PR|PR
a0Fg8000006qKopEAE|TUB-SC|SC
a0Fg8000006qKorEAE|CCM-SC|SC
a0Fg8000006qKosEAE|CXJ-RS|RS
a0Fg8000006qKotEAE|F LOD-PR|PR
a0Fg8000006qKowEAE|F PET-RS|RS
a0Fg8000006qKp1EAE|CLB-PR|PR
a0Fg8000006qKp3EAE|TUB-SC|SC
a0Fg8000006qKp4EAE|F JOI-SC|SC
a0Fg8000006qKp5EAE|ALM-PR|PR
a0Fg8000006qKp6EAE|F BLU-SC|SC
a0Fg8000006qKp7EAE|POA-RS|RS
a0Fg8000006qKp8EAE|CIC-PR|PR
a0Fg8000006qKpEEAU|F ARP-PR|PR
a0Fg8000006qKpHEAU|SJE-SC|SC
a0Fg8000006qKpIEAU|CCM-SC|SC
a0Fg8000006qKpJEAU|ARP-PR|PR
a0Fg8000006qKpKEAU|F CNS-RS|RS"""
drivers = [l.split("|") for l in DRIVERS.splitlines()]
drv_by_state = {}
for did, base, st in drivers:
    drv_by_state.setdefault(st, []).append((did, base))

CD = {"PR": "PR SJS", "SC": "SC BNU", "RS": "RS NSR"}
CITIES = {
 "PR": ["Curitiba", "Londrina", "Maringa", "Cascavel", "Ponta Grossa", "Sao Jose dos Pinhais", "Foz do Iguacu", "Colombo", "Guarapuava", "Paranagua", "Toledo", "Apucarana"],
 "SC": ["Joinville", "Florianopolis", "Blumenau", "Chapeco", "Itajai", "Criciuma", "Lages", "Jaragua do Sul", "Balneario Camboriu", "Tubarao", "Sao Jose", "Palhoca"],
 "RS": ["Porto Alegre", "Caxias do Sul", "Pelotas", "Canoas", "Santa Maria", "Gravatai", "Novo Hamburgo", "Passo Fundo", "Sao Leopoldo", "Rio Grande", "Alvorada", "Sapucaia do Sul"],
}
MKT = ["Shopee", "Mercado Livre", "Shein", "TikTok Shop", "Amazon", "Magalu", "AliExpress", "Loja Propria"]
STREETS = ["Rua das Flores", "Av. Brasil", "Rua XV de Novembro", "Av. Getulio Vargas", "Rua Sao Paulo",
           "Rua Marechal Deodoro", "Av. das Torres", "Rua Parana", "Rua Santa Catarina", "Av. Sete de Setembro"]
DISTRICTS = ["Centro", "Jardim America", "Vila Nova", "Bairro Alto", "Sao Cristovao", "Boa Vista", "Industrial", "Cidade Alta"]
FIRST = ["Ana", "Bruno", "Carla", "Daniel", "Eduarda", "Felipe", "Gabriela", "Henrique", "Isabela", "Joao",
         "Karina", "Lucas", "Mariana", "Nicolas", "Olivia", "Pedro", "Rafaela", "Sofia", "Thiago", "Valentina"]
LAST = ["Silva", "Santos", "Oliveira", "Souza", "Pereira", "Lima", "Costa", "Ferreira", "Rodrigues", "Almeida",
        "Nascimento", "Carvalho", "Araujo", "Ribeiro", "Barbosa"]

STATUS_W = [
 ("Entregue", 60), ("Em Rota de Entrega", 5), ("Recebido na Base", 4), ("Em Triagem na Base", 3),
 ("Em Transferencia", 3), ("Em Triagem no SC", 3), ("Coletado", 2), ("Tentativa de Entrega", 4),
 ("Retido", 6), ("Sem Movimentacao", 3), ("Devolvido ao Remetente", 2), ("Extraviado", 2),
]
statuses = []
for s, w in STATUS_W:
    statuses += [s] * w

N = 420
ships = []
events = []
sc_seq = 77120000

for i in range(1, N + 1):
    sid, sname, sst = random.choice(shippers)
    # destination state: 55% same as shipper, else spread
    dst = sst if random.random() < 0.5 else random.choice(["PR", "SC", "RS"])
    city = random.choice(CITIES[dst])
    code = f"LT{sc_seq + i}BR"
    posted = NOW - datetime.timedelta(days=random.randint(1, 40), hours=random.randint(0, 23))
    sla_days = random.choice([3, 4, 5, 5, 6, 7])
    sla = (posted + datetime.timedelta(days=sla_days)).date()
    status = random.choice(statuses)
    drv_state_pool = drv_by_state.get(dst) or drivers
    did, dbase = random.choice([(d[0], d[1]) for d in drivers if d[2] == dst] or [(d[0], d[1]) for d in drivers])
    weight = round(random.uniform(0.1, 18.0), 3)
    declared = round(random.uniform(20, 1200), 2)

    coll_date = ""
    delivered_date = ""
    holder = "Ponto de Coleta"
    base_val = ""
    cd_val = ""
    driver_val = ""
    attempts = 0
    reimb = "false"

    # timeline anchors
    t_collect = posted + datetime.timedelta(hours=random.randint(4, 30))
    t_sc = t_collect + datetime.timedelta(hours=random.randint(6, 40))
    t_transfer = t_sc + datetime.timedelta(hours=random.randint(3, 20))
    t_base = t_transfer + datetime.timedelta(hours=random.randint(4, 24))
    t_route = t_base + datetime.timedelta(hours=random.randint(2, 14))
    t_deliv = t_route + datetime.timedelta(hours=random.randint(1, 10))

    ev = [("Etiqueta Gerada", posted, "", "", "Ponto de Coleta origem")]
    reached = ["Etiqueta Gerada"]

    def add(et, dt, unit="", drvid="", note=""):
        events.append({
            "LT_Shipment__r.LT_Tracking_Code__c": code,
            "LT_Event_Type__c": et,
            "LT_Event_DateTime__c": dt.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "LT_Unit__r.Unit_Code__c": unit,
            "LT_Driver__c": drvid,
            "LT_Location_City__c": city if et in ("Saiu para Entrega", "Entregue", "Tentativa de Entrega") else "",
            "LT_Notes__c": note,
        })

    add("Etiqueta Gerada", posted, note="Pedido postado pelo embarcador.")

    order = ["Coletado", "Em Triagem no SC", "Em Transferencia", "Recebido na Base", "Em Triagem na Base", "Em Rota de Entrega", "Entregue"]
    target_idx = order.index(status) if status in order else 99

    if status in ("Coletado",) or target_idx >= 0:
        pass

    # walk timeline up to the target status
    if status != "Etiqueta Gerada":
        add("Coleta Realizada", t_collect, note="Coleta realizada.")
        coll_date = t_collect.strftime("%Y-%m-%dT%H:%M:%S.000Z"); holder = "Motorista de Coleta"
    if status not in ("Etiqueta Gerada", "Coletado"):
        add("Chegada ao SC", t_sc, unit=CD[dst]); add("Triagem no SC", t_sc + datetime.timedelta(hours=2), unit=CD[dst])
        cd_val = CD[dst]; holder = "Centro de Distribuicao"
    if status not in ("Etiqueta Gerada", "Coletado", "Em Triagem no SC"):
        add("Saida do SC (Transferencia)", t_transfer, unit=CD[dst]); holder = "Em Transferencia"
    if status not in ("Etiqueta Gerada", "Coletado", "Em Triagem no SC", "Em Transferencia"):
        add("Chegada a Base", t_base, unit=dbase); base_val = dbase; holder = "Base de Entrega"
    if status not in ("Etiqueta Gerada", "Coletado", "Em Triagem no SC", "Em Transferencia", "Recebido na Base"):
        add("Triagem na Base", t_base + datetime.timedelta(hours=3), unit=dbase)
    if status in ("Em Rota de Entrega", "Entregue", "Tentativa de Entrega", "Devolvido ao Remetente", "Extraviado"):
        add("Bipado para Rota", t_route - datetime.timedelta(minutes=30), unit=dbase, drvid=did)
        add("Saiu para Entrega", t_route, drvid=did); driver_val = did; holder = "Motorista Last Mile"
        base_val = dbase
    if status == "Entregue":
        add("Entregue", t_deliv, drvid=did, note="Entregue ao destinatario.")
        delivered_date = t_deliv.strftime("%Y-%m-%dT%H:%M:%S.000Z"); holder = "Entregue"
    if status == "Tentativa de Entrega":
        attempts = random.randint(1, 2)
        add(random.choice(["Tentativa de Entrega", "Destinatario Ausente", "Endereco Nao Localizado"]), t_deliv, drvid=did,
            note="Sem sucesso na entrega. Nova tentativa agendada.")
        holder = "Motorista Last Mile"
    if status == "Retido":
        add("Retido", t_deliv + datetime.timedelta(days=1), unit=base_val or dbase,
            note="Passou do prazo de entrega sem sucesso.")
        base_val = base_val or dbase; holder = "Base de Entrega"
    if status == "Sem Movimentacao":
        add("Sem Movimentacao Detectada", (NOW - datetime.timedelta(hours=random.randint(7, 60))),
            unit=base_val or dbase, note="Sem atualizacao ha mais de 6 horas.")
        base_val = base_val or dbase
    if status == "Devolvido ao Remetente":
        attempts = 3
        add("Recusado pelo Destinatario", t_deliv, drvid=did)
        add("Devolucao Iniciada", t_deliv + datetime.timedelta(days=1), unit=dbase)
        holder = "Devolvido"
    if status == "Extraviado":
        add("Extravio Registrado", t_deliv + datetime.timedelta(days=random.randint(2, 8)), unit=dbase,
            note="Remessa nao localizada. Processo de extravio aberto.")
        reimb = random.choice(["true", "false"])
        holder = "Base de Entrega"

    ships.append({
        "LT_Tracking_Code__c": code,
        "LT_Shipper__c": sid,
        "LT_Origin_Marketplace__c": random.choice(MKT),
        "LT_Collection_Type__c": random.choice(["Coleta no Seller", "Coleta no Seller", "Coleta no DropOff"]),
        "LT_Package_Type__c": random.choice(["Pacote", "Pacote", "Pacote", "Envelope", "Caixa", "Volume Grande"]),
        "LT_Sender_Name__c": sname,
        "LT_Recipient_Name__c": f"{random.choice(FIRST)} {random.choice(LAST)}",
        "LT_Recipient_Phone__c": f"(4{random.randint(1,9)}) 9{random.randint(1000,9999)}-{random.randint(1000,9999)}",
        "LT_Dest_Street__c": f"{random.choice(STREETS)}, {random.randint(10, 3999)}",
        "LT_Dest_District__c": random.choice(DISTRICTS),
        "LT_Dest_City__c": city,
        "LT_Dest_State__c": dst,
        "LT_Dest_ZIP__c": f"{random.randint(80,99)}{random.randint(100,999)}-{random.randint(100,999)}",
        "LT_Weight_Kg__c": weight,
        "LT_Declared_Value__c": declared,
        "LT_Status__c": status,
        "LT_Current_Holder__c": holder,
        "LT_Posted_Date__c": posted.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        "LT_Collected_Date__c": coll_date,
        "LT_SLA_Deadline__c": sla.isoformat(),
        "LT_Delivered_Date__c": delivered_date,
        "LT_Delivery_Attempts__c": attempts,
        "LT_Destination_CD__r.Unit_Code__c": cd_val,
        "LT_Delivery_Base__r.Unit_Code__c": base_val,
        "LT_Last_Mile_Driver__c": driver_val,
        "LT_Value_Reimbursed__c": reimb,
    })

with open(f"{OUT}/shipments.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(ships[0].keys()))
    w.writeheader(); w.writerows(ships)
with open(f"{OUT}/tracking_events.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(events[0].keys()))
    w.writeheader(); w.writerows(events)

from collections import Counter
print("shipments:", len(ships), "events:", len(events))
print(Counter(s["LT_Status__c"] for s in ships))
