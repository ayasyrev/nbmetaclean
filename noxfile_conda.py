import nox


@nox.session(python=["3.8", "3.9", "3.10", "3.11", "3.12"], venv_backend="mamba")
def conda_tests(session: nox.Session) -> None:
    args = session.posargs or ["--cov"]
    session.conda_install("uv")
    session.run("uv", "pip", "install", ".[test]")
    session.run("pytest", *args)
