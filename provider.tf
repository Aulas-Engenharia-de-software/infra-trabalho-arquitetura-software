provider "aws" {
  region = var.aws_region
}

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# Pega dados da conta (Region, Account ID) dinamicamente
data "aws_region" "current" {}
data "aws_caller_identity" "current" {}