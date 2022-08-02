import os

model_path = './models/'
Restaurant_model_path = model_path + 'Restaurant.pth'
Cafe_model_path = model_path + 'Cafe.pth'
Bar_model_path = model_path + 'Bar.pth'

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'cs411-project'

