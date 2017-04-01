package dk.itu.mario.engine.level;

import java.util.Random;
import java.util.*;

//Make any new member variables and functions you deem necessary.
//Make new constructors if necessary
//You must implement mutate() and crossover()


public class MyDNA extends DNA
{

  public int numGenes = 0; //number of genes

  // Return a new DNA that differs from this one in a small way.
  // Do not change this DNA by side effect; copy it, change the copy, and return the copy.
  public MyDNA mutate () {
    MyDNA copy = new MyDNA();
    //YOUR CODE GOES BELOW HERE

    int idxToChange = (int)(Math.random() * this.length);
    String newChrom = this.chromosome.substring(0,idxToChange)+this.pickRandomChrom()+this.chromosome.substring(idxToChange+1);
    copy.setChromosome(newChrom);

    //YOUR CODE GOES ABOVE HERE
    return copy;
  }

  // Do not change this DNA by side effect
  public ArrayList<MyDNA> crossover (MyDNA mate) {
    ArrayList<MyDNA> offspring = new ArrayList<MyDNA>();
    //YOUR CODE GOES BELOW HERE

    String newChrom1 = this.chromosome.substring(0,(this.length/2)-1)+mate.chromosome.substring((this.length/2)-1);
    String newChrom2 = mate.chromosome.substring(0,(this.length/2)-1)+this.chromosome.substring((this.length/2)-1);

    MyDNA newDNA1 = new MyDNA();
    newDNA1.setChromosome(newChrom1);
    offspring.add(newDNA1);

    MyDNA newDNA2 = new MyDNA();
    newDNA2.setChromosome(newChrom2);
    offspring.add(newDNA2);


    //YOUR CODE GOES ABOVE HERE
    return offspring;
  }

  // Optional, modify this function if you use a means of calculating fitness other than using the fitness member variable.
  // Return 0 if this object has the same fitness as other.
  // Return -1 if this object has lower fitness than other.
  // Return +1 if this objet has greater fitness than other.
  public int compareTo(MyDNA other) {
    int result = super.compareTo(other);
    //YOUR CODE GOES BELOW HEREa

    if (this.getFitness() == other.getFitness()) {
      result = 0;
    }
    else if (this.getFitness() < other.getFitness()) {
      result = -1;
    }
    else {
      result = 1;
    }

    //YOUR CODE GOES ABOVE HERE
    return result;
  }


  // For debugging purposes (optional)
  public String toString () {
    String s = super.toString();
    //YOUR CODE GOES BELOW HERE

    s = this.chromosome;

    //YOUR CODE GOES ABOVE HERE
    return s;
  }

  public void setNumGenes (int n) {
    this.numGenes = n;
  }


  public ArrayList<String> getChromOptions() {
    ArrayList<String> chromOptions = new ArrayList<String>();

    chromOptions.add("a");
    chromOptions.add("b");
    chromOptions.add("c");
    chromOptions.add("d");

    return chromOptions;
  }

  public String pickRandomChrom() {
    ArrayList<String> chromOptions = this.getChromOptions();
    return chromOptions.get((int)(Math.random() * chromOptions.size()));
  }

  public void randomizeChrom() {
    int defaultChromLength = 10;
    String chrom = new String("");

    for (int i=0;i<defaultChromLength;i++) {
      chrom += this.pickRandomChrom();
    }

    this.setChromosome(chrom);
  }
}
