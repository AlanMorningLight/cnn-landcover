import spectral.io.envi as envi
from IndianPines import IndianPines_Input
import numpy as np
from spectral import imshow, get_rgb
from scipy import ndimage, stats
import matplotlib.patches as patches
import matplotlib.pyplot as plt
from pandas_ml import ConfusionMatrix


input = IndianPines_Input.IndianPines_Input()

img = envi.open('IndianPines/resultadosPatch/ps3/ps3.hdr', 'IndianPines/resultadosPatch/ps3/ps3.raw')
patch_size = 9

def modal(x):
    return stats.mode(x, axis=None)[0][0]

def mode_filter(img):
    return ndimage.generic_filter(img, modal, size=5)



def accuracy(input, img):

    correct_pixels_train, correct_pixels_test = [], []

    for i in range(input.height):
        for j in range(input.width):

            y_ = img[i, j]

            label = 0
            is_train = input.train_data[i, j] != 0
            is_test = input.test_data[i, j] != 0

            if is_train:
                label = input.train_data[i, j]
            elif is_test:
                label = input.test_data[i, j]

            if label == y_:
                if is_train:
                    correct_pixels_train.append(1)
                elif is_test:
                    correct_pixels_test.append(1)
            else:
                if is_train:
                    correct_pixels_train.append(0)
                elif is_test:
                    correct_pixels_test.append(0)


    train_acc = np.asarray(correct_pixels_train).mean() * 100
    test_acc = np.asarray(correct_pixels_test).mean() * 100
    return train_acc, test_acc


def output_image(input, output):
    return get_rgb(output, color_scale=input.color_scale)


def clean_image(input, img):
    clean = np.zeros(shape=(input.height, input.width))

    for i in range(input.height):
        for j in range(input.width):

            label = img[i, j]

            is_train = input.train_data[i, j] != 0
            is_test = input.test_data[i, j] != 0

            if is_train or is_test:
                clean[i, j] = label


    return clean


def apply_modal_filter(input, img):

    filt_img = img

    for n in range(5):
        print("---------------")
        print("Iteration " + str(n))
        filt_img = mode_filter(filt_img)

        train_acc, test_acc = accuracy(input, filt_img)
        print("Training accuracy: %.2f" %train_acc)
        print("Test accuracy: %.2f" %test_acc)

    clean_img = clean_image(input, filt_img)
    return clean_img, test_acc


def get_conf_matrix(input, img):

    test_labels, test_predictions = [], []

    for i in range(input.height):
        for j in range(input.width):

            y_ = img[i, j]
            label = input.complete_gt[i, j]
            is_test = input.test_data[i, j] != 0
            if is_test:

                if is_test:
                    test_labels.append(label)
                    test_predictions.append(y_)

    conf_matrix = ConfusionMatrix(test_labels, test_predictions)

    return conf_matrix



#
labelPatches = [patches.Patch(color=input.color_scale.colorTics[x+1]/255., label=input.class_names[x]) for x in range(input.num_classes) ]


train_acc, test_acc = accuracy(input,img)
view = output_image(input, img)
# imshow(view)
clean_img = clean_image(input, img)
view = output_image(input, clean_img)
# imshow(view)




print("Training accuracy: %.2f" %train_acc)
print("Test accuracy: %.2f" %test_acc)

print("---------------")
print("Modal filter")
filt_img = img.load()

for n in range(5):
    print("---------------")
    print("Iteration " + str(n))
    filt_img = mode_filter(filt_img)

    train_acc, test_acc = accuracy(input, filt_img)
    print("Training accuracy: %.2f" %train_acc)
    print("Test accuracy: %.2f" %test_acc)

view = output_image(input, filt_img)
fig = plt.figure(1)
lgd = plt.legend(handles=labelPatches, ncol=1, fontsize='small', loc=2, bbox_to_anchor=(1, 1))
imshow(view, fignum=1)
fig.savefig("IndianPines/resultadosPatch/ps"+str(patch_size)+"/ilt_lgd", bbox_extra_artists=(lgd,), bbox_inches='tight')



clean_img = clean_image(input, filt_img)
view = output_image(input, clean_img)
fig = plt.figure(2)
lgd = plt.legend(handles=labelPatches, ncol=1, fontsize='small', loc=2, bbox_to_anchor=(1, 1))
imshow(view, fignum=2)
fig.savefig("IndianPines/resultadosPatch/ps"+str(patch_size)+"/filt_clean_lgd", bbox_extra_artists=(lgd,), bbox_inches='tight')
#
envi.save_image("IndianPines/resultadosPatch/ps"+str(patch_size)+"/ip_filtro5.hdr", filt_img, dtype='uint8', force=True, interleave='BSQ', ext='raw')
#
