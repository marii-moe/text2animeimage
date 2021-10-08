# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/DataLoading.ipynb (unless otherwise specified).

__all__ = ['df_text', 'get_filtered_image_files', 'BlackCrop', 'CropImageBlock', 'CropText', 'Remove1',
           'DALLE_dataloader']

# Cell
import torch
from PIL import Image,ImageFile
from pathlib import Path
from fastai.basics import *
from fastai.vision.data import *
from fastai.vision.all import *
from fastai.text.all import *
Image.LOAD_TRUNCATED_IMAGES=True
ImageFile.LOAD_TRUNCATED_IMAGES=True

# Cell
#export
@patch
@delegates(TfmdDL.new)
def new(self:SortedDL, dataset=None, **kwargs):
    res = self.res if dataset is None else None

    return super(SortedDL, self).new(dataset=dataset, **merge({'res':res}, kwargs))

# Cell
class df_text(Transform):
    def __init__(self,table,id_tags):
        self.table=table
        self.id_tags=id_tags
    def encodes(self,path):
        file_id=int(path.stem)
        tags=L(list(self.table[self.table.id==file_id].tags.item()))
        return [' '.join(tags.shuffle().map(lambda x:self.id_tags[x]))]
    def decodes(self,text):
        return TitledStr(' '.join(text))

# Cell
def get_filtered_image_files(path):
    return get_image_files(path).filter(lambda p:p.stem[-2:]!='_n')

# Cell
class BlackCrop(DisplayedTransform):
    split_idx,order = None,-1
    "Danbooru images have a black border added, can read more here: https://www.gwern.net/Danbooru2020"
    def __init__(self, table,  **kwargs):
        store_attr()
        super().__init__(**kwargs)

    def encodes(self, x:(Path)):
        x_id=int(x.stem)
        x=PILImage.create(x)
        entry = self.table[self.table.id==x_id]
        w,h=entry.image_width.item(),entry.image_height.item()
        #should remove uncroppable images from dataset
        if(w==0 or h==0): return PILImage(x)
        if(w>h):
            return PILImage(x.crop((0,256-256*h/w,512,256+256*h/w)))
        else:
            return PILImage(x.crop((256-256*w/h,0,256+256*w/h,512)))
def CropImageBlock(full_table,cls=PILImage):
    "A `TransformBlock` for images of `cls`"
    return TransformBlock(type_tfms=BlackCrop(full_table), batch_tfms=IntToFloatTensor)

# Cell
class CropText(Transform):
    order=50
    def __init__(self,max_len=72):
        self.max_len=max_len
    def encodes(self,x:TensorText):
        return retain_type(x[:self.max_len],x)

# Cell
class Remove1(Transform):
    def encodes(self,x):
        return next(x)

# Cell
def DALLE_dataloader(image_path,full_table,id_tags,bs=64,seq_len=72,max_len=72):
    with open('vocab.pkl','rb') as f: vocab=pickle.load(f)
    tok=SentencePieceTokenizer(max_vocab_sz=2500,sp_model=Path('tmp/spm.model'))
    text_block=TextBlock(tok,vocab=vocab)
    text_block.type_tfms.insert(1,Remove1())
    #text_block.type_tfms.insert(3,CropText())
    dblock = DataBlock(blocks    = (CropImageBlock(full_table),text_block, CategoryBlock),
                   get_items = get_filtered_image_files,
                   get_x     = [lambda x:x,df_text(full_table,id_tags)],
                   get_y     = lambda x:1,
                   splitter  = RandomSplitter(),
                   n_inp=2,
                   item_tfms = [Resize(224),CropText(max_len=max_len)]

                  )
    return dblock.dataloaders(image_path, bs=bs, max_len=max_len,seq_len=seq_len,pad_first=False,dl_kwargs=[{'res':range(2575225)},{'res':range(643806)},{}])