View = require 'views/view'

module.exports = class Picture extends View
	view_name: 'Picture'

	init: ->
		@image = @element.find 'img'

		if @image.length is 1
			@initImage()

	initImage: ->
		# Measure the image and calculate aspect ratio
		@imageWidth = parseInt @image.attr 'width'
		@imageHeight = parseInt @image.attr 'height'
		@imageAspectRatio = @imageWidth / @imageHeight

		# Set max width and heights to actual dimensions
		@image.css
			'max-width': @imageWidth
			'max-height': @imageHeight

		# Redraw on window resize
		$(window).resize => @redraw()

		@redraw()

	redraw: ->
		# Measure picture frame
		frameWidth = @element.parent().width()
		frameHeight = @element.parent().height()
		frameAspectRatio = frameWidth / frameHeight

		# Do we need to downscale the image?
		downscale = @imageWidth > frameWidth || @imageHeight > frameHeight

		# Add portrait class if we have to downscale and
		if downscale and frameAspectRatio > @imageAspectRatio
			@element.addClass 'maximise-height'
		else
			@element.removeClass 'maximise-height'

	_update: (action, context, data) ->
		if context is 'post'
			imageLoader = new Image()
			imageLoader.onload = =>
				@image.attr
					src: data.url
					alt: data.name
					width: imageLoader.width
					height: imageLoader.height
				@initImage()
			imageLoader.src = data.url
