def functionTrain():
    print("Train")
    from keras.applications import VGG16
#from keras.applications import VGG16
    from keras.models import Sequential
    from keras.layers import Dense, Dropout, Activation, Flatten
    from keras.layers import Conv2D, MaxPooling2D, ZeroPadding2D
    from keras.layers.normalization import BatchNormalization
    from keras.models import Model
    from keras.optimizers import RMSprop
    from keras.preprocessing.image import ImageDataGenerator
    import os
    from keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau
    
    def addTopModel(bottom_model, num_classes, D=256):
        """creates the top or head of the model that will be 
        placed ontop of the bottom layers"""
        top_model = bottom_model.output
        top_model = Flatten(name = "flatten")(top_model)
        top_model = Dense(D, activation = "relu")(top_model)
        top_model = Dropout(0.3)(top_model)
        top_model = Dense(num_classes, activation = "softmax")(top_model)
        return top_model
    
    
    
    
    # Setting the input size now to 100 * 100 pixel 
    img_rows = 100
    img_cols = 100
    
    
    train_data_dir = './dataset/train'
    validation_data_dir = './dataset/test'
    
    train_datagen = ImageDataGenerator(
          rescale=1./255,
          rotation_range=20,
          width_shift_range=0.2,
          height_shift_range=0.2,
          horizontal_flip=True,
          fill_mode='nearest')
     
    test_datagen = ImageDataGenerator(rescale=1./255)
     
    # Change the batchsize according to your system RAM
    train_batchsize = 16
    test_batchsize = 10
     
    train_generator = train_datagen.flow_from_directory(
            train_data_dir,
            target_size=(img_rows, img_cols),
            batch_size=train_batchsize,
            class_mode='categorical')
     
    test_generator = test_datagen.flow_from_directory(
            validation_data_dir,
            target_size=(img_rows, img_cols),
            batch_size=test_batchsize,
            class_mode='categorical',
            shuffle=False)
    
    # Re-loads the VGG16 model without the top or FC layers
    vgg16 = VGG16(weights = 'imagenet', 
                     include_top = False, 
                     input_shape = (img_rows, img_cols, 3))
    
    # Freeze layers
    for layer in vgg16.layers:
        layer.trainable = False
        
    # Number of classes in the Flowers-17 dataset
    def fcount(path):
        count1 = 0
        for root, dirs, files in os.walk(path):
                count1 += len(dirs)
    
        return count1
    
    path = "./dataset/train"
    num_classes = fcount(path)
    
    FC_Head = addTopModel(vgg16, num_classes)
    
    model = Model(inputs=vgg16.input, outputs=FC_Head)
    
    print(model.summary())
    
    
    #from keras.optimizers import RMSprop
    
                 
    checkpoint = ModelCheckpoint("./classifier.h5",
                                 monitor="loss",
                                 mode="min",
                                 save_best_only = True,
                                 verbose=1)
    
    earlystop = EarlyStopping(monitor = 'loss', 
                              min_delta = 0, 
                              patience = 5,
                              verbose = 1,
                              restore_best_weights = True)
    
    reduce_lr = ReduceLROnPlateau(monitor = 'loss',
                                  factor = 0.2,
                                  patience = 3,
                                  verbose = 1,
                                  min_delta = 0.00001)
    
    
    # we put our call backs into a callback list
    callbacks = [earlystop, checkpoint, reduce_lr]
    
    # Note we use a very small learning rate 
    model.compile(loss = 'categorical_crossentropy',
                  optimizer = RMSprop(lr = 0.0001),
                  metrics = ['accuracy'])
    
    nb_train_samples = 101 * num_classes
    nb_validation_samples = 101  * num_classes
    epochs = 3
    batch_size = 16
    
    history = model.fit_generator(
        train_generator,
        steps_per_epoch = nb_train_samples // batch_size,
        epochs = epochs,
        callbacks = callbacks)
    
    model.save("./classifier.h5")
    
    