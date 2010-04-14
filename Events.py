# Events.py
# Copyright (C) 2010 Daniel Callander
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License.

import DeeIRC.Events as Events

# ------------------------------------------------------------------------------

class ConnectedEvent(Events.ConnectedEvent):
	def fire(self, bot):
		"""Joins the configured channels on connect."""
		for channel in bot.config["channels"]:
			bot.sendJoin(channel)

# ------------------------------------------------------------------------------

class MessageEvent(Events.MessageEvent):		
	def fire(self, bot, nick, target, message):
		"""Checks if a command has been said and run it if so."""
		if message[0] == bot.config["command_prefix"]:
			# Get the command from the message.
			trigger_end = message.find(" ")
			if not trigger_end >= 0:
				# No parameters.
				trigger_end = len(message)
			trigger = message[1:trigger_end].lower()

			# If the command exists, run the function.
			plugin_name = bot.findPluginFromTrigger(trigger)
			if plugin_name:
				plugin = bot.getPlugin(plugin_name)
				plugin.runCommand(bot, trigger, nick, target, message[trigger_end+1:])
				
				if bot.debug:
					bot.log("Command(" + plugin_name + ":" + trigger + "): (" + nick + ", " + target + ", " + message +")")
		else:
			# Run commands which do not rely on an actual trigger.
			for plugin_name in bot.plugins:
				plugin = bot.getPlugin(plugin_name)
				
				if plugin.hasCommand("*"):
					plugin.runCommand(bot, "*", nick, target, message)
					
					if bot.debug:
						bot.log("Command(" + plugin + ":*): (" + nick + ", " + target + ", " + message +")")
						pass