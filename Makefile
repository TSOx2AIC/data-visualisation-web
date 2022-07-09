DOCKER_REGISTRY=europe-west1-docker.pkg.dev/tsox2aic/tsox2aic
IMAGE_NAME=data-visualisation-web
SERVICE_NAME=data-visualisation-web

.PHONY: activate
## activate: activates the python virtual environment
activate:
		source venv/bin/activate

.PHONY: run-local
## run-local: runs the streamlit application
run-local:
		streamlit run main.py


.PHONY: build
## build: builds the docker image
build:
		pip3 freeze > requirements.txt  
		docker build . -t ${IMAGE_NAME}

.PHONY: run
## run: runs the docker container
run:
		docker run -p 8501:8501 -d ${IMAGE_NAME} --name ${IMAGE_NAME}


.PHONY: push
## push: pushes the docker image to the cloud artifact registry
push:
		docker tag ${IMAGE_NAME} ${DOCKER_REGISTRY}/${IMAGE_NAME}
		docker push ${DOCKER_REGISTRY}/${IMAGE_NAME}


.PHONY: deploy
## deploy: deploys the latest docker image to cloud run
deploy:
		gcloud run deploy ${SERVICE_NAME} --image ${DOCKER_REGISTRY}/${IMAGE_NAME}

.PHONY: help
## help: prints this help message
help:
		@echo "Usage: \n"
		@sed -n 's/^##//p' ${MAKEFILE_LIST} | column -t -s ':' |  sed -e 's/^/ /'