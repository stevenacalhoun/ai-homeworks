package dk.itu.mario.engine;


import dk.itu.mario.engine.PlayerProfile;
import dk.itu.mario.engine.level.Level;
import dk.itu.mario.engine.sprites.Enemy;

//This player profile is an even mix of the Scrooge and Killer profiles
public class KillerJumper extends PlayerProfile{
	//evaluation for this player profile
	//returns a number bounded from 0 to 1
	public double evaluateLevel(Level level)
	{


		boolean[] enemyInChunk = new boolean[50];

		for (int x = 0; x<200; x++){
			for (int y = level.getHeight()-2; y>0; y--){
				if ( level.getSpriteTemplate(x,y)!=null && (level.getSpriteTemplate(x,y).type == Enemy.ENEMY_RED_KOOPA || level.getSpriteTemplate(x,y).type == Enemy.ENEMY_GREEN_KOOPA || level.getSpriteTemplate(x,y).type == Enemy.ENEMY_GOOMBA) ){
					enemyInChunk[(int)(x/4)] = true;
				}
			}
		}


		double killerScore = 0.0;
		double numTrues = 0.0;

		for(int i = 0; i<enemyInChunk.length; i++){
			if(enemyInChunk[i]){
				numTrues+=1.0;
			}
		}

		killerScore = numTrues/50.0;

		if (killerScore>1.0){
			killerScore = 1.0;
		}

		// Jump score
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

		double score = ((jumpScore + killerScore) / 2.0) * (1 - (Math.abs(numJumps-numTrues)/(numJumps+numTrues)));

		return score;
	}
}
