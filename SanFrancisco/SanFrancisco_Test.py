from SanFrancisco import SanFrancisco_Input
from SanFrancisco import SanFrancisco_Decoder as Decoder
import time
from collections import Counter
import numpy as np
import CNNTrain_2D
import spectral.io.envi as envi
from spectral import imshow
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from sklearn.model_selection import train_test_split


def make_hparam_string(patch_size):
    return "ps%d" % patch_size


# Input data
print("------------------------")
print("Input data")
print("------------------------")
input = SanFrancisco_Input.SanFrancisco_Input()
print("Training pixels", np.count_nonzero(input.train_data))
print("------------------------")


# Configurable parameters
config = {}
config['patch_size'] = 3
config['in_channels'] = input.bands
config['num_classes'] = input.num_classes
config['kernel_size'] = 3
config['conv1_channels'] = 32
config['conv2_channels'] = 64
config['fc1_units'] = 1024
config['batch_size'] = 16
config['max_epochs'] = 15
config['train_dropout'] = 0.8
config['initial_learning_rate'] = 0.01
config['decaying_lr'] = True
config['seed'] = None
folder = 'SanFrancisco/'
oversampling = False
rotation_oversampling = False
validation_set = False




file = open(folder + "resultados.txt", "w+")

for patch_size in [15]:

    print("Patch size:" + str(patch_size))
    config['patch_size'] = patch_size
    log_dir = folder + "resultados/ps" + str(patch_size) + "/"
    config['log_dir'] = log_dir

    a = time.time()

    X_train, y_train,_ = input.read_data(config['patch_size'])
    _, X_test, _, y_test = train_test_split(X_train, y_train, test_size=0.1, random_state=None)

    # X, y = input.read_data(config['patch_size'])
    # X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=None)
    #X_test, y_test, X_train, y_train = input.read_data(config['patch_size'])


    if validation_set:
        X_train, X_val, y_train, y_val = \
            train_test_split(X_train, y_train, test_size=0.5, random_state=42, stratify=y_train)


    if oversampling:
        X_train, y_train = input.oversample_data(X_train, y_train, patch_size)

    if rotation_oversampling:
        X_train, y_train = input.rotation_oversampling(X_train, y_train)




    print('Start training')


    print(time.time() - a)

    file.write("\n--------------------------------\n")
    file.write("Size training set: %d\n" %len(X_train))
    print("Size training set", len(X_train))
    if validation_set:
        file.write("Size validation set: %d\n" % len(X_val))
        print("Size validation set", len(X_val))
    file.write("Size test set: %d\n" %len(X_test))
    print("Size test set", len(X_test))


    file.write("\n------------------\nResults for patch size " + str(patch_size) + ":\n")


    if validation_set:
        file.write("Class distribution:\n")
        file.write("#;Train;Validation;Test\n")
        dtrain = Counter(y_train)
        dval = Counter(y_val)
        dtest = Counter(y_test)
        for i in range(input.num_classes):
            file.write(str(i+1)+";" + str(dtrain[i]) + ";" + str(dval[i]) + ";" + str(dtest[i]) + "\n")
    #
        save_path, val_acc,  conf_matrix = CNNTrain_2D.train_model(X_train, y_train, X_val, y_val, config)
        # save_path, final_test_acc,  conf_matrix = CNNTrain_2D.train_model(X_test, y_test, X_train, y_train, config)

        # Clear memory
        del X_train, X_val, X_test, y_train, y_val, y_test

    else:
        file.write("Class distribution:\n")
        file.write("#;Train;Test\n")
        dtrain = Counter(y_train)
        dtest = Counter(y_test)
        for i in range(input.num_classes):
            file.write(str(i + 1) + ";" + str(dtrain[i]) + ";" + str(dtest[i]) + "\n")

        save_path, test_acc, conf_matrix = CNNTrain_2D.train_model(X_train, y_train, X_test, y_test, config)

        # Clear memory
        del X_train, X_test, y_train, y_test




    train_acc, test_acc= 0, 0
    # Decode result
    raw = Decoder.decode(input, config, save_path)

    print("Train accuracy: ", train_acc)
    file.write("Train accuracy; %.3f" % train_acc + "\n")
    if validation_set:
        print("Validation accuracy: ", val_acc)
        file.write("Validation accuracy; %.3f" % val_acc + "\n")
    print("Test accuracy: ", test_acc)
    file.write("Test accuracy; %.3f" % test_acc + "\n")
    conf_matrix.to_dataframe().to_csv(config['log_dir'] + "conf_matrix" + str(patch_size))
    conf_matrix.classification_report.to_csv(config['log_dir'] + "classification_report"
                                             + str(patch_size))



    # Output image
    envi.save_image(config['log_dir'] + "ps" + str(patch_size) + ".hdr",
                    raw, dtype='uint8', force=True, interleave='BSQ', ext='raw')


    output = Decoder.output_image(input, raw)
    # view = imshow(output)
    # plt.savefig(config['log_dir'] + 'img/' + str(patch_size) +'.png')


    # Image with legend
    labelPatches = [patches.Patch(color=input.color_scale.colorTics[x + 1] / 255., label=input.class_names[x]) for x in
                    range(input.num_classes)]
    fig = plt.figure(2)
    lgd = plt.legend(handles=labelPatches, ncol=1, fontsize='small', loc=2, bbox_to_anchor=(1, 1))
    imshow(output, fignum=2)
    # fig.savefig(config['log_dir'] + 'img/' + str(patch_size) + '_lgd.png',
    # bbox_extra_artists=(lgd,), bbox_inches='tight')


    #save_rgb('ps'+str(patch_size)+'.png', output, format='png')



file.close()


































