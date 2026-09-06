"""Shared metadata generation helpers for LogiTrack modules."""
import os

def ensure(base, subs=("fields", "validationRules", "compactLayouts", "listViews", "recordTypes")):
    for s in subs:
        os.makedirs(os.path.join(base, s), exist_ok=True)

def wf(base, name, xml):
    open(os.path.join(base, "fields", f"{name}.field-meta.xml"), "w", encoding="utf-8", newline="\n").write(xml.strip() + "\n")

def wv(base, name, desc, formula, msg, field=None, active=True):
    fld = f"\n    <errorDisplayField>{field}</errorDisplayField>" if field else ""
    open(os.path.join(base, "validationRules", f"{name}.validationRule-meta.xml"), "w", encoding="utf-8", newline="\n").write(
f"""<?xml version="1.0" encoding="UTF-8"?>
<ValidationRule xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>{name}</fullName>
    <active>{str(active).lower()}</active>
    <description>{desc}</description>
    <errorConditionFormula>{formula}</errorConditionFormula>{fld}
    <errorMessage>{msg}</errorMessage>
</ValidationRule>
""")

def wobj(base, api, label, plural, name_label, name_type="Text", display_format=None,
         compact=None, mdchild=False, history=True):
    nf = f"        <label>{name_label}</label>\n        <type>{name_type}</type>"
    if name_type == "AutoNumber":
        nf = f"        <displayFormat>{display_format}</displayFormat>\n" + nf
    cl = f"\n    <compactLayoutAssignment>{compact}</compactLayoutAssignment>" if compact else ""
    sm = "ControlledByParent" if mdchild else "ReadWrite"
    open(os.path.join(base, f"{api}.object-meta.xml"), "w", encoding="utf-8", newline="\n").write(
f"""<?xml version="1.0" encoding="UTF-8"?>
<CustomObject xmlns="http://soap.sforce.com/2006/04/metadata">
    <allowInChatterGroups>false</allowInChatterGroups>{cl}
    <deploymentStatus>Deployed</deploymentStatus>
    <description>{label} - LogiTrack Operations 360.</description>
    <enableActivities>{str(not mdchild).lower()}</enableActivities>
    <enableBulkApi>true</enableBulkApi>
    <enableHistory>{str(history).lower()}</enableHistory>
    <enableReports>true</enableReports>
    <enableSearch>true</enableSearch>
    <enableStreamingApi>true</enableStreamingApi>
    <label>{label}</label>
    <nameField>
{nf}
    </nameField>
    <pluralLabel>{plural}</pluralLabel>
    <sharingModel>{sm}</sharingModel>
    <visibility>Public</visibility>
</CustomObject>
""")

def picklist(api, label, desc, values, default=None, helptext="", track=True, restricted=True, sorted_=False):
    vs = "\n".join(
f"""            <value>
                <fullName>{v}</fullName>
                <default>{'true' if v == default else 'false'}</default>
                <label>{v}</label>
            </value>""" for v in values)
    h = f"\n    <inlineHelpText>{helptext}</inlineHelpText>" if helptext else ""
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>{api}</fullName>
    <description>{desc}</description>{h}
    <label>{label}</label>
    <required>false</required>
    <trackHistory>{str(track).lower()}</trackHistory>
    <trackFeedHistory>false</trackFeedHistory>
    <type>Picklist</type>
    <valueSet>
        <restricted>{str(restricted).lower()}</restricted>
        <valueSetDefinition>
            <sorted>{str(sorted_).lower()}</sorted>
{vs}
        </valueSetDefinition>
    </valueSet>
</CustomField>"""

def gvs_picklist(api, label, desc, gvs_name, track=True, helptext=""):
    h = f"\n    <inlineHelpText>{helptext}</inlineHelpText>" if helptext else ""
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>{api}</fullName>
    <description>{desc}</description>{h}
    <label>{label}</label>
    <required>false</required>
    <trackHistory>{str(track).lower()}</trackHistory>
    <trackFeedHistory>false</trackFeedHistory>
    <type>Picklist</type>
    <valueSet>
        <restricted>true</restricted>
        <valueSetName>{gvs_name}</valueSetName>
    </valueSet>
</CustomField>"""

def field(api, label, desc, ftype, required=False, track=True, help="", **kw):
    extra = ""
    if ftype in ("Number", "Currency", "Percent"):
        extra = f"\n    <precision>{kw.get('precision', 12)}</precision>\n    <scale>{kw.get('scale', 0)}</scale>"
    elif ftype == "Text":
        extra = f"\n    <length>{kw.get('length', 80)}</length>\n    <unique>{str(kw.get('unique', False)).lower()}</unique>"
        if kw.get("extid"):
            extra += "\n    <externalId>true</externalId>"
        if kw.get("unique"):
            extra += "\n    <caseSensitive>false</caseSensitive>"
    elif ftype == "LongTextArea":
        extra = f"\n    <length>{kw.get('length', 4000)}</length>\n    <visibleLines>{kw.get('lines', 3)}</visibleLines>"
    h = f"\n    <inlineHelpText>{help}</inlineHelpText>" if help else ""
    dv = f"\n    <defaultValue>{kw['default']}</defaultValue>" if "default" in kw else ""
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>{api}</fullName>
    <description>{desc}</description>{h}
    <label>{label}</label>
    <required>{str(required).lower()}</required>{dv}
    <trackHistory>{str(track).lower()}</trackHistory>
    <trackFeedHistory>false</trackFeedHistory>
    <type>{ftype}</type>{extra}
</CustomField>"""

def formula(api, label, desc, ftype, expr, blanks="BlankAsZero", **kw):
    extra = ""
    if ftype in ("Number", "Currency", "Percent"):
        extra = f"\n    <precision>{kw.get('precision', 18)}</precision>\n    <scale>{kw.get('scale', 2)}</scale>"
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>{api}</fullName>
    <description>{desc}</description>
    <label>{label}</label>
    <formula>{expr}</formula>
    <formulaTreatBlanksAs>{blanks}</formulaTreatBlanksAs>{extra}
    <type>{ftype}</type>
</CustomField>"""

def lookup(api, label, desc, ref, rel_label, rel_name, required=False, track=True, help="",
           delete="SetNull", lf_items=None, lf_msg="", lf_optional=False):
    filt = ""
    if lf_items:
        items = "\n".join(
f"""        <filterItems>
            <field>{f}</field>
            <operation>{op}</operation>
            <value>{v}</value>
        </filterItems>""" for f, op, v in lf_items)
        filt = f"""
    <lookupFilter>
        <active>true</active>
        <errorMessage>{lf_msg}</errorMessage>
{items}
        <isOptional>{str(lf_optional).lower()}</isOptional>
    </lookupFilter>"""
    h = f"\n    <inlineHelpText>{help}</inlineHelpText>" if help else ""
    dc = f"\n    <deleteConstraint>{delete}</deleteConstraint>" if required else ""
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>{api}</fullName>
    <description>{desc}</description>{h}
    <label>{label}</label>
    <referenceTo>{ref}</referenceTo>
    <relationshipLabel>{rel_label}</relationshipLabel>
    <relationshipName>{rel_name}</relationshipName>
    <required>{str(required).lower()}</required>{dc}
    <trackHistory>{str(track).lower()}</trackHistory>
    <type>Lookup</type>{filt}
</CustomField>"""

def mdfield(api, label, desc, ref, rel_label, rel_name):
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>{api}</fullName>
    <description>{desc}</description>
    <label>{label}</label>
    <referenceTo>{ref}</referenceTo>
    <relationshipLabel>{rel_label}</relationshipLabel>
    <relationshipName>{rel_name}</relationshipName>
    <relationshipOrder>0</relationshipOrder>
    <reparentableMasterDetail>false</reparentableMasterDetail>
    <type>MasterDetail</type>
    <writeRequiresMasterRead>false</writeRequiresMasterRead>
</CustomField>"""

def rollup(api, label, desc, child, fk, op, summ_field=None, filters=None):
    sf_ = f"\n    <summarizedField>{child}.{summ_field}</summarizedField>" if summ_field else ""
    ff = ""
    if filters:
        ff = "\n" + "\n".join(
f"""    <summaryFilterItems>
        <field>{child}.{f}</field>
        <operation>{o}</operation>
        <value>{v}</value>
    </summaryFilterItems>""" for f, o, v in filters)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>{api}</fullName>
    <description>{desc}</description>
    <label>{label}</label>{sf_}
    <summaryForeignKey>{child}.{fk}</summaryForeignKey>
    <summaryOperation>{op}</summaryOperation>{ff}
    <type>Summary</type>
</CustomField>"""

def compact(api, label, fields):
    fs = "\n".join(f"    <fields>{f}</fields>" for f in fields)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<CompactLayout xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>{api}</fullName>
{fs}
    <label>{label}</label>
</CompactLayout>
"""

def listview(name, label, columns, filters=None, scope="Everything", orderby=None):
    cols = "\n".join(f"    <columns>{c}</columns>" for c in columns)
    fil = ""
    if filters:
        fil = "\n" + "\n".join(
f"""    <filters>
        <field>{f}</field>
        <operation>{o}</operation>
        <value>{v}</value>
    </filters>""" for f, o, v in filters)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<ListView xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>{name}</fullName>
{cols}
    <filterScope>{scope}</filterScope>{fil}
    <label>{label}</label>
</ListView>
"""

def simple_layout(path, sections, related=None):
    secs = ""
    for label, style, cols in sections:
        colblocks = ""
        for col in cols:
            items = "".join(f"""
            <layoutItems>
                <behavior>{beh}</behavior>
                <field>{fld}</field>
            </layoutItems>""" for beh, fld in col)
            colblocks += f"""
        <layoutColumns>{items}
        </layoutColumns>"""
        secs += f"""
    <layoutSections>
        <customLabel>true</customLabel>
        <detailHeading>true</detailHeading>
        <editHeading>true</editHeading>
        <label>{label}</label>{colblocks}
        <style>{style}</style>
    </layoutSections>"""
    rl = ""
    if related:
        rl = "\n" + "\n".join(f"    <relatedLists>\n        <relatedList>{r}</relatedList>\n    </relatedLists>" for r in related)
    open(path, "w", encoding="utf-8", newline="\n").write(
f"""<?xml version="1.0" encoding="UTF-8"?>
<Layout xmlns="http://soap.sforce.com/2006/04/metadata">{secs}{rl}
    <showEmailCheckbox>false</showEmailCheckbox>
    <showHighlightsPanel>true</showHighlightsPanel>
    <showInteractionLogPanel>false</showInteractionLogPanel>
    <showRunAssignmentRulesCheckbox>false</showRunAssignmentRulesCheckbox>
    <showSubmitAndAttachButton>false</showSubmitAndAttachButton>
</Layout>
""")
