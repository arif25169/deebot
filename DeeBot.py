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
#			"commands":{
#				"[trigger]":[command_function]
#			}		
#		}
#	}

import DeeIRC.IRC
import threading

class DeeBot(DeeIRC.IRC.DeeIRC):
	"""DeeBot!"""
	
	def __init__(self):
		"""Constructor"""
		self.debug = True # set debug before calling init
		super(DeeBot, self).__init__("DeeBot")
		
		# Config
		self.config = {}
		self.config["server"] = "irc.synirc.org"
		self.config["channels"] = ["#glasnost"]
		self.config["command_prefix"] = "!" 
		self.config["admins"] = ["Knifa"]
		
		# Add events.
		self.addEvent("connected", DeeBot.eventConnected_JoinChannels)
		self.addEvent("message", DeeBot.eventMessage_RunCommands)
		self.addEvent("disconnected", DeeBot.eventDisconnected)
			
		# Plugin modules are loaded into the plugin dictionary, with the key
		# being the name of the module.
		self.plugins = {}
		
		# Load base plugins.
		self.loadPlugin("Admin")
		if self.debug:
			self.loadPlugin("Debug")
		
		# Run the main loop in a thread, because that is cool.
		self.loop_thread = threading.Thread(target=self.run)
		self.loop_thread.start()
		self.loop_running = True
	
	# ------ Loop
	
	def run(self):
		"""Runs continously in it's own thread, calling plugin think functions.
		and other things.
		
		Neccessary for timers, etc."""
		self.connect(self.config["server"])
		self.loop_running = True
		
		while self.loop_running == True:
			# Lock the thread so we can loop through the plugins.	
			lock = threading.Lock()
			lock.acquire()
			
			# Loop through the plugins and call their loop function.
			for plugin in self.plugins:
				if self.plugins.has_key(plugin):
					plugin_module = self.plugins[plugin]["module"]
							
					# If they have one.
					if "pluginLoop" in dir(plugin_module):
						plugin_module.pluginLoop(self)
			
			# Release the lock.			
			lock.release()
			
	# ------ Plugin helpers
	
	def loadPlugin(self, plugin_name):
		"""Loads a plugin"""
		try:
			# Get the full import string.
			plugin_import = "Plugins." + plugin_name
			
			# Try load the plugin into the dictionary.
			self.plugins[plugin_name] = {"module":__import__(plugin_import, globals(), 
				locals(), plugin_name), "commands":{}}
				
			# Run the initalization command.
			self.plugins[plugin_name]["module"].pluginLoad(self)
		
			# Log it.
			self.log("Loaded plugin(" + plugin_name + ")")
		except:
			self.error("Failed to load plugin(" + plugin_name + ")")
			raise # pass so calling function can manage it.
		
	def reloadPlugin(self, plugin_name):
		"""Reloads a plugin"""
		if self.hasPlugin(plugin_name):
			# Basically just unloads and reloads them.
			reload(self.plugins[plugin_name]["module"])
			self.unloadPlugin(plugin_name)
			self.loadPlugin(plugin_name)
			
	def unloadPlugin(self, plugin_name):
		"""Unloads a plugin."""
		# Make sure the plugin exists first.
		if self.hasPlugin(plugin_name):		
			# Delete the plugin and log a message.
			del self.plugins[plugin_name]
			self.log("Unloaded plugin(" + plugin_name + ")")
	
	def hasPlugin(self, plugin_name):
		"""Returns true if a plugin is loaded, otherwise false"""
		if self.plugins.has_key(plugin_name):
			return True
		else:
			return False
			
	# ------ Command helpers
	
	def addCommand(self, plugin_name, trigger, function):
		"""Adds a command to the command dictionary."""
		trigger = trigger.lower()
			
		self.plugins[plugin_name]["commands"][trigger] = function
		self.log("Added command(" + plugin_name +":" + trigger + "): " + str(function))
		
	def removeCommand(self, trigger):
		"""Removes a command."""
		trigger = trigger.lower()
		
		plugin = self.findPluginFromTrigger(trigger)
		if plugin:
			del self.plugins[plugin][trigger]
			self.log("Removed command(" + trigger + ")")
	
	def findPluginFromTrigger(self, trigger_find):
		"""Returns the plugin name if a command exists, otherwise none"""
		trigger_find = trigger_find.lower()
		
		for plugin_name in self.plugins:
			plugin = self.plugins[plugin_name]
			
			for trigger in plugin["commands"]:
				if trigger == trigger_find:
					return plugin_name
		
		return None
			
	# ------ User helpers
	
	def isAdmin(self, nick):
		"""Returns if a user is an admin or not"""
		if nick in self.config["admins"]:
			return True
		else:
			return False
			
	# ------ Events
	
	def eventConnected_JoinChannels(self):
		"""Joins the configured channels on connect."""
		for channel in self.config["channels"]:
			self.sendJoin(channel)
			
	def eventMessage_RunCommands(self, nick, target, message):
		"""Checks if a command has been said and run it if so."""
		if message[0] == self.config["command_prefix"]:
			# Get the command from the message.
			trigger_end = message.find(" ")
			if not trigger_end >= 0:
				# No parameters.
				trigger_end = len(message)
			trigger = message[1:trigger_end].lower()

			# If the command exists, run the function.
			plugin = self.findPluginFromTrigger(trigger)
			if plugin:
				self.plugins[plugin]["commands"][trigger](self, nick, target, message[trigger_end+1:])
				
				if self.debug:
					self.log("Command(" + plugin + ":" + trigger + "): " + str(self.plugins[plugin]["commands"][trigger]))
		else:
			# Run commands which do not rely on an actual trigger.
			for plugin in self.plugins:
				plugin_dict = self.plugins[plugin]
				
				if "*" in plugin_dict["commands"]:
					plugin_dict["commands"]["*"](self, nick, target, message)
					
					if self.debug:
						self.log("Command(" + plugin + ":*): " + str(plugin_dict["commands"]["*"]))
						
	def eventDisconnected(self):
		"""Kills the main thread when we disconnect."""
		self.loop_running = False
			
	# ------ Error Messages and Logging
	
	def error(self, message, **args):
		"""Prints errors to console or channel. Overrides default one.
		
		args:
			target: Channel/user to output to.
			console: Boolean saying if we should output to console or not."""
		error_message = self.boldCode() + "Error: " + self.normalCode() + message
		
		if args.has_key("target"):
			self.sendMessage(args["target"], error_message)
			
		if args.has_key("console"):
			if args["console"]:
				print self.errorTime(), "<ERROR>", self.stripCodes(message)
		else:
			print self.errorTime(), "<ERROR>", self.stripCodes(message)
	
if __name__ == "__main__":
	bot = DeeBot()