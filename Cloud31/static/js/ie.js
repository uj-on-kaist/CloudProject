document.createElement('header');
document.createElement('footer');

var debugging = true; // or true
if (typeof console == "undefined") var console = { log: function() {} }; 
else if (!debugging || typeof console.log == "undefined") console.log = function() {};