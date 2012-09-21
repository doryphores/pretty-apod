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
		@clear()
		@timer = setTimeout func, ms

	repeat: (ms, func) ->
		@clear()
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


class Scroller extends Module
	@step: 20

	@overlayBars: (->
		detector = $ '<div />',
			css:
				width: 100
				height: 100
				position: 'absolute'
				overflow: 'scroll'
				top: -9999
		detector.appendTo 'body'

		detector[0].offsetWidth - detector[0].clientWidth is 0 and detector.remove()
	)()

	init: ->
		# Don't apply if browser has overlaid scroll bars (OSX lion style)
		unless Scroller.overlayBars
			@build()
			@disabled = true
			@redraw()
			$(window).on 'resize.scroller', => @redraw()

	build: ->
		# Disable scrolling and wrap inner with new DIV
		@element.css 'overflow', 'hidden'
		@element.wrapInner('<div class="scroller" />')
		@scroller = @element.find('.scroller')

		# Inject scrollbar
		@scrollbar = $('<div class="scroll-bar"><span class="handle"><span /></span><span class="track"><span /></span></div>').appendTo(@element)
		@hide()

		# Get reference to track
		@track = @scrollbar.find '.track'

		# Get reference to handle and make draggable (jQuery UI)
		@handle = @scrollbar.find('.handle').draggable
			containment: 'parent'
			axis: 'y'

		# Setup drag events
		@handle.on
			'dragstart': =>
				@dragging = true
				@scrollbar.addClass 'dragging'
			'dragstop': =>
				@dragging = false
				@scrollbar.removeClass 'dragging'
			'drag': =>
				@scroll @scroller[0].scrollHeight * parseInt(@handle.css('top'), 10) / @element.height()

	redraw: () ->
		scrollHeight = @scroller[0].scrollHeight
		height = @element.height()

		# Compute visible area as percentage
		visible = height / scrollHeight * 100;

		# Enable scrollbar if visible area is less than 100%
		if visible < 100 then @enable() else @disable()

		# Adjust bar and handle heights accordingly
		@scrollbar.height(height)
		@handle.height "#{visible}%"

		# Adjust handle position
		@handle.css 'top', @scroller[0].scrollTop

	scroll: (s) ->
		scrollHeight = @scroller[0].scrollHeight
		height = @element.height()

		# Limit scroll value
		scroll = Math.max(0, Math.min(s, scrollHeight - height))

		# Adjust handle position
		@handle.css 'top', scroll * height / scrollHeight

		# Adjust scrollTop if different
		if @scroller[0].scrollTop isnt scroll
			@scroller[0].scrollTop = scroll

	reset: ->
		@scroll(0)

	show: ->
		@scrollbar.removeClass 'hide'

	hide: ->
		@scrollbar.addClass 'hide'

	disable: ->
		if @disabled then return

		@disabled = true

		# Hide scrollbar and switch off event handlers
		@scrollbar.hide()
		@element.off '.scroller'

	enable: ->
		unless @disabled then return

		@disabled = false

		# Show scrollbar
		@scrollbar.show()

		# Create a new timer
		timer = new Timer

		# Switch on event handlers
		@element.on
			'mousewheel.scroller': (e, delta) =>
				@show()
				@scroll @scroller[0].scrollTop - delta * Scroller.step
			'mouseleave.scroller': => unless @dragging then timer.delay 1000, => @hide()
			'mouseenter.scroller': => timer.delay 500, => @show()


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

		# Add scroll bar
		@scroller = new Scroller(@element)

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
		# Reset scroll
		@scroller.reset()

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
				if @options.load then @element.find('.inner-panel').load @options.load, =>
					@options.load = false
					@scroller.redraw()
				@element.focus()
				@scroller.redraw()
				@trigger 'shown'

		Panel.currentPanel = @id

	hide: ->
		if @state is 'hidden' then return @

		evt = new $.Event 'hide'
		@trigger evt

		if evt.isDefaultPrevented() then return

		@state = 'hidden'
		@scroller.hide()

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
			e.currentTarget.blur()

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
		$el = $(el)
		if APOD.modules[$el.data('module')]?
			$el.data($el.data('module'), new APOD.modules[$el.data('module')](el))

	$(document).trigger 'ui_ready'
