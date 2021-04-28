import os
import re
import git
import random
import string
import base64
import typer
from git.exc import GitCommandError, InvalidGitRepositoryError


def get_repo():
    try:
        ret = git.Repo()
    except InvalidGitRepositoryError as e:
        typer.secho(f'not a git repository: {e}', fg=typer.colors.RED)
        os._exit(0)
    else:
        return ret
    

repo= get_repo()


def no_traceback(f):
    """block out python traceback message"""
    def _wapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except GitCommandError as e:
            # typer.echo(e)
            raise typer.Exit(e)
    return _wapper


def get_create_date(branch_name: str):
    """Get branch creation time"""
    txt = repo.git.reflog(branch_name, date='short')
    try:
        dates = re.findall('{[\d-]+}', txt)
        return dates[-1].strip('{}')
    except IndexError:
        return ''


def encrypt(s: string):
    """对token进行简单加密"""
    salt = ''.join(random.sample(string.ascii_letters+string.digits, 6))
    token = base64.b64encode(bytes(salt[:3]+s+salt[-3:], encoding='utf-8'))
    return token


def decrypt(s: bytes):
    """加密token"""
    return base64.b64decode(s)[3:-3].decode('utf-8')


class Conf:
    def __init__(self):
        pass

    @property
    def token(self):
        token = repo.config_reader('global').get('gitlab', option='token')
        # token = decrypt(token)
        return token

    @token.setter
    def token(self, value):
        # token = encrypt(value)
        repo.config_writer('global').set_value('gitlab', 'token', value).release()

    @property
    def host(self):
        return repo.config_reader('global').get('gitlab', option='host')

    @host.setter
    def host(self, value):
        repo.config_writer('global').set_value('gitlab', 'host', value).release()

    @property
    def version(self):
        return repo.config_reader('global').get('gitlab', option='version')

    @version.setter
    def version(self, value):
        repo.config_writer('global').set_value('gitlab', 'version', value).release()