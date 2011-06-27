
function edit_description(){
    if($("#topic_desc").is(":visible")){
		$("#topic_desc").hide();
		$(".edit_btn").hide();
		$("form.newDesc").show();
	}else{
		$("#topic_desc").show();
		$(".edit_btn").show();
		$("form.newDesc").hide();
	}
	return false;
}

function update_description(){
    var ed = tinyMCE.get('newDesc');
    var new_desc = ed.getContent();
    
    var topic_id = $("form.newDesc #topic_id").val();
    var tokenValue = $("#csrf_token").text();
    
    data= "topic_id=" + topic_id + "&desc=" + encodeURIComponent(new_desc);
    data +="&csrfmiddlewaretoken="+tokenValue;
    
	$.ajax({
		type : "POST",
		url : "/api/feed/update/desc",
		data : data,
		dataType : "JSON",
		success : function(json) {
		  console.log(json);
          if(json.success){
            $("#topic_desc").html(new_desc);
            edit_description();
          }
		},
		error : function(data){
		  console.log(data);
		}
	});
	
    
}