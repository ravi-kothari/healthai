# Local Development Without Docker - Healthcare AI Platform

This guide provides step-by-step instructions for setting up the development environment for the Healthcare AI Platform on Windows without using Docker. This approach is intended for developers who prefer or are required to run services natively.

## Quick Start Checklist

For developers who are already familiar with the tools and need a quick reminder:

1.  [ ] **Install Prerequisites:** Git, Python 3.11+, Node.js LTS, JDK 17, and Chocolatey.
2.  [ ] **Install Services:** Use Chocolatey to install PostgreSQL 15.
3.  [ ] **Install WSL2 & Redis:** Install WSL2 and then install `redis-server` within the WSL distribution.
4.  [ ] **Setup PostgreSQL:** Create the application database and user.
5.  [ ] **Setup HAPI FHIR:** Download the HAPI FHIR CLI JAR and run it.
6.  [ ] **Setup Backend:**
    *   Clone the repository.
    *   Create and activate a Python virtual environment.
    *   Install Python dependencies (`pip install -r requirements.txt`).
    *   Configure the `.env` file.
    *   Run database migrations (`alembic upgrade head`).
7.  [ ] **Setup Frontend:**
    *   Navigate to the `frontend` directory.
    *   Install Node dependencies (`npm install`).
    *   Configure the `.env.local` file.
8.  [ ] **Run All Services:** Start Redis (in WSL), HAPI FHIR, Backend, and Frontend in separate terminals.

## Prerequisites

Before you begin, ensure you have the following installed on your Windows 10/11 machine. We strongly recommend using [Chocolatey](https://chocolatey.org/), a package manager for Windows, to simplify the installation process.

1.  **Chocolatey:** If you don't have it, open PowerShell as **Administrator** and run:
    ```powershell
    Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
    ```
2.  **Core Tools:** Once Chocolatey is installed, open a new **Administrator** PowerShell terminal and install the required tools:
    ```powershell
    choco install -y git python --version=3.11.5 nodejs-lts openjdk --version=17
    ```
    *   This command installs Git, Python 3.11, the latest Node.js LTS, and OpenJDK 17.

3.  **Verification:** Close and reopen your terminal (as a regular user) and verify the installations:
    ```powershell
    git --version
    python --version
    node --version
    npm --version
    java --version
    ```

## Part 1: Windows Subsystem for Linux (WSL2) Setup

Redis is not officially supported on Windows. The recommended approach is to run it within WSL2, which provides a lightweight Linux environment on Windows.

1.  **Install WSL2:** Open PowerShell as **Administrator** and run:
    ```powershell
    wsl --install
    ```
    This will install the default Ubuntu distribution. You may need to restart your computer.

2.  **Launch WSL:** Open your Start Menu and search for "Ubuntu". Launch it to complete the setup, which will include creating a username and password for your Linux environment.

## Part 2: Database Setup (PostgreSQL)

1.  **Install PostgreSQL:** Open an **Administrator** PowerShell terminal.
    ```powershell
    choco install postgresql15 --params "/Password:YourSecurePassword"
    ```
    > **Note:** Replace `YourSecurePassword` with a strong password for the default `postgres` superuser. Remember this password.

2.  **Add PostgreSQL to Path:** You need to add the PostgreSQL `bin` directory to your system's PATH to use its command-line tools easily.
    *   Find the installation path, typically `C:\Program Files\PostgreSQL\15\bin`.
    *   Search for "Edit the system environment variables" in the Start Menu, click "Environment Variables...", select "Path" under "System variables", click "Edit...", and add the path.

3.  **Create the Application Database:**
    *   Open a new terminal (PowerShell or Git Bash).
    *   Log in to PostgreSQL as the superuser:
        ```bash
        psql -U postgres
        ```
    *   You will be prompted for the password you set during installation.
    *   Run the following SQL commands to create a database and a dedicated user for the application. Replace `myuser` and `mypassword` with secure credentials.

        ```sql
        CREATE DATABASE health_ai_db;
        CREATE USER health_ai_user WITH PASSWORD 'a_secure_password';
        GRANT ALL PRIVILEGES ON DATABASE health_ai_db TO health_ai_user;
        ALTER ROLE health_ai_user SET client_encoding TO 'utf8';
        ALTER ROLE health_ai_user SET default_transaction_isolation TO 'read committed';
        ALTER ROLE health_ai_user SET timezone TO 'UTC';
        \q
        ```

4.  **Verification:** Test the connection with the new user.
    ```bash
    psql -U health_ai_user -d health_ai_db -h localhost
    ```
    Enter the password you just created. If you see the `health_ai_db=>` prompt, it's working. Type `\q` to exit.

## Part 3: Cache Setup (Redis)

1.  **Launch WSL:** Open your Ubuntu terminal.

2.  **Install Redis:**
    ```bash
    sudo apt update
    sudo apt install redis-server
    ```

3.  **Start Redis Service:**
    ```bash
    sudo service redis-server start
    ```

4.  **Verification:** Check if Redis is running.
    ```bash
    redis-cli ping
    ```
    If it returns `PONG`, Redis is running correctly.

    > **Note:** By default, Redis in WSL is accessible from Windows at `localhost:6379`.

## Part 4: FHIR Server Setup (HAPI FHIR)

The HAPI FHIR server is a Java application that simulates a FHIR-compliant electronic health record (EHR) system.

1.  **Download HAPI FHIR:** Download the latest HAPI FHIR CLI `jar` file from the [HAPI FHIR GitHub Releases](https://github.com/hapifhir/hapi-fhir/releases). Look for a file named `hapi-fhir-cli-X.X.X-executable.jar`.

2.  **Create a Directory:** Create a folder for the server, e.g., `C:\dev\hapi-fhir`, and place the downloaded `.jar` file inside it.

3.  **Run the Server:** Open a terminal, navigate to the directory, and run the following command:
    ```powershell
    # Make sure you are in the directory where you saved the .jar file
    cd C:\dev\hapi-fhir

    # Rename the file for simplicity if you wish
    # ren .\hapi-fhir-cli-*.jar hapi-fhir-cli.jar

    java -jar .\hapi-fhir-cli.jar run-server
    ```

4.  **Verification:** The server will start up. Once you see log messages indicating it's running, open a web browser and navigate to `http://localhost:8080`. You should see the HAPI FHIR web interface.

## Part 5: Backend Setup (FastAPI)

1.  **Clone the Repository:**
    ```bash
    git clone <your-project-repo-url>
    cd <your-project-repo-name>/backend
    ```

2.  **Create and Activate Virtual Environment:**
    ```powershell
    # Create the virtual environment
    python -m venv .venv

    # Activate it (PowerShell)
    .\.venv\Scripts\Activate.ps1

    # For Git Bash / CMD
    # .\.venv\Scripts\activate
    ```
    Your terminal prompt should now be prefixed with `(.venv)`.

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables:**
    *   Create a `.env` file by copying the example: `copy .env.example .env`.
    *   Open the `.env` file and fill in the values, especially for the database and Redis.

    ```ini
    # .env
    DATABASE_URL="postgresql://health_ai_user:a_secure_password@localhost:5432/health_ai_db"
    REDIS_URL="redis://localhost:6379/0"
    FHIR_SERVER_URL="http://localhost:8080/fhir"
    # ... other variables
    ```

5.  **Run Database Migrations:**
    ```bash
    alembic upgrade head
    ```
    This will create the necessary tables in your `health_ai_db` database.

6.  **Run the Backend Server:**
    ```bash
    uvicorn app.main:app --reload --port 8000
    ```

7.  **Verification:** Open your browser to `http://localhost:8000/docs`. You should see the FastAPI Swagger UI.

## Part 6: Frontend Setup (Next.js)

1.  **Navigate to Frontend Directory:** In a **new terminal**, navigate to the frontend folder.
    ```powershell
    cd ../frontend
    ```

2.  **Install Dependencies:**
    ```bash
    npm install
    ```

3.  **Configure Environment Variables:**
    *   Create a `.env.local` file by copying the example: `copy .env.example .env.local`.
    *   Open `.env.local` and ensure the API URL points to your local backend.

    ```ini
    # .env.local
    NEXT_PUBLIC_API_URL=http://localhost:8000
    ```

4.  **Run the Frontend Server:**
    ```bash
    npm run dev
    ```

5.  **Verification:** Open your browser to `http://localhost:3000`. You should see the application's home page.

## Part 7: Running All Services

To run the full application, you will need four separate terminal windows.

```
+---------------------------+---------------------------+
| Terminal 1 (WSL/Ubuntu)   | Terminal 2 (PowerShell)   |
|---------------------------|---------------------------|
| > sudo service redis-..   | > cd C:\dev\hapi-fhir     |
| > redis-cli ping          | > java -jar hapi-fhir..   |
|                           |                           |
+---------------------------+---------------------------+
| Terminal 3 (PowerShell)   | Terminal 4 (PowerShell)   |
|---------------------------|---------------------------|
| > cd .../backend          | > cd .../frontend         |
| > .\.venv\Scripts\Act..   | > npm run dev             |
| > uvicorn app.main:app..  |                           |
+---------------------------+---------------------------+
```

1.  **Terminal 1 (WSL):** Start Redis.
2.  **Terminal 2:** Start the HAPI FHIR server.
3.  **Terminal 3:** Start the FastAPI backend.
4.  **Terminal 4:** Start the Next.js frontend.

## Part 8: Verification & Testing

*   **Full Stack Check:** Open `http://localhost:3000` in your browser. Log in or perform a core action. Check the network tab in your browser's developer tools to ensure requests to `http://localhost:8000` are succeeding.
*   **Backend Tests:** In the backend terminal (Terminal 3), stop the server (`Ctrl+C`) and run the test suite:
    ```bash
    pytest
    ```
*   **Frontend Tests:** In the frontend terminal (Terminal 4), stop the server (`Ctrl+C`) and run the test suite:
    ```bash
    npm test
    ```

## Part 9: Daily Development Workflow

### To Start Your Day:

1.  **Start PostgreSQL:** PostgreSQL usually runs as a Windows service and starts automatically. If not, open "Services" from the Start Menu, find `postgresql-x64-15`, and start it.
2.  **Start Redis:** Open an Ubuntu (WSL) terminal and run `sudo service redis-server start`.
3.  **Start HAPI FHIR:** Open a terminal, `cd` to your HAPI FHIR directory, and run `java -jar .\hapi-fhir-cli.jar run-server`.
4.  **Start Backend:** Open a terminal, `cd` to the `backend` directory, activate venv, and run `uvicorn app.main:app --reload --port 8000`.
5.  **Start Frontend:** Open a terminal, `cd` to the `frontend` directory, and run `npm run dev`.

### To End Your Day:

1.  Press `Ctrl+C` in the frontend, backend, and HAPI FHIR terminals.
2.  Stop Redis (optional, it uses few resources): In the WSL terminal, run `sudo service redis-server stop`.
3.  Stop PostgreSQL (optional): In the "Services" app, stop the `postgresql-x64-15` service.

## Part 10: Troubleshooting

*   **Port XXXX is already in use:**
    *   Find the process using the port. In PowerShell: `Get-Process -Id (Get-NetTCPConnection -LocalPort XXXX).OwningProcess`
    *   Kill the process: `Stop-Process -Id <PID>` or use Task Manager.
*   **PostgreSQL Connection Errors:**
    *   Verify the PostgreSQL service is running in Windows Services.
    *   Double-check the `DATABASE_URL` in your backend `.env` file. Ensure the username, password, and database name are correct.
    *   Check your firewall settings to ensure connections to port 5432 are not blocked.
*   **Redis Connection Errors:**
    *   Ensure WSL is running.
    *   Run `sudo service redis-server status` in WSL to see if it's active.
    *   Check that `REDIS_URL` in the `.env` file is `redis://localhost:6379/0`.
*   **Python `pip install` fails:**
    *   Some packages may have system dependencies. If a package fails to build, the error log often indicates what's missing (e.g., C++ build tools). You may need to install "Microsoft C++ Build Tools" via the Visual Studio Installer.
*   **`alembic` command not found:**
    *   Your Python virtual environment is likely not activated. Run `.\.venv\Scripts\Activate.ps1`.

## Appendix: Port Reference

| Service               | Default Port | Configuration File | Notes                               |
| --------------------- | ------------ | ------------------ | ----------------------------------- |
| Frontend (Next.js)    | `3000`       | `package.json`     | Can be run on another port via `npm run dev -- -p 3001` |
| Backend (FastAPI)     | `8000`       | CLI argument       | `uvicorn ... --port 8000`           |
| PostgreSQL            | `5432`       | `postgresql.conf`  | Standard port for PostgreSQL.       |
| Redis                 | `6379`       | `redis.conf`       | Standard port for Redis.            |
| HAPI FHIR Server      | `8080`       | CLI argument       | Default for the `run-server` command. |

---

**Last Updated:** November 27, 2024
**Version:** 1.0.0
**Maintainer:** Development Team

**Note:** This guide was created with assistance from AI to provide a comprehensive alternative to Docker-based development. For the Docker-based approach, please refer to `DEVELOPER_ONBOARDING_WINDOWS.md`.
