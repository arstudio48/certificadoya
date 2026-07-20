#!/usr/bin/env python3
"""
Oracle Cloud Free Tier — Crear instancia Always-Free probando regiones suscritas
Consulta regiones suscritas y prueba solo esas hasta encontrar capacidad.
"""
import oci
import base64
import os

# Config base (se sobreescribe region por cada intento)
CONFIG_PATH = r"C:\Users\artur\.oci\config"
PRIVATE_KEY = r"C:\Users\artur\.oci\oci_api_key.pem"
SSH_PUB = r"C:\Users\artur\.ssh\id_rsa.pub"

# Regiones candidatas - el script filtrará solo las suscritas
REGIONES_CANDIDATAS = ["eu-madrid-3", "eu-frankfurt-1", "uk-london-1", "us-ashburn-1"]

CLOUD_INIT = """#cloud-config
package_update: true
packages:
  - curl
runcmd:
  - curl -fsSL https://tailscale.com/install.sh | sh
  - tailscale up --authkey=tskey-auth-REEMPLAZAR --advertise-tags=tag:oracle
"""

def get_subscribed_regions(identity, compartimento):
    """Obtiene lista de regiones suscritas para el tenancy"""
    try:
        regions = oci.pagination.list_call_get_all_results(
            identity.list_region_subscriptions, compartimento
        ).data
        return [r.region_name for r in regions]
    except Exception as e:
        print(f"  ⚠ Error consultando regiones suscritas: {e}")
        return []

def get_image(compute, compartimento, region):
    imgs = oci.pagination.list_call_get_all_results(
        compute.list_images, compartimento,
        operating_system="Canonical Ubuntu",
        sort_by="TIMECREATED", sort_order="DESC"
    ).data
    arm = [i for i in imgs if 'aarch64' in (i.display_name or '').lower()]
    if not arm:
        arm = [i for i in imgs if 'VM.Standard.A1.Flex' in (i.compatible_shapes or [])]
    return arm[0].id

def get_subnet(network, compute, compartimento, region):
    vcns = oci.pagination.list_call_get_all_results(
        network.list_vcns, compartimento, display_name="certificadoya-vcn"
    ).data
    if vcns:
        vcn_id = vcns[0].id
    else:
        vcn = network.create_vcn(oci.core.models.CreateVcnDetails(
            cidr_block="10.0.0.0/16", display_name="certificadoya-vcn",
            compartment_id=compartimento
        )).data
        vcn_id = vcn.id
        oci.wait_until(network, network.get_vcn(vcn_id), 'lifecycle_state', 'AVAILABLE')

    subnets = oci.pagination.list_call_get_all_results(
        network.list_subnets, compartimento, vcn_id=vcn_id, display_name="public-subnet"
    ).data
    if subnets:
        return subnets[0].id, vcn_id

    ig = network.create_internet_gateway(oci.core.models.CreateInternetGatewayDetails(
        compartment_id=compartimento, vcn_id=vcn_id, display_name="igw", is_enabled=True
    )).data
    rt = network.create_route_table(oci.core.models.CreateRouteTableDetails(
        compartment_id=compartimento, vcn_id=vcn_id, display_name="public-rt",
        route_rules=[oci.core.models.RouteRule(
            destination="0.0.0.0/0", destination_type="CIDR_BLOCK", network_entity_id=ig.id
        )]
    )).data
    subnet = network.create_subnet(oci.core.models.CreateSubnetDetails(
        compartment_id=compartimento, vcn_id=vcn_id, display_name="public-subnet",
        cidr_block="10.0.1.0/24", route_table_id=rt.id, prohibit_public_ip_on_vnic=False
    )).data
    oci.wait_until(network, network.get_subnet(subnet.id), 'lifecycle_state', 'AVAILABLE')
    return subnet.id, vcn_id

def intentar_region(region):
    config = oci.config.from_file(CONFIG_PATH)
    config["region"] = region
    config["key_file"] = PRIVATE_KEY
    compute = oci.core.ComputeClient(config)
    network = oci.core.VirtualNetworkClient(config)
    identity = oci.identity.IdentityClient(config)
    compartimento = config["tenancy"]

    print(f"\n=== REGIÓN: {region} ===")
    # Verificar ADs
    ads = oci.pagination.list_call_get_all_results(
        identity.list_availability_domains, compartimento
    ).data
    if not ads:
        print(f"  Sin ADs (región no suscrita?)")
        return False
    ad = ads[0].name

    # Comprobar si ya existe instancia
    existing = oci.pagination.list_call_get_all_results(
        compute.list_instances, compartimento, display_name="certificadoya-oracle"
    ).data
    running = [i for i in existing if i.lifecycle_state in ('RUNNING', 'PROVISIONING')]
    if running:
        print(f"  ✅ Ya existe instancia en {region}: {running[0].id}")
        return True

    try:
        image_id = get_image(compute, compartimento, region)
        subnet_id, vcn_id = get_subnet(network, compute, compartimento, region)
        details = oci.core.models.LaunchInstanceDetails(
            compartment_id=compartimento,
            display_name="certificadoya-oracle",
            availability_domain=ad,
            shape="VM.Standard.A1.Flex",
            shape_config=oci.core.models.LaunchInstanceShapeConfigDetails(ocpus=2, memory_in_gbs=12),
            source_details=oci.core.models.InstanceSourceViaImageDetails(source_type="image", image_id=image_id),
            create_vnic_details=oci.core.models.CreateVnicDetails(
                subnet_id=subnet_id, assign_public_ip=True, display_name="vnic-public"
            ),
            metadata={
                "ssh_authorized_keys": open(SSH_PUB).read().strip(),
                "user_data": base64.b64encode(CLOUD_INIT.encode()).decode()
            }
        )
        instance = compute.launch_instance(details).data
        print(f"  ✅ Instancia creada en {region}: {instance.id}")
        oci.wait_until(compute, compute.get_instance(instance.id), 'lifecycle_state', 'RUNNING')
        vnics = oci.pagination.list_call_get_all_results(
            compute.list_vnic_attachments, compartimento, instance_id=instance.id
        ).data
        vnic = network.get_vnic(vnics[0].vnic_id).data
        print(f"  🌐 IP: {vnic.public_ip} | ssh ubuntu@{vnic.public_ip}")
        return True
    except oci.exceptions.ServiceError as e:
        if 'Out of host capacity' in str(e):
            print(f"  ⏳ Sin capacidad en {region}")
            return False
        else:
            print(f"  ❌ Error en {region}: {e.message}")
            return False

def main():
    print("🔄 Consultando regiones suscritas...")
    config = oci.config.from_file(CONFIG_PATH)
    config["key_file"] = PRIVATE_KEY
    identity = oci.identity.IdentityClient(config)
    compartimento = config["tenancy"]
    
    regiones_suscritas = get_subscribed_regions(identity, compartimento)
    print(f"📍 Regiones suscritas: {regiones_suscritas}")
    
    # Filtrar solo regiones candidatas que están suscritas
    regiones_a_probar = [r for r in REGIONES_CANDIDATAS if r in regiones_suscritas]
    if not regiones_a_probar:
        print("❌ Ninguna región candidata está suscrita. Ve a Console → Subscriptions → Add Region")
        return
    
    print(f"🎯 Probando: {regiones_a_probar}")
    
    for region in regiones_a_probar:
        try:
            if intentar_region(region):
                print(f"\n🎉 ÉXITO en {region}")
                return
        except Exception as e:
            print(f"  ⚠ {region}: {str(e)[:120]}")
    print("\n❌ Sin capacidad en ninguna región suscrita. Reintentará en próximo ciclo.")

if __name__ == "__main__":
    main()
