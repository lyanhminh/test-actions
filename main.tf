variable "name" {}

module "s3" {
  source = "github.com/lyanhminh/tfm-s3"

  name   = "thing"
}
