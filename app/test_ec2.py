import unittest
import pulumi


class MyMocks(pulumi.runtime.Mocks):
    def new_resource(self, args: pulumi.runtime.MockResourceArgs):
        outputs = args.inputs
        if args.typ == "aws:ec2/instance:Instance":
            outputs = {
                **args.inputs,
                "publicIp": "203.0.113.12",
                "publicDns": "ec2-203-0-113-12.compute-1.amazonaws.com",
            }
        return [args.name + '_id', outputs]
    def call(self, args: pulumi.runtime.MockCallArgs):
        print(args.token)
        if args.token == "aws:ec2/getAmi:getAmi":
            return {
                "architecture": "x86_64",
                "id": "ami-0eb1f3cdeeb8eed2a",
            }
        return {}

pulumi.runtime.set_mocks(MyMocks())


# It's important to import `infra` _after_ the mocks are defined.
import infra

class TestingWithMocks(unittest.TestCase):

    # check 1: Instances have a Name tag.
    @pulumi.runtime.test
    def test_server_tags(self):
        def check_tags(args):
            urn, tags = args
            self.assertIsNotNone(tags, f'server {urn} must have tags')
            self.assertIn('Name', tags, 'server {urn} must have a name tag')

        return pulumi.Output.all(infra.web_server.urn, infra.web_server.tags).apply(check_tags)

    # check 2: Instances must not use an inline userData script.
    @pulumi.runtime.test
    def test_server_userdata(self):
        def check_user_data(args):
            urn, user_data = args
            self.assertFalse(user_data, f'illegal use of user_data on server {urn}')

        return pulumi.Output.all(infra.web_server.urn, infra.web_server.user_data).apply(check_user_data)

    # check 3: Test if port 22 for ssh is exposed.
    @pulumi.runtime.test
    def test_security_group_rules(self):
        def check_security_group_rules(args):
            urn, ingress = args
            ssh_open = any([rule['from_port'] == 22 and any([block == "0.0.0.0/0" for block in rule['cidr_blocks']]) for rule in ingress])
            self.assertFalse(ssh_open, f'security group {urn} exposes port 22 to the Internet (CIDR 0.0.0.0/0)')

        return pulumi.Output.all(infra.sec_group_http.urn, infra.sec_group_http.ingress).apply(check_security_group_rules)

    # check 4: Instance sec groups don't include one like ssh
    @pulumi.runtime.test
    def test_instances_security_group_rules(self):
        def check_instances_security_group_rules(args):
            urn, sec_groups = args
            for sec_group_name in sec_groups:
                self.assertNotIn('ssh', sec_group_name, f'instance {urn} has a security group ssh')

        return pulumi.Output.all(infra.web_server.urn, infra.web_server.vpc_security_group_ids).apply(check_instances_security_group_rules)
