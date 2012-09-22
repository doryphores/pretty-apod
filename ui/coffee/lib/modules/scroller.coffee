Timer = require 'utils/timer'
Module = require 'modules/module'

module.exports = class Scroller extends Module
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
