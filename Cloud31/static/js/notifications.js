function get_notis_count(){
    $.ajax({
		type : "GET",
		url : "/api/noti/get/",
		dataType : "JSON",
		cache : false,
		success : function(json) {
		  if(json.success){
		      if(json.unread_notis.length == 0){
		          $(".noti_count").text("");
		          $('#noti_selector').attr('status','nor');
		          $('#noti_selector').removeClass("sel");
                  $('#noti_selector').addClass("nor");
		      }else{
		          $('#noti_selector').attr('status','high');
		          $('#noti_selector').removeClass("nor");
		          $('#noti_selector').addClass("high");
		          $(".noti_count").text(json.unread_notis.length);
		      }
		  }
		},
		error : function(data){
		  console.log(data);
		}
	});
}

function load_notis(){
    if($('#noti_list').is(":visible")){
        hide_noti();
        return false;
    }
    
    $.ajax({
		type : "GET",
		url : "/api/noti/get/",
		dataType : "JSON",
		cache : false,
		success : function(json) {
		  if(json.success){
		      console.log(json.unread_notis, json.read_notis);
		      
		      var notis = new Array();
		      for (var i=0; i<json.unread_notis.length; i++){
		          notis.push(json.unread_notis[i]);
		      }
		      if(notis.length <5){
		          var needed = 5 - notis.length;
		          for(var i=0; i<needed && i<json.read_notis.length; i++){
		              var noti = json.read_notis[i];
		              notis.push(noti);
		          }
		      }
		      show_noti(notis);
		      if(json.unread_notis.length != 0)
		          $(".noti_count").text(json.unread_notis.length);
		  }
		},
		error : function(data){
		  console.log(data);
		}
	});

    return false;
}
function show_noti(notis){
    $('#noti_list').show();
    $('#noti_list li.header').click(function(){
        return false;
    });
    $('#noti_selector').removeClass("nor high");
    $('#noti_selector').addClass("sel");
    
    $('#noti_list li.noti_item').remove();
    for(var i=0; i<notis.length; i++){
        var noti=notis[i];
        console.log(noti);
        var noti_layout= $("#noti_list li.noti_item_template").clone();
        noti_layout.removeClass("noti_item_template");
        noti_layout.addClass("noti_item");
        if(!noti.is_read){
            noti_layout.addClass("unread");
        }
        noti_layout.attr("noti_id",noti.id);
        noti_layout.attr("related_type",noti.related_type);
        noti_layout.attr("related_id",noti.related_id);
        noti_layout.find(".user_picture").attr("src","/picture/"+noti.sender);
        noti_layout.find(".message").html(noti.contents);
        noti_layout.find(".noti_time abbr").text(humane_date(noti.reg_date));
        noti_layout.click(function(event){
            var url='/';
            var noti_id = $(this).attr("noti_id");
            var related_type=$(this).attr("related_type");
            var related_id=$(this).attr("related_id");
            if(related_type == "Message")
                url="/feed/detail/"+related_id;
            else if(related_type == "Event")
                url="/event/detail/"+related_id;
            else if(related_type == "DM" || related_type == "DM_Reply")
                url="/message/detail/"+related_id;
            else{
                stopEvent(event);
                return;
            }
            
            var tokenValue = $("#csrf_token").text();
            $.ajax({
		      type : "POST",
		      url : "/api/noti/read/"+noti_id,
		      dataType : "JSON",
		      cache : false,
		      data : "&csrfmiddlewaretoken="+tokenValue,
		      success : function(json) {
		          location.href=url; 
		      }, error : function(data){
		          location.href=url;
		          console.log(data);
		      }
	       });
            
            stopEvent(event);
        });
        $('#noti_list a.see_more').before(noti_layout);
    }

}

function hide_noti(){
    $('#noti_list').hide();
    $('#noti_selector').removeClass("sel");
    $('#noti_selector').addClass($('#noti_selector').attr('status'));

}