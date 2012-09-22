Timer = require 'utils/timer'

module.exports = class Transition
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
