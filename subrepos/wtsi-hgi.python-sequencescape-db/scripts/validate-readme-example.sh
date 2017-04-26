#!/bin/bash
tempFile=$(mktemp /tmp/validate-readme-XXXXXXXXXX)
sed -n '/^```python/,/^```/ p' < README.md | sed '/^```/ d' > $tempFile

# Validate syntax by compilation
PYTHONPATH=. python3 -m py_compile $tempFile

if [[ $? -eq 0 ]]
then
    echo "Example Python in README.md is syntactically valid"
else
    echo "Example Python in README.md is not syntactically valid!"
fi

exit $?
