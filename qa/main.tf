module "service" {
  source = "github.com/lyanhminh/test-actions//modules/ecs?ref=0.0.1"

  environment = "qa"
  text        = var.text
  build_tag   = var.build_tag
} 

resource "terraform_data" "test_infra" {
  provisioner "local-exec" {
    command = "echo  'Extra testing infrastructure for QA environment'"
  }
}
