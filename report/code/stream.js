function streaming(id,friend,txt_length){
			$.ajax({
				dataType: "jsonp",
				url: "https://api.twitter.com/1/statuses/oembed.json?id="+id+'&align=center',
				type: 'GET',
					success: function(data,args) {
						if (data.html){
							$(".slides").append('<section id="'+id+'" value="'+friend+'" name="'+txt_length+'">'+data.html+'</section>');
						}
					},
				    error: function(Xhr, textStatus, errorThrown) {
				    	alert(Xhr);
				    }, 	
		});
}