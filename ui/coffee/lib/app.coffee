module.exports = App =
	init: ->
		Growler = require 'modules/growler'
		# Initialise growler
		growler = new Growler

		# Listen for events
		$(document).on
			'image_loaded': -> growler.hide()
			'image_loading': -> growler.info "Please wait while the picture is downloaded and processed"
			'ui_ready': ->
				$(document.documentElement).addClass 'ui-ready'
				# Focus on page element
				page = $('.site-page').attr('tabindex', -1).focus()

		# Initialise modules
		for el in $('[data-module]')
			$el = $(el)
			for module_name in $el.data('module').split(' ')
				console.log module_name
				mod = require('modules/' + module_name)
				$el.data($el.data('module'), new mod(el))

		$(document).trigger 'ui_ready'
