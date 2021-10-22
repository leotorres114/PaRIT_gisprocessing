# set environment
from arcpy import env
import os.path
from datetime import date

######## IMPORTANT: you must set these variables for the script to work ############
env.workspace="C:/Users/ltorre37/OneDrive - University of Illinois - Urbana/UP510" #change path to where all the data lives
path = "C:/Users/ltorre37/OneDrive - University of Illinois - Urbana/UP510/Urbana_PaRIT/Urbana_PaRIT.gdb" #path to store a copy of data

#path to all_plans feature class (this is the hosted layer for the app!)
plans_path = "C:/Users/ltorre37/OneDrive - University of Illinois - Urbana/UP510/UP510/plans.gdb/all_plans_layer" 

featureclass = 'TIP_220921_points_Buffer' #name of feature class that we want to add to the tool
plan_title = 'Transportation Improvement Program (TIP) FY 2020-2025' #change to correct plan title
plan_year = '2020' #change to correct plan year
theme = 'transportation' #change to correct plan theme (housing, transportation, social/economic, comp plan, small-area)
author = 'Champaign-Urbana Urbanized Area Transportation Study (CUUATS)' #change to correct plan author
pdf_url = 'https://ccrpc.org/documents/tip-2020-2025/introduction-and-background-tip-fy20-25/' #change to correct URL
unique_id = 'project_title' #change to a field in your feature class that is unique to each geometry in the plan feature class

####################################################################################

#create a copy of the feature class so we don't modify the original
copypath = os.path.join(path, "{0}_copy".format(featureclass))
arcpy.management.CopyFeatures(featureclass,copypath)

#reset featureclass to the copy
featureclass = copypath

#add the fields (columns) to the feature class
dtype = 'TEXT' #most of our fields are going to be text
arcpy.management.AddFields(featureclass, 
                          [['plan_title', dtype],
                          ['plan_year', dtype],
                          ['theme', dtype],
                          ['author', dtype],
                          ['pdf_url', dtype]])

# get objects to iterate through
cur = arcpy.UpdateCursor(featureclass)
fields = [i.name for i in arcpy.ListFields(featureclass)]

#filter list of fields to update only ones we added
fields = fields[-5:]

#creates list of values from custom variables defined above
values = [plan_title, plan_year, theme, author, pdf_url]

#inputs values from custom variables into corresponding fields
for row in cur:
    for i in range(len(fields)):
        row.setValue(fields[i], values[i])
        cur.updateRow(row)

# Next, we will add a last_update field to show when that feature class was last processed
arcpy.management.AddField(featureclass, 'last_update', 'DATE')

# Automatically fills the last_update field with today's date
with arcpy.da.UpdateCursor(featureclass, 'last_update') as rows:
    for row in rows:
        rows.updateRow([date.today().strftime('%m/%d/%Y')]) 
        
#Next, we will delete all unnecessary fields
newfields = [f.name for f in arcpy.ListFields(featureclass)]

#IMPORTANT: Double check that these fields are correct. This is case sensitive.
fieldstokeep = ['OBJECTID','Shape','Shape_Length', 'Shape_Area',unique_id,'plan_title','plan_year','theme','author','pdf_url', 'last_update']
fieldstodelete = list(set(newfields)-set(fieldstokeep))

#deletes fields
arcpy.DeleteField_management(featureclass, fieldstodelete)

#renames unique_id field to match the plans geodatabase
arcpy.AlterField_management(featureclass, unique_id, 'name', clear_field_alias="TRUE")

#finally, we append the resulting feature class to the all_plans feature class in the plans.gdb
arcpy.Append_management(featureclass, plans_path, schema_type='NO_TEST')