import nox

locations = "."
nox.options.default_venv_backend = "uv|virtualenv"
nox.options.reuse_existing_virtualenvs = True


@nox.session(python=["3.8", "3.9", "3.10", "3.11", "3.12"])
def lint(session: nox.Session) -> None:
    args = session.posargs or locations
    session.install("ruff")
    session.run("ruff", "check", *args)
