# Report
## Report Details


## Questions
1) Why doesn't the bot avoid the radiation in the default map? What would have to be different for the bot to avoid as much of it as possible?

2) Under the default reward, the bot runs away from the enemy. What is the largest value for enemyDead that would make it so that the bot is willing to kill the enemy if they cross paths. Explain why. What is the smallest value for enemyDead that would induce the bot to seek out the enemy and kill it. Explain why.

3) What effect does switching enemyMode from 1 (follow the influence map) to 2 during training have on the behavior of the bot, if any? How does more or less training episodes help or hurt? Hint: experiment with play = 2.

## Answers

1) The penalty for radiation is very small. It only affects the bot if it stays in the radiation. So passing through the radiation twice (once to go rescue the human, and once to come back to home base) is a very small sacrifice to get the 10 additional reward per turn for rescuing the human. If the radiation somehow stuck to the bot and cause a penalty on a per turn basis, then the bot would be less inclined to pass through the radiation in order to rescue the human. I believe that even if the entire path to the human was lined with radiation, the bot would still learn to get the humans. Traveling through the radiation would still only cause a static amount of penalty, but rescuing the humans provides a steady stream of reward.

2)

3) I found that training takes more trials when the enemy is set to move randomly. This makes sense because when the enemy uses the heat map the bot can observe a repeated pattern in the enemies movement and therefore learn quicker. In this example map, the bot learns that when the enemy is on the home base it will always move up on the next turn unless it can torture. So the bot simply has to move off for one move, then back on. Whereas if the enemy is moving randomly, then the enemy could potentially linger on the home base for a while before moving off. This requires a bit more learning to know to wait until the enemy moves off the base before moving back on to the home base. During execution, if the enemy is set to move according to the heat map, the behaviors will appear the same. The bot will wait until the enemy is on the base with it, then move off the base on the next turn. In either training case, the bot will know to move back on to the base because it is now safe, for at least one turn, to be there.

Interestingly, if the bot is trained using the heat map enemy but executed using the random enemy, there is a noticeable decrease in reward. In this case the bot expects the enemy to act in a predictable but the bot acts randomly and sometimes confuses the bot. Training the bot on a random enemy makes the bot much more capable against a random bot.
