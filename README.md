# Pulumi cloud demo

## Cloud service vs local

To not use the pulumi cloud services: `pulumi login --local`.

Otherwise using the cloud services you will enjoy the UI.

## Stage 1

Start a new project: `pulumi new aws-python --dir app --name cloud-app --stack cloud-app-dev`

Verify the project:

    * `cd app`
    * `pulumi up`
