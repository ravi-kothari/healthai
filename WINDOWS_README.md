# Windows Deployment Guide

This guide will help you set up and run the Healthcare Application on a Windows machine.

## Prerequisites

1.  **Docker Desktop for Windows**:
    *   Download and install from [Docker Hub](https://www.docker.com/products/docker-desktop).
    *   Ensure **WSL 2** (Windows Subsystem for Linux) backend is enabled (recommended).
2.  **PowerShell**: Pre-installed on Windows.
3.  **Git**: To clone the repository.

## Quick Start (Automated)

We have provided a PowerShell script to automate the entire process.

1.  Open **PowerShell** as Administrator (optional, but recommended for Docker interactions).
2.  Navigate to the project root directory:
    ```powershell
    cd path\to\azure-healthcare-app
    ```
3.  Run the deployment script:
    ```powershell
    .\deploy_windows.ps1
    ```
    *   *Note: If you get a security warning, you may need to allow script execution by running `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` first.*

The script will:
*   Check if Docker is running.
*   Build the application containers.
*   Start the services (Frontend, Backend, Database, Redis, FHIR Server).
*   Wait for the database to initialize.
*   Seed the database with test users and data.
*   Display the access URLs.

## Manual Setup

If you prefer to run commands manually or if the script fails:

1.  **Build and Start Containers**:
    ```powershell
    docker-compose -f backend/docker/docker-compose.yml up -d --build
    ```

2.  **Wait for Database**:
    Wait about 10-20 seconds for the database to initialize. You can check status with:
    ```powershell
    docker ps
    ```
    Ensure `healthcare-postgres` is "healthy".

3.  **Seed Data**:
    Run the seed script inside the API container:
    ```powershell
    docker exec healthcare-api python src/api/scripts/seed_test_data.py
    ```

## Accessing the Application

*   **Frontend (Patient/Provider Portal)**: [http://localhost:3000](http://localhost:3000)
*   **Backend API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
*   **FHIR Server**: [http://localhost:8081](http://localhost:8081)

## Default Credentials

*   **Provider (Doctor)**:
    *   Email: `doctor@healthai.com`
    *   Password: `password123`
*   **Tenant Admin**:
    *   Email: `admin@healthai.com`
    *   Password: `admin123`
*   **Super Admin**:
    *   Email: `superadmin@healthai.com`
    *   Password: `admin123`

## Troubleshooting

*   **Port Conflicts**: Ensure ports 3000, 8000, 8081, and 5433 are not in use.
*   **Docker Memory**: If builds fail, try increasing Docker's memory limit in Docker Desktop settings (Settings -> Resources -> Memory).
*   **Execution Policy**: If `deploy_windows.ps1` fails to run, check your PowerShell execution policy (`Get-ExecutionPolicy`).
