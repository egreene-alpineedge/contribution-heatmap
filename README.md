## Desktop GitHub Contribution Heatmap

A transparent, draggable desktop widget that displays a **GitHub-style contribution heatmap** for a user, with colors automatically **extracted from your current desktop wallpaper**.

### Features

- **Full-year contribution grid** similar to GitHub's profile page.
- **Wallpaper-aware palette**: Dominant colors are sampled from your current wallpaper and brightened.
- **Hover details**: Hover over any square to see the exact date and contribution count.
- **Draggable, borderless window** that blends into the desktop using transparency.
- **Automatic refresh**: Contribution data and colors are periodically refreshed.

### Requirements

- **OS**: Windows.
- **Python**: 3.x.
- **Python packages** (at minimum):
  - `Pillow` (listed in `requirements.txt`)
  - `requests`
  - `python-dotenv`

You can install everything with:

```bash
pip install Pillow requests python-dotenv
```

Or, if you keep `requirements.txt` updated with all dependencies:

```bash
pip install -r requirements.txt
```

### GitHub API configuration

The script calls the GitHub GraphQL API to fetch real contribution data.

- **Username**: configured in `heatmap.py`:
  - `GITHUB_USERNAME = "egreene-alpineedge"`
  - Change this value if you want to visualize a different account.

- **Authentication (recommended)**:
  - Create a **Personal Access Token** on GitHub (fine-grained or classic with minimal read-only scopes for public data).
  - Create a `.env` file in this folder with:

    ```bash
    GITHUB_TOKEN=your_token_here
    ```

  - The script loads this via `python-dotenv` and sends it as a `Bearer` token when calling the API.

**Do not commit your `.env` or token to version control.**

### Project files

- **`heatmap.py`**: Main Tkinter app that:
  - Gets your wallpaper via the Windows registry.
  - Extracts a color palette with Pillow.
  - Fetches contribution data from GitHub and maps counts to color levels.
  - Draws the grid and handles hover interactions and dragging.
- **`run_heatmap.vbs`**: Windows Script Host launcher that runs `pythonw heatmap.py` with **no console window**.
- **`run_heatmap.bat`**: Batch file that runs `pythonw heatmap.py` from a command prompt.
- **`.env`**: Local configuration file for `GITHUB_TOKEN` (not for sharing/committing).
- **`requirements.txt`**: Base Python dependency list (currently includes at least `Pillow`).

### Running the widget

- **Typical usage (no console window)**  
  Double‑click `run_heatmap.vbs` in Explorer.  
  This:
  - Sets the working directory to the script folder.
  - Runs `pythonw heatmap.py` without opening a terminal window.

- **Alternative (batch wrapper)**  
  Double‑click `run_heatmap.bat` if you prefer a simple `.bat` wrapper.

- **Debug / development mode (with console)**  
  From a terminal in `contribution-heatmap`:

  ```bash
  python heatmap.py
  ```

### Interaction and layout

- **Default position**: Top-right of the primary screen.
- **Dragging**: Click and hold anywhere in the window, then move the mouse.
- **Hover info**: Move the mouse over a square to see `weekday, month day, year` plus the contribution count.
- **Refresh**: The grid automatically redraws every few hours to stay up to date.

