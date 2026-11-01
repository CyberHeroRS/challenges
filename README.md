# challs
Public repository containing archive of challenges created for CyberHero competitions

## Layout

Each event keeps its existing `sccYYYY-stage` name. Challenge folders use
category-free, lowercase slugs; categories remain in challenge metadata.

```text
scc2025-quals/
`-- challenges/
    `-- waffles/
        |-- challenge.yml
        |-- README.md
        |-- public/
        |-- source/
        |-- solution/
        |-- assets/
        `-- package.sh
```

- `public/`: participant downloads, including packaged archives.
- `source/`: runtime sources, Dockerfiles, and build inputs. Build from the
  Dockerfile's directory so its context contains the required files.
- `solution/`: solvers, checkers, and solution write-ups.
- `assets/`: optional authoring inputs that are not participant downloads.
- `package.sh`: optional packaging script, run from the challenge directory.

Unused directories are omitted. Existing artifact filenames and registry image
references are preserved.

The manifests still use the legacy CTFd format. Operator `challenge.yaml` and
event `ctf.yaml` manifests will be introduced during the subsequent conversion;
this layout change does not deploy challenges or convert their metadata.
