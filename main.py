from fastapi import FastAPI , Path , HTTPException , Query
import json;

def load_data():
  with open('patients.json','r') as f:
    data=json.load(f)
  return data;    

  
app= FastAPI()

@app.get("/")
def hellow():
  return {'message':'Patient management system API'}

@app.get("/about")
def about():
  return {'message':'A fully functional API to manage patient records'}  

@app.get('/view')
def view():
  data=load_data()
  return data; 

@app.get('/patient/{patient_id}')
def view_patient(patient_id:str=Path(..., description='ID of the patien in the DB', example='PXXX')):

  deta=load_data()

  if patient_id in deta:  
    return deta[patient_id];
  raise HTTPException(status_code=404, detail='patient not found')

@app.get('/sort')
def sort_patients(sort_by:str=Query(..., description='sort on the basis of height , weight, bmi' ), order: str=Query('asc', description='sort by asc or dsc'  )):
  valid_field=['weight', 'height','bmi']
  if sort_by not in valid_field:
    raise HTTPException(status_code=400, detail=f'invalid field select from {valid_field}')

  if order not in ['asc', 'desc']:
    raise HTTPException(status_code=400, detail='invalid order select between asc or desc')

  data=load_data()
  sort_order=True if order=='desc' else False
  sorted_deta=sorted(data.values(), key=lambda x:x.get(sort_by,0),reverse=sort_order)
  return sorted_deta;

  

