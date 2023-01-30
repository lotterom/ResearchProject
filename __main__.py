import pulumi
from pulumi_azure_native import resources, network, compute
import pulumi_azure_native as azure_native
import pulumi_azure as azure
from pulumi_azure import sql
from pulumi_random import random_string
import base64
#import pulumi.secrets

# Import the program's configuration settings.
config = pulumi.Config()
loc = "westeurope"
vm_name = config.get("vmName", "*")
vm_size = config.get("vmSize", "Standard_DS1_v2")
os_image = config.get("osImage", "UbuntuServer:latest")
admin_username = config.get("adminUsername", "naam")
service_port = config.get("servicePort", "80")


# Create a resource group.
resource_group = resources.ResourceGroup("*")

# Create a virtual network.
virtual_network = network.VirtualNetwork(
    "vnet",
    resource_group_name=resource_group.name,
    address_space=network.AddressSpaceArgs(
        address_prefixes=["192.168.0.0/16"],
    ),
    subnets=[
        network.SubnetArgs(
            name="webservers",
            address_prefix="192.168.20.0/24",
        ),
        network.SubnetArgs(
            name="database",
            address_prefix="192.168.10.0/24",
        ),
    ],
)

# Create a public IP address
public_ip = network.PublicIPAddress("publicIP",
    resource_group_name=resource_group.name,
    public_ip_allocation_method=network.IpAllocationMethod.DYNAMIC,
)

#Create security group (inbount rules port 80 en 22)
network_SG = azure.network.NetworkSecurityGroup("security-group",
    location=loc,
    resource_group_name=resource_group.name,
    security_rules=[
        network.SecurityRuleArgs(
            name=f"{vm_name}-securityrule",
            priority=1000,
            direction=network.AccessRuleDirection.INBOUND,
            access="Allow",
            protocol="Tcp",
            source_port_range="*",
            source_address_prefix="*",
            destination_address_prefix="*",
            destination_port_ranges=[
                service_port,
                "22",
            ],
        ),
    ],
)

# Create a network interface
network_interface = network.NetworkInterface(
    "nic1",
    resource_group_name=resource_group.name,
    id=network_SG.id,
    ip_configurations=[
        network.NetworkInterfaceIPConfigurationArgs(
        name="ipconfig1",
        private_ip_allocation_method=network.IpAllocationMethod.DYNAMIC,
        subnet=network.SubnetArgs(
                id=virtual_network.subnets.apply(lambda subnets: subnets[0].id),
            ),
            public_ip_address=network.PublicIPAddressArgs(
                id=public_ip.id,
            ),
        ),
    ]
)

# Create a virtual machine
vm = compute.VirtualMachine("webserver",
    location=loc,
    resource_group_name=resource_group.name,
    network_profile=compute.NetworkProfileArgs(
        network_interfaces=[
            compute.NetworkInterfaceReferenceArgs(
                id=network_interface.id,
                primary=True,
            )
        ]
    ),
    hardware_profile=compute.HardwareProfileArgs(
        vm_size="Standard_DS1_v2",
    ),
    storage_profile=compute.StorageProfileArgs(
        os_disk=compute.OSDiskArgs(
            name="disk",
            create_option=compute.DiskCreateOption.FROM_IMAGE,
        ),
        image_reference=compute.ImageReferenceArgs(
            publisher="Canonical",
            offer="UbuntuServer",
            sku="16.04-LTS",
            version="latest",
        ),
    ),
    os_profile={
        "computer_name": "*",
        "admin_username": "*",
        "admin_password": "*",
    },
)

# Export the IP address of the virtual machine
pulumi.export("ip_address", public_ip.ip_address)

const cloudConfig = cloudinit.getConfig({
  gzip: false,
  base64Encode: false,
  parts: [
    {
      contentType: "text/x-shellscript",
      content: fs.readFileSync("script.sh", "utf8"),
    },
    {
      contentType: "text/x-shellscript",
      content: fs.readFileSync("../cloud-init/install-k3s.sh", "utf8"),
    },
  ],
});

#Create sql server
sql_server = azure.postgresql.Server("sqlserver",
    resource_group_name=resource_group.name,
    location=loc,
   sku_name="B_Gen5_1",
    storage_mb=5120,
    backup_retention_days=7,
    geo_redundant_backup_enabled=False,
    auto_grow_enabled=True,
    administrator_login="*",
    administrator_login_password="*",
    version="9.5",
    ssl_enforcement_enabled=True
)

#Create Sql Database
database = azure.postgresql.Database("database",
    resource_group_name=resource_group.name,
    server_name=sql_server.name,
    charset="UTF8",
    collation="English_United States.1252"
)