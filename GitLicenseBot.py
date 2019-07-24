import praw, requests, json, re
from urllib.parse import urlparse

#####################################################
redditsToFollow = 'python'

def getGitLink (author, text2Search):
    # this function will only return github url with a user and repo
    # if link goes further into repo (folder or specific file) it returns None
    #
    # 2DO: check to see if author is in blacklist
    results = re.search('http[s]?://github.com/[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+/?', text2Search, flags=re.IGNORECASE)
    if results != None:
        if len(re.findall('/',urlparse(results.group(0)).path)) == 2: #filters out urls inside repo
            return results.group(0)
        else:
            return None
    else:
        return None

def getGitLicense (gitUser, gitRepo):
    # this function will return the JSON license data from Github based on the supplied
    # user and repo.
    #
    # 2DO: possibly pull back additional information to include in message
    query = "query { \
                     repository(owner:\"" + gitUser + "\", name:\"" + gitRepo + "\") {\
                            description \
                                licenseInfo {\
                                id\
                                } \
                            } \
                    }"
    request = requests.post('https://api.github.com/graphql', json={'query':query}, headers=headers)
    #2DO: test for failed request
    return request.json()

# create subreddit object and directory if one doesn't exist
reddit = praw.Reddit('GitLicenseBot')
subreddit = reddit.subreddit(redditsToFollow)
# 2DO: can token be pulled from ini file like Praw data?
headers = {'Authorization': 'Token 123456789012345678901234567890'}   #for github api


testuser = 'freeezer98'
testrep = 'export-archive-reddit-saved'
gitLicense = (getGitLicense(testuser, testrep))['data']['repository']['licenseInfo']
if gitLicense == None:
    #do something here to post to submission
    print('nothing found')
else:
    print("License exists:",gitLicense['id'])
print("-----------------")

#for submission in subreddit.stream.submissions(skip_existing=True):
for submission in subreddit.new(limit=100):
    ####################
    #look for github url
    gitLink = getGitLink("me", submission.selftext + submission.url)
    if gitLink == None:
        continue    #no github url was found, or url does not point to main repo
    #################################
    #parse out user and repo from url
    #MAYBE?: check to see if repo is in blacklist
    gitParts = urlparse(gitLink).path.split('/')
    gitUser = gitParts[1]
    gitRepo = gitParts[2]
    ###############################
    # pull license data from Github
    gitLicense = (getGitLicense(gitUser, gitRepo))['data']['repository']['licenseInfo']
    if gitLicense == None:
        #do something here to post to submission
        print('nothing found')
    else:
        print("License exists:",gitLicense['id'])
 #   print (gitLicense['data']['repository']['licenseInfo'])
 
#
input("Press Enter to continue...")
