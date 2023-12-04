terraform {
    backend "s3" {
        bucket = "data-track-integrated-exercise"
        key    = "Alec-data/terraform"
        region = "eu-west-1"
    }
}