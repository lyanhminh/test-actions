module "service" {
  source = "github.com/lyanhminh/test-actions//modules/ecs?ref=0.0.1"

  environment = "production"
  text        = "olly"
} 
