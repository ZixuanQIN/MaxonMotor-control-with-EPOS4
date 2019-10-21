Tools: Maxon motor, EPOS4 compact 50/5, python 3.7.4

This code is for controlling maxon motor by python command line.

How To Use It:
1. git clone https://github.com/ZixuanQIN/MaxonMotor-control-with-EPOS4.git
2. open terminal, input: python or python3
3. >>> from prosthesis.py import *
4. >>> name = Motor()  # "name" is the motor you named it.
5. >>> initial(name)
6. >>> name.angle = ***   # set the parameters, for example, angle or velocity
7. >>> start(name)
...... control your motor as you like
