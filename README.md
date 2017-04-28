[![Build Status](https://travis-ci.org/wtsi-hgi/openstack-tenant-cleanup.svg?branch=master)](https://travis-ci.org/wtsi-hgi/openstack-tenant-cleanup)
[![codecov](https://codecov.io/gh/wtsi-hgi/openstack-tenant-cleanup/branch/master/graph/badge.svg)](https://codecov.io/gh/wtsi-hgi/openstack-tenant-cleanup)
[![Docker Repository on Quay](https://quay.io/repository/wtsi-hgi/openstack-tenant-cleanup/status "Docker Repository on Quay")](https://quay.io/repository/wtsi-hgi/openstack-tenant-cleanup)

# OpenStack Tenant Cleanup
## Introduction
This software can help prevent your OpenStack tenants (particularly ones where you run CI!) from becoming full of old 
images, instances and key-pairs.


## Features
- Cleans images, instances and key-pairs based on their age.
- Controls to prevent deletion based on name and whether they are in use.
- Both one-shot and periodic run modes.
- Non-destructive dry-mode.
- Can clean up multiple tenants.


## How To Use
### Usage
```bash
usage: openstack-tenant-cleanup [-h] [-d] [-s] configuration_location

OpenStack Tenant Cleanup

positional arguments:
  configuration_location
                        location of the configuration file

optional arguments:
  -h, --help            show this help message and exit
  -d, --dry-run         runs but does not delete anything
  -s, --single-run      run once then stop
```

### Configuration
#### Example
```yaml

---

general:
  run-every: 1h
  log:
    location: my.log
    level: DEBUG
  tracking-database: tracking.sqlite
  max-simultaneous-deletes: 4

cleanup:
  - openstack-auth-url: http://openstack.example.com:5000/v2.0/
    tenant: hgi
    credentials:
      - username: colin
        password: somepassword

    instances:
      remove-if-older-than: 24h
      exclude:
        - "my-special-instance"

    images:
      remove-only-if-unused: true
      remove-if-older-than: 14d
      exclude:
        - ".*-latest"

    key-pairs:
      remove-only-if-unused: true
      remove-if-older-than: 24h
      exclude:
        - "colin.*"
        - "josh.*"
```

#### Notes
- If a file path is not absolute, it is considered as relative to the location of the configuration file.
- Excludes are regular expression patterns - remember to escape special characters.
- Time deltas are parsed by [the Python `boltons` library](
http://boltons.readthedocs.io/en/latest/timeutils.html#boltons.timeutils.parse_timedelta) - it supports human readable
formats such as `X.Ym, 2 weeks 1 day`.
- Logs are rotated when they reach 100MB and the 3 most recent are kept (there is currently no option to configure 
this).
- Logging to stdout is set at `INFO` and cannot currently be configured.
- Multiple credentials can be supplied for a tenant to clean up key-pairs that are owned by different users. For all 
other clean up areas, only the first credentials in the list are used.

### Installation
#### Local
Prerequisites:
- python >= 3.6

Bleeding edge versions can be installed directly from GitHub:
```bash
$ git clone https://github.com/wtsi-hgi/openstack-tenant-cleanup.git
$ cd openstack-tenant-cleanup
$ python setup.py install
```
or
```bash
$ pip install git+https://github.com/wtsi-hgi/openstack-tenant-cleanup.git@<commit_id_or_branch_or_tag>#egg=openstacktenantcleanup
```

#### Docker
Run in Docker container using:
```bash
docker run -d -v ${directoryWithMyConfig}:/config quay.io/wtsi-hgi/openstack-tenant-cleanup /config/my-config.yml
```


## Known Issues
### Limitations
- OpenStack (or at least in the setup we have) does not provide created timestamps for key-pairs. In order to be able
to delete keys older than a given age, this software maintains a SQLite database to track when they were created. This 
database is updated when the cleaner is ran. Therefore, the accuracy of the key-pair end will depend on the run 
frequency.

### Dragons
- Not tested across different timezones.
- Not tested in parallel (probably best to just use one instance to clean a tenant!).
- Limited validation of configuration values - negative times and wrong times will undoubtedly cause weird things to 
happen! 


## Development
### Setup
Prerequisites:
- python >= 3.6

Install both library dependencies and the dependencies needed for testing:
```bash
$ pip install -q -r test_requirements.txt
```

### Testing
Using unittest (from the project directory):
```bash
$ PYTHONPATH=. python -m unittest discover -v -s .
```


## License
[MIT license](LICENSE.txt).

Copyright (c) 2017 Genome Research Limited
