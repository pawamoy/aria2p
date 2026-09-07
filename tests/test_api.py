"""Tests for the `api` module and our public API."""

from __future__ import annotations

import threading
import time
from collections import defaultdict
from pathlib import Path
from typing import TYPE_CHECKING

import griffe
import pytest
from mkdocstrings import Inventory

import aria2p
from aria2p import API, Client, ClientException, Download
from tests import BUNSENLABS_MAGNET, BUNSENLABS_TORRENT, CONFIGS_DIR, DEBIAN_METALINK, INPUT_FILES, XUBUNTU_MIRRORS
from tests.conftest import Aria2Server

if TYPE_CHECKING:
    from collections.abc import Iterator


def test_add_magnet_method(server: Aria2Server) -> None:
    assert server.api.add_magnet(BUNSENLABS_MAGNET)


def test_add_metalink_method(server: Aria2Server) -> None:
    assert server.api.add_metalink(DEBIAN_METALINK)


def test_add_torrent_method(server: Aria2Server) -> None:
    assert server.api.add_torrent(BUNSENLABS_TORRENT)


def test_add_uris_method(server: Aria2Server) -> None:
    assert server.api.add_uris(XUBUNTU_MIRRORS)


def test_get_download_method(tmp_path: Path, port: int) -> None:
    with Aria2Server(tmp_path, port, session="1-dl-paused.txt") as server:
        assert server.api.get_download("0000000000000001")  # == server.api.get_downloads()[0].gid


def test_get_downloads_method(tmp_path: Path, port: int) -> None:
    with Aria2Server(tmp_path, port, session="2-dls.txt") as server:
        downloads = server.api.get_downloads()
        assert len(downloads) == 2
        assert isinstance(downloads[0], Download)
        assert downloads[0].gid == "0000000000000001"


def test_get_global_options_method(tmp_path: Path, port: int) -> None:
    with Aria2Server(tmp_path, port, config=CONFIGS_DIR / "max-5-dls.conf") as server:
        options = server.api.get_global_options()
        assert options.download is None
        assert options.max_concurrent_downloads == 5


def test_get_options_method(tmp_path: Path, port: int) -> None:
    with Aria2Server(tmp_path, port, session="max-dl-limit-10000.txt") as server:
        downloads = server.api.get_downloads()
        options = server.api.get_options(downloads)[0]
        assert options.max_download_limit == 10000


def test_get_stats_method(server: Aria2Server) -> None:
    assert server.api.get_stats()


def test_move_method(tmp_path: Path, port: int) -> None:
    with Aria2Server(tmp_path, port, session="2-dls-paused.txt") as server:
        downloads = server.api.get_downloads()
        assert server.api.move(downloads[0], 1) == 1
        new_pos_downloads = server.api.get_downloads()
        assert downloads == list(reversed(new_pos_downloads))


def test_move_down_method(tmp_path: Path, port: int) -> None:
    with Aria2Server(tmp_path, port, session="2-dls-paused.txt") as server:
        downloads = server.api.get_downloads()
        assert server.api.move_down(downloads[0]) == 1
        new_pos_downloads = server.api.get_downloads()
        assert downloads == list(reversed(new_pos_downloads))


def test_move_to_method(tmp_path: Path, port: int) -> None:
    with Aria2Server(tmp_path, port, session="2-dls-paused.txt") as server:
        downloads = server.api.get_downloads()
        assert server.api.move_to(downloads[0], 1) == 1
        new_pos_downloads = server.api.get_downloads()
        assert new_pos_downloads == [downloads[1], downloads[0]]

        assert server.api.move_to(downloads[1], -1) == 1
        new_pos_downloads = server.api.get_downloads()
        assert new_pos_downloads == downloads


def test_move_to_bottom_method(tmp_path: Path, port: int) -> None:
    with Aria2Server(tmp_path, port, session="2-dls-paused.txt") as server:
        downloads = server.api.get_downloads()
        assert server.api.move_to_bottom(downloads[0]) == 1
        new_pos_downloads = server.api.get_downloads()
        assert new_pos_downloads == [downloads[1], downloads[0]]


def test_move_to_top_method(tmp_path: Path, port: int) -> None:
    with Aria2Server(tmp_path, port, session="2-dls-paused.txt") as server:
        downloads = server.api.get_downloads()
        assert server.api.move_to_top(downloads[1]) == 0
        new_pos_downloads = server.api.get_downloads()
        assert new_pos_downloads == [downloads[1], downloads[0]]


def test_move_up_method(tmp_path: Path, port: int) -> None:
    with Aria2Server(tmp_path, port, session="2-dls-paused.txt") as server:
        downloads = server.api.get_downloads()
        assert server.api.move_up(downloads[0]) == 0
        new_pos_downloads = server.api.get_downloads()
        assert downloads == new_pos_downloads


def test_pause_method(tmp_path: Path, port: int) -> None:
    with Aria2Server(tmp_path, port, session="big-download.txt") as server:
        time.sleep(0.1)
        downloads = server.api.get_downloads()
        if downloads[0].has_failed:
            pytest.xfail("Failed to establish connection (sporadic error)")
        assert server.api.pause([downloads[0]])
        assert downloads[0].live.status == "paused"


def test_pause_all_method(tmp_path: Path, port: int) -> None:
    with Aria2Server(tmp_path, port, session="3-dls.txt") as server:
        assert server.api.pause_all()
        # The following code block is commented out because we cannot ensure
        # that the downloads will be paused in sufficient time.
        # aria2c returns "OK" immediately, and only then proceeds to pause the downloads
        # (with potential additional steps like contacting trackers).
        # Therefore we simply check the the call goes well.

        # for _ in range(5):
        #     time.sleep(1)
        #     downloads = server.api.get_downloads()
        #     try:
        #         assert all([d.is_paused for d in downloads])
        #     except AssertionError:
        #         pass
        #     else:
        #         break
        # else:
        #     raise AssertionError


def test_autopurge_method(tmp_path: Path, port: int) -> None:
    with Aria2Server(tmp_path, port, session="3-dls.txt") as server:
        assert server.api.autopurge()


def test_remove_method(tmp_path: Path, port: int) -> None:
    with Aria2Server(tmp_path, port, session="3-dls.txt") as server:
        downloads = server.api.get_downloads()
        if not all(server.api.remove(downloads)):
            pytest.xfail("Sporadic failures")
        downloads = server.api.get_downloads()
        assert not downloads


def test_remove_files_method(tmp_path: Path, port: int) -> None:
    with Aria2Server(tmp_path, port, session="very-small-download.txt") as server:
        time.sleep(1)
        download = server.api.get_downloads()[0]
        while not download.live.is_complete:
            if download.has_failed:
                pytest.xfail("Failed to establish connection (sporadic error)")
            time.sleep(0.1)
        assert server.api.remove([download], files=True)
        for file in download.root_files_paths:
            assert not file.exists()


def test_remove_files_not_complete(tmp_path: Path, port: int) -> None:
    with Aria2Server(tmp_path, port, session="2-dls-paused.txt") as server:
        downloads = server.api.get_downloads()
        assert server.api.remove(downloads, files=True)
        for download in downloads:
            for file in download.root_files_paths:
                assert file.exists()


def test_remove_files_tree(server: Aria2Server) -> None:
    directory = server.tmp_dir / "some-directory"
    directory.mkdir()

    class _Download:
        is_complete = True
        root_files_paths = [directory]  # noqa: RUF012

    assert server.api.remove_files([_Download])  # ty:ignore[invalid-argument-type]
    assert not directory.exists()


def test_remove_all_method(tmp_path: Path, port: int) -> None:
    with Aria2Server(tmp_path, port, session="3-dls.txt") as server:
        if not server.api.remove_all():
            pytest.xfail("Sporadic failures")
        downloads = server.api.get_downloads()
        assert not downloads


def test_resume_method(tmp_path: Path, port: int) -> None:
    with Aria2Server(tmp_path, port, session="2-dls-paused.txt") as server:
        downloads = server.api.get_downloads()
        assert server.api.resume(downloads)
        downloads = server.api.get_downloads()
        active = [d.is_active for d in downloads]
        if not all(active):
            pytest.xfail("Not all downloads were resumed (sporadic error)")
        assert all(active)


def test_resume_all_method(tmp_path: Path, port: int) -> None:
    with Aria2Server(tmp_path, port, session="2-dls-paused.txt") as server:
        time.sleep(0.1)
        assert server.api.resume_all()
        time.sleep(0.1)
        downloads = server.api.get_downloads()
        for download in downloads:
            if download.has_failed:
                pytest.xfail("Failed to establish connection (sporadic error)")
        assert all(d.is_active for d in downloads)


def test_set_global_options_method(tmp_path: Path, port: int) -> None:
    with Aria2Server(tmp_path, port, config=CONFIGS_DIR / "max-5-dls.conf") as server:
        assert server.api.set_global_options({"max-concurrent-downloads": "10"})
        options = server.api.get_global_options()
        assert options.max_concurrent_downloads == 10


def test_set_options_method(tmp_path: Path, port: int) -> None:
    with Aria2Server(tmp_path, port, session="max-dl-limit-10000.txt") as server:
        downloads = server.api.get_downloads()
        try:
            assert server.api.set_options({"max-download-limit": "20000"}, downloads)[0]
        except ClientException:
            pytest.xfail("Cannot change option for some reason")
        try:
            options = server.api.get_options(downloads)[0]
        except ClientException:
            pytest.xfail("Cannot change option for some reason")
        assert options.max_download_limit == 20000


# @pytest.mark.flaky(reruns=5)
def test_copy_files_method(tmp_path_factory: pytest.TempPathFactory, port: int) -> None:
    with Aria2Server(tmp_path_factory.mktemp("copy_files"), port, session="very-small-download.txt") as server:
        # initialize temp dir to copy to
        tmp_dir = tmp_path_factory.mktemp("copy_files")

        # wait until download is finished
        download = server.api.get_downloads()[0]
        while not download.live.is_complete:
            if download.has_failed:
                pytest.xfail("Failed to establish connection (sporadic error)")
            time.sleep(0.2)

        # actual method run
        server.api.copy_files([download], tmp_dir)

        # assert file was copied and contents are identical
        source = download.files[0].path
        target = tmp_dir / source.name

        assert source.exists()
        assert target.exists()

        with open(source) as stream:  # noqa: PTH123
            source_contents = stream.read()
        with open(target) as stream:  # noqa: PTH123
            target_contents = stream.read()
        assert source_contents == target_contents

        # clean up
        target.unlink()
        tmp_dir.rmdir()


def test_move_files_method(tmp_path_factory: pytest.TempPathFactory, port: int) -> None:
    with Aria2Server(tmp_path_factory.mktemp("move_files"), port, session="very-small-download.txt") as server:
        # initialize temp dir to copy to
        tmp_dir = tmp_path_factory.mktemp("move_files")

        # wait until download is finished
        download = server.api.get_downloads()[0]
        while not download.live.is_complete:
            if download.has_failed:
                pytest.xfail("Failed to establish connection (sporadic error)")
            time.sleep(0.2)

        # read source contents before move
        source = download.files[0].path
        with open(source) as stream:  # noqa: PTH123
            source_contents = stream.read()

        # actual method run
        server.api.move_files([download], tmp_dir)

        # assert file was copied and contents are identical
        target = tmp_dir / source.name

        assert not source.exists()
        assert target.exists()

        with target.open() as stream:
            target_contents = stream.read()
        assert source_contents == target_contents

        # clean up
        target.unlink()
        tmp_dir.rmdir()


def test_listen_to_notifications(tmp_path: Path, port: int) -> None:
    with Aria2Server(tmp_path, port, session="2-dls-paused.txt") as server:
        server.api.listen_to_notifications(threaded=True, timeout=1)
    time.sleep(3)
    assert server.api.listener
    assert not server.api.listener.is_alive()


def test_listen_to_notifications_then_stop(port: int) -> None:
    api = API(Client(port=port))
    api.listen_to_notifications(threaded=True, timeout=1)
    api.stop_listening()
    assert api.listener is None


def test_listen_to_notifications_callbacks(tmp_path: Path, port: int, capsys: pytest.CaptureFixture) -> None:
    with Aria2Server(tmp_path, port, session="2-dls-paused.txt") as server:
        server.api.listen_to_notifications(
            on_download_start=lambda api, gid: print("started " + gid),  # noqa: T201
            threaded=True,
            timeout=1,
        )
        time.sleep(1)
        server.api.resume_all()
        time.sleep(3)
        server.api.stop_listening()
    assert capsys.readouterr().out == "started 0000000000000001\nstarted 0000000000000002\n"


def test_listen_to_notifications_no_thread(tmp_path: Path, port: int) -> None:
    with Aria2Server(tmp_path, port, session="2-dls-paused.txt") as server:

        def thread_target() -> None:
            server.api.listen_to_notifications(threaded=False, timeout=1)

        thread = threading.Thread(target=thread_target)
        thread.start()
        time.sleep(1)
        server.client.stop_listening()
        time.sleep(1)
        server.api.stop_listening()


def test_parse_input_file() -> None:
    api = API()

    downloads = api.parse_input_file(INPUT_FILES[0])
    assert len(downloads) == 2

    downloads = api.parse_input_file(INPUT_FILES[1])
    assert len(downloads) == 1

    downloads = api.parse_input_file(INPUT_FILES[2])
    assert len(downloads) == 0


# -----------------------------------------------------------
# Tests for the public API.
# -----------------------------------------------------------
@pytest.fixture(name="loader", scope="module")
def _fixture_loader() -> griffe.GriffeLoader:
    loader = griffe.GriffeLoader()
    loader.load("aria2p")
    loader.resolve_aliases()
    return loader


@pytest.fixture(name="internal_api", scope="module")
def _fixture_internal_api(loader: griffe.GriffeLoader) -> griffe.Module:
    return loader.modules_collection["aria2p._internal"]


@pytest.fixture(name="public_api", scope="module")
def _fixture_public_api(loader: griffe.GriffeLoader) -> griffe.Module:
    return loader.modules_collection["aria2p"]


def _yield_public_objects(
    obj: griffe.Module | griffe.Class,
    *,
    modules: bool = False,
    modulelevel: bool = True,
    inherited: bool = False,
    special: bool = False,
) -> Iterator[griffe.Object | griffe.Alias]:
    for member in obj.all_members.values() if inherited else obj.members.values():
        try:
            if member.is_module:
                if member.is_alias or not member.is_public:
                    continue
                if modules:
                    yield member
                yield from _yield_public_objects(
                    member,  # ty: ignore[invalid-argument-type]
                    modules=modules,
                    modulelevel=modulelevel,
                    inherited=inherited,
                    special=special,
                )
            elif member.is_public and (special or not member.is_special):
                yield member
            else:
                continue
            if member.is_class and not modulelevel:
                yield from _yield_public_objects(
                    member,  # ty: ignore[invalid-argument-type]
                    modules=modules,
                    modulelevel=False,
                    inherited=inherited,
                    special=special,
                )
        except (griffe.AliasResolutionError, griffe.CyclicAliasError):
            continue


@pytest.fixture(name="modulelevel_internal_objects", scope="module")
def _fixture_modulelevel_internal_objects(internal_api: griffe.Module) -> list[griffe.Object | griffe.Alias]:
    return list(_yield_public_objects(internal_api, modulelevel=True))


@pytest.fixture(name="internal_objects", scope="module")
def _fixture_internal_objects(internal_api: griffe.Module) -> list[griffe.Object | griffe.Alias]:
    return list(_yield_public_objects(internal_api, modulelevel=False, special=True))


@pytest.fixture(name="public_objects", scope="module")
def _fixture_public_objects(public_api: griffe.Module) -> list[griffe.Object | griffe.Alias]:
    return list(_yield_public_objects(public_api, modulelevel=False, inherited=True, special=True))


@pytest.fixture(name="inventory", scope="module")
def _fixture_inventory() -> Inventory:
    inventory_file = Path(__file__).parent.parent / "site" / "objects.inv"
    if not inventory_file.exists():
        pytest.skip("The objects inventory is not available.")
    with inventory_file.open("rb") as file:
        return Inventory.parse_sphinx(file)


def test_exposed_objects(modulelevel_internal_objects: list[griffe.Object | griffe.Alias]) -> None:
    """All public objects in the internal API are exposed under `aria2p`."""
    not_exposed = [
        obj.path
        for obj in modulelevel_internal_objects
        if obj.name not in aria2p.__all__ or not hasattr(aria2p, obj.name)
    ]
    assert not not_exposed, "Objects not exposed:\n" + "\n".join(sorted(not_exposed))


def test_unique_names(modulelevel_internal_objects: list[griffe.Object | griffe.Alias]) -> None:
    """All internal objects have unique names."""
    names_to_paths = defaultdict(list)
    for obj in modulelevel_internal_objects:
        names_to_paths[obj.name].append(obj.path)
    non_unique = [paths for paths in names_to_paths.values() if len(paths) > 1]
    assert not non_unique, "Non-unique names:\n" + "\n".join(str(paths) for paths in non_unique)


def test_single_locations(public_api: griffe.Module) -> None:
    """All objects have a single public location."""

    def _public_path(obj: griffe.Object | griffe.Alias) -> bool:
        return obj.is_public and (obj.parent is None or _public_path(obj.parent))

    multiple_locations = {}
    for obj_name in aria2p.__all__:
        obj = public_api[obj_name]
        if obj.aliases and (
            public_aliases := [path for path, alias in obj.aliases.items() if path != obj.path and _public_path(alias)]
        ):
            multiple_locations[obj.path] = public_aliases
    assert not multiple_locations, "Multiple public locations:\n" + "\n".join(
        f"{path}: {aliases}" for path, aliases in multiple_locations.items()
    )


def test_api_matches_inventory(inventory: Inventory, public_objects: list[griffe.Object | griffe.Alias]) -> None:
    """All public objects are added to the inventory."""
    ignore_names = {"__getattr__", "__init__", "__repr__", "__str__", "__post_init__"}
    not_in_inventory = [
        f"{obj.relative_filepath}:{obj.lineno}: {obj.path}"
        for obj in public_objects
        if obj.name not in ignore_names and obj.path not in inventory
    ]
    msg = "Objects not in the inventory (try running `make run zensical build --clean`):\n{paths}"
    assert not not_in_inventory, msg.format(paths="\n".join(sorted(not_in_inventory)))


def test_inventory_matches_api(
    inventory: Inventory,
    public_objects: list[griffe.Object | griffe.Alias],
    loader: griffe.GriffeLoader,
) -> None:
    """The inventory doesn't contain any additional Python object."""
    not_in_api = []
    public_api_paths = {obj.path for obj in public_objects}
    public_api_paths.add("aria2p")
    for item in inventory.values():
        if item.domain == "py" and "(" not in item.name and (item.name == "aria2p" or item.name.startswith("aria2p.")):
            obj = loader.modules_collection[item.name]
            if obj.path not in public_api_paths and not any(path in public_api_paths for path in obj.aliases):
                not_in_api.append(item.name)
    msg = "Inventory objects not in public API (try running `make run zensical build --clean`):\n{paths}"
    assert not not_in_api, msg.format(paths="\n".join(sorted(not_in_api)))


def test_no_module_docstrings_in_internal_api(internal_api: griffe.Module) -> None:
    """No module docstrings should be written in our internal API.

    The reasoning is that docstrings are addressed to users of the public API,
    but internal modules are not exposed to users, so they should not have docstrings.
    """

    def _modules(obj: griffe.Module) -> Iterator[griffe.Module]:
        for member in obj.modules.values():
            yield member
            yield from _modules(member)

    for obj in _modules(internal_api):
        assert not obj.docstring
