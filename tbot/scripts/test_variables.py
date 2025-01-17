import os
from ssg.products import get_all
from ssg.variables import (
    get_variables_by_products,
    get_variable_values,
)
from pprint import pprint

def _get_root_content_dir() -> str:
    # Update the path according to your environment
    home_dir = os.path.expanduser("~")
    content_root_dir = os.path.join(home_dir, "projects", "content")
    return content_root_dir


def get_products(content_root_dir: str) -> dict:
    products = get_all(content_root_dir)
    return products


def validate_products(products: dict, test_products: list) -> bool:
    if test_products in products:
        return True
    return False


def main():
    # test_products = ['rhel8', 'rhel9', 'rhel10']
    test_products = ['ocp4']
    content_root_dir = _get_root_content_dir()
    products = get_products(content_root_dir)
    print("--------------------------------------- All Products --------------------------------------------")
    print(products)
    print("\n")
    
    # missing_products = [product for product in test_products if product not in products.linux]
    missing_products = [product for product in test_products if product not in products.other]
    if missing_products:
        print(f"Check the existence of these products: {missing_products}")
        exit(1)

    profile_variables = get_variables_by_products(content_root_dir, test_products)
    print("--------------------------------------- Profile Variables ---------------------------------------")
    pprint(profile_variables)
    print("\n")
    profile_variables_values = get_variable_values(content_root_dir, profile_variables)
    print("--------------------------------------- Profile Variables Values --------------------------------")
    pprint(profile_variables_values)


if __name__ == "__main__":
    main()
