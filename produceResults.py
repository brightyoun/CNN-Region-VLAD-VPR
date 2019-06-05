from sklearn.metrics import precision_recall_curve,auc,average_precision_score
import os
import matplotlib.pyplot as plt
import pickle
from pylab import imread,subplot,imshow,show
import matplotlib.gridspec as gridspec

DATASETS = ["berlin_halenseestrasse","berlin_kudamm","berlin_A100","GardenPointWalking","Synthesized_Nordland"]
REFERENCE_DATASET = ["berlin_halenseestrasse_1","berlin_kudamm_1","berlin_A100_2","night_right","summer"]
TEST_DATASET = ["berlin_halenseestrasse_2","berlin_kudamm_2","berlin_A100_1","day_left","winter"]

Configuration1=["200","128"]
Configuration2=["400","256"]

Settings = [Configuration1,Configuration2]

dir = "../CNN-Region-VLAD-VPR/"


def load_obj(name ):
    with open( name, 'rb') as f:
        return pickle.load(f)
    
datasetIndex = 4
img_for=".jpg"
#imgTag= "images-"
imgTag= ""

dataset = DATASETS[datasetIndex]
testTraverse = TEST_DATASET[datasetIndex]
referenceTraverse = REFERENCE_DATASET[datasetIndex]

def showAUCPR():
    files_list=[]
    datasetPath = os.path.join(dir,dataset)
    testPath = os.path.join(dir,dataset,testTraverse)
    referencePath = os.path.join(dir,dataset,referenceTraverse)
    
    
    for file in os.listdir(datasetPath):
        if file.endswith(".pkl"):
            files_list.append(file)
        else:
            continue 
    resultPath = os.path.join(dir,dataset,"Result")
    PR_values = list()
    for ind,file in enumerate(files_list): 

        N = file.split("_")[2]
        V = (file.split("_")[3]).split(".")[0]
        Results = load_obj(os.path.join(datasetPath,file))

        print(dataset,N,V)
        
        predictionLabel,predictionScore = list(),list()
        for _,result in Results.items():
            predictionLabel.append(result[1])
            predictionScore.append(result[2])
        
        precision, recall, thresholds = precision_recall_curve(predictionLabel,predictionScore)
                
        plt.step(recall, precision, alpha=0.2,
                 where='post')
        plt.fill_between(recall, precision, step='post', alpha=0.2)
        
        plt.xlabel('Recall')
        plt.ylabel('Precision')
        plt.ylim([0.0, 1.05])
        plt.xlim([0.0, 1.0])
#        PR_values.append(str(auc(recall, precision)))
        tiTle= "Region-VLAD " +dataset + " AUC-PR: " + str(auc(recall, precision))
        plt.grid(True)
       # plt.legend(tiTle)
        plt.title(tiTle,fontsize=8)
        plt.savefig(os.path.join(resultPath,"AUC-PR"+"_"+str(N)+"_"+str(V)+'.jpg'),dpi=200)
        plt.close()                             

def groundTruth():
    
    folderPath="../..../berlin_kudamm/"
    ImgFolderList=["berlin_kudamm_2","berlin_kudamm_1"]
    keylist,values = list(),defaultdict(list)
    ImgVsGps = defaultdict(list)   
    folder = list() 
    latLongList = list()
        
    for ind,path in enumerate(ImgFolderList):
        folder.append(os.path.join(folderPath,path))
        for file in os.listdir(folder[ind]):
            if file.endswith(".jpg"):
                if "." in file[0]:
                    continue
                keylist.append(file.split(".jpg")[0])
        
        save_obj(keylist,os.path.join(folder[ind],"imgIds.pickle"))  
        keyList = load_obj(os.path.join(folder[ind],"imgIds.pickle"))
        
        latLongList.clear()
        
        
        for file in keyList:
            with open(os.path.join(folder[ind],file+".jpg.json")) as f:
                Data = json.load(f)
                latLongList.append(Data["lon"])
                latLongList.append(Data["lat"])
                ImgVsGps[file]=latLongList.copy()
                latLongList.clear()
                    
        save_obj(OrderedDict(sorted(ImgVsGps.items(), key=operator.itemgetter(1))), os.path.join(folder[ind],"imgsVsGps.pickle") )       
        values[ind]=(load_obj(os.path.join(folder[ind],"imgsVsGps.pickle")))
        print(values[ind])
        keylist.clear()
        ImgVsGps.clear()

    path1,path2, dif = defaultdict(list),defaultdict(list) , defaultdict(list) 
     
    for key1, val1 in values[0].items():
        for key2, val2 in values[1].items():
            dif[key2] = math.sqrt(sum([(a - b)**2 for a, b in zip(val1, val2)]))
        path1[key1] = list(OrderedDict(sorted(dif.items(), key=operator.itemgetter(1),reverse=False)).keys())[:5]  
        dif.clear()

    print(path1)
    save_obj(path1, os.path.join(folder[0],"groundTruth.pickle")) 
    
    for key1, val1 in values[1].items():
        for key2, val2 in values[0].items():
            dif[key2] = math.sqrt(sum([(a - b)**2 for a, b in zip(val1, val2)]))
        path2[key1] = list(OrderedDict(sorted(dif.items(), key=operator.itemgetter(1),reverse=False)).keys())[:5]   
        dif.clear()
        
    save_obj(path2,os.path.join(folder[1],"groundTruth.pickle"))
    print(path2)

def showResults():
    
    files_list=[]
    datasetPath = os.path.join(dir,dataset)
    testPath = os.path.join(dir,dataset,testTraverse)
    referencePath = os.path.join(dir,dataset,referenceTraverse)
    
    
    for file in os.listdir(datasetPath):
        if file.endswith(".pkl"):
            files_list.append(file)
        else:
            continue 
    
    for ind,file in enumerate(files_list): 

        N = file.split("_")[2]
        V = (file.split("_")[3]).split(".")[0]
        Results = load_obj(os.path.join(datasetPath,file))
        columns = 3
        rows = 1 # 8
        total = columns * rows
        box = dict(facecolor='yellow', pad=5, alpha=0.2)
        print(dataset,N,V)
        resultPath = os.path.join(dir,dataset,"Result",str(N)+"_"+str(V))

        for testImgName,result in Results.items():
            testImg = os.path.join(testPath,imgTag+testImgName+img_for)
            fig, ax = plt.subplots(rows, columns,sharex=True, sharey=True,figsize=(14,6))
            start_col=0
            gndTruthImgName = result[0]
            predictionLabel = result[1]
            predictionScore = result[2]
            retrievedImgName = result[3]
            gndTruthImg = os.path.join(referencePath,imgTag+gndTruthImgName+img_for)
            retrivedImg = os.path.join(referencePath,imgTag+retrievedImgName+img_for)

            ax[start_col].set_title('TestImage\n'+testImgName,bbox=box,fontsize=13)
            ax[start_col].imshow(plt.imread(testImg),interpolation='nearest', aspect='auto')
            ax[start_col].set_xticks([])
            ax[start_col].set_yticks([])
            start_col +=1

            ax[start_col].set_title('Ground Truth\n'+gndTruthImgName,bbox=box,fontsize=13)
            ax[start_col].imshow(plt.imread(gndTruthImg),interpolation='nearest', aspect='auto')
            ax[start_col].set_xticks([])
            ax[start_col].set_yticks([])
            start_col +=1
            if predictionLabel==1:
                ax[start_col].set_title('Retrieved Image\n'+retrievedImgName,bbox=box,color='g',fontsize=13)
            else:
                ax[start_col].set_title('Retrieved Image\n'+retrievedImgName,bbox=box,color='r',fontsize=13)
            ax[start_col].imshow(plt.imread(retrivedImg),interpolation='nearest', aspect='auto')
            ax[start_col].set_xticks([])
            ax[start_col].set_yticks([])
            plt.savefig(os.path.join(resultPath,testImgName+'.png'),dpi=200)
            plt.close()                             

showAUCPR()
showResults()

