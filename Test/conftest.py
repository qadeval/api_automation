import base64
import json

import pytest
import requests


def pytest_addoption(parser):
    parser.addoption(
        "--xray-client-id",
        action="store",
        default="8FDF6ABBBC11424083A39B7538FFE6DE",
        help="Xray client ID",
    )
    parser.addoption(
        "--xray-client-secret",
        action="store",
        default="d8a6a4043dcbed5a24a8a538fc911e8d724ca0d9c4d6fe701b918ac8b4f9fc41",
        help="Xray client secret",
    )
    parser.addoption(
        "--xray-base-url",
        action="store",
        default="https://xray.cloud.getxray.app",
        help="Xray base URL",
    )
    parser.addoption(
        "--jira-username",
        action="store",
        default = "devalth8@gmail.com",
        # default=                           os.environ.get("JIRA_USERNAME", ""),
        help="Jira username",
    )
    parser.addoption(
        "--jira-password",
        action="store",
        default='ATATT3xFfGF0XIEet5A85uJfOoI6dHKBpqy5cSLoN4QHQmtIJTGzlYsEsqdFL9A1wg9E3ObwmpbfZlGysYgE0lBj1zF7x1nJfmhO90q5QUOdNMn4H7qpnTJiXbw1sUaPHhf0eSBgpgthFSlcUUdrJGhnHM6V44zLeQPQdxdFRmlBuodVP7aNFjU=3F6ADBB1',
        help="Jira password",
    )
    parser.addoption(
        "--jira-base-url",
        action="store",
        default='https://devalth8.atlassian.net/',
        help="Jira base URL",
    )

@pytest.fixture(scope="session")
def xray_credentials(request):
    client_id = request.config.getoption("--xray-client-id")
    client_secret = request.config.getoption("--xray-client-secret")
    base_url = request.config.getoption("--xray-base-url")

    return {
        "client_id": client_id,
        "client_secret": client_secret,
        "base_url": base_url,
    }


@pytest.fixture(scope="session")
def jira_credentials(request):
    username = request.config.getoption("--jira-username")
    password = request.config.getoption("--jira-password")
    base_url = request.config.getoption("--jira-base-url")
    
    return {
        "username": username,
        "password": password,
        "base_url": base_url,
    }


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    xray_credentials = item._request.getfixturevalue('xray_credentials')
    jira_credentials = item._request.getfixturevalue('jira_credentials')
    outcome = yield
    rep = outcome.get_result()
    
    # Check if the test passed or failed
    if rep.passed:
        xray_test_status = "PASS"
        jira_status = "Done"
        jira_transition_id = 123  # ID of the "Done" transition in your Jira instance
        jira_comment = "This issue was updated by an automated test"
    else:
        xray_test_status = "FAIL"
        jira_issue_type = "Bug"
        jira_issue_status = "Open"
        jira_comment = "This issue was created by an automated test"
        
        # Define the Jira project key and issue type ID to create the issue
        jira_project_key = "REAL"
        jira_issue_type_id = 123  # ID of the "Bug" issue type in your Jira instance
        
        # Define the URL to the Jira REST API to create the issue
        jira_issue_create_url = f"{jira_credentials['base_url']}/rest/api/2/issue/"
        
        # Define the Jira issue create payload
        jira_issue_create_payload = {
            "fields": {
                "project": {
                    "key": jira_project_key
                },
                "issuetype": {
                    "id": jira_issue_type_id
                },
                "summary": "Automated test failure",
                "description": "This issue was created by an automated test",
                "priority": {
                    "name": "High"
                },
                "labels": ["automated-test"]
            }
        }

        # Set up the authentication headers for the Jira REST API
        jira_auth_headers = {
            "Authorization": f"Basic {base64.b64encode((jira_credentials['username'] + ':' + jira_credentials['password']).encode()).decode()}",
            "Content-Type": "application/json"
        }

        # Create the Jira issue
        response = requests.post(jira_issue_create_url, headers=jira_auth_headers,
                                 data=json.dumps(jira_issue_create_payload))
        response.raise_for_status()

        # Get the issue key from the response
        jira_issue_key = response.json()["key"]

        # Define the URL to the Jira REST API to add a comment to the issue
        jira_comment_url = f"{jira_credentials['base_url']}/rest/api/2/issue/{jira_issue_key}/comment"

        # Define the Jira comment payload
        jira_comment_payload = {
            "body": jira_comment
        }

        # Add a comment to the Jira issue
        response = requests.post(jira_comment_url, headers=jira_auth_headers, data=json.dumps(jira_comment_payload))
        response.raise_for_status()

        # Define the Jira transition ID to move the issue to the "In Progress" status
        jira_transition_id = 456  # ID of the "In Progress" transition in your Jira instance

        # Define the URL to the Jira REST API to update the issue
        jira_issue_url = f"{jira_credentials['base_url']}/rest/api/2/issue/{jira_issue_key}/transitions"

        # Define the Jira transition payload
        jira_transition_payload = {
            "transition": {
                "id": jira_transition_id
            }
        }

        # Update the Jira issue
        response = requests.post(jira_issue_url, headers=jira_auth_headers, data=json.dumps(jira_transition_payload))
        response.raise_for_status()

    # Update the Xray test status and the corresponding Xray test case and test execution
    xray_test_execution_key = "REAL-20"
    xray_test_case_key = "REAL-19"
    xray_test_case_url = f"{xray_credentials['base_url']}/rest/raven/1.0/api/test/{xray_test_case_key}/status"
    

    xray_credentials_dict = xray_credentials
    xray_test_execution_url = f"{xray_credentials['base_url']}/rest/raven/1.0/api/testexec/{xray_test_execution_key}/test"

    xray_auth_headers = {
        "Authorization": f"Basic {base64.b64encode((xray_credentials['client_id'] + ':' + xray_credentials['client_secret']).encode()).decode()}",
        "Content-Type": "application/json"
    }

    xray_test_status_payload = {
        "status": xray_test_status
    }

    response = requests.put(xray_test_execution_url, headers=xray_auth_headers,
                            data=json.dumps(xray_test_status_payload))
    response.raise_for_status()

    response = requests.put(xray_test_case_url, headers=xray_auth_headers, data=json.dumps(xray_test_status_payload))
    response.raise_for_status()

