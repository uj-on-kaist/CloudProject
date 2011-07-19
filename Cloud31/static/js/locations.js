function get_random_feeds(){
    $("#load_more_box").hide();
    $("#loading_box").show();

    $.ajax({
		type : "GET",
		url : '/api/location/random',
		dataType : "JSON",
		cache : false,
		success : function(json) {
		  $("#loading_box").hide();
		  if(json.success){
		      $("#feed_list").attr('type','random');
		      
		      display_location_feeds(json.feeds, 'random');
		      
		      $("#load_more_box").hide();
		  }
		},
		error : function(data){
		  $("#loading_box").hide();
		  console.log(data);
		}
	});
}

function display_location_feeds(feeds, type){
    for(var i=0; i<feeds.length; i++){
        
        var feed=feeds[i];
        //console.log(feed);
        
        var feed_layout= $("div.stream.template").clone();
        feed_layout.removeClass("template");
        feed_layout.addClass("feed_item");
        feed_layout.attr('id','feed_'+feed.id);
        feed_layout.attr('base_id',feed.base_id);
        feed_layout.find('.user_link').attr('href','/user/'+feed.author);
        feed_layout.find('.from a').text(feed.author);
        feed_layout.find('.from span.author_name').text(feed.author_name);
        feed_layout.find('.feed_content').html(nl2br(feed.contents));
        
        if(feed.favorite){
            feed_layout.find('.like_action a span.favor').hide();
            feed_layout.find('.like_action a span.unfavor').show();
            feed_layout.find('.like_action a').attr('feed_id',feed.id);
            
            feed_layout.find('.like_action a').click(function(){
                feed_like($(this), false);
                return false;
            });
        }else{
            feed_layout.find('.like_action a span.favor').show();
            feed_layout.find('.like_action a span.unfavor').hide();
            feed_layout.find('.like_action a').attr('feed_id',feed.id);
            feed_layout.find('.like_action a').click(function(){
                feed_like($(this), true);
                return false;
            });
        }
        
        feed_layout.find('abbr.feed_time').text(humane_date(feed.reg_date));
        feed_layout.find('img.avatar.author').attr('src',feed.author_picture);

        display_files(feed.file_list, feed_layout, feed.id);
        feed_layout.find("a.fancy_image").fancybox({
            'titlePosition'     : 'over',
            'titleFormat'       : function(title, currentArray, currentIndex, currentOpts) {
            return '<span id="fancybox-title-over"><b style="float:right;">' +  (currentIndex + 1) + ' / ' + currentArray.length + ' </b>' + title + '</span>';
            }
        });
        
        
        if(feed.lat && feed.lng){
            var location = feed.lat+","+feed.lng;
            var layout="<img src='http://maps.google.com/maps/api/staticmap?center="+location+"&zoom=17&size=180x80&maptype=roadmap&markers=color:red|color:red|label:Here|"+location+"&sensor=false' location='"+location+"'/>";
            var item = feed_layout.find('p.feed_location').html(layout);
            item.addClass('small');
            item.find('img').click(function(){
                window.open('http://maps.google.com/?q='+$(this).attr('location'));
            });
            
            addNewMarker(feed);
            
        }else{
            feed_layout.find('p.feed_location').remove();
        }
        
        if(feed.author == $("#user_name_info").text()){
            feed_layout.find('.stream_element_delete.feed').remove();
        }
        
        feed_layout.find('.comment_action a').attr("feed_id",feed.id);
        feed_layout.find('.comment_action a').click(function(){
            $("#feed_"+$(this).attr("feed_id")+" ul.comments").show();
        });
        
        feed_layout.find('span.comment_count_text').text(feed.comments.length);
        if(feed.comments.length == 0){
            
            feed_layout.find('ul.comments.comment_count li span').text('댓글이 없습니다.');
            feed_layout.find('ul.comments.comment_list').hide();
            feed_layout.find("ul.comments.comment_count a.show_all").attr('id','comment_show_'+feed.id);
            feed_layout.find("ul.comments.comment_count a.show_all").hide();
        }else{
            if (feed.comments.length == 1){
                feed_layout.find("ul.comments.comment_count a.show_all").hide();
            }
            feed_layout.find('ul.comments.comment_count span span').text(feed.comments.length);
            feed_layout.find("ul.comments.comment_count a.show_all").attr('id','comment_show_'+feed.id);
        }
        feed_layout.find("ul.comments.comment_count a.show_all").click(function(){
                if($(this).text().indexOf('보기') != -1){
                    $(this).text('숨기기');
                    var id=$(this).attr('id').split('_')[2];
                    $('#feed_'+id+' ul.comments.comment_list li').show();
                }else{
                    $(this).text('모두 보기');
                    var id=$(this).attr('id').split('_')[2];
                    var total=$('#feed_'+id+' ul.comments.comment_list li').length;
                    $('#feed_'+id+' ul.comments.comment_list li').each(function(i){
                        $(this).hide();
                    });
                }
                return false;
        });
        
        for(var j=0; j<feed.comments.length; j++){
            add_comment(feed_layout, feed.comments[j], j, feed.comments.length);
        }
        $("#feed_list").append(feed_layout);
        feed_layout.find(".comment_area").attr('id','comment_area_'+feed.id);
        feed_layout.find(".comment_submit").attr('id','comment_submit_'+feed.id);

        feed_layout.find(".comment_submit").click(function(){
                var id=$(this).attr('id').split('_')[2];
                update_comment(id);
        });
        feed_layout.find("textarea").click(function(){
                var reply_btn = $(this).parent().parent().find('.submit_button');
                reply_btn.show();
        });    
        feed_layout.find('textarea').elastic();
        
        if(feed.comments.length != 0)
            feed_layout.find('ul.comments').show();
            
        if(type == 'notice'){
            feed_layout.find("span.like_action").remove();
            feed_layout.find("span.comment_action").remove();
            feed_layout.find("ul.comments").remove();
        }
        
    }
}

var marker_arr=new Array();
function addNewMarker(feed){
    var latlng = new google.maps.LatLng(parseFloat(feed.lat),parseFloat(feed.lng));
    var marker = new google.maps.Marker({
      position: latlng, 
      map: map
    });
    marker.feed = feed;
    marker_arr.push(marker);
    google.maps.event.addListener(marker, "click", function(item) {
       var feed_id = "#feed_"+marker.feed.id;
       window.location.hash = feed_id;
       $(".feed_item").css('background-color',"#fff");
       $(feed_id).css('background-color',"#FAFAFA");
    });
}

function initialize_search_map() {
    geocoder = new google.maps.Geocoder();
    var latlng = new google.maps.LatLng(37.528068,126.967691);
    var myOptions = {
      zoom: 16,
      center: latlng,
      mapTypeId: google.maps.MapTypeId.ROADMAP
    };
    map = new google.maps.Map(document.getElementById("map_canvas"), myOptions);
    //map.enableGoogleBar(); 
    google.maps.event.addListener(map, "dragend", function() {
       var bounds = map.getBounds(); 
       load_location_feed(bounds, false);
    });
    google.maps.event.addListener(map, "zoom_changed", function() {
       var bounds = map.getBounds(); 
       load_location_feed(bounds, false);
    });
}

function load_location_feed(bounds, in_data, load_more){
    $("#load_more_box").hide();
    $("#loading_box").show();
        
    var data = in_data;
    if(data == ''){
        var sw = bounds.getSouthWest();
        var ne = bounds.getNorthEast();
        var sw_str = sw.lat()+","+sw.lng();
        var ne_str = ne.lat()+","+ne.lng();
        data = 'sw='+sw_str+"&ne="+ne_str;
    }else{
        var base_id = $("#feed_list").find(".stream.feed_item").last().attr("base_id");
        if (base_id == undefined || base_id == ''){
            return false;
        }
        data += "&base_id="+base_id;
    }
    
    $.ajax({
		type : "GET",
		url : '/api/location/get',
        data : data,
		dataType : "JSON",
		cache : false,
		success : function(json) {
		  $("#loading_box").hide();
		  if(json.success){
		      console.log(json);
		      $("#feed_list").attr('type','random');
		      if(!load_more){
		          $(".feed_item").remove();
		          for (i in marker_arr) {
		              marker_arr[i].setMap(null);
		          }
		          marker_arr = new Array();
		      }
		      display_location_feeds(json.feeds, 'location');
		      
		      if(json.load_more){
		          $("#load_more_box").show();
		          $("#load_more_box a").attr('base_url',data);
		      }else{
		          $("#load_more_box").hide();
		      }
		  }
		},
		error : function(data){
		  $("#loading_box").hide();
		  console.log(data);
		}
	});
}