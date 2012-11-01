Action = require 'utils/action'
Debug = require 'utils/debug'
Milk = require 'vendor/milk'
Transition = require 'utils/transition'

Debug.ON = true

module.exports = App =
	init: ->
		# Initialise views
		$('[data-view]').each ->
			$el = $ this
			for view_name in $el.data('view').split(' ')
				view = require('views/' + view_name)
				$el.data($el.data('view'), new view(this))

		page1 = $ '.page:first'
		page2 = $ '.page:last'
		page2.hide()

		$('nav a:last').click (e) ->
			e.preventDefault()

			page2.show()

			tran = new Transition(page1)
			tran.start ->
				page1.addClass 'previous'
				page2.removeClass 'next'

			tran.end ->
				page1.hide()

		$('nav a:first').click (e) ->
			e.preventDefault()

			page1.show()

			tran = new Transition(page1)
			tran.start ->
				page1.removeClass 'previous'
				page2.addClass 'next'

			tran.end ->
				page2.hide()
