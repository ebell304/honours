***USER GUIDE***

**Access Application Using URL**: https://honours-96qt.onrender.com/
Note: The website will take up to 2 minutes to start up from inactivity.

**OR**

**Access Application by running locally (Strongly recommended to minimize latency)**:
1. Clone this git repository onto your local machine.
2. Open up **app.py** using a Python IDE such as Visual Studio Code.
3. Comment out the line 'server = app.server'.
4. Uncomment out the lines 'if __name__ == "__main__": app.run(debug=True)
![image](https://github.com/user-attachments/assets/e4443502-fd9d-4084-bcb3-ea13cbba5115)
5. Within the Python terminal, type 'pip install -r requirements.txt' to install project dependencies
6. Still within the terminal, type 'py app.py' to start the applicaion.
7. The application will now be accessible with the url: http://127.0.0.1:8050/ (localhost)
8. Once finished, use CTRL+C within the Python terminal to close the application.










**games.json NOTICE**

Currently, the **'games.json'** file is far too large to upload directly to GitHub (590MB conflicting with 100MB maximum upload).

This file is required to run dataProcessing.py and can be downloaded from the following link: [Steam Games Dataset: games.json](https://www.kaggle.com/datasets/fronkongames/steam-games-dataset?select=games.json)

Place the file within the root directory before running dataProcessing.py.


**NOTE:** The dash web server functionality is NOT dependant on the games.json file, but rather the 4 .csv files output by dataProcessing.py. Therefore it is not required for the main application.
