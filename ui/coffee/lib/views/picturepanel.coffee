Panel = require 'views/panel'

module.exports = class PicturePanel extends Panel
	view_name: 'PicturePanel'

	_update: (action, context, data) ->
		if context is 'pre'
			@hide()
		else
			@element.find('.explanation').html data.explanation
