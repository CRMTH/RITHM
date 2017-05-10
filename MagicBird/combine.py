import os, csv, re

class csvcombine:

    def __init__ (self, dirOut = "", directory = "", dirTemp = ""):
        self.dirOut = dirOut
        self.directory = directory
        self.dirTemp = dirTemp

    def combinecsv (self, frequency, dirOut = "", directory = "", dirTemp = ""):
        if dirOut is "":
            dirOut = self.dirOut
        if directory is "":
            directory = self.directory
        if dirTemp is "":
            dirTemp = self.dirTemp

        combine = csvcombine._get_files_to_combine(self, dirTemp, frequency)

        for key in combine.keys():
            files = combine[key]
            fileCount = 0
            for f in files:
                ####### IF THERE IS NO HEADER, REMOVE THE LINE fileCount += 1 ######
                ####### THAT WILL KEEP IT ON THE if PORTION THAT GETS EVERY LINE #####
                if fileCount == 0:
                    with open(dirOut + key + 'MasterCSV.csv', 'a', newline='') as csvfile:
                        #saveFile = csv.writer(csvfile, delimiter=',', dialect='excel')
                        saveFile = csv.writer(csvfile, delimiter=',')
                        with open(dirTemp + f, 'r') as read:
                            for line in read:

                                line = re.sub('\r', '', line)
                                line = re.sub('\n', '', line)
                                cells = line.split(',')
                                saveFile.writerow([cell for cell in cells])
                    fileCount += 1 ### THIS ONE ### 
                else:
                    with open(dirOut + key + 'MasterCSV.csv', 'a', newline='') as csvfile:
                        saveFile = csv.writer(csvfile, delimiter=',')
                        with open(dirTemp + f, 'r') as read:            
                            count = 0
                            for line in read:
                                if count == 0:
                                    doNothing = 0 #this will skip over the header                        
                                else:
                                    line = re.sub('\r', '', line)
                                    line = re.sub('\n', '', line)
                                    cells = line.split(',')
                                    saveFile.writerow([cell for cell in cells])
                                count += 1

        

    def _get_files_to_combine (self, dirTemp, frequency):
        files_to_combine = {}
        files = sorted(os.listdir(dirTemp))
        if frequency == "monthly":
            month = "00"
            for f in files:
                if f[-4:] =='.csv':
                    temp_month = f[4:6]
                    if month == temp_month:
                        files_to_combine[month].append(f)
                    else:
                        month = temp_month
                        files_to_combine.update({month:[f]})
        else:
            files_to_combine.update({"all" :  []})
            for f in files:
                if f[-4:] =='.csv':
                    files_to_combine["all"].append(f)

        return files_to_combine
