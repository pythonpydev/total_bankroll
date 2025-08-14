If you're trying to run the **Gemini CLI** (Google's command-line AI agent) from your terminal on Linux Mint, here's how to get started:

---

### 1. Install the CLI

First, ensure you have Node.js **version 20 or higher** installed. You can check with:

```bash
node -v
```

If you're on Node.js 18 or below, update it before proceeding.

Then install Gemini CLI in one of two ways:

* **Run it directly without installing (via npx)**:

  ```bash
  npx @google/gemini-cli
  ```

  or

  ```bash
  npx https://github.com/google-gemini/gemini-cli
  ```

  ([GitHub][1])

* **Install globally with npm**:

  ```bash
  npm install -g @google/gemini-cli
  ```

  If you encounter permission errors, you may need to use `sudo`:

  ```bash
  sudo npm install -g @google/gemini-cli
  ```

  ([GitHub][1], [thecreatorsai.com][2], [OMG! Ubuntu][3], [Philschmid][4])

---

### 2. Launch the Gemini CLI

Once installed (or via `npx`), simply run:

```bash
gemini
```

This will start an interactive terminal session where you can chat with the Gemini AI—ask it to analyze files, generate code, run shell commands, and more. You’ll be prompted to authenticate with your Google account upon first use ([DEV Community][5]).

**Note for Ubuntu/Linux Mint users:**
If installed via `npx` only and not globally, the plain `gemini` command might not work. In that case, you'll need to run:

```bash
npx @google/gemini-cli
```

as your launch command instead ([OMG! Ubuntu][3]).

---

### Summary Table

| Installation Method      | Command                             | Launch Command                                                |
| ------------------------ | ----------------------------------- | ------------------------------------------------------------- |
| Without installing (npx) | `npx @google/gemini-cli`            | `npx @google/gemini-cli` (required if not globally installed) |
| Global install via npm   | `npm install -g @google/gemini-cli` | `gemini`                                                      |

---

### Example Workflow on Linux Mint

```bash
# Ensure Node.js is up to date
node -v

# Option A: Run without installing
npx @google/gemini-cli

# Option B: Install globally (may need sudo)
sudo npm install -g @google/gemini-cli
gemini
```

When you run it (whichever method you choose), Gemini CLI will guide you through authentication—typically by asking you to sign in with a Google account—and then you'll be ready to interact with it directly from your terminal ([DEV Community][5]).

---

### Extra Tips & Features

* Use **interactive mode** simply by running `gemini`, or use:

  ```bash
  gemini -p "Your prompt here"
  ```

  for one-shot prompts. ([Philschmid][4], [GitHub][6])

* You can authenticate using an API key from **Google AI Studio**, by setting the `GEMINI_API_KEY` environment variable or placing it in a `.env` file. ([Philschmid][4])

* Many command‑line flags are available like `--sandbox`, `--debug`, `--yolo`, etc., to control things like sandboxing, tool usage, auto‑approval, etc. ([Philschmid][4])

---

Let me know if you'd like help configuring authentication, fine-tuning options, or anything else about using Gemini CLI!

[1]: https://github.com/google-gemini/gemini-cli?utm_source=chatgpt.com "google-gemini/gemini-cli: An open-source AI agent that ..."
[2]: https://thecreatorsai.com/p/complete-guide-to-gemini-cli?utm_source=chatgpt.com "Complete Guide to Gemini CLI"
[3]: https://www.omgubuntu.co.uk/2025/07/how-to-install-gemini-cli-on-ubuntu?utm_source=chatgpt.com "How to Install Gemini CLI on Ubuntu to Access AI from ..."
[4]: https://www.philschmid.de/gemini-cli-cheatsheet?utm_source=chatgpt.com "Google Gemini CLI Cheatsheet"
[5]: https://dev.to/proflead/gemini-cli-full-tutorial-2ab5?utm_source=chatgpt.com "Gemini CLI Full Tutorial"
[6]: https://github.com/reugn/gemini-cli?utm_source=chatgpt.com "reugn/gemini-cli: A command-line interface ..."
