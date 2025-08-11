from collections import defaultdict

def calculate_trip_balances(trip):
    """
    Calculates financial balances, settlement transactions, and category summaries.
    Returns balances, transactions, and a category summary.
    """

    balances = defaultdict(float)
    category_summary = defaultdict(float)

    for expense in trip.expenses.all():
        # Aggregate expenses by category
        category_summary[expense.get_category_display()] += float(expense.amount)

        # Credit the person who paid for the expense
        balances[expense.paid_by] += float(expense.amount)

        # Determine who the expense should be split among
        split_with_users = expense.split_with.all()
        if not split_with_users:
            split_with_users = trip.participants.all()

        num_participants_in_expense = len(split_with_users)
        if num_participants_in_expense > 0:
            cost_per_person = float(expense.amount) / num_participants_in_expense
            for participant in split_with_users:
                # Debit each person their share of the expense
                balances[participant] -= cost_per_person

    # --- Settlement Calculation (unchanged) ---
    debtors = []
    creditors = []
    for user, balance in balances.items():
        if balance < -0.01:
            debtors.append({'user': user, 'amount': -balance})
        elif balance > 0.01:
            creditors.append({'user': user, 'amount': balance})

    debtors.sort(key=lambda x: x['amount'], reverse=True)
    creditors.sort(key=lambda x: x['amount'], reverse=True)

    transactions = []

    while debtors and creditors:
        debtor = debtors[0]
        creditor = creditors[0]
        payment_amount = min(debtor['amount'], creditor['amount'])

        transactions.append({
            'from': debtor['user'],
            'to': creditor['user'],
            'amount': payment_amount
        })

        debtor['amount'] -= payment_amount
        creditor['amount'] -= payment_amount

        if debtor['amount'] < 0.01:
            debtors.pop(0)
        if creditor['amount'] < 0.01:
            creditors.pop(0)

    return balances, transactions, category_summary
