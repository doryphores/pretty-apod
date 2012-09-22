Transition = require 'utils/transition'
Module = require 'modules/module'

module.exports = class FullScreen extends Module
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
