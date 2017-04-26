[![Build Status](https://travis-ci.org/wtsi-hgi/python-sequencescape-db.svg)](https://travis-ci.org/wtsi-hgi/python-sequencescape-db)
[![codecov.io](https://codecov.io/gh/wtsi-hgi/python-sequencescape-db/graph/badge.svg)](https://codecov.io/gh/wtsi-hgi/python-sequencescape-db/)

# Python 3 Sequencescape Database Client


## How to use
### Installation
The client can be installed directly from GitHub:
```bash
$ pip3 install git+https://github.com/wtsi-hgi/sequencescape-python-client.git@<commit_id_or_branch_or_tag>#egg=sequencescape
```

To declare this library as a dependency of your project, add it to your `requirement.txt` file.


### API
```python
from sequencescape import connect_to_sequencescape, Sample, Study, Library, MultiplexedLibrary, Well

# Classes of models of data in Sequencescape. Each have constructors with named parameters
available_models = [Sample, Study, Library, MultiplexedLibrary, Well]

# Declares a connection to Sequencescape. (Actual network connections are only opened when required)
api = connect_to_sequencescape("mysql://user:@host:3306/database")

# Available for: study, sample, library, multiplexed_library, well
api.sample.get_by_name("sample_name")   # type: List[Sample]
api.sample.get_by_name(["sample_name", "other_sample_name"])   # type: List[Sample]

# Available for: study, sample, library, multiplexed_library, well
api.library.get_by_id(123)   # type: List[Library]
api.library.get_by_id([123, 456])   # type: List[Library]

# Available for: study, sample
api.study.get_by_accession_number("accession_number")   # type: List[Study]
api.study.get_by_accession_number(["accession_number", "other_accession_number"])   # type: List[Study]

# Available for: study, sample, library, multiplexed_library, well
api.sample.get_by_property_value("property", "value")   # type: List[Sample]
api.sample.get_by_property_value("property", ["value", "other_value"])   # type: List[Sample]
api.sample.get_by_property_value([("property", "value"), ("other_property", "other_value")])   # type: List[Sample]

# Available for: study
api.study.get_associated_with_sample(sample)  # type: List[Study]
api.study.get_associated_with_sample([sample_1, sample_2])  # type: List[Study]

# Available for: sample
api.sample.get_associated_with_study(study)  # type: List[Sample]
api.sample.get_associated_with_study([study_1, study_2])  # type: List[Sample]
```


## How to develop
### Testing
Using nosetests, in the project directory, run:
```bash
$ nosetests -v --exclude-test=sequencescape.tests._json_converters_test_factory.create_json_converter_test
```

To generate a test coverage report with nosetests:
```bash
$ nosetests -v --with-coverage --cover-package=sequencescape --cover-inclusive nosetests -v --with-coverage --cover-package=sequencescape --cover-inclusive --exclude-test=sequencescape.tests._json_converters_test_factory.create_json_converter_test
```


## License
[MIT license](LICENSE.txt).

Copyright (c) 2015, 2016 Genome Research Limited