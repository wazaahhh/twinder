// Full list of configuration options available here:
// https://github.com/hakimel/reveal.js#configuration
$(document).ready(function(){
	Reveal.initialize({
	controls: false,
	progress: true,
	history: false,
	center: true,
	//autoSlide: 5000,
	keyboard: true,
	//loop: true,
	progress: false,

	theme: Reveal.getQueryHash().theme || 'serif', // available themes are in /css/theme
	transition: Reveal.getQueryHash().transition || 'linear', // default/cube/page/concave/zoom/linear/fade/none

	//keyboard modifications
	keyboard:{
		'76':'next',
		'70':'next',
	},

	});

	KeyboardJS.on('l', function() { mark(Reveal.getCurrentSlide(),'left');add_last() }, null)
	KeyboardJS.on('f', function() { mark(Reveal.getCurrentSlide(),'right');add_last() }, null)

});

function mark(slide,direction) {

	if ($(slide).attr('id')){
		$.ajax({
			url: "/mark/",
			type: 'POST',
			data: {'tweet_id': $(slide).attr('id'), 'friend_id':$(slide).attr('value'), 'txt_length':$(slide).attr('name'), 'direction':direction},
				success: function(data) {
					if (data === false){alert('error')};
				}
		})
	}
}