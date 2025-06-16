# -*- coding: utf-8 -*-
__title__ = "Z elevation updater" 
__author__ = "Tuah Hamid  - AECOM KL" 
__helpurl__ = "https://teams.microsoft.com/l/chat/0/0?users=tuah.hamid@aecom.com"

from Autodesk.Revit.DB import Document, BuiltInCategory, BuiltInParameter, ElementId, UnitUtils, UnitTypeId

# ╔═╗╔═╗╔╗╔╔═╗╔╦╗╔═╗╔╗╔╔╦╗╔═╗  
# ║  ║ ║║║║╚═╗ ║ ╠═╣║║║ ║ ╚═╗  
# ╚═╝╚═╝╝╚╝╚═╝ ╩ ╩ ╩╝╚╝ ╩ ╚═╝  

tagging_parameter = "ACM_EC_Absolute Elevation"

# ╔═╗╦ ╦╔╗╔╔═╗╔╦╗╦╔═╗╔╗╔╔═╗  
# ╠╣ ║ ║║║║║   ║ ║║ ║║║║╚═╗  
# ╚  ╚═╝╝╚╝╚═╝ ╩ ╩╚═╝╝╚╝╚═╝  
                                                                                                                                                                   
def convert_internal_to_millimeter(internal_unit_value): # type: (float) -> float
    '''Convert internal ft to mm'''
    converted_unit = UnitUtils.ConvertFromInternalUnits(internal_unit_value, UnitTypeId.Millimeters)
    return converted_unit

def convert_millimeter_to_internal(project_unit_value): # type: (float) -> float
    '''Convert mm to internal ft'''
    converted_unit = UnitUtils.ConvertToInternalUnits(project_unit_value, UnitTypeId.Millimeters)
    return converted_unit

# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝ VARIABLES
# ==================================================

sender = __eventsender__
args = __eventargs__

doc = args.GetDocument() # type:Document

modified_el_ids = args.GetModifiedElementIds()
deleted_el_ids = args.GetDeletedElementIds()
new_el_ids = args.GetAddedElementIds()
modified_el = [doc.GetElement(e_id) for e_id in modified_el_ids]

# only allow cable tray and duct elements to be updated 
allowed_cats = [ElementId(BuiltInCategory.OST_CableTray), ElementId(BuiltInCategory.OST_DuctCurves)]
for el in modified_el:
    if el.Category.Id in allowed_cats:
        # get cable tray/duct height from element location
        ct_height = el.Height
        scaled_height = ct_height / 2
        ct_elev = el.Location.Curve.Origin.Z - scaled_height
        elev_param = el.LookupParameter(tagging_parameter)
        elev_param.Set(ct_elev)