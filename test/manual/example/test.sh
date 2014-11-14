#!/bin/sh

dir=$(dirname $0)
tmp=$(mktemp.exe -d)

bundler="$dir/../../../bundler.py -i $dir/in.html"

#echo "dir = $dir"
#echo "tmp = $tmp"

$bundler -o "$tmp/out_raw.html"
$bundler -o "$tmp/out_fullfeatured.html" --compress --strip-markers "@stripOnBundle" --strip-tags "@stripOnBundle" --strip-comments

errors=0

echo -n "checking out_raw.html ... "
if diff $tmp/out_raw.html $tmp/out_raw.html >/dev/null
then
    echo "same"
else
    errors=$errors+1
    echo "different"
fi

echo -n "checking out_fullfeatured.html ... "
if diff $tmp/out_fullfeatured.html $tmp/out_fullfeatured.html >/dev/null
then
    echo "same"
else
    errors=$errors+2
    echo "different"
fi

rm -rf $tmp

echo "exit with errors: $errors"
exit $errors