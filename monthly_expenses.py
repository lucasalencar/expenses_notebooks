import pandas as pd
import numpy as np
import seaborn
import formatting as fmt
from record_summary import *
from date_helpers import records_for_month

def balance(expense, income):
    """Computes balance based on expenses and incomes.
    Returns balance and its percentage."""
    balance_val = income + expense
    balance_perc = balance_val / income
    return [balance_val, balance_perc]


def summary_expenses(expenses, incomes):
    """Builds a Dataframe with the expenses,
    incomes, balance and balance percentage."""
    balance_val, balance_perc = balance(expenses, incomes)
    summary_exp = pd.concat([expenses, incomes, balance_val, balance_perc], axis=1, sort=False)
    summary_exp.columns = ['Expenses', 'Incomes', 'Balance', 'Balance (%)']
    return summary_exp.dropna().sort_index()


MONTHLY_COST_COLS_FORMAT = {
    'Expenses': fmt.BR_CURRENCY_FORMAT,
    'Incomes': fmt.BR_CURRENCY_FORMAT,
    'Balance': fmt.BR_CURRENCY_FORMAT,
    'Balance (%)': fmt.PERC_FORMAT
}


def style_summary_expenses(summary, balance_goal):
    return summary.style\
        .format(MONTHLY_COST_COLS_FORMAT)\
        .applymap(fmt.amount_color, subset=['Expenses', 'Incomes'])\
        .applymap(fmt.red_to_green_background(balance_goal), subset=['Balance (%)'])


def expense_distribution(expenses, denominator):
    denominator_sum = denominator.amount.sum()
    expenses_by_category = total_amount_by('category', expenses).sort_values('amount')
    return expenses_by_category / denominator_sum


def describe_expenses(expenses, incomes):
    expenses_by_category = total_amount_by('category', expenses)
    dist_by_spent = expense_distribution(expenses, expenses)
    dist_by_income = expense_distribution(expenses,
                                          incomes[incomes.category == 'renda']) * -1

    return pd.DataFrame({'amount #': expenses_by_category.amount,
                         '% by expenses': dist_by_spent.amount,
                         '% by income': dist_by_income.amount},
                        columns=['amount #', '% by expenses', '% by income']).sort_values('amount #')


EXPENSES_DISTRIBUTION_COLS_FORMAT = {
    'amount #': fmt.BR_CURRENCY_FORMAT,
    '% by expenses': fmt.PERC_FORMAT,
    '% by income': fmt.PERC_FORMAT
}


def style_expenses_distribution(dist):
    return dist.style.format(EXPENSES_DISTRIBUTION_COLS_FORMAT)


def _expenses_over_time_(expenses, incomes, post_describe_fn):
    """Computes expenses distribution over time, for all months available in expenses"""
    exps = {}
    for month in available_months(expenses):
        exps[month] = post_describe_fn(
            describe_expenses(records_for_month(expenses, month_to_date(month)),
                              records_for_month(incomes, month_to_date(month))))
    return pd.DataFrame(exps, columns=sorted(exps.keys()))\
        .replace([np.inf, -np.inf], np.nan).fillna(0).transpose()


def expenses_over_time(expenses, incomes, column):
    """Computes expenses distribution over time, for all months available in expenses"""
    post_describe_fn = None
    if column == 'amount #':
        post_describe_fn = lambda x: x['amount #'] * -1
    else:
        post_describe_fn = lambda x: x[column]
    return _expenses_over_time_(expenses, incomes, post_describe_fn)


def plot_expenses_over_time(expenses):
    """Line plots for expenses over time"""
    data = expenses.reset_index().rename(columns={'index': 'date'})
    plt = data.plot(figsize=(20, 5), grid=True, fontsize=15, xticks=data.index)
    plt.set_xticklabels(data.date)
    plt.legend(fontsize=15)
    return plt
