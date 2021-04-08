"""Macros and filters made available in Markdown pages."""

import re
from itertools import chain
from pathlib import Path

import toml
from pip._internal.commands.show import search_packages_info  # noqa: WPS436 (no other way?)


def get_credits_data() -> dict:
    """
    Return data used to generate the credits file.

    Returns:
        Data required to render the credits template.
    """
    project_dir = Path(__file__).parent.parent
    metadata = toml.load(project_dir / "pyproject.toml")["project"]
    metadata_pdm = toml.load(project_dir / "pyproject.toml")["tool"]["pdm"]
    lock_data = toml.load(project_dir / "pdm.lock")
    project_name = metadata["name"]

    all_dependencies = chain(
        metadata.get("dependencies", []),
        chain(*metadata.get("optional-dependencies", {}).values()),
        chain(*metadata_pdm.get("dev-dependencies", {}).values()),
    )
    direct_dependencies = {re.sub(r"[^\w-].*$", "", dep) for dep in all_dependencies}
    direct_dependencies = {dep.lower() for dep in direct_dependencies}
    indirect_dependencies = {pkg["name"].lower() for pkg in lock_data["package"]}
    indirect_dependencies -= direct_dependencies

    packages = {}
    for pkg in search_packages_info(direct_dependencies | indirect_dependencies):
        pkg = {_: pkg[_] for _ in ("name", "home-page")}
        packages[pkg["name"].lower()] = pkg

    # all packages might not be credited,
    # like the ones that are now part of the standard library
    # or the ones that are only used on other operating systems,
    # and therefore are not installed,
    # but it's not that important

    return {
        "project_name": project_name,
        "direct_dependencies": sorted(direct_dependencies),
        "indirect_dependencies": sorted(indirect_dependencies),
        "package_info": packages,
    }


def define_env(env):
    """
    Add macros and filters into the Jinja2 environment.

    This hook is called by `mkdocs-macros-plugin`
    when building the documentation.

    Arguments:
        env: An object used to add macros and filters to the environment.
    """
    env.variables.update(get_credits_data())

    @env.macro  # noqa: WPS430
    def cite_package(info, name):  # noqa: WPS430
        package = info.get(name, {})
        return f"[`{package.get('name', name)}`]({package.get('home-page', '')})"

    @env.macro  # noqa: WPS430
    def cite_packages(info, names):  # noqa: WPS430
        return " | ".join(cite_package(info, name) for name in names)
