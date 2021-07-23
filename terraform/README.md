# Flash Terraform

## Terraform Introduction

Terraform is an Infrastructure as Code (IaC) tool. It can be used to define and manage resources from a variety of local and cloud service providers (https://www.terraform.io/docs/providers/index.html). It is useful for maintaining repeatable, searchable, and hopefully consistent infrastructure.

Terraform accomplishes this by converting its configuration files into sets of api calls which it can execute. It saves the results of those calls as "state", which it uses on subsequent runs to determine if changes are needed.

Notes of Interest:
* There is no terraform daemon. It runs only when invoked. This can be done manually, in Terraform Cloud, or by CI scripting.
* Terraform only reads the config in the current working directory and the modules that config explicitly references.
* Terraform is helpful for managing infrastructure resources, but it is not a replacement for understanding relevant aspects of the target platform.
* Use a non-production account for manual testing, experimentation, and prototyping terraform config.
* Terraform will attempt to modify resources it controls so that they match the config. Some attributes cannot be changed in place, and require destroying/recreating the resource.
* Terraform config belongs in version control.
* Terraform state is not backwards compatible. Expect it to complain if you're trying to `plan` or `apply` with an older version than was last used.
* To keep pace with platform api changes, Terraform providers are frequently updated. If this worries you, consider pinning them.

## Usage Workflow

1. Have credentials accessible (e.g. `~/.aws/config` or env variables: `AWS_ACCESS_KEY_ID`, etc.)
1. Have a terraform config in your `pwd`
1. `terraform init` caches provider applications and module configs into `.terraform` (tf will complain if this needs done)
1. `terraform plan` compares resources as defined in the config with resources as described by the provider, and outputs what it would need to do to make the resource match what is specified in the config.
1. Edit the terraform config to make additions, changes, and removals.
1. `terraform apply` does the same as `plan` with the addition of the question: "Do you want me to do these things?"
    * Respond `yes` and Terraform will execute the plan.
1. It never hurts to run another `terraform plan`.

* Official docs: https://www.terraform.io/guides/core-workflow.html

## Useful commands
* `terraform state list`: list items stored in Terraform's state
* `terraform state show <resource_address>`: print details of item from Terraform's state
* `terraform import <resource_address> <identifier>`: bring an existing resource under Terraform's control (resource docs usually have an import example). You can do this with a _minimal_ resource config then use `terraform plan` or `terraform state show` to see about fleshing it out.
* `terraform state rm <resource_address>`: remove a resource from Terraform's control without changing it. You are then free to remove the Terraform config for the resource, and Terraform will not try to destroy it. Similarly, if you keep the config for the resource, Terraform will want to make a new one.
* `terraform console`: interact with the interpolation parser without running `plan` or `apply`. This is quite useful for working out tricky syntax issues.

Official docs: https://www.terraform.io/docs/cli-index.html

# File/Directory Organization

This repo contains a single directory of `terraform` config that supports the straightforward sudoku on EC2 solution.

## Reference Skeleton
```
cloud-ftp
└───terraform
│   backend.tf
|   locals.tf
|   resources.tf
|   ...
```

## Description and Details
* In the single `terraform` directory, we put terraform configuration files to specify the desired resources. Explanations of a few common/notable files included in the reference above:
   * `backend.tf` should contain the `provider` and `backend` blocks used in the config. It is also a reasonable location for frequently used `data` blocks.
   * `locals.tf` should contain a `locals` block, which can be used to set constant values that need to be reused, or are often defined in each config.
   * `resources.tf` is used here as a stand-in for any .tf file that is primarily defining `resource` blocks.
     It is reasonable for these to also include `data` or `locals` blocks if they are not anticipated to be used by resources defined elsewhere. To avoid very long resource files, I prefer to have resources of the same/related cloud service in files named after those services (e.g. `rds.tf`, `vpc.tf`, `ec2_bastion.tf`, etc.)
    * Not always used, `outputs.tf` should contain the complete set of `output` blocks defined in a module or config. Output blocks are used primarily to expose attributes of resources created by `modules` to the "calling" Terraform config. They are also used to allow resource attributes to be read via `data.terraform_remote_state` blocks in other configs (e.g. in the `shared` directory). They also cause values to be printed in the output of `plan` and `apply` operations.
    * `variables.tf` should contain the complete set of `variable` blocks in a module or config. Variable blocks are used to provide a parameterization capability for Terraform modules and workspace-aware configs.
    * `main.tf` is the conventional name for the file which defines resources in a Terraform module.

Official docs: https://www.terraform.io/docs/configuration/index.html

# Principles of Use

It is best if no resources are created for production use outside of terraform.

It is best if no modifications to production resources are made outside of terraform.
