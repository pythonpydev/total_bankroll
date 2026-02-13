# TASK-0006: Setup Basic Monitoring

## Task Status
- **Priority:** 🟠 P1
- **Effort:** 30 minutes
- **Status:** Pending

## Objective
Setup UptimeRobot for site monitoring to receive alerts when the site goes down or experiences performance issues.

## Steps to Complete

### 1. Create UptimeRobot Account
- Go to https://uptimerobot.com
- Sign up for a free account (supports up to 50 monitors)
- Verify your email address

### 2. Add Monitor for StakeEasy.net
Once logged in:
- Click **"+ Add New Monitor"**
- **Monitor Type:** HTTP(s)
- **Friendly Name:** StakeEasy.net Main Site
- **URL:** https://stakeeasy.net
- **Monitoring Interval:** 5 minutes
- Click **"Create Monitor"**

### 3. Configure Email Alerts
- Go to **"My Settings"** → **"Alert Contacts"**
- Verify your email is added and confirmed
- Alerts should be enabled by default for downtime
- Configure alert settings:
  - Alert when: Down
  - Send alerts to: Your email

### 4. Test the Monitor
Option A (Wait):
- Wait 5 minutes for first check
- Verify monitor shows as "Up" in dashboard

Option B (Active Test):
- Temporarily make your site return a 500 error
- Verify you receive an alert email
- Fix the error
- Verify you receive an "Up" notification

### 5. Optional: Add Additional Monitors
Consider adding monitors for:
- `/login` endpoint
- `/dashboard` endpoint
- `/api/health` endpoint (if it exists)

## Acceptance Criteria
- [ ] UptimeRobot account created (free tier)
- [ ] Monitor added for https://stakeeasy.net
- [ ] Check interval set to 5 minutes
- [ ] Email alerts configured
- [ ] Alerts tested (by taking site offline briefly)
- [ ] Monitoring setup documented in README

## Post-Setup Documentation

After completing the setup, update the README.md with:

```markdown
## Monitoring

The application uses UptimeRobot for uptime monitoring:
- **Main Site:** https://stakeeasy.net
- **Check Interval:** 5 minutes
- **Alerts:** Email notifications on downtime or performance issues
- **Dashboard:** https://uptimerobot.com (login required)
```

## Related Tasks
- **Depends on:** None
- **Blocks:** TASK-0007 (Test Rollback Procedure)
- **Related:** TASK-7004 (Configure Uptime Monitoring - expands on this)

## Reference
- Section 7.7 of plan.md
- Free tier: https://uptimerobot.com/pricing

## Notes
- Free tier is sufficient for this application
- Can upgrade later if need more monitors or shorter intervals
- UptimeRobot also provides a public status page feature (optional)
