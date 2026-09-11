happens, `read_csv` would fail.
Wait, can `amount_cents` in `transactions.csv` be that large? "amount_cents" typically represents cents of currency. Even trillions of dollars in cents is $10^{12} \times 100 = 10^{14}$, which fits in `int64` (up to $9.22 \times 10^{18}$).
Wait, what if `amount_cents` is read without specifying `int64` dtype?
If not specified, pandas inspects the column. If all values are integers fitting in int64, it automatically infers `int64`. If they don't, it infers `object` or `float6
