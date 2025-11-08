# total_bankroll

Keeps a track of total poker bankroll, including funds on each site, cash and other assets.

## Caching

The application uses Flask-Caching for improved performance:
- **Backend:** SimpleCache (in-memory) for development and PythonAnywhere hosting
- **Default TTL:** 5 minutes (configurable)
- **Future Scaling:** Redis support ready for when traffic increases
- **Configuration:** Set via `CACHE_TYPE` in `.env` file

To upgrade to Redis (when needed):
1. Sign up for Upstash Redis free tier
2. Update `.env`: `CACHE_TYPE=RedisCache` and set `REDIS_URL`
3. Reload application - no code changes needed!

## Monitoring

The application uses UptimeRobot for uptime monitoring:
- **Main Site:** https://stakeeasy.net
- **Check Interval:** 5 minutes
- **Alerts:** Email notifications on downtime or performance issues
- **Dashboard:** https://uptimerobot.com (login required)
