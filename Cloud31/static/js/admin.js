

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
    if($("#location_info_box").attr("attached") == "true"){
        var lat = $("#lat_value").text().substring(0,14);
        var lng = $("#lng_value").text().substring(0,14);
        location_info = lat+"|"+lng;
    }
    
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



function check_all_users(item){
    if(!item.attr("checked")){
        $("#user_list_table input[type=checkbox]").removeAttr('checked');
    }else{
        $("#user_list_table input[type=checkbox]").attr('checked','checked');
    }
}

function authority_apply(item){
    item.attr('disabled','disabled');
    
    var user_list = '';
    $('#user_list_table tr.authority_item input[type=checkbox]:checked').each(function(){
    
        user_list+=$(this).attr('user_id')+'|';
    });
    
    var action = $("#authority_select option:selected").attr('value');
    
    console.log( user_list, action);
    
    var tokenValue = $("#csrf_token").text();
    data= "user_list=" + user_list + "&action=" + action;
    data +="&csrfmiddlewaretoken="+tokenValue;
	$.ajax({
		type : "POST",
		url : "/admin/authority/update/",
		data : data,
		dataType : "JSON",
		cache : false,
		success : function(json) {
		  console.log(json);
		  item.removeAttr('disabled');
          if(json.success){
            alert('Success');
            if(action == 'user'){
                document.location.href='/admin/authority/?show_staff=0';
            }else{
                document.location.href='/admin/authority/?show_staff=1';
            }
          }else{
            alert(json.message);
          }
		},
		error : function(data){
		  console.log(data);
		  alert('Error Occured');
		}
	});
    
   
}


