// Full list of configuration options available here:
// https://github.com/hakimel/reveal.js#configuration
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
	'68':'next',
	'76':'next',
},

});

KeyboardJS.on('l', function() { mark(Reveal.getCurrentSlide(),'left') }, null)
KeyboardJS.on('d', function() { mark(Reveal.getCurrentSlide(),'right') }, null)



function mark(slide,direction) {

	if ($(slide).attr('id')){
		$.ajax({
			url: "/mark/",
			type: 'POST',
			data: {'tweet_id': $(slide).attr('id'), 'tweet_text':$(slide).attr('value'), 'direction':direction},
				success: function(data) {
					if (data === false){alert('error')};
				}
		})
	}
}