// remember for development: lines that include the string "@striponbundle" will be stripped on build ;-)

var a = "alert from external JS";
    a += " - with a external part that should be removed on build"; // external @striponbundle
alert(a);
