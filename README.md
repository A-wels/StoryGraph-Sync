# StoryGraph-Sync
Synchronize your reading progress with [TheStoryGraph](https://app.thestorygraph.com/)

## Features
- Grab  [Moon+ Reader](https://www.moondownload.com/) reading progress from Nextcloud
- Grab [Audiobookshelf](https://www.audiobookshelf.org/) listening progress from the API
- Automatically match with currently read books on StoryGraph
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

### Possible parameters
- `--path`Path to moon+ reader cache files
- `--interval` Sync interval in hours
- `--audiobookshelf` Disabled audiobookshelf sync
- `---moonplus`Disabled Moon+ sync

The reading progress will be synced every hour.

# Disclaimer
This project is not affiliated with TheStoryGraph. Use at your own risk.
