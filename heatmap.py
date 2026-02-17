import tkinter as tk
import winreg
from PIL import Image
import colorsys
from datetime import datetime, timedelta
import random
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class HeatmapWindow:
    # Constants
    DEFAULT_COLORS = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
    BRIGHTNESS_FACTOR = 5
    IMAGE_RESIZE_DIM = 150
    NUM_COLOR_LEVELS = 26
    GITHUB_USERNAME = "egreene-alpineedge"
    GITHUB_API_URL = "https://api.github.com/graphql"
    def __init__(self):
        self.root = tk.Tk()

        # Remove window decorations (title bar, borders)
        self.root.overrideredirect(True)

        # Set window size and position at top right
        window_width = 825
        window_height = 300
        screen_width = self.root.winfo_screenwidth()
        x_position = screen_width - window_width
        y_position = 0
        self.root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

        # Set dark theme colors (matching design.html)
        self.bg_color = "#0d1117"
        self.root.configure(bg=self.bg_color)

        # Make background transparent
        self.root.attributes("-transparentcolor", self.bg_color)

        # Variables for dragging
        self.offset_x = 0
        self.offset_y = 0

        # Bind drag events
        self.root.bind("<Button-1>", self.start_drag)
        self.root.bind("<B1-Motion>", self.do_drag)

        # Add a simple text label
        # self.label = tk.Label(
        #     self.root,
        #     text="Contribution Activity",
        #     font=("Segoe UI", 24, "bold"),
        #     fg="#c9d1d9",
        #     bg=self.bg_color
        # )
        # self.label.pack(pady=40)

        # Create canvas for heatmap grid
        self.canvas = tk.Canvas(
            self.root,
            bg=self.bg_color,
            highlightthickness=0,
            width=1100,
            height=150
        )
        self.canvas.pack(pady=20)

        # Create hover info label near the grid
        self.hover_label = tk.Label(
            self.root,
            text="",
            font=("Segoe UI", 10),
            fg="#8b949e",
            bg=self.bg_color,
            justify="left",
            anchor="w"
        )
        self.hover_label.place(x=50, y=175)

        # Draw the grid
        self.draw_grid()

    def brighten_color(self, hex_color, factor=None):
        """Increase the brightness of a hex color"""
        if factor is None:
            factor = self.BRIGHTNESS_FACTOR

        # Remove # if present
        hex_color = hex_color.lstrip('#')
        # Convert to RGB
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)

        # Convert to HSV
        h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)

        # Increase brightness (value)
        v = min(1.0, v * factor)
        
        # Convert back to RGB
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        r, g, b = int(r * 255), int(g * 255), int(b * 255)
        
        # Convert back to hex
        return f"#{r:02x}{g:02x}{b:02x}"

    def fetch_github_contributions(self):
        """Fetch contribution data from GitHub GraphQL API"""
        query = """
        query($username: String!) {
            user(login: $username) {
                contributionsCollection {
                    contributionCalendar {
                        weeks {
                            contributionDays {
                                contributionCount
                                date
                            }
                        }
                    }
                }
            }
        }
        """

        # Try to fetch without authentication first (public profiles)
        headers = {"Content-Type": "application/json"}

        # Check for token in environment (loaded from .env file)
        token = os.environ.get('GITHUB_TOKEN')
        if token:
            headers["Authorization"] = f"Bearer {token}"

        try:
            response = requests.post(
                self.GITHUB_API_URL,
                json={"query": query, "variables": {"username": self.GITHUB_USERNAME}},
                headers=headers,
                timeout=10
            )

            print(f"GitHub API response status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print(f"GitHub API response: {data}")

                if 'data' in data and data['data'] and 'user' in data['data']:
                    weeks = data['data']['user']['contributionsCollection']['contributionCalendar']['weeks']

                    # Convert to dictionary mapping date -> count
                    contributions = {}
                    for week in weeks:
                        for day in week['contributionDays']:
                            date_str = day['date']
                            count = day['contributionCount']
                            contributions[date_str] = count

                    print(f"Successfully fetched {len(contributions)} days of contributions")
                    return contributions
                else:
                    print(f"Unexpected API response structure")
                    if 'errors' in data:
                        print(f"API errors: {data['errors']}")
            else:
                print(f"API request failed with status {response.status_code}")
                print(f"Response: {response.text}")

            return None

        except Exception as e:
            print(f"Error fetching GitHub contributions: {e}")
            import traceback
            traceback.print_exc()
            return None

    def get_contribution_level(self, count):
        """Convert contribution count to level (0-4) matching GitHub's thresholds"""
        if count == 0:
            return 0
        elif count <= 1:
            return 1
        elif count <= 2:
            return 2
        elif count <= 3:
            return 3
        else:
            return 4

    def get_wallpaper_path(self):
        """Get the current desktop wallpaper path from Windows registry"""
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                r"Control Panel\Desktop", 0, winreg.KEY_READ)
            wallpaper_path, _ = winreg.QueryValueEx(key, "WallPaper")
            winreg.CloseKey(key)
            return wallpaper_path
        except Exception as e:
            print(f"Error getting wallpaper path: {e}")
            return None

    def extract_colors_from_wallpaper(self, num_colors=None):
        """Extract dominant colors from the desktop wallpaper"""
        if num_colors is None:
            num_colors = self.NUM_COLOR_LEVELS

        wallpaper_path = self.get_wallpaper_path()
        if not wallpaper_path:
            colors = [self.brighten_color(c) for c in self.DEFAULT_COLORS]
            print(f"Using default colors (brightened): {colors}")
            return colors

        try:
            # Open and resize image for faster processing
            img = Image.open(wallpaper_path)
            img = img.resize((self.IMAGE_RESIZE_DIM, self.IMAGE_RESIZE_DIM))
            img = img.convert('RGB')

            # Get colors using quantization
            img_quantized = img.quantize(colors=num_colors)
            palette = img_quantized.getpalette()

            # Extract the colors
            colors = []
            for i in range(num_colors):
                r, g, b = palette[i*3:(i+1)*3]
                colors.append((r, g, b))

            # Sort colors by brightness
            colors.sort(key=lambda rgb: colorsys.rgb_to_hsv(rgb[0]/255, rgb[1]/255, rgb[2]/255)[2])

            # Convert to hex
            hex_colors = [f"#{r:02x}{g:02x}{b:02x}" for r, g, b in colors]
            
            # Brighten the colors
            hex_colors = [self.brighten_color(c) for c in hex_colors]
            
            print(f"Using extracted colors (brightened): {hex_colors}")

            return hex_colors
        except Exception as e:
            print(f"Error extracting colors: {e}")
            colors = [self.brighten_color(c) for c in self.DEFAULT_COLORS]
            print(f"Falling back to default colors (brightened): {colors}")
            return colors

    def create_rounded_rectangle(self, x1, y1, x2, y2, radius, **kwargs):
        """Draw a rounded rectangle on the canvas"""
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1
        ]
        return self.canvas.create_polygon(points, smooth=True, **kwargs)

    def draw_grid(self):
        # Clear any existing drawings so redraws replace the old grid
        self.canvas.delete("all")

        # Grid settings (matching design.html)
        square_size = 11
        gap = 3
        weeks = 53
        days_per_week = 7
        start_x = 50
        start_y = 40  # Increased to make room for month labels
        corner_radius = 2

        # Extract colors from wallpaper
        colors = self.extract_colors_from_wallpaper()

        # Fetch GitHub contributions
        github_contributions = self.fetch_github_contributions()

        # Generate dates for the last year (trailing 365 days)
        today = datetime.now()
        start_date = today - timedelta(days=364)  # Last 365 days including today

        # Create date grid
        dates = []
        current_date = start_date
        for _ in range(365):
            dates.append(current_date)
            current_date += timedelta(days=1)

        # Group dates by weeks
        weeks_data = []
        current_week = []
        first_day = start_date.weekday()

        # Add empty cells for the first week
        for _ in range((first_day + 1) % 7):
            current_week.append(None)

        for date in dates:
            current_week.append(date)
            if len(current_week) == 7:
                weeks_data.append(current_week)
                current_week = []

        if current_week:
            while len(current_week) < 7:
                current_week.append(None)
            weeks_data.append(current_week)

        # Draw month labels
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        current_month = -1

        for week_idx, week in enumerate(weeks_data):
            first_day = next((d for d in week if d is not None), None)
            if first_day:
                month = first_day.month - 1
                if month != current_month:
                    x = start_x + week_idx * (square_size + gap)
                    self.canvas.create_text(
                        x,
                        start_y - 15,
                        text=month_names[month],
                        fill="#8b949e",
                        font=("Segoe UI", 10),
                        anchor="w"
                    )
                    current_month = month

        # Draw day labels
        day_labels = ["", "Mon", "", "Wed", "", "Fri", ""]
        for i, label in enumerate(day_labels):
            if label:
                self.canvas.create_text(
                    start_x - 20,
                    start_y + i * (square_size + gap) + square_size // 2,
                    text=label,
                    fill="#8b949e",
                    font=("Segoe UI", 9),
                    anchor="e"
                )

        # Draw the grid squares
        for week_idx, week in enumerate(weeks_data):
            for day_idx, date in enumerate(week):
                x = start_x + week_idx * (square_size + gap)
                y = start_y + day_idx * (square_size + gap)

                if date:
                    # Get contribution count from GitHub or use random
                    date_str = date.strftime('%Y-%m-%d')
                    if github_contributions and date_str in github_contributions:
                        count = github_contributions[date_str]
                        
                        level = self.get_contribution_level(count)
                        # print(f"Count for {date_str}: {count} (level: {level}) -> {colors[level]}")
                    else:
                        # Fallback to random if GitHub data not available
                        level = random.randint(0, 4)
                        count = level * 3  # Approximate count from level

                    color = colors[level*5+1]

                    square = self.create_rounded_rectangle(
                        x, y,
                        x + square_size, y + square_size,
                        corner_radius,
                        fill=color,
                        outline=color,
                        width=1
                    )

                    # Bind hover events to show date and count
                    self.canvas.tag_bind(square, '<Enter>',
                        lambda e, d=date, c=count: self.on_hover(d, c))
                    self.canvas.tag_bind(square, '<Leave>',
                        lambda e: self.on_leave())

        # Schedule next refresh in 6 hours (6 * 60 * 60 * 1000 ms)
        six_hours_ms = 6 * 60 * 60 * 1000
        self.root.after(six_hours_ms, self.draw_grid)

    def on_hover(self, date, count):
        """Display date and contribution count when hovering over a square"""
        date_str = date.strftime('%A, %B %d, %Y')
        if count == 0:
            contribution_text = "No contributions"
        elif count == 1:
            contribution_text = "1 contribution"
        else:
            contribution_text = f"{count} contributions"
        self.hover_label.config(
            text=f"{date_str} - {contribution_text}"
        )

    def on_leave(self):
        """Clear the hover label when mouse leaves a square"""
        self.hover_label.config(text="")

    def start_drag(self, event):
        self.offset_x = event.x
        self.offset_y = event.y

    def do_drag(self, event):
        x = self.root.winfo_x() + event.x - self.offset_x
        y = self.root.winfo_y() + event.y - self.offset_y
        self.root.geometry(f"+{x}+{y}")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = HeatmapWindow()
    app.run()
