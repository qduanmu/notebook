import os
from ssg.products import get_all
from ssg.profiles import get_profiles_from_products
from ssg.variables import (
    get_variable_property,
    get_variable_values,
    get_variables_from_profiles,
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
    
    # missing_products = [product for product in test_products if product not in products.linux]
    missing_products = [product for product in test_products if product not in products.other]
    if missing_products:
        print(f"Check the existence of these products: {missing_products}")
        exit(1)
    
    # Get all profiles for the specified products. Besides profile and product ids and titles,
    # the profile object also contain rules and variables with respective values for that profile.
    profiles = get_profiles_from_products(content_root_dir, test_products, sorted=True)
    for profile in profiles:
        print(f'Rules for {profile.product_id} in profile {profile.profile_id}:')
        print(profile.rules)
        print("\n")
        
        print(f'Variables for {profile.product_id} in profile {profile.profile_id}:')
        print(profile.variables)
        print("\n")

    # Get variables used in a list of profiles and organize them into a nested dictionary.
    profile_variables = get_variables_from_profiles(profiles)
    #pprint(profile_variables)

    # Variables are defined in control files and profiles as variable_id=variable_option.
    # But the real values for these options are stored in the variable files. This function
    # will return these specific values including the implicit default value for the variable.
    # import pdb; pdb.set_trace()
    print(f'Variables values for {profile.product_id} in profile {profile.profile_id}:')
    profile_variables_values = get_variable_values(content_root_dir, profile_variables)
    #pprint(profile_variables_values)
    print("\n")

    # Once we have a variable id, we can easily collect any property of it. For example, the title
    # and description.
    variable_title = get_variable_property(content_root_dir, 'sshd_idle_timeout_value', 'title')
    variable_description = get_variable_property(content_root_dir, 'sshd_idle_timeout_value', 'description')
    print(f'{variable_title} - {variable_description}')


if __name__ == "__main__":
    main()
