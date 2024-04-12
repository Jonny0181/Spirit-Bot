
---

# Todo and Progress Tracker

## Task Status: 
- 🔃 **In Progress**
- ✅ **Completed**

---

## 1. Commands
1. 🔃 **kick** - *(user, reason)* - Needs to have a reason on why the user was kicked. (Will be logged to the modlog system)
2. 🔃 **ban** - *(user, reason, messages)* - Needs to have a reason on why the user was banned, and how many days of messages to delete. (Will be logged to the modlog system)
3. 🔃 **call** - Call admins to the current channel for assistance.

---

## 2. Systems

### Warnings:

- **Commands:**
    - ✅ **setup** - *(channel, warn_kick, warn_ban)* - Needs to have a channel mention for warning logs. warn_kick and warn_ban need an int value of how many warnings until that action is taken.
    - ✅ **warns** - *(user)* - Need to mention a user to view their active warnings and reasons behind them. (Preferably an embed containing a list.)
    - ✅ **clear** - *(user)* - Need to mention a user to clear all of their active warnings.
    - ✅ **add** - *(user, reason)* - Need to mention a user and reason to give someone a warning. Needs to save an ID that can be used later to remove the warning.
    - ✅ **remove** - *(id, user)* - Need to pass the warning ID and mention the user to remove a specific warning from the user.
    - ✅ Implement checks to make sure you can't give admins warnings, also need to check about higher roles than the bot. (Permissions issue when kicking/banning)

- **Events:**
    - ✅ **logs** - When a user is given a warning, send a log to the given channel when command setup was used.
    - ✅ **commit** - Check users' warnings when one is given, if the number of warns matches warn_kick or warn_ban... PERFORM ACTION!

### ModLog:

- **Commands:**
    - ✅ **enable** - *(channel)* - Mention a channel to use an already existing channel, or don't to have one created.
    - ✅ **disable** - Disable the system, if the channel was created delete it otherwise don't.
    - ✅ **toggle** - *(option [messages, leave, join, channel, guild, voice])* - Provide a list of options the user can enable/disable.
    - 🔃 Finish implementing all modlog events.

### Tickets:

- **Commands:**
    - 🔃 **setup** - *(channel)* - Mention a channel to use an already existing channel, or don't to have one created.

- **Messages:**
    - 🔃 **create-message** - Create a embed message to be send to the tickets channel with a button to open a new ticket.
    - 🔃 **new-ticket-message** - Create a embed message that has buttons to add users, remove user or close/set the ticket as solved.

- **Modals:**
    - 🔃 **ticket-modal** - Create a modal and ask the user why they are opening a ticket.

- **Events:**
    - 🔃 **save-ticket-transcript** - When a ticket is closed, save all messages to a .txt file with the ticket number-username-date format.

### Snipe:

- **Commands:**
    - 🔃 **snipe** - *(user)* Mention a user to fetch their last deleted message, or don't to get the last deleted message in the current channel.

- **Events:**
    - 🔃 **message-delete** - When a message is deleted save it to a snipeMessages dict.

### Report:

- **Commands:**
    - 🔃 **setup** - *(channel)* - Mention a channel to use an already existing channel, or don't to have one created.
    - 🔃 **report** - *(user, reason)* - Report a user with a given reason.

- **Events:**
    - 🔃 **submit-report** - When a report is sent through, send it the the config channel and mention admins in content. Create an embed with field user (reported), by (reporter) and reason.

---

[Developer Discord](https://discord.com/users/827940585201205258 "I'm the best") | [Bot Invite](https://discord.com/api/oauth2/authorize?client_id=1208974336795344977&permissions=8&scope=bot+applications.commands "Invite the best discord bot!") | [Discord Server](https://discord.gg/bngG4MFDMh "Join the project today!")

---
