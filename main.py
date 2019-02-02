import requests
import os
import shlex
from subprocess import run, DEVNULL
from dotenv import load_dotenv

load_dotenv()

HEADERS = {'Private-Token': os.getenv('PRIVATE_TOKEN')}
GROUP_PATH = os.getenv('GROUP_PATH')
MIRROR_DIR = os.getenv('MIRROR_DIR')


def get_subgroups(group):
    url = 'https://gitlab.com/api/v4/groups/%s/subgroups' % group

    for subgroup in requests.get(url, headers=HEADERS).json():
        yield subgroup['full_path']


def get_projects(group):
    url = 'https://gitlab.com/api/v4/groups/%s/projects' % group

    for project in requests.get(url, headers=HEADERS).json():
        yield {
            'path': project['path_with_namespace'],
            'repo': project['ssh_url_to_repo'],
        }


def git_mirror(project):
    path = '%s/%s' % (MIRROR_DIR, project['path'])

    if os.path.exists(path):
        print('git remote update: %s' % project['path'])
        cmd = shlex.split('git remote update')
        run(cmd, cwd=path, stderr=DEVNULL, stdout=DEVNULL)
    else:
        print('git clone: %s' % project['path'])
        cmd = shlex.split('git clone --mirror %s %s' % (project['repo'],  path))
        run(cmd, stderr=DEVNULL, stdout=DEVNULL)


def go(group):
    print('process group: %s' % group)
    group = group.replace('/', '%2F')

    for project in get_projects(group):
        git_mirror(project)

    for subgroup in get_subgroups(group):
        go(subgroup)


go(GROUP_PATH)
