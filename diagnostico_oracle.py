#!/usr/bin/env python3
"""Script de diagnóstico Oracle - Verificar estado actual sin crear nada"""
import oci

CONFIG_PATH = r"C:\Users\artur\.oci\config"
PRIVATE_KEY = r"C:\Users\artur\.oci\oci_api_key.pem"

print("=== DIAGNÓSTICO ORACLE ===")

config = oci.config.from_file(CONFIG_PATH)
config["key_file"] = PRIVATE_KEY

identity = oci.identity.IdentityClient(config)
compartimento = config["tenancy"]

# Regiones suscritas
print("\n1. Regiones suscritas:")
regions = oci.pagination.list_call_get_all_results(
    identity.list_region_subscriptions, compartimento
).data
for r in regions:
    print(f"   - {r.region_name}")

# Verificar que las regiones candidatas estén suscritas
REGIONES_CANDIDATAS = ["eu-madrid-3", "eu-frankfurt-1", "uk-london-1", "us-ashburn-1"]
regiones_suscritas = [r.region_name for r in regions]
regiones_disponibles = [r for r in REGIONES_CANDIDATAS if r in regiones_suscritas]

print(f"\n2. Regiones candidatas disponibles: {regiones_disponibles}")

# Verificar Availability Domains
print("\n3. Availability Domains disponibles:")
for region in regiones_disponibles[:1]:  # Solo primera región disponible
    config_region = {**config, "region": region}
    identity_region = oci.identity.IdentityClient(config_region)
    ads = oci.pagination.list_call_get_all_results(
        identity_region.list_availability_domains, compartimento
    ).data
    for ad in ads:
        print(f"   - {ad.name}")

# Verificar instancia existente
print("\n4. Instancia existente 'certificadoya-oracle':")
for region in regiones_disponibles:
    config_region = {**config, "region": region}
    compute = oci.core.ComputeClient(config_region)
    existing = oci.pagination.list_call_get_all_results(
        compute.list_instances, compartimento, display_name="certificadoya-oracle"
    ).data
    running = [i for i in existing if i.lifecycle_state in ('RUNNING', 'PROVISIONING')]
    print(f"   {region}: {len(running)} instancias corriendo")

# Verificar VCN y subnet
print("\n5. Redes existentes:")
for region in regiones_disponibles[:1]:
    config_region = {**config, "region": region}
    network = oci.core.VirtualNetworkClient(config_region)
    
    vcns = oci.pagination.list_call_get_all_results(
        network.list_vcns, compartimento, display_name="certificadoya-vcn"
    ).data
    print(f"   VCN: {len(vcns)} encontrada(s)")
    
    if vcns:
        vcn_id = vcns[0].id
        subnets = oci.pagination.list_call_get_all_results(
            network.list_subnets, compartimento, vcn_id=vcn_id, display_name="public-subnet"
        ).data
        print(f"   Subnet: {len(subnets)} encontrada(s)")

print("\n=== FIN DIAGNÓSTICO ===")