module.exports = class Timer
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
