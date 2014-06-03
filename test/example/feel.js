// remember for development: lines that include the string "@striponbuild" will be stripped on build ;-)

var a = "alert from external JS";
    a += " - with a part that should be removed on build"; // @striponbuild
alert(a);
