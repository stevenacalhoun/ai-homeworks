package dk.itu.mario.engine;


import dk.itu.mario.engine.PlayerProfile;
import dk.itu.mario.engine.level.Level;
import dk.itu.mario.engine.sprites.Enemy;

//This player profile is an even mix of the Scrooge and Killer profiles
public class JumperCollector extends PlayerProfile{
	//evaluation for this player profile
	//returns a number bounded from 0 to 1
	public double evaluateLevel(Level level)
	{


		boolean[] jumpInChunk = new boolean[50];

		for (int x = 0; x<200; x++){
			boolean isGap = true;
			for (int y = 13; y<15; y++){
				if(level.getBlock(x,y)!=Level.EMPTY){
					isGap = false;
					break;
				}
			}

			if(isGap){
				jumpInChunk[(int)x/4]=true;
			}
			else{
				if ( (level.getBlock(x,12) == Level.TUBE_SIDE_LEFT && level.getBlock(x,13)==Level.HILL_TOP ) || (level.getBlock(x,12) == Level.ROCK && level.getBlock(x,13)==Level.HILL_TOP ) || (level.getBlock(x,12) == Level.CANNON_BASE && level.getBlock(x,13)==Level.HILL_TOP ) || (level.getBlock(x,12) == Level.CANNON_MID && level.getBlock(x,13)==Level.HILL_TOP ) || (level.getBlock(x,12) == Level.CANNON_TOP && level.getBlock(x,13)==Level.HILL_TOP ) ){
					jumpInChunk[(int)(x/4)] = true;
				}
			}
		}


		double jumpScore = 0.0;
		double numJumps = 0.0;

		for(int i = 0; i<jumpInChunk.length; i++){
			if(jumpInChunk[i]){
				numJumps+=1.0;
			}
		}

		jumpScore = numJumps/50.0;

		if (jumpScore>1.0){
			jumpScore = 1.0;
		}

		// Coin score
		int numCoins = 0;

		int prevYMin = 12;
		for (int x = 0; x<level.getWidth(); x++){
			int currYMin = 12;
			for (int y = level.getHeight()-2; y>0; y--){
				if (level.getBlock(x,y) == Level.HILL_TOP || level.getBlock(x,y) == Level.CANNON_TOP || level.getBlock(x,y) == Level.TUBE_TOP_LEFT || level.getBlock(x,y) == Level.TUBE_TOP_RIGHT || level.getBlock(x,y) == Level.ROCK){
					currYMin = y;
				}
				if (level.getBlock(x,y) == Level.COIN || (level.getBlock(x,y) == Level.BLOCK_COIN && level.getBlock(x,y+1) == Level.EMPTY) ){
					if(Math.abs(y-currYMin)<5 && Math.abs(y-prevYMin)<5){
						numCoins +=1;
					}
				}

			}
			prevYMin = currYMin;
		}


		double coinScore = 0.0;
		coinScore = numCoins/100.0;

		if (coinScore>1.0){
			coinScore = 1.0;
		}

		double score = ((coinScore + jumpScore) / 2.0) * (1 - (Math.abs(numCoins-2*numJumps)/(numCoins+2*numJumps)));

		return score;
	}
}
