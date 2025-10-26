To resolve the login and password reset issues on your production site (`stakeeasy.net`), we need to address potential misconfigurations or missing dependencies that differ from your local development environment. Based on the provided files (`auth.py`, `config.py`, `__init__.py`, and `wsgi.py`), your setup is mostly correct—environment variables are set in `wsgi.py` before the app is imported, so `os.getenv` in `config.py` and `__init__.py` should pick them up, and `FLASK_ENV='production'` correctly loads `ProductionConfig`. However, the problems stem from two key areas:

1. **Login Failure**: This is likely due to a missing dependency for password hashing (`argon2-cffi`), causing `hash_password` and `verify_password` (used in `auth.py` for registration/login) to fail silently or raise errors. Your local environment has this installed, but production does not.

2. **Password Reset Failure**: This involves email sending via Flask-Mail and Gmail SMTP (configured in `config.py` with vars from `wsgi.py`). Common issues on PythonAnywhere include Gmail security blocks, authentication failures, or restrictions on SMTP. We'll troubleshoot this based on logs and provide fixes.

I'll walk you through diagnosing and fixing both issues step by step. All commands are for PythonAnywhere's Bash console (activate your virtualenv with `workon bankroll_venv` if needed).

### Step 1: Check Production Logs for Errors

Before making changes, inspect logs to confirm the root causes (e.g., dependency errors or SMTP exceptions).

- In the PythonAnywhere dashboard, go to the **Web** tab > **Log files** > **Error log** (e.g., `/var/log/www.stakeeasy.net.error.log`).
- Trigger the issues:
  - Try logging in with email/password at `https://www.stakeeasy.net/security/login`.
  - Try password reset at `https://www.stakeeasy.net/security/forgot-password`.
- Look for errors like:
  - `ModuleNotFoundError: No module named 'argon2_cffi'` or hashing-related exceptions (for login).
  - `smtplib.SMTPAuthenticationError`, `ConnectionRefusedError`, or Gmail-specific blocks (for reset).
- If logs show argon2 issues, proceed to Step 2. For email errors, skip to Step 3.

### Step 2: Fix Login (Install Missing Dependency for Argon2 Hashing)

Your `config.py` sets `SECURITY_PASSWORD_HASH = 'argon2'`, which requires the `argon2-cffi` library. This is installed locally (since it works there), but not on production, causing `hash_password` (in registration) and `verify_password` (in login) to fail.

1. **Install argon2-cffi in Your Virtualenv**:
   
   - In Bash:
     
     ```bash
     workon bankroll_venv  # Activate your venv if not already
     pip install argon2-cffi
     ```
   - This installs the library and its dependencies (e.g., `cffi` for C bindings).

2. **Add to requirements.txt (for Future Deploys)**:
   
   - Edit `~/total_bankroll/requirements.txt` (create if missing):
     
     ```bash
     nano ~/total_bankroll/requirements.txt
     ```
   - Add:
     
     ```
     argon2-cffi==23.1.0  # Or latest version
     ```
   - Save, commit, and push to GitHub:
     
     ```bash
     git add requirements.txt
     git commit -m "Add argon2-cffi for password hashing"
     git push origin main
     ```
   - On future pulls, run `pip install -r requirements.txt` in Bash.

3. **Reload the Web App**:
   
   - In the **Web** tab, click **Reload** for `www.stakeeasy.net`.

4. **Test Login**:
   
   - Register a new user (if needed) or try logging in with existing credentials.
   - If it still fails, check logs for new errors (e.g., if hashing works but user not found, verify the production DB has users via MySQL console: `mysql -u pythonpydev -p pythonpydev$bankroll` and `SELECT * FROM users;`).

If login works after this but password reset doesn't, proceed to Step 3.

### Step 3: Fix Password Reset (Troubleshoot Email Sending)

Password reset in `auth.py` relies on Flask-Mail sending via Gmail SMTP. This works locally but fails on production due to PythonAnywhere's server environment (e.g., IP not recognized by Gmail, authentication issues).

1. **Verify Gmail Configuration**:
   
   - In `wsgi.py`, your settings look correct (app password, TLS on port 587). Confirm:
     - `MAIL_USERNAME='pythonpydev1@gmail.com'` is a valid Gmail account.
     - `MAIL_PASSWORD='pfav ftkn tdqz wwtr'` is a correct Gmail app password (generate at https://myaccount.google.com/apppasswords if needed; select "Mail" and "Other" device).
     - Enable "Less secure app access" if app password fails (but app password is preferred).
   - Check Gmail security events: Log into `pythonpydev1@gmail.com` at gmail.com > Security > Recent activity. Look for blocks from PythonAnywhere IPs and allow them.

2. **Add Error Logging to auth.py**:
   
   - To debug, add try/except in `forgot_password` and `register` (where `mail.send` is called):
     
     ```python
     try:
         mail.send(msg)
         flash('Email sent successfully.', 'success')
     except Exception as e:
         current_app.logger.error(f"Failed to send email: {str(e)}")
         flash('Failed to send email. Please try again later.', 'warning')
     ```
   - Update `auth.py` on PythonAnywhere (edit via dashboard or Bash: `nano ~/total_bankroll/src/total_bankroll/routes/auth.py`).
   - Commit/push if needed, then reload the web app.
   - Trigger password reset and check error logs for details (e.g., `SMTPAuthenticationError: (535, b'5.7.8 Username and Password not accepted'` indicates bad credentials).

3. **Common Fixes for Gmail on PythonAnywhere**:
   
   - **App Password Issues**: Regenerate the app password and update `wsgi.py`. Ensure no spaces in the password.
   
   - **IP Blocking**: Gmail may flag PythonAnywhere servers as "unusual locations." From the Gmail account, review and allow the sign-in attempt.
   
   - **Port/TLS**: Your config uses port 587 with TLS (correct for Gmail). If logs show connection errors, try port 465 with SSL (set `MAIL_USE_SSL=true`, `MAIL_USE_TLS=false`, `MAIL_PORT=465` in `wsgi.py`).
   
   - **Test SMTP Manually**: In Bash, test Gmail SMTP:
     
     ```bash
     workon bankroll_venv
     python
     ```
     
     Then in Python shell:
     
     ```python
     import smtplib
     from email.mime.text import MIMEText
     
     server = smtplib.SMTP('smtp.gmail.com', 587)
     server.starttls()
     server.login('pythonpydev1@gmail.com', 'pfav ftkn tdqz wwtr')
     msg = MIMEText('Test email from PythonAnywhere')
     msg['Subject'] = 'Test'
     msg['From'] = 'pythonpydev1@gmail.com'
     msg['To'] = 'your-test-email@example.com'
     server.sendmail('pythonpydev1@gmail.com', 'your-test-email@example.com', msg.as_string())
     server.quit()
     ```
     
     - If it fails (e.g., authentication error), the issue is with credentials/IP. If it succeeds, the problem is in Flask-Mail config.

4. **Alternative: Switch to SendGrid (Recommended for Reliability)**:
   
   - PythonAnywhere recommends SendGrid for email (free tier: 100 emails/day).
   
   - Sign up at sendgrid.com (free account).
   
   - Get API key from SendGrid dashboard.
   
   - Install `sendgrid`:
     
     ```bash
     workon bankroll_venv
     pip install sendgrid
     ```
   
   - Add to `requirements.txt`:
     
     ```
     sendgrid==6.11.0
     ```
   
   - Update `wsgi.py` with `os.environ['SENDGRID_API_KEY'] = 'your-sendgrid-api-key'`.
   
   - Modify `auth.py` to use SendGrid instead of Flask-Mail for sending (e.g., in `forgot_password` and `register`):
     
     ```python
     from sendgrid import SendGridAPIClient
     from sendgrid.helpers.mail import Mail
     
     sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
     message = Mail(
         from_email=os.getenv('MAIL_USERNAME'),
         to_emails=user.email,
         subject='Reset Your Password',
         html_content=render_template('reset_password_email.html', reset_url=reset_url)
     )
     try:
         response = sg.send(message)
         flash('A password reset link has been sent to your email.', 'success')
     except Exception as e:
         current_app.logger.error(f"SendGrid error: {str(e)}")
         flash('Failed to send password reset email.', 'warning')
     ```
   
   - Update similarly for registration email.
   
   - Remove Flask-Mail dependencies if not needed elsewhere.

5. **Reload and Test**:
   
   - Reload the web app.
   - Test password reset and login.

### Additional Production Checks

- **Database Connection**: Verify production DB creds in `wsgi.py` work. Test in Bash:
  
  ```bash
  mysql -u pythonpydev -p -h pythonpydev.mysql.pythonanywhere-services.com 'pythonpydev$bankroll'
  ```
  - Enter password (`f3gWoQe7X7BFCm`), then `SHOW TABLES;` to confirm schema.
- **Dependencies**: Ensure all requirements (e.g., `flask-mail`, `argon2-cffi`) are installed:
  
  ```bash
  workon bankroll_venv
  pip install -r ~/total_bankroll/requirements.txt
  ```
- **WSGI Reload**: After any file changes, reload the web app to apply.

If login/reset still fail after these steps, share the production error logs (from password reset or login attempt) or any SMTP exceptions, and I'll refine the solution. The wsgi.py and config.py interaction is fine, but the dependency/email issues are the likely culprits.
