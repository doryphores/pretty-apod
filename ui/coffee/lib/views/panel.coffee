Transition = require 'utils/transition'
View = require 'views/view'

module.exports = class Panel extends View
	@currentPanel: null

	view_name: 'Panel'

	defaults:
		load: false
		disabled: false

	init: ->
		@id = @element.attr 'id'

		# Reference to panel element (make focusable)
		@panel = @element.find('.panel').attr 'tabindex', -1
		@panel.css 'bottom', -@panel.height()

		# Initial state
		@state = 'hidden'

		# Attach behaviour to tab
		@tab = @element.find('h2').on 'click.panel', (e) =>
			e.preventDefault()
			@toggle()

		if @options.disabled then @disable()

	show: ->
		# Ignore if already open or disabled
		if @options.disabled or @state is 'visible' then return @

		# Tell everyone I'm about to open
		evt = new $.Event 'show'
		@trigger evt

		# Stop if prevented
		if evt.isDefaultPrevented() then return @

		@debugger.log "opening #{@id}"

		if cp = Panel.currentPanel
			# Close open panel before opening
			cp.off 'hidden'
			cp.one 'hidden', => @_show()
			cp.hide()
		else
			@_show()

		return @

	_show: ->
		# Make panel visible
		@panel.show()

		@state = 'visible'

		tran = new Transition @element

		# Start animation
		tran.start =>
			@element.addClass 'active'
			@panel.css 'bottom', 0
			@tab.css 'top', -@panel.height()

		# When animation ends
		tran.end =>
			if @element.hasClass 'active'
				if @options.load then @element.find('.inner-panel').load @options.load, =>
					@options.load = false
					@trigger 'loaded'

				# Focus on panel
				@panel.focus()

				# Tell everyone I'm open
				@trigger 'shown'

				$(window).on 'resize.panel', =>
					@debugger.log 'Hello'
					@tab.css 'top', -@panel.height()

				@debugger.log "#{@id} is open"

		# I am now the current open panel
		Panel.currentPanel = @

	hide: (immediate = false)->
		# Ignore if already closed or disabled
		if @options.disabled or @state is 'hidden' then return @

		# Tell everyone I'm about to close
		evt = new $.Event 'hide'
		@trigger evt

		# Stop if prevented
		if evt.isDefaultPrevented() then return @

		@debugger.log "closing #{@id}"

		@state = 'hidden'

		tran = new Transition @element

		# Start animation
		tran.start =>
			@element.removeClass 'active'
			@panel.css 'bottom', -@panel.height()
			@tab.css 'top', 0

		# When animation ends
		tran.end =>
			unless @element.hasClass 'active'
				# Hide the panel
				@panel.hide()

				# Reset current panel
				if Panel.currentPanel is @ then Panel.currentPanel = null

				$(window).off 'resize.panel'

				# Tell everyone I'm closed
				@trigger 'hidden'

				@debugger.log "#{@id} is closed"

		return @

	toggle: ->
		if @state == 'hidden' then @show() else @hide()

		return @


	disable: ->
		@element.hide()
		@hide()

		@options.disabled = true

		return @

	enable: ->
		@element.show()

		@options.disabled = false

		return @
