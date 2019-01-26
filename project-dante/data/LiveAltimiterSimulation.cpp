#include <iostream>
#include <fstream>
#include <Windows.h>

using namespace std;

int OUTPUT_FREQUENCY = 5 * 20; // num seconds * 20

int main()
{
	char line[100];
	int totalTime = 0;
	int counter = OUTPUT_FREQUENCY-1;

	ifstream fin;
	fin.open("AltitudeDataOrig.dat");

  while (fin.getline(line, 100, '\n'))
	{
		ifstream fin;
		fin.open("AltitudeDataOrig.dat");

		ofstream fout;
    fout.open("AltitudeData.dat", ios::app);

		fout<<line<<endl;

		fout.close();
		fin.close();

		counter++;

		Sleep(50);

		while (counter == OUTPUT_FREQUENCY)
		{
			cout<<line<<endl;
			counter = 0;
		}

	}

	fin.close();



	return 0;
}
