#!/usr/bin/env python3
"""
Oracle Cloud Free Tier — Crear instancia Always-Free en eu-madrid-3
Usa OCI SDK (Python). Requiere ~/.oci/config y ~/.oci/oci_api_key.pem
"""
import oci
import time

# Config se lee automáticamente de ~/.oci/config
config = oci.config.from_file()

# Clientes
compute = oci.core.ComputeClient(config)
network = oci.core.VirtualNetworkClient(config)
identity = oci.identity.IdentityClient(config)

# Parámetros
COMPARTIMENTO = config["tenancy"]  # Usamos el tenancy como compartment root
REGION = "eu-madrid-3"
# Obtener AD disponibles
ads = oci.pagination.list_call_get_all_results(
    identity.list_availability_domains, COMPARTIMENTO
).data
AD = ads[0].name  # Primer AD disponible
print(f"  AD seleccionado: {AD}")

def get_shape():
    """Devuelve la shape always-free disponible (ARM AMpere 4 OCPU / 24GB o AMD 2x1GB)"""
    # Intentamos ARM primero (mejor)
    return "VM.Standard.A1.Flex"

def get_image():
    """Busca la imagen ARM (aarch64) de Ubuntu 22.04 más reciente en la región"""
    list_images = oci.pagination.list_call_get_all_results(
        compute.list_images,
        COMPARTIMENTO,
        operating_system="Canonical Ubuntu",
        sort_by="TIMECREATED",
        sort_order="DESC"
    )
    # Filtrar solo ARM (aarch64)
    arm = [i for i in list_images.data if 'aarch64' in (i.display_name or '').lower()]
    if not arm:
        arm = [i for i in list_images.data if 'VM.Standard.A1.Flex' in (i.compatible_shapes or [])]
    return arm[0].id

def get_subnet():
    """Encuentra o crea una VCN + subnet pública"""
    # Buscar VCN existente
    vcns = oci.pagination.list_call_get_all_results(
        network.list_vcns, COMPARTIMENTO, display_name="certificadoya-vcn"
    ).data
    if vcns:
        vcn_id = vcns[0].id
    else:
        vcn = network.create_vcn(oci.core.models.CreateVcnDetails(
            cidr_block="10.0.0.0/16",
            display_name="certificadoya-vcn",
            compartment_id=COMPARTIMENTO
        )).data
        vcn_id = vcn.id
        # Esperar a que esté disponible
        oci.wait_until(network, network.get_vcn(vcn_id), 'lifecycle_state', 'AVAILABLE')

    # Buscar subnet
    subnets = oci.pagination.list_call_get_all_results(
        network.list_subnets, COMPARTIMENTO, vcn_id=vcn_id, display_name="public-subnet"
    ).data
    if subnets:
        return subnets[0].id, vcn_id

    # Crear Internet Gateway
    ig = network.create_internet_gateway(oci.core.models.CreateInternetGatewayDetails(
        compartment_id=COMPARTIMENTO,
        vcn_id=vcn_id,
        display_name="igw",
        is_enabled=True
    )).data

    # Crear route table
    rt = network.create_route_table(oci.core.models.CreateRouteTableDetails(
        compartment_id=COMPARTIMENTO,
        vcn_id=vcn_id,
        display_name="public-rt",
        route_rules=[oci.core.models.RouteRule(
            destination="0.0.0.0/0",
            destination_type="CIDR_BLOCK",
            network_entity_id=ig.id
        )]
    )).data

    # Crear subnet pública
    subnet = network.create_subnet(oci.core.models.CreateSubnetDetails(
        compartment_id=COMPARTIMENTO,
        vcn_id=vcn_id,
        display_name="public-subnet",
        cidr_block="10.0.1.0/24",
        route_table_id=rt.id,
        prohibit_public_ip_on_vnic=False
    )).data
    oci.wait_until(network, network.get_subnet(subnet.id), 'lifecycle_state', 'AVAILABLE')
    return subnet.id, vcn_id

def main():
    import time
    print(f"🚀 Creando instancia Always-Free en {REGION}...")
    image_id = get_image()
    print(f"  Imagen: {image_id}")
    subnet_id, vcn_id = get_subnet()

    cloud_init = """#cloud-config
package_update: true
packages:
  - curl
runcmd:
  - curl -fsSL https://tailscale.com/install.sh | sh
  - tailscale up --authkey=tskey-auth-REEMPLAZAR --advertise-tags=tag:oracle
"""

    ads = oci.pagination.list_call_get_all_results(
        identity.list_availability_domains, COMPARTIMENTO
    ).data
    ad_names = [a.name for a in ads]
    print(f"  ADs disponibles: {ad_names}")

    last_err = None
    for ad in ad_names:
        instance_details = oci.core.models.LaunchInstanceDetails(
            compartment_id=COMPARTIMENTO,
            display_name="certificadoya-oracle",
            availability_domain=ad,
            shape="VM.Standard.A1.Flex",
            shape_config=oci.core.models.LaunchInstanceShapeConfigDetails(
                ocpus=2,
                memory_in_gbs=12
            ),
            source_details=oci.core.models.InstanceSourceViaImageDetails(
                source_type="image",
                image_id=image_id
            ),
            create_vnic_details=oci.core.models.CreateVnicDetails(
                subnet_id=subnet_id,
                assign_public_ip=True,
                display_name="vnic-public"
            ),
            metadata={
                "ssh_authorized_keys": open(r"C:\Users\artur\.ssh\id_rsa.pub").read().strip(),
                "user_data": __import__('base64').b64encode(cloud_init.encode()).decode()
            }
        )
        try:
            instance = compute.launch_instance(instance_details).data
            print(f"✅ Instancia creada en AD {ad}: {instance.id}")
            oci.wait_until(compute, compute.get_instance(instance.id), 'lifecycle_state', 'RUNNING')
            vnics = oci.pagination.list_call_get_all_results(
                compute.list_vnic_attachments, COMPARTIMENTO, instance_id=instance.id
            ).data
            vnic = network.get_vnic(vnics[0].vnic_id).data
            print(f"🌐 IP pública: {vnic.public_ip}")
            print(f"🔑 Conéctate con: ssh ubuntu@{vnic.public_ip}")
            return
        except Exception as e:
            err = str(e)
            if 'Out of host capacity' in err:
                print(f"  ⏳ AD {ad}: sin capacidad, probando siguiente...")
                last_err = e
                continue
            else:
                raise
    print("❌ No hay capacidad en ningún AD ahora mismo. Reintenta más tarde (Oracle libera capacidad a distintas horas).")
    if last_err:
        raise last_err

if __name__ == "__main__":
    main()
