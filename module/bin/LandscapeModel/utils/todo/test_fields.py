#    def create_runs():
#        """
#        
#        """
#        
#        errorlog = ""
#        #######################################################################
#        # 1. Check if the model is running with 1 to n fields
#        fieldcount = len(FieldList)
#        fieldnames = [field["name"] for field in FieldList]
#        reachnames = [reach["name"] for reach in ReachList]
#    
#
#        for i in range(fieldcount):
#            test_list_index = []
#            reaches_test_list_index = []
#            message=str(i+1) + "/" + str(fieldcount) + " " + FieldList[i]["name"] + " start"
#            errorlog += message; print(message)
#            
#            #add actual field
#            test_list_index.append(i)
#            
#            #add all fields which are needed to connect the current field to
#            # a reach segment
#            if FieldList[i]["reach"] == 'None':
#                nextfield = FieldList[fieldnames.index(FieldList[i]["adjacent_field"])]
#                reachConnection=False
#
#                while not reachConnection:
#
#                    if nextfield["reach"] == 'None':
#                        # add enct field to list
#                        test_list_index.append(fieldnames.index(nextfield["name"]))
#                        # get the adjancent field of next field
#                        nextfield = FieldList[fieldnames.index(nextfield["adjacent_field"])]
#                    else:
#                        # add enct field to list
#                        test_list_index.append(fieldnames.index(nextfield["name"]))
#                        reaches_test_list_index.append(reachnames.index(nextfield["reach"]))
#                        reachConnection = True
#            else:
#                reaches_test_list_index.append(reachnames.index(FieldList[i]["reach"]))
#
#            # create field list for test
#            test_fieldList = FieldList[test_list_index]  
#            
#            #create test reachlist
#            test_reachList = ReachList[reaches_test_list_index]  
#            test_reachList[0]["downstream"] = "Outlet"
#
#
#            print([f["name"] for f in test_fieldList])
#            print([r["name"] for r in test_reachList])
#
#            # run model for two timesteps
#            end = end = datetime(2011,1,3)
#                        
#            #create model setup
#            sc = SubCatchment(name,test_reachList,SubbasinList,test_fieldList,
#                                      None,
#                                     ClimateStationList,SoilLayerList,
#                                     CropCoefficientList,ManagementList,
#                                     timestep,timestep_convert,begin,database_path=fpath,
#                                     inputdata_path=fpath,clim_start=clim_start,clim_step=clim_step,
#                                     separate_solver=separate_solver,withDrift=False)   
#            # try to conduct model run; proceed i ncase of error without field                
#            try:
#                sc(begin,end,printCatchmentOutput=False,printFieldOutput=False)	
#                message=str(i+1) + "/" + str(fieldcount) + " " + FieldList[i]["name"] + " successful"  + "\n"
#                errorlog += message; print(message)
#            except Exception as e:
#                message=str(i+1) + "/" + str(fieldcount) + " " + FieldList[i]["name"] + " ERROR: " + str(e) + "\n"
#                errorlog += message; print(message)
#                next
#                
#        # return error log
#        return errorlog
#
#    errorlog = validate_flow_network()
#
#
#


