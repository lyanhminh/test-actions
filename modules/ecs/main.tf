resource "terraform_data" "replacement" {
  provisioner "local-exec" {
    command = "echo 'This is the ECS ${var.environment}' environment saying, '${var.text}' running with build tag '${var.build_tag}'"
  }
}
