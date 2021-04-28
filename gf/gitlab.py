import typer
import re
import urllib
from typing import Optional
from configparser import NoOptionError, NoSectionError
from .utils import repo, Conf
from .dialog import conf_dialog
import requests

app = typer.Typer(help='Interact with gitlab by accessing gitlab-api')
conf = Conf()


@app.command()
def config():
    conf = Conf()
    try:
        conf.host, conf.version, conf.token = conf_dialog(host=conf.host, version=conf.version, token=conf.token)
    except TypeError:
        pass


@app.command(name='mr')
def merge_request():
    headers = {"Private-Token": Conf().token}
    pid = get_project_id()
    url = f'{conf.host}/api/{conf.version}/projects/{pid}/merge_requests'
    data = {
        'source_branch': repo.head.reference.name,
        'target_branch': 'master',
        'title': 'test api merge request'
    }
    resp = requests.post(url, headers=headers, json=data)
    if resp.ok:
        typer.echo('Merge request has been successfully submitted')
    else:
        typer.echo('Merge request failed')
        typer.echo(resp.content)


def get_project_id():
    remote = repo.remote()
    # todo 多个远端仓库
    url = next(remote.urls)
    project_name = re.match('.*:(.*).git', url).groups()[0]
    project_name = urllib.parse.quote(project_name, 'utf-8')
    conf = Conf()
    headers = {"Private-Token": conf.token}
    project_id = requests.get(f'{conf.host}/api/{conf.version}/projects/{project_name}', headers=headers)

    return project_id.json().get('id')












