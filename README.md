# AID-template-engine

## Introduction
This program implements a template engine similar to [jinja](https://jinja.palletsprojects.com/en/2.10.x/) as requested
in the recruiting process from AID

## Requirements
- The template must be able to replace simple strings and loop over arrays iterating with an index variable
- Example of template file:
```
some random text
I wanted to say {{variable1}} to you
some other text

{{#loop array1 item}}
do something with the {{item}}
{{/loop}}

now I say {{variable2}} to everyone
more text
```
- Example of variable file:
```
"variable1": "hello"
"array1": ["a", "b", "c"]
"variable2": "bye"
```
- Example of the result obtained after the translation:
```
some random text
I wanted to say hello to you
some other text

do something with the a
do something with the b
do something with the c

now I say bye to everyone
more text
```

## Execution
There are 3 ways you can use the tool:
- Directly from the shell interpreter
```shell script
unzip aid_template_engine.zip
virtualenv my_virtualenv -p python3
source my_virtualenv/bin/activate
pip install -e aid_template_engine
./template -t TEMPLATE_FILE_PATH -v VARIABLES_FILE_PATH -o OUTPUT_FILE_PATH
```

- As a python executable
```shell script
unzip aid_template_engine.zip
python3 aid_template_engine/engine/translator.py -t TEMPLATE_FILE_PATH -v VARIABLES_FILE_PATH -o OUTPUT_FILE_PATH
```

- From inside a python script
```shell script
unzip aid_template_engine.zip
virtualenv my_virtualenv -p python3
source my_virtualenv/bin/activate
pip install -e aid_template_engine
```

```python
from translator import Template
template = Template("template.txt", "variables.txt", "output.txt")
template.replace()
```

## Technical design
- [Technical documentation](docs/Technical_Design.md)
