from flask import Flask, request, abort
from requests import get, post

app = Flask(__name__)

OPSGENIE_API_KEY = "******"
OPSGENIE_API_URL = "https://api.opsgenie.com/"
OPSGENIE_WHOIS_ON_CALL_PATH = "v2/schedules/%s/on-calls"
GENIE_KEY = "GenieKey %s"
SLACK_API = "https://slack.com/api/"
SLACK_USERS_LIST = "users.list"
SLACK_USERGROUP_UPDATE = "usergroups.users.update"
SLACK_USERGROUP_LIST = "usergroups.users.list"
SLACK_TOKEN = "******"
BEARER = "Bearer %s"


def update_slack_team(team, user_id):
    headers, payload = {}, {}
    headers['Content-Type'] = 'application/json'
    headers['Authorization'] = BEARER % (SLACK_TOKEN)
    payload['usergroup'] = team
    payload['users'] = user_id
    response = post(url=SLACK_API+SLACK_USERGROUP_UPDATE, json=payload, headers=headers)
    if response.status_code > 399:
        return False
    return True

def find_user_id(slack_users, on_call_mail):
    for user in slack_users:
        profile = user['profile']
        if on_call_mail == profile['email']:
            return user['id']
    return "User not found"

def get_slack_user_list():
    headers, params = {}, {}
    headers['Content-Type'] = "application/x-www-form-urlencoded"
    params['token'] = SLACK_TOKEN
    return get(url=SLACK_API+SLACK_USERS_LIST, params=params, headers=headers).json()['members']

def get_who_is_on_call(schedule):
    headers, params = {}, {}
    params['scheduleIdentifierType'] = 'name'
    params['flat'] = 'true'
    headers['Authorization'] = GENIE_KEY % (OPSGENIE_API_KEY)
    response = get(url=OPSGENIE_API_URL+OPSGENIE_WHOIS_ON_CALL_PATH%(schedule), params=params, headers=headers).json()
    data = response['data']
    return data['onCallRecipients'][0]

@app.route('/', methods=['POST'])
def update_slack_team_with_opsgenie_oncall_api():
    if request.method == 'POST':
        data = request.get_json(force=True)
        usergroup_id = data['user-group']
        schedule = data['schedule']
        on_call = get_who_is_on_call(schedule=schedule)
        users = get_slack_user_list()
        user_id = find_user_id(slack_users=users, on_call_mail=on_call)
        if user_id == 'User not found':
            abort(406)
        update_slack_team(team=usergroup_id, user_id=user_id)
        print (usergroup_id, schedule)
    else:
        error = 'Wrong method'
    return "Tamam Yaparim"


if __name__ == '__main__':
    app.run()
