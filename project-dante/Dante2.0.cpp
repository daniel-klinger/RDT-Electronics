/*
-------- Project Dante --------
Missouri S&T Rocket Design Team
Contributors:
  Ryker Travis
  Stephan Myes
  Caleb Hock
*/

#include <iostream>
#include <cstring>
#include <string>
#include <fstream>
#include <ctime>
#include <Windows.h>
#include "AudioFile.h"
using namespace std;

const char TIME        = 't';
const char ALTITUDE    = 'a';
const char TEMPERATURE = 'f';
const char VOLTAGE     = 'v';

const int TIME_DELAY = 5;
const string LAUNCH_CODE = "RocketDesign2019";

// Files
const string NUMBERFILE = ".\\resources\\sound\\numbers\\";
const string WORDFILE = ".\\resources\\sound\\words\\";

AudioFile <double> audioFile;

// Desc: Speaks the value of the number in the character array for the designated data type
void speak(char numToSpeak[], char dataType);
// Desc: Plays a countdown
void takeoff();
// Desc: Fills the character array passed with null characters starting at starter
void clearArray(char array[], const int starter = 0, const int size = 10);
// Desc: Uses windows functions to play sound files
void playSound(char numToSpeak[]);

int main()
{
  char timeVal[10];
  char timeStore[10];

  char altVal[10];
  char tempVal[10];
  char voltVal[10];

  int sleepVal = 0;

  bool validUser = false;

  string LaunchCode;

  //playSound(".\\resourcgit es\\sound\\words\\spaceOdyssey.wav");

  //playSound(".\\resources\\sound\\words\\BrettSafety.wav");

  std::time_t startTime = std::time(0);

  cout << "Enter Launch Code: ";
  cin  >> LaunchCode;

  while (LaunchCode != LAUNCH_CODE)
  {
      cout << "Invalid Code..." << endl
           << "Enter Launch Code: ";
      cin  >> LaunchCode;
  }
  takeoff();

  cout<<"Time\tAlt\tTemp\tVolt"<<endl;
  //while ((std::time(0) - startTime) < 999)

  // Infinite Loop
  while(1)
  {
    ifstream fin;
  	fin.open(".\\data\\AltitudeData.dat");

    // sleepVal=((std::time(0)-startTime)%TIME_DELAY);
    // Sleep((TIME_DELAY-sleepVal)*1000);
    Sleep(TIME_DELAY*1000);

    // Retrieves data from the AltitudeData.dat file
    while(fin.getline(timeStore, 50, '\t'))
  	{
  		strcpy(timeVal,timeStore);
      fin.getline(altVal, 50, '\t');
      fin.getline(tempVal, 50, '\t');
      fin.getline(voltVal, 50, '\n');
    }
    // If there is nothing in the second's place, there is no data
    if(!isdigit(timeVal[0]))
  	{
  		playSound(".\\resources\\sound\\words\\noData.wav");
  		cout<<"NO DATA AVALIABLE"<<endl;
  	}
    // Outputs the data in correct formatting
    else
  	{
    	cout<<timeVal<<'\t'<<altVal<<'\t'<<tempVal<<'\t'<<voltVal<<endl;
      speak(static_cast<int>(timeVal), TIME);
      speak(static_cast<int>(altVal), ALTITUDE);
    	speak(static_cast<int>(tempVal), TEMPERATURE);
      speak(static_cast<int>(voltVal), VOLTAGE);
  	}
  	fin.close();
  }
	return 0;
}

void takeoff()
{
  {
    // T minus 5...4...3...2...1...
  	playSound(".\\resources\\sound\\words\\tMinus.wav");
    playSound(".\\resources\\sound\\numbers\\5.wav");
    playSound(".\\resources\\sound\\numbers\\4.wav");
    playSound(".\\resources\\sound\\numbers\\3.wav");
    playSound(".\\resources\\sound\\numbers\\2.wav");
    playSound(".\\resources\\sound\\numbers\\1.wav");

    playSound(".\\resources\\sound\\words\\Usman_OMG.wav");
    playSound(".\\resources\\sound\\words\\r2d2_scream.mp3");
  }
  return;
}

void speak(char numToSpeak[], char dataType)
{
  const int MAX_LENGTH = 6;
  const int FILE_SIZE = 100;
  int dataNum;
  char toSpeak [FILE_SIZE];

  // Converts number array into an integer
  dataNum = atoi(numToSpeak);

  // Speaks time, altitude, and temperature
  if(dataType != VOLTAGE) {

    // Get numeric places of number
    int digitHundredThousands = (dataNum / 100000) % 10;
    int digitTenThousands     = (dataNum / 10000) % 10;
    int digitThousands        = (dataNum / 1000) % 10;
    int digitHundreds         = (dataNum / 100) % 10;
    int digitTens             = (dataNum / 1) % 100;

    { // Formats numToSpeak
      char storeNum[10];
      clearArray(storeNum);
      strcpy(storeNum, numToSpeak);
      if(strlen(numToSpeak) < MAX_LENGTH)
      {
      	clearArray(numToSpeak);
      	for (int i = 0; i < (MAX_LENGTH-strlen(storeNum)); i++) {
      		numToSpeak[i] = '0';
      	}
      	strcat(numToSpeak, storeNum);
      }
    }

    // Formats toSpeak array
    clearArray(toSpeak, 0, FILE_SIZE);
    strcat(toSpeak, ".\\resources\\sound\\numbers\\");
    int fileCounter = 0; // Counter for the # of characters in the file directory
    for(fileCounter = 0; toSpeak[fileCounter] != '\0'; fileCounter++);

//Speaking/////////////////////////////////////////////////////////////////////
    // Speaks hundred thousands place
    if(digitHundredThousands) {
      // Formats file to play
    	toSpeak[fileCounter] = numToSpeak[0];
      strcat(toSpeak, ".wav");

    	playSound(toSpeak);
      playSound(".\\resources\\sound\\numbers\\hundred.wav");

    	clearArray(toSpeak, fileCounter, FILE_SIZE);
    }

    // Speaks ten thousands / thousands place
    if (digitTenThousands && digitThousands) {
      // Formats file to play
    	toSpeak[fileCounter] = numToSpeak[1];
      toSpeak[fileCounter + 1] = numToSpeak[2];
    	strcat(toSpeak, ".wav");

    	playSound(toSpeak);

    	clearArray(toSpeak, fileCounter, FILE_SIZE);
    }

    // Speaks ten thousands place (no thousands)
    else if (digitTenThousands) {
      // Formats file to play
    	toSpeak[fileCounter] = numToSpeak[1];
      strcat(toSpeak, ".wav");

    	playSound(toSpeak);

    	clearArray(toSpeak, fileCounter, FILE_SIZE);
    }

    // Speaks thousands place (no ten thousands)
    else if (digitThousands) {
      // Formats file to play
    	toSpeak[fileCounter] = numToSpeak[2];
      strcat(toSpeak, ".wav");

    	playSound(toSpeak);

    	clearArray(toSpeak, fileCounter, FILE_SIZE);
    }

    // Speaks "thousands"
    if (digitHundredThousands || digitTenThousands || digitThousands) {
    	playSound(".\\resources\\sound\\numbers\\thousand.wav");
    }
    // Speaks hundreds place
    if (digitHundreds) {
      // Formats file to play
    	toSpeak[fileCounter] = numToSpeak[3];
      strcat(toSpeak, ".wav");

    	playSound(toSpeak);
      playSound(".\\resources\\sound\\numbers\\hundred.wav");

      clearArray(toSpeak, fileCounter, FILE_SIZE);
    }

    // Speaks tens place
    if (digitTens) {
    	// Two digits
    	if (digitTens > 9) {
        // Formats file to play
      	toSpeak[fileCounter] = numToSpeak[4];
        toSpeak[fileCounter + 1] = numToSpeak[5];
        strcat(toSpeak, ".wav");
      }
      // One digit
  		else {
        // Formats file to play
      	toSpeak[fileCounter] = numToSpeak[5];
        strcat(toSpeak, ".wav");
      }
      if (dataNum) {
      playSound(toSpeak);
      clearArray(toSpeak, fileCounter, FILE_SIZE);
      }
      else {
      	playSound(".\\resources\\sound\\numbers\\0.wav");
      }
    }

    // Speaks unit
    switch(dataType) {
      case TIME:
        playSound(".\\resources\\sound\\numbers\\seconds.wav");
        break;
      case ALTITUDE:
        playSound(".\\resources\\sound\\numbers\\feet.wav");
        break;
      case TEMPERATURE:
        playSound(".\\resources\\sound\\words\\DegF.wav");
        break;
    }
//End Speaking/////////////////////////////////////////////////////////////////
  }
  // Speaks voltage level (high, nominal, low)
  else if (dataType == VOLTAGE) {
		{
			if(dataNum <= 12 && dataNum >= 8)
      {
        playSound(".\\resources\\sound\\words\\voltNominal.wav");
      }
			else if(dataNum < 8)
      {
        //playSound(".\\resources\\sound\\words\\warning.wav");
			  playSound(".\\resources\\sound\\words\\lowVolt.wav");
			}
			else if(dataNum > 12)
      {
				//playSound(".\\resources\\sound\\words\\warning.wav");
			  playSound(".\\resources\\sound\\words\\highVolt.wav");
			}
		}
	}
	return;
}

void clearArray(char array[], const int starter, const int size) {
  for (int i = starter; i < size; i++) {
    array[i] = '\0';
  }
  return;
}

void playSound(char numToSpeak[])
{
	audioFile.load(numToSpeak);
	double soundLength = audioFile.getLengthInSeconds();

  system(numToSpeak);
	Sleep(soundLength*1000);
}
