from pydantic import ValidationError

from src.validation.customer_schema import CustomerSchema


customers = [
    {
        "customer_id": "C001",
        "full_name": "Thabo Mokoena",
        "email": "thabo@example.com",
        "customer_status": "Active"
    },
    {
        "customer_id": "C005",
        "full_name": "Nomsa Khumalo",
        "email": "nomsa@example.com",
        "customer_status": "Closeds"
    }
]


for customer in customers:
    try:
        validated = CustomerSchema.model_validate(customer)

        print(
            f"VALID: {validated.customer_id}"
        )

    except ValidationError as error:
        print(
            f"INVALID: {customer['customer_id']}"
        )

        for issue in error.errors():
            print(f"Reason: {issue['msg']}")