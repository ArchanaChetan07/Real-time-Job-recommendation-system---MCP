# Push to GitHub

Push this project to: **https://github.com/ArchanaChetan07/Real-time-Job-recommendation-system---MCP**

## Option 1: Run the script (PowerShell)

From the **project root** (folder that contains `app.py`):

```powershell
.\push-to-github.ps1
```

If you get an execution policy error, run first:
```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

## Option 2: Run Git commands manually

Open a terminal in the project root (folder with `app.py`, `src/`, `README.md`).

**If this folder is not yet a Git repo:**

```bash
git init
git branch -M main
git remote add origin https://github.com/ArchanaChetan07/Real-time-Job-recommendation-system---MCP.git
git add -A
git commit -m "Add AI Job Recommender: Streamlit app, MCP server, tests, Docker"
git push -u origin main
```

**If it is already a Git repo:**

```bash
git remote set-url origin https://github.com/ArchanaChetan07/Real-time-Job-recommendation-system---MCP.git
git add -A
git status
git commit -m "Add AI Job Recommender: Streamlit app, MCP server, tests, Docker"
git push -u origin main
```

## Authentication

- **HTTPS:** When you `git push`, Git will ask for your GitHub username and a **Personal Access Token** (not your password). Create one: GitHub → Settings → Developer settings → Personal access tokens.
- **SSH:** If you use SSH keys, set the remote to:  
  `git@github.com:ArchanaChetan07/Real-time-Job-recommendation-system---MCP.git`  
  then run `git push -u origin main`.

## Note

Ensure **Git is installed** and available in your PATH. On Windows you can install it from https://git-scm.com/download/win and restart the terminal.
