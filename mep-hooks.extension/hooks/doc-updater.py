# -*- coding: utf-8 -*-
__title__ = "Z elevation updater" 
__author__ = "Tuah Hamid  - AECOM KL" 
__helpurl__ = "https://teams.microsoft.com/l/chat/0/0?users=tuah.hamid@aecom.com"

from Autodesk.Revit.DB import Document, BuiltInCategory, ElementId, ConnectorProfileType, BuiltInParameter, InsulationLiningBase
# ╔═╗╔═╗╔╗╔╔═╗╔╦╗╔═╗╔╗╔╔╦╗╔═╗  
# ║  ║ ║║║║╚═╗ ║ ╠═╣║║║ ║ ╚═╗  
# ╚═╝╚═╝╝╚╝╚═╝ ╩ ╩ ╩╝╚╝ ╩ ╚═╝  

tagging_parameter = "ACM_EC_Absolute Elevation"

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

duct_cat_id = ElementId(BuiltInCategory.OST_DuctCurves)
ct_cat_id = ElementId(BuiltInCategory.OST_CableTray)
pipe_cat_id = ElementId(BuiltInCategory.OST_PipeCurves)

for ele in modified_el:
    if ele.Category.Id == duct_cat_id:
        direction = ele.Location.Curve.Direction.Z # type: float
        duct_shape = ele.DuctType.Shape
        if direction == 0 and duct_shape != ConnectorProfileType.Round:
            try:
                duct_height = ele.Height / 2
                duct_elevation = ele.Location.Curve.Origin.Z
                new_val = duct_elevation - duct_height
                elev_param = ele.LookupParameter(tagging_parameter)
                elev_param.Set(new_val)
            except:
                pass
    elif ele.Category.Id == ct_cat_id:
        if ele.CurveNormal.Z == 1:
            try:
                ct_height = ele.Height / 2
                ct_elevation = ele.Location.Curve.Origin.Z
                new_val = ct_elevation - ct_height
                elev_param = ele.LookupParameter(tagging_parameter)
                elev_param.Set(new_val)
            except:
                pass
    elif ele.Category.Id == pipe_cat_id:
        if ele.get_Parameter(BuiltInParameter.RBS_PIPE_SLOPE).AsDouble() == 0:
            try:
                pipe_elev = ele.Location.Curve.Origin.Z
                outer_radius = ele.get_Parameter(BuiltInParameter.RBS_PIPE_OUTER_DIAMETER).AsDouble() / 2
                insulation_id = InsulationLiningBase.GetInsulationIds(doc, ele.Id)

                # calculate new bottom of pipe elevation
                if insulation_id:
                    insulation_element = doc.GetElement(insulation_id[0])
                    insulation_thickness = insulation_element.Thickness
                    new_val = pipe_elev - outer_radius - insulation_thickness
                    elev_param = ele.LookupParameter(tagging_parameter)
                    elev_param.Set(new_val)
                else:
                    new_val = pipe_elev - outer_radius
                    elev_param = ele.LookupParameter(tagging_parameter)
                    elev_param.Set(new_val) 
            except:
                pass