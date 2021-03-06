"""Tests for clippingutils.py"""

import pytest

from pathlib import Path
import numpy as np
from nna import clippingutils
from testparams import INPUTS_OUTPUTS_PATH
from testparams import SOUND_EXAMPLES
IO_clippingutils_path = INPUTS_OUTPUTS_PATH / "clippingutils/"


def compare_exact(first, second):
    """Return whether two dicts of arrays are exactly equal"""
    if first.keys() != second.keys():
        return False
    return all(np.array_equal(first[key], second[key]) for key in first)


# TODO: test with flac files and librosa
test_data_load_audio = [
    (
        SOUND_EXAMPLES / "10seconds.mp3",
        np.int16,
        "pydub",
        {
            "average_sound_array": -13.158468995418849,
            "sum_sound_array": -11581137,
            "array_shape": (2, 440064),
            "sampling_rate": 44100
        },
    ),
    (
        SOUND_EXAMPLES / "10minutes.mp3",
        np.int16,
        "pydub",
        {
            "average_sound_array": -0.7629345493367584,
            "sum_sound_array": -40373178,
            "array_shape": (2, 26459136),
            "sampling_rate": 44100,
        },
    ),
]


@pytest.mark.parametrize("filepath, dtype, backend, expected_stats",
                         test_data_load_audio)
def test_load_audio(filepath, dtype, backend, expected_stats):
    """test clippingutils.load_audio using stats of output array.

    Expected output is generated by:
    ```[python]
    expected_stats={}
    expected_stats["average_sound_array"]= np.average(sound_array)
    expected_stats["sum_sound_array"] = np.sum(sound_array)
    expected_stats["array_shape"] = sound_array.shape
    expected_stats["sampling_rate"]= sr
    ```

    """
    output = clippingutils.load_audio(filepath, dtype, backend)
    assert len(output) == 2
    sound_array, sr = output
    assert expected_stats["average_sound_array"] == np.average(sound_array)
    assert expected_stats["sum_sound_array"] == np.sum(sound_array)
    assert expected_stats["array_shape"] == sound_array.shape
    assert expected_stats["sampling_rate"] == sr


# TODO: add a example with high clipping rate
test_data_get_clipping_percent = [
    (
        IO_clippingutils_path / "get_clipping_percent" / "inputs" /
        "10minutes.mp3_sound_array.npy",
        1,
        [1.2887797999148574e-05, 0.0],
    ),
    (
        IO_clippingutils_path / "get_clipping_percent" / "inputs" /
        "10seconds.mp3_sound_array.npy",
        1,
        [0.0, 0.0],
    ),
]


@pytest.mark.parametrize("sound_array_path, threshold, expected",
                         test_data_get_clipping_percent)
def test_get_clipping_percent(sound_array_path, threshold, expected):
    """test clippingutils.get_clipping_percent using expected values.

        Input files are stored as npy at
           ./data/inputs/clippingutils/XXX_sound_array.npy
           Generated by:
           ```python
            from nna import clippingutils
            import numpy as np
            from testparams import SOUND_EXAMPLES
            from pathlib import Path

            filepath = SOUND_EXAMPLES / "10seconds.mp3"
            input_folder = Path('./data/inputs_outputs/clippingutils/')
            input_folder = input_folder / 'get_clipping_percent/inputs/'
            input_folder.mkdir(exist_ok=True)
            input_file = input_folder / '10seconds.mp3_sound_array.npy'
            sound_array, sr = clippingutils.load_audio(filepath,
                    dtype = np.int16,
                    backend="pydub",)
            np.save(str(input_file),sound_array)
           ```
    """

    sound_array = np.load(sound_array_path)
    output = clippingutils.get_clipping_percent(sound_array, threshold)
    assert output == expected


test_run_task_save_path = IO_clippingutils_path / "run_task_save/"

test_data_run_task_save = [
    (
        [
            "./data/sound_examples/10seconds.mp3",
            "./data/sound_examples/10minutes.mp3",
        ],
        "test_area",
        test_run_task_save_path / "outputs",
        1.0,  #clipping_threshold
        10,  #segment_len
        "pydub",
        True,
        (
            (
                test_run_task_save_path / "outputs" / "test_area_1,0.pkl",
                test_run_task_save_path / "expected_outputs" /
                "test_area_1,0.pkl",
            ),
            (
                test_run_task_save_path / "outputs" / "test_area_1,0_error.pkl",
                test_run_task_save_path / "expected_outputs" /
                "test_area_1,0.pkl_error.pkl",
            ),
        ),
    ),
]


@pytest.mark.parametrize(
    "allfiles, area_id, results_folder, clipping_threshold,segment_len," +
    "audio_load_backend, save, expected", test_data_run_task_save)
def test_run_task_save(allfiles, area_id, results_folder, clipping_threshold,
                       segment_len, audio_load_backend, save, expected):
    """test clippingutils.run_task_save using expected values.
    """
    assert isinstance(segment_len, int)
    # sound_array = np.load(sound_array_path)
    output = clippingutils.run_task_save(allfiles, area_id, results_folder,
                                         clipping_threshold, segment_len,
                                         audio_load_backend, save)
    assert len(output) == 2
    all_results_dict, files_w_errors = output
    assert len(files_w_errors) == 0
    for key in all_results_dict.keys():
        assert isinstance(key, str)
    all_results_dict_expected_path = expected[0][1]
    all_results_dict_output_path = expected[0][0]
    all_results_dict_expected = np.load(all_results_dict_expected_path,
                                        allow_pickle=True)[()]
    all_results_dict_output = np.load(all_results_dict_output_path,
                                      allow_pickle=True)[()]

    # assert all_results_dict_output == all_results_dict
    # assert all_results_dict_expected == all_results_dict_output
    assert compare_exact(all_results_dict_output, all_results_dict)
    assert compare_exact(all_results_dict_expected, all_results_dict_output)
    error_file_expected_path = expected[1][1]
    assert Path(error_file_expected_path).exists() is False
    all_results_dict_output_path.unlink()
