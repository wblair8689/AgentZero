# Deployment Strategy: AgentZero

This document outlines the deployment choices and configuration for the AgentZero project.

## Deployment Target

- **Platform:** Google Cloud Run
- **Reasoning:** Chosen for its balance of fast iteration speed (especially with source-based deployments), managed infrastructure, scalability (including scaling to zero), and strong integration with other Google Cloud services like Vertex AI, Cloud Build, and Artifact Registry.

## Google Cloud Configuration

- **Project ID:** `agentzero-457213`
- **Project Name:** `AgentZero`
- **Organization:** `whbiv.com`
- **Owner Account:** `bill@whbiv.com`
- **Region:** `us-central1` (Primary region for deployment)

## Source Code Repository

- **Provider:** GitHub
- **Connection:** Connected to Google Cloud Build via the GCP Console.

## Artifact Storage

- **Service:** Google Artifact Registry
- **Repository Name:** `agentzero-repo`
- **Location:** `us-central1`
- **Format:** Docker
- **Reasoning:** Tightly integrated with Cloud Build and Cloud Run, provides security features (vulnerability scanning, IAM permissions), and supports various artifact formats. Artifact Registry will store the container images built by Cloud Build.

## CI/CD

- **Service:** Google Cloud Build
- **GCP Setup:**
    - APIs Enabled: Cloud Build, Cloud Run, Artifact Registry, IAM.
    - Artifact Registry Repository (`agentzero-repo`) created in `us-central1`.
    - Cloud Build Service Account (`[PROJECT_NUMBER]@cloudbuild.gserviceaccount.com`) granted roles:
        - `roles/artifactregistry.writer` (Push to Artifact Registry)
        - `roles/run.admin` (Deploy to Cloud Run)
        - `roles/iam.serviceAccountUser` (Act as Compute Engine default service account for deployment)
- **Configuration File:** `cloudbuild.yaml` (located at the repository root).
- **Trigger:** Configured via GCP Console.
    - **Event:** Triggered by pushes to the `main` branch (or as configured).
    - **Source:** Linked GitHub repository.
    - **Substitutions (Set in Trigger):**
        - `_SERVICE_NAME`: e.g., `agentzero-orchestrator` (Specific name depends on the agent being deployed)
        - `_REGION`: `us-central1`
- **Workflow:** Fetch code -> Install dependencies (`npm install`) -> Run tests (`npm test`) -> Build & Deploy to Cloud Run (`gcloud run deploy --source .` using configured substitutions) -> Store image in Artifact Registry (`agentzero-repo`). 