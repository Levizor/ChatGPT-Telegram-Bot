# ChatGPT-Telegram-Bot

## Project Description

**ChatGPT-Telegram-Bot** is a Telegram bot designed to provide intelligent responses using OpenAI's ChatGPT. Alongside ChatGPT, the bot integrates other AI technologies to enhance its capabilities. Additionally, it features practical functions such as downloading content from YouTube and TikTok.

## Installation Instructions

Follow these steps to set up and run the **ChatGPT-Telegram-Bot**:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Levizor/ChatGPT-Telegram-Bot.git
   ```

2. **Install the required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure your variables:**
   - Create a `config.py` file based on the provided sample `config.sample.py`.
   - Optionally, if you prefer polling instead of setting up a webhook, set the `TEST` variable to `True` in the configuration.

4. **Additional Configuration for YouTube Video Downloads:**

   The bot uses the `pytube` module for downloading videos. If you encounter issues with downloading age-restricted videos, follow these instructions:

   - Locate the `innertube.py` file within the `pytube` package (usually found in your Python environment's `site-packages` directory).
   - Open the file and find the `InnerTube` class.
   - Modify the `client` parameter on line 223 from `ANDROID_MUSIC` to `ANDROID`.

   Now it should look like:
   
     ```innertube.py
     class InnerTube:
            """Object for interacting with the innertube API."""
            def __init__(self, client='ANDROID', use_oauth=False, allow_cache=True):
                """Initialize an InnerTube object.

     ```


Now, your **ChatGPT-Telegram-Bot** is ready to use. Just run main.py file in console. 

You can use ngrok for establishing webhook. 
