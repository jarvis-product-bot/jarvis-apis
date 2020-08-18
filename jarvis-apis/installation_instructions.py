from config import validateToken
import json
import base64
import requests
import markdown2
from bs4 import BeautifulSoup
from dateutil.parser import parse
from datetime import datetime, timezone
from config import timebuilder



def githubCredBuilder(userdata):
    username = userdata["github_creds"]["git_username"]
    personal_token = userdata["github_creds"]["git_personal_token"]
    base64string = base64.encodestring('{}/token:{}'.format(username, personal_token).encode()).decode().replace("\n", "")
    return {"Authorization": "Basic "+base64string}


def featureDevelopmentSummary(token, projectname, issuename):
    tokenValidator = validateToken(token)
    if not tokenValidator[0]:
        return tokenValidator[1]
    data = json.loads(tokenValidator[1].to_json())
    org_name = data["github_creds"]["org_name"]
    github_creds = githubCredBuilder(data)
    issues_url = "https://api.github.com/repos/{}/{}/issues?state=all"
    issues_url = issues_url.format(org_name, projectname)
    resp = requests.get(issues_url, headers=github_creds)
    if resp.status_code != 200:
        return {
            "statusCode": 301,
            "reason": resp.json(),
            "issues_url": issues_url,
            "message": "Issues Request Failed"
        }
    for i in resp.json():
        if i["title"].lower() == issuename.lower():
            issueNumber = i["number"]
            issueData = i
    timeline_url = "https://api.github.com/repos/{}/{}/issues/{}/timeline"
    timeline_url = timeline_url.format(org_name, projectname, issueNumber)
    github_creds["Accept"] = "application/vnd.github.mockingbird-preview"
    timelineresp = requests.get(timeline_url, headers=github_creds)
    if timelineresp.status_code != 200:
        return {
            "statusCode": 301,
            "reason": timelineresp.json(),
            "timeline_url": timeline_url,
            "message": "Could not get feature timeline"
        }
    timelineresp = timelineresp.json()
    metadata_str = "This feature request was first added by {} on {} and was last updated {} {} ago. The current feature description is: {} The client has added {} extra comments on it."
    a, b = timebuilder(
        (
            datetime.now(timezone.utc) - parse(issueData["updated_at"])
        ).seconds
    )
    metadata_str = metadata_str.format(
        issueData["user"]["login"],
        parse(issueData["created_at"]).strftime("%I:%M %p %d %B, %Y"),
        a,
        b,
        issueData["body"],
        issueData["comments"]
    )
    if issueData["comments"] != 0:
        comments_url = "https://api.github.com/repos/{}/{}/issues/{}/comments"
        comments_url = comments_url.format(org_name, projectname, issueNumber)
        resp = requests.get(comments_url, headers={"Authorization": github_creds["Authorization"]})
        if resp.status_code == 200 and len(resp.json()) >= 1:
            comment_data = "The most recent comment by the customer is: " + resp.json()[-1]["body"][: 150]
            metadata_str += comment_data
    restr_timeline = []
    for i in timelineresp:
        if i["event"] in ["closed", "labeled", "milestoned", "closed", "reopened", "referenced", "assigned", "commented"]:
            i["created_at"] = parse(i["created_at"]).strftime("%I:%M %p %d %B, %Y")
            i["actor"] = i["actor"]["login"]
            restr_timeline.append(i)
    changehistory_str = "Now we will begin with the detailed change history of the feature timeline. "
    changehistory_str = ""
    for i in restr_timeline:
        if i == restr_timeline[0]:
            content = "Firstly, "
        elif i == restr_timeline[-1]:
            content = "Lastly, "
        else:
            content = "Then, "
        if i["event"] == "labeled":
            content += "a label {} was added on the feature request by {} on {}. ".format(i["label"]["name"], i["actor"], i["created_at"])
        elif i["event"] == "milestoned":
            content += "this feature request {} was added by {} on {}. ".format(i["milestone"]["title"], i["actor"], i["created_at"])
        elif i["event"] == "closed":
            content += "this feature request was closed by {} on {}. ".format(i["actor"], i["created_at"])
        elif i["event"] == "reopened":
            content += "this feature request was reopened by {} on {}. ".format(i["actor"], i["created_at"])
        elif i["event"] == "assigned":
            content += "this feature request was assigned to {} by {} on {}. ".format(i["assignee"]["login"], i["actor"], i["created_at"])
        elif i["event"] == "referenced":
            content += "this feature request was referenced by {} via commit id {} on {}. ".format(i["actor"], i["commit_id"], i["created_at"])
        elif i["event"] == "commented":
            content += "this feature request was commented on by {} at {}. He said that {}".format(i["actor"], i["created_at"], i["body"])
        changehistory_str += content
    
    return {
        "statusCode": 200,
        "change_history": changehistory_str,
        "metadata_string": metadata_str 
    }


def projectreleasestatus(token, projectname):
    tokenValidator = validateToken(token)
    if not tokenValidator[0]:
        return tokenValidator[1]
    data = json.loads(tokenValidator[1].to_json())
    org_name = data["github_creds"]["org_name"]
    milestone_url = "https://api.github.com/repos/{}/{}/milestones?sort=due_on"
    milestone_url = milestone_url.format(org_name, projectname)
    github_creds = githubCredBuilder(data)
    resp = requests.get(milestone_url, headers=github_creds)
    if resp.status_code != 200:
        return {
            "statusCode": 301,
            "reason": resp.json(),
            "message": "Milestone Request Failed"
        }
    resp = resp.json()
    if len(resp)<1:
        return {
            "statusCode": 301,
            "message": "No Milestone Found"
        }
    milestone = resp[0]
    issues_url = "https://api.github.com/repos/{}/{}/issues?state=all&labels=urgent&milestone={}"
    issues_url = issues_url.format(org_name, projectname, milestone["number"])
    resp = requests.get(issues_url, headers=github_creds)
    if resp.status_code != 200:
        return {
            "statusCode": 301,
            "reason": resp.json(),
            "message": "Milestone Request Failed"
        }
    milestone["urgent_issues"] = resp.json()
    return {
        "statusCode":200,
        "milestone": milestone
    }


def listgitrepos(token):
    tokenValidator = validateToken(token)
    if not tokenValidator[0]:
        return tokenValidator[1]
    data = json.loads(tokenValidator[1].to_json())
    org_name = data["github_creds"]["org_name"]
    url = "https://api.github.com/orgs/{}/repos".format(org_name)
    resp = requests.get(url, headers=githubCredBuilder(data))
    if resp.status_code != 200:
        return {
            "statusCode": 301,
            "reason": resp.json(),
            "message": "Repository Request Failed"
        }
    else:
        data = resp.json()
        reponames = []
        for i in data:
            reponames.append({"name": i["name"]}) 
        data = {
            "statusCode": 200,
            "data": reponames
        }
        return data
    

def helpwithinstallation(token, projectname, needDocker=False, OS="ubuntu"):
    tokenValidator = validateToken(token)
    if not tokenValidator[0]:
        return tokenValidator[1]
    data = json.loads(tokenValidator[1].to_json())
    org_name = data["github_creds"]["org_name"]
    url = "https://raw.githubusercontent.com/{}/{}/master/README.md".format(
        org_name, projectname
    )
    resp = requests.get(url)
    if resp.status_code != 200:
        return {
            "statusCode": 200, 
            "message": "I am extremely sorry but no installation instructions were found on your repository. You are on your own for this one."
        }
    resp = resp.text
    soup = BeautifulSoup(
        markdown2.markdown(resp), 
        "html.parser"
    )
    instrSet = {}
    for i in soup.find_all("code"):
        instructions = i.get_text()
        print(instructions, type(instructions))
        if instructions[0:4] == "bash":
            if instructions.find("apt") != -1:
                instrSet["ubuntu"] = instructions[5:].strip().split("\n")
            elif instructions.find("yum"):
                instrSet["redhat"] = instructions[5:].strip().split("\n")
        elif instructions[0:6] == "shell":
            instrSet["windows"] = instructions[7:].strip().split("\n")
        else:
            instrSet["macos"] = instructions[7:].strip().split("\n")
    if instrSet == {}:
        return {
            "statusCode": 200, 
            "message": "I am extremely sorry but no installation instructions were found on your repository. You are on your own for this one."
        }
    if not needDocker:
        return {
            "statusCode": 200,
            "instructions": instrSet.get(
                OS, 
                "Sorry this software doesn't install on your OS"
            )
        }
    dockerFile = """
        # Pull base image.
        FROM ubuntu:18.04

        # Install.
        RUN \
        sed -i 's/# \(.*multiverse$\)/\1/g' /etc/apt/sources.list && \
        apt-get update && \
        apt-get -y upgrade && \
        apt-get install -y build-essential && \
        apt-get install -y software-properties-common && \
        apt-get install -y byobu curl git htop man unzip vim wget && \
        rm -rf /var/lib/apt/lists/* && \ {}

        # Add files.
        ADD root/.bashrc /root/.bashrc
        ADD root/.gitconfig /root/.gitconfig
        ADD root/.scripts /root/.scripts

        # Set environment variables.
        ENV HOME /root

        # Define working directory.
        WORKDIR /root

        # Define default command.
        CMD ["bash"]
    """.format("&&\\\n".join(i for i in instrSet["ubuntu"]))
    return mailInstallationInstructions(dockerFile,data["email"])

def mailInstallationInstructions(dataToMail, email):
    # TODO Actually send the mail
    # email_username = environ.get('username')
    # email_password = environ.get('password')
    return {
        "statusCode": 200, 
        "message": "A docker file with relevant instructions has been compiled and sent to your email, please read it and use docker to run the file on your server."
    }   