<div align="center" align="left">
    <img src="images/avatar-circle.png" alt="Spirit-Bot" style="width: 100px; height: 100px;">
    <div>   
        <h1>Spirit-Bot</h1>
        <p>This is a Discord moderation bot designed to assist SpiritMC server moderators in managing user behavior through various commands and systems.</p>
    </div>
</div>

## Features

- **Commands**: Includes commands for kicking, banning, warning users, and managing moderation logs.
- **Warning System**: Allows moderators to issue warnings to users, track them, and take automated actions based on warning thresholds.
- **ModLog**: Logs moderation actions to a designated channel for transparency and record-keeping.
- **Customization**: Provides options to enable/disable specific features and customize moderation settings.

## Usage

To use the bot, you need to invite it to your Discord server. You can do so by following the [Bot Invite](https://discord.com/api/oauth2/authorize?client_id=1208974336795344977&permissions=8&scope=bot+applications.commands) link.

Once the bot is in your server, you can use various commands to manage moderation tasks and configure the bot's behavior according to your server's needs.

## Installation

1. Clone the repository:

   ```
   git clone https://github.com/Jonny0181/Spirit-Bot.git
   ```

2. Navigate into the directory:

    ```
    cd Spirit-Bot
    ```

3. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables:

   - Create a `.env` file in the root directory.
   - Add the following variables:
     ```
     TOKEN=your_discord_bot_token
     PREFIX=your_prefix
     MONGO_DB_COLLECTION=your_collection_name
     MONGO_DB=your_mongodb_connection_string
     ```
   Replace `TOKEN` with your actual Discord bot token. And all others ones with valid values.

5. Run the bot:

   ```
   python main.py
   ```

## Contributing

Contributions are welcome! If you find any bugs or have suggestions for improvements, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.