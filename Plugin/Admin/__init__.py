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

import Plugin

# ------------------------------------------------------------------------------

class AdminPlugin(Plugin.Plugin):
	"""Admin plugin. Provides plugin loading commands, etc."""
	
	def load(self, bot):
		"""Add our commands."""
		self.addCommand("load", self.commandPluginLoad)
		self.addCommand("unload", self.commandPluginUnload)
		self.addCommand("reload", self.commandPluginReload)
		
		self.addCommand("join", self.commandJoin)
		self.addCommand("part", self.commandPart)
		
		self.addCommand("exec", self.commandExec)
		self.addCommand("eval", self.commandEval)
		
		self.addCommand("quit", self.commandQuit)

	# --------------------------------------------------------------------------
	
	def commandPluginLoad(self, bot, nick, target, message):
		"""Attempt to load a plugin."""
		if bot.isAdmin(nick):
			try:
				bot.loadPlugin(message)
			except:
				bot.sendMessage(target, "Failed to load plugin.")
			else:
				bot.sendMessage(target, "Loaded plugin.")
		
	def commandPluginUnload(self, bot, nick, target, message):
		"""Unload a plugin."""
		if bot.isAdmin(nick):
			bot.unloadPlugin(message)
			bot.sendMessage(target, "Unloaded plugin.")
		
	def commandPluginReload(self, bot, nick, target, message):
		"""Reloads a plugin. If the plugin name is sent as "all", loop through
		all plugins and reload them."""
		if bot.isAdmin(nick):
			if message == "all":
				for plugin_name in bot.plugins:
					bot.reloadPlugin(plugin_name)
					
				bot.sendMessage(target, "Reloaded all plugins.")
			else:
				bot.reloadPlugin(message)
				bot.sendMessage(target, "Reloaded plugins.")
	
	# --------------------------------------------------------------------------
	
	def commandJoin(self, bot, nick, target, message):
		"""Causes the bot to join a channel."""
		if bot.isAdmin(nick):
			bot.sendJoin(message)
		
	def commandPart(self, bot, nick, target, message):
		"""Causes the bot to leave a channel."""
		if bot.isAdmin(nick):
			bot.sendPart(message)
		
	# --------------------------------------------------------------------------
	
	def commandExec(self, bot, nick, target, message):
		"""Executes a Python line."""
		if bot.isAdmin(nick):
			try:
				exec(message)
			except Exception, e:
				bot.sendMessage(target, str(e))
				
	def commandEval(self, bot, nick, target, message):
		"""Evaluates a Python statement and prints it to the IRC channel."""
		if bot.isAdmin(nick):
			try:
				eval_result = eval(message)
			except Exception, e:
				bot.sendMessage(target, str(e))
			else:
				bot.sendMessage(target, "eval(" + message + ") = " + str(eval_result))
			
	# --------------------------------------------------------------------------
	
	def commandQuit(self, bot, nick, target, message):
		"""Makes the bot disconnect."""
		if bot.isAdmin(nick):
			bot.disconnect()
		
# ------------------------------------------------------------------------------

__plugin_instance = None
def getPluginInstance():
	global __plugin_instance
	
	if not __plugin_instance:
		__plugin_instance = AdminPlugin()
		
	return __plugin_instance