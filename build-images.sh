# login
aws ecr-public get-login-password --region us-east-1 | docker login --user name AWS --password-stdin public.ecr.aw

# build ingest image + tag it
docker build . --file .ingest.Dockerfile --tag public.ecr.aws/t1k8b0u7/alec-ingest:latest

# build transform image + tag it
docker build . --file .transform.Dockerfile --tag public.ecr.aws/t1k8b0u7/alec-transform:latest