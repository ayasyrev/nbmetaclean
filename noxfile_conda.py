import nox

nox.options.default_venv_backend = "mamba|conda"
nox.options.reuse_existing_virtualenvs = True


@nox.session(python=["3.8", "3.9", "3.10", "3.11", "3.12"])
def conda_tests(session: nox.Session) -> None:
    args = session.posargs or ["--cov"]
    session.conda_install("uv")
    session.run("uv", "pip", "install", "-e", ".[test]")
    session.run("pytest", *args)
