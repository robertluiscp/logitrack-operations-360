"""Modulo S (avaliador externo): Permission Set somente-leitura para navegacao
sem edicao nem exclusao. Gera LT_Read_Only_Viewer.permissionset-meta.xml
enumerando objeto + cada campo customizado dos 20 objetos LT_*, mais leitura
de Account/Contact/Opportunity/Case (sem create/edit/delete em nenhum).

Elementos de mesmo tipo precisam ficar agrupados e em ordem alfabetica de tag
(applicationVisibilities, fieldPermissions, objectPermissions, tabSettings),
senao o Metadata API rejeita como "element duplicated"."""
import os

ROOT = os.path.join(os.path.dirname(__file__), "..", "..", "force-app", "main", "default")
OBJ_DIR = os.path.join(ROOT, "objects")
OUT = os.path.join(ROOT, "permissionsets", "LT_Read_Only_Viewer.permissionset-meta.xml")

CUSTOM_OBJECTS = [
    "LT_Commercial_Agreement__c", "LT_Delivery_Attempt__c", "LT_Driver_Document__c",
    "LT_Driver_Penalty__c", "LT_Driver__c", "LT_Expense__c", "LT_Logistics_Unit__c",
    "LT_Loss_Claim__c", "LT_Manifest_Line__c", "LT_Manifest__c", "LT_Monthly_Billing__c",
    "LT_Operational_Incident__c", "LT_Payment_Request__c", "LT_Payment__c",
    "LT_Pickup_Request__c", "LT_Route__c", "LT_Shipment__c", "LT_Tracking_Event__c",
    "LT_Vehicle__c", "Operational_Indicator__c",
]
STANDARD_OBJECTS = ["Account", "Contact", "Opportunity", "Case"]

APPS = [
    "LogiTrack_Operations_360", "LogiTrack_Comercial", "LogiTrack_Cadastro",
    "LogiTrack_SAC", "LogiTrack_Financeiro", "LogiTrack_Executivo",
]


def custom_fields(obj):
    """Campos customizados que aceitam fieldPermissions: required e
    MasterDetail nao entram (o Metadata API rejeita FLS nesses)."""
    d = os.path.join(OBJ_DIR, obj, "fields")
    if not os.path.isdir(d):
        return []
    out = []
    for fn in sorted(os.listdir(d)):
        if not fn.endswith(".field-meta.xml"):
            continue
        content = open(os.path.join(d, fn), encoding="utf-8").read()
        if "<required>true</required>" in content:
            continue
        if "<type>MasterDetail</type>" in content:
            continue
        out.append(fn[: -len(".field-meta.xml")])
    return out


def build():
    app_vis, field_perms, obj_perms, tab_settings = [], [], [], []

    for app in APPS:
        app_vis.append(
            "    <applicationVisibilities>\n"
            f"        <application>{app}</application>\n"
            "        <visible>true</visible>\n"
            "    </applicationVisibilities>\n"
        )

    for obj in STANDARD_OBJECTS + CUSTOM_OBJECTS:
        obj_perms.append(
            "    <objectPermissions>\n"
            f"        <object>{obj}</object>\n"
            "        <allowCreate>false</allowCreate>\n"
            "        <allowDelete>false</allowDelete>\n"
            "        <allowEdit>false</allowEdit>\n"
            "        <allowRead>true</allowRead>\n"
            "        <modifyAllRecords>false</modifyAllRecords>\n"
            "        <viewAllRecords>true</viewAllRecords>\n"
            "    </objectPermissions>\n"
        )

    for obj in CUSTOM_OBJECTS:
        tab_settings.append(
            "    <tabSettings>\n"
            f"        <tab>{obj}</tab>\n"
            "        <visibility>Visible</visibility>\n"
            "    </tabSettings>\n"
        )
        for f in custom_fields(obj):
            field_perms.append(
                "    <fieldPermissions>\n"
                f"        <field>{obj}.{f}</field>\n"
                "        <editable>false</editable>\n"
                "        <readable>true</readable>\n"
                "    </fieldPermissions>\n"
            )

    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>\n',
        '<PermissionSet xmlns="http://soap.sforce.com/2006/04/metadata">\n',
    ]
    parts += app_vis
    parts.append(
        "    <description>Navegacao completa por todas as areas do LogiTrack, sem criar, "
        "editar ou excluir nenhum registro. Para visitantes/avaliadores externos do "
        "portfolio.</description>\n"
    )
    parts += field_perms
    parts.append("    <hasActivationRequired>false</hasActivationRequired>\n")
    parts.append("    <label>LT - Somente Leitura (Avaliador)</label>\n")
    parts += obj_perms
    parts += tab_settings
    parts.append("</PermissionSet>\n")

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("".join(parts))
    print("escrito:", OUT)
    print("tamanho:", os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    build()
