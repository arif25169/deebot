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
# You should have received a copy of the GNU General Public License
	
class Plugin():
	"""Plugin Base Class for DeeBot"""
	
	def __init__(self):
		"""Constructor. Sets up command dictionary."""
		self.commands = {}
		
	def load(self, bot):
		"""Called when the plugin is loaded. Use this to add commands."""
		pass
		
	def unload(self, bot):
		"""Called when the plugin is unloaded."""
		pass
		
	# --------------------------------------------------------------------------
		
	def runCommand(self, bot, trigger, nick, target, message):
		"""Runs the specified command."""
		if trigger in self.commands:
			self.commands[trigger](bot, nick, target, message)
		
	def hasCommand(self, trigger):
		"""Returns true if a trigger exists in this plugin."""
		if trigger in self.commands:
			return True
		else:
			return False
	
	# --------------------------------------------------------------------------
			
	def addCommand(self, trigger, function):
		"""Adds a command to the command dictionary so it can be triggered."""
		if not trigger in self.commands:
			self.commands[trigger] = function
		
	def removeCommand(self, trigger):
		"""Removed a commadn from the command dictionary."""
		if trigger in self.commands:
			del self.commands[trigger]