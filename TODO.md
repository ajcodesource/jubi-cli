# Jubi TODO

**Finish line:** the API runs on Azure, and the CLI on my laptop talks to it.

This is the only to-do list. Work from top to bottom. Only refactor code that the current task touches.

## Next session

- [ ] **Status history** (`jubi history <job_id>`)
    - `add_job` and `update_job_status` already write to `status_history`; only the read side is missing
    - [ ] Repository: query `status_history` by `job_id`, oldest first
    - [ ] Service: turn `job_service` into a class that receives its repository (same style as `ResumeService`), then add `get_status_history`
    - [ ] API: `GET /jobs/{job_id}/history` (404 if the job doesn't exist)
    - [ ] CLI: `jubi history <job_id>`
    - [ ] Tests for each layer

## Up next

1. [ ] **Send resume upload through the API**
    - Decision: the CLI is only an HTTP client. It never calls services or writes files itself.
    - [ ] `POST /resume` stores the PDF on the server
    - [ ] CLI `upload` sends the file through `controller.py`
    - [ ] `analyze`: return a 4xx when no resume has been uploaded (right now it's an unhandled 500 that crashes the CLI)
    - [ ] `analyze`: check the response status and `notification_sent` before printing success
2. [ ] **README**
    - [ ] Overview: what Jubi does and how to run it
    - [ ] Architecture diagram (CLI → API → services → Postgres, resume storage, Gemini, Discord)
3. [ ] **API tests** (`tests/test_api.py` is empty)
4. [ ] **API authentication**
5. [ ] **Background worker** for LLM and Discord requests
    - [ ] Create a `tasks` table in Postgres
6. [ ] **Deploy to Azure**
    - [ ] Load `.env` in one place (it's loaded three different ways now: `database.py`, `notifications.py`, `llm_client.py`)
    - [ ] Create tables once at startup instead of on every query
    - [ ] Decide where uploaded resumes live on the server (disk, Postgres, or blob storage)

## Small fixes (do these when you're already in the file)

- Remove the leftover `# TODO` comments in `resume_repository.py` (that code is already written)
- The 400 response from `POST /jobs/` says "unexpected server error"
- Job status is validated in both `controller.postJob` and `job_service.add_job`
- The table schema is written twice in `DatabaseController`
