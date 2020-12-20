Hooting Yard Indexes API
------------------------

Set-up:
* Install this package in a virtual environment:
```a
python setup.py develop
```
* Check out the keyml and analytics repos
* Ceate a configuration file that should be in `~/.config/hootingyard/config.yaml` whcih contins the locations of the important directories.

The configuration file should look something like this:

```yaml
project_directory: /home/sal/Dropbox/hooting_yard_projects
keyml_directory: /home/sal/workspace/scf/hooting_yard/keyml
analysis_directory: /home/sal/workspace/scf/hooting_yard/analysis
```

Where `project_directory` is the locatioon of the Dropbox shared folder "hooting_yard_projects", `keyml_directory` is where you checked out the keyml repo and `analysis_rirectory` is where you checked out the analysis repo.
