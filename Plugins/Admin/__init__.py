# ------ Plugin Management

def loadPluginCommand(self, nick, target, message):
	"""Called when an admin requests to load a plugin."""
	if self.isAdmin(nick):	
		try:
			# Attempt to load a plugin.
			self.loadPlugin(message)
		except:
			# Oh noes!
			self.error("Unable to load " + self.boldCode() + message + 
				self.normalCode() + ".", target=target, console=False)
		else:
			# It all went okay.
			self.sendMessage(target, "Loaded " + message)
			
def unloadPluginCommand(self, nick, target, message):
	"""Called when an admin requests to unload a plugin"""
	if self.isAdmin(nick):
		self.unloadPlugin(message)
			
def reloadAllPluginCommand(self, nick, target, message):
	"""Called when an admin requests to reload all plugins."""
	if self.isAdmin(nick):
		# Loop through all plugins and reload them.
		for plugin in self.plugins:
			self.reloadPlugin(plugin)
			
	self.sendMessage(target, "Reloaded plugins.")
		
def listPluginsCommand(self, nick, target, message):
	"""Called when a user requests a list of all plugins."""
	loaded_plugins = ""
	
	# Loop through all plugins and add their name to the string.
	for plugin in self.plugins:
		loaded_plugins = loaded_plugins + plugin + " "
		
	self.sendMessage(target, "Plugins: " + loaded_plugins)

# ------ Channel Management

def joinCommand(self, nick, target, message):
	if self.isAdmin(nick):
		self.sendJoin(message)
		
def partCommand(self, nick, target, message):
	if self.isAdmin(nick):
		self.sendPart(message)
		
# ------ Main Management

def quitCommand(self, nick, target, message):
	if self.isAdmin(nick):
		self.disconnect()
		
def nickCommand(self, nick, target, message):
	if self.isAdmin(nick):
		self.sendNick(message)

# ------------------------------------------------------------------------------
def pluginLoad(self):
	self.addCommand("Admin", "load", loadPluginCommand)
	self.addCommand("Admin", "unload", unloadPluginCommand)
	self.addCommand("Admin", "reloadall", reloadAllPluginCommand)
	self.addCommand("Admin", "list", listPluginsCommand)
	
	self.addCommand("Admin", "join", joinCommand)
	self.addCommand("Admin", "part", partCommand)
	
	self.addCommand("Admin", "quit", quitCommand)
	self.addCommand("Admin", "nick", nickCommand)