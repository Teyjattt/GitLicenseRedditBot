from urllib.parse import urlparse
import json
import re
import praw
import requests

#####################################################
REDDITS_TO_FOLLOW = 'testingground4bots'
REDDIT = praw.reddit('GitLicenseBot')
SUBREDDIT = REDDIT.subreddit(REDDITS_TO_FOLLOW)
HEADERS = {'Authorization': 'Token 123456789012345678901234567890'}   #for github api

def main():
    update_optout_file()
    with open('optout.json') as optout_file:
        optout_list = json.load(optout_file)

    for submission in SUBREDDIT.stream.submissions(skip_existing=True):
        ############################################
        #look for github url if users did not optout
        if str(submission.author) not in optout_list:
            git_link = get_git_link(submission.url + ' ' + submission.selftext)
        else:
            continue    #continue to next submission because user optedout
        if git_link is None:
            continue    #no github url was found, or url does not point to main repo
        #################################
        #parse out user and repo from url
        git_parts = urlparse(git_link).path.split('/')
        git_user = git_parts[1]
        git_repo = git_parts[2]
        ###############################
        # pull license data from Github
        try:
            git_license = (get_git_license(git_user, git_repo))['data']['repository']['licenseInfo']
            if git_license is None:
                reply_license_msg(submission, 'nolicense')
        except TypeError as t_e:
            #private/non-existent repos will flow to here
            reply_license_msg(submission, 'private')

def get_git_link(text2Search):
    # this function will only return github url with a user and repository
    # if link goes further into repo (folder or specific file) it returns None
    results = re.search('http[s]?://github.com/[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+/?', text2Search, flags=re.IGNORECASE)
    if results is not None:
        if len(re.findall('/', urlparse(results.group(0)).path)) == 2: #filters out urls inside repo
            return results.group(0)

def get_git_license(git_user, git_repo):
    # this function will return the JSON license data from Github
    # based on the supplied user and repo.
    query = "query { \
                     repository(owner:\"" + git_user + "\", name:\"" + git_repo + "\") {\
                            description \
                                licenseInfo {\
                                    id\
                                } \
                            } \
                    }"
    request = requests.post('https://api.github.com/graphql', json={'query':query}, HEADERS=HEADERS)
    return request.json()

def reply_license_msg(submission, message_type):
    # creates a message based on the message_type sent and posts as a reply.
    if message_type == 'nolicense':
        reply_template = "Good day u/" + str(submission.author) + ",\n\r   The github repository you linked does not have a license. If you need help\
        picking out a license, might I suggest https://choosealicense.com. \
        \n\r\n\r^(This is a bot, to stop receiving these automated replies, please send me a message to) \
        [^optout](https://www.REDDIT.com/message/compose?to=TeyjatttsBots&subject=optout&message=Please leave subject as optout and send this message as is.)^."
    elif message_type == 'private':
        reply_template = "Good day u/" + str(submission.author) + ",\n\r   The github repository you linked is either private or does not exist.\
        \n\r\n\r^(This is a bot, to stop receiving these automated replies, please send me a message to) \
        [^optout](https://www.REDDIT.com/message/compose?to=TeyjatttsBots&subject=!optout&message=!optout)^."
    submission.reply(reply_template)


def update_optout_file():
    for message in REDDIT.inbox.all(limit=None):
        if str(message.subject) == 'optout':
            with open('optout.json') as optout_file:
                optout_list = json.load(optout_file)
            if str(message.author) not in optout_list:
                optout_list.append(str(message.author))
                with open('optout.json', 'r+') as optout_file:
                    optout_file.write(json.dumps(optout_list))
                REDDIT.redditor(str(message.author)).message("Optout confirmation.", "This message confirms your username has been added to the optput list.")

if __name__ == '__main__':
    main()
