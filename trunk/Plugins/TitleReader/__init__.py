def titleReader(self, nick, target, message):
	if self.isAdmin(nick):
		self.sendNick(message)

# ------------------------------------------------------------------------------
def pluginLoad(self):
	self.addCommand("TitleReader", "*", titleReader)