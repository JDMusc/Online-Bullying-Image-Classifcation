import os
import shutil

import numpy as np

from toolz import pipe as p


def makeScrapData(classes, dest_dir = None, n_train = 30, n_val = None, src_dir = 'image_data'):
    if dest_dir is None:
        dest_dir = 'scrap_data' + str(n_train)

    fs = {c: [os.path.join(src_dir, c, f) for f in p(os.path.join(src_dir, c), os.listdir)]
          for c in classes}
    
    by_phase = 'train' in os.listdir(src_dir) and 'test' in os.listdir(src_dir)
    class_percents = classPercentages(src_dir, classes = classes, by_phase= by_phase)['percent']
    
    train_counts = {c: int(class_percents[c]/100 * n_train) for c in classes}
    
    train_fs = {c: np.random.choice(fs[c], train_counts[c], replace = False) for c in classes}
    
    val_candidates = lambda c: list(set(fs[c]) - set(train_fs[c]))
    val_fs = {c: val_candidates(c) for c in classes}
    if n_val is not None:
        val_counts = {c: int(class_percents[c]/100 * n_val) for c in classes}
        val_fs = {c: np.random.choice(val_candidates(c), val_counts[c], replace = False)
                  for c in classes}
    
    if os.path.exists(dest_dir):
        shutil.rmtree(dest_dir)
        
    os.mkdir(dest_dir)
    
    joinDirGen = lambda d: lambda f: os.path.join(d, f)
    joinScrapDir = joinDirGen(dest_dir)
    
    train_val_fs = dict(train=train_fs, val=val_fs)
    for tv in ('train', 'val'):
        p(tv, joinScrapDir, os.mkdir)
        
        for c in classes:
            p(c, joinDirGen(tv),  joinScrapDir, os.mkdir)    
            
            tv_fs = train_val_fs[tv][c]
            for f in tv_fs:
                dest = p(f,
                         os.path.basename,
                         joinDirGen(c), 
                         joinDirGen(tv),
                         joinScrapDir)
                shutil.copyfile(f, dest)
            
            
def classPercentages(data_dir, by_phase = True, classes = None):
    
    if not by_phase:
        classes = os.listdir(data_dir) if classes is None else classes
        class_counts = {c: p(os.path.join(data_dir, c), os.listdir, len) for c in classes}
        n_total = sum(class_counts.values())
        
        class_percents = {c: count/n_total * 100 for (c, count) in class_counts.items()}
        
        return dict(percent = class_percents, count = class_counts)
    
    xs = ('train', 'val')
    
    if classes is None:
        train_dir = os.path.join(data_dir, 'train')
        classes = os.listdir(train_dir)
    
    folders = {(x,c):os.path.join(data_dir, x, c) for x in xs
          for c in classes}
    
    train_val_counts = {x:sum(
        [p(folders[x, c], os.listdir, len) for c in classes])
                        for x in xs}
    
    class_counts = {(x, c): p(folders[x, c], os.listdir, len)
                    for c in classes for x in xs}
    
    class_percents = {xc: count/train_val_counts[xc[0]] 
                      for (xc, count) in class_counts.items()}
    
    return dict(percent = class_percents, count = class_counts)
