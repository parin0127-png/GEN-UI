# GEN-UI 🎨
> AI-powered UI generator that creates production-grade HTML, CSS, JS interfaces from a single line prompt

[![PyPI version](https://badge.fury.io/py/genui-ai.svg)](https://badge.fury.io/py/genui-ai)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## 🚀 What is GEN-UI?
GEN-UI takes a text prompt and automatically:
1. **Searches** the web for UI design references
2. **Scrapes** the best result for style inspiration
3. **Generates** a complete production-grade HTML/CSS/JS file
4. **Opens** it instantly in your browser

## ✨ Example Outputs
- 🚗 Luxury car dealership website with real photos
- 🚀 Space tourism booking platform with live countdown
- 🎵 Spotify clone with music player
- 💎 3D creative agency portfolio with animations
- 💰 Cryptocurrency exchange platform
- 📸 Instagram clone with stories and feed
- 🏨 5-star hotel booking website
- 🎬 Netflix-style streaming platform

## ⚡ Installation

```bash
pip install genui-ai
```

## 🔑 Setup
Create a `.env` file in your working directory:
Get your **free** API key at **cloud.cerebras.ai** — no credit card required!

## ▶️ Run
```bash
genui
```

## 💡 Example Prompts
Build a luxury car dealership with dark theme and gold accents
Create a space tourism booking website with animated starfield
Make a Spotify clone with music player and equalizer
Build a crypto exchange platform like Binance
Create a 3D creative agency portfolio with glassmorphism
Build a Netflix clone with movie cards and subscription plans
Create an Instagram clone with stories and post feed

## 🛠️ Tech Stack
+-------------------------------------------------+
|  Component     |  Technology                    |
|----------------|--------------------------------|
| AI Provider    | Cerebras API                   |
| Primary Model  | qwen-3-235b-a22b-instruct-2507 |
| Fallback Model | llama3.1-8b                    |
| Web Search     | DuckDuckGo (DDGS)              |
| Scraping       | BeautifulSoup4                 |
|      UI        | Rich Console                   |
+-------------------------------------------------+
## ⚡ Architecture
User Prompt
↓
Web Search (DuckDuckGo)
↓
Scrape Best URL (BeautifulSoup)
↓
Generate HTML/CSS/JS (Cerebras AI)
↓
Save & Open in Browser

## 📁 Project Structure
GEN-UI/
├── genui/
│   ├── init.py
│   └── UI.py
├── outputs/        # Generated HTML files
├── .env            # API keys (not committed)
├── .gitignore
├── LICENSE
├── README.md
├── setup.py
└── pyproject.toml

## 🔄 Changelog
- **v1.0.0** - Pipeline architecture with Cerebras

## 🤝 Contributing
Pull requests are welcome! For major changes please open an issue first.

## 📄 License
MIT License — see [LICENSE](LICENSE) file for details

## 👨‍💻 Author
**Parin** — [@parin0127-png](https://github.com/parin0127-png)

---
⭐ If you found this useful, please star the repo!