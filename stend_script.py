"""
Stend script for demonstrate Visualizer_task.py work in 
different mode with different arguments    	
"""


import subprocess


process = "python Visualizer_task.py "
mode = ["create ", "append "]
file1 = "test1.json "
file2 = "--new_file test2.json "
output = "--output graph_"
intervals = ["--interval 0 36000 ","--interval 1 3600 ",
             "--interval 2 36 ", "--interval 3 1 ", "--interval 4 1 "]
period = " --period 2017-08-29 08:15:27.243860 2017-10-25 09:15:27.243860"


if __name__ == "__main__":
    print("\n **********")
    print("At first create plot in mode:create according to the data from the file",
	      "name * at all possible intervals not limited by a period of time")
    print(" interval for ticks on axis of 2 arguments:",
	      "first argument:", 
		  "0-sec, 1-min, 2-hour, 3-day, 4-week, second argument - length of interval.")

	        
    print("Plots and data saves in directory",
	      "with the name specified in output argument.")
    print("Respectively, the script calls on the command line:")
    for interval in intervals:
        print(process, mode[0], file1, interval, output, "create",
		       interval[11])
			  
    for interval in intervals:
        subprocess.call("".join([process, mode[0], file1, interval, output,
		                         "create", interval[11]]), shell=True)
	
    print("\n\n**********")
    print("Now call script with period argument:")
    print(process, mode[0], file1, intervals[3], output, "create",
	      intervals[3][11], period)
    subprocess.call("".join([process, mode[0], file1, intervals[3][11], output,
	                         "create", intervals[3][11], period]), shell=True)
					
    print("\n\n**********")
    print("And, finally, call script in append mode with no period argument:")
    print(process, mode[1], file1, file2, intervals[3][11], output, "append",
	      intervals[3][11])
    subprocess.call("".join([process, mode[1], file1, file2, intervals[3],
	                        output, "append", intervals[3][11]]), shell=True)
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	