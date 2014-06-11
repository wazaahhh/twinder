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

theme: Reveal.getQueryHash().theme || 'serif', // available themes are in /css/theme
transition: Reveal.getQueryHash().transition || 'linear', // default/cube/page/concave/zoom/linear/fade/none
});

// set keyboard shortcuts
KeyboardJS.on('q', function() { interestedIn(Reveal.getCurrentSlide()) }, null)
KeyboardJS.on('l', function() { skip(Reveal.getCurrentSlide()) }, null)
KeyboardJS.on('r', function() { retweet(Reveal.getCurrentSlide()) }, null)
KeyboardJS.on('m', function() { favorites(Reveal.getCurrentSlide()) }, null)
// we open this queue after user is down browsing
function favorites(slide) {
	if ($(slide).attr('id')) {
		$.ajax({
			type: 'POST',
			url: '/favorites',
			contentType: 'application/json',
			dataType:'json',
			data: JSON.stringify({id: $(slide).attr('id') }) ,
				success: function(data) {
					alert('favorite');
					alert(data);
				}
		})
	} else { alert('No post') }
}

function retweet(slide) {
	if ($(slide).attr('id')) {
		$.ajax({
			type: 'POST',
			url: '/retweet',
			contentType: 'application/json',
			dataType:'json',
			data: JSON.stringify({id: $(slide).attr('id') }) ,
				success: function(data) {
					alert('retweet');
					alert(data);
				}
		})
	} else { alert('No post') }
}

var read_queue = []

// when we first express interest, we go to article preview
// if we express interest from article preview, we queue and go to the next slide
function interestedIn(slide) {

	// make sure we're not on the last slide
	if (!Reveal.isLastSlide()) {

		//  if we're on the main display slide,
		if ($(slide).attr('id')) {

			// go down to the article preview slide
			Reveal.down()

		// if we're on a article preview slide
		} else {

			queue(slide)

			// check if we're done
			checkIfEndOfFeed()

			// go up
			Reveal.up()
			// wait 150ms, then go right
			setTimeout(Reveal.right, 300);
		}
	}

}

function skip(slide) {

	// check if we're done
	checkIfEndOfFeed()

	// if we're on a main display slide,
	if (!$(slide).attr('id')) {

		// first of all, get the slide with the interest marker on it
		var main_slide = $(slide).prev()

		// second of all, go up
		Reveal.up()

	}

	// otherwise, we're already on the main slide
	else 
		var main_slide = $(slide)



	// if user was interested in it before
	if (hasInterestMarker(main_slide)) {

		// we keep post url in id of <section> tag
		var url = main_slide.attr('id') 

		// use url to lookup post
		for (var i=0;i<read_queue.length;i++) {
			if (read_queue[i]['url'] === url) {
				// remove the post from the queue
				remove(read_queue,read_queue[i])
			}
		}

		// remove interest marker from the main slide
		removeInterestMarker(main_slide)

	}


}

// adds the URL for the given slide to our interest queue
function queue(slide) {

	// the main display slide has the url 
	var main_slide = $(slide).prev()

	// we keep post url in id of <section> tag
	var url = main_slide.attr('id') 
	var title = main_slide.children('.title').html()

	if (!hasInterestMarker(main_slide)) {

	  	// add url to queue as a json object
	  	read_queue.push({
	  		url:url,
	  		title:title
	  	})

	  	// add visual feedback to the slide to mark interest
	  	addInterestMarker(main_slide)

	}
	

}

// takes a jquery object and puts an interest marker on it
// static/i.png is the interest marker
function addInterestMarker(slide) {
		slide.append("<div class='i'><img src='static/i.png'></div>")
}

function removeInterestMarker(slide) {
		slide.children('.i').remove()
}

// returns true if the slide has already been liked
function hasInterestMarker(slide) {
	if (slide.children('.i').html() == undefined)
		return false;
	return true
}

// if we are at end of list, open up all the urls
// NB: this is triggered when 'l' key is pressed AND whenever queue() is called
function checkIfEndOfFeed() {

	if (Reveal.isLastSlide()) {

		// post the json object to server
		$.ajax({
			type: 'POST',
			url: '/done',
			contentType: 'application/json',
			dataType:'json',
			data: JSON.stringify({posts: read_queue}),
			success: function(data) {
				document.body.innerHTML = data.html
			}
		})
	}

}



// remove an item from an array
function remove(arr, item) {
	for(var i = arr.length; i--;) {if(arr[i] === item) {arr.splice(i, 1); } } return arr } 