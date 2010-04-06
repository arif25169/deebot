def nicksCommand(self, nick, target, message):
	self.sendMessage(target, str(self.channels[target]["nicks"]))

def execCommand(self, nick, target, message):
	if self.isAdmin(nick):
		try:
			exec(message)
		except Exception, e:
			self.sendMessage(target, str(e))
			
def evalCommand(self, nick, target, message):
	if self.isAdmin(nick):
		try:
			eval_result = eval(message)
		except Exception, e:
			self.sendMessage(target, str(e))
		else:
			self.sendMessage(target, "eval(" + message + ") = " + str(eval_result))
		
# ------------------------------------------------------------------------------
def pluginLoad(self):
	self.addCommand("Debug", "nicks", nicksCommand)
	self.addCommand("Debug", "exec", execCommand)
	self.addCommand("Debug", "eval", evalCommand)