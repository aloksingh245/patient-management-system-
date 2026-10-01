from fastapi import FastAPI, Path, HTTPException, Query
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal
import json


def load_data():
    with open('patients.json', 'r') as f:
        data = json.load(f)
    return data


def save_data(data):
    with open('patients.json', 'w') as f:
        json.dump(data, f)


app = FastAPI()


class Patient(BaseModel):
    id: Annotated[str,
                  Field(..., description='ID of the patient', examples=['P001'])
                  ]
    name: Annotated[str,
                    Field(..., description='Name of the patient', examples=['Alok'])
                    ]
    city: Annotated[str,
                    Field(..., description='Name of the city', examples=['Patna'])
                    ]
    age: Annotated[int,
                   Field(..., gt=0, description='Age of the patient')
                   ]
    gender: Annotated[Literal['male', 'female', 'others'],
                      Field(..., description='Gender of the patient')
                      ]
    height: Annotated[float,
                      Field(..., gt=0, description='Height of the patient in mtrs')
                      ]
    weight: Annotated[float,
                      Field(..., gt=0, description='Weight of the patient in kgs')
                      ]

    @computed_field
    @property
    def bmi(self) -> float:
        bmi = round(self.weight / (self.height ** 2), 2)
        return bmi

    @computed_field
    @property
    def verdict(self) -> str:
        if self.bmi < 18.5:
            return 'underweight'
        elif self.bmi < 25:
            return 'normal'
        elif self.bmi < 30:
            return 'overweight'   # ✅ Fixed: was incorrectly returning 'normal'
        else:
            return 'obese'


@app.get("/")
def hello():
    return {'message': 'Patient management system API'}


@app.get("/about")
def about():
    return {'message': 'A fully functional API to manage patient records'}


@app.get('/view')
def view():
    data = load_data()
    return data


@app.get('/patient/{patient_id}')
def view_patient(patient_id: str = Path(..., description='ID of the patient in the DB', examples=['PXXX'])):
    data = load_data()
    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code=404, detail='Patient not found')


@app.get('/sort')
def sort_patients(
    sort_by: str = Query(..., description='Sort on the basis of height, weight, bmi'),
    order: str = Query('asc', description='Sort by asc or desc')
):
    valid_fields = ['weight', 'height', 'bmi']
    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail=f'Invalid field. Select from {valid_fields}')

    if order not in ['asc', 'desc']:
        raise HTTPException(status_code=400, detail='Invalid order. Select between asc or desc')

    data = load_data()
    sort_order = True if order == 'desc' else False
    sorted_data = sorted(data.values(), key=lambda x: x.get(sort_by, 0), reverse=sort_order)
    return sorted_data
