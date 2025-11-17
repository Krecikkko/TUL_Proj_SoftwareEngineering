# TUL_Proj_SoftwareEngineering
## Git workflow
There are two main branches:
- `main` - Production-ready releases only
- `develop` - Latest working version (integration branch)
- `feature/*` - Individual feature branches
> Always create your branches from `develop` branch.
### How to start working?
1. Create feature branch
```
git branch feature/your-feature-name
git checkout feature/your-feature-name
```
2. Commit regularly with clear messages
3. Push and create **Pull request** to develop
4. Get 1+ team member approval before merging
5. Delete feature branch after merge
### Important notes
- Try to provide the appropriate unit tests for you module, testing the most important
functionalities of your module (backend teams using `pytest`). It will be beneficial
to automate the process of reviewing Pull requests, the process will be less error prone.
Instead of manualy checking, reviewer will be able to run unit tests and check if everything is correct.
- In Pull request put only checked and correct code, according to your best knowledge.
## Project structure
```
.
├── backend/
│   ├── common/                                         # Place to store code shared between all backend teams (optional)
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── utils/
│   │   └── config.py
│   ├── alerts-authentication-and-communication/        # Backend team 1
│   │   ├── app/
│   │   │   ├── api/                                    # fastapi routers
│   │   │   ├── services/
│   │   │   ├── repositories/
│   │   │   ├── schemas/
│   │   │   ├── models/
│   │   │   └── main.py
│   │   └── tests/
│   ├── data-access-and-control/                        # Backend team 2
│   │   └── ...
│   └── forecast-and-optimization/                      # Backend team 3
│       └── ...
│
├── frontend/
│   ├── common/                                         # Place to store code shared between all frontend teams (optional)
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── styles/
│   │   └── utils/
│   ├── data-visualization/                             # Frontend team 1
│   │   ├── src/
│   │   │   ├── pages/
│   │   │   ├── components/
│   │   │   ├── hooks/
│   │   │   └── index.tsx
│   │   └── tests/
│   └── ui-ux/                                          # Frontend team 2
│       └── src/...
│
├── db/
│
├── docs/
│   ├── backend/
│   │   ├── alerts-authentication-and-communication/
│   │   ├── data-access-and-control/
│   │   └── forecast-and-optimization/
|   └── frontend/
│       ├── data-visualization/
│       └── ui-ux/
│
└── README.md
```
Try to provide readable and consistent docs regarding your module, to make work easier for the teams, that
base on your module. I suppose that they will be grateful for that ;)
## Suggestions for the backend teams
To make your life easier try to use python virtual environment. To use it go to backend folder and type:
```Windows
python -m venv venv
```
```Linux
python3 -m venv venv
```
Then every dependency you will download using `pip` will be saved in the `venv` of our project. Remember that that
folder should not be put on github (by default it is included in `.gitignore`). Note that before working on a project
and downloading the dependencies, you need to make sure that your `venv` is activated. To achive that you need to:
```Windows
venv\Scripts\activate
```
```Linux
source venv/bin/activate
```
> If you use dependencies in your module please save them in a file `requirements.txt` in your module directory. It will allow
> people who would like to run your program, donwload using only one command all needed dependencies.
You just simpy need to use following command, being in the folder of you module:
```
pip freeze > requirements.txt
```
In order to download dependencies you just type, being in the folder of the given module:
```
pip install -r requirements.txt
```
The general `requirements.txt` is also provided, with dependencies that must be used by all teams.