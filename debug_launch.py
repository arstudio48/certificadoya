#!/usr/bin/env python3
"""Intento crear instancia"""
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
    imgs = oci.pagination.list_call_get_all_results(
        compute.list_images, compartimento,
        operating_system="Canonical Ubuntu",
        sort_by="TIMECREATED", sort_order="DESC"
    ).data
    arm = [i for i in imgs if 'aarch64' in (i.display_name or '').lower()]
    image_id = arm[0].id
    print(f"Imagen: {image_id}")
    
    # Obtener subnet existente
    vcns = oci.pagination.list_call_get_all_results(
        network.list_vcns, compartimento, display_name="certificadoya-vcn"
    ).data
    vcn_id = vcns[0].id
    
    subnets = oci.pagination.list_call_get_all_results(
        network.list_subnets, compartimento, vcn_id=vcn_id, display_name="public-subnet"
    ).data
    subnet_id = subnets[0].id
    print(f"Subnet: {subnet_id}")
    
    # Leer clave SSH
    with open(SSH_PUB) as f:
        ssh_key = f.read().strip()
    
    # Preparar metadata
    metadata = {
        "user_data": base64.b64encode(CLOUD_INIT.encode()).decode(),
        "ssh_authorized_keys": ssh_key
    }
    
    # Crear instancia
    print("\nIntentando crear instancia...")
    details = oci.core.models.LaunchInstanceDetails(
        compartment_id=compartimento,
        display_name="certificadoya-oracle",
        availability_domain=ad,
        shape="VM.Standard.A1.Flex",
        shape_config=oci.core.models.LaunchInstanceShapeConfigDetails(ocpus=2, memory_in_gbs=12),
        source_details=oci.core.models.InstanceSourceViaImageDetails(
            source_type="image", image_id=image_id
        ),
        create_vnic_details=oci.core.models.CreateVnicDetails(
            subnet_id=subnet_id, assign_public_ip=True, display_name="vnic-public"
        ),
        metadata=metadata
    )
    
    try:
        response = compute.launch_instance(details)
        print(f"Respuesta: {response}")
        print(f"Instance ID: {response.data.id}")
        print("Esperando estado RUNNING...")
        instance = oci.wait_until(compute, compute.get_instance(response.data.id), 'lifecycle_state', 'RUNNING')
        print(f"Instancia creada: {instance.id} - {instance.display_name}")
    except oci.exceptions.ServiceError as e:
        print(f"ServiceError: {e}")
        print(f"  Status: {e.status}")
        print(f"  Code: {e.code}")
        print(f"  Request ID: {e.request_id}")
        print(f"  Message: {e.message}")
        if 'Out of host capacity' in str(e):
            print("\n==> OUT OF HOST CAPACITY")
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()