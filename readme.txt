## ====================================
## Using the Code 
## ====================================

(1) Open Main4.py
(2) Input necessary parameters which are:
	(a) current time, in seconds (time now in code). 12 am refers to 0 seconds
	(b) prediction time, in seconds (analysistime in code)
	(c) day (day in code)
	(d) Weather. Weather information is required in intervals (0,6), (6,12), 	     (12,18) and (18,24) hours. If current time is 10 am and analysis time is 5 hours, then time interval is between 10 and 15. In this case, provide weather information for (6,12) and (12, 18). Input format is given in the code.
	(e) Intersection Distance (intersection_dist in code)
	(f) Interested Accident Type (acc_nature in code)
	(g) Severity of accident (severity in code)
	(h) Month (month in code)

(3) These parameters are available under the comment “Changeable parameters”
(4) After inputting the necessary parameters, run the program. The output, i.e., hexagon locations and their probabilities, for every cluster type are printed to the console.

Note: If Hex location probabilities is not printed, then data corresponding to incidents to learn the probabilities at the set parameters are not available in the dataset" 