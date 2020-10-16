
"""
Test Factory to make fake objects for testing
"""
import factory
from factory.fuzzy import FuzzyChoice
from service.models import Supplier


class SupplierFactory(factory.Factory):
    """ Creates fake suppliers that you don't have to feed """

    class Meta:
        model = Supplier

    name = FuzzyChoice(choices=["supplier1", "supplier2", "supplier3", "supplier4"])
    like_count = factory.Sequence(lambda n: n)
    is_active = FuzzyChoice(choices=[True, False])
    products = FuzzyChoice(choices=[[1, 2, 3], [2, 3, 4], [3, 4, 5]])
    rating = FuzzyChoice(choices=[5.6, 6.8, 7.5, 9.5, 3.8])


if __name__ == "__main__":
    for _ in range(10):
        supplier = SupplierFactory()
        print(supplier.serialize())
