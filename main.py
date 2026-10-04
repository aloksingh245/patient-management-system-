from fastapi import FastAPI, Path, HTTPException, Query
from fastapi.responses import JSONResponse 
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal , Optional
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
            return 'overweight'   
        else:
            return 'obese'


class PatientUpdate(BaseModel):                           
    name: Annotated[Optional[str],
                    Field(default=None)
                    ]
    city: Annotated[Optional[str],
                        Field(default=None)
                        ]
    age: Annotated[Optional[int],
                        Field(default=None)
                        ]
    gender: Annotated[Optional[str],
                        Field(default=None)
                        ]
    height: Annotated[Optional[float],
                        Field(default=None)
                        ]
    weight: Annotated[Optional[float],
                        Field(default=None)
                        ]
    
    





        


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

@app.post('/create')
#data came from clinte in form of json and save it in patient then the deta goes to the deta type {Patient } for data validation as well as bmi and validation caluclation then it comes and store
    
def create_patient(patient: Patient):

    #load existing data
    data=load_data( )


    #check if the patient alredy exist
    if patient.id in data:
        raise HTTPException(status_code=400 , detail='patient already exist')


    #new patient add to the da(json)
    data[patient.id]= patient.model_dump(exclude=['id'])

    #save in db(json)
    save_data(data)  

    return JSONResponse(status_code=201 ,content={'message':'patient created sucessfully'})


@app.put('/edit/{patient_id}')
def update_patient(patient_id: str , patient_update:PatientUpdate):
    data=load_data()

    if patient_id not in data:
        raise HTTPException(status_code=404 , detail='patient id not found')

    existing_patient_info=data[patient_id]

    updated_patient_info=  patient_update.model_dump(exclude_unset=True) #exclude all the fild which patient wont give any value

    for key, value in updated_patient_info.items():
        existing_patient_info[key]=value  

    existing_patient_info['id'] = patient_id

    patient_pydantic_obj = Patient(**existing_patient_info)
    existing_patient_info = patient_pydantic_obj.model_dump(exclude={'id'})

    data[patient_id] = existing_patient_info
    save_data(data)

    return JSONResponse(status_code=200, content={'message': 'patient updated'})



@app.delete('/delete/{patient_id}')
def delete_patient(patient_id: str):
    data=load_data()

    if patient_id not in data:
        raise HTTPException(status_code=404, detail='patient not found') 

    del data[patient_id]


    save_data(data)

    return JSONResponse(status_code=200, content={'message':'patient data deleted'})

