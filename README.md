# All-In-One Automatic Clicker

An automatic clicker for the (Hamster ~ TapSwap ~ Cex IO) bots.

## Prerequisites

- Python 3.10 or higher

## Installation

Follow these steps to install and set up the automatic clicker on Telegram:

1. **Clone the Repository**
   ```sh
   git clone https://github.com/Poryaei/All-In-One
   cd All-In-One
   ```

2. **Create and Activate a Virtual Environment**
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. **Install Dependencies**
   ```sh
   pip install -r requirements.txt
   ```

## Setup

1. **Configure Telegram Accounts**
   - Ensure you have the phone numbers for each account that will be used to operate the clicker.

2. **Edit the Configuration File**
   - Open the `config.json` file and edit the necessary parameters.
   - Example `config.json`:
     ```json
     {
         "api_id": 8086441,
         "api_hash": "2a305482a93b5a762d2acd4be90dd00f",
         "admin": 0000000,
         "tapswap_clicker": "on",
         "hamster_clicker": "on",
         "cexio_clicker": "on",
         "auto_upgrade": true,
         "max_days_for_return": 30,
         "max_charge_level": 5,
         "max_energy_level": 10,
         "max_tap_level": 10
     }
     ```
   - **Note:** 
     - Replace the value of `admin` with the numeric ID of the admin. You can get this ID by contacting [@chatIDrobot](https://t.me/chatIDrobot) on Telegram.
     - If you set any of the clickers (`tapswap_clicker`, `hamster_clicker`, `cexio_clicker`) to "off", the bot will not interact with that specific bot.
     - The `max_days_for_return` setting is for the Hamster bot. It specifies the maximum number of days it should take for a card to return its profit.
     - The `max_charge_level`, `max_energy_level`, and `max_tap_level` settings are for the TapSwap bot.
     - Replace `cexio_ref_code` with your own referral code.

## Running the Script

1. **Run the Clicker Bot**
   ```sh
   python app.py
   ```

2. **Login with Phone Numbers**
   - When prompted, enter the phone numbers of the Telegram accounts.
   - Complete the login process by entering the verification codes sent to each phone.

3. **Send /help Command**
   - After successfully running the script, send the command `/help` to the phone number that the script is running on to see the help instructions.

4. **Monitor the Logs**
   - Check the logs to ensure the bot is running correctly and interacting with the specified bots (Hamster, TapSwap, Cex IO).

## Usage

- The bot will automatically perform the clicking actions on the specified Telegram bots.
- Ensure your environment and setup are correct to avoid any disruptions.

## Troubleshooting

- Ensure Python version 3.10 or higher is installed.
- Verify all dependencies are correctly installed.
- Double-check your phone numbers and ensure they are entered correctly.
- Verify the `config.json` file is correctly configured.

## Contact

For further assistance, please reach out to the project maintainer.

---

This guide provides a comprehensive setup and usage manual for the **All-In-One Automatic Clicker**. Make sure to follow each step carefully to ensure the tool functions correctly.
