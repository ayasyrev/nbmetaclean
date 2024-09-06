import nox


nox.options.default_venv_backend = "uv|virtualenv"
nox.options.reuse_existing_virtualenvs = True


@nox.session(python=["3.8", "3.9", "3.10", "3.11", "3.12"])
def tests(session: nox.Session) -> None:
    args = session.posargs or ["--cov"]
    session.install("-e", ".[test]")
    session.run("pytest", *args)
