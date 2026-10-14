# FastAPI on Google Cloud Run

A small FastAPI service packaged as a Docker image and deployed with Cloud Build to Artifact Registry and Cloud Run in `asia-south1`.

## Endpoints

- `GET /` returns a welcome message.
- `GET /health` returns `{"status":"healthy"}`.
- `GET /users/{user_id}` accepts an integer and returns it as an example user record.
- FastAPI serves Swagger UI at `/docs` and the OpenAPI schema at `/openapi.json`.

## Run locally on macOS

Install Python 3.12 if needed (for example, with Homebrew):

```sh
brew install python@3.12
```

From this directory, create and activate a virtual environment, install dependencies, and start the server:

```sh
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
uvicorn main:app --reload
```

Open `http://127.0.0.1:8000/docs`, or use:

```sh
curl http://127.0.0.1:8000/
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/users/123
```

## Deploy to Google Cloud

### Prerequisites

You need a Google Cloud account with billing enabled on a project, permission to enable APIs and create an Artifact Registry repository, and access to use Cloud Build and Cloud Run. Install the Google Cloud CLI on macOS with Homebrew:

```sh
brew install --cask google-cloud-sdk
```

Start a shell session that has `gcloud` on its path if prompted, then authenticate and select your project. Replace `YOUR_PROJECT_ID` with the project ID:

```sh
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
gcloud config get-value project
```

Enable the APIs and create the Docker repository (the location must match the image location in `cloudbuild.yaml`):

```sh
gcloud services enable cloudbuild.googleapis.com run.googleapis.com artifactregistry.googleapis.com
gcloud artifacts repositories create fastapi-repo \
  --repository-format=docker \
  --location=asia-south1 \
  --description="Docker images for the FastAPI application"
```

Submit the build from this project directory:

```sh
gcloud builds submit --config=cloudbuild.yaml .
```

By default, the deploy does not grant public (unauthenticated) access. To explicitly request public invocation, submit with this option:

```sh
gcloud builds submit --config=cloudbuild.yaml \
  --substitutions=_ALLOW_UNAUTHENTICATED=true .
```

The identity running the build must be permitted to deploy the service and grant the requested access. Public access also depends on project organization policies. Review this choice before using it.

Once deployment succeeds, retrieve the service URL and call the routes:

```sh
SERVICE_URL="$(gcloud run services describe fastapi-service \
  --region=asia-south1 --format='value(status.url)')"
printf '%s\n' "$SERVICE_URL"
curl "$SERVICE_URL/"
curl "$SERVICE_URL/health"
open "$SERVICE_URL/docs"
```

If the service is private, `curl` and the browser need an identity token. For example:

```sh
TOKEN="$(gcloud auth print-identity-token)"
curl -H "Authorization: Bearer $TOKEN" "$SERVICE_URL/health"
```

The `/docs` UI also needs access to the app's OpenAPI endpoint, so use an authenticated browser session or temporarily test it locally when the deployed service is private.

## What the Google Cloud services do

- **Cloud Build** runs the Docker build, pushes the image, and deploys the service from the build configuration.
- **Artifact Registry** stores the versioned container image at `asia-south1-docker.pkg.dev/PROJECT_ID/fastapi-repo/fastapi-app:BUILD_ID`.
- **Cloud Run** runs the container as a managed HTTP service and provides its service URL.

## IAM permissions

The human or CI identity submitting builds needs permission to submit Cloud Build jobs and use the project. The Cloud Build execution service account needs permission to push images to the `fastapi-repo` Artifact Registry repository (`roles/artifactregistry.writer`), deploy Cloud Run services (`roles/run.admin`), and act as the runtime service account (`roles/iam.serviceAccountUser`). API enablement and repository creation require the corresponding Service Usage and Artifact Registry administration permissions. Exact grants depend on organization policy and whether the project uses the legacy or newer default Cloud Build service account. Follow least privilege and have an administrator grant only the roles actually needed; this project does not change IAM policy.

Granting unauthenticated invocation is a separate access decision. The build account must be allowed to set the service's invoker policy, and organization policy may prevent public access. The default build does not request it.

## Costs

Cloud Build build minutes, Artifact Registry image storage and network egress, and Cloud Run CPU/memory/request usage may incur charges. Free allowances and prices can change; check current Google Cloud pricing and quotas for your project before deploying. This repo does not create cloud resources until you run the commands above.
# fastapi-gcp-deployment
