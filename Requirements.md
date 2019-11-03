# Template engine
## Template format example
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

## Replacement values example
```
"variable1": "hello"
"array1": ["a", "b", "c"]
"variable2": "bye"
```

## Expected result
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