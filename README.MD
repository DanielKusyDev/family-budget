# Budget app
The app is divided into three parts following Hexagonal architecture pattern. FastAPI with GraphQL server sits on the 
left side of the hex, when the MSSQL database serves as a main infrastructure service.

### Quality Checks
 - pytest
 - flake8 + isort + black


## Installation

### Note about tests
Since the form of development of this application is very similar to POC, no real and full tests were created. I used 
this (very short) time I had to create a POC-like application. With more time available the following testing approaches
would be used:
 - all helpers and "small" functions, not related to the actual domain would be tested using pytest + hypothesis
 - domain services such as list views would be tested using BDD methodology (Behave). In-Memory database would be use 
for that purpose.
 - infrastructure would be tested through pytest and fake database running in a docker container (MSSQL Express)
 - driver application would be tested using pytest and Starlatte's test client