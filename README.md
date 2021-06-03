# Verfuchst - A Gamer for Four Players
[![CodeFactor](https://www.codefactor.io/repository/github/yths/yths.verfuchst/badge/main)](https://www.codefactor.io/repository/github/yths/yths.verfuchst/overview/main)
## Introduction
The purpose of this project is foremost to teach me different concepts of software engineering, data science and design; and thus might seem overengineered or unnecessarily complicated in some places. As a side effect a little game called "Verfuchst" is developed.
## Rules of the Game
"Verfuchst" is game for at least two to (currently) up to four placers. Each player has three pieces, which are located at the start tile and have to reach the goal tile by traversing a path of score tiles. On a players turn, they first roll a six-sided die and then move one of their pieces according to the die roll towards the goal. They are free to choose among their remaining pieces - pieces that reach the goal tile are taken out of the game. If a piece reaches the goal with less steps than the die roll would allow, the remaining steps expire. If a piece leaves a score tile and the score tile is not occupied by another piece or a guardian, the player has to take the score tile. The gap in the path that is created by taking a score tile is ignored by subsequent moves of pieces. Guardians are neutral pieces that initially are distributed on the score tiles of the path. On a players turn, they can move a guardian instead of their own piece - if the guardian shares a score tile with a piece of any player (not necessarily their own). There are three different types of score tiles - score tiles with positive score, with negative score and lucky tiles that turn negative score tiles into positive score tiles. The winner of the game is the player who collected score tiles that sum up to the highest value. Lucky tiles always turn the score tile with the most negative score into a positive score. If the player has more lucky tiles than negative tiles, the superfluous lucky tiles are ignored.
