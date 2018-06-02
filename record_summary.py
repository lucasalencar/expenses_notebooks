def groupby_month(data):
    """Returns groupby month given data records"""
    return data['date'].dt.strftime("%Y-%m")


def total_amount_by(groupby, records, ascending=True):
    """Sums total amount given a column to group by"""
    return records.groupby(groupby).sum().sort_values('amount', ascending=ascending)
