# cot Homebrew tap

Install [cot](https://cot.run), a Mac app for self-hosted observability of AI coding agents:

```sh
brew install --cask cot-intelligence/tap/cot
```

Apple Silicon only. Open `cot.app` from Applications to complete setup. If cot is
already installed manually, Homebrew may report that the app already exists.
Quit cot and use `brew install --cask --adopt cot-intelligence/tap/cot` to adopt
an existing matching version instead of replacing it.

The current builds are ad-hoc signed and are not notarized. macOS Gatekeeper may
require approval in System Settings > Privacy & Security on first launch.
Homebrew does not bypass Gatekeeper.

## Updates

cot has an in-app updater. You can also explicitly upgrade through Homebrew:

```sh
brew update
brew upgrade --cask cot-intelligence/tap/cot
```

## Maintaining the tap

The **Update cot cask** workflow checks the latest published stable release of
`cot-intelligence/cot` every 30 minutes. GitHub can delay scheduled runs. You can
also run it manually from Actions, optionally selecting a version.

The updater downloads the release DMG and verifies its SHA-256 and size against
GitHub's release metadata before changing the cask. It rejects drafts,
prereleases, unexpected URLs, missing checksums and downgrades. It pushes a
`release/cot-vX.Y.Z` branch with the new version and checksum. The workflow summary
links to the comparison page where you can open a PR. Review and merge it to
publish to Homebrew. Existing release branches are never overwritten.
It never merges changes and does not change cot's app update manifest.

The workflow uses this repository's `GITHUB_TOKEN`; no cross-repo token is needed.
The organization blocks workflow-created PRs, so it creates review branches
instead. Default workflow permissions stay read-only, with contents write access
only for the updater job. No organization permission changes are needed.

For a manual update:

```sh
python3 scripts/update-cask.py --version 1.13.3
brew style --cask cot-intelligence/tap/cot
git diff -- Casks/cot.rb
```

Commit and push the cask once reviewed. The updater uses only Python's standard
library. `GH_TOKEN` is optional locally and raises GitHub's API rate limit.

Apple notarization can be added to cot's desktop build later without changing
this tap's release process.
