# Template engine
## Template format example
```
some random text
{{variable1}}
some other text

{{#loop array1 item}}
do something with the {{item}}
{{/loop}}

{{variable2}}
more text
```

## Replacement values example
```
"variable1": "hello"
"array1": ["a", "b", "c"]
"variable2": "bye"
```

## Expected result
```
some random text
hello
some other text

do something with the a
do something with the b
do something with the c

bye
more text
```