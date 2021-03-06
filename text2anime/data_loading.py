# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/DataLoading.ipynb (unless otherwise specified).

__all__ = ['df_text', 'get_filtered_image_files', 'open_image', 'MyImageBlock', 'Remove1', 'DALLE_dataloader']

# Cell
import torch
from PIL import Image
from pathlib import Path
from fastai.basics import *
from fastai.vision.data import *
from fastai.vision.all import *
from fastai.text.all import *

# Cell
#export
@patch
@delegates(TfmdDL.new)
def new(self:SortedDL, dataset=None, **kwargs):
    res = self.res if dataset is None else None

    return super(SortedDL, self).new(dataset=dataset, **merge({'res':res}, kwargs))

# Cell
class df_text(Transform):
    def __init__(self,table):
        self.table=table
    def encodes(self,path):
        file_id=int(path.stem)
        tags=L(list(self.table[self.table.id==file_id].tags.item()))
        return [' '.join(tags.shuffle().map(lambda x:id_tags[x]))]
    def decodes(self,text):
        return TitledStr(' '.join(text))

# Cell
def get_filtered_image_files(path):
    return get_image_files(path).filter(lambda p:p.stem[-2:]!='_n')

# Cell
def open_image(path):
    file_id=int(path.stem)
    img=PILImage.create(path)
    width=int(full_table[full_table.id==file_id].image_width.item())
    height=int(full_table[full_table.id==file_id].image_height.item())
    pw, ph = img.size
    if(width>height): dim=(0,(1-height/width)*256,512,256+height/width*256)
    else: dim=((1-width/height)*256,0,256+width/height*256,512)
    return PILImage(img.crop(dim))

# Cell
def MyImageBlock(cls=PILImage):
    "A `TransformBlock` for images of `cls`"
    return TransformBlock(type_tfms=open_image, batch_tfms=IntToFloatTensor)

# Cell
class Remove1(Transform):
    def encodes(self,x):
        return next(x)

# Cell
def DALLE_dataloader():
    with open('vocab.pkl','rb') as f: vocab=pickle.load(f)
    tok=SentencePieceTokenizer(max_vocab_sz=2500,sp_model=Path('tmp/spm.model'))
    text_block=TextBlock(tok,vocab=vocab)
    text_block.type_tfms.insert(1,Remove1())
    dblock = DataBlock(blocks    = (MyImageBlock,text_block, CategoryBlock),
                   get_items = get_filtered_image_files,
                   get_x     = [lambda x:x,df_text(full_table)],
                   get_y     = lambda x:1,
                   splitter  = RandomSplitter(),
                   n_inp=2,
                   item_tfms = Resize(224)
                  )
    return dblock.dataloaders(image_path, bs=64, seq_len=72,dl_kwargs=[{'res':range(2575225)},{'res':range(643806)},{}])