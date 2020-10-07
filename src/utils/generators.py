import os
import sys
import tensorflow as tf
import pandas as pd
from tensorflow.keras.preprocessing.image import *
from sklearn.datasets import make_blobs
from tensorflow.python.keras.preprocessing.image_dataset import \
    image_dataset_from_directory

sys.path.insert(0, './')
from data_augmentation import *


def get_generator(dataset_parameters, model_parameters):
    num_classes = dataset_parameters['num_classes']
    training_data_generator = get_data_generator(dataset_parameters)
    validation_data_generator = get_data_generator(dataset_parameters, False)

    if dataset_parameters['dataset_name'] == 'cifar10':
        # load the images from keras
        (training_images, training_labels), (test_images, test_label) \
            = tf.keras.datasets.cifar10.load_data()

        # one-hot-encode the labels
        training_labels = tf.keras.utils. \
            to_categorical(training_labels, num_classes)
        test_label = tf.keras.utils. \
            to_categorical(test_label, num_classes)

        # create generators for easier use in model.fit()
        training_generator = training_data_generator.flow(
            training_images,
            training_labels,
            batch_size=model_parameters['batch_size']
        )
        validation_generator = validation_data_generator.flow(
            test_images,
            test_label
        )

    elif 'csv' in dataset_parameters['labels_type']:
        training_dataframe = pd.read_csv(
            model_parameters['csv_training_file'])
        validation_dataframe = pd.read_csv(
            model_parameters['csv_validation_file'])

        training_generator = training_data_generator.flow_from_dataframe(
            dataframe=training_dataframe,
            directory=dataset_parameters['training_directory'],
            x_col='subDirectory_filePath',
            y_col=dataset_parameters['class_label'],
            has_ext=True,
            class_mode='categorical',
            target_size=(model_parameters['image_height'],
                         model_parameters['image_width']),
            batch_size=model_parameters['batch_size'],
            shuffle=True
        )

        validation_generator = validation_data_generator.flow_from_dataframe(
            dataframe=validation_dataframe,
            directory=dataset_parameters['validation_directory'],
            x_col='subDirectory_filePath',
            y_col=dataset_parameters['class_label'],
            has_ext=True,
            class_mode='categorical',
            target_size=(model_parameters['img_height'],
                         model_parameters['img_width']),
            batch_size=model_parameters['batch_size'],
            shuffle=False,
        )

    elif 'directory' in dataset_parameters['labels_type']:
        training_directory = dataset_parameters['training_directory']
        validation_directory = dataset_parameters['validation_directory']

        if not os.path.isdir(training_directory):
            raise ValueError('Training directory does not exist',
                             training_directory)
        if not os.path.isdir(validation_directory):
            raise ValueError('Validation directory does not exist',
                             validation_directory)

        training_generator = image_dataset_from_directory(
            training_directory,
            label_mode='categorical',
            class_names=dataset_parameters['class_names'],
            batch_size=model_parameters['batch_size'],
            image_size=(model_parameters['img_height'],
                        model_parameters['img_width']),
            shuffle=True,
        )
        validation_generator = image_dataset_from_directory(
            validation_directory,
            label_mode='categorical',
            class_names=dataset_parameters['class_names'],
            image_size=(model_parameters['img_height'],
                        model_parameters['img_width']),
            shuffle=True,
        )

    # not working? blob are can only be created as shape (samples, features)
    elif dataset_parameters['dataset_name'] == 'blob':
        training_data, training_labels = make_blobs(n_samples=1000,
                                                    n_features=3,
                                                    centers=num_classes,
                                                    random_state=0)
        test_data, test_label = make_blobs(n_samples=100,
                                           n_features=3,
                                           centers=num_classes,
                                           random_state=0)

        training_labels = tf.keras.utils.to_categorical(training_labels,
                                                        num_classes)
        test_label = tf.keras.utils.to_categorical(test_label,
                                                   num_classes)

        training_generator = [training_data, training_labels]
        validation_generator = [test_data, test_label]

    return training_generator, validation_generator
