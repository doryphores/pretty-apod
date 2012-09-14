# Add support for namespaces

namespace = (target, name, block) ->
	[target, name, block] = [(if typeof exports isnt 'undefined' then exports else window), arguments...] if arguments.length < 3
	top    = target
	target = target[item] or= {} for item in name.split '.'
	block target, top


# Timer functions

class Timer
	@immediate: (func) ->
		setTimeout func, 0

	constructor: ->
		@timer = null

	delay: (ms, func) ->
		@timer = setTimeout func, ms

	repeat: (ms, func) ->
		@timer = setInterval func, ms

	clear: ->
		if @timer
			clearTimeout @timer
			clearInterval @timer


# Transition helper

class Transition
	@timeout: 500

	@support: (->
		transitionEnd = (->
			el = document.createElement 'bootstrap'
			transEndEventNames =
				'WebkitTransition' : 'webkitTransitionEnd'
				'MozTransition'    : 'transitionend'
				'OTransition'      : 'oTransitionEnd'
				'msTransition'     : 'MSTransitionEnd'
				'transition'       : 'transitionend'

			for name of transEndEventNames
				if el.style[name] isnt undefined
					return transEndEventNames[name]
		)()

		return transitionEnd and
			end: transitionEnd
	)()

	constructor: (@element, @timeout = Transition.timeout) ->
		@deferred = $.Deferred()
		@timer = new Timer()

	start: (func) ->
		@reflow()
		@element.addClass "animated"
		@reflow()

		if Transition.support
			Timer.immediate func
		else
			func()

		@deferred.always => @element.removeClass "animated"

		if Transition.support
			@element.off Transition.support.end
			@element.on Transition.support.end, (e) =>
				unless e.target is e.currentTarget
					@element.off Transition.support.end
					@timer.clear()
					@deferred.resolve();

			@timer.delay @timeout, =>
				@element.off Transition.support.end
				@deferred.resolve()
		else
			@deferred.resolve()

	end: (func) ->
		@deferred.done func

	reflow: ->
		@element.offset()


namespace "APOD.utils", (exports) ->
	exports.Timer = Timer
	exports.Transition = Transition


# Base module class

class Module
	constructor: (element = {}, options = {}) ->
		@element = $ element

		# Parse data attribute options
		dataOptions = {}
		for key, value of @element.data() when typeof value isnt 'object'
			dataOptions[key] = value

		# Set module options
		@options = $.extend {}, @defaults, dataOptions, options

		# Treat 'onSomething' options as event handlers
		for key, value of @options when key.indexOf('on') is 0 and typeof value is 'function'
			eventType = key.replace /on(.)(.*)/g, (s, first, rest) -> first.toLowerCase() + rest
			@element.on eventType, value

		@init()

	init: () ->

	# Event handling (all return this instance)

	trigger: (args...) ->
		@element.trigger args...
		return @

	trigger: (args...) ->
		@element.trigger args...

	on: (args...) ->
		@element.on args...

	off: (args...) ->
		@element.off args...

	one: (args...) ->
		@element.one args...


# Modules

class Viewport extends Module
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
		timer.delay 500, => @image.addClass 'loaded'

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


class Panel extends Module
	@panels: {}
	@currentPanel: null

	@getCurrentPanel: ->
		return Panel.panels[Panel.currentPanel]

	defaults:
		overlapping: false
		load: false

	timer: new Timer()

	init: ->
		@element.attr 'tabindex', -1
		@id = @element.attr 'id'
		@state = 'hidden'

		@toggles = $('body').find "[data-toggle=#{@id}]"

		$('body').on 'click.panel', "[data-toggle=#{@id}]", (e) =>
			e.preventDefault()
			e.stopImmediatePropagation()
			@toggle()

		Panel.panels[@id] = @

		@on
			'click.panel': (e) -> e.stopPropagation()
			'hide.panel': => @toggles.removeClass('active')
			'show.panel': => @toggles.addClass('active')

		# Close when click outside
		$(document).on 'click.panel', (e) =>
			@hide() if e.button is 0

	show: ->
		if @state is 'visible' then return @

		evt = new $.Event 'show'
		@trigger evt

		if evt.isDefaultPrevented() then return @

		if cp = Panel.getCurrentPanel()
			cp.one 'hidden', => @_show()
			cp.hide()
		else
			@_show()

		return @

	_show: ->
		evt = new $.Event 'show'
		@trigger evt
		if evt.isDefaultPrevented() then return

		@element.show()

		@state = 'visible'

		tran = new Transition @element

		tran.start =>
			$('body').addClass 'open-panel'
			unless @options.overlapping
				$('body').addClass 'push-panel'
				@startResize()

		tran.end =>
			@stopResize() unless @options.overlapping
			if $('body').hasClass 'open-panel'
				if @options.load then @element.find('.inner-panel').load @options.load, => @options.load = false
				@element.focus()
				@trigger 'shown'

		Panel.currentPanel = @id

	hide: ->
		if @state is 'hidden' then return @

		evt = new $.Event 'hide'
		@trigger evt

		if evt.isDefaultPrevented() then return

		@state = 'hidden'

		tran = new Transition @element

		tran.start =>
			$('body').removeClass 'open-panel'
			unless @options.overlapping
				$('body').removeClass 'push-panel'
				@startResize()

		tran.end =>
			@stopResize() unless @options.overlapping
			unless $('body').hasClass 'open-panel'
				@element.hide()
				Panel.currentPanel = null
				@trigger 'hidden'

		return @

	toggle: ->
		cp = Panel.getCurrentPanel()
		if cp is @ then @hide() else @show()

		return @

	startResize: ->
		$(window).triggerHandler 'resize'
		# Start triggering resize events
		if Transition.support
			@timer.repeat 10, -> $(window).triggerHandler 'resize'

	stopResize: ->
		$(window).triggerHandler 'resize'
		# Stop timer
		@timer.clear()


class Growler extends Module

	@build: ->
		unless Growler.box
			# Create and inject message box element
			Growler.box = $('<div class="growler"><p><i class="icon-time"></i> <span></span></p></div>').appendTo 'body'
			Growler.msgContainer = Growler.box.find('span').first()

	show: ->
		@trigger 'show'

		Growler.box.appendTo 'body'
		Growler.box.offset()

		# Add Transition
		tran = new Transition Growler.box
		tran.start ->
			Growler.box.addClass 'open'
		tran.end =>
			@trigger 'shown' if Growler.box.hasClass 'open'

	info: (msg) ->
		Growler.build()

		Growler.msgContainer.text msg

		@show()

	hide: ->
		if Growler.box
			@trigger 'hide'

			tran = new Transition Growler.box, 200
			tran.start ->
				Growler.box.removeClass 'open'
			tran.end ->
				Growler.box.remove() unless Growler.box.hasClass 'open'


class FullScreen extends Module
	defaults:
		class_name: 'full-screen'

	init: ->
		@state = 'off'
		@root = $(document.documentElement)

		$('body').on 'click.fullscreen', '[data-toggle=fullscreen]', (e) =>
			e.preventDefault()
			@toggle()

	enable: ->
		evt = new $.Event 'resize_full'
		@trigger evt

		if evt.isDefaultPrevented() then return

		@state = 'on'

		@root.addClass @options.class_name

	disable: ->
		evt = new $.Event 'resize_small'
		@trigger evt

		if evt.isDefaultPrevented() then return

		@state = 'off'

		tran = new Transition @element

		@root.removeClass @options.class_name

	toggle: ->
		if @state is 'off' then @enable() else @disable()


namespace 'APOD.modules', (exports) ->
	exports.Viewport = Viewport
	exports.Panel = Panel
	exports.Growler = Growler
	exports.FullScreen = FullScreen


$ ->
	# Initialise growler
	growler = new Growler

	# Listen for events
	$(document).on
		'image_loaded': -> growler.hide()
		'image_loading': -> growler.info "Please wait will the picture is downloaded and processed"
		'ui_ready': ->
			$(document.documentElement).addClass 'ui-ready'
			# Focus on page element
			page = $('.site-page').attr('tabindex', -1).focus()

	# Initialise modules
	for el in $('[data-module]')
		new APOD.modules[$(el).data('module')](el)


	$(document).trigger 'ui_ready'