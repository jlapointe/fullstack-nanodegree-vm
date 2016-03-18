-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.


CREATE TABLE players(
	id serial primary key,
	name text
);

CREATE TABLE matches(
	id serial primary key,
	winner integer REFERENCES players(id),
	loser integer REFERENCES players(id)
);

CREATE VIEW matches_count AS 
	SELECT players.id, count(matches.id) AS count
	FROM players LEFT JOIN matches 
		ON matches.winner = players.id OR matches.loser = players.id 
		GROUP BY players.id
	ORDER BY players.id;

CREATE VIEW wins_count AS
	SELECT players.id, count(matches.id) AS count
	FROM players LEFT JOIN matches 
		ON matches.winner = players.id
		GROUP BY players.id
	ORDER BY players.id;

CREATE VIEW results_table AS
	SELECT matches_count.id, matches_count.count AS m, wins_count.count AS w
	FROM wins_count JOIN matches_count 
		ON wins_count.id = matches_count.id;

CREATE VIEW player_standings AS
	SELECT ROW_NUMBER() OVER(ORDER BY w desc) as num, players.id, name, w, m 
	FROM players JOIN results_table 
		ON players.id=results_table.id 
	ORDER BY w desc;

CREATE VIEW odd_standings AS
	SELECT row_number() OVER(ORDER BY p1.num) as i, p1.num AS num1, id, name 
	FROM player_standings AS p1 
	WHERE p1.num%2=1;

CREATE VIEW even_standings AS
	SELECT row_number() OVER(ORDER BY p2.num) as i, p2.num AS num2, id, name 
	FROM player_standings AS p2 
	WHERE p2.num%2=0;

CREATE VIEW swiss_pairings AS
	SELECT s1.id AS id1, s1.name AS name1, s2.id AS id2, s2.name as name2 
	FROM odd_standings AS s1 JOIN even_standings AS s2 
		ON s1.i=s2.i;
