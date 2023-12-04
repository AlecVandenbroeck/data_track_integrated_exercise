aws ecr get-login-password --region eu-west-1 | docker login --username AWS --password-stdin 167698347898.dkr.ecr.eu-west-1.amazonaws.com
docker push 167698347898.dkr.ecr.eu-west-1.amazonaws.com/alec-ingest-tf:latest
docker push 167698347898.dkr.ecr.eu-west-1.amazonaws.com/alec-transform-tf:latest
docker push 167698347898.dkr.ecr.eu-west-1.amazonaws.com/alec-create-datamarts-tf:latest
docker push 167698347898.dkr.ecr.eu-west-1.amazonaws.com/alec-egress-tf:latest