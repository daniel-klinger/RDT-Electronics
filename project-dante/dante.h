#include <iostream>
using namespace std;

#ifndef DANTE_H
#define DANTE_H

const int MAX_LENGTH = 6;

class Altitude
{
  public:
    void readAltitude(const int altitudeValue);

  private:
    int altitudeReading;
};

#endif
