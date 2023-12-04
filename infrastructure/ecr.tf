resource "aws_ecr_repository" "ingest-repo" {

  name                 = "alec-ingest-tf"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_ecr_repository" "transform-repo" {

  name                 = "alec-transform-tf"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_ecr_repository" "create-datamarts-repo" {

  name                 = "alec-create-datamarts-tf"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_ecr_repository" "egress-repo" {

  name                 = "alec-egress-tf"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}