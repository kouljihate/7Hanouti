# 7Hanouti (حانوتي)

A cross-platform inventory and cash management application for small shop owners, built with Python and [Flet](https://flet.dev).

## Features

- **Dashboard** — Real-time KPIs: stock value, cash balance, product count, low stock alerts
- **Stock Management** — Add/edit/delete products, stock in/out movements with full history
- **Cash Management** — Track income & expenses, view balance and transaction history
- **Multi-language** — Arabic, French, English
- **Dark & Light Themes** — Toggle between dark and light mode
- **Local Database** — SQLite, no internet required

## Screenshots

*(Add screenshots here)*

## Requirements

- Python 3.8+

## Installation & Usage

```bash
# Clone the repository
git clone https://github.com/kouljihate/7Hanouti.git
cd 7Hanouti

# Run (auto-installs dependencies)
python run.py
```

Or manually:

```bash
pip install flet>=0.25.0
python main.py
```

## Project Structure

```
7Hanouti/
├── app/
│   ├── screens/          # UI screens (login, dashboard, stock, cash, settings)
│   ├── database.py       # SQLite database operations
│   ├── theme.py          # App theme and colors
│   ├── translations.py   # Multi-language translations (AR/FR/EN)
│   └── version.py        # Version info
├── assets/
│   ├── fonts/            # Custom fonts
│   └── icon.png          # App icon
├── data/                 # SQLite database directory
├── main.py               # Application entry point
├── run.py                # Launcher script
└── requirements.txt      # Python dependencies
```

## Versioning

Current version: **1.2.0**

## License

MIT
