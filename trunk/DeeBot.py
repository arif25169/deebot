# DeeBot.py
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
#
# ------ Data Structures
#	DeeBot.plugins = {
#		"[plugin_name]":{
#			"module":[module_object], 
#			"instance":[instance_object],
#		}
#	}

import threading

import DeeIRC
import DeeIRC.Utils as Utils

import Plugin
import Events

# ------------------------------------------------------------------------------

class DeeBot(DeeIRC.IRC.DeeIRC):
	"""DeeBot!"""
	
	def __init__(self):
		"""Constructor"""
		self.debug = False # set debug before calling init
		super(DeeBot, self).__init__("DeeBot")
		
		# Config
		self.config = {}
		self.config["server"] = "irc.synirc.org"
		self.config["channels"] = ["#glasnost", "#underwares"]
		self.config["command_prefix"] = "?" 
		self.config["admins"] = ["Knifa"]
		self.config["plugins"] = ["Admin", "Uno"]
		
		# Add events.
		self.addEvent("connected", Events.ConnectedEvent())
		self.addEvent("message", Events.MessageEvent())
			
		# Plugin modules are loaded into the plugin dictionary, with the key
		# being the name of the module.
		self.plugins = {}
		
		# Load plugins.
		for plugin in self.config["plugins"]:
			self.loadPlugin(plugin)
	
	# ------ Loop --------------------------------------------------------------
	
	def run(self):
		"""Runs continously in it's own thread, calling plugin think functions.
		and other things.
		
		Neccessary for timers, etc."""
		self.connect(self.config["server"])
			
	# ------ Plugin helpers ----------------------------------------------------
	
	def loadPlugin(self, plugin_name):
		"""Loads a plugin"""
		try:
			# Get the full import string and import the module
			import_path = "Plugin." + plugin_name
			plugin_module = __import__(import_path, globals(), locals(), plugin_name)
			
			# Get the instance of the plugin and load it.
			plugin = plugin_module.getPluginInstance()
			plugin.load(self)
			
			# Add it into the dictionary.
			self.plugins[plugin_name] = {
				"module":plugin_module,
				"instance":plugin,
			}				

			# Log it.
			self.log("Loaded plugin(" + plugin_name + ")")
		except Exception, e:
			self.error("Failed to load plugin(" + plugin_name + "): " + str(e))
			raise # pass so calling function can manage it.
		
	def reloadPlugin(self, plugin_name):
		"""Reloads a plugin"""
		if self.hasPlugin(plugin_name):
			# Reload the actual module file.
			reload(self.plugins[plugin_name]["module"])
			
			# Run the unload/load functions on it.
			self.unloadPlugin(plugin_name)
			self.loadPlugin(plugin_name)
			
	def unloadPlugin(self, plugin_name):
		"""Unloads a plugin."""
		if self.hasPlugin(plugin_name):		
			# Run the unload method.
			self.getPlugin(plugin_name).unload(self)
		
			# Delete the plugin and log a message.
			del self.plugins[plugin_name]
			self.log("Unloaded plugin(" + plugin_name + ")")
	
	def hasPlugin(self, plugin_name):
		"""Returns true if a plugin is loaded, otherwise false"""
		if plugin_name in self.plugins:
			return True
		else:
			return False
	
	def getPlugin(self, plugin_name):
		"""Returns a plugin instance."""
		if plugin_name in self.plugins:
			return self.plugins[plugin_name]["module"].getPluginInstance()
		else:
			return None
			
	# ------ Command helpers ---------------------------------------------------
	
	def findPluginFromTrigger(self, trigger):
		"""Returns the plugin name if a command exists, otherwise none"""
		trigger = trigger.lower() # lowercase!
		
		# Loop through all plugins.
		for plugin_name in self.plugins:
			plugin = self.getPlugin(plugin_name)
			
			# Check if the plugin has that trigger.
			if plugin.hasCommand(trigger):
				return plugin_name
		
		# Not found :(
		return None
			
	# ------ User helpers ------------------------------------------------------
	
	def isAdmin(self, nick):
		"""Returns if a user is an admin or not"""
		if nick in self.config["admins"]:
			return True
		else:
			return False
			
	# ------ Error Messages and Logging ----------------------------------------
	
	def error(self, message, **args):
		"""Prints errors to console or channel. Overrides default one.
		
		args:
			target: Channel/user to output to.
			console: Boolean saying if we should output to console or not."""
		error_message = Utils.boldCode() + "Error: " + Utils.normalCode() + message
		
		if args.has_key("target"):
			self.sendMessage(args["target"], error_message)
			
		if args.has_key("console"):
			if args["console"]:
				print self.errorTime(), "<ERROR>", Utils.stripCodes(message)
		else:
			print self.errorTime(), "<ERROR>", Utils.stripCodes(message)
			
# ------------------------------------------------------------------------------

if __name__ == "__main__":
	print "DeeBot (SVN)"
	print "--- Now with additional butts."
	print
	
	bot = DeeBot()
	bot.run()