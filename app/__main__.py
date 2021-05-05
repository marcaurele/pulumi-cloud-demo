"""Cloud engineering exercise in Pulumi"""

import pulumi
import pulumi_aws as aws

size = 't3.micro'

# Cannot use ED25519 keys!
deployer = aws.ec2.KeyPair("pix4d-backend",
    public_key="ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQC9HOOxB6T48ajUxQzp5qKOIc63GIob8+dOUb7IWQ+cy7kx2gb1LZR5/17yN56LHYx6QMyhbE1O0BwHSPu5oQOBtChkg62Ygjx+V5cntyNUbBWPKvpCEKU3GQN9IejyFVpKB35p4vDnSKEcpEN8UFj8u3fqYtIyZvw2RRUMIJb0n41U6HtnfnL6rX6zlkLnRWZrHczGcPfb6W3NzHX9rI2353yuoFEWkqiqa295KQ6pOQkNImuTdOkc0sIoNAxF+M2bu6nZBRrjDRBikdhHn0YyKTZByDu227XkUFIUszFhi6gOajvyZa1TtFUGdenfarhsisana+LFK/vx0Ct81xvASaT/gPYUXN03d+WplY76Ew6MDYVt/T3PlBaF1RPUiwcGFs1EsqaTAYp5/uGAIvGf0ITj79edKcEAz4FnUt1eLWLJ2xmBgEQP+nw2mIw+IM1IJEyGzdiBeX5yL1KUkQKkDvXlvbpQkcsVjvkRnSb1pGJ9ZR49BxoYzXyKXm26vl8ryWC07+n5ZxV/phgsE553fIUSCRUb/BPKtxWxHeq4fa18bmqVMRSm9aQv+JRpgjtRD2SsuE9qiNdgxirPhrvrhUcCsR7D3dT3D027VzvbIC8aav75v/9U/SXbSOVCB1JpSRsas2GZO6N8VmGrldvkyD2+qFY9BT67ezPpXVIh/Q== ch_dev_cloud_backend@pix4d.com")

ami = aws.ec2.get_ami(most_recent=True,
                  owners=["099720109477"],
                  filters=[
                    {
                      "name":"root-device-type",
                      "values":["ebs"]
                    },
                    {
                      "name":"virtualization-type",
                      "values":["hvm"]
                    },
                  ],
                  name_regex="ubuntu/images/hvm-ssd/ubuntu-focal")

sec_group_ssh = aws.ec2.SecurityGroup('ssh-access',
    description='Enable SSH access',
    ingress=[aws.ec2.SecurityGroupIngressArgs(
        description="SSH to server",
        from_port=22,
        to_port=22,
        protocol="tcp",
        cidr_blocks=["0.0.0.0/0"],
        ipv6_cidr_blocks=["::/0"],
    )])
sec_group_http = aws.ec2.SecurityGroup('webserver-http',
    description='Enable HTTP access',
    ingress=[aws.ec2.SecurityGroupIngressArgs(
        description="HTTP to server",
        from_port=80,
        to_port=80,
        protocol="tcp",
        cidr_blocks=["0.0.0.0/0"],
        ipv6_cidr_blocks=["::/0"],
    )])
sec_group_outbound = aws.ec2.SecurityGroup('outbound-traffic',
    description='Enable outbound traffic',
    egress=[aws.ec2.SecurityGroupEgressArgs(
        description="Allow all",
        from_port=0,
        to_port=0,
        protocol="-1",
        cidr_blocks=["0.0.0.0/0"],
        ipv6_cidr_blocks=["::/0"],
    )])

user_data = """
#cloud-config
users:
  - default
  - name: pix4d
    ssh_authorized_keys:
      - ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIOqxR74+cr66BvCK7hHwXq/jDdUnJy4EWanNtD9SkZhB openpgp:0xF98C6282
    sudo: ['ALL=(ALL) NOPASSWD:ALL']
    groups: sudo
    shell: /bin/bash
"""

user_data_webserver = user_data + """
repo_update: true
repo_upgrade: all

packages:
  - nginx
"""

web_server = aws.ec2.Instance('webserver-www',
    instance_type=size,
    vpc_security_group_ids=[sec_group_ssh.id, sec_group_http.id, sec_group_outbound.id],
    ami=ami.id,
    key_name=deployer.key_name,
    user_data=user_data_webserver,
    tags={"Name": "webserver"})

backend_server = aws.ec2.Instance('backend',
    instance_type=size,
    vpc_security_group_ids=[sec_group_ssh.id, sec_group_outbound.id],
    ami=ami.id,
    key_name=deployer.key_name,
    user_data=user_data,
    tags={"Name": "backend"})

pulumi.export('amiId', ami.id)
pulumi.export('web_server', web_server)
pulumi.export('backend_server', backend_server)
pulumi.export('publicIp', web_server.public_ip)
pulumi.export('publicHostName', web_server.public_dns)
