# Trainer aptitude sync

Set `APTITUDE_SYNC_SECRET` to the same long, random value on the dashboard server and the bot service. The dashboard also needs `BOT_API_BASE` pointing to the bot API and `FRONTEND_URL` matching the web frontend origin. Restart both services after configuration. The bot rejects updates if the shared secret is missing, the request signature is invalid, or the account is not a Trainer.
