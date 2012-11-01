Debug = require 'utils/debug'
Action = require 'utils/action'

module.exports = class View
	constructor: (element = {}, options = {}) ->
		@debugger = new Debug(@view_name)

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

		# Attach actions
		if @element.data('listen')
			for action in @element.data('listen').split(' ')
				@debugger.log "Attached '#{action}' action"
				Action(action).subscribe (action, context, data) => @update(action, context, data)

		@debugger.log 'View initialised'

		@init()

	init: () ->

	update: (action, context, data) ->
		@debugger.log "'#{action}/#{context}' action intercepted with: ", data
		if @_update then @_update(action, context, data)

	# Event handling (all return this instance)

	trigger: (args...) ->
		@element.trigger args...
		return @

	on: (args...) ->
		@element.on args...
		return @

	off: (args...) ->
		@element.off args...
		return @

	one: (args...) ->
		@element.one args...
		return @
