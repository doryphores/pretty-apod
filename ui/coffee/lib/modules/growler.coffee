Transition = require 'utils/transition'
Module = require 'modules/module'

module.exports = class Growler extends Module

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
