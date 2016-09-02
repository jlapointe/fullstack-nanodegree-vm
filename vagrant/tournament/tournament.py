#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match records from the database."""
    db = connect()
    cursor = db.cursor()
    query = "DELETE FROM matches *;"
    cursor.execute(query)
    db.commit()
    db.close()
    return

def deletePlayers():
    """Remove all the player records from the database."""
    db = connect()
    cursor = db.cursor()
    query = "DELETE FROM players *;"
    cursor.execute(query)
    db.commit()
    db.close()
    return

def countPlayers():
    """Returns the number of players currently registered."""
    db = connect()
    cursor = db.cursor()
    query = "SELECT count(*) FROM players;"
    cursor.execute(query)
    result = cursor.fetchall()[0][0] #Return the value of the count, not the list that stores it
    db.close()
    return result

def registerPlayer(name):
    """Adds a player to the tournament database.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).
    """
    db = connect()
    cursor = db.cursor()
    query = "INSERT INTO players (name) VALUES (%s)"
    cursor.execute(query, (name,)) #Prevent injection attack
    db.commit()
    db.close()
    return

def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """

    """results_table is a view containing the number of matches and wins for each player id"""

    query = "SELECT id, name, w, m FROM player_standings;"
    db = connect()
    cursor = db.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    db.close()

    return result


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """

    query = "INSERT INTO matches(winner,loser) VALUES(%s,%s);" #Prevent injection attack
    db = connect()
    cursor = db.cursor()
    cursor.execute(query, (winner,loser))
    db.commit()
    db.close()

    return
 
def swissPairings():
    """Returns a list of pairs of players for the next round of a match.
  
    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.
  
    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name 
    """
    #Assuming an even number of players, generate a list of tuples from the standings list.

    db = connect()
    cursor = db.cursor()
    query = "SELECT id1, name1, id2, name2 FROM swiss_pairings";
    cursor.execute(query)
    result = cursor.fetchall()
    db.close()

    return result
