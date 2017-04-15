# Report
## Report Details


## Questions
1) Why doesn't the bot avoid the radiation in the default map? What would have to be different for the bot to avoid as much of it as possible?

2) Under the default reward, the bot runs away from the enemy. What is the largest value for enemyDead that would make it so that the bot is willing to kill the enemy if they cross paths. Explain why. What is the smallest value for enemyDead that would induce the bot to seek out the enemy and kill it. Explain why.

3) What effect does switching enemyMode from 1 (follow the influence map) to 2 during training have on the behavior of the bot, if any? How does more or less training episodes help or hurt? Hint: experiment with play = 2.

## Answers

1) The penalty for radiation is very small. It only affects the bot if it stays in the radiation. So passing through the radiation twice (once to go rescue the human, and once to come back to home base) is a very small sacrifice to get the 10 additional reward per turn for rescuing the human. If the radiation somehow stuck to the bot and cause a penalty on a per turn basis, then the bot would be less inclined to pass through the radiation in order to rescue the human. I believe that even if the entire path to the human was lined with radiation, the bot would still learn to get the humans. Traveling through the radiation would still only cause a static amount of penalty, but rescuing the humans provides a steady stream of reward.

2) 

3)
