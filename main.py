from subprocess import Popen, PIPE
from pre_process_func import *

import os, shutil
import tensorflow as tf

from time import time
import argparse
import sys
import numpy as np

sys.path.insert(0, './audioset')
import vggish_slim
import vggish_params
import vggish_input
import vggish_postprocess
# sp = subprocess.run(["conda","run","-n","speechEnv","python", "test_env.py"],stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
# print(sp.stdout)

#async


ram_memory=100 #GB
segment_length=1 #hour
cpu_count=50
file_per_epoch=70

#1 hour is 0.04
memory_usage=(0.04*30*segment_length*cpu_count)
disk_space=500 #gb
disk_usage= file_per_epoch*2 #gb
assert disk_usage<=disk_space, "not enough disk space"
assert memory_usage<=ram_memory, "not enough ram memory"

abs_input_path="/home/data/nna/stinchcomb/NUI_DATA/"
output_folder="/scratch/enis/data/nna/NUI_DATA/"

if not os.path.exists(output_folder):
    SRC=abs_input_path
    DEST=output_folder
    shutil.copytree(SRC, DEST, ignore=ig_f)

def CreateVGGishNetwork(hop_size=0.96):   # Hop size is in seconds.
    """Define VGGish model, load the checkpoint, and return a dictionary that points
    to the different tensors defined by the model.
    """

    vggish_slim.define_vggish_slim(training=False)
    checkpoint_path = 'vggish_model.ckpt'
    vggish_params.EXAMPLE_HOP_SECONDS = hop_size

    vggish_slim.load_vggish_slim_checkpoint(sess, checkpoint_path)

    features_tensor = sess.graph.get_tensor_by_name(
      vggish_params.INPUT_TENSOR_NAME)
    embedding_tensor = sess.graph.get_tensor_by_name(
      vggish_params.OUTPUT_TENSOR_NAME)

    layers = {'conv1': 'vggish/conv1/Relu',
    'pool1': 'vggish/pool1/MaxPool',
    'conv2': 'vggish/conv2/Relu',
    'pool2': 'vggish/pool2/MaxPool',
    'conv3': 'vggish/conv3/conv3_2/Relu',
    'pool3': 'vggish/pool3/MaxPool',
    'conv4': 'vggish/conv4/conv4_2/Relu',
    'pool4': 'vggish/pool4/MaxPool',
    'fc1': 'vggish/fc1/fc1_2/Relu',
    'fc2': 'vggish/fc2/Relu',
    'embedding': 'vggish/embedding',
    'features': 'vggish/input_features',
     }
    g = tf.get_default_graph()
    for k in layers:
        layers[k] = g.get_tensor_by_name( layers[k] + ':0')
        pca_params_path="./vggish_pca_params.npz"
        pproc = vggish_postprocess.Postprocessor(pca_params_path)

    return {'features': features_tensor,
      'embedding': embedding_tensor,
      'layers': layers,
     },pproc

def inference(pre_processed_npy_files,vgg,sess,embeddings_file_name,batch_size=256):
    # print("len sounds",len(sounds))
    embeddings = np.array([], dtype=np.int16).reshape(0,128)
    for npy_file in pre_processed_npy_files:
        sound=np.load(npy_file)
        # for sound in sounds:
        # print(len(sound))
        numberoffiles=sound.shape[0]
        for batch_index in range(0,numberoffiles,batch_size):
            # print("inference")
            if (batch_index+batch_size) <numberoffiles:
                a_batch=sound[batch_index:batch_index+batch_size]
            else:
                a_batch=sound[batch_index:]
            [embedding_batch] = sess.run([vgg['embedding']],
                feed_dict={vgg['features']: a_batch})
            embeddings = np.concatenate((embeddings,embedding_batch))
        # print("postprocess")
        # del sounds
    raw_embeddings_file_name=embeddings_file_name[:-15]+"rawembeddings.npy"
    np.save(raw_embeddings_file_name,embeddings)
    postprocessed_batch = pproc.postprocess(embeddings)
    # del embeddings
    # print("saving")
    np.save(embeddings_file_name,postprocessed_batch)
    # del postprocessed_batch
    return embeddings_file_name


########################main.py
my_file=open("/home/enis/projects/nna/mp3files.txt","r+")
temp = my_file.read().splitlines()
my_file.close()

tf.reset_default_graph()
sess = tf.Session()
vgg,pproc = CreateVGGishNetwork()

for i in range(0,len(temp),file_per_epoch):
    epoch_files=temp[i:i+file_per_epoch]
    with open("/home/enis/projects/nna/input.txt", 'w') as f:
        for item in epoch_files:
            k=f.write("%s\n" % item)
    command_text="conda run -n speechEnv "
    command_text+="cat /home/enis/projects/nna/input.txt | "
    command_text+="parallel -P {} -n 1 ".format(cpu_count)
    command_text+="python pipe_pre.py --input_files {} > logs.txt"
    command_list=command_text.split(" ")
    process = Popen(command_list, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    ##### step - 0 get prepare names
    for input_file in epoch_files:
        mp3_file_path,segments_folder,embeddings_file_name,pre_processed_folder=preb_names(input_file,output_folder,abs_input_path)
        pre_processed_npy_files=[pre_processed_folder+file for file in os.listdir(pre_processed_folder)]
        embeddings_file_name=inference(pre_processed_npy_files,vgg,sess,embeddings_file_name,batch_size=128)
        rmv_segmets(pre_processed_folder)

# this one does VGGish inference
