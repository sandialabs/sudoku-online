
provider "aws" {
  region  = "us-east-1"


  default_tags {
    tags = {
      automation          = "terraform"
      "automation.config" = "sudoku/terraform"
    }
  }
}

# provider "aws" {
#   alias  = "utility"
#   region = "us-east-1"
#   assume_role {
#     role_arn = "arn:aws:iam::339610064134:role/OrganizationAccountAccessRole"
#   }
# }