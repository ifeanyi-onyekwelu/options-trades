from django import forms


class DepositForm(forms.Form):
    METHOD_CHOICES = [
        ("BITCOIN", "BITCOIN - (BTC)"),
        ("ETHEREUM", "ETHEREUM - (ETH - ERC20)"),
        ("USDT", "USDT - (Tether USD - TRC20)"),
        ("LITECOIN", "Litecoin"),
        ("BANK", "Bank Transfer"),
    ]

    method = forms.ChoiceField(
        choices=METHOD_CHOICES,
        required=True,
        widget=forms.Select(
            attrs={
                "class": "form-control",  # Bootstrap class
                "data-trigger": "true",  # Matches your form
                "id": "choices-single-default",
            }
        ),
    )

    amount = forms.DecimalField(
        min_value=1,
        required=True,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control form-control-lg crypto-buy-sell-input",  # Bootstrap class
                "placeholder": "Amount",
                "aria-label": "Amount",
            }
        ),
    )
