# Squyrrel

## Installation

```$ pip install squyrrel```

## Run from command line

Example:
```$ manage.py load_package squyrrel```

## Run Sonarqube analysis
1) start the sonarqube server (locally) by running the StartSonar.bat:
```
c:\users\lspiegel\sonarqube\sonarqube-8.3.1.34397\bin\windows-x86-64\StartSonar.bat
```
2) cd into the project root director and start the scanner:
```
c:\users\lspiegel\sonarqube\sonar-scanner-4.3.0.2102-windows\bin\sonar-scanner
```

## Deploy new Squyrrel version to Pipy
To release a new version on the [PyPi Python Package Index](https://pypi.org/), follow these steps: 

* Delete files in dist folder (in case there is a dist folder in the root dir of the project and it contains files) 
* Update version number (as you see fit) in setup.py and possibly commit this update as 'update version' or sth.
* Run 
```
$ setup.py sdist
``` 
on the cmd line in your project root. This will create (or fill) the dist folder (creating a tar.gz archive)
* Run
```
$ twine upload dist/*
```
on the cmd line in your project root. This will upload the archive created in the previous step to you pypi package repository
(and thus making the new release available through pip install <pypi_repo_name>
