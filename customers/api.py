from ninja import Router

router = Router()


@router.get("/")
def list_customers(request):
    return "customers"