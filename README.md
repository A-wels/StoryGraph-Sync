# StoryGraph-Sync
Synchronize your reading progress with [TheStoryGraph](https://app.thestorygraph.com/)

## Features
- Grab  [Moon+ Reader](https://www.moondownload.com/) reading progress from Nextcloud
- Automatically match with currenlty read books on StoryGraph
- Update reading progress automatically every hour

## Getting started
Clone the repository and install the requirements into a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
Copy `config-template.py`to `config.py` and enter your information.

Run `python main.py`

The reading progress will be synced every hour.

# Disclaimer
This project is not affiliated with TheStoryGraph. Use at your own risk.
