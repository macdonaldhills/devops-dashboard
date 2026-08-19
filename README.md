# DevOps Dashboard

A small Flask app that started as a beginner project and turned into my first real end-to-end CI/CD pipeline. This repo is less about the app itself and more about everything wired around it: automated testing, containerization, a Jenkins pipeline, and a Kubernetes deployment that Jenkins updates automatically every time I push code.

I'm a Computer Engineering student learning DevOps and Cloud Engineering, and this project was where a lot of that learning actually clicked — mostly through breaking things and fixing them.

## What it does

The app itself is a simple dashboard exposing a health status endpoint (`/health`) that reports the application as running. It's intentionally simple — the real point of the project is the pipeline that builds, tests, ships, and deploys it automatically.

## Tech stack

- **Python / Flask** — the application
- **Pytest** — automated tests run in the pipeline before anything gets built
- **Docker** — containerizes the app
- **Docker Hub** — stores and versions the built images (`chibi7/devops-dashboard`)
- **Jenkins** — runs in its own Docker container and orchestrates the whole pipeline
- **GitHub Webhooks + ngrok** — a push to `main` triggers Jenkins automatically, even though Jenkins is running locally
- **Kubernetes** (Docker Desktop's built-in cluster) — runs the app as a 2-replica Deployment with a NodePort Service

## Project structure

```
devops-dashboard/
├── app.py
├── templates/
├── static/
├── tests/
│   └── test_app.py
├── k8s/
│   ├── deployment.yaml
│   └── service.yaml
├── Dockerfile
├── Jenkinsfile
├── requirements.txt
└── README.md
```

## Running it locally

```bash
pip install -r requirements.txt
python app.py
```

The app runs on port `5000`.

## Testing

```bash
pytest
```

Tests run automatically as the first real stage of the Jenkins pipeline — if they fail, the pipeline stops before anything gets built or deployed.

## Docker

```bash
docker build -t devops-dashboard .
docker run -p 5000:5000 devops-dashboard
```

The image is based on `python:3.12-slim` and includes a `HEALTHCHECK` that hits `/health` so Docker (and later Kubernetes) can tell if the app is actually up, not just running.

## CI/CD pipeline (Jenkins)

This is the core of the project. The Jenkinsfile defines these stages:

1. **Checkout** — pulls the latest code from GitHub
2. **Test** — runs the Pytest suite
3. **Build Docker Image** — tags it as both `:latest` and `:<build-number>`, so every image can be traced back to the exact Jenkins build that produced it
4. **Push Docker Image** — pushes both tags to Docker Hub
5. **Deploy to Kubernetes** — applies the deployment/service manifests and updates the running deployment to the new image
6. **Kubernetes Health Check** — waits for the rollout to finish and confirms the pods are actually healthy before calling the build successful

Jenkins itself runs inside a Docker container, with the Docker socket mounted so it can build and push images, and `kubectl` installed inside it so it can talk to the cluster directly.

## Triggering builds from GitHub

A GitHub webhook is configured to hit Jenkins at `/github-webhook/` on every push to `main`. Since Jenkins runs locally rather than on a public server, I used **ngrok** to expose it to the internet so GitHub can actually reach it. (Note: the ngrok URL changes every time it restarts, so the webhook URL in the repo settings has to be updated after a restart — this isn't a "set it and forget it" piece yet.)

## Kubernetes deployment

- **Deployment**: `devops-dashboard`, 2 replicas, container port `5000`
- **Liveness/readiness probes**: both hit `/health`
- **Service**: `devops-dashboard`, type `NodePort`, exposed on port `30080`

Once deployed, the app is reachable at `http://localhost:30080`, and its health can be checked at `http://localhost:30080/health`.

## What I actually learned building this

This project was where I moved past "make Docker work" into real infrastructure automation, and most of the learning came from things breaking:

- **Jenkins didn't have `kubectl` by default.** I had to install it manually inside the Jenkins container after `apt` ran into Debian repository signature issues — downloading the binary directly was the fix.
- **Jenkins couldn't talk to Kubernetes at first.** The kubeconfig pointed at `127.0.0.1`, which doesn't mean anything from inside a container. `host.docker.internal` got further but failed TLS validation. The actual fix was pointing it at `kubernetes.docker.internal`, which is what Docker Desktop's Kubernetes API actually presents a valid certificate for.
- **The webhook didn't fire at first**, which turned out to be because I was hitting the base ngrok URL instead of the specific `/github-webhook/` path Jenkins listens on.
- **Kubernetes rejected an image tag** (`InvalidImageName`) when I tried to use a `${IMAGE_TAG}` placeholder directly in a YAML file applied with `kubectl` — Kubernetes doesn't expand shell variables in a manifest. Jenkins now sets the image tag properly as part of the deploy stage instead.

## Current status

The pipeline works end-to-end: a push to `main` → GitHub webhook → Jenkins → tests → Docker build → Docker Hub push → Kubernetes deployment → health check, with no manual steps in between once the code is committed.

## Future improvements

- Move off ngrok to something more permanent so the webhook doesn't need reconfiguring after every restart
- Add more meaningful application-level tests beyond the basics
- Look into persisting Jenkins configuration outside the container so setup survives more cleanly
