# codiyapa
This is another online code judge that I developed overnight for conducting an event.
You are supposed to provide an input file with all test cases for download.
The participants should run their code with this file as input and upload their output file.
eg. for Python,
```python myprog.py <infile >outfile```

This is similar to Google Code Jam pattern, except that I haven't added the time limit once the input file is downloaded.

To use this as your judge, install Python 2.7 on your server, install Flask module, and run
```python base.py``` from the directory.

Put all the input cases for each problem in the ```infile``` folder, the corresponding correct output
in ```outfile``` folder and the problems in the ```templates``` folder.

I tested this judge for a competition with 30 people, using the in-built Flask server and it seemed to 
work well. However, I don't think this is production ready and you should use this only if you can read code.

To Do
-----
* Add time limits to the judge. The output file uploaded should be checked and seen if "Pretests Pass".
If the pretests pass, the code uploaded can be checked after the contest is over, to check for "Time Limit Exceeded" 
and for other errors.
* The interface is extremely simple (and bland!).
* Contest can be started with a timer, instead of doing so manually.
* Put all usernames and passwords in the database instead of a dict.
