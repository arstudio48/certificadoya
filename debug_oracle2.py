#!/usr/bin/env python3
"""Debug script para ver error de creación de instancia"""
import oci
import traceback
import base64

CONFIG_PATH = r"C:\Users\artur\.oci\config"
PRIVATE_KEY = r"C:\Users\artur\.oci\oci_api_key.pem"
SSH_PUB = r"C:\Users\artur\.ssh\id_rsa.pub"

CLOUD_INIT = """#cloud-config
packageUpdate: true
packages:
  - curl
runcmd:
  - curl -fsSL https://tailscale.com/install.sh | sh
  - tailscale up --authkey=tskey-auth-REEMPLAZAR --advertise-tags=tag:oracle
"""

def main():
    config = oci.config.from_file(CONFIG_PATH)
    config["key_file"] = PRIVATE_KEY
    compartimento = config["tenancy"]
    
    # Configuración para eu-madrid-3
    region = "eu-madrid-3"
    config["region"] = region
    compute = oci.core.ComputeClient(config)
    network = oci.core.VirtualNetworkClient(config)
    identity = oci.identity.IdentityClient(config)
    
    # Obtener Availability Domain
    ads = oci.pagination.list_call_get_all_results(
        identity.list_availability_domains, compartimento
    ).data
    ad = ads[0].name
    print(f"AD: {ad}")
    
    # Obtener imagen Ubuntu ARM
    print("Buscando imagen Ubuntu ARM...")
    try:
        imgs = oci.pagination.list_call_get_all_results(
            compute.list_images, compartimento,
            operating_system="Canonical Ubuntu",
            sort_by="TIMECREATED", sort_order="DESC"
        ).data
        arm = [i for i in imgs if 'aarch64' in (i.display_name or '').lower()]
        if not arm:
            arm = [i for i in imgs if 'VM.Standard.A1.Flex' in (i.compatible_shapes or [])]
        if not arm:
            print("ERROR: No se encontró imagen ARM")
            return
        image_id = arm[0].id
        print(f"Imagen encontrada: {arm[0].display_name} ({image_id})")
    except Exception as e:
        print(f"Error obteniendo imagen: {e}")
        traceback.print_exc()
        return
    
    # Verificar VCN existente
    print("\nBuscando VCN existente...")
    try:
        vcns = oci.pagination.list_call_get_all_results(
            network.list_vcns, compartimento, display_name="certificadoya-vcn"
        ).data
        print(f"VCNs encontradas: {len(vcns)}")
        if vcns:
            vcn_id = vcns[0].id
            print(f"VCN ID: {vcn_id}")
        else:
            print("No hay VCN, se debe crear...")
    except Exception as e:
        print(f"Error listando VCN: {e}")
        traceback.print_exc()
        # Continuar para crear VCN si no existe
        vcn_id = None
    
    # Verificar subnet existente
    subnet_id = None
    if vcn_id:
        print("\nBuscando subnet existente...")
        try:
            subnets = oci.pagination.list_call_get_all_results(
                network.list_subnets, compartimento, vcn_id=vcn_id, display_name="public-subnet"
            ).data
            print(f"Subnets encontradas: {len(subnets)}")
            if subnets:
                subnet_id = subnets[0].id
                print(f"Subnet ID: {subnet_id}")
        except Exception as e:
            print(f"Error listando subnets: {e}")
            traceback.print_exc()
    
    # Si no hay subnet, ver si necesitamos crear Internet Gateway y Route Table
    if vcn_id and not subnet_id:
        print("\nBuscando Internet Gateway...")
        try:
            igs = oci.pagination.list_call_get_all_results(
                network.list_internet_gateways, compartimento, vcn_id=vcn_id
            ).data
            ig = None
            for gateway in igs:
                if gateway.display_name == "igw" and gateway.is_enabled:
                    ig = gateway
                    break
            if not ig:
                print("No hay IGW, se debe crear...")
            else:
                print(f"I GW encontrado: {ig.id}")
        except Exception as e:
            print(f"Error listando IGW: {e}")
    
    # Intentar listar route tables
    print("\nBuscando Route Tables...")
    try:
        rts = oci.pagination.list_call_get_all_results(
            network.list_route_tables, compartimento, vcn_id=vcn_id
        ).data
        print(f"Route Tables encontradas: {len(rts)}")
        for rt in rts:
            print(f"  - {rt.display_name}: {rt.id}")
    except Exception as e:
        print(f"Error listando route tables: {e}")

if __name__ == "__main__":
    main()