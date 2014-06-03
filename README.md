# HTML builder

a small tool, that analyses and compresses HTMl and tries to put external files inline.

see `./test/example/` for details



## requirements:

* java
* python

### install python requirements
```sh
pip install -i requirements.txt
```




## use

```sh
<path_to_here>/bundler.py <path_to_somewere>/myfile.html
```



## note

this will break pre-wrapped HTML - even in `<pre>` tags


