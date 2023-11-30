# login
aws ecr-public get-login-password --region us-east-1 | docker login --username AWS --password-stdin public.ecr.aws

# build ingest image + tag it
docker build . --file .ingest.Dockerfile --tag 167698347898.dkr.ecr.eu-west-1.amazonaws.com/alec-ingest-tf:latest

# build transform image + tag it
docker build . --file .transform.Dockerfile --tag 167698347898.dkr.ecr.eu-west-1.amazonaws.com/alec-transform-tf:latest

# build egress image + tag it
docker build . --file .egress.Dockerfile --tag 167698347898.dkr.ecr.eu-west-1.amazonaws.com/alec-egress-tf:latest