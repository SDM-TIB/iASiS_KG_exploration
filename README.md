#  iASIS KG exploration service

## 1.  About

Service for the exploration of the iASIS KG

## 2. Usage

Execute

`./run_iasis_KG_exploration_service.sh`

### Examples of calls to service:

Example 1 Getting the publications: 

`curl -H "Content-Type: application/json" -d  '{ "comorbidities" : ["C0242339","c0149871"], "biomarkers":["EGFR","ALK","ROS1"], "tumorType":["Non-squamous"], "drugsGroups":["pain killer", "antibiotic"], "drugs":["C0000979","C0028978"],"oncologicalTreatments":["immunotherapy","tki", "chemotherapy"],"immunotherapyDrugs":["C3657270"],"tkiDrugs":["C1135135"], "chemotherapyDrugs":["C0008838"]}'  -X POST http://localhost:5002/iasiskgexploration?"type=publications&limit=6" --output  example_output1.txt`

Example 2 Getting side effects:

`curl -H "Content-Type: application/json" -d  '{ "comorbidities" : ["C0242339","c0149871"], "biomarkers":["EGFR","ALK","ROS1"], "tumorType":["Non-squamous"], "drugsGroups":["pain killer", "antibiotic"], "drugs":["C0000979","C0028978"],"oncologicalTreatments":["immunotherapy","tki", "chemotherapy"],"immunotherapyDrugs":["C3657270"],"tkiDrugs":["C1135135"], "chemotherapyDrugs":["C0008838"]}'  -X POST http://localhost:5002/iasiskgexploration?"type=sideEffects&limit=10" --output  example_output2.txt`

