# Pulumi cloud demo

## Cloud service vs local

To not use the pulumi cloud services: `pulumi login --local`.

Otherwise using the cloud services you will enjoy the UI.

## Stage 1

Start a new project: `pulumi new aws-python --dir app --name cloud-app --stack cloud-app-dev`

Verify the project:

    * `cd app`
    * `pulumi up`

## Stage 2

Change the type of resources and create a server in eu-central-1 based
on a Ubuntu 20.04 image as a webserver. Opens the port `22` for SSH access
and port `80` for HTTP.

You can try to log on the server but where is the password?

## Stage 3

Add SSH key, add backend server, open internet access to download packages,
upgrades. Customize the image with cloud-init configuration steps.

## Stage 4

Add unit tests to the infrastructure. Verify and fix the tests:

    ./venv/bin/python -m unittest
