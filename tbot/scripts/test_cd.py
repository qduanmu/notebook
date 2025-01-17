import json

def main():
    cd_json = "/home/qduanmu/backup/trestlebot/component-definition.json"
    with open(cd_json, "r", encoding="utf-8") as f:
        data = json.load(f)
        cd = data['component-definition']
        # print(cd.keys())
        # print(cd['metadata'].keys())
        # print(len(cd['components']))  # 2

        # prop_names = []
        # for prop in cd['components'][0]['props']:
        #     if prop["name"] not in prop_names:
        #         prop_names.append(prop["name"])
        # print(prop_names)
        # Output: ['Rule_Id', 'Rule_Description', 'Parameter_Id', 'Parameter_Description', 'Parameter_Value_Alternatives']

        # print(len(cd['components'][0]['control-implementations'])) # 2
        # for ci in cd['components'][0]['control-implementations']:
            # print(ci.keys())
            # # Output: ['uuid', 'source', 'description', 'set-parameters', 'implemented-requirements']
            # # 'source' example: profiles/OCP4_CIS/profile.json
            # if ci.get("set-parameters"):
            #     print(ci["set-parameters"])
            #     # Output: a list of dict, example dict:
            #     # {'param-id': 'var_kubelet_eviction_thresholds_set_hard_memory_available', 'values': ['200Mi']}, {'param-id': 'var_kubelet_eviction_thresholds_set_hard_nodefs_available', 'values': ['5%']}
            # print(len(ci["implemented-requirements"])) # 31, 88 

        ci = cd['components'][0]['control-implementations'][1]
        # print(ci["implemented-requirements"][0].keys())
        # # Output: dict_keys(['uuid', 'control-id', 'description', 'props'])
        # print(ci["implemented-requirements"][0]["control-id"])  # CIS-1.2.1
        # print(ci["implemented-requirements"][0]["props"])
        # # Output: [{'name': 'Rule_Id', 'ns': 'http://ibm.github.io/compliance-trestle/schemas/oscal/cd', 'value': 'api_server_anonymous_auth'}, {'name': 'implementation-status', 'value': 'planned'}]


if __name__ == "__main__":
    main()

