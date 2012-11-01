module.exports = class Debug
	@ON: false

	@log: (args...) ->
		if Debug.ON and window.console
			console.log args...

	constructor: (name) ->
		@name = name

	log: (args...) ->
		if @name
			Debug.log "#{@name}:", args...
		else
			Debug.log args...
