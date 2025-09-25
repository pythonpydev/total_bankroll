### Steps to Purchase a Domain Like StakeEasy.net and Link It to a PythonAnywhere Website

Purchasing a domain name and pointing it to a hosting service like PythonAnywhere is a straightforward process, but it involves two main phases: acquiring the domain from a registrar and configuring DNS settings to link it to your site. Note that PythonAnywhere's free accounts (like the one implied by your example URL, https://pythonpydev.pythonanywhere.com/) **do not support custom domains**. You must upgrade to a paid plan (starting at $5/month for the Hacker plan) to use a custom domain for hosting a website. Free accounts are limited to subdomains like `yourusername.pythonanywhere.com` or custom subdomains of PythonAnywhere's domain. The new name of the site is StakeEasy.net.

Assuming you have (or will upgrade to) a paid PythonAnywhere account and your Flask app (like StakeEasy.net) is already set up and running on the free subdomain, here are the detailed steps. The process typically takes 1-2 hours to set up, plus up to 24 hours for DNS changes to propagate across the internet.

#### Phase 1: Purchasing the Domain (e.g., StakeEasy.net)
Domain names are registered through ICANN-accredited registrars. Popular, reliable options include GoDaddy, Namecheap, Google Domains, or Hostinger. Costs for a .net domain like StakeEasy.net are usually $10-15 for the first year (renewals may be $15-20/year), but check availability as prices can vary if it's premium or already taken.

1. **Choose and Search for the Domain**:
   - Go to a registrar's website (e.g., https://www.godaddy.com/domains or https://www.namecheap.com/domains).
   - Use their domain search tool: Enter "StakeEasy.net".
   - Check availability. If available, it will show the price. If not, the tool suggests alternatives (e.g., pokerprofits.com or poker-profits.io).
   - Evaluate value: Use free tools like EstiBot (https://www.estibot.com/) or GoDaddy's appraisal tool to estimate worth based on length, keywords, and SEO potential. For a poker-related domain, it could be valuable due to niche relevance, but avoid trademark issues (e.g., don't mimic existing brands).

2. **Select Registration Options**:
   - Choose the top-level domain (TLD): .net is a good choice for a web application.
   - Add privacy protection (WHOIS privacy): This hides your personal info from public databases to prevent spam (~$5-10/year, often free with Namecheap).
   - Opt for auto-renewal to avoid losing the domain.
   - Decide on add-ons: Skip extras like hosting or email unless needed (PythonAnywhere handles hosting).

3. **Create an Account and Complete Purchase**:
   - Sign up or log in to the registrar.
   - Add the domain to your cart and enter payment details (credit card, PayPal, etc.).
   - Provide registrant info: Your name, address, email, and phone (required by ICANN; privacy protection masks this publicly).
   - Agree to terms and complete the purchase. You'll receive a confirmation email with login details for managing the domain.
   - Verification: Some registrars (e.g., GoDaddy) may require email/phone verification.

4. **Post-Purchase Setup**:
   - Log in to your registrar dashboard to manage DNS records (you'll need this for Phase 2).
   - The domain is now yours for 1-10 years (renew as needed).

**Tips**:
- Compare registrars for deals (e.g., Namecheap often has promo codes for $8-10 .com registrations).
- If StakeEasy.net is taken, search auctions on GoDaddy Auctions or Sedo for expired/premium domains.
- Total cost: ~$10-20 initially, plus PythonAnywhere's $5/month upgrade.

#### Phase 2: Linking the Domain to Your PythonAnywhere Website
Once purchased, configure your PythonAnywhere web app to use the custom domain and update DNS to point traffic to PythonAnywhere's servers. This uses a CNAME record (recommended for reliability). Your app (e.g., the StakeEasy.net Flask site) must be configured for the new domain in your code (e.g., update ALLOWED_HOSTS in settings.py for Django/Flask).

1. **Upgrade Your PythonAnywhere Account (If Needed)**:
   - Log in to PythonAnywhere (https://www.pythonanywhere.com).
   - Go to the "Account" tab > "Plans" and upgrade to at least the Hacker plan ($5/month). This enables custom domains (up to 2 web apps on Hacker; more on higher plans).
   - Confirm the upgrade; it takes effect immediately. Your existing free subdomain (e.g., pythonpydev.pythonanywhere.com) will still work until you reconfigure.

2. **Configure the Web App for the Custom Domain**:
   - Go to the "Web" tab in your PythonAnywhere dashboard.
   - If reusing your existing app: Click the pencil icon next to the domain field (currently your free subdomain) and change it to `www.poker-profits.com` (use "www" for the subdomain; naked domains like poker-profits.com require extra setup—see below).
   - If creating a new app: Click "Add a new web app," select your domain (`www.stakeeasy.net`), choose Python/Flask, and set up your code/files as before (upload your StakeEasy.net app if needed).
   - Reload the web app (green "Reload" button). PythonAnywhere will now expect traffic for `www.stakeeasy.net`.
   - Update your app code: In your Flask/Django settings, add the new domain to `ALLOWED_HOSTS` (e.g., `ALLOWED_HOSTS = ['www.stakeeasy.net', 'stakeeasy.net']`). Reload again.
   - Note the CNAME value: On the Web tab, under "DNS configuration," you'll see a value like `webapp-12345.pythonanywhere.com` (this is unique to your app—copy it).

3. **Set Up DNS Records at Your Registrar**:
   - Log in to your registrar's dashboard and find the DNS management section (e.g., "DNS" or "Zone Editor" on GoDaddy/Namecheap).
   - Add a CNAME record:
     - **Host/Alias/Name**: `www` (this points the www subdomain).
     - **Value/Points To/Canonical Name**: Paste the value from PythonAnywhere (e.g., `webapp-12345.pythonanywhere.com.`—note the trailing dot if required by your registrar).
     - **TTL (Time to Live)**: Set to 1 hour (or default; this controls propagation speed).
   - Delete conflicting records: If there's an existing TXT or A record for `www`, remove it (e.g., OVH auto-creates a TXT—delete it).
   - Save changes. Propagation takes 1-48 hours (usually 1-24); check status on PythonAnywhere's Web tab (it shows a warning if DNS isn't set up) or use a tool like https://www.whatsmydns.net/.
   - For naked/apex domain (stakeeasy.net without www): CNAMEs don't work here. Instead:
     - Use your registrar's forwarding/redirect tool to redirect `stakeeasy.net` to `www.stakeeasy.net` (e.g., GoDaddy's "Forwarding" feature).
     - Or set an A record to PythonAnywhere's IP (not recommended—use CNAME for www and redirect for naked).

4. **Test and Secure the Setup**:
   - Wait for propagation, then visit `www.stakeeasy.net`—it should load your StakeEasy.net app.
   - If issues: Check PythonAnywhere's DNS troubleshooting (https://help.pythonanywhere.com/pages/TroubleshootingDNS). Common fixes: Wait longer, verify CNAME syntax, or contact support.
   - Enable HTTPS (recommended for security, especially for financial apps like bankroll tracking):
     - On the Web tab, go to "Security" section > Enable "HTTPS/SSL" (free Let's Encrypt certificate).
     - Force HTTPS redirects in your app code or PythonAnywhere settings.
   - Update any internal links in your app (e.g., from free subdomain to new domain).

5. **Verify and Maintain**:
   - Use tools like https://www.digwebinterface.com/ to confirm the CNAME points correctly.
   - Monitor: Renew your domain annually via the registrar. PythonAnywhere bills monthly—cancel anytime with a 30-day money-back guarantee.
   - For multi-currency support in your app (as per the document), ensure your code handles the domain change without issues.

**Potential Costs and Timeline**:
- Domain: $10-20/year.
- PythonAnywhere: $5+/month.
- Total time: 1-2 days (mostly waiting for DNS).
- Troubleshooting: If stuck, PythonAnywhere forums/support are excellent; registrar support can help with DNS.

This setup will make your StakeEasy.net app accessible at stakeeasy.net, improving professionalism for tracking poker funds and assets. If the domain is unavailable, search for alternatives during purchase. For poker-themed domains, check for .poker TLDs (~$8-10 via Namecheap/GoDaddy) if .com is taken.
