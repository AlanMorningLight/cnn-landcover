from Flevoland import Flevoland_Input
import Decoder
import time
from collections import Counter
import numpy as np
import CNNTrain_2D
import spectral.io.envi as envi
from spectral import imshow
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.feature_selection import SelectFromModel
from pandas_ml import ConfusionMatrix
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn import svm
from sklearn.neighbors import KNeighborsClassifier


# Input data
print("------------------------")
print("Input data")
print("------------------------")
input = Flevoland_Input.Flevoland_Input()
print("Training pixels", np.count_nonzero(input.train_data))
# print("Test pixels", np.count_nonzero(input.test_data))
print("------------------------")


# Configurable parameters
config = {}
patch_size = 5
feature_selection = False
apply_filter = False
classifiers = ["RF", "SVM", "1NN", "3NN", "5NN"]
classifier = classifiers[4]
seed = None
folder = 'Flevoland/'
rotation_oversampling = False

if "NN" in classifier:
    feature_selection = True


file = open(folder + "resultados.txt", "w+")

print("Patch size:" + str(patch_size))
file.write("\n--------------------------------\n")
file.write("Patch size: "+ str(patch_size) + "\n")
log_dir = folder + "resultados/" + classifier


a = time.time()


X_train, y_train,_ = input.read_data(patch_size)
X_train = X_train.reshape(len(X_train), -1)






if rotation_oversampling:
    X_train, y_train = input.rotation_oversampling(X_train, y_train)



print('Start training')


print(time.time() - a)

file.write("\n--------------------------------\n")
file.write("Size training set: %d\n" %len(X_train))
print("Size training set", len(X_train))


file.write("\n------------------\nResults for patch size " + str(patch_size) + ":\n")
file.write("Class distribution:\n")
file.write("#;Train;Test\n")
dtrain = Counter(y_train)
for i in range(input.num_classes):
    file.write(str(i + 1) + ";" + str(dtrain[i]) + ";" + "\n")




if feature_selection:
    fs = ExtraTreesClassifier(n_estimators=100)
    fs = fs.fit(X_train, y_train)
    model = SelectFromModel(fs, prefit=True)
    X_train = model.transform(X_train)
    print(X_train.shape)
else:
    model = None

if classifier == "RF":
    clf = RandomForestClassifier(n_estimators=100, max_depth=None, random_state=None, n_jobs=-1)
elif classifier == "SVM":
    clf = svm.SVC(C=50, gamma=0.01, kernel='rbf')
elif classifier == "1NN":
    clf = KNeighborsClassifier(n_neighbors=1, n_jobs=-1)
elif classifier == "3NN":
    clf = KNeighborsClassifier(n_neighbors=3, n_jobs=-1)
elif classifier == "5NN":
    clf = KNeighborsClassifier(n_neighbors=5, n_jobs=-1)

clf.fit(X_train, y_train)


train_acc = accuracy_score(y_train, clf.predict(X_train))*100

print("Train accuracy:" + str(train_acc))




# Clear memory
del X_train, y_train


#
#
# # Decode result
raw = Decoder.decode_sklearn(input, patch_size, clf , model)
#
#
# print("Train accuracy: ", train_acc)
# file.write("Train accuracy; %.3f" % train_acc + "\n")
# print("Test accuracy: ", test_acc)
# file.write("Test accuracy; %.3f" % test_acc + "\n")
# conf_matrix.to_dataframe().to_csv(config['log_dir'] + "conf_matrix" + str(config['patch_size']))
# conf_matrix.classification_report.to_csv(config['log_dir'] + "classification_report"
#                                          + str(config['patch_size']))
#
#
#
#
# # Output image
envi.save_image(log_dir + "ps" + str(patch_size) + ".hdr",
                 raw, dtype='uint8', force=True, interleave='BSQ', ext='raw')
#
#
output = Decoder.output_image(input, raw)
view = imshow(output)
plt.savefig(log_dir + str(patch_size) +'.png')
#
#
# # Image with legend
# labelPatches = [patches.Patch(color=input.color_scale.colorTics[x + 1] / 255., label=input.class_names[x]) for x in
#                 range(input.num_classes)]
# fig = plt.figure(2)
# lgd = plt.legend(handles=labelPatches, ncol=1, fontsize='small', loc=2, bbox_to_anchor=(1, 1))
# imshow(output, fignum=2)
# # fig.savefig(config['log_dir'] + 'img/' + str(patch_size) + '_lgd.png',
# # bbox_extra_artists=(lgd,), bbox_inches='tight')
#
#
# #save_rgb('ps'+str(patch_size)+'.png', output, format='png')
#
#
#
# file.close()
#

































