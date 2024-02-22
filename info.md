🔃 In progess
✅ Done

## 1. Commands
1. 🔃 kick - (user, reason) Needs to have a reason on why the user was kicked. (Will be logged to the modlog system)
2. 🔃 ban - (user, reason, messages) Needs to have a reason on why the user was banned, and how many days of messages to delete. (Will be logged to the modlog system)

# 2. Systems

## Warning System:

### Commands:
1. 🔃 setup - (channel, warn_kick, warn_ban) Needs to have a channel mention for warning logs. warn_kick and warn_ban need a int value of how many warnings until that action is taken.
2. 🔃 warns - (user) Need to mention a user to view their active warnings and reasons behind them. (Preferably an embed containing a list.)
3. 🔃 clear - (user) Need to mention a user to clear all of their active warnings.
4. 🔃 add - (user, reason) Need to mention a user and reason to give someone a warning. Needs to save a ID that can be used later to remove the warning.
5. 🔃 remove (id, user) Need to pass warning id and mention user to remove a specific warning from the user.

### Events:
1. 🔃 logs - When a user is given a warning send a log to the given channel when command setup was used.
2. 🔃 commit - Check users warnings when one is given, if number of warns matches warn_kick or warn_ban...PERFORM ACTION!

## ModLod:

### Commands:
1. 🔃 enable (channel) - Mention a channel to use an already existing channel, or don't to have on created.
2. 🔃 disable - Disable the system, if the channel was created delete it otherwise don't.
3. 🔃 toggle - (option [messages, leave, join, channel, guild, voice]) - Provide a list of options the user can enable/disable.

[Developer](https://discord.com/users/827940585201205258 "I'm the best") [Bot Invite](https://discord.com/api/oauth2/authorize?client_id=1208974336795344977&permissions=8&scope=bot+applications.commands "Invite the best discord bot!") [Discord Server](https://discord.gg/bngG4MFDMh "Join the project today!")
