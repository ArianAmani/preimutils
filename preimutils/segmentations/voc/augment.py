import albumentations as A
import cv2
import os
from tqdm import tqdm
from dataset_info import LabelMap
import utils
from count import export_path_count_for_each_label


class SegmentationAug:

    """A wrapper class on albumentations package to work on voc segmentation format easily

    Attributes:
        xmls_dir: annotations files paths.
        images_dir: images files paths.
    """

    file_counter = 0

    def __init__(self, label_map_path, masks_dir, images_dir):
        """
        Args:
            label_map_path (:obj:`str`): you should have a txt file like this
            object1:0,0,0::
            object2:128,0,0::
            object3:0,128,0::
            object4:128,128,0::
            object5:0,0,128::
            objectN:128,0,128::
            mask_dir (str): annotations files paths.
            images_dir (str) :images files paths.
        """

        assert os.path.exists(label_map_path), 'label_map .txt file not exist'
        self.label_handler = LabelMap(label_map_path)

        assert os.path.exists(
            masks_dir), 'XML path not exist please check the path'
        self._masks_dir = masks_dir

        assert os.path.exists(
            images_dir), 'Image path not exist please check the image path'
        self._images_dir = images_dir
        self.filters_of_aug = [

            A.ShiftScaleRotate(scale_limit=0.5, rotate_limit=0,
                               shift_limit=0.1, p=1, border_mode=0),
            A.RandomRotate90(p=0.2),
            A.RandomBrightnessContrast(p=0.2),
            A.RandomShadow(p=0.1),
            A.RandomSnow(snow_point_lower=0.1,
                         snow_point_upper=0.15, p=0.1),
            A.RGBShift(p=0.2),
            A.CLAHE(p=0.2),

            A.HueSaturationValue(
                p=0.1, hue_shift_limit=10, sat_shift_limit=10, val_shift_limit=10),

            A.MotionBlur(p=0.1),
            A.MedianBlur(p=0.2),
            A.ISONoise(p=0.2),
            A.Posterize(p=0.2),
            A.IAAPerspective(p=0.1),
            A.IAAPiecewiseAffine(p=0.1, scale=(0.01, 0.02)),
            A.IAAEmboss(p=0.2),
        ]
    def get_aug(self, aug):
        return A.Compose(aug)

    def augment_image(self, mask_path, quantity, resize=False, width=0, height=0):
        """augmentation for one picture depend on quantity that you get for it
        if your image and mask names are same
        save your aug image in your dataset path with the following pattern aug_{counter}.jpg

        Args:
            mask_path: single mask file path.
            quantity: quantity for your image to augment
            resize:(bool : optional)-> defult False ... resize your augmented images
            width:(int : optional) width for resized ... if resize True you should use this arg
            height:(int : optional) height for resized... if resize True you should use this arg
        Returns:
            No return
        """

        # if resize:
        #     filters_of_aug.append(A.Resize(width, height, always_apply=True))
        aug = self.get_aug(self.filters_of_aug)
        image_path = utils.find_image_from_mask(mask_path, self._images_dir)
        image = cv2.imread(image_path)
        mask = cv2.imread(mask_path)
        for i in tqdm(range(quantity), desc='Singel image'):
            augmented = aug(image=image, mask=mask)
            nimage = augmented['image']
            nmask = augmented['mask']
            SegmentationAug.file_counter += 1
            file_name = 'aug_{}'.format(SegmentationAug.file_counter)
            nimage_path = os.path.join(self._images_dir, file_name + '.jpg')
            nmask_path = os.path.join(self._masks_dir, file_name + '.png')
            cv2.imwrite(nimage_path, nimage)
            cv2.imwrite(nmask_path, nmask)

    def auto_augmentation(self,count_of_each):
        """auto augmentation for each picture depend on statistic of the object exist in your dataset
        if your image and xml names are same
        save your aug image in your dataset path with the following pattern aug_{counter}.jpg

        Args:
            count_of_each(int): How much of each label you want to have !
            resize:(bool : optional)-> defult False ... resize your augmented images
            width:(int : optional) width for resized ... if resize True you should use this arg
            height:(int : optional) height for resized... if resize True you should use this arg
        Returns:
            No return
        """
        labels_statistics = export_path_count_for_each_label(self.label_handler.color_label(),self._images_dir,self._masks_dir)
        for label in tqdm(self.label_handler.label_color()):
            print(label)
            count = labels_statistics[label]['count']
            masks_paths = labels_statistics[label]['masks_path']
            if not count:
                continue
            coefficient = count_of_each // count
            print(coefficient)
            for mask in masks_paths:
                self.augment_image(mask, coefficient)

