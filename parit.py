import sys
import os.path
import argparse
from arcpy import env
from datetime import date

def main(params):
    """
    This script does the following:
    1. Sets ArcGIS geoprocessing env
    2. Creates a copy of the input featureclass to be added to the plans gdb
    3. Inputs CLI args into corresponding field values
    4. Autofills 'last_update' field value
    5. Removes unnecessary fields
    6. Renames fields unique to each feature in the feature class
    7. Appends the input featureclass to the plans geodatabase
    """
    datapath = params.data #path of new data to add to geodatabase
    gdbpath = params.gdb #path of geodatabase
    planspath = params.allplans #path to all_plans feature class (this is the hosted layer for the app!)
    featureclass = params.fc #name of feature class that we want to add to the tool
    plan_title = params.title
    plan_year = params.year
    theme = params.theme #housing, transportation, social/economic, comp plan, small-area
    author = params.author
    pdf_url = params.pdf
    unique_id = params.id #field that is unique to the data
    
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
    if len(fieldstodelete) == 0:
        pass
    else:
        arcpy.DeleteField_management(featureclass, fieldstodelete)

    #renames unique_id field to match the plans geodatabase
    arcpy.AlterField_management(featureclass, unique_id,'name', clear_field_alias="TRUE")

    #finally, we append the resulting feature class to the all_plans feature class in the plans.gdb
    arcpy.Append_management(featureclass, planspath, schema_type='NO_TEST')

    return print("The script has run successfully. The new plan has been appended to the plans layer.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Automate GIS data processing for PaRIT')

    parser.add_argument('--data', help='path of data to add to PaRIT')
    parser.add_argument('--gdb', help='path of plans geodatabase')
    parser.add_argument('--allplans', help="""path to all_plans feature class (PaRIT's hosted layer""")
    parser.add_argument('--fc', help='name of feature class to process')
    parser.add_argument('--title', help='title of the plan')
    parser.add_argument('--year', help='year when plan was created')
    parser.add_argument('--theme', help='housing, transportation, social/economic, comp plan, small-area')
    parser.add_argument('--author', help='organization that authored the plan')
    parser.add_argument('--pdf', help='URL of plan PDF')
    parser.add_argument('--id', help='unique column for each plan project')

    args = parser.parse_args()

    main(args)