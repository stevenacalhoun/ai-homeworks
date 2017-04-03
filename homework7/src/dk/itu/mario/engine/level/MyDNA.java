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

    // Create half split children
    String childChrom1 = this.chromosome.substring(0,(this.length/2)-1)+mate.chromosome.substring((this.length/2)-1);
    String childChrom2 = mate.chromosome.substring(0,(this.length/2)-1)+this.chromosome.substring((this.length/2)-1);

    MyDNA child1 = new MyDNA();
    child1.setChromosome(childChrom1);
    offspring.add(child1);

    MyDNA child2 = new MyDNA();
    child2.setChromosome(childChrom2);
    offspring.add(child2);

    // Create alternating children
    String childChrom3 = new String("");
    String childChrom4 = new String("");

    for (int i=0;i<this.length;i++) {
      if (i % 2 == 0) {
        childChrom3 += this.chromosome.charAt(i);
        childChrom4 += mate.chromosome.charAt(i);
      }
      else {
        childChrom3 += mate.chromosome.charAt(i);
        childChrom4 += this.chromosome.charAt(i);
      }
    }

    MyDNA child3 = new MyDNA();
    child3.setChromosome(childChrom3);
    offspring.add(child3);

    MyDNA child4 = new MyDNA();
    child4.setChromosome(childChrom4);
    offspring.add(child4);

    // Create a bunch of random children
    for (int i=0;i<10;i++) {
      String randomChildString = new String("");

      // Randomly select a character from one of the parents
      for (int j=0;i<this.length;i++) {
        if (Math.random() < 0.5) {
          randomChildString += this.chromosome.charAt(i);
        }
        else {
          randomChildString += mate.chromosome.charAt(i);
        }
      }

      MyDNA randomChild = new MyDNA();
      randomChild.setChromosome(randomChildString);
      offspring.add(randomChild);
    }

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

  // Return all the chromosome options
  public ArrayList<String> getChromOptions() {
    ArrayList<String> chromOptions = new ArrayList<String>();

    chromOptions.add("a");
    chromOptions.add("b");
    chromOptions.add("c");
    chromOptions.add("d");
    chromOptions.add("e");
    chromOptions.add("f");
    chromOptions.add("g");
    chromOptions.add("h");
    chromOptions.add("i");
    chromOptions.add("j");
    chromOptions.add("k");
    chromOptions.add("l");
    chromOptions.add("m");
    chromOptions.add("n");

    return chromOptions;
  }

  // Pick a random chromosome character
  public String pickRandomChrom() {
    ArrayList<String> chromOptions = this.getChromOptions();
    return chromOptions.get((int)(Math.random() * chromOptions.size()));
  }

  // Chreate a random chromosome
  public void randomizeChrom() {
    int defaultChromLength = 20;
    String chrom = new String("");

    for (int i=0;i<defaultChromLength;i++) {
      chrom += this.pickRandomChrom();
    }

    this.setChromosome(chrom);
  }
}
