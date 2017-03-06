# cmput404-project
------------------
This is the course work for CMPUT 404 (Winter 2017) @ University of Alberta, Canada.



# Set up Enviroment
-------------------
This section described how to set up your environment in you local computer. The software can only run if your environment set up properly, so be careful of it.


##  Dependency & Tools Installation (First time on your computer)
You can skip this part is you have ```virtualenv```, ```pip```,```python2.7``` installed. If you didn't done that, use the follow cammands to get them install,


### Python
We recommend to install Python 2 >=2.7.9 or Python 3 >=3.4 downloaded from [python.org](https://www.python.org/). 

Mac OS X users can also install Python via [Homebrew](#homebrew-for-mac) using this code:
```bash
$ brew install python
```


### pip
According to this link: [https://pip.pypa.io/en/stable/installing/#do-i-need-to-install-pip](https://pip.pypa.io/en/stable/installing/#do-i-need-to-install-pip), 
> pip is already installed if you're using Python 2 >=2.7.9 or Python 3 >=3.4 downloaded from python.org, but you'll need to upgrade pip.

the pip is ready for you if you have installed [Python 2 >=2.7.9 or Python 3 >=3.4 downloaded from python.org](#python)

If you haven't get the pip installed (could be test by type `$ pip` in your commend line shell), you can find the instructions for installing and/or upgrading pip in [here](https://pip.pypa.io/en/stable/installing/).

Mac users who install Python via [Homebrew](#homebrew-for-mac) will have pip ready to use.

The detail documentation and/or guides of pip could be found in [here](https://pip.pypa.io/en/stable/)


#### virthualenv (the virtual environment for python)
```
$ pip install virtualenv
```




# Get Project Running
---------------------
If you don't want to see those details explanation, there is a [Quick Start](#quick-start) section for you.

## Details Explanation
Once your enviroment have set up, run following command to download the project,
```
$ git clone https://github.com/Web-Applications-and-Architect-Group/cmput404-project.git 
```

Then, goes into this directory and create a python virtual environment in it,
```
$ cd cmput404-project
$ virtualenv venv
```

When the virtual environment have been created, Mac & and Linux can activate it by command,
```
$ . venv/bin/activate
```
Windows can activate it by command,
```
$ venv\Scripts\activate
```

Make sure you are inside the virtual environment (see if there is a ```(venv)``` before your username in terminal). Then, install requirements on Mac by command,
```
$ sudo pip install -r requirements.txt
```
Install requirements on Windows by command,
```
$ pip install -r requirements.txt
```

Now, you should able to run the project on your local computer! Test it with Django's server this command,
```
$ python manage.py runserver
```


## Quick Start
No explanation here, copy the following command into terminal and it could run magically!

#### Mac
```
git clone https://github.com/Web-Applications-and-Architect-Group/cmput404-project.git 
cd cmput404-project
virtualenv venv
. venv/bin/activate
sudo pip install -r requirements.txt
```
#### Windows
```
git clone https://github.com/Web-Applications-and-Architect-Group/cmput404-project.git 
cd cmput404-project
virtualenv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Then test it by command,
```
$ python manage.py runserver
```



# Start Developing
------------------
When you start developing a task, a function, and/or a user case, please follows these steps bellow.

**Step 1: Create a new branch**

We prefer to have a new branch for each new implementation of a function. So, the first step of developing is to create a new branch. Since the dev branch will be the most updated version of our software, it a good idea to copy the dev branch as a starting point of the new branch. The ```name of branch``` will be the task code in Trello sprint board. 

To copy dev branch as a new branch,
```
$ git checkout dev
$ git checkout -b <name of branch>
```

**Step 2: Implementation**

Now, you can start implement the new function. 

**Step 3: Set Branch Upstream Server**

Once you have your first commit. You will be able to add this branch to git upstream server by the following code,
```
$ git push --set-upstream https://github.com/Web-Applications-and-Architect-Group/cmput404-project.git <name of branch>
```

After you have done those 3 steps, you should able to push your commit without --set-upstream flag, like the following command,
```
$ git push
```



# Code Reviewing
----------------



