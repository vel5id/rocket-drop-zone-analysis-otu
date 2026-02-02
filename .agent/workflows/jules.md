---
description: Workflow for using the Google Jules CLI tool for critical debugging and tasks.
---

# 🕶️ JULES: GOOGLE JULES CLI WORKFLOW

This workflow utilizes the `jules` CLI tool for advanced AI-driven debugging and task execution.
See: https://jules.google/docs/cli/reference/

## 1. SETUP & AUTHENTICATION
Before using Jules, ensure it is installed and authenticated.

### Installation
```bash
npm install -g @google/jules
```
// If not installed, run this manually or via `npm`.

### Authentication
**REQUIRED**: You must authenticate manually once.
```bash
jules login
```
Follow the browser prompts to log in with your Google account.

## 2. USAGE COMMANDS
Use the `jules` command to interact with the agent.

### Start a Session
To start a new session for a specific task:
```bash
jules remote new --session "Your task description here"
```
Example: `jules remote new --session "Fix the memory leak in data_processing.py"`

### List Sessions
To see active or past sessions:
```bash
jules remote list --session
```

### Pull Results
To applying changes from a session:
```bash
jules remote pull --session <session_id>
```

## 3. COMPLIANCE CHECK
Ensure you are logged in before running critical tasks.
Use `jules --version` to verify installation.

## 4. CRITICAL SITUATION PROTOCOL
When invoked via `/jules`, follow these steps:
1.  **Run**: `jules remote new --session "<CRITICAL_ISSUE_DESCRIPTION>"`
2.  **Monitor**: `jules remote list` to check status.
3.  **Apply**: `jules remote pull --session <ID>` once complete.

---
// End of Workflow
