import numpy as np
from torch.utils.data import Dataset, DataLoader,TensorDataset
import torch
from net import SimilarityModel
import torch.nn as nn
import random
import torch.optim as optim
import os

# 创建空列表用于保存划分后的数据
test_data = np.load('test.npy')
test_label = np.load('test_label.npy')
test_data = test_data[:1000]
test_label = test_label[:1000]
test_input = torch.tensor(test_data)
test_label= torch.tensor(test_label)
test_label = torch.squeeze(test_label)

test_ids = TensorDataset(test_input,test_label)
test_dataloader = DataLoader(test_ids,batch_size=1,shuffle=True)

train_data = np.load('trianData.npy')
train_label = np.load('trainLabel.npy')
sample2_input = torch.tensor(train_data)
sample2_label= torch.tensor(train_label)
sample2_label = torch.squeeze(sample2_label)

import torch
from torch.utils.data import DataLoader, TensorDataset

# 将sample2_input数据按类别划分
class_indices = []
num_classes = 10
num_samples_per_class = 200

for class_id in range(num_classes):
    # 获取当前类别的数据索引
    indices = (sample2_label == class_id).nonzero().view(-1)
    class_indices.append(indices)

# 创建每个类别的数据加载器
sample2_dataloaders = []
batch_size = 32

for class_id in range(num_classes):
    class_indices_tensor = class_indices[class_id]
    class_data = sample2_input[class_indices_tensor]
    class_label = sample2_label[class_indices_tensor]
    class_dataset = TensorDataset(class_data, class_label)
    class_dataloader = DataLoader(class_dataset, batch_size=1, shuffle=True)
    sample2_dataloaders.append(class_dataloader)
# sample2_ids = TensorDataset(sample2_input,sample2_label)
# sample2_dataloader = DataLoader(sample2_ids,batch_size=32,shuffle=True)


'''定义损失函数'''
criterion = nn.CrossEntropyLoss()

model = SimilarityModel()
'''异常处理结构'''
try:
    model.load_state_dict(torch.load('./best_model.pt'))
except:
    '''如果模型是导入GPU训练的 需要把模型再倒回CPU'''
    model.load_state_dict(torch.load('./best_model.pt', map_location=torch.device('cpu')))


classes = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']


import random

def test2(model, test_dataloader, sample2_dataloaders):
    model.eval()
    correct = 0
    # 对test_dataloader中的每个样本进行测试
    for sample1, labels in test_dataloader:
        sample1 = sample1.unsqueeze(1).float()
        similarity_scores = []

        # 对每个类别的sample2进行测试
        for i, dataloader in enumerate(sample2_dataloaders):
            class_label = i  # 当前类别的标签

            # 随机选择一个sample2进行测试
            sample2, _ = random.choice(list(dataloader))
            sample2 = sample2.unsqueeze(1).float()

            # 计算sample1和当前sample2的相似度
            similarity_score = model(sample1, sample2)
            similarity_scores.append(similarity_score.item())

        predicted_socre = max(similarity_scores)
        predicted_label = similarity_scores.index(predicted_socre)
        if predicted_label == labels.item():
            correct = correct + 1

        # 打印预测结果和真实标签
        print(f"Sample1 belongs to class: {predicted_label}, True class: {labels.item()}")

    accuracy = correct/2000
    print('Accuracy: ', accuracy)

test2(model, test_dataloader, sample2_dataloaders)

def test5(model, test_dataloader):
    model.eval()

    # 对test_dataloader中的每个样本进行测试
    for sample1, labels in test_dataloader:
        similarity_scores = []

        # 对每个类别的sample2进行测试
        for i, dataloader in enumerate(sample2_dataloaders):
            class_label = i  # 当前类别的标签
            class_similarity_scores = []

            # 重复五次，计算每个类别的平均相似度
            for _ in range(5):
                # 获取当前类别中的一个sample2进行测试
                sample2, _ = next(iter(dataloader))
                sample2 = sample2.unsqueeze(1).float()

                # 计算sample1和当前sample2的相似度
                similarity_score = model(sample1, sample2)
                class_similarity_scores.extend(similarity_score.tolist())

            similarity_scores.append(class_similarity_scores)

        # 找到相似度最高的类别
        predicted_label = np.argmax(np.array(similarity_scores).mean(axis=1))

        # 打印预测结果和真实标签
        print(f"Sample1 belongs to class: {predicted_label}, True class: {labels[0].item()}")

