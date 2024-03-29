package dk.itu.mario.engine.level;
import java.util.*;
import dk.itu.mario.MarioInterface.Constraints;
import dk.itu.mario.MarioInterface.GamePlay;
import dk.itu.mario.MarioInterface.LevelInterface;
import dk.itu.mario.engine.sprites.SpriteTemplate;
import dk.itu.mario.engine.sprites.Enemy;
import dk.itu.mario.engine.level.MyDNA;

//To Run: java -cp bin dk.itu.mario.engine.PlayCustomized [PLAYER_TYPE]
public class MyLevel extends Level{
  //Store information about the level
  public   int ENEMIES = 0; //the number of enemies the level contains
  public   int BLOCKS_EMPTY = 0; // the number of empty blocks
  public   int BLOCKS_COINS = 0; // the number of coin blocks
  public   int BLOCKS_POWER = 0; // the number of power blocks
  public   int COINS = 0; //These are the coins in boxes that Mario collect

  private Random random;

  private static final int STARTOFFSET = 5;
  private static final int EXITOFFSET = 5;
  private static final int EXITPOSITION = 3; // number of blocks from the end
  private static final int DEFAULTHEIGHT = 15;

  public MyLevel(int width, int height) {
    super(width, height);
    random = new Random();
  }

  public MyLevel(MyDNA dna, int type) {
    // Add 10 units for the beginning platform and exit platform
    this(205, 15);
    create(dna, type);
  }

  public void create(MyDNA dna, int type) {
    //Initial starting platform is 3 blocks wide and flat ground.
    for (int x = 0; x < STARTOFFSET; x++) {
      this.setBlock(x, DEFAULTHEIGHT-2, HILL_TOP);
      this.setBlock(x, DEFAULTHEIGHT-1, GROUND);
    }

    // Start your level at block index STARTOFFSET.
    //// YOUR CODE GOES BELOW HERE ////

    // Keep up with current world loc
    int currentWorldLoc = STARTOFFSET;

    int chunkWidth = 10;
    // Generate each letter of the chromosome
    for (int i=0;i<dna.length;i++) {
      // Last chunk needs to be 5 wide
      if (i == dna.length - 1) {
        chunkWidth = 5;
      }

      switch (dna.chromosome.charAt(i)) {
        // Hill, safe
        case 'a':
          currentWorldLoc += this.buildHillStraight(currentWorldLoc, chunkWidth, 0);
          break;

        // Hill, easy
        case 'b':
          currentWorldLoc += this.buildHillStraight(currentWorldLoc, chunkWidth, 10);
          break;

        // Hill, medium
        case 'c':
          currentWorldLoc += this.buildHillStraight(currentWorldLoc, chunkWidth, 20);
          break;

        // Hill, hard
        case 'd':
          currentWorldLoc += this.buildHillStraight(currentWorldLoc, chunkWidth, 30);
          break;

        // Jump
        case 'e':
          currentWorldLoc += this.buildJump(currentWorldLoc, chunkWidth);
          break;

        // Straight, safe
        case 'f':
          currentWorldLoc += this.buildStraight(currentWorldLoc, chunkWidth, false, 0);
          break;

        // Straight, easy
        case 'g':
          currentWorldLoc += this.buildStraight(currentWorldLoc, chunkWidth, false, 10);
          break;

        // Straight, med
        case 'h':
          currentWorldLoc += this.buildStraight(currentWorldLoc, chunkWidth, false, 20);
          break;

        // Straight, hard
        case 'i':
          currentWorldLoc += this.buildStraight(currentWorldLoc, chunkWidth, false, 30);
          break;

        // Tubes, easy
        case 'j':
          currentWorldLoc += this.buildTubes(currentWorldLoc, chunkWidth, 10);
          break;

        // Tubes, med
        case 'k':
          currentWorldLoc += this.buildTubes(currentWorldLoc, chunkWidth, 20);
          break;

        // Tubes, hard
        case 'l':
          currentWorldLoc += this.buildTubes(currentWorldLoc, chunkWidth, 30);
          break;

        // Cannons
        case 'm':
          currentWorldLoc += this.buildCannons(currentWorldLoc, chunkWidth);
          break;

        // Jump land, safe
        case 'n':
          currentWorldLoc += this.buildJumpLand(currentWorldLoc, chunkWidth, 0);
          break;

        // Jump land, easy
        case 'o':
          currentWorldLoc += this.buildJumpLand(currentWorldLoc, chunkWidth, 10);
          break;

        // Jump land, medium
        case 'p':
          currentWorldLoc += this.buildJumpLand(currentWorldLoc, chunkWidth, 20);
          break;

        // Jump land, hard
        case 'q':
          currentWorldLoc += this.buildJumpLand(currentWorldLoc, chunkWidth, 30);
          break;
      }
    }

    // Clean it up
    this.fixWalls();

    //// YOUR CODE GOES ABOVE HERE ////

    // Final exit is on flat ground in the last 3 blocks.
    for (int x = width-EXITOFFSET; x < width; x++) {
      this.setBlock(x, DEFAULTHEIGHT-2, HILL_TOP);
      this.setBlock(x, DEFAULTHEIGHT-1, GROUND);
    }

    xExit = width-EXITPOSITION;
    yExit = DEFAULTHEIGHT-2;
  }

  /* BELOW HERE ARE EXAMPLE FUNCTIONS FOR HOW TO CREATE SOME INTERESTING STRUCTURES */

  public int buildJumpLand(int xo, int length, int difficulty) {
    int floor = height - 1 - random.nextInt(4);
    floor = 13;
    int block = xo;
    boolean placedBlock = false;
    int highestJump = -1;

    for (int x = xo; x < xo + length; x++) {
      if (placedBlock) {
        placedBlock = false;
        block += 3;
      }

      // Random jump height
      int jumpHeight = floor - random.nextInt(4) - 1;

      if ((jumpHeight < highestJump) || (highestJump == -1)) {
        highestJump = jumpHeight;
      }

      for (int y = 0; y < height; y++) {
        // Paint ground under floor
        if (y >= floor) {
          if (y==floor) {
            setBlock(x, y, HILL_TOP);
          }
          else {
            setBlock(x, y, GROUND);
          }
        }
        else {
          if (x == block && y >= jumpHeight) {
            setBlock(x, y, Level.ROCK);
            placedBlock = true;
          }
        }
      }
    }

    decorate(xo + 1, xo + length - 1, highestJump, difficulty);

    return length;
  }

  //A built in function for helping to build a jump
  public int buildJump(int xo, int length) {
    //jl: jump length
    //js: the number of blocks that are available at either side for free
    int js = 3;
    int jl = 4;

    boolean hasStairs = random.nextInt(3) == 0;

    if (length == 5) {
      hasStairs = false;
      js = 1;
      jl = 2;
    }

    int floor = height - 1 - random.nextInt(4);
    // Run from the start x position, for the whole length
    for (int x = xo; x < xo + length; x++) {

      // Paint left and right sides
      if (x < xo + js || x > xo + length - js - 1) {

        // Paint all blocks beneath hilltop
        for (int y = 0; y < height; y++) {
          // We've reached the start
          if (y >= floor) {
            // Hill top
            if (y==floor) {
              if ((x == xo+js-1) || (x==xo+length-1)) {
                setBlock(x, y, HILL_TOP_RIGHT_IN);
              }
              else if ((x == xo + length - js) || (x == xo)) {
                setBlock(x, y, HILL_TOP_LEFT_IN);
              }
              else {
                setBlock(x, y, HILL_TOP);
              }
            }

            // Hill underneath
            else {
              // Right side
              if ((x == xo+js-1) || (x == xo+length-1)) {
                setBlock(x, y, HILL_RIGHT);
              }

              // Left side
              else if ((x == xo + length - js) || (x == xo)) {
                setBlock(x, y, HILL_LEFT);
              }

              //
              else {
                if (x == xo) {
                  setBlock(x, y, HILL_LEFT);
                }
                else if (x == xo + length-1) {
                  setBlock(x, y, HILL_RIGHT);
                }
                else {
                  setBlock(x, y, GROUND);
                }
              }
            }
          }
          //if it is above ground, start making stairs of rocks
          else if (hasStairs) {
            //LEFT SIDE
            if (x < xo + js) {
              //we need to max it out and level because it wont
              //paint ground correctly unless two bricks are side by side
              if (y >= floor - (x - xo) + 1) {
                setBlock(x, y, ROCK);
              }
            }
            else {
              //RIGHT SIDE
              if (y >= floor - ((xo + length) - x) + 2) {
                setBlock(x, y, ROCK);
              }
            }
          }
        }
      }
    }
    return length;
  }

  //A built in function for helping to build a cannon
  public int buildCannons(int xo, int length) {
    int floor = height - 1 - random.nextInt(4);
    int xCannon = xo + 1 + random.nextInt(4);
    for (int x = xo; x < xo + length; x++) {

      // Space each cannon by 2-6
      if (x > xCannon) {
        xCannon += 2 + random.nextInt(4);
      }
      if (xCannon == xo + length - 1) xCannon += 10;

      // Random cannon height
      int cannonHeight = floor - random.nextInt(4) - 1;

      for (int y = 0; y < height; y++) {
        // Paint ground under floor
        if (y >= floor) {
          if (y==floor) {
            setBlock(x, y, HILL_TOP);
          }
          else {
            setBlock(x, y, GROUND);
          }
        }
        else {
          if (x == xCannon && y >= cannonHeight) {
            if (y == cannonHeight) {
              setBlock(x, y, Level.CANNON_TOP);
            }
            else if (y == cannonHeight + 1) {
              setBlock(x, y, Level.CANNON_MID);
            }
            else {
              setBlock(x, y, Level.CANNON_BASE);
            }
          }
        }
      }
    }
    return length;
  }

  //A built in function for building a flat hill
  public int buildHillStraight(int xo, int length, int difficulty) {
    if (length == 5) {
      return this.buildStraight(xo, length, false, difficulty);
    }
    int floor = height - 1 - random.nextInt(4);
    for (int x = xo; x < xo + length; x++) {
      for (int y = 0; y < height; y++) {
        if (y >= floor) {
          setBlock(x, y, GROUND);
        }
      }
    }

    addEnemyLine(xo + 1, xo + length - 1, floor - 1, difficulty);

    int h = floor;

    boolean keepGoing = true;

    boolean[] occupied = new boolean[length];
    while (keepGoing) {
      h = h - 2 - random.nextInt(3);

      if (h <= 0) {
        keepGoing = false;
      }
      else {
        int l = random.nextInt(5) + 3;
        int xxo = random.nextInt(length - l - 2) + xo + 1;

        if (occupied[xxo - xo] || occupied[xxo - xo + l] || occupied[xxo - xo - 1] || occupied[xxo - xo + l + 1]) {
          keepGoing = false;
        }
        else {
          occupied[xxo - xo] = true;
          occupied[xxo - xo + l] = true;
          addEnemyLine(xxo, xxo + l, h - 1, difficulty);
          if (random.nextInt(4) == 0) {
            decorate(xxo - 1, xxo + l + 1, h, difficulty);
            keepGoing = false;
          }
          for (int x = xxo; x < xxo + l; x++) {
            for (int y = h; y < floor; y++) {
              int xx = 5;
              if (x == xxo) xx = 4;
              if (x == xxo + l - 1) xx = 6;
              int yy = 9;
              if (y == h) yy = 8;

              if (getBlock(x, y) == 0) {
                setBlock(x, y, (byte) (xx + yy * 16));
              }
              else {
                if (getBlock(x, y) == HILL_TOP_LEFT) setBlock(x, y, HILL_TOP_LEFT_IN);
                if (getBlock(x, y) == HILL_TOP_RIGHT) setBlock(x, y, HILL_TOP_RIGHT_IN);
              }
            }
          }
        }
      }
    }
    return length;
  }

  //A built in function for adding a line of enemies at a given height (y) and difficulty
  public void addEnemyLine(int x0, int x1, int y, int difficulty) {
    for (int x = x0; x < x1; x++) {
      if (random.nextInt(35) < difficulty + 1) {
        int type = random.nextInt(4);

        if (difficulty < 1) {
          type = Enemy.ENEMY_GOOMBA;
        }
        else if (difficulty < 3) {
          type = random.nextInt(3);
        }

        setSpriteTemplate(x, y-1, new SpriteTemplate(type, random.nextInt(35) < difficulty));//Second boolean value determines if enemy is flying
        ENEMIES++;
      }
    }
  }

  //A built in function for building a tube (difficulty determines chance of flower spawn)
  public int buildTubes(int xo, int length, int difficulty) {
    int floor = height - 1 - random.nextInt(4);
    int xTube = xo + 1 + random.nextInt(4);
    int tubeHeight = floor - random.nextInt(2) - 2;
    for (int x = xo; x < xo + length; x++) {
      if (x > xTube + 1) {
        xTube += 3 + random.nextInt(4);
        tubeHeight = floor - random.nextInt(2) - 2;
      }
      if (xTube >= xo + length - 2) xTube += 10;

      if (x == xTube && random.nextInt(11) < difficulty + 1) {
        setSpriteTemplate(x, tubeHeight, new SpriteTemplate(Enemy.ENEMY_FLOWER, false));
        ENEMIES++;
      }

      for (int y = 0; y < height; y++) {
        if (y >= floor) {
          setBlock(x, y,GROUND);
        }
        else {
          if ((x == xTube || x == xTube + 1) && y >= tubeHeight) {
            int xPic = 10 + x - xTube;

            if (y == tubeHeight) {
              //tube top
              setBlock(x, y, (byte) (xPic + 0 * 16));
            }
            else {
              //tube side
              setBlock(x, y, (byte) (xPic + 1 * 16));
            }
          }
        }
      }
    }
    return length;
  }

  //A built in function for building a straight path
  public int buildStraight(int xo, int length, boolean safe, int difficulty) {
    int floor = height - 1 - random.nextInt(4);

    //runs from the specified x position to the length of the segment
    for (int x = xo; x < xo + length; x++) {
      for (int y = 0; y < height; y++) {
        if (y >= floor) {
          setBlock(x, y, GROUND);
        }
      }
    }

    if (!safe) {
      if (length > 5) {
        decorate(xo, xo + length, floor, difficulty);
      }
    }
    return length;
  }

  //A built in function to add "decoration"
  public void decorate(int xStart, int xLength, int floor, int difficulty) {
    //if its at the very top, just return
    if (floor < 1)
      return;

    //    boolean coins = random.nextInt(3) == 0;
    boolean rocks = true;

    //add an enemy line above the box
    addEnemyLine(xStart + 1, xLength - 1, floor - 1, difficulty);

    int s = random.nextInt(4);
    int e = random.nextInt(4);

    if (floor - 2 > 0){
      if ((xLength - 1 - e) - (xStart + 1 + s) > 1) {
        for(int x = xStart + 1 + s; x < xLength - 1 - e; x++) {
          setBlock(x, floor - 2, COIN);
          COINS++;
        }
      }
    }

    s = random.nextInt(4);
    e = random.nextInt(4);

    //this fills the set of blocks and the hidden objects inside them
    if (floor - 4 > 0) {
      if ((xLength - 1 - e) - (xStart + 1 + s) > 2) {
        for (int x = xStart + 1 + s; x < xLength - 1 - e; x++) {
          if (rocks) {
            if (x != xStart + 1 && x != xLength - 2 && random.nextInt(3) == 0) {
              if (random.nextInt(4) == 0) {
                setBlock(x, floor - 4, BLOCK_POWERUP);
                BLOCKS_POWER++;
              }
              else{
                //the fills a block with a hidden coin
                setBlock(x, floor - 4, BLOCK_COIN);
                BLOCKS_COINS++;
              }
            }
            else if (random.nextInt(4) == 0) {
              if (random.nextInt(4) == 0) {
                setBlock(x, floor - 4, (byte) (2 + 1 * 16));
                // setBlock(x, floor - 4, (byte) (2 + 1 * 16));
              }
              else {
                setBlock(x, floor - 4, (byte) (1 + 1 * 16));
                // setBlock(x, floor - 4, BLOCK_COIN);
              }
            }
            else {
              setBlock(x, floor - 4, BLOCK_COIN);
              BLOCKS_EMPTY++;
            }
          }
        }
      }
    }
  }

  //A built in function to fix edges or walls at the end of level creation
  public void fixWalls() {
    boolean[][] blockMap = new boolean[width + 1][height + 1];

    for (int x = 0; x < width + 1; x++) {
      for (int y = 0; y < height + 1; y++) {
        int blocks = 0;
        for (int xx = x - 1; xx < x + 1; xx++) {
          for (int yy = y - 1; yy < y + 1; yy++) {
            if (getBlockCapped(xx, yy) == GROUND){
              blocks++;
            }
          }
        }
        blockMap[x][y] = blocks == 4;
      }
    }
    blockify(this, blockMap, width+1, height+1);
  }

  //blockify is used for fixing up walls
  public void blockify(Level level, boolean[][] blocks, int width, int height){
    int to = 0;

    boolean[][] b = new boolean[2][2];

    for (int x = 0; x < width; x++) {
      for (int y = 0; y < height; y++) {
        for (int xx = x; xx <= x + 1; xx++) {
          for (int yy = y; yy <= y + 1; yy++) {
            int _xx = xx;
            int _yy = yy;
            if (_xx < 0) _xx = 0;
            if (_yy < 0) _yy = 0;
            if (_xx > width - 1) _xx = width - 1;
            if (_yy > height - 1) _yy = height - 1;
            b[xx - x][yy - y] = blocks[_xx][_yy];
          }
        }

        if (b[0][0] == b[1][0] && b[0][1] == b[1][1]) {
          if (b[0][0] == b[0][1]) {
            if (b[0][0]) {
              level.setBlock(x, y-1, GROUND);
            }
            else {
              // KEEP OLD BLOCK!
            }
          }
          else {
            if (b[0][0]) {
              //down grass top?
              level.setBlock(x, y-1, (byte) (1 + 10 * 16 + to));
            }
            else {
              //up grass top
              level.setBlock(x, y-1, HILL_TOP);
            }
          }
        }
        else if (b[0][0] == b[0][1] && b[1][0] == b[1][1]) {
          if (b[0][0]) {
            //right grass top
            level.setBlock(x, y-1, RIGHT_GRASS_EDGE);
          }
          else {
            //left grass top
            level.setBlock(x, y-1, LEFT_GRASS_EDGE);
          }
        }
        else if (b[0][0] == b[1][1] && b[0][1] == b[1][0]) {
          level.setBlock(x, y, GROUND);
        }
        else if (b[0][0] == b[1][0]) {
          if (b[0][0]) {
            if (b[0][1]) {
              level.setBlock(x, y-1, (byte) (3 + 10 * 16 + to));
            }
            else {
              level.setBlock(x, y-1, (byte) (3 + 11 * 16 + to));
            }
          }
          else {
            if (b[0][1]) {
              //right up grass top
              level.setBlock(x, y-1, RIGHT_UP_GRASS_EDGE);
            }
            else {
              //left up grass top
              level.setBlock(x, y-1, LEFT_UP_GRASS_EDGE);
            }
          }
        }
        else if (b[0][1] == b[1][1]) {
          if (b[0][1]) {
            if (b[0][0]) {
              //left pocket grass
              level.setBlock(x, y-1, LEFT_POCKET_GRASS);
            }
            else {
              //right pocket grass
              level.setBlock(x, y-1, RIGHT_POCKET_GRASS);
            }
          }
          else {
            if (b[0][0]) {
              level.setBlock(x, y-1, (byte) (2 + 10 * 16 + to));
            }
            else {
              level.setBlock(x, y-1, (byte) (0 + 10 * 16 + to));
            }
          }
        }
        else {
          level.setBlock(x, y-1, BLOCK_EMPTY);
        }
      }
    }
  }

  //Clones this level
  public MyLevel clone() {

    MyLevel clone=new MyLevel(width, height);

    clone.xExit = xExit;
    clone.yExit = yExit;
    byte[][] map = getMap();
    SpriteTemplate[][] st = getSpriteTemplate();

    for (int i = 0; i < map.length; i++)
    for (int j = 0; j < map[i].length; j++) {
      clone.setBlock(i, j, map[i][j]);
      clone.setSpriteTemplate(i, j, st[i][j]);
    }

    clone.BLOCKS_COINS = BLOCKS_COINS;
    clone.BLOCKS_EMPTY = BLOCKS_EMPTY;
    clone.BLOCKS_POWER = BLOCKS_POWER;
    clone.ENEMIES = ENEMIES;
    clone.COINS = COINS;

    return clone;
  }
}
