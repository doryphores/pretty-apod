Debug = require 'utils/debug'

actions = {}

module.exports = Action = (name) ->
	action = name && actions[name]

	if !action
		callbacks = $.Callbacks()

		action =
			publish		: callbacks.fire
			subscribe	: callbacks.add
			unsubscribe	: callbacks.remove

		if name then actions[name] = action

	action

# Setup data API

$('body').on 'click.action', '[data-action]', (e) ->
	$el = $(this)

	# Prevent original action
	e.preventDefault()

	# For each action
	for action_name in $el.data('action').split ' '
		# Publish trigger version of action
		Action(action_name).publish(action_name, 'pre')

		# Make JSON call and publish action when done
		$.getJSON($el.attr('href')).done (data) ->
			Action(action_name).publish(action_name, 'post', data)
