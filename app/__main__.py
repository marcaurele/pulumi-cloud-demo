"""Cloud engineering exercise in Pulumi"""

import pulumi
import pulumi_aws as aws

size = 't3.micro'
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
    ingress=[
        { 'protocol': 'tcp', 'from_port': 22, 'to_port': 22, 'cidr_blocks': ['0.0.0.0/0'] },
    ])
sec_group_http = aws.ec2.SecurityGroup('webserver-http',
    description='Enable HTTP access',
    ingress=[
        { 'protocol': 'tcp', 'from_port': 80, 'to_port': 80, 'cidr_blocks': ['0.0.0.0/0'] },
    ])

web_server = aws.ec2.Instance('webserver-www',
    instance_type=size,
    vpc_security_group_ids=[sec_group_ssh.id, sec_group_http.id],
    ami=ami.id)

pulumi.export('amiId', ami.id)
pulumi.export('publicIp', web_server.public_ip)
pulumi.export('publicHostName', web_server.public_dns)