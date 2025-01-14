import argparse
from os import path
from typing import Any, Dict, List, Union

from tealprint import TealPrint

from ..config import config
from ..core.entities.actions import Actions
from ..core.entities.mod import ModArg
from ..core.entities.sites import Site, Sites
from ..utils.log_colors import LogColors


def parse_args():
    parser = argparse.ArgumentParser(description="Install or update Minecraft mods from Modrinth and CurseForge")

    parser.add_argument(
        "action",
        choices=Actions.get_all_names_as_list(),
        help="What you want to do. version prints the version of this application",
    )
    parser.add_argument(
        "mods",
        nargs="*",
        help="The mods to install, update, or configure. "
        + "If no mods are specified during an update, all mods will be updated. "
        + "To specify the download site for the mod you can put '=site' after the mod. "
        + "E.g. 'litematica=curse'. By default it searches all sites for the mod. "
        + "To configure an slug for the mod, use 'mod_name=curse:SLUG'. E.g. 'dynmap=curse:dynmapforge' "
        + "To reset configuration, type 'mod_name='. To specify multiple sites add a comma between site names. "
        + "E.g. 'dynmap=curse,modrinth' or 'dynmap=curse:dynmapforge,modrinth' if you want to have different slugs",
    )
    parser.add_argument(
        "-d",
        "--dir",
        type=_is_dir,
        help="Location of the mods folder. By default it's the current directory",
    )
    parser.add_argument(
        "-v",
        "--minecraft-version",
        help="Only update mods to this Minecraft version",
    )
    parser.add_argument(
        "--beta",
        action="store_true",
        help="Allow beta releases of mods",
    )
    parser.add_argument(
        "--alpha",
        action="store_true",
        help="Allow alpha and beta releases of mods",
    )
    parser.add_argument(
        "--mod-loader",
        choices=["fabric", "forge"],
        help="Only install mods that use this mod loader. "
        + "You rarely need to be this specific. "
        + "The application figures out for itself which type you'll likely want to install.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print more messages",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Turn on debug messages. This automatically turns on --verbose as well",
    )
    parser.add_argument(
        "--pretend",
        action="store_true",
        help="Only pretend to install/update/configure. Does not change anything",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"{config.app_name}: {config.app_version}",
        help="Show application version",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable color output",
    )

    args = parser.parse_args()
    args.action = Actions.from_name(args.action)
    args.mods = _parse_mods(args.mods)
    return args


def _parse_mods(args_mod: Any) -> List[ModArg]:
    mods: List[ModArg] = []
    for mod_arg in args_mod:
        mod_arg = str(mod_arg)
        mod = ModArg("")
        if "=" in mod_arg:
            if mod_arg.count("=") > 1:
                _print_invalid_mod_syntax(mod_arg, "Too many equal signs '=' in argument")
            mod.id, sites = mod_arg.split("=")
            mod.sites = _parse_sites(mod_arg, sites)
        else:
            mod.id = mod_arg
        mods.append(mod)

    return mods


def _parse_sites(mod_arg, sites: str) -> Dict[Sites, Site]:
    sites_str = sites.split(",") if "," in sites else [sites]
    sites_dict: Dict[Sites, Site] = {}
    for site_str in sites_str:
        if site := _parse_site(mod_arg, site_str):
            sites_dict[site.name] = site
    return sites_dict


def _parse_site(mod_arg: str, site_str: str) -> Union[Site, None]:
    if not site_str:
        return None

    slug: Union[str, None] = None
    name_str: str = ""

    # Slug
    if ":" in site_str:
        if site_str.count(":") > 1:
            _print_invalid_mod_syntax(mod_arg, "Too many colon signs ':' in argument")
        name_str, slug = site_str.split(":")
    else:
        name_str = site_str

    try:
        name = Sites[name_str]
        return Site(name, slug=slug)
    except KeyError:
        _print_invalid_mod_syntax(mod_arg, f"Invalid site, valid sites are {Sites.all()}")
        return None


def _print_invalid_mod_syntax(mod_arg: str, extra_info: str) -> None:
    TealPrint.error(f"Invalid mod syntax: {mod_arg}")
    TealPrint.error(extra_info)
    TealPrint.error(
        f"Valid syntax is: {LogColors.command}dynmap=curse{LogColors.no_color}, "
        + f"{LogColors.command}dynmap=curse:dynmapforge{LogColors.no_color}, or "
        + f"{LogColors.command}dynmap=modrinth,curse:dynmapforge{LogColors.no_color}",
        exit=True,
    )


def _is_dir(dir: str) -> str:
    if path.isdir(dir):
        return dir
    else:
        raise NotADirectoryError(dir)
