Timer = require 'utils/timer'
Transition = require 'utils/transition'
Module = require 'modules/module'
Scroller = require 'modules/scroller'

module.exports = class Panel extends Module
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
