resource "terraform_data" "replacement" {
  provisioner "local-exec" {
    command = "echo 'This was ECS ${var.environment}' environment but now we are migrating toe EKS running build_tag '${var.build_tag}'"
  }
}
