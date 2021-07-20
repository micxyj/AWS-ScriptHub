from tf2crf import CRF
import tensorflow as tf
def my_load_model(file_path):
    my_object={"loss":CRF.loss,"accuracy":CRF.accuracy}
    model_loaded = tf.keras.models.load_model(file_path,custom_objects=my_object)
    return model_loaded


if __name__=="__main__":
    model_path= "ModelWeights/model_zh/BiLSTM"
    model=my_load_model(model_path)

    test_a=[2450, 2127, 7057, 7031, 6982, 2420,    0,
            0,    0,    0,    0,    0,    0,    0,    0,
            0,    0,    0,    0,    0,    0,    0,    0,
            0,    0,    0,    0,    0,    0,    0]
    #[array([ 2,  7,  3,  8,  0,  5, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17,
     #  17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17])]
    test_b=[4205, 1377, 2453, 4888, 1061, 2170 ,
            0,    0,    0,    0,    0,    0,    0,    0,    0,
            0,    0,    0,    0,    0,    0,    0,    0,    0,
            0,    0,    0,    0,    0,    0]
    #[array([ 2,  7,  3,  8,  0,  5, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17,
    #   17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17])]
    print(model.predict([test_a]))
