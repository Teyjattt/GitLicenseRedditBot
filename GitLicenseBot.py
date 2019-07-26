import praw, requests, json, re
from urllib.parse import urlparse
from urllib.parse import quote_plus

#####################################################
redditsToFollow = 'testingground4bots'
reddit = praw.Reddit('GitLicenseBot')
subreddit = reddit.subreddit(redditsToFollow)
headers = {'Authorization': 'Token 123456789012345678901234567890'}   #for github api

def main():
    updateOptoutFile()
    with open('optout.json') as optoutFile:
        optoutList = json.load(optoutFile)
    
    for submission in subreddit.stream.submissions(skip_existing=True):
        ############################################
        #look for github url if users did not optout
        if str(submission.author) not in optoutList:
            gitLink = getGitLink(submission.url + ' ' + submission.selftext)
        else:
            continue    #continue to next submission because user optedout
        if gitLink == None:
            continue    #no github url was found, or url does not point to main repo
        #################################
        #parse out user and repo from url
        gitParts = urlparse(gitLink).path.split('/')
        gitUser = gitParts[1]
        gitRepo = gitParts[2]
        ###############################
        # pull license data from Github
        try:
            gitLicense = (getGitLicense(gitUser, gitRepo))['data']['repository']['licenseInfo']
            if gitLicense == None:
                replyLicenseMsg(submission, 'nolicense')
        except TypeError as te:
            #private/non-existent repos will flow to here
            replyLicenseMsg(submission, 'private')

def getGitLink (text2Search):
    # this function will only return github url with a user and repository
    # if link goes further into repo (folder or specific file) it returns None
    results = re.search('http[s]?://github.com/[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+/?', text2Search, flags=re.IGNORECASE)
    if results != None:
        if len(re.findall('/',urlparse(results.group(0)).path)) == 2: #filters out urls inside repo
            return results.group(0)
        else:
            return None
    else:
        return None

def getGitLicense (gitUser, gitRepo):
    # this function will return the JSON license data from Github
    # based on the supplied user and repo.
    query = "query { \
                     repository(owner:\"" + gitUser + "\", name:\"" + gitRepo + "\") {\
                            description \
                                licenseInfo {\
                                    id\
                                } \
                            } \
                    }"
    request = requests.post('https://api.github.com/graphql', json={'query':query}, headers=headers)
    return request.json()

def replyLicenseMsg(submission, messageType):
    # creates a message based on the messageType sent and posts as a reply.
    if messageType == 'nolicense':
        replyTemplate = "Good day u/" + str(submission.author) + ",\n\r   The github repository you linked does not have a license. If you need help\
        picking out a license, might I suggest https://choosealicense.com. \
        \n\r\n\r^This ^is ^a ^bot, ^to ^stop ^receiving ^these ^automated ^replies, ^please ^send ^me ^a ^message ^to \
        [^optout](https://www.reddit.com/message/compose?to=TeyjatttsBots&subject=optout&message=Please leave subject as optout and send this message as is.)^."
    elif messageType == 'private':
        replyTemplate = "Good day u/" + str(submission.author) + ",\n\r   The github repository you linked is either private or does not exist.\
        \n\r\n\r^This ^is ^a ^bot, ^to ^stop ^receiving ^these ^automated ^replies, ^please ^send ^me ^a ^message ^to \
        [^optout](https://www.reddit.com/message/compose?to=TeyjatttsBots&subject=!optout&message=!optout)^."
    submission.reply(replyTemplate)


def updateOptoutFile():
    for message in reddit.inbox.all(limit=None):
        if str(message.subject) == 'optout':
            with open('optout.json') as optoutFile:
                optoutList = json.load(optoutFile)
            if str(message.author) not in optoutList:
                optoutList.append(str(message.author))
                with open('optout.json','r+') as optoutFile:
                    optoutFile.write(json.dumps(optoutList))
                reddit.redditor(str(message.author)).message("Optout confirmation.","This message confirms your username has been added to the optput list.")

if __name__ == '__main__':
    main()
    
