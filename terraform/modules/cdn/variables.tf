variable "project_name" {
  description = "Project name used for naming and tags"
  type        = string
}

variable "alb_dns_name" {
  description = "DNS name of the load balancer CloudFront forwards to"
  type        = string
}

variable "price_class" {
  description = "CloudFront price class"
  type        = string
  default     = "PriceClass_100"

  validation {
    condition     = contains(["PriceClass_100", "PriceClass_200", "PriceClass_All"], var.price_class)
    error_message = "price_class must be PriceClass_100, PriceClass_200 or PriceClass_All."
  }
}
