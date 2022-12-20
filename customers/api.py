from ninja import Router

router = Router()


@router.get("/")
def list_accounts(request):
    return "hello"
