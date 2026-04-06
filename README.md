# Show Your Flow

Weekly AI showcase app for enterprise LLM users.

## Deploy 

1. Push this folder to a new GitHub repo
2. Go to share.streamlit.io → Create app
3. Set main file path: `app.py`
4. Add secret in Streamlit Cloud → Manage App → Settings → Secrets:

```toml
ADMIN_PASSWORD = "your-password-here"
```

## Files

- `app.py` — main app
- `requirements.txt` — dependencies
- `submissions.json` — auto-created when first submission is made

## Admin access

Go to the Review tab and enter the ADMIN_PASSWORD to select/pass submissions.
