resource "terraform_data" "replacement" {
  provisioner "local-exec" {
    command = "echo 'This is the EKS ${var.env}' environment saying '${var.text}'"
  }
}
