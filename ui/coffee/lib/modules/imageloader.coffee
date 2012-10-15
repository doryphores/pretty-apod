Module = require 'modules/module'
Timer = require 'utils/timer'

module.exports = class ImageLoader extends Module
	defaults:
		size: 'small'

	@small:
		lines		: 11,		# The number of lines to draw
		length		: 4,		# The length of each line
		width		: 2,		# The line thickness
		radius		: 5,		# The radius of the inner circle

	@big:
		lines		: 13,		# The number of lines to draw
		length		: 7,		# The length of each line
		width		: 4,		# The line thickness
		radius		: 11,		# The radius of the inner circle

	@spinnerOptions:
		corners		: 1,		# Corner roundness (0..1)
		rotate		: 0,		# The rotation offset
		color		: '#dedede',
		speed		: 1.0,		# Rounds per second
		trail		: 60,		# Afterglow percentage
		shadow		: false,	# Whether to render a shadow
		hwaccel		: true,		# Whether to use hardware acceleration

	init: ->
		@spinner = new Spinner $.extend ImageLoader.spinnerOptions, ImageLoader[@options.size]

		@img = @element.find 'img'

		# Create an image object to fire on load
		@imageLoader = new Image
		@imageLoader.onload = @imageLoader.onerror = => @stop()
		@imageLoader.src = @img.prop('src')

		@timer = new Timer

		# Start spinner with a 1 second delay (don't want to show the spinner when image loads fast)
		@timer.delay 1000, => @spinner.spin @element[0]

	stop: ->
		@timer.clear()
		@spinner.stop()
		@element.addClass 'loaded'
		@imageLoader.onload = @imageLoader.onerror = null;
