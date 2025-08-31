### Traffic Handling on PythonAnywhere Hacker Plan

The PythonAnywhere Hacker plan ($5/month) is designed for low-to-moderate traffic sites, such as personal projects or small applications like your Total Bankroll Flask app. It can handle a reasonable amount of usage for zero-traffic personal use or initial advertising, but limits are based on web workers, CPU allowance, bandwidth (fuzzy "low" tier), and storage. There's no strict limit on the number of requests or user accounts, but performance degrades if you exceed the plan's resources—requests queue up, leading to slowdowns or errors (e.g., 502 Bad Gateway). Below, I'll break down the key capacities based on official documentation and forum insights from PythonAnywhere staff.

#### Number of Requests and Concurrent Users
- **Web Workers**: The Hacker plan includes **2 web workers per web app** by default. Each worker is an independent process that handles one request at a time. With 2 workers, your site can process up to 2 concurrent requests simultaneously. If more requests arrive (e.g., multiple users loading pages at once), they queue until a worker is free.
  - **Concurrent Users**: This directly limits concurrent users to ~2 for optimal performance. If 3+ users access the site simultaneously, the third (and subsequent) requests wait, potentially causing delays. For example, if your app takes 0.2 seconds per request, 2 workers handle ~10 requests/second total. Multiple tabs from one user or shared access (e.g., during advertising) count as separate requests and consume workers.
  - **Daily Requests/Hits**: No hard limit, but estimates are ~10,000–100,000 hits/day for efficient code (e.g., quick Flask views with minimal processing). This assumes low CPU per request and static files served separately (configure in the Web tab to avoid tying up workers). For your bankroll app (tracking funds, assets, multi-currency conversions), if each page load involves database queries or calculations, aim for under 10,000 daily hits to stay responsive. Exceeding this leads to queuing and slowdowns during peaks.
  - **Scaling for Growth**: You can customize the plan to add more workers (e.g., 3–5 for $6–$7/month), increasing concurrency to match. Staff recommend monitoring access logs (in the Web tab) for response times and peak traffic to decide. For example, one user reported handling 60,000 hits in 5 hours on a similar plan without issues, but mostly crawlers. If advertising brings spikes, use caching (e.g., via code) or upgrade to Web Developer ($12/month, 3 workers per app, ~150,000 hits/day).

- **CPU Allowance**: Web apps don't consume from the daily CPU quota (100,000 CPU-seconds/day on Hacker), which applies only to consoles, scheduled tasks, and always-on tasks. However, if your app's requests are CPU-intensive (e.g., complex profit calculations), workers can enter the "tarpit" (throttled mode) if overall account CPU spikes, slowing everything. For low-traffic personal use, this isn't an issue.

- **Bandwidth**: "Low" fuzzy limit (not enforced strictly yet, but monitored). Sufficient for small sites (e.g., occasional users querying poker sites/assets). If you exceed "fair use" (e.g., serving large files or high-volume API calls), staff may email you to upgrade. For your app, with zero traffic now, it's fine; even 1,000 daily accesses to a 100KB CSV-like data export would be negligible.

#### Number of User Accounts
- No explicit limit on user accounts in your MySQL database. You can support as many as your storage allows (see below). For a bankroll tracker, this means unlimited users (e.g., 100–1,000+) as long as the data per user is small (e.g., funds, assets, history logs). Each user's data (e.g., poker site balances, crypto holdings) is stored in rows/tables, and concurrent logins are handled by workers as above.
- **Practical Limit**: Tied to database size and query efficiency. If each user has 1MB of data (e.g., historical trends), 1,000 users = 1GB, hitting your quota. Optimize with indexes and efficient queries to avoid slowdowns for many users.

#### MySQL Database Size Limit
- Yes, there **is a limit**: MySQL storage counts toward your overall disk quota on the Hacker plan, which is **1GB total** (files + databases). It's a soft limit—PythonAnywhere monitors periodically and emails if you approach/exceed it, giving time to clean up or upgrade. They don't auto-delete but may restrict access if ignored.
  - **Free Plan Comparison**: 512MB total (as you may have used initially).
  - **No Hard Per-DB Limit**: You can have multiple databases, but total size (data + indexes) is capped. Use this SQL query in a MySQL console to check current size:
    ```
    SELECT table_schema "Database Name", SUM(data_length + index_length) / (1024 * 1024) "Database Size in MB"
    FROM information_schema.TABLES GROUP BY table_schema;
    ```
  - **For Your App**: With features like historical data/trends and multi-currency support, start small (e.g., <100MB for personal use). As users grow via advertising, monitor via the dashboard. If you hit 1GB, upgrade storage (e.g., +1GB for ~$1–$2/month via custom plan) or optimize (e.g., archive old data).
  - **Other DB Notes**: Unlimited consoles/connections for paid plans, but shared servers mean high-load queries (e.g., for many users) may slow down. No row/table limits, but design for concurrency (e.g., use transactions for updates like withdrawals to prevent errors).

#### Recommendations for Your Setup
- **For Zero Traffic/Personal Use**: Hacker plan handles it easily—2 workers for occasional access, 1GB for your DB (plenty for one user's bankroll tracking).
- **For Advertising/Growth**: Expect 10,000+ daily hits or 10+ concurrent users to require more workers (customize via Account > Upgrade > Customize). Test with tools like Apache Bench (locally) or monitor logs. If DB grows beyond 1GB, upgrade storage.
- **Tips to Maximize Capacity**:
  - Serve static files (e.g., Bootstrap CSS) separately to free workers.
  - Optimize Flask code: Use efficient MySQL queries (indexes, pooling with SQLAlchemy recycle=280 to avoid timeouts).
  - For high concurrency, consider async (future feature) or offload heavy tasks (e.g., profit calcs) to scheduled tasks.
  - If limits bind, upgrade to Web Developer ($12/month) for 3 workers/app and more CPU/hits.

If traffic spikes unexpectedly, contact support—they're responsive and can adjust temporarily. For your app's financial safeguards (e.g., preventing over-withdrawals), the limits won't affect core logic but ensure DB queries are fast to avoid queuing.
