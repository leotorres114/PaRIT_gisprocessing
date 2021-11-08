import sys
import os.path
from arcpy import env
from datetime import date

def main(datapath, gdbpath, planspath, featureclass, plan_title, plan_year, theme, author, pdf_url, unique_id):
    #set the workspace environment
    env.workspace = datapath

    #create a copy of the feature class so we don't modify the original
    copypath = os.path.join(gdbpath, "{0}_copy".format(featureclass))
    arcpy.management.CopyFeatures(featureclass, copypath)

    #reset featureclass to the copy
    featureclass = copypath

    #add the fields (columns) to the feature class
    dtype = 'TEXT'  # most of our fields are going to be text
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
    fieldstokeep = ['OBJECTID', 'Shape', 'Shape_Length', 'Shape_Area', unique_id,
                    'plan_title', 'plan_year', 'theme', 'author', 'pdf_url', 'last_update']
    fieldstodelete = list(set(newfields)-set(fieldstokeep))

    #deletes fields
    arcpy.DeleteField_management(featureclass, fieldstodelete)

    #renames unique_id field to match the plans geodatabase
    arcpy.AlterField_management(featureclass, unique_id,'name', clear_field_alias="TRUE")

    #finally, we append the resulting feature class to the all_plans feature class in the plans.gdb
    arcpy.Append_management(featureclass, planspath, schema_type='NO_TEST')

    return print("The script has run successfully. The new plan has been appended to the plans layer.")

if __main__ == '__main__':
    paras = sys.argv[-10:]

    datapath = str(paras[0]) #path of new data to add to geodatabase
    gdbpath = str(paras[1]) #path of geodatabase
    planspath = str(paras[2]) #path to all_plans feature class (this is the hosted layer for the app!)
    featureclass = str(paras[3]) #name of feature class that we want to add to the tool
    plan_title = str(paras[4])
    plan_year = str(paras[5])
    theme = str(paras[6]) #housing, transportation, social/economic, comp plan, small-area
    author = str(paras[7])
    pdf_url = str(paras[8])
    unique_id = str(paras[9]) #field that is unique to the data

    main(datapath, gdbpath, planspath, featureclass, plan_title, plan_year, theme, author, pdf_url, unique_id)