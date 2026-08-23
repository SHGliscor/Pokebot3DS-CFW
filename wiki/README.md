# Wiki source

This directory contains the maintained Markdown source for the Pokebot3DS-CFW documentation Wiki.

`Home.md` is the entry page and `_Sidebar.md` contains the intended GitHub Wiki navigation.

These files are kept in the main repository so documentation changes are versioned alongside the project and can be reviewed before being published to GitHub's separate Wiki repository.

The repository now includes `.github/workflows/publish-wiki.yml`, which automatically mirrors this directory into the real GitHub Wiki repository whenever files under `wiki/` are changed on `main`.

`README.md` itself is excluded from the published Wiki so it remains source-maintenance documentation rather than becoming a visible Wiki page.
