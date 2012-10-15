Module = require 'modules/module'
Timer = require 'utils/timer'
Transition = require 'utils/transition'

module.exports = class Viewport extends Module
	init: ->
		# Do nothing if the element doesn't exist
		if @element.length is 0
			return

		@image = @element.find '.picture'

		if @image.length is 0
			return

		@window = $ window

		imageTag = @image.get(0).tagName.toLowerCase()

		if imageTag is 'img'
			# Image is ready
			@window.load => @initImage()
		else
			# Call server to process image
			@trigger 'image_loading'

			timer = new Timer()
			timer.delay 1000, => $.getJSON @image.data('url') , (data) => @processImage(data)

	initImage: ->
		# Measure the image
		@imageWidth = parseInt @image.attr 'width'
		@imageHeight = parseInt @image.attr 'height'
		@imageAspectRatio = @imageWidth / @imageHeight

		@redraw()

		@window.resize => @redraw()

		timer = new Timer()

		@trigger 'image_loaded'

	processImage: (image_data) ->
		# Replace with empty IMG tag
		imgTag = $('<img />').attr
			width: image_data.width
			height: image_data.height
		.css
			maxWidth: image_data.width
			maxHeight: image_data.height

		@image.replaceWith imgTag
		@image = imgTag

		# Load image
		image = new Image image_data.width, image_data.height
		image.onload = =>
			# Image is now fully downloaded
			@image.attr 'src', image_data.url
			@initImage()

		image.src = image_data.url

	redraw: ->
		# Measure viewport
		viewportWidth = @element.width()
		viewportHeight = @element.height()
		viewportAspectRatio = viewportWidth / viewportHeight

		# Do we need to downscale the image?
		downscale = @imageWidth > viewportWidth || @imageHeight > viewportHeight

		# Add portrait class if we have to downscale and
		if downscale and viewportAspectRatio > @imageAspectRatio
			@element.addClass 'maximise-height'
		else
			@element.removeClass 'maximise-height'
