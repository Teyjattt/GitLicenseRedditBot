# GitLicenseRedditBot
   This is my first serious attempt at writing something (that is beyond solving project Euler problems). Someone had posted in r/learnpython to build a bot that checks for a license on github repositories, and I thought it would be a good way to learn. It is currently working exactly how I expect it to, though there are things that I know I need to add or cleanup. Below I'll explain some of what I have built and some things that I currently still need to work on.
   1) I started with using a json file to hold my list of users that optput. I went with a json file as I was originally thinking of keeping a list of blocked users and blocked repositories and a json file seemed the easiest way to do that. I decided against blocking repositories after I had the json process built and didn't see any reason to change it.
   2) I'm looking for github urls that have just the user and repository name. If the path is longer than that, they are pointing at something more specific and I didn't feel like this bot would be as useful in that instance. Though this could easily be changed in the getGitLink function.
   3) I made the steps to look for a url a function as it would make it easier to expand functionality to check comments for github urls in the future if I wanted to add that functionality.
   4) While Im pulling the License ID, I'm currently only reply with a message if the license is blank (leaves a reply that there is no license) or the github pull fails which has indicated to me the repository is either private or doesn't exist (and leaves a different reply to indicate that).
   5) After looking at the data that comes back from several submissions, it appears the license id from github indicates what type of license it is. I had considered adding a reply explaining that there was a license and what license it is. Still an option would take more research on the different license ids.
   6) I have a function to update the optout file based on checking messages that are sent to the bot. I currently have it set to update when the bot starts and it checks all messages and adds user to list if they aren't currenlty in it. I would like to:
      a) run the function on a more frequent basis automatically
      b) only check the unread messages
   7) One feature I would like to add is a limit on how many times the bot would reply to a given repository. That is if someone posted a specific repository two days ago and the bot replied that it did not have a license, and then they posted it again today I didn't want my bot to hit them yet again. I was thinking maybe leaving a 7 day gap before replying about the same repository.
