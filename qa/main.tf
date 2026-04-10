module "service" {
  source = "../modules/ecs"

  environment = var.environment
  text        = var.text
  build_tag   = var.build_tag
} 

resource "terraform_data" "test_infra" {
  provisioner "local-exec" {
    command = "echo  'Extra testing infrastructure for QA environment'"
  }
}
