

function reloadSWF(name, url) {
  swfobject.embedSWF(
    	  "/static/open-flash-chart2.swf", name, 
    	  "525", "200", "9.0.0", "/static/expressInstall.swf",
    	  {"data-file":url}, {"wmode":"transparent"} );
  return false;
}

function accuSet(item,name, url){
    if(item.attr("checked") == "checked"){
        reloadSWF(name, url+"?accu=1");
    }else{
        reloadSWF(name, url+"?accu=0");
    }    
}


function reloadSWFRange(item, name, url){
    var start = item.parent().find(".startpicker").val();
    var end = item.parent().find(".endpicker").val();
    var accu = 0;
    if(item.parent().find("input[type=checkbox]").attr("checked") == "checked"){
        accu = 1;
    }
    var requestURL = url+"?start="+start+"&end="+end+"&accu="+accu;
    console.log(requestURL);
    reloadSWF(name, encodeURIComponent(requestURL));
    
}

