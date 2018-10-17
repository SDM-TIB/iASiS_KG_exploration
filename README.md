#  iASIS Lung Cancer exploration service

## 1.  About

Service for the exploration of the entities related to Lung Cancer in iASIS KG.

## 2. Usage

Setup the variable with the iASiS endpoint

`export IASISKG_ENDPOINT=http://node2.research.tib.eu:7171/sparql`

Execute

`./run_iasis_lc_exploration_service.sh`

### Examples of calls to service:

Example 1 Getting publications: 

curl -H "Content-Type: application/json" -d  '{ "comorbidities" : ["C0242339", "C0020538", "C0149871"], "biomarkers":["C0034802","C1332080","C0812281"], "tumorType":["C0152013"], "drugGroups":["C0002771", "C0003232"], "drugs":["C0000979","C0028978"],"oncologicalTreatments":["C0021083", "C3665472", "C3899317", "C0596087", "C0034619", "C0543467"],"immunotherapyDrugs":["C3657270", "C3658706", "C1367202"],"tkiDrugs":["C1135135", "C2987648", "C4058811", "C1122962", "C3853921", "C3818721"], "chemotherapyDrugs":["C0008838", "C4082227", "C0771375", "C0015133", "C0079083", "C0045093", "C0144576", "C0210657", "C0078257"]}'  -X POST http://localhost:5000/lc_exploration?"type=publications&limit=4" --output  example_output6.txt

Example 2 Getting publications, side-effects, and drug-interactions:

curl -H "Content-Type: application/json" -d  '{ "comorbidities" : ["C0242339", "C0020538", "C0149871"], "biomarkers":["C0034802","C1332080","C0812281"], "tumorType":["C0152013"], "drugGroups":["C0002771", "C0003232"], "drugs":["C0000979","C0028978"],"oncologicalTreatments":["C0021083", "C3665472", "C3899317", "C0596087", "C0034619", "C0543467"],"immunotherapyDrugs":["C3657270", "C3658706", "C1367202"],"tkiDrugs":["C1135135", "C2987648", "C4058811", "C1122962", "C3853921", "C3818721"], "chemotherapyDrugs":["C0008838", "C4082227", "C0771375", "C0015133", "C0079083", "C0045093", "C0144576", "C0210657", "C0078257"]}'  -X POST http://localhost:5000/lc_exploration?"type=publications,sideEffects,drugInteractions&limit=4" --output  example_output7.txt

