import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import torch.utils.data as data

from webapp import db
import sqlalchemy
import json
import os
import config

################## Data Class Definition #############
class NCFData(data.Dataset):
	def __init__(self, features, num_item, train_mat=None, num_ng=0):
		super(NCFData, self).__init__()

		self.features_ps = features
		self.num_item = num_item
		self.train_mat = train_mat
		self.num_ng = num_ng
		self.labels = [0 for _ in range(len(features))]

	def ng_sample(self):
		self.features_ng = []
		for x in self.features_ps:
			u = x[0]
			for t in range(self.num_ng):
				j = np.random.randint(self.num_item)
				while (u, j) in self.train_mat:
					j = np.random.randint(self.num_item)
				self.features_ng.append([u, j])

		labels_ps = [1 for _ in range(len(self.features_ps))]
		labels_ng = [0 for _ in range(len(self.features_ng))]

		self.features_fill = self.features_ps + self.features_ng
		self.labels_fill = labels_ps + labels_ng

	def __len__(self):
		return (self.num_ng + 1) * len(self.labels)

	def __getitem__(self, idx):
		features = self.features_fill
		labels = self.labels_fill

		user = features[idx][0]
		item = features[idx][1]
		label = labels[idx]
		return user, item ,label

################## Model Definition ##############
class NCF(nn.Module):
    def __init__(self, number_user, number_restaurant, factor_num, num_layers, dropout_rate):
        super(NCF, self).__init__()
        
        self.dropout = dropout_rate
        self.embed_user_GMF = nn.Embedding(number_user, factor_num)
        self.embed_re_GMF = nn.Embedding(number_restaurant, factor_num)
        self.embed_user_MLP = nn.Embedding(number_user, factor_num * (2 ** (num_layers - 1)))
        self.embed_re_MLP = nn.Embedding(number_restaurant, factor_num * (2 ** (num_layers - 1)))

        MLP_modules = []
        for i in range(num_layers):
            input_size = factor_num * (2 ** (num_layers - i))
            MLP_modules.append(nn.Dropout(p=self.dropout))
            MLP_modules.append(nn.Linear(input_size, input_size//2))
            MLP_modules.append(nn.ReLU())
        self.MLP_layers = nn.Sequential(*MLP_modules)
        
        predict_size = factor_num * 2
        self.predict_layer = nn.Linear(predict_size, 1)

        self._init_weight_()

    def _init_weight_(self):
        ## intializing weights
        nn.init.normal_(self.embed_user_GMF.weight, std=0.01)
        nn.init.normal_(self.embed_user_MLP.weight, std=0.01)
        nn.init.normal_(self.embed_re_GMF.weight, std=0.01)
        nn.init.normal_(self.embed_re_MLP.weight, std=0.01)

        for m in self.MLP_layers:
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight)
        nn.init.kaiming_uniform_(self.predict_layer.weight, a=1, nonlinearity='sigmoid')

        for m in self.modules():
            if isinstance(m, nn.Linear) and m.bias is not None:
                m.bias.data.zero_()

    def forward(self, user, re):
        embed_user_GMF = self.embed_user_GMF(user)
        embed_re_GMF = self.embed_re_GMF(re)
        output_GMF = embed_user_GMF * embed_re_GMF

        embed_user_MLP = self.embed_user_MLP(user)
        embed_re_MLP = self.embed_re_MLP(re)
        interaction = torch.cat((embed_user_MLP, embed_re_MLP), -1)
        output_MLP = self.MLP_layers(interaction)

        t = torch.cat((output_GMF, output_MLP), -1)

        prediction = self.predict_layer(t)
        return prediction.view(-1)

#################### Training ####################
def load_data(type):

    return train_data, number_user, number_restaurant, train_mat

def train(type, num_ng=0, batch_size=32, training_epoch=10, learning_rate=0.1, factor_num=10, num_layers=4, dropout=0.1):
    # prepare data
    train_data, number_user, number_restaurant, train_mat = load_data(type)
    train_dataset = NCFData(train_data, number_user, train_mat, num_ng)
    train_loader = data.DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=4)

    # initialize model
    model = NCF(number_user=number_user, number_restaurant=number_restaurant, factor_num=factor_num, num_layers=num_layers, dropout=dropout)
    model.cuda()
    loss_function = nn.BCEWithLogitsLoss()

    optimizer = optim.Adam(model.parameters(), lr=learning_rate)

    # train
    for epoch in range(training_epoch):
        model.train()
        train_loader.dataset.ng_sample()

        for user, restaurant, label in train_loader:
            user = user.cuda()
            restaurant = restaurant.cuda()
            label = label.float().cuda()

            model.zero_grad()
            prediction = model(user, restaurant)
            loss = loss_function(prediction, label)
            loss.backward()
            optimizer.step()

        model.eval()

    if not os.path.exists(config.model_path):
        os.mkdir(config.model_path)
    torch.save(model, config.model_path+type+".pth")

############# Return Rec ###########
def recommend(username, key):
    if key == "restaurants": type = "Restaurant"
    elif key == "bars": type = "Bar"
    elif key == "cafes": type = "Cafe"

    assert os.path.exists(config.model_path+type+".pth"), "No trained model to load"
    model = torch.load(config.model_path+type+".pth")

    conn = db.connect()
    rec = {}
    if type == "Restaurant":
        query = sqlalchemy.text('SELECT DISTINCT id FROM Restaurant');
        complete_list = conn.execute(query).fetchall()
    elif type == "Bar":
        query = sqlalchemy.text('SELECT DISTINCT id FROM Bar');
    elif type == "Cafe":
        query = sqlalchemy.text('SELECT DISTINCT id FROM Cafe');

    conn.close()

    return rec