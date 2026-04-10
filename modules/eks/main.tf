resource "terraform_data" "replacement" {
  provisioner "local-exec" {
    command = "echo 'This is the EKS ${var.environment}' environment saying '${var.text}' on build tag '${var.build_tag}'" "
  }
}
