#!/usr/bin/env python3
"""Ejecutar el script Oracle directamente"""
import oci
import base64

CONFIG_PATH = r"C:\Users\artur\.oci\config"
PRIVATE_KEY = r"C:\Users\artur\.oci\oci_api_key.pem"
SSH_PUB = r"C:\Users\artur\.ssh\id_rsa.pub"
REGIONES_CANDIDATAS = ["eu-madrid-3", "eu-frankfurt-1", "uk-london-1", "us-ashburn-1"]

print("=== VERIFICANDO ESTADO ACTUAL ===")

try:
    config = oci.config.from_file(CONFIG_PATH)
    config["key_file"] = PRIVATE_KEY
    identity = oci.identity.IdentityClient(config)
    compartimento = config["tenancy"]
    
    # Ver regiones suscritas
    regions = oci.pagination.list_call_get_all_results(
        identity.list_region_subscriptions, compartimento
    ).data
    regiones_suscritas = [r.region_name for r in regions]
    print(f"Regiones suscritas: {regiones_suscritas}")
    
    # Ver si existe instancia
    compute_eu = oci.core.ComputeClient({**config, "region": "eu-madrid-3"})
    existing = oci.pagination.list_call_get_all_results(
        compute_eu.list_instances, compartimento, display_name="certificadoya-oracle"
    ).data
    running = [i for i in existing if i.lifecycle_state in ('RUNNING', 'PROVISIONING')]
    print(f"Instancias existentes: {len(running)}")
    if running:
        print("Ya existe instancia corriendo - ÉXITO")
    else:
        # Verificar si hay capacity
        print("Intentando crear en eu-madrid-3...")
        network = oci.core.VirtualNetworkClient(config)
        compute = oci.core.ComputeClient({**config, "region": "eu-madrid-3"})
        
        # Verificar VCN y subnet
        vcns = oci.pagination.list_call_get_all_results(
            network.list_vcns, compartimento, display_name="certificadoya-vcn"
        ).data
        vcn_id = vcns[0].id if vcns else None
        
        if vcn_id:
            subnets = oci.pagination.list_call_get_all_results(
                network.list_subnets, compartimento, vcn_id=vcn_id, display_name="public-subnet"
            ).data
            subnet_id = subnets[0].id if subnets else None
            
            if subnet_id:
                # Obtener imagen
                imgs = oci.pagination.list_call_get_all_results(
                    compute.list_images, compartimento,
                    operating_system="Canonical Ubuntu",
                    sort_by="TIMECREATED", sort_order="DESC"
                ).data
                arm = [i for i in imgs if 'aarch64' in (i.display_name or '').lower()]
                if arm:
                    image_id = arm[0].id
                    
                    # Intentar lanzar
                    print("Probando lanzamiento...")
                    details = oci.core.models.LaunchInstanceDetails(
                        compartment_id=compartimento,
                        display_name="certificadoya-oracle",
                        availability_domain="BYCK:EU-MADRID-3-AD-1",
                        shape="VM.Standard.A1.Flex",
                        shape_config=oci.core.models.LaunchInstanceShapeConfigDetails(ocpus=2, memory_in_gbs=12),
                        source_details=oci.core.models.InstanceSourceViaImageDetails(
                            source_type="image", image_id=image_id
                        ),
                        create_vnic_details=oci.core.models.CreateVnicDetails(
                            subnet_id=subnet_id, assign_public_ip=True, display_name="vnic-public"
                        ),
                        metadata={"user_data": base64.b64encode(b"#cloud-config\npackages:\n  - nginx\nruncmd:\n  - echo 'Hello World'").decode()}
                    )
                    
                    try:
                        response = compute.launch_instance(details)
                        print("INSTANCE LANZADA, ESPERANDO...")
                        instance = oci.wait_until(compute, compute.get_instance(response.data.id), 'lifecycle_state', 'RUNNING', max_wait_seconds=600)
                        vnics = oci.pagination.list_call_get_all_results(
                            compute.list_vnic_attachments, compartimento, instance_id=instance.id
                        ).data
                        vnic = network.get_vnic(vnics[0].vnic_id).data
                        print(f"ÉXITO|{vnic.public_ip}")
                    except oci.exceptions.ServiceError as e:
                        if 'Out of host capacity' in str(e):
                            print("[SILENT] - Out of host capacity")
                        else:
                            print(f"ERROR|{str(e)[:200]}")
            else:
                print("Verificando subnet...")
except Exception as e:
    print(f"ERROR|{str(e)[:200]}")
    import traceback
    traceback.print_exc()