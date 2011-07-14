

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

function upload_notice(item){
    item.attr('disabled','disabled');
    
    start_loading(item);
    
    var attach_list='';
    var count=$(".qq-upload-list").find('li').length;
    $(".qq-upload-list").find('li').each(function(i, val){
        var file_id = $(this).attr('id').split('#');
        if(file_id.length != 2)
            return false;
        if (i == count-1)
            attach_list+=file_id[1];
        else
            attach_list+=file_id[1]+'.';
    });
    console.log("Attach: " + attach_list);
    
    var message=$('textarea#feed_message_input').val();
    var location_info='';
    
    var tokenValue = $("#csrf_token").text();
    
    if(message == ""){
        finish_loading(item);
        return false;
    }
    
    data= "message=" + message + "&attach_list=" + attach_list + "&location_info="+location_info;
    data +="&csrfmiddlewaretoken="+tokenValue;
	$.ajax({
		type : "POST",
		url : "/api/notice/update/",
		data : data,
		dataType : "JSON",
		cache : false,
		success : function(json) {
		  console.log(json);
		  item.removeAttr('disabled');
          if(json.success){
            clear_feed_input();
            var feed_type=$("#feed_list").attr('type');
            load_feed(feed_type);
          }
          
          finish_loading(item);
		},
		error : function(data){
		  console.log(data);
		  alert('Error Occured');
		}
	});
    
}


