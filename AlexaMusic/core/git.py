import os
import shutil
import asyncio
import shlex
from typing import Tuple

from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError

import config
from ..logging import LOGGER

loop = asyncio.get_event_loop_policy().get_event_loop()

def install_req(cmd: str) -> Tuple[str, str, int, int]:
    async def install_requirements():
        args = shlex.split(cmd)
        process = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        return (
            stdout.decode("utf-8", "replace").strip(),
            stderr.decode("utf-8", "replace").strip(),
            process.returncode,
            process.pid,
        )

    return loop.run_until_complete(install_requirements())

def git():
    if not shutil.which("git"):
        LOGGER(__name__).info("Git komutu bulunamadı, güncelleme işlemi atlanıyor.")
        return

    REPO_LINK = config.UPSTREAM_REPO
    if config.GIT_TOKEN:
        GIT_USERNAME = REPO_LINK.split("com/")[1].split("/")[0]
        TEMP_REPO = REPO_LINK.split("https://")[1]
        UPSTREAM_REPO = f"https://{GIT_USERNAME}:{config.GIT_TOKEN}@{TEMP_REPO}"
    else:
        UPSTREAM_REPO = config.UPSTREAM_REPO

    try:
        repo = Repo(os.getcwd())
        LOGGER(__name__).info(f"Git Client Found [VPS DEPLOYER]")
    except (GitCommandError, InvalidGitRepositoryError):
        try:
            repo = Repo.init(os.getcwd())
            if "origin" in repo.remotes:
                origin = repo.remote("origin")
            else:
                origin = repo.create_remote("origin", UPSTREAM_REPO)
            origin.fetch()
            repo.create_head(
                config.UPSTREAM_BRANCH,
                origin.refs[config.UPSTREAM_BRANCH],
            )
            repo.heads[config.UPSTREAM_BRANCH].set_tracking_branch(
                origin.refs[config.UPSTREAM_BRANCH]
            )
            repo.heads[config.UPSTREAM_BRANCH].checkout(True)
        except Exception as e:
            LOGGER(__name__).warning(f"Git işlemi başarısız: {e}")
            return

    try:
        nrs = repo.remote("origin")
        nrs.fetch(config.UPSTREAM_BRANCH)
    except Exception as e:
        LOGGER(__name__).warning(f"Uzak repo fetch başarısız: {e}")
        return

    requirements_file = "requirements.txt"
    try:
        diff_index = repo.head.commit.diff("FETCH_HEAD")
        requirements_updated = any(
            diff.a_path == requirements_file or diff.b_path == requirements_file
            for diff in diff_index
        )
    except Exception:
        requirements_updated = False

    try:
        nrs.pull(config.UPSTREAM_BRANCH)
    except GitCommandError:
        repo.git.reset("--hard", "FETCH_HEAD")

    if requirements_updated:
        install_req("pip3 install --no-cache-dir -r requirements.txt")

    LOGGER(__name__).info(f"Güncellemeler çekildi: {REPO_LINK}")