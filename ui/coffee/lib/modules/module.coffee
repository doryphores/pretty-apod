module.exports = class Module
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
