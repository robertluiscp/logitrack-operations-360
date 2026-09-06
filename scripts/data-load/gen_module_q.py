#!/usr/bin/env python3
"""Modulo Q: External Services - Named Credential + External Service (ViaCEP) + Flow."""
import os, json
ROOT = r"C:\Users\Robert Luis\Desktop\LogiTrack-SFDX\force-app\main\default"

def w(path, body):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w", encoding="utf-8", newline="\n").write(body.rstrip() + "\n")

# 1. Named Credential (legacy style, sem autenticacao)
w(os.path.join(ROOT, "namedCredentials", "LogiTrack_CEP.namedCredential-meta.xml"),
"""<?xml version="1.0" encoding="UTF-8"?>
<NamedCredential xmlns="http://soap.sforce.com/2006/04/metadata">
    <allowMergeFieldsInBody>false</allowMergeFieldsInBody>
    <allowMergeFieldsInHeader>false</allowMergeFieldsInHeader>
    <calloutStatus>Enabled</calloutStatus>
    <endpoint>https://viacep.com.br</endpoint>
    <generateAuthorizationHeader>false</generateAuthorizationHeader>
    <label>LogiTrack CEP (ViaCEP)</label>
    <principalType>Anonymous</principalType>
    <protocol>NoAuthentication</protocol>
</NamedCredential>""")

# 2. Remote Site Setting (allowlist do callout)
w(os.path.join(ROOT, "remoteSiteSettings", "ViaCEP.remoteSite-meta.xml"),
"""<?xml version="1.0" encoding="UTF-8"?>
<RemoteSiteSetting xmlns="http://soap.sforce.com/2006/04/metadata">
    <description>API publica ViaCEP para consulta de endereco por CEP.</description>
    <disableProtocolSecurity>false</disableProtocolSecurity>
    <isActive>true</isActive>
    <url>https://viacep.com.br</url>
</RemoteSiteSetting>""")

# 3. External Service Registration com schema OpenAPI 3
schema = {
    "openapi": "3.0.0",
    "info": {
        "title": "ViaCEP",
        "version": "1.0.0",
        "description": "Consulta de endereco brasileiro por CEP (API publica ViaCEP)."
    },
    "servers": [{"url": "/"}],
    "paths": {
        "/ws/{cep}/json/": {
            "get": {
                "operationId": "consultarCep",
                "summary": "Consulta endereco por CEP",
                "parameters": [
                    {"name": "cep", "in": "path", "required": True,
                     "description": "CEP com 8 digitos, sem traco.", "schema": {"type": "string"}}
                ],
                "responses": {
                    "200": {
                        "description": "Endereco encontrado.",
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Endereco"}}}
                    }
                }
            }
        }
    },
    "components": {
        "schemas": {
            "Endereco": {
                "type": "object",
                "properties": {
                    "cep": {"type": "string"},
                    "logradouro": {"type": "string"},
                    "complemento": {"type": "string"},
                    "bairro": {"type": "string"},
                    "localidade": {"type": "string"},
                    "uf": {"type": "string"},
                    "ibge": {"type": "string"},
                    "ddd": {"type": "string"},
                    "erro": {"type": "string"}
                }
            }
        }
    }
}
schema_json = json.dumps(schema, indent=2, ensure_ascii=False)
esc = (schema_json.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
       .replace('"', "&quot;"))
w(os.path.join(ROOT, "externalServiceRegistrations", "ViaCEP.externalServiceRegistration-meta.xml"),
f"""<?xml version="1.0" encoding="UTF-8"?>
<ExternalServiceRegistration xmlns="http://soap.sforce.com/2006/04/metadata">
    <description>Consulta de endereco por CEP via API publica ViaCEP. Usada por Flow para preencher endereco de destino de remessas e coletas.</description>
    <label>ViaCEP - Consulta de Endereco</label>
    <namedCredentialReference>LogiTrack_CEP</namedCredentialReference>
    <operations>
        <active>true</active>
        <name>consultarCep</name>
    </operations>
    <registrationProviderType>Custom</registrationProviderType>
    <schema>{esc}</schema>
    <schemaType>OpenApi3</schemaType>
    <status>Complete</status>
    <systemVersion>3</systemVersion>
</ExternalServiceRegistration>""")

print("Modulo Q: named credential + remote site + external service (ViaCEP) gerados.")
