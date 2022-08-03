from itertools import count
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import torch.utils.data as data

from webapp import db
import sqlalchemy
import pandas as pd
import os
import config
import json

################## Data Class Definition #############
class NCFData(data.Dataset):
	def __init__(self, features, num_item, train_mat, num_ng=0):
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

    conn = db.connect()
    if type=="Restaurant":
        query = sqlalchemy.text(f'SELECT username, res_id FROM Order{type} ORDER BY username')
    else:
        query = sqlalchemy.text(f'SELECT username, id FROM Order{type} ORDER BY username')
    result = conn.execute(query).fetchall()

    if type == "Restaurant":
        max_resid_query = sqlalchemy.text(f'SELECT MAX(res_id) FROM Order{type}')
    else:
        max_resid_query = sqlalchemy.text(f'SELECT MAX(id) FROM Order{type}')
    max_resid_result = conn.execute(max_resid_query).fetchall()
    max_resid = int(max_resid_result[0][0]) + 1
    
    count_username_query = sqlalchemy.text(f'SELECT COUNT(DISTINCT username) FROM Order{type}')
    count_username_result = conn.execute(count_username_query).fetchall()
    count_username = int(count_username_result[0][0]) + 1

    user_count = -1
    current_username = ""

    user_hash = pd.DataFrame(columns=['Username','Id'])
    train_mat = [[0 for x in range(max_resid)] for y in range(count_username)] 
    train_data = []
    for row in result:
        username = row[0]
        res_id = row[1]

        
        if( username != current_username):
            user_hash = user_hash.append([[username, int(user_count+1)]])
            user_count = user_count + 1
            current_username = username
        train_data.append([user_count,res_id])
        train_mat[user_count][res_id] +=1

    number_user = user_count + 1
    number_restaurant = max_resid

    if os.path.exists(config.model_path+"user.csv"):
        os.remove(config.model_path+"user.csv")
    user_hash.to_csv(config.model_path+"user.csv")
    return train_data, number_user,number_restaurant, train_mat

def train(type, num_ng=0, batch_size=32, training_epoch=10, learning_rate=0.05, factor_num=100, num_layers=4, dropout_rate=0.1):
    # prepare data
    train_data, number_user, number_restaurant, train_mat = load_data(type)
    train_dataset = NCFData(train_data, number_user, train_mat, num_ng)
    train_loader = data.DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=4)

    # initialize model
    model = NCF(number_user=number_user, number_restaurant=number_restaurant, factor_num=factor_num, num_layers=num_layers, dropout_rate=dropout_rate)
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
    if os.path.exists(config.model_path+type+".pth"):
        os.remove(config.model_path+type+".pth")

    torch.save(model, config.model_path+type+".pth")

############# Return Rec ###########
def recommend(username, key):
    type = ""
    if key == "restaurant": 
        type = "Restaurant"
    elif key == "bars": 
        type = "Bar"
    else: 
        type = "Cafe"

    assert os.path.exists(config.model_path+type+".pth"), "No trained model to load"
    assert os.path.exists(config.model_path+"user.csv"), "No trained model to load"
    
    model = torch.load(config.model_path+type+".pth")
    user_hash = pd.read_csv(config.model_path+"user.csv")
    rec = {}
    res1 = {}
    conn = db.connect()

    if (user_hash["Username"]==username).any():
        da, n, _, mat = load_data(type)
        t = NCFData(da,n,mat)
        loader = data.DataLoader(t,batch_size=16, shuffle=False, num_workers=0)
        loader.dataset.ng_sample()
        for user, item, label in loader:
            predictions = model(user, item)
        _, indices = torch.topk(predictions, 3) #fetch top 3 most possible restaurants
        query = query = sqlalchemy.text(f'SELECT DISTINCT id, res_name, price_level, rating, num_ratings, address FROM {type} WHERE id ={indices[0]} OR id ={indices[1]} OR id ={indices[2]}')
        if type=="Restaurant":
            query = sqlalchemy.text(f'SELECT DISTINCT res_id, res_name, price_level, rating, num_ratings, address FROM Restaurant WHERE res_id ={indices[0]} OR res_id ={indices[1]} OR res_id ={indices[2]}')
        #res1 = [dict(e) for e in conn.execute(query).fetchall()]
        rec[key] = [dict(e) for e in conn.execute(query).fetchall()]
    else:
        if key == "restaurant":
            query = sqlalchemy.text('SELECT DISTINCT res_id, res_name, price_level, rating, num_ratings, address FROM Restaurant r JOIN ServeRestaurant s ON r.id = s.res_id WHERE price_level IN (1, 2) AND rating > 4.5 AND num_ratings > 100 AND food_id IN (SELECT food_id FROM Favorites WHERE username="'+username+'") ORDER BY rating DESC, num_ratings DESC LIMIT 15');
            suggestions = conn.execute(query)
            #res1 = [dict(e) for e in suggestions.fetchall()]
            rec["restaurant"] = [dict(e) for e in suggestions.fetchall()]
        if key == "bars":
            query = sqlalchemy.text('SELECT DISTINCT bar_id, res_name, price_level, rating, num_ratings, address FROM Bar r JOIN ServeBar s ON r.id = s.bar_id WHERE price_level IN (1, 2) AND rating > 4.5 AND num_ratings > 100 AND food_id IN (SELECT food_id FROM Favorites WHERE username="'+username+'") ORDER BY rating DESC, num_ratings DESC LIMIT 15');
            suggestions = conn.execute(query)
            rec ["bars"] = [dict(e) for e in suggestions.fetchall()]
        if key == "cafes":
            query = sqlalchemy.text('SELECT DISTINCT cafe_id, res_name, price_level, rating, num_ratings, address FROM Cafe r JOIN ServeCafe s ON r.id = s.cafe_id WHERE price_level IN (1, 2) AND rating > 4.5 AND num_ratings > 100 AND food_id IN (SELECT food_id FROM Favorites WHERE username="'+username+'") ORDER BY rating DESC, num_ratings DESC LIMIT 15');
            suggestions = conn.execute(query)
            rec ["cafes"] = [dict(e) for e in suggestions.fetchall()]

    conn.execute(sqlalchemy.text(f'CALL findUserCandidatePlaces("{username}")'))
    tem = conn.execute(sqlalchemy.text(f'SELECT * FROM userCandidatePlaces limit 5'))
    res2 = [dict(e) for e in tem.fetchall()]
    for x in res2:
        rec[key].append(x)

    return json.dumps(rec)
