import os
import unittest

import boto3
from pulumi import automation as auto


class TestEC2(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.STACK_NAME = 'e2e'
        cls.REGION_NAME = 'eu-central-1'
        cls.WORK_DIR = os.path.join(os.path.dirname(__file__))

        cls.stack = auto.create_or_select_stack(stack_name=cls.STACK_NAME, work_dir=cls.WORK_DIR)
        cls.stack.set_config("aws:region", auto.ConfigValue(value=cls.REGION_NAME))
        cls.stack.up(on_output=print)
        cls.outputs = cls.stack.outputs()
        cls.ec2 = boto3.resource('ec2')

    @classmethod
    def tearDownClass(cls) -> None:
        cls.stack.destroy(on_output=print)
        cls.stack.workspace.remove_stack(cls.STACK_NAME)

    def test_instances_count(self):
        instances = self.ec2.instances.all()
        instance_names = []
        for instance in instances:
            instance_names.append(instance.name)
        output_web_server = self.outputs.get('web_server').value
        output_backend_server = self.outputs.get('backend_server').value
        print(output_backend_server)
        self.assertIn('tags', output_web_server)
        self.assertIn('Name', output_web_server['tags'])
        self.assertIn(output_web_server['tags']['Name'], instance_names)
        self.assertIn('tags', output_backend_server)
        self.assertIn('Name', output_backend_server['tags'])
        self.assertIn(output_backend_server['tags']['Name'], instance_names)


if __name__ == '__main__':
    unittest.main()