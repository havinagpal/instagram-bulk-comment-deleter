# Instagram Bulk Comment Deleter

This repository provides a Python script to automate the deletion of comments on Instagram using Selenium WebDriver. It is intended for users who want to efficiently manage and remove their Instagram comments in a secure manner.

## Features
- Automates bulk deletion of Instagram comments (or unlikes) using Selenium WebDriver
- **Works with Chrome, Firefox, and Edge** — choose your browser at startup
- Interactive CLI prompts to configure batch size, delays, and retry behavior
- Handles Instagram rate limiting with configurable wait-and-retry logic
- Supports English and French Instagram UI text
- Uses `webdriver-manager` to automatically install the correct browser driver
- Graceful error handling: recovers from "Something went wrong" pages, stale elements, and browser closure
- Safe shutdown on Ctrl+C — closes the browser cleanly even if it was never opened

## Requirements
- Python 3.8 or higher
- At least one of the following browsers installed:
  - Google Chrome
  - Mozilla Firefox
  - Microsoft Edge
- Python packages (see `requirements.txt`):
   - `selenium`
   - `webdriver-manager`

## Installation
1. **Clone the repository:**
   ```sh
   git clone https://github.com/<your-username>/instagram-comment-delete.git
   cd instagram-comment-delete
   ```
2. **(Optional) Create a virtual environment:**
   ```sh
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```
3. **Install the requirements:**
   ```sh
   pip install -r requirements.txt
   ```

## Usage
1. Run the script:
   ```sh
   python main.py
   ```
2. The script will prompt you to configure:
   - **Browser** — choose Chrome, Firefox, or Edge (default: Chrome)
   - **Batch size** — how many comments to select per batch (default: 5)
   - **Delay between selections** — seconds to wait between each checkbox click (default: 2.0s)
   - **Delay after batch deletion** — seconds to wait after each batch is deleted (default: 10.0s)
   - **Rate-limit retry interval** — hours to wait before retrying if rate-limited (default: 1.0h)
3. A Chrome browser window will open. **Log in to Instagram manually** in that window.
4. Once logged in, the script will automatically navigate to your comment activity page and begin deleting comments in batches.
5. Press **Ctrl+C** at any time to stop the script safely.

**Important Notes:**
- The script creates a browser profile folder (`chrome-profile`, `firefox-profile`, or `edge-profile`) in the script directory to persist your login session.
- This folder may contain sensitive session data. **Delete the profile folder after you are done to protect your account.**
- This script does **not** intentionally cache or store your Instagram credentials, but the browser profile folder may contain session information.
- Use this script responsibly and in accordance with Instagram's terms of service.

## Security
- No credentials are intentionally cached or stored by this script, but the browser profile folder (`chrome-profile`, `firefox-profile`, or `edge-profile`) may contain session data.
- Always delete the profile folder after use to protect your account.
- Keep your credentials secure and avoid sharing them.

## .gitignore
This repository includes a `.gitignore` file to prevent sensitive files, virtual environments, and cache (including `chrome-profile`) from being committed.

## License
This project is licensed under the MIT License.
