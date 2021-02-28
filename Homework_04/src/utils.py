import pandas as pd
import numpy as np

def prefilter_items(data, item_features=None):
    # Уберем самые популярные
    popularity = data.groupby('item_id')['user_id'].nunique().reset_index() / data['user_id'].nunique()
    popularity.rename(columns={'user_id': 'specific_unique_users'}, inplace=True)

    max_popular_items = popularity[popularity['specific_unique_users'] > 0.2].item_id.tolist()
    data = data[~data['item_id'].isin(max_popular_items)]

    # Уберем самые непопулярные
    min_popular_items = popularity[popularity['specific_unique_users'] < 0.02].item_id.tolist()
    data = data[~data['item_id'].isin(min_popular_items)]

    # Уберем товары, которые не продавались за последние 12 месяцев
    last_12_months = data.loc[data['week_no'] > data['week_no'].max() - 52].item_id.tolist()
    data.loc[~data['item_id'].isin(last_12_months), 'item_id'] = 999999

    # Уберем не интересные для рекоммендаций категории (department)
    if item_features is not None:
        department_size = pd.DataFrame(item_features.groupby('department')['item_id'].\
                                       nunique().sort_values(ascending=False)).reset_index()

        department_size.columns = ['department', 'n_items']
        rare_departments = department_size[department_size['n_items'] < 150].department.tolist()
        items_in_rare_departments = item_features[item_features['department'].isin(rare_departments)].item_id.unique().tolist()

        data = data[~data['item_id'].isin(items_in_rare_departments)]

    # Уберем слишком дешевые товары (на них не заработаем). 1 покупка из рассылок стоит 60 руб.
    data['price'] = data['sales_value'] / (np.maximum(data['quantity'], 1))
    data = data[data['price'] > 2]

    # Уберем слишком дорогие товары
    data = data[data['price'] < 50]

    # Оставим только 5000 самых популярных товаров
    popularity = data.groupby('item_id')['quantity'].sum().reset_index()
    popularity.rename(columns={'quantity': 'n_sold'}, inplace=True)
    top_5000 = popularity.sort_values('n_sold', ascending=False).head(5000).item_id.tolist()

    # добавим, чтобы не потерять юзеров
    data.loc[~data['item_id'].isin(top_5000), 'item_id'] = 999999

    return data


def postfilter_items():
    pass

