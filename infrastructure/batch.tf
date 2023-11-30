resource "aws_batch_job_definition" "ingest" {
  name = "dt-alec-ingest-tf"
  type = "container"
  container_properties = jsonencode({
    command = ["ls", "-la"],
    image   = "167698347898.dkr.ecr.eu-west-1.amazonaws.com/alec-ingest-tf:latest",
    jobRoleArn = "arn:aws:iam::167698347898:role/integrated-exercise/integrated-exercise-batch-job-role",
    executionRoleArn = "arn:aws:iam::167698347898:role/integrated-exercise/integrated-exercise-batch-job-role",
    resourceRequirements = [
      {
        type  = "VCPU"
        value = "1"
      },
      {
        type  = "MEMORY"
        value = "512"
      }
    ]
  })
  timeout {
    attempt_duration_seconds = 1800
  }
}

resource "aws_batch_job_definition" "transform" {
  name = "dt-alec-transform-tf"
  type = "container"
  container_properties = jsonencode({
    command = ["ls", "-la"],
    image   = "167698347898.dkr.ecr.eu-west-1.amazonaws.com/alec-transform-tf:latest",
    jobRoleArn = "arn:aws:iam::167698347898:role/integrated-exercise/integrated-exercise-batch-job-role",
    executionRoleArn = "arn:aws:iam::167698347898:role/integrated-exercise/integrated-exercise-batch-job-role",
    resourceRequirements = [
      {
        type  = "VCPU"
        value = "1"
      },
      {
        type  = "MEMORY"
        value = "512"
      }
    ]
  })
  timeout {
    attempt_duration_seconds = 1800
  }
}

resource "aws_batch_job_definition" "egress" {
  name = "dt-alec-egress-tf"
  type = "container"
  container_properties = jsonencode({
    command = ["ls", "-la"],
    image   = "167698347898.dkr.ecr.eu-west-1.amazonaws.com/alec-egress-tf:latest",
    jobRoleArn = "arn:aws:iam::167698347898:role/integrated-exercise/integrated-exercise-batch-job-role",
    executionRoleArn = "arn:aws:iam::167698347898:role/integrated-exercise/integrated-exercise-batch-job-role",
    resourceRequirements = [
      {
        type  = "VCPU"
        value = "1"
      },
      {
        type  = "MEMORY"
        value = "512"
      }
    ]
  })
  timeout {
    attempt_duration_seconds = 1800
  }
}