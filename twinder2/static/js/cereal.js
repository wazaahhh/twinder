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
	'37':'next',
	'39':'next',
},

});

KeyboardJS.on('left', function() { mark(Reveal.getCurrentSlide(),'left') }, null)
KeyboardJS.on('right', function() { mark(Reveal.getCurrentSlide(),'right') }, null)



function mark(slide,direction) {
	if ($(slide).attr('id')) {
		$.ajax({
			type: 'POST',
			url: '/mark/',
			contentType: 'application/json',
			dataType:'json',
			data: JSON.stringify({id: $(slide).attr('id'), csrfmiddlewaretoken: $( "#csrfmiddlewaretoken" ).val() }) ,
				success: function(data) {
					alert('retweet');
					alert(data);
				}
		})
	} else { alert('No post') }
}