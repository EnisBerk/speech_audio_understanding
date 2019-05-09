import os
from pydub import AudioSegment
import sys

sys.path.insert(0, './audioset')
# import vggish_slim
# import vggish_params
import vggish_input
# import vggish_postprocess

import shutil

import numpy as np
import subprocess


def rmv_segmets(segments_folder):
	try:
		shutil.rmtree(segments_folder)
	except OSError as e:
		print ("Error: %s - %s." % (e.filename, e.strerror))


# create directories given set of file paths
def ig_f(dir, files):
	return [f for f in files if os.path.isfile(os.path.join(dir, f))]

def preb_names(mp3_file_path,output_dicretory,abs_input_path):
# def mp3toEmbed(mp3_file_path,output_dicretory,abs_input_path):
	# mp3_file_path="/home/data/nna/stinchcomb/NUI_DATA/18 Fish Creek 4/July 2016/FSHCK4_20160629_194935.MP3"
	# output_dicretory="/scratch/enis/data/nna/embeddings/"
	# abs_input_path="/home/data/nna/stinchcomb/NUI_DATA/"
	abs_len=len(abs_input_path)
	relative_path=mp3_file_path[abs_len:]
	mp3_file_name=os.path.basename(mp3_file_path)
	path_to_file=relative_path[:-len(mp3_file_name)]
	mp3_file_name=mp3_file_name.split(".")[0]
	# wav_file_name=mp3_file_name+".wav"
	# wav_file_path=os.path.join(output_dicretory,path_to_file,wav_file_name)
	embeddings_file_name=os.path.join(output_dicretory,path_to_file,mp3_file_name)+"_embeddings.npy"
	segments_folder=os.path.join(output_dicretory,path_to_file,mp3_file_name+"_segments/")
	pre_processed_folder=os.path.join(output_dicretory,path_to_file,mp3_file_name+"_preprocessed/")
	return mp3_file_path,segments_folder,embeddings_file_name,pre_processed_folder

# gs://deep_learning_enis/speech_audio_understanding/nna/test/
def divide_mp3(mp3_file_path,segments_folder,segment_len="01:00:00"):
	# print(segments_folder)
	# print("******",os.path.exists(segments_folder))
	sys.stdout.flush()
	if not os.path.exists(segments_folder):
		os.mkdir(segments_folder)
	sp = subprocess.run(['ffmpeg','-y','-i',mp3_file_path,"-c","copy","-map","0",
								"-segment_time", segment_len, "-f", "segment",
								segments_folder+"output%03d.mp3"],stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
	# sp.wait()
	print("processssssseing done")
	sys.stdout.flush()
	mp3_segments=os.listdir(segments_folder)
	return mp3_segments

def pre_process(mp3_segment,segments_folder,pre_processed_folder,saveNoReturn=False):
	# for mp3_segment in mp3_segments:
	input_file_path=segments_folder+mp3_segment
	tmp_npy=pre_processed_folder+mp3_segment[:-4]+".npy"
	#########
	wav_data = AudioSegment.from_mp3(input_file_path)
	sr=wav_data.frame_rate
	wav_data = wav_data.get_array_of_samples()
	wav_data = np.array(wav_data)
	##########

	assert wav_data.dtype == np.int16, 'Bad sample type: %r' % wav_data.dtype
	wav_data = wav_data/  32768.0  # Convert to [-1.0, +1.0]
	# print("ready to waveform")
	# sys.stdout.flush()
	# print(wav_data.size)
	sound= vggish_input.waveform_to_examples(wav_data, sr)
	# print(sound.size)
	sound=sound.astype(np.float32)
	# print("ready to return")
	# sys.stdout.flush()

	if saveNoReturn:
		np.save(tmp_npy,sound)
	else:
		return sound