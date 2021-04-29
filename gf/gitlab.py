import typer
import re
import urllib
from .utils import repo, Conf
from .dialog import conf_dialog
import requests

app = typer.Typer(help='Interact with gitlab by accessing gitlab-api')
conf = Conf()


# @app.command()
def config():
    """ configuration for accessing gitlab-api\n
    host : gitlab host info.  example: https://gitlab.com\n
    version : gitlab api version.  example: [v1 | v2 | v3 | v4]\n
    token : gitlab private token. example: 679Pqw11v739pqfy2jRg
    """
    try:
        conf.host, conf.version, conf.token = conf_dialog(host=conf.host, version=conf.version, token=conf.token)
    except TypeError:
        typer.Abort()


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


@app.callback()
def check_config(verbose: bool = False):
    """
    Manage users in the awesome CLI app.
    """
    if conf.token == 'example_token':
        typer.echo('Need gitlab configuration !')
        config()















