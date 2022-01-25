# Automating GIS Data Processing for PaRIT
Python script that automates the processing of GIS data to add on to the City of Urbana's Plans, Projects, and Regulations Information Tool (PaRIT), created for Fall 2021 UP510 Plan Making course at UIUC.

Tool can be found here: [link](https://arcg.is/nO0jm)

# Run the Script

We can run this Python script via the command line using [these](https://pro.arcgis.com/en/pro-app/2.8/arcpy/get-started/using-conda-with-arcgis-pro.htm) instructions from ArcGIS Pro's Python documentation. 

```Shell
  c:\Progra~1\ArcGIS\Pro\bin\Python\scripts\propy.bat parit.py \
  --data /path/to/data/to/be/added \
  --gdb /path/to/plans/geodatabase \
  --allplans /path/to/allplans/featureclass \ #this is PaRIT's hosted layer
  --fc name_of_featureclass_process \
  --title plan_title
  --year plan_year
  --theme {housing, transportation, social/economic, comp plan, small-area}
  --author author_of_plans
  --pdf {PDF_URL}
  --id unique_column_name
```
