module "service" {
  source = "github.com/lyanhminh/test-actions//modules/eks?ref=0.0.1"

  environment = "qa"
  text        = var.text
} 
