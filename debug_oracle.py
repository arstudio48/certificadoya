#!/usr/bin/env python3
"""Debug script para ver qué está pasando con Oracle"""
import oci
import traceback

CONFIG_PATH = r"C:\Users\artur\.oci\config"
PRIVATE_KEY = r"C:\Users\artur\.oci\oci_api_key.pem"
SSH_PUB = r"C:\Users\artur\.ssh\id_rsa.pub"
REGIONES_CANDIDATAS = ["eu-madrid-3", "eu-frankfurt-1", "uk-london-1", "us-ashburn-1"]

def main():
    config = oci.config.from_file(CONFIG_PATH)
    config["key_file"] = PRIVATE_KEY
    identity = oci.identity.IdentityClient(config)
    compartimento = config["tenancy"]
    
    # 1. Ver regiones suscritas
    print("=== PASO 1: Regiones suscritas ===")
    try:
        regions = oci.pagination.list_call_get_all_results(
            identity.list_region_subscriptions, compartimento
        ).data
        regiones_suscritas = [r.region_name for r in regions]
        print(f"Regiones suscritas: {regiones_suscritas}")
    except Exception as e:
        print(f"Error obteniendo regiones: {e}")
        return
    
    # 2. Filtrar regiones
    print("\n=== PASO 2: Filtrar regiones candidatas ===")
    regiones_a_probar = [r for r in REGIONES_CANDIDATAS if r in regiones_suscritas]
    print(f"Regiones a probar: {regiones_a_probar}")
    
    if not regiones_a_probar:
        print("ERROR: Ninguna región candidata está suscrita")
        return
    
    # 3. Probar primera región
    print("\n=== PASO 3: Probar creación en eu-madrid-3 ===")
    region = "eu-madrid-3"
    config["region"] = region
    compute = oci.core.ComputeClient(config)
    
    # Verificar si ya existe instancia
    print("Buscando instancia existente...")
    try:
        existing = oci.pagination.list_call_get_all_results(
            compute.list_instances, compartimento, display_name="certificadoya-oracle"
        ).data
        print(f"Instancias encontradas: {len(existing)}")
        for i in existing:
            print(f"  - {i.display_name}: {i.lifecycle_state}")
    except Exception as e:
        print(f"Error listando instancias: {e}")
        traceback.print_exc()
    
    # ListarAvailability Domains
    print("\nBuscando Availability Domains...")
    try:
        ads = oci.pagination.list_call_get_all_results(
            identity.list_availability_domains, compartimento
        ).data
        print(f"ADs encontrados: {len(ads)}")
        for ad in ads:
            print(f"  - {ad.name}")
    except Exception as e:
        print(f"Error obteniendo ADs: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()