#!/usr/bin/env python3
"""Update the cask from a published cot release, checking the downloaded DMG."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
from urllib.request import Request, urlopen


REPO = "cot-intelligence/cot"
CASK = Path(__file__).resolve().parents[1] / "Casks/cot.rb"
VERSION = re.compile(r"[0-9]+\.[0-9]+\.[0-9]+")


def release_metadata(version):
    suffix = f"tags/v{version}" if version else "latest"
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "cot-homebrew-tap"}
    if token := os.environ.get("GH_TOKEN"):
        headers["Authorization"] = f"Bearer {token}"
    request = Request(f"https://api.github.com/repos/{REPO}/releases/{suffix}", headers=headers)
    with urlopen(request, timeout=30) as response:
        return json.load(response)


def update(release, cask_path=CASK):
    tag = release["tag_name"]
    version = tag.removeprefix("v")
    if not tag.startswith("v") or not VERSION.fullmatch(version):
        raise ValueError(f"Expected a stable vX.Y.Z tag, got {tag!r}")
    if release.get("draft") or release.get("prerelease"):
        raise ValueError("Only published stable releases can update the cask")

    text = cask_path.read_text()
    current = re.search(r'^  version "([0-9.]+)"$', text, re.MULTILINE).group(1)
    if tuple(map(int, version.split("."))) < tuple(map(int, current.split("."))):
        raise ValueError(f"Refusing to downgrade {current} to {version}")

    name = f"cot_{version}_aarch64.dmg"
    assets = [asset for asset in release["assets"] if asset["name"] == name]
    if len(assets) != 1 or assets[0].get("state") != "uploaded":
        raise ValueError(f"Expected one uploaded {name}")
    asset = assets[0]
    url = f"https://github.com/{REPO}/releases/download/{tag}/{name}"
    if asset["browser_download_url"] != url:
        raise ValueError("Unexpected DMG download URL")
    expected = asset.get("digest", "")
    if not re.fullmatch(r"sha256:[a-f0-9]{64}", expected):
        raise ValueError("Release asset has no valid SHA-256 digest")

    digest = hashlib.sha256()
    size = 0
    # Do not send the API token to the download host or its redirects.
    with urlopen(url, timeout=60) as response:
        while chunk := response.read(1024 * 1024):
            digest.update(chunk)
            size += len(chunk)
    sha256 = digest.hexdigest()
    if f"sha256:{sha256}" != expected or size != asset["size"]:
        raise ValueError("Downloaded DMG does not match the release digest and size")

    text, versions = re.subn(r'^  version "[^"]+"$', f'  version "{version}"', text, flags=re.MULTILINE)
    text, checksums = re.subn(r'^  sha256 "[^"]+"$', f'  sha256 "{sha256}"', text, flags=re.MULTILINE)
    if versions != 1 or checksums != 1:
        raise ValueError("Expected one version and checksum in the cask")
    cask_path.write_text(text)
    print(f"Verified {name}: {sha256}")
    if output := os.environ.get("GITHUB_OUTPUT"):
        with open(output, "a") as stream:
            stream.write(f"version={version}\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", help="Stable release version; defaults to latest")
    args = parser.parse_args()
    if args.version and not VERSION.fullmatch(args.version):
        parser.error("--version must be X.Y.Z")
    update(release_metadata(args.version))


if __name__ == "__main__":
    main()
