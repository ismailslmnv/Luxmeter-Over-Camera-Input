# Luxmeter-Over-Camera-Input
Detecting Light Density Over Raspberry Pi Camera Module

This program is designed to measure approximate value of inner light of a experimental room and give result as LUX value. 
The main work priciple is described below:
  
    > Firstly recorded some measurements by a LUXMETER on a different light values.
  
    > Next regression test applied on these Lux values and software results of the same light densities. 
  
    > The result of this analysis gave us X-constant and tolerence for the formula.
  
    > With help of this formula the software output is about 5-10% tolerenced on 0 - 900 LUX. 
  

    Regression Result of Inner Lights ON Status
    
    X Constant = 81.3161669250621
   
    Tolerence Constant = 0.194858452777609
 ![alt text](https://github.com/ismailslmnv/Luxmeter-Over-Camera-Input/blob/master/regression_g.png)
   

    
    Regression Result of Inner Lights OFF Status
    
    X Constant = 62.7637685159081
   
    Tolerence Constant = 0.503275917659405
 ![alt text](https://github.com/ismailslmnv/Luxmeter-Over-Camera-Input/blob/master/regression_g1.png)
 
 Before use need to calibrate for the new environment. 
 
 Dependencies of the project are below:
 
    > opencv-python
    > numpy
    > picamera
To start run this command:

    > python3 main.py
