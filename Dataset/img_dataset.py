import torch
import torchvision
from torchvision import transforms
import numpy as np
import cv2
from collections import OrderedDict
import glob
import os

from torch.utils.data import Dataset
from torch.utils.data import DataLoader
from torchvision.transforms import ToTensor

rng = np.random.RandomState(2017)


def np_load_frame(filename, resize_height, resize_width):
    image_decoded = cv2.imread(filename)
    image_resized = cv2.resize(image_decoded, (resize_width, resize_height))
    image_resized = image_resized.astype(dtype=np.float32)
    image_resized = image_resized / 255.0
    image_resized = np.transpose(image_resized, [2, 0, 1])
    return image_resized


class ano_pred_Dataset(Dataset):
    """
    No data augmentation.
    Normalized from [0,255] to [0,1], the channels are BGR due to cv2 and liteFlownet.
    """

    # video clip mean
    def __init__(self, dataset_folder, clip_length, size=(256, 256)):
        self.dir = dataset_folder
        self.videos = OrderedDict()
        self.image_height = size[0]
        self.image_width = size[1]
        self.clip_length = clip_length
        self.setup()

    def __len__(self):
        return len(self.videos)

    def setup(self):
        videos = glob.glob(os.path.join(self.dir, '*'))
        for video in sorted(videos):
            video_name = video.split('/')[-1]
            self.videos[video_name] = {}
            self.videos[video_name]['path'] = video
            self.videos[video_name]['frame'] = glob.glob(os.path.join(video, '*.jpg'))
            self.videos[video_name]['frame'].sort()
            self.videos[video_name]['length'] = len(self.videos[video_name]['frame'])
        self.videos_keys = self.videos.keys()

    def __getitem__(self, indice):
        # When getting frames, 5 frames are one unit, shuffle across all video folders and all frames in one folder.
        key = list(self.videos_keys)[indice]
        start = rng.randint(0, self.videos[key]['length'] - self.clip_length)
        video_clip = []

        for frame_id in range(start, start + self.clip_length):
            video_clip.append(np_load_frame(self.videos[key]['frame'][frame_id], self.image_height, self.image_width))

        video_clip = np.array(video_clip).reshape((-1, self.image_height, self.image_width))
        video_clip = torch.from_numpy(video_clip)

        return video_clip


class test_dataset(Dataset):
    def __init__(self, video_folder, clip_length, size=(256, 256)):
        self.path = video_folder
        self.clip_length = clip_length
        self.img_height, self.img_width = size
        self.pics = glob.glob(self.path + '/*.jpg')
        self.pics.sort()

    def __len__(self):
        return len(self.pics) - 4

    def __getitem__(self, indice):
        video_clips = []
        for frame_id in range(indice, indice + self.clip_length):
            video_clips.append(np_load_frame(self.pics[frame_id], self.img_height, self.img_width))

        video_clips = np.array(video_clips).reshape((-1, self.img_height, self.img_width))
        video_clips = torch.from_numpy(video_clips)
        return video_clips
