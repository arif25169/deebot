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
# UnoPlugin.players = [
#	[player_index]:{
#			"nick":[player_nick],
#			"hand":[player_hand]
#		}
# ]

import random

import Plugin
import DeeIRC.Utils as Utils

from threading import Timer

# ------- Constants ------------------------------------------------------------

UNO_STATE_STOPPED = 0
UNO_STATE_STARTING = 1
UNO_STATE_STARTED = 2

# ------------------------------------------------------------------------------

class UnoPlugin(Plugin.Plugin):
	"""Uno plugin. Let's us play silly Uno games."""
	
	def load(self, bot):
		"""Add our commands and do initialization."""		
		self.addCommand("uno", self.commandUno)

		# Set the default state.
		self.state = UNO_STATE_STOPPED
		self.deck = None
		self.pile = None
		self.channel = None
		self.players = None
		self.turn_index = None
		self.reverse = False
		self.last_card = False
		
	# ------- Gameplay ---------------------------------------------------------
	
	def commandUno(self, bot, nick, target, message):
		"""Main uno command."""
		if self.state == UNO_STATE_STOPPED:			
			if not message:
				# Start Uno by initalizing the deck and pile.
				self.deck = self.createDeck()
				self.shuffleDeck(self.deck)
				self.pile = []
				
				# Setup the plugin for starting.
				self.channel = target
				self.state = UNO_STATE_STARTING
				
				# Setup the players.
				self.players = []
				self.addPlayer(bot, nick)
				
				# Start a timer.
				Timer(30.0, self.unoTimer, args=[bot]).start()
				
				# Print a message.
				bot.sendMessage(target, "Uno is starting in 30 seconds.")
		elif self.state == UNO_STATE_STARTING:
			if not message:
				# Add the player.
				self.addPlayer(bot, nick)
		elif self.state == UNO_STATE_STARTED:
			# Get the current player and card.
			player = self.players[self.turn_index]
			player_index = self.turn_index
		
			# Make sure it's the player using the command.
			if player["nick"] == nick:
				if message == "draw":
					# Move the cards from the deck to the player's hand.
					self.moveCards(self.deck, player["hand"], 1)
					
					# Send a message to the channel and send the player's hand.
					bot.sendMessage(target, player["nick"] + " drew a card.")
					self.sendPlayerHand(bot, player_index)
							
					# Run the next turn.
					self.doTurn(bot)
				else:
					# Assume a card was played.
					
					turn_played = False
					if message[1] == "w":
						# Wild card
						if message[2:4] == "d4" and "wd4" in player["hand"]:
							# Draw two.	Get the next player.
							next_player_index = self.getNextPlayerIndex()		
							next_player = self.players[next_player_index]
								
							# Move the cards from the deck to the player's hands.
							self.drawCards(next_player_index, 4)
				
							# Print a message and send the player their hand.
							bot.sendMessage(target, next_player["nick"] + " draws four cards.")
							self.sendPlayerHand(bot, next_player_index)	
												 	
							# Skip their turn.
							self.skipTurn()
							
							# Remove the card from the player.
							self.removeCardFromHand(player_index, "wd4")
							
							# mark that we played a turn.
							turn_played = True
						elif "w" in player["hand"]:
							# remove the card from the the palyer
							self.removeCardFromHand(player_index, "w")
							
							# we did indeed lpay a turn, derp.
							turn_played = True
					elif message[0] == self.last_card[0] or message[1] == self.last_card[1]:
						# Make sure the palyer actually has that card.
						if message in player["hand"]:							
							if message[1] == "r":
								# Reverse
								self.reverse = not self.reverse
							elif message[1] == "s":
								# Skip. Get the next player.	
								next_player = self.players[self.getNextPlayerIndex()]
								
								# Print out a message.							
								bot.sendMessage(target, next_player["nick"] + " skips their turn.")	
								
								# Skip their turn.
								self.skipTurn()		
							elif message[1:3] == "d2":
								# Draw two.	Get the next player.
								next_player_index = self.getNextPlayerIndex()		
								next_player = self.players[next_player_index]
								
								# Move the cards from the deck to the player's hands.
								self.moveCards(self.deck, next_player["hand"], 2)
				
								# Print a message and send the player their hand.
								bot.sendMessage(target, next_player["nick"] + " draws two cards.")			
								self.sendPlayerHand(bot, next_player_index)
								
								# Skip the turn.
								self.skipTurn()
					
							# Remove the card from the player's hand.
							self.removeCardFromHand(player_index, message)
						
							# Yep.
							turn_played = True
						
					if turn_played:			
						# Send a message to th channel and send the player's hand.
						bot.sendMessage(target, player["nick"] + " played " + self.cardString(message))			
						self.sendPlayerHand(bot, player_index)
						
						# HACKS
						self.last_card = message
						
						# Run the next turn.
						self.doTurn(bot)
		
		# Check if we're either starting or started.							
		if self.state == UNO_STATE_STARTING or self.state == UNO_STATE_STARTED:	
			if message == "stop":
				self.resetUno()
				
				# Print a message.
				bot.sendMessage(target, "Uno has stopped.")
	
	def drawCards(self, player_index, amount=1):
		"""Gives the player a new card."""
		self.moveCards(self.deck, self.players[player_index]["hand"])

	def removeCardFromHand(self, player_index, card):
		"""Removes a card from a players hand and puts it in the pile."""
		self.players[player_index]["hand"].remove(card)
		self.pile.append(card)
		
	def skipTurn(self):
		"""Skips the next turn."""
		self.turn_index = self.getNextPlayerIndex()
		
	def doTurn(self, bot):
		"""Initiates the current player's turn."""
		# Set the turn to the first player the turn index isn't set.
		# Else move on to the next player.
		if self.turn_index == None:
			self.turn_index = 0
		else:
			self.turn_index = self.getNextPlayerIndex()
								
		# Get the current player's info.
		player = self.players[self.turn_index]
		nick = player["nick"]
		hand = player["hand"]
		
		# Send them their hand.
		self.sendPlayerHand(bot, self.turn_index)
		
		# Print out messages to the channel.
		bot.sendMessage(self.channel, nick + "'s turn!")
	
	def resetUno(self):
		"""Resets the game variables."""
		# Stop the game.
		self.deck = None
		self.channel = None
		self.players = None
		self.turn_index = None
		self.reverse = False
		self.state = UNO_STATE_STOPPED
		
	#---------------------------------------------------------------------------

	def unoTimer(self, bot):
		"""Handles various timed functions."""
		if self.state == UNO_STATE_STARTING:
			if len(self.players) >= 0:
				# Start the game~
				self.state = UNO_STATE_STARTED
				
				# Send a message
				bot.sendMessage(self.channel, "Uno has started!")
				
				# Send the hand to each player, except the first.
				for i in range(1, len(self.players)):
					self.sendPlayerHand(bot, i)
				
				# Get one card face up.
				self.moveCards(self.deck, self.pile, 1)
				self.last_card = self.pile[0]
				
				# Send a message
				bot.sendMessage(self.channel, "Top card: " + self.cardString(self.last_card))
				
				# Start the turn.
				self.doTurn(bot)
			else:
				# Not enough players.
				bot.sendMessage(self.channel, "Not enough players for Uno.")
				self.resetUno()
	
	# ------- Player Helpers ---------------------------------------------------
	
	def addPlayer(self, bot, nick):
		"""Adds a player to the game."""
		if not self.isPlayerInGame(nick):
			self.players.append({"nick":nick, "hand":[]})
			self.moveCards(self.deck, self.players[len(self.players)-1]["hand"])
			
			bot.sendMessage(self.channel, nick + " added to player list.")
	
	def sendPlayerHand(self, bot, player_index):
		"""Sends a notice to a player with their current hand."""
		nick = self.players[player_index]["nick"]
		hand = self.players[player_index]["hand"]
		hand_string = self.deckString(hand)
			
		bot.sendNotice(nick, "Hand: " + hand_string)
	
	def getNextPlayerIndex(self, turns=1):
		"""Returns the index of the next player."""

		# LOOPS FOR SCIENCE!
		for i in range(turns+1):
			# reverse?
			if not self.reverse:
				next_index = self.turn_index + i
			else:
				next_index = self.turn_index - i
				
			# Wrap around back to the correct player.
			if next_index >= len(self.players):
				next_index = 0
			if next_index < 0:
				next_index = len(self.players) - 1
			
		return next_index
			
	def isPlayerInGame(self, nick):
		"""Returns True if player is in game."""
		for player in self.players:
			if player["nick"] == nick:
				return True
				
		return False
	
	# ------- Deck Helpers -----------------------------------------------------
	
	def createDeck(self):
		"""Creates an Uno deck."""
		colors = ["r", "g", "b", "y"]
		
		deck = []
		for i in range(4):
			deck.append(colors[i] + "0")
			
			for j in range(9):
				for k in range(2):
					deck.append(colors[i] + str(j+1))
			
			for j in range(2):	
				deck.append(colors[i] + "d2")
				deck.append(colors[i] + "s")
				deck.append(colors[i] + "r")
				
		for i in range(4):
			deck.append("w")
			deck.append("wd4")
					
		return deck
	
	def shuffleDeck(self, deck):
		"""Shuffles the deck."""
		random.shuffle(deck)
	
	def moveCards(self, deck_from, deck_to, amount=7):
		"""Moves cards from decks."""
		deck_to.extend(deck_from[0:amount])
		del deck_from[0:amount]
	
	def deckString(self, deck):
		"""Returns a string with all of the cards in the deck, colored."""
		deck_string = ""
		for i in range(len(deck)):
			deck_string = deck_string + self.cardString(deck[i]) + " "
			
		return deck_string
	
	# ------- Card Helpers -----------------------------------------------------

	def cardColorCode(self, card):
		"""Returns the appropriate colour code for a card."""
		colors = {
			"r":{"fg":0, "bg":4}, 
			"g":{"fg":0, "bg":3},
			"b":{"fg":0, "bg":12}, 
			"y":{"fg":1, "bg":8},
			"w":{"fg":0, "bg":1}
		}
		
		if len(card) == 2:
			if card[0] == "w":
				color = colors[card[1]]
			else:
				color = colors[card[0]]
		else:
			color = colors[card[0]]
			
		
		return Utils.colorCode(**color)
	
	def cardString(self, card):
		"""Returns the card name including colours."""
		return self.cardColorCode(card) + card + Utils.normalCode()
	
# ------- Plugin Loader --------------------------------------------------------

__plugin_instance = None
def getPluginInstance():
	global __plugin_instance
	
	if not __plugin_instance:
		__plugin_instance = UnoPlugin()
	return __plugin_instance